"""Contract tests for the Paper 1+ multi-satellite generalization campaign.

Passes in both campaign states: the current `insufficient_data` dry run and a
future populated run. Nothing here asserts a scientific result.
"""

from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Final

ROOT: Final = Path(__file__).resolve().parents[1]
EXP: Final = ROOT / "experiments/exp14_multisat_generalization_matrix"
DOCS: Final = ROOT / "docs/paper1_plus/generalization"

RESULTS: Final = EXP / "results.json"
MATRIX_CSV: Final = EXP / "multisat_generalization_matrix.csv"
PER_SAT_CSV: Final = EXP / "per_satellite_summary.csv"
REJECT_CSV: Final = EXP / "reject_sensitivity_summary.csv"

REPORTS: Final = (
    DOCS / "TLE_DATA_INVENTORY.md",
    DOCS / "GENERALIZATION_STRESS_TEST_REPORT.md",
    DOCS / "CURRENT_PAPER_INTEGRATION_DECISION.md",
)

VALID_GATE: Final = {"open", "closed", "unavailable"}
VALID_STATUS: Final = {"evaluated", "insufficient_pairs"}
NUMERIC_KEYS: Final = (
    "val_mae_phys_hz",
    "val_mae_ml_hz",
    "baseline_test_mae_hz",
    "learned_test_mae_hz",
    "degradation_pct",
    "p95_abs_error_hz",
    "p99_abs_error_hz",
)

sys.path.insert(0, str(EXP))
import run_multisat_generalization_matrix as runner  # noqa: E402


def _load() -> dict[str, Any]:
    return json.loads(RESULTS.read_text(encoding="utf-8"))


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_result_files_exist_and_parse() -> None:
    for path in (RESULTS, MATRIX_CSV, PER_SAT_CSV, REJECT_CSV):
        assert path.exists(), path
    assert isinstance(_load(), dict)
    for path in (MATRIX_CSV, PER_SAT_CSV, REJECT_CSV):
        _rows(path)


def test_metadata_declares_software_only_scope() -> None:
    meta = _load()["metadata"]
    assert meta["reference_is_measured_truth"] is False
    assert meta["hardware_used"] is False
    assert meta["rf_used"] is False
    assert "measured" not in str(meta["scope"]).lower() or "not" in str(
        meta["scope"]
    ).lower()


def test_gate_decisions_use_declared_values() -> None:
    for row in _load()["matrix_rows"]:
        assert row["status"] in VALID_STATUS, row["status"]
        assert row["gate_decision"] in VALID_GATE, row["gate_decision"]
        if row["status"] != "evaluated":
            assert row["gate_decision"] == "unavailable"


def test_evaluated_rows_have_no_nan_in_key_metrics() -> None:
    for row in _load()["matrix_rows"]:
        if row["status"] != "evaluated":
            continue
        for key in NUMERIC_KEYS:
            value = row.get(key)
            assert value is not None, (key, row["train_source"])
            assert math.isfinite(float(value)), (key, value)
        for key in ("n_train_pairs", "n_val_pairs", "n_test_pairs"):
            assert int(row[key]) > 0, (key, row[key])


def test_gate_matches_validation_margin_when_evaluated() -> None:
    """G must follow Eq. (6) on validation, never from test values."""
    for row in _load()["matrix_rows"]:
        if row["status"] != "evaluated":
            continue
        expected = float(row["val_mae_ml_hz"]) < float(row["gamma"]) * float(
            row["val_mae_phys_hz"]
        )
        assert row["gate_decision"] == ("open" if expected else "closed"), row


def test_dry_run_state_is_explicit_when_data_is_insufficient() -> None:
    meta = _load()["metadata"]
    found = int(meta["satellites_found"])
    minimum = int(meta["min_satellites_for_generalization_claim"])
    if found >= minimum:
        assert meta["dry_run"] is False
        return
    assert meta["dry_run"] is True
    joined = " ".join(_load()["notes"]).lower()
    assert "no generalization claim" in joined or "no multi-satellite" in joined


def test_reports_do_not_claim_measured_or_rf_evidence() -> None:
    forbidden = (
        r"\bmeasured Doppler truth\b(?!\s*(is|:)?\s*(false|absent))",
        r"\bPER\b",
        r"\bPDR\b",
        r"\bCRC\b",
        r"\bOTA\b",
        r"\bLR1131\b",
    )
    for path in REPORTS:
        text = path.read_text(encoding="utf-8")
        assert "reference_is_measured_truth" in text, path.name
        for pattern in forbidden[1:]:
            assert re.search(pattern, text) is None, (path.name, pattern)
        for line in text.splitlines():
            low = line.lower()
            if "measured doppler" in low or "measured rf" in low:
                assert any(
                    marker in low
                    for marker in ("no ", "not ", "false", "without", "never")
                ), (path.name, line)


def test_reports_state_insufficient_data_when_below_threshold() -> None:
    meta = _load()["metadata"]
    if int(meta["satellites_found"]) >= int(
        meta["min_satellites_for_generalization_claim"]
    ):
        return
    report = (DOCS / "GENERALIZATION_STRESS_TEST_REPORT.md").read_text(
        encoding="utf-8"
    )
    assert "dry run" in report.lower()
    assert "insufficient data" in report.lower()


def test_stale_partner_selection_picks_closest_gap_in_band() -> None:
    import datetime as dt

    t0 = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
    epochs = [t0 + dt.timedelta(hours=6 * k) for k in range(10)]
    # Target 24 h, band [16, 36]: from index 9 the closest gap is index 5.
    assert runner.select_stale_partner(epochs, 9, 24.0, 16.0, 36.0) == 5
    # No partner exists inside a band that starts beyond the whole history.
    assert runner.select_stale_partner(epochs, 2, 168.0, 144.0, 192.0) is None


def test_ridge_recovers_a_known_linear_map() -> None:
    import numpy as np

    rng = np.random.default_rng(0)
    x = rng.normal(size=(400, 3))
    true_w = np.array([2.0, -1.0, 0.5])
    y = x @ true_w + 0.25
    w = runner._ridge_weights(x, y, alpha=1e-6)
    assert np.allclose(w[:3], true_w, atol=1e-3)
    assert abs(w[3] - 0.25) < 1e-3
