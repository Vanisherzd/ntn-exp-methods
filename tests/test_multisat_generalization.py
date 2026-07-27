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


# ------------------------------------------------- qualification rule (Phase 1)

sys.path.insert(0, str(EXP))
import qualify_dataset as qual  # noqa: E402


def _sat(key: str, regime: str, n_bands: int) -> dict[str, Any]:
    """One per-satellite qualification record with n_bands supported."""
    bands = [8, 24, 48, 72, 96, 168][:n_bands]
    return {
        "satellite_key": key,
        "satellite_name": key,
        "norad_id": int(key.replace("NORAD", "")),
        "regime": regime,
        "supported_bands": bands,
        "n_supported_bands": len(bands),
        "retained": len(bands) >= qual.MIN_BANDS_PER_SATELLITE,
    }


def _per_sat(spec: list[tuple[str, int]]) -> dict[str, dict[str, Any]]:
    return {
        f"NORAD{i:05d}": _sat(f"NORAD{i:05d}", regime, n_bands)
        for i, (regime, n_bands) in enumerate(spec, start=1)
    }


def test_preregistered_thresholds_are_unchanged() -> None:
    assert qual.MIN_SATELLITES == 6
    assert qual.MIN_REGIMES == 3
    assert qual.MIN_BANDS_PER_SATELLITE == 2
    assert qual.MIN_PAIRS_PER_SPLIT == 3


def test_nine_ingested_seven_retained_three_regimes_qualifies() -> None:
    """The real observed shape: dropping weak candidates must not fail the set."""
    spec = [
        ("regime_a", 6), ("regime_a", 6), ("regime_b", 6),
        ("regime_b", 6), ("regime_c", 6), ("regime_c", 6),
        ("regime_c", 6),
        ("regime_d", 0), ("regime_d", 0),   # two dropped, as with the Starlinks
    ]
    verdict = qual.evaluate_qualification(_per_sat(spec))
    checks = verdict["checks"]
    assert checks["retention_rule_applied"]["satellites_ingested"] == 9
    assert checks["retention_rule_applied"]["satellites_retained"] == 7
    assert checks["retention_rule_applied"]["satellites_dropped"] == 2
    assert checks["min_satellites"]["observed"] == 7
    assert checks["min_regimes"]["observed"] == 3
    assert verdict["qualified"] is True


def test_nine_ingested_five_retained_fails() -> None:
    spec = [
        ("regime_a", 6), ("regime_a", 6), ("regime_b", 6),
        ("regime_b", 6), ("regime_c", 6),
        ("regime_c", 1), ("regime_c", 1), ("regime_d", 0), ("regime_d", 0),
    ]
    verdict = qual.evaluate_qualification(_per_sat(spec))
    assert verdict["checks"]["min_satellites"]["observed"] == 5
    assert verdict["checks"]["min_satellites"]["pass"] is False
    assert verdict["qualified"] is False


def test_seven_retained_but_only_two_regimes_fails() -> None:
    spec = [("regime_a", 6)] * 4 + [("regime_b", 6)] * 3
    verdict = qual.evaluate_qualification(_per_sat(spec))
    assert verdict["checks"]["min_satellites"]["pass"] is True
    assert verdict["checks"]["min_regimes"]["observed"] == 2
    assert verdict["checks"]["min_regimes"]["pass"] is False
    assert verdict["qualified"] is False


def test_satellite_below_band_rule_cannot_count_toward_retention() -> None:
    """A one-band satellite must never be retained, and must not add a regime."""
    spec = [("regime_a", 6)] * 3 + [("regime_b", 6)] * 3 + [("regime_c", 1)]
    per_sat = _per_sat(spec)
    one_band = [s for s in per_sat.values() if s["n_supported_bands"] == 1]
    assert len(one_band) == 1
    assert one_band[0]["retained"] is False
    verdict = qual.evaluate_qualification(per_sat)
    assert verdict["checks"]["min_satellites"]["observed"] == 6
    assert one_band[0]["satellite_key"] not in verdict["retained_keys"]
    # regime_c came only from the dropped satellite, so it must not be counted
    assert "regime_c" not in verdict["checks"]["min_regimes"]["regimes"]
    assert verdict["checks"]["min_regimes"]["observed"] == 2
    assert verdict["qualified"] is False


def test_retention_invariant_rejects_a_corrupted_retained_flag() -> None:
    """Guard: a <2-band satellite forced into the retained set must fail."""
    per_sat = _per_sat([("regime_a", 6)] * 6 + [("regime_b", 6)] * 2)
    corrupted = dict(_sat("NORAD99999", "regime_c", 1))
    corrupted["retained"] = True          # deliberately inconsistent
    per_sat["NORAD99999"] = corrupted
    verdict = qual.evaluate_qualification(per_sat)
    assert verdict["checks"]["retention_rule_applied"]["pass"] is False
    assert verdict["qualified"] is False


# ------------------------------------- canonical ingestion + client (P0 repair)

import datetime as _dt  # noqa: E402

import spacetrack_client as stc  # noqa: E402


def _write_history(dirpath: Path, norad: int, n: int, gap_h: float = 6.0) -> None:
    """Write a gp_history JSON and an equivalent TLE archive for one object."""
    from sgp4.api import WGS72, Satrec
    from sgp4.exporter import export_tle

    jd0 = 2461041.5
    rows, tle_lines = [], []
    for k in range(n):
        sat = Satrec()
        sat.sgp4init(
            WGS72, "i", norad, jd0 + k * gap_h / 24.0 - 2433281.5,
            1.0e-4, 0.0, 0.0, 0.0012, 0.5, 0.9, 1.1, 0.0630,
            (0.7 + 0.063 * k * gap_h * 60.0) % 6.283185,
        )
        line1, line2 = export_tle(sat)
        epoch = _dt.datetime(2026, 1, 1, tzinfo=_dt.timezone.utc) + _dt.timedelta(
            hours=k * gap_h
        )
        rows.append(
            {
                "NORAD_CAT_ID": str(norad),
                "OBJECT_NAME": f"TEST-{norad}",
                "EPOCH": epoch.isoformat().replace("+00:00", ""),
                "TLE_LINE1": line1,
                "TLE_LINE2": line2,
            }
        )
        tle_lines += [line1, line2]
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / f"gp_history_{norad}.json").write_text(json.dumps(rows))
    (dirpath / f"gp_history_{norad}.tle").write_text("\n".join(tle_lines) + "\n")


def test_json_plus_tle_archive_does_not_double_the_record_count(tmp_path) -> None:
    """P0-A: the archival TLE copy must not become a second observation set."""
    root = tmp_path / "spacetrack"
    _write_history(root / "test_70001", 70001, 40)

    both = runner.discover_satellites(root)
    assert len(both) == 1
    assert both[0].n_records == 40, both[0].ingestion_audit
    assert both[0].ingestion_audit["tle_used_for_science"] is False
    assert both[0].ingestion_audit["canonical_source"] == "json"

    (root / "test_70001" / "gp_history_70001.tle").unlink()
    json_only = runner.discover_satellites(root)
    assert json_only[0].n_records == both[0].n_records


def test_duplicate_json_rows_collapse_to_one_canonical_element(tmp_path) -> None:
    """P0-A: repeated GP rows must yield one element, counted as duplicates."""
    root = tmp_path / "spacetrack"
    d = root / "test_70002"
    _write_history(d, 70002, 20)
    path = d / "gp_history_70002.json"
    rows = json.loads(path.read_text())
    # duplicate every row, and perturb the epoch text below the 1 ms quantum
    dupes = [dict(r, EPOCH=r["EPOCH"] + ".000100") for r in rows]
    path.write_text(json.dumps(rows + dupes))

    sats = runner.discover_satellites(root)
    assert sats[0].n_records == 20
    assert sats[0].ingestion_audit["duplicate_rows_in_canonical_source"] == 20
    ids = [r["element_id"] for r in sats[0].records]
    assert len(ids) == len(set(ids))


def test_element_id_is_norad_plus_normalized_epoch() -> None:
    when = _dt.datetime(2026, 3, 4, 5, 6, 7, 891234, tzinfo=_dt.timezone.utc)
    assert runner.normalize_epoch(when).endswith("05:06:07.891+00:00")
    assert runner.element_id(12345, when).startswith("12345|")
    nearby = when.replace(microsecond=891987)
    assert runner.element_id(12345, when) == runner.element_id(12345, nearby)


def test_pair_ids_are_unique_and_survive_tle_removal(tmp_path) -> None:
    """P0-A: pair count must be invariant to the archival TLE copy."""
    root = tmp_path / "spacetrack"
    _write_history(root / "test_70003", 70003, 60)
    gs, carrier = (24.0, 121.0, 100.0), 868e6

    sat_both = runner.discover_satellites(root)[0]
    acc_both, _, _ = runner.build_pairs(sat_both, 24, 1e9, gs, carrier)
    ids = [p["pair_id"] for p in acc_both]
    assert len(ids) == len(set(ids)), "pair_id must be unique"
    assert all(len(p["y"]) == runner.K_SAMPLES_PER_PAIR for p in acc_both)

    (root / "test_70003" / "gp_history_70003.tle").unlink()
    sat_json = runner.discover_satellites(root)[0]
    acc_json, _, _ = runner.build_pairs(sat_json, 24, 1e9, gs, carrier)
    assert len(acc_json) == len(acc_both)
    assert {p["pair_id"] for p in acc_json} == set(ids)


def test_one_reference_element_yields_at_most_one_pair(tmp_path) -> None:
    """The 24 in-pass samples are children of a pair, never separate pairs."""
    root = tmp_path / "spacetrack"
    _write_history(root / "test_70004", 70004, 50)
    sat = runner.discover_satellites(root)[0]
    accepted, _, _ = runner.build_pairs(
        sat, 24, 1e9, (24.0, 121.0, 100.0), 868e6
    )
    refs = [p["ref_epoch_utc"] for p in accepted]
    assert len(refs) == len(set(refs)), "one reference element -> one pair"


def test_sign_test_n_counts_pairs_not_sample_rows(tmp_path) -> None:
    """P0-A: the statistical unit must be pair_id, never the 24 samples."""
    import numpy as np

    root = tmp_path / "spacetrack"
    _write_history(root / "test_70005", 70005, 50)
    sat = runner.discover_satellites(root)[0]
    accepted, _, _ = runner.build_pairs(
        sat, 24, 1e9, (24.0, 121.0, 100.0), 868e6
    )
    assert accepted
    stats = runner.paired_pair_level_test(
        accepted,
        lambda x: np.zeros(x.shape[0]),
        lambda x: np.full(x.shape[0], 1.0),
        500.0,
        n_boot=50,
        seed=1,
    )
    n_unique_pairs = len({p["pair_id"] for p in accepted})
    assert stats["n_pairs"] == n_unique_pairs
    assert stats["n_pairs"] != n_unique_pairs * runner.K_SAMPLES_PER_PAIR
    assert (
        stats["pair_wins_learned"] + stats["pair_losses_learned"] + stats["pair_ties"]
        == n_unique_pairs
    )


def test_bootstrap_resamples_pairs_not_samples(tmp_path) -> None:
    """Bootstrap draws exactly n_pairs values, so its unit is the pair."""
    import numpy as np

    root = tmp_path / "spacetrack"
    _write_history(root / "test_70006", 70006, 40)
    sat = runner.discover_satellites(root)[0]
    accepted, _, _ = runner.build_pairs(
        sat, 24, 1e9, (24.0, 121.0, 100.0), 868e6
    )
    drawn: list[int] = []
    real_choice = np.random.Generator.choice

    class _Spy(np.random.Generator):
        def choice(self, a, size=None, replace=True, **kw):  # type: ignore[override]
            drawn.append(size)
            return real_choice(self, a, size=size, replace=replace, **kw)

    rng = _Spy(np.random.PCG64(0))
    orig = np.random.default_rng
    np.random.default_rng = lambda *a, **k: rng  # type: ignore[assignment]
    try:
        stats = runner.paired_pair_level_test(
            accepted,
            lambda x: np.zeros(x.shape[0]),
            lambda x: np.full(x.shape[0], 0.5),
            500.0,
            n_boot=7,
            seed=0,
        )
    finally:
        np.random.default_rng = orig  # type: ignore[assignment]
    assert drawn and set(drawn) == {stats["n_pairs"]}


# ---------------------------------------------- response validation (Task 3)


RATE_LIMIT_BODY = json.dumps(
    [{"error": "You've violated your query rate limit.  Please refer to ..."}]
).encode()


def test_rate_limit_payload_is_never_an_empty_result() -> None:
    for classify in (stc.classify_satcat, stc.classify_gp_history):
        resp = classify(RATE_LIMIT_BODY)
        assert resp.state is stc.ResponseState.RATE_LIMITED
        assert resp.state is not stc.ResponseState.EMPTY
        assert resp.archivable is False


def test_response_states_are_classified_explicitly() -> None:
    assert stc.classify_satcat(b"[]").state is stc.ResponseState.EMPTY
    assert stc.classify_satcat(b"not json").state is stc.ResponseState.PARSE_ERROR
    assert (
        stc.classify_satcat(json.dumps([{"error": "bad request"}]).encode()).state
        is stc.ResponseState.API_ERROR
    )
    good = json.dumps([{"NORAD_CAT_ID": "25544", "OBJECT_NAME": "ISS"}]).encode()
    assert stc.classify_satcat(good, 25544).state is stc.ResponseState.VALID
    assert (
        stc.classify_satcat(good, 99999).state is stc.ResponseState.IDENTITY_MISMATCH
    )


def test_gp_history_requires_norad_and_epoch() -> None:
    missing = json.dumps([{"NORAD_CAT_ID": "1"}]).encode()
    assert stc.classify_gp_history(missing).state is stc.ResponseState.API_ERROR
    ok = json.dumps(
        [{"NORAD_CAT_ID": "1", "EPOCH": "2026-01-01T00:00:00"}]
    ).encode()
    assert stc.classify_gp_history(ok, 1).state is stc.ResponseState.VALID


def test_tle_body_must_be_tle_text() -> None:
    assert stc.classify_tle(RATE_LIMIT_BODY).state is stc.ResponseState.RATE_LIMITED
    assert stc.classify_tle(b"<html>error</html>").state is stc.ResponseState.API_ERROR
    assert stc.classify_tle(b"").state is stc.ResponseState.EMPTY
    real = b"1 25544U 98067A   26001.00000000  .00000000  00000-0  00000-0 0  9990\n"
    assert stc.classify_tle(real).state is stc.ResponseState.VALID


# ------------------------------------------- throttle and retry (Task 4)


def _scheduler(**kw):
    slept: list[float] = []
    clock = {"t": 0.0}

    def fake_sleep(s: float) -> None:
        slept.append(s)
        clock["t"] += s

    sched = stc.RequestScheduler(
        sleep=fake_sleep, clock=lambda: clock["t"], initial_backoff_s=10.0, **kw
    )
    return sched, slept


def test_rate_limited_response_is_retried_then_succeeds() -> None:
    sched, slept = _scheduler(requests_per_minute=60.0, max_retries=3)
    good = json.dumps([{"NORAD_CAT_ID": "1", "OBJECT_NAME": "X"}]).encode()
    bodies = [RATE_LIMIT_BODY, RATE_LIMIT_BODY, good]
    resp = sched.fetch(lambda: bodies.pop(0), stc.classify_satcat, "t")
    assert resp.state is stc.ResponseState.VALID
    assert sched.stats["retries"] == 2
    assert slept[:2] == [10.0, 20.0], slept  # increasing backoff


def test_retry_exhaustion_reports_rate_limited_not_empty() -> None:
    sched, _ = _scheduler(requests_per_minute=60.0, max_retries=2)
    resp = sched.fetch(lambda: RATE_LIMIT_BODY, stc.classify_satcat, "t")
    assert resp.state is stc.ResponseState.RATE_LIMITED
    assert resp.archivable is False
    assert sched.stats["requests"] == 3


def test_scheduler_paces_requests_below_the_limit() -> None:
    sched, slept = _scheduler(requests_per_minute=20.0, max_retries=0)
    good = json.dumps([{"NORAD_CAT_ID": "1", "OBJECT_NAME": "X"}]).encode()
    for _ in range(3):
        sched.fetch(lambda: good, stc.classify_satcat, "")
    assert all(abs(s - 3.0) < 1e-9 for s in slept), slept
    assert sched.stats["waits"] == 2


def test_transport_exception_becomes_api_error_not_empty() -> None:
    sched, _ = _scheduler(requests_per_minute=60.0, max_retries=0)

    def boom() -> bytes:
        raise OSError("connection reset")

    resp = sched.fetch(boom, stc.classify_satcat, "t")
    assert resp.state is stc.ResponseState.API_ERROR


def test_valid_cache_is_reused_and_error_cache_is_refetched(tmp_path) -> None:
    good = tmp_path / "good.json"
    good.write_bytes(json.dumps([{"NORAD_CAT_ID": "1", "OBJECT_NAME": "X"}]).encode())
    assert stc.cached_response(good, stc.classify_satcat) is not None

    bad = tmp_path / "bad.json"
    bad.write_bytes(RATE_LIMIT_BODY)
    assert stc.cached_response(bad, stc.classify_satcat) is None
    assert stc.cached_response(tmp_path / "missing.json", stc.classify_satcat) is None


def test_no_quarantined_response_is_in_a_scientific_manifest() -> None:
    """Task 5: an invalid archived body must not appear in any fetch manifest."""
    root = ROOT / "dataraw" / "spacetrack"
    if not root.is_dir():
        return
    for manifest_path in sorted(root.glob("*/fetch_manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest.get("files", []):
            path = Path(entry["path"])
            assert path.exists(), f"manifest references missing file: {path}"
            assert "_quarantine" not in path.parts
            if path.name.startswith("satcat_"):
                norad = int(path.stem.split("_")[1])
                state = stc.classify_satcat(path.read_bytes(), norad).state
                assert state is stc.ResponseState.VALID, (path, state)
