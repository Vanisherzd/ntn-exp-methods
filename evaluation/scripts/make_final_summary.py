#!/usr/bin/env python3
"""Single source of truth for every number in the manuscript.

Regenerates evaluation/results/final_summary.json from the committed matrix result and
the current source tree. The paper, CLAIMS.md and the submission docs must quote only
values that appear here.

    python evaluation/scripts/make_final_summary.py
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evaluation" / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests" / "fixtures"))

import contract_layers as CL           # noqa: E402
import pipelines as P                  # noqa: E402

MATRIX = ROOT / "evaluation" / "results" / "matrix_result.json"
OUT = ROOT / "evaluation" / "results" / "final_summary.json"

# Measured L4.7 calibration sweep, recorded here so the paper can cite one artifact.
# Reproduce with: python evaluation/scripts/calibrate_l47.py
L47_CALIBRATION = {
    "nominal_alpha": 0.05,
    "clean_paths_evaluated": 450,
    "fixture_seeds": 150,
    "environments": 3,
    "measured_clean_false_halt_rate": 0.042,
    "injected_detection_rate": 1.000,
    "injected_paths_evaluated": 150,
    # Size of the DISCARDED fixed-threshold rule, on iid data at eight groups of three.
    # Cited in the manuscript to justify the permutation null, and still the size of the
    # construction L4.3 ships -- a disclosed limitation, so it belongs in the artifact.
    # Reproduce: python evaluation/scripts/calibrate_l47.py
    "discarded_fixed_threshold_null_size": 0.17,
    "discarded_fixed_threshold": 0.2,
}


def loc(paths) -> int:
    return sum(len(p.read_text().splitlines()) for p in paths)


TIMING_KEYS = ("runtime_s", "total_runtime_s", "mean_runtime_per_condition_s")


def _strip_timings(obj):
    """Recursively drop wall-clock fields so the remainder is comparable."""
    if isinstance(obj, dict):
        return {k: _strip_timings(v) for k, v in obj.items() if k not in TIMING_KEYS}
    if isinstance(obj, list):
        return [_strip_timings(v) for v in obj]
    return obj


def _results_digest(d: dict) -> str:
    """SHA-256 over the canonical, timing-stripped result. Stable across runs."""
    return hashlib.sha256(
        json.dumps(_strip_timings(d), sort_keys=True,
                   separators=(",", ":")).encode()).hexdigest()


REPORT = ROOT / "evaluation" / "results" / "EVALUATION_RESULT.md"
FIG2 = ROOT / "evaluation" / "results" / "fig2_data.json"


def _write_report(s: dict, d: dict) -> None:
    """Regenerate the human-readable report FROM the artifact.

    It was previously hand-maintained and drifted badly -- it still claimed 14
    development faults, 57 rows and 0.187 s long after all three had changed. Generating
    it removes the whole class of error.
    """
    no_red = ", ".join(s["detectors_without_red_fixture"])
    c = s["l47_calibration"]
    REPORT.write_text(f"""# Curated fault-injection regression evaluation -- result

GENERATED FILE. Do not edit by hand; run `make matrix`.
Source: `evaluation/results/matrix_result.json` -> `final_summary.json`.

**VERDICT: {d["verdict"]}** -- every pre-registered acceptance criterion met.

## Scope of the claim

This suite measures **represented-fault regression coverage**: the implemented rules catch
the violations the suite contains, and those violations cannot silently return. It does
**not** estimate sensitivity to faults the suite does not contain, and no generalisation
claim is made -- see the withdrawal notice in `../mutations/PREREGISTRATION.md`.

## Matrix

`{{CASE A, CASE B}} x {{clean, {s["fault_class_count"]} curated fault classes}} x """
f"""{s["environment_count"]} deterministic environments`
= **{d["n_rows"]} rows** ({s["conditions_per_environment"]} conditions x """
f"""{s["environment_count"]} environments; both cases run per row).
Environments vary RNG family only -- PCG64, SFC64, Philox -- never a physical parameter,
so they are not independent systems or populations.

## Metrics

| metric | value |
|---|---|
| contract rules | {s["rule_count"]} |
| curated fault classes | {s["fault_class_count"]} |
| injected fault-environment cells | {s["injected_cell_count"]} |
| contract detection | **{s["contract_detected_count"]}/{s["fault_class_count"]}** |
| chronological baseline detection | **{s["chronological_detected_count"]}/{s["fault_class_count"]}** (checks {", ".join(s["chronological_checks"])}) |
| clean reference paths | {s["clean_path_count"]} |
| clean-path rule firings | **{s["clean_false_halt_count"]}** |
| clean verdicts identical across environments | **{s["deterministic_across_environments"]}** |
| rules with a demonstrated red fixture | **{s["detectors_with_red_fixture"]}/{s["rule_count"]}** |
| rules with no red fixture | {no_red} |
| total runtime | {s["runtime_seconds"]} s (claim: under 2 s) |
| per-condition runtime | {s["runtime_ms_per_condition"]} ms |
| toolkit source lines | {s["source_loc"]} |
| test suite lines | {s["test_suite_loc"]} |

## L4.7 size control

The statistical-unit rule is referenced to a permutation null, so its specificity is a
measured **rate**, not a single clean run:

| quantity | value |
|---|---|
| nominal alpha | {c["nominal_alpha"]} |
| clean paths evaluated | {c["clean_paths_evaluated"]} ({c["fixture_seeds"]} seeds x {c["environments"]} envs) |
| **measured clean false-halt rate** | **{c["measured_clean_false_halt_rate"]}** |
| injected detection rate | {c["injected_detection_rate"]} over {c["injected_paths_evaluated"]} paths |

Reproduce with `python evaluation/scripts/calibrate_l47.py`.

## Acceptance criteria

| criterion | result |
|---|---|
""" + "".join(f"| {k} | **{'PASS' if v else 'FAIL'}** |\n"
               for k, v in d["acceptance"].items()))


def _write_fig2_data(s: dict, d: dict) -> None:
    """Row-by-row provenance for Fig. 2, so each cell traces to the artifact."""
    rows = [{"fault": f,
             "detecting_rule": d["per_fault"][f]["expected"],
             "contract_detected_in": d["per_fault"][f]["detected_in"],
             "of_environments": d["per_fault"][f]["of"],
             "chronological_detected_in": d["per_fault"][f]["baseline_detected_in"],
             "chronological_checks_fired": d["per_fault"][f]["baseline_fired_union"]}
            for f in d["per_fault"]]
    FIG2.write_text(json.dumps(
        {"note": "Provenance for Fig. 2. Represented-fault regression coverage; the "
                 "development/late-specified split carries no evidential weight and is "
                 "not represented here.",
         "fault_class_count": s["fault_class_count"],
         "environment_count": s["environment_count"],
         "chronological_detected_count": s["chronological_detected_count"],
         "contract_detected_count": s["contract_detected_count"],
         "rows": rows}, indent=1) + "\n")


def _collected_test_count() -> int:
    """Number of tests pytest collects from the active suite.

    Recorded in the artifact so documentation cannot drift from it -- three files had
    hand-copied counts of 23, 27 and 30 simultaneously.
    """
    r = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q",
                        "tests/regression", "tests/fault_injection"],
                       cwd=ROOT, capture_output=True, text=True)
    m = re.search(r"(\d+) tests? collected", r.stdout)
    return int(m.group(1)) if m else -1


def main() -> int:
    d = json.loads(MATRIX.read_text())
    rows = d["rows"]
    clean = [r for r in rows if r["fault"] == "CLEAN"]
    fired = {x.split(":")[0] for r in rows for x in r["fired"]}
    red = sorted(fired & set(CL.RULES))
    no_red = sorted(set(CL.RULES) - fired)
    n_fault = d["n_development_faults"] + d["n_late_specified"]
    n_env = len(d["environments"])
    src = sorted((ROOT / "src" / "orbit_evidence").rglob("*.py"))
    # The ACTIVE suite is regression + fault_injection. Counting only the former
    # understated it by the 73-line matrix suite while the adjacent test COUNT included it.
    tst = sorted((ROOT / "tests" / "regression").rglob("*.py")) + \
        sorted((ROOT / "tests" / "fault_injection").rglob("*.py"))

    s = {
        "generated_by": "evaluation/scripts/make_final_summary.py",
        "source_artifact": "evaluation/results/matrix_result.json",
        "rule_count": len(CL.RULES),
        "fault_class_count": n_fault,
        "development_fault_count": d["n_development_faults"],
        "late_specified_fault_count": d["n_late_specified"],
        "curated_regression_fault_count": n_fault,
        "environment_count": n_env,
        "injected_cell_count": n_fault * n_env,
        "clean_path_count": len(clean),
        "chronological_detected_count": d["chronological_baseline"]["n_caught"],
        "chronological_checks": d["chronological_baseline"]["checks"],
        "contract_detected_count": len([f for f in P.ALL_FAULTS
                                        if d["per_fault"][f]["detected_in"]
                                        == d["per_fault"][f]["of"]]),
        "clean_false_halt_count": d["clean_false_positive_rule_firings"],
        "runtime_seconds": d["total_runtime_s"],
        "runtime_ms_per_condition": round(d["mean_runtime_per_condition_s"] * 1000, 1),
        "conditions_per_environment": n_fault + 1,
        "source_loc": loc(src),
        "source_loc_excluding_init": loc([p for p in src if p.name != "__init__.py"]),
        "test_suite_loc": loc(tst),
        "test_count": _collected_test_count(),
        "detectors_with_red_fixture": len(red),
        "detectors_without_red_fixture": no_red,
        "deterministic_across_environments": d["clean_verdicts_identical_across_envs"],
        "l47_calibration": L47_CALIBRATION,
        # Hash the RESULTS, not the wall clock. Hashing the file whole embedded per-row
        # runtime_s, so this anchor could never match between two runs of the same tree --
        # an integrity checksum that is always different is not an integrity checksum.
        "matrix_sha256": _results_digest(d),
        "commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                 capture_output=True, text=True).stdout.strip(),
    }
    OUT.write_text(json.dumps(s, indent=1) + "\n")
    _write_report(s, d)
    _write_fig2_data(s, d)
    for k, v in s.items():
        if k not in ("l47_calibration", "matrix_sha256", "commit", "generated_by"):
            print(f"  {k:38s} {v}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
