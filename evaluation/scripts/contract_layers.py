"""Orbit-Evidence contract, organised as four mechanically checkable layers.

Every violation raises `ContractViolation` carrying a RULE ID, so a finding names the
rule it broke rather than surfacing a bare assertion failure.

Layers:
  L1  data availability
  L2  physical / scheduling validity
  L3  model-state causality
  L4  statistical independence and reproducibility

Four rules here are GENERAL rules written before any held-out mutation was injected
and without knowledge of its outcome: L1.5 (boundary probing), L2.4 (declared relation
versus implementation), L4.6 (provenance completeness by differential test) and L4.7
(statistical unit at the correct nesting level). Two of those four had no predecessor
detector of any kind.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np

SRC = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(SRC))

from orbit_evidence.experiment_contract import experiment_contract as EC   # noqa: E402
from orbit_evidence.causal_registry import causal_registry as CR       # noqa: E402
from orbit_evidence.pass_scheduler import visible_pass as VP         # noqa: E402


class ContractViolation(AssertionError):
    """Raised by every detector. Carries the rule it violated."""

    def __init__(self, rule: str, detail: str):
        self.rule = rule
        self.detail = detail
        super().__init__(f"[{rule}] {detail}")


@dataclass(frozen=True)
class Rule:
    rule_id: str
    layer: str
    protected_object: str
    statement: str
    failure_action: str = "halt the experiment"


RULES: dict[str, Rule] = {}


def _reg(r: Rule) -> Rule:
    RULES[r.rule_id] = r
    return r


# ==========================================================================
# L1 — DATA AVAILABILITY
# ==========================================================================

_reg(Rule("L1.1", "L1", "feature availability",
          "Every deployment feature must be computable from state available at the "
          "decision instant."))
_reg(Rule("L1.2", "L1", "availability clock",
          "An item's descriptive timestamp and its publication timestamp are distinct "
          "clocks; selection must use publication."))
_reg(Rule("L1.3", "L1", "label closure",
          "A label may enter training or selection only once its closure time has "
          "passed."))
_reg(Rule("L1.4", "L1", "row membership",
          "Later data may change a row's label status, value, uncertainty or closure "
          "time, but never whether the row exists."))
_reg(Rule("L1.5", "L1", "comparison boundaries",
          "Every availability comparison must be probed at exact equality, not only "
          "in the strict-ordering interior."))


def check_feature_availability(feature_fn: Callable[[float], np.ndarray],
                               probe_times: Sequence[float],
                               truncate_at: Callable[[float], Any],
                               restore: Callable[[Any], None]) -> None:
    try:
        EC.assert_no_future_dependency(feature_fn, probe_times, truncate_at, restore)
    except AssertionError as e:
        raise ContractViolation("L1.1", str(e)) from None


def check_availability_clock(descriptive: np.ndarray, published: np.ndarray,
                            t_decision: float, selected_index: int) -> None:
    if selected_index < 0:
        return
    if float(published[selected_index]) > t_decision:
        raise ContractViolation(
            "L1.2",
            f"selected item {selected_index} was published at "
            f"{published[selected_index]} but the decision instant is {t_decision}; "
            f"selection appears to have used the descriptive clock "
            f"({descriptive[selected_index]})")


def check_label_closure(closure_times: np.ndarray, decision_time: float,
                        used_mask: np.ndarray) -> None:
    late = np.asarray(closure_times, dtype=float)[np.asarray(used_mask, dtype=bool)]
    bad = int(np.sum(late > decision_time))
    if bad:
        raise ContractViolation(
            "L1.3", f"{bad} label(s) used at decision time {decision_time} close "
                    f"later (max closure {float(late.max())})")


def check_row_membership(build_fn, window, full_source, truncated_source) -> None:
    try:
        CR.assert_membership_independent_of_future(build_fn, window,
                                                  full_source, truncated_source)
    except AssertionError as e:
        raise ContractViolation("L1.4", str(e)) from None


def probe_comparison_boundary(admit_fn: Callable[[float, float], bool],
                             t_decision: float = 100.0) -> None:
    """L1.5 -- GENERAL RULE, written before any held-out mutation was injected.

    An availability predicate must admit an item published strictly before the
    decision instant, admit one published exactly at it, and reject one published
    after. Interior-only testing cannot distinguish `<=` from `<`, and the sign of
    that error is silent: it discards usable data or admits unusable data depending
    on which way it is wrong.
    """
    before, equal, after = t_decision - 1.0, t_decision, t_decision + 1.0
    if not admit_fn(before, t_decision):
        raise ContractViolation("L1.5",
            "predicate rejects an item published strictly before the decision instant")
    if not admit_fn(equal, t_decision):
        raise ContractViolation("L1.5",
            "predicate rejects an item published EXACTLY at the decision instant; "
            "the boundary comparison is strict where it must be inclusive")
    if admit_fn(after, t_decision):
        raise ContractViolation("L1.5",
            "predicate admits an item published after the decision instant")


# ==========================================================================
# L2 — PHYSICAL / SCHEDULING VALIDITY
# ==========================================================================

_reg(Rule("L2.1", "L2", "sampling geometry",
          "Every scheduled transmission must lie inside a predicted-visible interval."))
_reg(Rule("L2.2", "L2", "physical scale",
          "The target must lie between a resolution floor and a plausibility ceiling."))
_reg(Rule("L2.3", "L2", "hidden state",
          "No hidden state may diverge without bound over the evaluation window."))
_reg(Rule("L2.4", "L2", "declared relation",
          "The relation declared in configuration must reproduce the implementation "
          "across the declared domain AND an extrapolation margin beyond it."))


def check_sampling_geometry(elevations: np.ndarray, mask_deg: float,
                           tol: float = 1e-6) -> None:
    e = np.asarray(elevations, dtype=float)
    bad = int(np.sum(e < mask_deg - tol))
    if bad:
        raise ContractViolation(
            "L2.1", f"{bad} of {e.size} scheduled transmissions lie below the "
                    f"{mask_deg} deg mask (min {float(e.min()):.4f} deg)")


def check_physical_scale(residual: np.ndarray, reference: np.ndarray,
                        floor: float, ceiling: float) -> None:
    v = EC.physical_scale_check(residual, reference, floor, ceiling)
    if not v["pass"]:
        raise ContractViolation(
            "L2.2", f"target/reference ratio {v['ratio']:.5f} is {v['label']} "
                    f"(floor {floor}, ceiling {ceiling})")


def check_bounded_state(times: np.ndarray, quantity: np.ndarray,
                       max_ratio: float = 3.0) -> None:
    v = EC.unbounded_divergence_check(times, quantity, max_ratio)
    if not v["pass"]:
        raise ContractViolation(
            "L2.3", f"late/early magnitude ratio {v['ratio']:.3f} exceeds "
                    f"{max_ratio}; hidden state is integrating")


def check_declared_relation(declared: Callable[[np.ndarray], np.ndarray],
                           implemented: Callable[[np.ndarray], np.ndarray],
                           domain: tuple[float, float],
                           extrapolation_margin: float = 0.5,
                           rtol: float = 1e-3, n: int = 256) -> None:
    """L2.4 -- GENERAL RULE, written before any held-out mutation was injected.

    A declared relation is checked on the declared domain and on an extrapolation
    margin beyond it. Checking only the declared domain cannot separate a correct
    implementation from one that agrees where it was fitted and diverges outside --
    which is exactly the shape a silent config/code drift takes.
    """
    lo, hi = domain
    span = hi - lo
    x = np.linspace(lo - extrapolation_margin * span,
                    hi + extrapolation_margin * span, n)
    d, i = np.asarray(declared(x), dtype=float), np.asarray(implemented(x), dtype=float)
    scale = max(float(np.max(np.abs(d))), 1e-12)
    err = float(np.max(np.abs(d - i))) / scale
    if err > rtol:
        inside = np.abs(x - 0.5 * (lo + hi)) <= 0.5 * span
        err_in = float(np.max(np.abs(d[inside] - i[inside]))) / scale
        raise ContractViolation(
            "L2.4", f"declared relation departs from implementation by {err:.3e} "
                    f"relative (inside the declared domain only {err_in:.3e}); "
                    f"configuration and code disagree")


# ==========================================================================
# L3 — MODEL-STATE CAUSALITY
# ==========================================================================

_reg(Rule("L3.1", "L3", "state channels",
          "No state channel -- feature tensor, scaler, coefficients, tracker latent "
          "state, selected-model metadata or gate bit -- may carry information from "
          "after the freeze."))
_reg(Rule("L3.3", "L3", "negative control",
          "A control whose injected effect is zero must not admit a learned branch, at "
          "any level of the study covariate."))
_reg(Rule("L3.2", "L3", "canary effectiveness",
          "A mutation used to test a channel must be shown to change behaviour before "
          "its detectability means anything."))


def check_state_channels(run_fn: Callable[[str | None], Mapping[str, Any]],
                        channels: Sequence[str] = EC.STATE_CHANNELS,
                        observables: Sequence[str] = ("val_ratio", "gate", "m_star"),
                        ) -> dict[str, bool]:
    detected = EC.mutation_canary(run_fn, channels, observables)
    missed = [c for c, ok in detected.items() if not ok]
    if missed:
        raise ContractViolation(
            "L3.1", f"future information injected into {missed} produced no observable "
                    f"change; these channels are unguarded")
    return detected


def assert_canary_effective(run_fn: Callable[[str | None], Mapping[str, Any]],
                           channel: str,
                           observables: Sequence[str] = ("val_ratio", "gate", "m_star"),
                           ) -> None:
    clean, mut = run_fn(None), run_fn(channel)
    if all(mut.get(k) == clean.get(k) for k in observables):
        raise ContractViolation(
            "L3.2", f"mutation on channel '{channel}' is a no-op; an inert mutation "
                    f"cannot demonstrate that the channel is guarded")


def check_negative_control(gate_open_rates, max_rate: float = 0.20) -> None:
    v = EC.negative_control_verdict(gate_open_rates, max_rate)
    if not v["pass"]:
        raise ContractViolation(
            "L3.3", f"zero-effect control admits in {v['failing_cells']} "
                    f"(limit {max_rate}); the control contains undeclared "
                    f"deterministic signal")


# ==========================================================================
# L4 — STATISTICAL INDEPENDENCE AND REPRODUCIBILITY
# ==========================================================================

_reg(Rule("L4.1", "L4", "chronology",
          "Train, validation and deployment folds must be chronologically ordered and "
          "disjoint."))
_reg(Rule("L4.2", "L4", "paired randomness",
          "Compared conditions must share one physical realisation; only the "
          "intervention may differ."))
_reg(Rule("L4.3", "L4", "repeated measures",
          "Replicates of one physical event must be aggregated before any metric."))
_reg(Rule("L4.4", "L4", "seed hygiene",
          "Burned and evaluation seed namespaces must remain disjoint."))
_reg(Rule("L4.5", "L4", "provenance hashes",
          "Every declared artifact must be hashed and the manifest itself hashed."))
_reg(Rule("L4.6", "L4", "provenance completeness",
          "If two runs produce different outputs their provenance manifests must "
          "differ; every behaviour-changing input must be covered."))
_reg(Rule("L4.7", "L4", "statistical unit",
          "The chosen statistical unit must show negligible residual correlation at "
          "the next coarser grouping."))


def check_chronology(fold: np.ndarray, times: np.ndarray) -> None:
    f, t = np.asarray(fold, dtype=int), np.asarray(times, dtype=float)
    hi = [float(t[f == k].max()) if np.any(f == k) else -np.inf for k in (0, 1, 2)]
    lo = [float(t[f == k].min()) if np.any(f == k) else np.inf for k in (0, 1, 2)]
    for a, b, nm in ((0, 1, "train/validation"), (1, 2, "validation/deployment")):
        if hi[a] > lo[b]:
            raise ContractViolation(
                "L4.1", f"{nm} folds overlap in time: fold {a} ends {hi[a]}, "
                        f"fold {b} starts {lo[b]}")


def check_paired_conditions(matrices: Mapping[str, np.ndarray],
                           mask: np.ndarray | None = None) -> None:
    try:
        EC.assert_paired(matrices, mask)
    except AssertionError as e:
        raise ContractViolation("L4.2", str(e)) from None


def check_repeated_measures(values: np.ndarray, group_ids: np.ndarray,
                           aggregated: bool, icc_warn: float = 0.2) -> None:
    icc = EC.within_group_icc(values, group_ids)
    if np.isfinite(icc) and icc > icc_warn and not aggregated:
        raise ContractViolation(
            "L4.3", f"within-group correlation {icc:.3f} exceeds {icc_warn} but "
                    f"replicates were not aggregated before the metric")


def check_seed_hygiene(registry: EC.SeedRegistry,
                      about_to_run: Sequence[int] = ()) -> None:
    try:
        registry.assert_clean()
        if about_to_run:
            registry.assert_not_evaluation(about_to_run)
    except AssertionError as e:
        raise ContractViolation("L4.4", str(e)) from None


def check_provenance_hashes(manifest: Mapping[str, Any]) -> None:
    if "files" not in manifest or "manifest_sha256" not in manifest:
        raise ContractViolation("L4.5", "manifest lacks files or its own hash")
    if not manifest["files"]:
        raise ContractViolation("L4.5", "manifest covers no artifact")


def check_provenance_completeness(
        run_fn: Callable[[Mapping[str, Any]], tuple[Any, Mapping[str, Any]]],
        input_variations: Sequence[Mapping[str, Any]]) -> None:
    """L4.6 -- GENERAL RULE, written before any held-out mutation was injected.
    No predecessor detector of any kind existed for this proposition.

    Differential test: run under each variation, collect (output_digest, manifest_hash).
    If two variations produce DIFFERENT outputs under the SAME manifest hash, the
    manifest omits a behaviour-changing input and provenance is not reproducible.

    Note the asymmetry that makes this checkable: identical outputs under different
    manifests is merely redundant, and is not an error.
    """
    seen: dict[str, set[str]] = {}
    for cfg in input_variations:
        out, man = run_fn(cfg)
        od = hashlib.sha256(
            np.asarray(out, dtype=float).tobytes()
            if not isinstance(out, (str, bytes)) else
            (out.encode() if isinstance(out, str) else out)).hexdigest()
        mh = str(man.get("manifest_sha256", "MISSING"))
        seen.setdefault(mh, set()).add(od)
    for mh, digests in seen.items():
        if len(digests) > 1:
            raise ContractViolation(
                "L4.6", f"{len(digests)} distinct outputs share provenance hash "
                        f"{mh[:12]}; a behaviour-changing input is not covered by the "
                        f"manifest")


def check_statistical_unit(values: np.ndarray, unit_ids: np.ndarray,
                          coarser_ids: np.ndarray,
                          residual_icc_max: float = 0.2,
                          min_coarser_groups: int = 8) -> dict[str, Any]:
    """L4.7 -- GENERAL RULE, written before any held-out mutation was injected.
    No predecessor detector of any kind existed for this proposition.

    Aggregate to the CHOSEN unit, then measure the intraclass correlation of those
    unit-level values within the next COARSER grouping. Material residual correlation
    means the chosen unit shares state with its neighbours, so intervals computed over
    it are optimistic. Aggregating correctly at one level says nothing about whether
    that level is the exchangeable one; this is the check for the level itself.

    ESTIMABILITY PRECONDITION. The rule does not halt when it cannot estimate. With
    fewer than `min_coarser_groups` coarser groups the ICC estimate is dominated by
    sampling noise: measured on this repository's own clean fixture at four groups of
    three, two environments returned 0.000 and 0.018 while a third returned 0.201 --
    crossing a 0.2 threshold on noise alone, which would have been a false halt and a
    non-reproducible verdict across environments. A rule that halts on an unestimable
    statistic is worse than no rule, so below the precondition the check reports
    INDETERMINATE and raises nothing.

    Returns a verdict dict so a caller can distinguish "passed" from "could not judge".
    """
    u, agg = EC.aggregate_repeated_measures(values, unit_ids)
    ui, ci = np.asarray(unit_ids), np.asarray(coarser_ids)
    coarse_of: dict[Any, Any] = {}
    for a, b in zip(ui.tolist(), ci.tolist()):
        coarse_of.setdefault(a, b)
    grp = np.array([coarse_of[k] for k in u.tolist()])
    n_groups = len({g for g, c in zip(grp.tolist(), np.bincount(
        np.unique(grp, return_inverse=True)[1]).tolist()) } | set(grp.tolist()))
    n_groups = len(set(grp.tolist()))
    if n_groups < min_coarser_groups:
        return {"verdict": "INDETERMINATE", "n_coarser_groups": n_groups,
                "min_required": min_coarser_groups, "icc": None,
                "reason": "too few coarser groups to estimate an ICC; not halting"}
    icc = EC.within_group_icc(agg, grp)
    if not np.isfinite(icc):
        return {"verdict": "INDETERMINATE", "n_coarser_groups": n_groups,
                "icc": None, "reason": "ICC not estimable"}
    if icc > residual_icc_max:
        raise ContractViolation(
            "L4.7", f"unit-level values retain correlation {icc:.3f} within the next "
                    f"coarser grouping over {n_groups} groups (limit "
                    f"{residual_icc_max}); the chosen statistical unit is finer than "
                    f"the exchangeable one")
    return {"verdict": "PASS", "n_coarser_groups": n_groups, "icc": float(icc)}


# ==========================================================================

def rule_table() -> list[dict[str, str]]:
    """Source for TABLE I."""
    return [{"rule": r.rule_id, "layer": r.layer,
             "protected_object": r.protected_object, "statement": r.statement,
             "failure_action": r.failure_action}
            for r in sorted(RULES.values(), key=lambda x: x.rule_id)]


GENERAL_RULES_WRITTEN_BLIND = ("L1.5", "L2.4", "L4.6", "L4.7")
NO_PREDECESSOR_DETECTOR = ("L4.6", "L4.7")
