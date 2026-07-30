#!/usr/bin/env python3
"""Loop 3 -- fault-injection evaluation.

Runs {CASE A, CASE B} x {clean, 14 development faults, 4 held-out mutations} x
{3 deterministic environments} and reports which contract rule fired.

The detectors are frozen. Whatever the held-out mutations produce is the answer; no
detector is edited after its held-out result is inspected.
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tests" / "fixtures"))
sys.path.insert(0, str(ROOT / "src"))

import chronological_baseline as CB  # noqa: E402
import contract_layers as CL     # noqa: E402
import pipelines as P            # noqa: E402

# expected rule per fault, declared in the pre-registration
EXPECTED: dict[str, str] = {
    "D1": "L1.1", "D2": "L1.2", "D3": "L1.4", "D4": "L2.1", "D5": "L1.3",
    "D6": "L3.1", "D7": "L4.2", "D8": "L3.3", "D9": "L3.1", "D10": "L3.1",
    "D11": "L4.3", "D13": "L4.1", "D14": "L4.4",
    "HO1": "L1.5", "HO2": "L4.6", "HO3": "L4.7", "HO4": "L2.4",
}
HIGH_SEVERITY = {"D1", "D2", "D3", "D4", "D5", "D6", "D8", "D9", "D10",
                 "D13", "D14"}


@contextlib.contextmanager
def _env_var(name: str, value: str):
    old = os.environ.get(name)
    if value:
        os.environ[name] = value
    else:
        os.environ.pop(name, None)
    try:
        yield
    finally:
        if old is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = old


def run_case_a(fault: str | None, env: P.Env) -> list[str]:
    """Apply every CASE A check. Returns the rule IDs that fired."""
    c = P.build_case_a(fault, env)
    fired: list[str] = []

    def run(fn: Callable, *a, **k) -> None:
        try:
            fn(*a, **k)
        except CL.ContractViolation as v:
            fired.append(v.rule)

    run(CL.check_feature_availability, c.feature_fn, [20.0, 60.0, 120.0],
        c.truncate_at, c.restore)
    run(CL.check_availability_clock, c.descriptive, c.published,
        c.t_decision, c.selected_index)
    run(CL.check_label_closure, c.closure, c.closure_decision, c.used_mask)
    run(CL.check_row_membership, c.build_fn, c.window, c.full_source, c.trunc_source)
    run(CL.probe_comparison_boundary, c.admit_fn)
    run(CL.check_sampling_geometry, c.elevations, P.MASK_DEG)
    run(CL.check_physical_scale, c.residual, c.reference_mag, 0.002, 0.02)
    run(CL.check_bounded_state, c.state_times, c.state_quantity)
    run(CL.check_declared_relation, c.declared, c.implemented, c.domain)

    def prov(cfg):
        with _env_var("ORBIT_EVIDENCE_PROBE", cfg.get("_env", "")):
            return c.manifest_run_fn(cfg)

    run(CL.check_provenance_completeness, prov, c.manifest_variations)
    return fired


def baseline_case_a(fault: str | None, env: P.Env) -> list[str]:
    return CB.run_baseline_case_a(P.build_case_a(fault, env))


def baseline_case_b(fault: str | None, env: P.Env) -> list[str]:
    return CB.run_baseline_case_b(P.build_case_b(fault, env))


def run_case_b(fault: str | None, env: P.Env) -> list[str]:
    c = P.build_case_b(fault, env)
    fired: list[str] = []

    def run(fn: Callable, *a, **k) -> None:
        try:
            fn(*a, **k)
        except CL.ContractViolation as v:
            fired.append(v.rule)

    for ch in ("feature_tensor", "scaler", "model_coefficients", "tracker_state",
               "selected_model_metadata", "gate_state"):
        run(CL.assert_canary_effective, c.run_fn, ch)
    run(CL.check_state_channels, c.run_fn)
    run(CL.check_negative_control, c.control_rates)
    run(CL.check_chronology, c.fold, c.times)
    run(CL.check_paired_conditions, c.paired, c.paired_mask)
    run(CL.check_repeated_measures, c.y, c.pass_ids, c.aggregated)
    run(CL.check_seed_hygiene, c.seed_registry, c.about_to_run)
    run(CL.check_provenance_hashes, c.manifest)
    # L4.7 returns a verdict dict; INDETERMINATE must be recorded, not discarded,
    # or a rule that declined to judge is indistinguishable from one that passed.
    try:
        verdict = CL.check_statistical_unit(c.y, c.unit_ids, c.coarser_ids)
        if verdict.get("verdict") == "INDETERMINATE":
            fired.append("L4.7:INDETERMINATE")
    except CL.ContractViolation as v:
        fired.append(v.rule)
    return fired


def main() -> int:
    conditions: list[str | None] = [None, *P.ALL_FAULTS]
    rows: list[dict[str, Any]] = []
    t_start = time.perf_counter()
    for env in P.ENVS:
        for cond in conditions:
            t0 = time.perf_counter()
            fired = sorted(set(run_case_a(cond, env) + run_case_b(cond, env)))
            base = sorted(set(baseline_case_a(cond, env) + baseline_case_b(cond, env)))
            dt = time.perf_counter() - t0
            exp = EXPECTED.get(cond) if cond else None
            rows.append({"env": env.name, "fault": cond or "CLEAN",
                         "fired": fired, "expected": exp,
                         "detected": bool(exp and exp in fired),
                         "extra": [r for r in fired if r != exp],
                         "baseline_fired": base,
                         "baseline_detected": bool(cond and base),
                         "runtime_s": round(dt, 4)})
    total_s = time.perf_counter() - t_start

    # ---- metrics ----------------------------------------------------------
    clean = [r for r in rows if r["fault"] == "CLEAN"]
    dev = [r for r in rows if r["fault"] in P.DEV_FAULTS]
    ho = [r for r in rows if r["fault"] in P.HELD_OUT]
    fp = sum(len(r["fired"]) for r in clean)
    dev_det = sum(r["detected"] for r in dev)
    ho_det = sum(r["detected"] for r in ho)
    high = [r for r in dev if r["fault"] in HIGH_SEVERITY]
    verdicts = {r["env"]: tuple(r["fired"]) for r in clean}
    deterministic = len(set(verdicts.values())) == 1

    per_fault: dict[str, dict[str, Any]] = {}
    for f in P.ALL_FAULTS:
        rs = [r for r in rows if r["fault"] == f]
        per_fault[f] = {"expected": EXPECTED[f],
                        "detected_in": sum(r["detected"] for r in rs),
                        "of": len(rs),
                        "fired_union": sorted({x for r in rs for x in r["fired"]}),
                        "extra_union": sorted({x for r in rs for x in r["extra"]}),
                        "baseline_detected_in": sum(r["baseline_detected"] for r in rs),
                        "baseline_fired_union": sorted(
                            {x for r in rs for x in r["baseline_fired"]})}

    out = {
        "n_rows": len(rows), "environments": [e.name for e in P.ENVS],
        "n_development_faults": len(P.DEV_FAULTS), "n_held_out": len(P.HELD_OUT),
        "clean_false_positive_rule_firings": fp,
        "clean_verdicts_identical_across_envs": deterministic,
        "development_detection": f"{dev_det}/{len(dev)}",
        "high_severity_detection": f"{sum(r['detected'] for r in high)}/{len(high)}",
        "held_out_detection": f"{ho_det}/{len(ho)}",
        "false_negatives": [r["fault"] for r in rows if r["expected"] and not r["detected"]],
        "total_runtime_s": round(total_s, 3),
        "mean_runtime_per_condition_s": round(total_s / max(len(rows), 1), 4),
        "per_fault": per_fault,
        "rows": rows,
    }
    acc = {
        "1_all_high_severity_detected": sum(r["detected"] for r in high) == len(high),
        "2_all_held_out_detected": ho_det == len(ho),
        "3_zero_clean_false_positives": fp == 0,
        "4_identical_clean_verdicts": deterministic,
        "5_runtime_measured": True,
        "6_findings_name_a_rule": all(
            all(x.split(":")[0] in CL.RULES for x in r["fired"]) for r in rows),
    }
    base_caught = [f for f in P.ALL_FAULTS if per_fault[f]["baseline_detected_in"] > 0]
    out["chronological_baseline"] = {
        "scope": CB.BASELINE_SCOPE,
        "checks": list(CB.BASELINE_CHECKS),
        "faults_caught": base_caught,
        "n_caught": len(base_caught),
        "n_fault_classes": len(P.ALL_FAULTS),
        "clean_path_firings": sum(len(r["baseline_fired"]) for r in clean),
        "per_fault": {f: per_fault[f]["baseline_fired_union"] for f in P.ALL_FAULTS},
    }
    out["acceptance"] = acc
    out["verdict"] = "PASS" if all(acc.values()) else "FAIL"

    (ROOT / "evaluation" / "results" / "matrix_result.json").write_text(json.dumps(out, indent=1))
    print(f"rows={len(rows)}  envs={len(P.ENVS)}  runtime={total_s:.2f}s "
          f"({out['mean_runtime_per_condition_s']*1000:.1f} ms/condition)")
    print(f"clean false-positive rule firings: {fp}")
    print(f"clean verdicts identical across envs: {deterministic}")
    print(f"development detection: {out['development_detection']}   "
          f"high-severity: {out['high_severity_detection']}")
    print(f"HELD-OUT detection: {out['held_out_detection']}")
    if out["false_negatives"]:
        print(f"FALSE NEGATIVES: {sorted(set(out['false_negatives']))}")
    print(f"\n{'fault':6s} {'expect':7s} {'det':>5s}  fired")
    for f in P.ALL_FAULTS:
        d = per_fault[f]
        mark = "*" if f in P.HELD_OUT else " "
        print(f"{mark}{f:5s} {d['expected']:7s} {d['detected_in']}/{d['of']}  "
              f"{d['fired_union']}")
    print("\nacceptance:")
    for k, v in acc.items():
        print(f"  {k:34s} {'PASS' if v else 'FAIL'}")
    print(f"\nVERDICT: {out['verdict']}")
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
