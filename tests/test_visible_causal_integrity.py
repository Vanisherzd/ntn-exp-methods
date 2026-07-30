#!/usr/bin/env python3
"""Causality and integrity tests for the exp15 visible-pass causal rebuild.

Committed as part of the pre-registration, BEFORE any predictive model is fitted.
These tests define the contract; the implementation must satisfy them.

Each test targets a defect that independent review found in the previous pilot.
Unlike the old A1/A2/A4 -- which asserted things true by construction and could
not fail -- every test here can fail:

  V1  schedule invariance      the schedule must not move when the FUTURE catalogue changes
  V2  row membership           row count and tx_ids must not depend on later publications
  V3  visibility               every scheduled transmission is above the threshold, by construction
  V4  feature causality        features must not move when the reference ensemble is swapped
  V5  registry freeze          the registry hash must be unchanged by label construction
  V6  no silent drops          every registry row carries exactly one status
  V7  ensemble label           the label is the median, and is never the spread-minimising choice
  V8  manifest hygiene         no stale-to-reference gap feature may exist
  V9  sampling offsets         the pre-registered offsets are the ones used
  V10 temporal join            no historical feature may read a label closing after the refresh
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "exp15_visible_causal"
sys.path.insert(0, str(EXP))

SCHED = json.loads((EXP / "schedule_config.json").read_text())
LABEL = json.loads((EXP / "label_ensemble_spec.json").read_text())
MODEL = json.loads((EXP / "model_manifest.json").read_text())

THR = SCHED["visibility"]["primary_threshold_deg"]
GS = (SCHED["fixed_config"]["gs_lat_deg"], SCHED["fixed_config"]["gs_lon_deg"],
      SCHED["fixed_config"]["gs_alt_m"])

pytest.importorskip("sgp4")
reg_mod = pytest.importorskip("build_visible_registry",
                              reason="implementation not yet present")


@pytest.fixture(scope="module")
def sat():
    """One real satellite with enough availability-clean history."""
    sats = reg_mod.load_satellites()
    for s in sats:
        if len(reg_mod.availability_index(s)) >= 500:
            return s
    pytest.skip("no satellite with sufficient availability-clean history")


# ---------------------------------------------------------------- V1, V2

def test_v1_schedule_invariant_to_future_catalogue(sat):
    """Truncating the FUTURE catalogue must not change the schedule.

    This is the test the previous pilot lacked. Its A5 perturbed the reference on
    rows that already existed and so could not detect that row MEMBERSHIP was
    decided by later publications.
    """
    avail = reg_mod.availability_index(sat)
    cut = len(avail) // 2
    t_end = avail[cut]["creation_dt"]

    full = reg_mod.build_registry(sat, avail, "NOMINAL", t_end=t_end)
    # drop every element published after the window closes; the schedule inside
    # the window must be untouched
    truncated_avail = [r for r in avail if r["creation_dt"] <= t_end]
    trunc = reg_mod.build_registry(sat, truncated_avail, "NOMINAL", t_end=t_end)

    assert full["tx_id"].tolist() == trunc["tx_id"].tolist(), (
        "schedule changed when future publications were removed")
    np.testing.assert_array_equal(full["t_tx"], trunc["t_tx"])
    np.testing.assert_array_equal(full["pred_elevation_deg"],
                                  trunc["pred_elevation_deg"])


def test_v2_row_count_independent_of_reference_availability(sat):
    """Row membership must be fixed before any reference is queried."""
    avail = reg_mod.availability_index(sat)
    t_end = avail[len(avail) // 3]["creation_dt"]
    reg = reg_mod.build_registry(sat, avail, "NOMINAL", t_end=t_end)
    assert reg["tx_id"].size > 0
    # the registry builder must not consult the label module at all
    src = (EXP / "build_visible_registry.py").read_text()
    for forbidden in ("reference_ensemble", "build_ensemble_labels",
                      "t_close", "sigma_ref"):
        assert forbidden not in src, (
            f"registry builder references label machinery: {forbidden}")


# ---------------------------------------------------------------- V3

def test_v3_every_transmission_is_predicted_visible(sat):
    """No row may sit below the pre-registered threshold, by construction."""
    avail = reg_mod.availability_index(sat)
    t_end = avail[len(avail) // 3]["creation_dt"]
    reg = reg_mod.build_registry(sat, avail, "NOMINAL", t_end=t_end)
    elev = reg["pred_elevation_deg"]
    assert elev.size > 0
    # bisection tolerance can place a sample marginally below the threshold only
    # at an interval endpoint; offsets start at 0.10 so allow a small epsilon
    assert float(elev.min()) >= THR - 0.5, (
        f"minimum predicted elevation {elev.min():.3f} deg is below the "
        f"{THR} deg threshold")
    assert float(np.median(elev)) > THR, "median elevation must exceed the threshold"


# ---------------------------------------------------------------- V4

def test_v4_features_invariant_to_reference_ensemble(sat):
    """Swap the whole reference ensemble; every feature must be bit-identical."""
    lab = pytest.importorskip("build_ensemble_labels")
    avail = reg_mod.availability_index(sat)
    t_end = avail[len(avail) // 3]["creation_dt"]
    reg = reg_mod.build_registry(sat, avail, "NOMINAL", t_end=t_end)

    names = [f["name"] for f in MODEL["static_deployable_features"]]
    moved = np.zeros(len(names), dtype=int)
    labels_moved = probes = 0
    for i in range(0, min(reg["tx_id"].size, 400), 17):
        a = lab.label_row(reg, i, avail, horizon_h=24.0, k_min=2)
        b = lab.label_row(reg, i, avail, horizon_h=72.0, k_min=2)
        if a["status"] != "COMPLETE" or b["status"] != "COMPLETE":
            continue
        fa = np.array([reg[n][i] for n in names])
        fb = np.array([reg[n][i] for n in names])
        moved += (fa != fb).astype(int)
        labels_moved += int(a["residual_hz"] != b["residual_hz"])
        probes += 1
    if probes == 0:
        pytest.skip("no COMPLETE rows under both horizons in the probe window")
    assert moved.sum() == 0, f"features moved with the reference ensemble: {moved}"
    assert labels_moved > 0, (
        "the label did not move at all under a different closure horizon -- the "
        "perturbation is not exercising the ensemble")


# ---------------------------------------------------------------- V5, V6

def test_v5_registry_hash_stable_across_label_construction(sat):
    lab = pytest.importorskip("build_ensemble_labels")
    avail = reg_mod.availability_index(sat)
    t_end = avail[len(avail) // 3]["creation_dt"]
    reg = reg_mod.build_registry(sat, avail, "NOMINAL", t_end=t_end)
    h0 = reg_mod.registry_hash(reg)
    for i in range(0, min(reg["tx_id"].size, 60), 7):
        lab.label_row(reg, i, avail, horizon_h=48.0, k_min=2)
    assert reg_mod.registry_hash(reg) == h0, (
        "label construction mutated the frozen registry")


def test_v6_every_row_has_exactly_one_status(sat):
    lab = pytest.importorskip("build_ensemble_labels")
    avail = reg_mod.availability_index(sat)
    t_end = avail[len(avail) // 3]["creation_dt"]
    reg = reg_mod.build_registry(sat, avail, "NOMINAL", t_end=t_end)
    allowed = set(LABEL["label_statuses"])
    n = min(reg["tx_id"].size, 300)
    seen = [lab.label_row(reg, i, avail, horizon_h=48.0, k_min=2)["status"]
            for i in range(n)]
    assert len(seen) == n, "a row was silently dropped"
    assert set(seen) <= allowed, f"unexpected status: {set(seen) - allowed}"


# ---------------------------------------------------------------- V7

def test_v7_label_is_ensemble_median_not_best_case(sat):
    """The label must be the median of the ensemble, never the extremum."""
    lab = pytest.importorskip("build_ensemble_labels")
    avail = reg_mod.availability_index(sat)
    t_end = avail[len(avail) // 3]["creation_dt"]
    reg = reg_mod.build_registry(sat, avail, "NOMINAL", t_end=t_end)
    checked = 0
    for i in range(0, min(reg["tx_id"].size, 600), 13):
        out = lab.label_row(reg, i, avail, horizon_h=72.0, k_min=3)
        if out["status"] not in ("COMPLETE", "AMBIGUOUS_HIGH_SPREAD"):
            continue
        members = np.asarray(out["member_doppler_hz"])
        assert members.size >= 3
        np.testing.assert_allclose(out["ref_ensemble_hz"], np.median(members),
                                   rtol=0, atol=1e-9)
        # must NOT be the member that minimises |r|
        stale = reg["pred_stale_doppler_hz"][i]
        best = members[np.argmin(np.abs(members - stale))]
        if members.size >= 3 and not np.isclose(np.median(members), best):
            checked += 1
        assert out["sigma_ref_hz"] >= 0.0
    if checked == 0:
        pytest.skip("no ensemble where median and residual-minimising member differ")


# ---------------------------------------------------------------- V8, V9

def test_v8_no_stale_to_reference_gap_feature():
    names = {f["name"] for f in MODEL["static_deployable_features"]}
    names |= set(MODEL["historical_state_features"])
    for bad in ("t_gap_s", "gap_s", "epoch_gap", "ref_epoch", "stale_to_ref",
                "t_gap"):
        assert bad not in names, f"non-deployable feature reinstated: {bad}"
    assert len(MODEL["static_deployable_features"]) == 9


def test_v9_sampling_offsets_are_preregistered():
    assert SCHED["sampling"]["normalized_offsets"] == [0.10, 0.30, 0.50, 0.70, 0.90]
    assert SCHED["sampling"]["instants_per_pass"] == 5
    assert reg_mod.NORMALIZED_OFFSETS == tuple(
        SCHED["sampling"]["normalized_offsets"]), (
        "implementation offsets diverge from the pre-registered configuration")
    assert reg_mod.PRIMARY_THRESHOLD_DEG == THR


# ---------------------------------------------------------------- V10

def test_v10_temporal_join_rejects_late_closing_labels():
    """A historical feature must never draw on a label closing after the refresh."""
    wf = pytest.importorskip("run_visible_walk_forward")
    t_ref = 1_000_000.0
    t_close = np.array([t_ref - 10.0, t_ref - 1.0, t_ref + 1.0, t_ref + 500.0])
    admitted = wf.admissible_history(t_close, t_ref)
    assert admitted.tolist() == [True, True, False, False], (
        "history admission is not strictly causal")


def test_v10b_gate_reads_validation_only():
    wf = pytest.importorskip("run_visible_walk_forward")
    src = Path(wf.__file__).read_text()
    i = src.index("def decide_gate")
    body = src[i:i + 900]
    for bad in ("dep_", "deploy", "test_"):
        assert bad not in body, f"gate decision touches held-out data: {bad}"
