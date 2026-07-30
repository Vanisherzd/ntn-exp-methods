"""Experiment-contract utilities: seed hygiene, pairing, provenance, canaries.

Fourth reusable asset, and the one whose absence caused the most damage. Every
function here exists because its absence produced a specific measured failure in the
stopped research line.
"""

from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np


# ---------------------------------------------------------------- seeds

@dataclass
class SeedRegistry:
    """Three disjoint namespaces. A seed whose OUTCOMES have been inspected is burned.

    Historical cause: an independent reviewer executed a full protocol on the intended
    evaluation seeds and inspected the results, which then informed a design revision.
    Those seeds became development seeds. This happened twice.
    """
    burned: set[int] = field(default_factory=set)
    debug: set[int] = field(default_factory=set)
    evaluation: set[int] = field(default_factory=set)

    def burn(self, seeds: Iterable[int], reason: str = "") -> None:
        self.burned |= set(seeds)
        self.evaluation -= set(seeds)

    def assert_clean(self) -> None:
        if self.evaluation & self.burned:
            raise AssertionError(
                f"burned seeds present in evaluation set: "
                f"{sorted(self.evaluation & self.burned)}")
        if self.evaluation & self.debug:
            raise AssertionError("debug seeds present in evaluation set")

    def assert_not_evaluation(self, seeds: Iterable[int]) -> None:
        bad = set(seeds) & self.evaluation
        if bad:
            raise AssertionError(f"would execute evaluation seeds: {sorted(bad)}")


def derive_seed(prefix: str, *parts: Any, digits: int = 8) -> int:
    """Deterministic, non-selective seed derivation. No filtering or resampling."""
    key = "|".join([prefix, *map(str, parts)])
    return int(hashlib.sha256(key.encode()).hexdigest()[:digits], 16)


def common_random_numbers(prefix: str, invariant_parts: Sequence[Any],
                          n: int) -> list[int]:
    """One seed list shared by every CONDITION of a cell.

    The condition label must NOT appear in `invariant_parts`. Including it gives each
    condition a different physical realisation, which silently destroys pairing while
    every surface claim still reads "conditions differ only in the intervention".
    """
    return [derive_seed(prefix, *invariant_parts, i) for i in range(n)]


def assert_paired(matrices: Mapping[str, np.ndarray],
                  mask: np.ndarray | None = None, tol: float = 0.0) -> None:
    """All condition arms bit-identical (default) on the given rows."""
    names = list(matrices)
    ref = np.asarray(matrices[names[0]])
    r = ref if mask is None else ref[mask]
    for nm in names[1:]:
        o = np.asarray(matrices[nm])
        oo = o if mask is None else o[mask]
        if r.shape != oo.shape:
            raise AssertionError(f"{names[0]} vs {nm}: shape {r.shape} != {oo.shape}")
        d = float(np.max(np.abs(r - oo))) if r.size else 0.0
        if d > tol:
            raise AssertionError(f"{names[0]} vs {nm}: max|delta| = {d:.3e} > {tol}")


# ---------------------------------------------------------------- provenance

def file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def provenance_manifest(paths: Sequence[str | Path],
                        extra: Mapping[str, Any] | None = None) -> dict[str, Any]:
    m: dict[str, Any] = {"files": {str(p): file_sha256(p) for p in paths}}
    if extra:
        m.update(dict(extra))
    m["manifest_sha256"] = hashlib.sha256(
        json.dumps(m, sort_keys=True).encode()).hexdigest()
    return m


# ---------------------------------------------------------------- temporal checks

def assert_no_future_dependency(feature_fn: Callable[[float], np.ndarray],
                               times: Sequence[float],
                               truncate_at: Callable[[float], Any],
                               restore: Callable[[Any], None]) -> None:
    """Recompute features with all state after t removed; require bit-identity.

    This is the truncation form. It is the only form that can fail: comparing two
    arrays built from the same object cannot, and a historical test that did exactly
    that passed under a mutation piping the label straight into a feature column.
    """
    for t in times:
        before = np.array(feature_fn(t), dtype=float, copy=True)
        saved = truncate_at(t)
        try:
            after = np.array(feature_fn(t), dtype=float, copy=True)
        finally:
            restore(saved)
        if not np.array_equal(before, after):
            raise AssertionError(f"feature at t={t} depends on state after t")


def assert_reads_only(fn: Callable, forbidden_names: Sequence[str]) -> None:
    """Source-level guard: the function body must not mention forbidden identifiers."""
    src = inspect.getsource(fn)
    hits = [n for n in forbidden_names if n in src]
    if hits:
        raise AssertionError(f"{fn.__name__} references forbidden names: {hits}")


# ---------------------------------------------------------------- canaries

STATE_CHANNELS = ("feature_tensor", "scaler", "model_coefficients",
                  "tracker_state", "selected_model_metadata", "gate_state")


def mutation_canary(run_fn: Callable[[str | None], Mapping[str, Any]],
                    channels: Sequence[str] = STATE_CHANNELS,
                    observables: Sequence[str] = ("val_ratio", "gate", "m_star"),
                    ) -> dict[str, bool]:
    """Inject future information per channel; each must change an observable.

    Two historical lessons are encoded. First, a canary scoped to "a feature column"
    misses leaks through model, scaler, tracker, selection and gate state -- one such
    leak produced a 14-31 % gain on a null control. Second, a mutation that happens to
    be a NO-OP is not a test: if the poked component is not the selected one, nothing
    changes and "undetectable" is reported where "ineffective" is true. Verify the
    mutation is effective before trusting its detectability.
    """
    clean = run_fn(None)
    out: dict[str, bool] = {}
    for ch in channels:
        m = run_fn(ch)
        out[ch] = any(m.get(k) != clean.get(k) for k in observables)
    return out


# ---------------------------------------------------------------- controls

def negative_control_verdict(gate_open_rates: Mapping[str, float],
                             max_rate: float = 0.20) -> dict[str, Any]:
    """A control with the injected effect set to zero must not admit.

    Two independent failures: a leaked tracker state gave 83-92 % admission, and a
    deterministic secular mismatch surviving zero injection gave 100 % admission with
    a 57-93 % apparent gain. Run the control at EVERY level of the covariate -- the
    second leak was monotone in staleness and invisible at the single level where the
    control had originally been scheduled.
    """
    failing = {k: v for k, v in gate_open_rates.items() if not (v <= max_rate)}
    return {"max_rate": max_rate, "failing_cells": failing,
            "pass": not failing}


def physical_scale_check(residual: np.ndarray, reference_magnitude: np.ndarray,
                         floor: float, ceiling: float) -> dict[str, Any]:
    """Both bounds. A floor alone permitted a 5.8 %-of-signal, 77 km divergence.

    Below `floor` the quantity is finer than the instrument resolves and any apparent
    learning is noise; above `ceiling` the scenario has left physical plausibility.
    Label and RETAIN out-of-range cells; never tune a parameter to move them in.
    """
    r = float(np.median(np.abs(residual)))
    d = float(np.median(np.abs(reference_magnitude)))
    ratio = r / d if d > 0 else float("inf")
    return {"ratio": ratio, "floor": floor, "ceiling": ceiling,
            "label": ("INSUFFICIENT_SCALE" if ratio < floor else
                      "EXCEEDS_PHYSICAL_CEILING" if ratio > ceiling else "IN_RANGE"),
            "pass": floor <= ratio <= ceiling}


def unbounded_divergence_check(times: np.ndarray, residual: np.ndarray,
                               max_late_early_ratio: float = 3.0) -> dict[str, Any]:
    """Late-window vs early-window magnitude. Detects integrating error."""
    o = np.argsort(np.asarray(times, dtype=float))
    a = np.abs(np.asarray(residual, dtype=float))[o]
    h = a.size // 2
    if h < 2:
        return {"ratio": float("nan"), "pass": True}
    ratio = float(np.median(a[h:]) / max(np.median(a[:h]), 1e-12))
    return {"ratio": ratio, "pass": ratio <= max_late_early_ratio}


# ---------------------------------------------------------------- audits

def functional_form_match(X: np.ndarray, y: np.ndarray, train: np.ndarray,
                          test: np.ndarray, term_builder: Callable[[np.ndarray], np.ndarray],
                          threshold: float = 0.95) -> dict[str, Any]:
    """Out-of-sample R2 of an oracle built from admissible terms.

    Replaces a single-feature correlation guard, which read 0.66-0.77 while an oracle
    on two admissible terms reached 0.998 -- so the guard could not see that the
    benchmark's difficulty was set by which features had been omitted. If the match
    exceeds `threshold`, the scenario is a CALIBRATION control and cannot support a
    generalisation claim.
    """
    A = term_builder(X[train])
    w = np.linalg.lstsq(A, y[train], rcond=None)[0]
    p = term_builder(X[test]) @ w
    ss = float(np.sum((y[test] - y[test].mean()) ** 2))
    r2 = float(1.0 - np.sum((y[test] - p) ** 2) / max(ss, 1e-12))
    return {"r2_out_of_sample": r2, "threshold": threshold,
            "classification": ("CONTROLLED CALIBRATION / SANITY SCENARIO"
                               if r2 >= threshold else "not calibration-classified")}


def aggregate_repeated_measures(values: np.ndarray, group_ids: np.ndarray
                                ) -> tuple[np.ndarray, np.ndarray]:
    """Collapse within-group replicates BEFORE any metric or interval.

    Measured within-group ICC ran 0.59-0.79 on real data and up to 0.999 between
    symmetric sample positions, so treating replicates as independent overstated
    precision by roughly the square root of the group size.
    """
    g = np.asarray(group_ids)
    uniq = np.unique(g)
    v = np.asarray(values, dtype=float)
    return uniq, np.array([float(np.mean(v[g == u])) for u in uniq])


def within_group_icc(values: np.ndarray, group_ids: np.ndarray) -> float:
    g, v = np.asarray(group_ids), np.asarray(values, dtype=float)
    grp = [v[g == u] for u in np.unique(g) if int((g == u).sum()) >= 2]
    if len(grp) < 2:
        return float("nan")
    gm = float(np.concatenate(grp).mean())
    sb = float(np.mean([(x.mean() - gm) ** 2 for x in grp]))
    sw = float(np.mean([x.var() for x in grp]))
    return sb / (sb + sw) if sb + sw > 0 else float("nan")


def grid_uniformity_warning(cell_metrics: Mapping[str, Mapping[str, float]],
                            spread_tol: float = 0.01) -> dict[str, Any]:
    """Warn if every cell returns the same answer.

    A grid that varies only NON-correctness axes cannot detect a defect shared by all
    cells: it shows up as uniformity, not as variation. One emulation returned 27 of 27
    cells identical in both reported quantities. Uniformity triggers INSPECTION, never
    an automatic parameter change.
    """
    warn: dict[str, Any] = {}
    keys = {k for m in cell_metrics.values() for k in m}
    for k in keys:
        vals = [m[k] for m in cell_metrics.values() if k in m]
        if not vals:
            continue
        warn[k] = bool(max(vals) - min(vals) <= spread_tol)
    return {"per_metric_uniform": warn, "fires": any(warn.values()),
            "action": "DESIGN INSPECTION -- do not change parameters automatically"}
