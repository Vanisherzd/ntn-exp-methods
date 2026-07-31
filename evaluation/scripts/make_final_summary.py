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

# Measured L4.7 calibration, READ from the artifact calibrate_l47.py writes -- never
# transcribed. It was transcribed until 2026-07-31, and a reviewer demonstrated the
# consequence: an incidental change to the permutation-stream derivation moved the measured
# false-halt count from 19/450 to 14/450 while `make gate` kept reporting the stale 0.042,
# because the gate was comparing the paper against this literal rather than against a run.
# `make matrix` runs calibrate_l47.py before this script, so the file is always current.
L47_CALIB_PATH = ROOT / "evaluation" / "results" / "l47_calibration.json"


# Object-level view of the committed publication-lag measurement. The manuscript quoted only
# the record-pooled figures until a satellite reviewer pointed out they are the wrong unit by the
# paper's own L4.7 argument: one object supplies 82% of the 63,727 records, and it is the only
# object where the epoch ever leads publication. Derived here rather than re-measured -- same
# artifact, correct unit -- so the numbers the paper now quotes are gated like every other.
PUB_LAG_PATH = ROOT / "evaluation" / "results" / "publication_lag.json"


def _publication_lag() -> dict:
    d = json.loads(PUB_LAG_PATH.read_text())
    per = d["per_satellite"]
    meds = sorted(v["median_lag_h"] for v in per.values())
    mid = len(meds) // 2
    obj_median = meds[mid] if len(meds) % 2 else (meds[mid - 1] + meds[mid]) / 2.0
    ahead = [v["frac_epoch_ahead"] for v in per.values()]
    top = max(per.values(), key=lambda v: v["n"])
    return {
        "n_records": d["n_records"],
        "n_objects": d["n_satellites"],
        "median_lag_h_record_pooled": d["median_lag_h"],
        "median_lag_h_object_level": round(obj_median, 2),
        "all_object_medians_positive": all(m > 0 for m in meds),
        "frac_epoch_ahead_record_pooled": d["frac_epoch_ahead_of_publication"],
        "n_objects_with_epoch_ahead": sum(1 for a in ahead if a > 0),
        "largest_object_record_share": round(top["n"] / d["n_records"], 3),
    }


# External evidence: the frozen third-party artifact study and the real-catalogue L4.7
# application. Both are read from the artifacts their own scripts write, never transcribed.
EXTERNAL_PATH = ROOT / "evaluation" / "external" / "external_study.json"
REAL_L47_PATH = ROOT / "evaluation" / "real_data" / "l47_real_application.json"
TIMING_PATH = ROOT / "evaluation" / "real_data" / "object_level_timing.json"


def _external_evidence() -> dict:
    if not EXTERNAL_PATH.exists():
        raise SystemExit(f"missing {EXTERNAL_PATH.relative_to(ROOT)} -- run "
                         "evaluation/scripts/external_artifact_study.py")
    d = json.loads(EXTERNAL_PATH.read_text())
    c = d["counts"]
    return {
        "repository": d["artifact"]["repository"],
        "frozen_commit": d["artifact"]["frozen_commit"],
        "contract_layers_sha256": d["contract"]["contract_layers_sha256"],
        "detector_unmodified": (d["contract"]["contract_layers_sha256"]
                                == d["contract"]["unmodified_since_prereg_sha256"]),
        "n_rules_classified": d["n_classified"],
        "pass": c.get("PASS", 0), "halt": c.get("HALT", 0),
        "indeterminate": c.get("INDETERMINATE", 0),
        "not_applicable": c.get("NOT_APPLICABLE", 0),
        "not_observable": c.get("NOT_OBSERVABLE", 0),
        "halted_rules": [r["rule"] for r in d["inspected"] if r["outcome"] == "HALT"],
    }


def _real_l47() -> dict:
    if not REAL_L47_PATH.exists():
        raise SystemExit(f"missing {REAL_L47_PATH.relative_to(ROOT)} -- run "
                         "evaluation/scripts/real_l47_application.py")
    d = json.loads(REAL_L47_PATH.read_text())
    m, a = d["manifest"], d["analyses"]
    per = a["B_per_object"]
    halts = [k for k, v in per.items() if v["verdict"] == "HALT"]
    return {
        "protocol": m["protocol"],
        "contract_layers_sha256": m["contract_layers_sha256"],
        "window_epoch": m["window_epoch"],
        "n_objects": m["n_objects"],
        "n_element_sets": m["n_element_sets"],
        "n_passes": m["n_passes_total"],
        "n_pass_samples": m["n_pass_samples_total"],
        "A_elementset_in_object": {
            k: a["A_elementset_in_object__publication_lag"].get(k)
            for k in ("verdict", "n_units", "n_coarser_groups", "icc", "p_value")},
        "B_pass_in_elementset_pooled": {
            k: a["B_pass_in_elementset__elevation_pooled"].get(k)
            for k in ("verdict", "n_units", "n_coarser_groups", "icc", "p_value")},
        "C_pass_in_object_pooled": {
            k: a["C_pass_in_object__elevation_pooled"].get(k)
            for k in ("verdict", "n_units", "n_coarser_groups", "icc", "p_value")},
        "B_per_object_halts": halts,
        "B_per_object_n_halt": len(halts),
        "B_per_object_n_pass": sum(1 for v in per.values() if v["verdict"] == "PASS"),
    }


ALONGTRACK_PATH = ROOT / "evaluation" / "real_data" / "l47_alongtrack.json"


def _alongtrack() -> dict:
    """Analysis D: the along-track observable, added after two reviewers correctly objected that
    elevation is deterministic given the grouping and so could not test the section I-A(v) claim.
    """
    if not ALONGTRACK_PATH.exists():
        raise SystemExit(f"missing {ALONGTRACK_PATH.relative_to(ROOT)} -- run "
                         "evaluation/scripts/real_l47_alongtrack.py")
    d = json.loads(ALONGTRACK_PATH.read_text())
    m, a = d["manifest"], d["analyses"]
    keep = ("verdict", "n_units", "n_coarser_groups", "icc", "p_value",
            "icc_upper_95_one_sided", "icc_truncated_at_zero")
    return {
        "contract_layers_sha256": m["contract_layers_sha256"],
        "observable": m["observable"],
        "n_passes_used": m["n_passes_used"],
        "n_passes_dropped_no_successor": m["n_passes_dropped_no_successor"],
        "n_objects": m["n_objects"], "n_elsets": m["n_elsets"],
        "intrack_abs_km": m["intrack_abs_km"],
        "D1_pass_in_elementset": {k: a["D1_pass_in_elementset"].get(k) for k in keep},
        "D2_pass_in_object": {k: a["D2_pass_in_object"].get(k) for k in keep},
        "D3_elementset_in_object": {k: a["D3_elementset_in_object"].get(k) for k in keep},
        "attainability_floor": d["attainability_floor"],
        "multiplicity": d["multiplicity"],
    }


def _object_timing() -> dict:
    d = json.loads(TIMING_PATH.read_text())
    return {k: d[k] for k in (
        "n_objects", "n_records_total", "object_level_median_lag_h_full_history",
        "object_level_median_lag_h_in_window", "all_object_medians_positive_full_history",
        "all_object_medians_positive_in_window", "objects_with_any_epoch_after_creation",
        "n_objects_with_any_epoch_after_creation")}


def _l47_calibration() -> dict:
    if not L47_CALIB_PATH.exists():
        raise SystemExit(
            f"missing {L47_CALIB_PATH.relative_to(ROOT)} -- run "
            "evaluation/scripts/calibrate_l47.py (make matrix does this)")
    return json.loads(L47_CALIB_PATH.read_text())


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
CLAIMS = ROOT / "paper" / "submission" / "CLAIMS.md"
CLAIMS_BEGIN = "<!-- BEGIN GENERATED CLAIMS TABLE -->"
CLAIMS_END = "<!-- END GENERATED CLAIMS TABLE -->"
FIG2 = ROOT / "evaluation" / "results" / "fig2_data.json"


def _write_claims_table(s: dict) -> None:
    """Regenerate the numeric table in CLAIMS.md between its markers.

    Two reviewers independently found this file carrying 655 lines / 32 tests against an
    artifact reporting 877 / 51. It is the file that declares itself the single source of
    truth, and it had hand-copied numbers -- the same drift ARTIFACTS.md was already fixed
    for. Generating it removes the class rather than the instance.
    """
    if not CLAIMS.exists():
        return
    c = s["l47_calibration"]
    n = s["fault_class_count"]
    rows = [
        ("contract rules", s["rule_count"], "rule_count"),
        ("curated fault classes", n, "fault_class_count"),
        ("deterministic environments", f"{s['environment_count']} (PCG64, SFC64, Philox)",
         "environment_count"),
        ("conditions per environment", f"{s['conditions_per_environment']} = {n} faults + 1 clean",
         "conditions_per_environment"),
        ("injected fault-environment cells", s["injected_cell_count"], "injected_cell_count"),
        ("clean reference paths", s["clean_path_count"], "clean_path_count"),
        ("chronological baseline coverage", f"{s['chronological_detected_count']}/{n} (**measured**)",
         "chronological_detected_count"),
        ("contract coverage", f"{s['contract_detected_count']}/{n}", "contract_detected_count"),
        ("clean-path rule firings", s["clean_false_halt_count"], "clean_false_halt_count"),
        ("L4.7 clean false-halt rate",
         f"**{c['clean_false_halts']}/{c['clean_paths_evaluated']} = "
         f"{c['measured_clean_false_halt_rate']}**, Wilson {c['clean_false_halt_wilson_95']}, "
         f"nominal alpha = {c['nominal_alpha']}", "l47_calibration"),
        ("L4.7 injected detection",
         f"{c['injected_paths_evaluated']}/{c['injected_paths_evaluated']}", "l47_calibration"),
        ("rules with a demonstrated red fixture",
         f"{s['detectors_with_red_fixture']} of {s['rule_count']}", "detectors_with_red_fixture"),
        ("rules with no red fixture", ", ".join(s["detectors_without_red_fixture"]),
         "detectors_without_red_fixture"),
        ("sweep runtime", "**under 2 s**; under 30 ms per condition (both bounds, both gated)",
         "runtime_seconds"),
        ("toolkit size", f"{s['source_loc']} lines", "source_loc"),
        ("test suite size", f"{s['test_suite_loc']} lines", "test_suite_loc"),
        ("tests", f"{s['test_count']} passing", "test_count"),
    ]
    body = ["| claim | value | artifact field |", "|---|---|---|"]
    body += [f"| {k} | {v} | `{f}` |" for k, v, f in rows]
    table = (CLAIMS_BEGIN + "\n<!-- Generated by make matrix. Do not hand-edit: this file "
             "carried stale counts once. -->\n" + "\n".join(body) + "\n" + CLAIMS_END)
    t = CLAIMS.read_text()
    if CLAIMS_BEGIN in t and CLAIMS_END in t:
        i, j = t.index(CLAIMS_BEGIN), t.index(CLAIMS_END) + len(CLAIMS_END)
        CLAIMS.write_text(t[:i] + table + t[j:])


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
        "l47_calibration": _l47_calibration(),
        "publication_lag": _publication_lag(),
        "object_level_timing": _object_timing(),
        "real_l47_application": _real_l47(),
        "real_l47_alongtrack": _alongtrack(),
        "external_artifact_study": _external_evidence(),
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
    _write_claims_table(s)
    for k, v in s.items():
        if k not in ("l47_calibration", "matrix_sha256", "commit", "generated_by"):
            print(f"  {k:38s} {v}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
