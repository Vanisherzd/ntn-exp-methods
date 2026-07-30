"""Assert the fault-injection matrix reproduces its committed result.

This is the CI form of the paper's evaluation: it re-runs the full matrix and checks
every acceptance criterion, so a regression in any detector fails the build.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "evaluation" / "results" / "matrix_result.json"
RUNNER = ROOT / "evaluation" / "scripts" / "run_matrix.py"


@pytest.fixture(scope="module")
def committed() -> dict:
    return json.loads(RESULT.read_text())


def test_committed_result_passes_every_criterion(committed):
    assert committed["verdict"] == "PASS"
    for name, ok in committed["acceptance"].items():
        assert ok is True, f"acceptance criterion {name} is not satisfied"


def test_counts_are_self_consistent(committed):
    """The three denominators the paper must keep apart: rules, fault classes, conditions.

    The development/late-specified split is provenance only and carries no evidential
    weight -- it is asserted here so the totals stay honest, not to support a held-out
    claim (withdrawn; see evaluation/mutations/PREREGISTRATION.md).
    """
    n_dev = committed["n_development_faults"]
    n_late = committed["n_late_specified"]
    n_env = len(committed["environments"])
    # 17 = 13 + 4. Was 18 until D12 was found to be the same injection as D3, producing
    # a byte-identical registry; see the threats section.
    assert n_dev + n_late == 17, "fault-class count changed"
    assert n_env == 3
    # 18 conditions per environment = 17 fault classes + 1 clean path
    assert committed["n_rows"] == (n_dev + n_late + 1) * n_env
    assert committed["development_detection"] == f"{n_dev * n_env}/{n_dev * n_env}"
    assert committed["late_specified_detection"] == f"{n_late * n_env}/{n_late * n_env}"
    assert committed["clean_false_positive_rule_firings"] == 0
    assert committed["false_negatives"] == []


def test_every_finding_names_a_registered_rule(committed):
    sys.path.insert(0, str(ROOT / "evaluation" / "scripts"))
    sys.path.insert(0, str(ROOT / "src"))
    import contract_layers as CL

    for row in committed["rows"]:
        for rule in row["fired"]:
            assert rule in CL.RULES, f"{rule} is not a registered contract rule"


def test_matrix_reproduces_from_source():
    """Re-run the evaluation and require the same verdict and detection counts."""
    before = json.loads(RESULT.read_text())
    r = subprocess.run([sys.executable, str(RUNNER)], capture_output=True, text=True,
                       cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    after = json.loads(RESULT.read_text())
    for k in ("verdict", "development_detection", "late_specified_detection",
              "clean_false_positive_rule_firings", "n_rows",
              "clean_verdicts_identical_across_envs"):
        assert after[k] == before[k], f"{k} changed on re-run: {before[k]} -> {after[k]}"
