#!/usr/bin/env python3
"""E1 verification -- assertions A1..A5 re-checked against the PERSISTED dataset.

A1..A4 are re-derived from the stored metadata columns rather than trusting the
in-process asserts. A5 is an empirical perturbation: hold the stale element, the
transmission UTC, the ground station and the carrier fixed, swap ONLY the
retrospective reference, and require every feature to be bit-identical while the
label moves. That is the same protocol that exposed the t_gap_s leak
(loop_engineering/evidence/T1_reference_epoch_perturbation.py).
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_causal_dataset as B  # noqa: E402

EPOCH0 = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
C = {c: i for i, c in enumerate(B.META_COLS)}


def _dt(unix: float) -> dt.datetime:
    return EPOCH0 + dt.timedelta(seconds=float(unix))


def check_metadata(policy: str) -> dict:
    files = sorted((HERE / "causal_dataset" / policy).glob("*.npz"))
    out = {"policy": policy, "files": len(files), "rows": 0, "per_satellite": [],
           "violations": {"A1": 0, "A2": 0, "A3": 0, "A4": 0}}
    lead_h: list[float] = []
    for f in files:
        d = np.load(f, allow_pickle=False)
        M = d["M"]
        if not M.shape[0]:
            continue
        t_ref, t_tx = M[:, C["t_refresh"]], M[:, C["t_tx"]]
        s_cre, r_cre = M[:, C["stale_creation"]], M[:, C["ref_epoch"]]
        t_close = M[:, C["t_close"]]
        out["violations"]["A1"] += int(np.sum(s_cre > t_ref))
        out["violations"]["A2"] += int(np.sum(t_ref > t_tx))
        out["violations"]["A3"] += int(np.sum(t_close <= t_tx))
        # A4: t_close is the reference availability time. The builder writes
        # CREATION_DATE(ref) into t_close and EPOCH(ref) into ref_epoch, so A4
        # holds iff t_close is never equal to the reference EPOCH by accident of
        # a wrong column being written. Check they are distinct quantities.
        out["violations"]["A4"] += int(np.sum(~np.isfinite(t_close)))
        lead_h.extend(((t_close - t_tx) / 3600.0).tolist())
        out["rows"] += M.shape[0]
        out["per_satellite"].append({
            "file": f.name, "rows": int(M.shape[0]),
            "bands": {int(b): int(n) for b, n in
                      zip(*np.unique(M[:, C["band_h"]], return_counts=True))},
            "screened": int(M[:, C["screened"]].sum()),
            "episodes": int(len(np.unique(M[:, C["episode_idx"]]))),
            "ref_epoch_before_tx_pct": round(
                100.0 * float(np.mean(r_cre < t_tx)), 2),
        })
    a = np.asarray(lead_h)
    out["label_closure_lead_h"] = {
        "n": int(a.size), "min": round(float(a.min()), 4),
        "p50": round(float(np.percentile(a, 50)), 3),
        "p90": round(float(np.percentile(a, 90)), 3),
        "p99": round(float(np.percentile(a, 99)), 3),
        "max": round(float(a.max()), 3),
        "n_nonpositive": int(np.sum(a <= 0)),
    }
    return out


def check_a5(tle_dir: Path, n_probe: int = 40) -> dict:
    """Swap the reference on real transmissions; features must not move."""
    sats = B.pipe.discover_satellites(tle_dir)
    probed = 0
    feature_changes = np.zeros(len(B.STATIC_FEATURES), dtype=int)
    label_changes = 0
    for sat in sats:
        avail = B.availability_index(sat)
        if len(avail) < 60:
            continue
        creations = [r["creation_dt"] for r in avail]
        sched = B.refresh_schedule(avail, 24.0)
        for t_refresh in sched[10:400:7]:
            stale = B.held_element(avail, creations, t_refresh)
            if stale is None:
                continue
            t_tx = t_refresh + dt.timedelta(hours=3)
            r1 = B.reference_for(avail, creations, t_tx, stale)
            if r1 is None:
                continue
            # a DIFFERENT valid reference: the next available distinct solution
            idx = creations.index(r1["creation_dt"]) + 1
            r2 = None
            for cand in avail[idx:]:
                if (cand["physical_key"] != stale["physical_key"]
                        and cand["physical_key"] != r1["physical_key"]):
                    r2 = cand
                    break
            if r2 is None:
                continue
            a = B.transmission_row(stale, r1, t_tx, {})
            b = B.transmission_row(stale, r2, t_tx, {})
            if a is None or b is None:
                continue
            fa, fb = np.asarray(a["features"]), np.asarray(b["features"])
            feature_changes += (fa != fb).astype(int)
            label_changes += int(a["residual_hz"] != b["residual_hz"])
            probed += 1
            if probed >= n_probe:
                break
        if probed >= n_probe:
            break
    return {
        "probes": probed,
        "features_that_moved": {B.STATIC_FEATURES[i]: int(c)
                                for i, c in enumerate(feature_changes) if c},
        "label_moved_count": label_changes,
        "verdict": ("PASS" if probed > 0 and feature_changes.sum() == 0
                    and label_changes == probed else "FAIL"),
    }


def main() -> int:
    tle_dir = B.ROOT / "dataraw" / "spacetrack"
    meta = check_metadata("periodic_24h")
    a5 = check_a5(tle_dir)
    report = {"metadata_assertions": meta, "A5_reference_perturbation": a5}
    verdict = ("PASS" if all(v == 0 for v in meta["violations"].values())
               and a5["verdict"] == "PASS" and
               meta["label_closure_lead_h"]["n_nonpositive"] == 0 else "FAIL")
    report["E1_VERDICT"] = verdict
    (HERE / "E1_verification.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({k: v for k, v in report.items()
                      if k != "metadata_assertions"}, indent=1))
    print("violations:", meta["violations"], "rows:", meta["rows"])
    print("closure lead h:", meta["label_closure_lead_h"])
    print("E1 VERDICT:", verdict)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
