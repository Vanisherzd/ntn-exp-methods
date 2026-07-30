#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "sgp4>=2.23"]
# ///
"""T1 — REFERENCE-EPOCH PERTURBATION.

Empirically proves (or refutes) the Loop-0 feature manifest.

Method: hold every deployment-available input fixed -- the stale element, the
transmission UTC, the ground station, the carrier -- and swap ONLY the future
reference element for a different one. Recompute the ten-element feature vector
exactly as build_pairs does. Any feature that changes is, by construction,
dependent on the reference element and therefore NON-DEPLOYABLE.

This test authors no verdict of its own: it reports which indices moved.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/Users/laizhendong/Desktop/LEO-Hybrid-PGRL")
EXP = ROOT / "experiments" / "exp14_multisat_generalization_matrix"
sys.path.insert(0, str(EXP))

import run_multisat_generalization_matrix as R  # noqa: E402
from sgp4.api import Satrec  # noqa: E402

GS = (24.0, 121.0, 100.0)
CARRIER = 868e6


def feature_row(stale, ref, t_abs, gs, carrier):
    """Recompute one feature row exactly as build_pairs does."""
    sat_old = Satrec.twoline2rv(stale["line1"], stale["line2"])
    age_s = (t_abs - stale["epoch"]).total_seconds()
    gap_s = (ref["epoch"] - stale["epoch"]).total_seconds()
    jd, fr = R._jd_of(t_abs)
    gs_r, gs_v = R._gs_teme_km(jd, fr, *gs)
    e_old, r_old, v_old = sat_old.sgp4(jd, fr)
    assert e_old == 0, "stale SGP4 failed"
    d_stale, elev, rng = R._doppler_and_geom(
        np.array(r_old), np.array(v_old), gs_r, gs_v, carrier)
    mean_anom = stale["mean_anomaly_rad"] + stale["mean_motion_rad_min"] * age_s / 60.0
    phase = mean_anom % (2.0 * math.pi)
    return [age_s, gap_s, d_stale, math.sin(phase), math.cos(phase),
            elev, rng, stale["mean_motion_rad_min"], stale["bstar"], stale["ecc"]]


def main() -> int:
    sats = R.discover_satellites(ROOT / "dataraw" / "spacetrack")
    results, verdict_changed = [], set()

    for sat in sats:
        recs = sat.records
        if len(recs) < 60:
            continue
        # deterministic choice: a mid-history stale element and two DIFFERENT
        # later references, both admissible as "a future element set"
        i = len(recs) // 2
        stale = recs[i]
        ref_a, ref_b = recs[i + 12], recs[i + 25]
        if ref_a["epoch"] == ref_b["epoch"]:
            continue
        # transmission instant held FIXED, independent of either reference
        t_abs = stale["epoch"] + dt.timedelta(hours=9.0)

        xa = feature_row(stale, ref_a, t_abs, GS, CARRIER)
        xb = feature_row(stale, ref_b, t_abs, GS, CARRIER)
        moved = [k for k in range(10) if xa[k] != xb[k]]
        verdict_changed.update(moved)
        results.append({
            "satellite": sat.name,
            "stale_epoch": stale["epoch"].isoformat(),
            "ref_a_epoch": ref_a["epoch"].isoformat(),
            "ref_b_epoch": ref_b["epoch"].isoformat(),
            "t_abs": t_abs.isoformat(),
            "indices_changed": moved,
            "gap_a_s": xa[1], "gap_b_s": xb[1],
        })

    manifest_deployable = list(R.FEATURE_NAMES)
    out = {
        "test": "T1_reference_epoch_perturbation",
        "n_satellites_tested": len(results),
        "feature_names": manifest_deployable,
        "indices_that_changed_when_only_the_reference_changed": sorted(verdict_changed),
        "=> NON_DEPLOYABLE_empirical": [manifest_deployable[k]
                                        for k in sorted(verdict_changed)],
        "=> DEPLOYABLE_empirical": [manifest_deployable[k] for k in range(10)
                                    if k not in verdict_changed],
        "per_satellite": results,
    }
    Path(__file__).with_name("T1_result.json").write_text(json.dumps(out, indent=2))

    print(f"satellites tested: {len(results)}")
    print(f"indices changed by reference swap: {sorted(verdict_changed)}")
    print(f"  -> non-deployable (empirical): "
          f"{[manifest_deployable[k] for k in sorted(verdict_changed)]}")
    print(f"  -> deployable (empirical): "
          f"{[manifest_deployable[k] for k in range(10) if k not in verdict_changed]}")

    expected = {1}
    if verdict_changed == expected:
        print("\nT1 PASS: exactly feature 1 (t_gap_s) depends on the reference "
              "element. Manifest CONFIRMED empirically.")
        return 0
    print(f"\nT1 FAIL: expected {expected}, observed {verdict_changed}. "
          "Manifest REFUTED — reopen Loop 0.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
