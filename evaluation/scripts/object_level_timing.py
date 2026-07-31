#!/usr/bin/env python3
"""Per-object catalogue timing statistics. Replaces the record-pooled headline figures.

CREATION_DATE is the OMM message creation time. It is an OPTIMISTIC LOWER BOUND on when a
consumer could have retrieved the element set: Space-Track publishes in batches, and the same
element set is republished under a new GP_ID with a later CREATION_DATE (verified here). So the
availability clock this instruments can only be too generous, never too strict.

Pooling over records is the wrong unit and this repository's own L4.7 says so: one object
supplies 82% of the 63,727 records. Everything below is per object.

Run: python evaluation/scripts/object_level_timing.py
Writes: evaluation/real_data/object_level_timing.json
"""
from __future__ import annotations
import glob, json, os
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "dataraw" / "spacetrack"
OUT = ROOT / "evaluation" / "real_data" / "object_level_timing.json"
WINDOW = ("2026-07-22", "2026-07-27")   # the L4.7 real-data analysis window


def iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "")).replace(tzinfo=timezone.utc)


def stats(lags: np.ndarray) -> dict:
    q1, q3 = (float(x) for x in np.percentile(lags, [25, 75]))
    return {"n": int(lags.size), "median_lag_h": round(float(np.median(lags)), 2),
            "iqr_h": [round(q1, 2), round(q3, 2)], "iqr_width_h": round(q3 - q1, 2),
            "min_h": round(float(lags.min()), 2), "max_h": round(float(lags.max()), 2),
            "frac_epoch_after_creation": round(float(np.mean(lags < 0)), 4)}


def main() -> int:
    per, win, republished = {}, {}, {}
    for d in sorted(glob.glob(str(DATA / "*/"))):
        obj = os.path.basename(d.rstrip("/"))
        hits = glob.glob(os.path.join(d, "gp_history_*.json"))
        if not hits:
            continue
        recs = json.load(open(hits[0]))
        lags = np.array([(iso(r["CREATION_DATE"]) - iso(r["EPOCH"])).total_seconds() / 3600.0
                         for r in recs])
        per[obj] = stats(lags)
        wr = [r for r in recs if WINDOW[0] <= r["EPOCH"][:10] < WINDOW[1]]
        if wr:
            win[obj] = stats(np.array(
                [(iso(r["CREATION_DATE"]) - iso(r["EPOCH"])).total_seconds() / 3600.0
                 for r in wr]))
        # Same element set republished under a new GP_ID: identical TLE, later CREATION_DATE.
        byep: dict[str, list] = {}
        for r in wr:
            byep.setdefault(r["EPOCH"], []).append(r)
        dups = [g for g in byep.values() if len(g) > 1]
        republished[obj] = {
            "duplicate_epoch_groups": len(dups),
            "all_identical_elements": all(
                len({x["TLE_LINE1"] + x["TLE_LINE2"] for x in g}) == 1 for g in dups),
        }

    med = sorted(v["median_lag_h"] for v in per.values())
    mid = len(med) // 2
    obj_median = med[mid] if len(med) % 2 else (med[mid - 1] + med[mid]) / 2.0
    wmed = sorted(v["median_lag_h"] for v in win.values())
    wmid = len(wmed) // 2
    win_median = wmed[wmid] if len(wmed) % 2 else (wmed[wmid - 1] + wmed[wmid]) / 2.0
    ahead = {k: v["frac_epoch_after_creation"] for k, v in per.items()}
    outliers = [k for k, v in ahead.items() if v > 0]

    doc = {
        "creation_date_semantics":
            "OMM message creation time. An optimistic LOWER BOUND on retrievability: batch "
            "publication adds unmeasured lag, and the same element set is republished under a "
            "new GP_ID with a later CREATION_DATE. The availability clock built on it can only "
            "be too generous.",
        "unit_note":
            "Per object. Record-pooled percentages are not reported as headline figures: the "
            "largest object supplies most of the records, so a pooled figure is that object's.",
        "n_objects": len(per),
        "n_records_total": sum(v["n"] for v in per.values()),
        "full_history": per,
        "analysis_window": {"window_epoch": list(WINDOW), "per_object": win},
        "object_level_median_lag_h_full_history": round(obj_median, 2),
        "object_level_median_lag_h_in_window": round(win_median, 2),
        "all_object_medians_positive_full_history": all(m > 0 for m in med),
        "all_object_medians_positive_in_window": all(m > 0 for m in wmed),
        "objects_with_any_epoch_after_creation": outliers,
        "n_objects_with_any_epoch_after_creation": len(outliers),
        "republished_element_sets_in_window": republished,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=1) + "\n")

    print(f"{'object':24s} {'n':>6s} {'med_h':>6s} {'IQR_h':>15s} {'eps>cre':>8s} {'win_med':>8s}")
    for k, v in per.items():
        w = win.get(k, {}).get("median_lag_h", float("nan"))
        print(f"{k:24s} {v['n']:6d} {v['median_lag_h']:6.2f} "
              f"[{v['iqr_h'][0]:6.2f},{v['iqr_h'][1]:6.2f}] "
              f"{v['frac_epoch_after_creation']:8.3f} {w:8.2f}")
    print(f"\nobject-level median lag: {obj_median:.2f} h full history, "
          f"{win_median:.2f} h in the analysis window")
    print(f"objects with any epoch after creation: {outliers or 'none'}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
