"""Contract tests for the Paper 1+ multi-satellite generalization campaign.

Passes in both campaign states: the current `insufficient_data` dry run and a
future populated run. Nothing here asserts a scientific result.

The invariants that matter most are the protocol ones (Phase 0): the gate must
be reproducible from validation metrics alone, the test split must never decide
anything, transfer cells must validate on the target, and pair identity must
survive every export.
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
TARGET_CSV: Final = EXP / "TARGET_SPECIFIC_LEARNABILITY.csv"
PAIR_CSV: Final = EXP / "pair_level_metrics.csv"
REJECTED_CSV: Final = EXP / "rejected_pairs.csv"
PER_SAT_CSV: Final = EXP / "per_satellite_summary.csv"
REJECT_CSV: Final = EXP / "reject_sensitivity_summary.csv"
GATE_AGREE_CSV: Final = EXP / "gate_metric_agreement.csv"
MANIFEST: Final = EXP / "data_manifest.json"
SCHEMA: Final = ROOT / "data/schemas/tle_data_manifest.schema.json"

ALL_CSVS: Final = (
    MATRIX_CSV,
    TARGET_CSV,
    PAIR_CSV,
    REJECTED_CSV,
    PER_SAT_CSV,
    REJECT_CSV,
    GATE_AGREE_CSV,
)

REPORTS: Final = tuple(sorted(DOCS.glob("*.md")))

VALID_GATE: Final = {"open", "closed", "unavailable"}
VALID_STATUS: Final = {"evaluated", "insufficient_pairs"}
NUMERIC_KEYS: Final = (
    "val_mae_phys_hz",
    "val_mae_ml_hz",
    "baseline_test_mae_hz",
    "learned_test_mae_hz",
    "degradation_pct",
    "pair_win_rate",
    "mean_pair_mae_delta_hz",
    "boot_ci_low_hz",
    "boot_ci_high_hz",
    "sign_test_p",
)
PAIR_IDENTITY_KEYS: Final = (
    "pair_id",
    "satellite",
    "stale_epoch_utc",
    "ref_epoch_utc",
    "actual_staleness_h",
    "band_h",
    "first_sample_utc",
    "last_sample_utc",
)

sys.path.insert(0, str(EXP))
import run_multisat_generalization_matrix as runner  # noqa: E402


def _load() -> dict[str, Any]:
    return json.loads(RESULTS.read_text(encoding="utf-8"))


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _evaluated() -> list[dict[str, Any]]:
    return [r for r in _load()["matrix_rows"] if r["status"] == "evaluated"]


# ---------------------------------------------------------------- artifacts


def test_all_result_files_exist_and_parse() -> None:
    assert RESULTS.exists()
    assert isinstance(_load(), dict)
    for path in ALL_CSVS:
        assert path.exists(), path
        _rows(path)
    assert isinstance(json.loads(MANIFEST.read_text(encoding="utf-8")), list)


def test_metadata_declares_software_only_scope() -> None:
    meta = _load()["metadata"]
    assert meta["reference_is_measured_truth"] is False
    assert meta["hardware_used"] is False
    assert meta["rf_used"] is False
    assert "not measured RF truth" in meta["scope"]


def test_metadata_records_the_unified_protocol() -> None:
    proto = _load()["metadata"]["unified_protocol"]
    assert proto["target_specific"] == "train_A -> validation_A -> test_A"
    assert proto["transfer"] == "train_A -> validation_B -> test_B"
    assert proto["selection_split"] == "target validation"
    assert proto["gate_split"] == "target validation"
    assert "never" in proto["test_role"]
    assert proto["experimental_unit"] == "accepted TLE pair"
    assert proto["single_code_path"] is True


def test_old_transfer_protocol_is_declared_superseded() -> None:
    assert "NOT" in _load()["metadata"]["supersedes"]


def test_manifest_matches_schema_shape() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required = set(schema["items"]["required"])
    for entry in json.loads(MANIFEST.read_text(encoding="utf-8")):
        assert required <= set(entry), required - set(entry)
        assert entry["reference_is_measured_truth"] is False


# ---------------------------------------------------------------- protocol


def test_gate_decisions_use_declared_values() -> None:
    for row in _load()["matrix_rows"]:
        assert row["status"] in VALID_STATUS, row["status"]
        for key in ("gate_decision",) + tuple(
            f"gate_{g}" for g in runner.GATE_OBJECTIVES
        ):
            assert row[key] in VALID_GATE, (key, row[key])
        if row["status"] != "evaluated":
            assert row["gate_decision"] == "unavailable"


def test_validation_decides_the_gate_and_test_never_does() -> None:
    """G must be reproducible from validation metrics alone (Eq. 6)."""
    for row in _evaluated():
        phys = float(row["val_mae_phys_hz"])
        ml = float(row["val_mae_ml_hz"])
        expected = "closed" if phys <= 0 else (
            "open" if ml < float(row["gamma"]) * phys else "closed"
        )
        assert row["gate_mae"] == expected, row
        if row["gamma"] == _load()["metadata"]["gamma"] and (
            _load()["metadata"]["primary_gate"] == "mae"
        ):
            assert row["gate_decision"] == expected, row


def test_gate_is_independent_of_test_metrics() -> None:
    """Perturbing only test metrics must not change any recorded decision."""
    for row in _evaluated():
        recomputed = runner.evaluate_gates(
            {
                "mae": float(row["val_mae_phys_hz"]),
                "p95": float(row["val_p95_phys_hz"]),
                "p99": float(row["val_p99_phys_hz"]),
                "outage": float(row["val_outage_phys"]),
            },
            {
                "mae": float(row["val_mae_ml_hz"]),
                "p95": float(row["val_p95_ml_hz"]),
                "p99": float(row["val_p99_ml_hz"]),
                "outage": float(row["val_outage_ml"]),
            },
            _Args(_load()["metadata"]),
        )
        for objective in runner.GATE_OBJECTIVES:
            assert row[f"gate_{objective}"] == recomputed[objective], (row, objective)


class _Args:
    """Minimal stand-in carrying the gate parameters from run metadata."""

    def __init__(self, meta: dict[str, Any]) -> None:
        self.gamma = meta["gamma"]
        self.alpha_g = meta["alpha_g"]
        self.hop_bandwidth_hz = meta["hop_bandwidth_hz"]


def test_transfer_cells_validate_and_test_on_the_target() -> None:
    pair_rows = _load()["pair_rows"]
    for row in pair_rows:
        assert row["satellite"] == row["deploy_target"], row
        if row["train_source"] != row["deploy_target"]:
            assert row["relation"] == "cross_satellite", row
        else:
            assert row["relation"] == "target_specific", row


def test_no_pair_leaks_between_validation_and_test() -> None:
    by_cell: dict[tuple[str, str], dict[str, set[str]]] = {}
    for row in _load()["pair_rows"]:
        cell = (row["train_source"], row["deploy_target"])
        splits = by_cell.setdefault(cell, {"validation": set(), "test": set()})
        splits[row["split"]].add(row["pair_id"])
    for cell, splits in by_cell.items():
        assert not (splits["validation"] & splits["test"]), cell


# ---------------------------------------------------------------- pair level


def test_pair_identity_is_preserved_in_exports() -> None:
    for row in _load()["pair_rows"]:
        for key in PAIR_IDENTITY_KEYS:
            assert str(row.get(key, "")).strip(), (key, row.get("pair_id"))
        assert row["pair_id"].count("|") == 2, row["pair_id"]
        assert int(row["n_samples"]) == runner.K_SAMPLES_PER_PAIR


def test_pair_level_metrics_exist_and_are_finite() -> None:
    for row in _load()["pair_rows"]:
        for key in (
            "baseline_mae_hz",
            "learned_mae_hz",
            "baseline_p95_hz",
            "learned_p95_hz",
            "baseline_p99_hz",
            "learned_p99_hz",
            "baseline_outage_proxy",
            "learned_outage_proxy",
        ):
            assert math.isfinite(float(row[key])), (key, row["pair_id"])
        assert row["pair_outcome"] in {"learned_win", "learned_loss", "tie"}


def test_rejected_pairs_carry_a_reason() -> None:
    valid = {"residual_cap", "sgp4_propagation_error", "tle_parse_error"}
    for row in _load()["rejected_rows"]:
        assert row["reject_reason"] in valid, row
        assert str(row.get("pair_id", "")).strip()


def test_evaluated_rows_have_no_nan_in_key_metrics() -> None:
    for row in _evaluated():
        for key in NUMERIC_KEYS:
            value = row.get(key)
            assert value is not None, (key, row["train_source"])
            assert math.isfinite(float(value)), (key, value)
        for key in ("n_train_pairs", "n_val_pairs", "n_test_pairs"):
            assert int(row[key]) > 0, (key, row[key])


def test_pair_counts_agree_between_matrix_and_pair_export() -> None:
    pair_rows = _load()["pair_rows"]
    for row in _evaluated():
        cell = [
            p
            for p in pair_rows
            if p["train_source"] == row["train_source"]
            and p["deploy_target"] == row["deploy_target"]
            and p["pair_id"].split("|")[1] == f"{row['staleness_h']}h"
        ]
        n_val = sum(1 for p in cell if p["split"] == "validation")
        n_test = sum(1 for p in cell if p["split"] == "test")
        assert n_val == int(row["n_val_pairs"]), row
        assert n_test == int(row["n_test_pairs"]), row


# ---------------------------------------------------------------- dry run


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


def test_reports_state_insufficient_data_when_below_threshold() -> None:
    meta = _load()["metadata"]
    if int(meta["satellites_found"]) >= int(
        meta["min_satellites_for_generalization_claim"]
    ):
        return
    for name in ("GENERALIZATION_STRESS_TEST_REPORT.md", "DATASET_DESIGN.md"):
        text = (DOCS / name).read_text(encoding="utf-8").lower()
        assert "dry run" in text or "not executed" in text, name


# ---------------------------------------------------------------- claims


def test_reports_do_not_claim_measured_or_rf_evidence() -> None:
    forbidden = (r"\bPER\b", r"\bPDR\b", r"\bCRC\b", r"\bOTA\b", r"\bLR1131\b")
    for path in REPORTS:
        text = path.read_text(encoding="utf-8")
        assert "reference_is_measured_truth" in text, path.name
        for pattern in forbidden:
            assert re.search(pattern, text) is None, (path.name, pattern)
        for line in text.splitlines():
            low = line.lower()
            if "measured doppler" in low or "measured rf" in low:
                assert any(
                    marker in low
                    for marker in ("no ", "not ", "false", "without", "never")
                ), (path.name, line)


# ---------------------------------------------------------------- unit


def test_stale_partner_selection_picks_closest_gap_in_band() -> None:
    import datetime as dt

    t0 = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
    epochs = [t0 + dt.timedelta(hours=6 * k) for k in range(10)]
    assert runner.select_stale_partner(epochs, 9, 24.0, 16.0, 36.0) == 5
    assert runner.select_stale_partner(epochs, 2, 168.0, 144.0, 192.0) is None


def test_ridge_recovers_a_known_linear_map() -> None:
    import numpy as np

    rng = np.random.default_rng(0)
    x = rng.normal(size=(400, 3))
    true_w = np.array([2.0, -1.0, 0.5])
    w = runner._ridge_weights(x, x @ true_w + 0.25, alpha=1e-6)
    assert np.allclose(w[:3], true_w, atol=1e-3)
    assert abs(w[3] - 0.25) < 1e-3


def test_gate_stays_closed_when_the_baseline_is_already_perfect() -> None:
    """A zero physics metric cannot be beaten by a margin -- never a false open."""
    meta = _load()["metadata"]
    zeros = {"mae": 0.0, "p95": 0.0, "p99": 0.0, "outage": 0.0}
    decisions = runner.evaluate_gates(zeros, zeros, _Args(meta))
    assert all(v == "closed" for v in decisions.values()), decisions


def test_sign_test_is_symmetric_and_bounded() -> None:
    assert runner._binom_two_sided_p(5, 10) == 1.0
    assert runner._binom_two_sided_p(0, 10) < 0.01
    assert runner._binom_two_sided_p(10, 10) == runner._binom_two_sided_p(0, 10)
