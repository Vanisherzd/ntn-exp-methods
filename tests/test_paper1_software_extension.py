"""Contract tests for the Paper 1 software-extension artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Final

ROOT: Final = Path(__file__).resolve().parents[1]
RESULT_PATHS: Final = (
    ROOT / "experiments/exp10_residual_learnability/results.json",
    ROOT / "experiments/exp11_stronger_baselines/results.json",
    ROOT / "experiments/exp12_tail_aware_gate/results.json",
    ROOT / "experiments/exp13_multisat_generalization/results.json",
)
VALID_GATE_VALUES: Final = {"open", "closed", "unavailable", "proxy_only"}


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _walk(value: object) -> list[dict[str, object]]:
    if isinstance(value, dict):
        items = [value]
        for child in value.values():
            items.extend(_walk(child))
        return items
    if isinstance(value, list):
        items: list[dict[str, object]] = []
        for child in value:
            items.extend(_walk(child))
        return items
    return []


def test_result_files_exist_and_parse() -> None:
    for path in RESULT_PATHS:
        assert path.exists(), path
        assert isinstance(_load(path), dict)


def test_numeric_metrics_are_finite_when_present() -> None:
    for path in RESULT_PATHS:
        for mapping in _walk(_load(path)):
            for key, value in mapping.items():
                if "gate" in key or "decision" in key:
                    continue
                if not any(
                    token in key for token in ("_mae", "_hz", "_pct", "_samples")
                ):
                    continue
                if value is None or value == "":
                    continue
                if isinstance(value, (int, float)):
                    numeric = float(value)
                else:
                    assert isinstance(value, str), (path, key, value)
                    numeric = float(value)
                assert math.isfinite(numeric), (path, key, value)


def test_gate_decisions_use_declared_values() -> None:
    for path in RESULT_PATHS:
        for mapping in _walk(_load(path)):
            for key, value in mapping.items():
                if "gate" not in key and "decision" not in key:
                    continue
                if isinstance(value, bool):
                    continue
                if not isinstance(value, str):
                    continue
                assert value in VALID_GATE_VALUES, (path, key, value)


def test_real_artifacts_do_not_claim_measured_rf_truth() -> None:
    for path in RESULT_PATHS[:3]:
        metadata = _load(path)["metadata"]
        assert isinstance(metadata, dict)
        assert metadata["reference_is_measured_truth"] is False
        scope = str(metadata["scope"]).lower()
        assert "measured" not in scope or "not" in scope


def test_synthetic_rows_are_explicitly_mechanism_only() -> None:
    payload = _load(RESULT_PATHS[2])
    metadata = payload["metadata"]
    assert isinstance(metadata, dict)
    assert metadata["synthetic_is_mechanism_check_only"] is True
    synthetic_rows = payload["synthetic_mechanism"]
    assert isinstance(synthetic_rows, list)
    assert synthetic_rows
    assert all(str(row["regime"]).startswith("synthetic_") for row in synthetic_rows)


def test_multisat_dry_run_is_not_presented_as_generalization_result() -> None:
    payload = _load(RESULT_PATHS[3])
    metadata = payload["metadata"]
    assert isinstance(metadata, dict)
    assert metadata["dry_run"] is True
    assert metadata["raw_tle_inputs_available"] is False
    rows = payload["matrix_rows"]
    assert isinstance(rows, list)
    assert rows
    assert all(row["status"] == "summary_only" for row in rows)
