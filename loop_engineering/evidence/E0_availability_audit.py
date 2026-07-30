#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "sgp4>=2.23"]
# ///
"""E0 — AVAILABILITY-TIME AUDIT.

Seven distinct clocks must be separated. The current pipeline conflates
several of them by treating the ELEMENT EPOCH as if it were the moment the
element became usable.

  1 element epoch        EPOCH            (osculating state time)
  2 availability time    CREATION_DATE    (Space-Track record creation)
  3 code's epochs[j]     = EPOCH of the reference element
  4 pair reference time  = epochs[j]      (anchor of the sample window)
  5 model-refresh time   NOT REPRESENTED in the current pipeline
  6 transmission time    t_abs = epochs[j] + k*step
  7 label-closure time   NOT REPRESENTED  (should be availability of reference)

Verdict computed here, not asserted.
"""
from __future__ import annotations
import datetime as dt, json, statistics, sys
from pathlib import Path

ROOT = Path("/Users/laizhendong/Desktop/LEO-Hybrid-PGRL")
EXP = ROOT / "experiments" / "exp14_multisat_generalization_matrix"
sys.path.insert(0, str(EXP))
import run_multisat_generalization_matrix as R  # noqa: E402

BANDS = R.STALENESS_BANDS
K, PERIOD = R.K_SAMPLES_PER_PAIR, R.PERIOD_SAMPLE_S


def parse(ts):
    if not ts:
        return None
    try:
        d = dt.datetime.fromisoformat(str(ts))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def main() -> int:
    sats = R.discover_satellites(ROOT / "dataraw" / "spacetrack")
    lags, per_sat, viol = [], {}, []
    for sat in sats:
        recs = [r for r in sat.records if r.get("creation_date")]
        if len(recs) < 30:
            continue
        L = []
        for r in recs:
            c = parse(r["creation_date"])
            if c:
                L.append((c - r["epoch"]).total_seconds() / 3600.0)
        if not L:
            continue
        lags += L
        L.sort()
        per_sat[sat.name] = {
            "n": len(L), "min_h": round(L[0], 3),
            "p50_h": round(statistics.median(L), 3),
            "p90_h": round(L[int(0.9 * (len(L) - 1))], 3),
            "max_h": round(L[-1], 3),
            "negative_lag_count": sum(1 for x in L if x < 0),
        }
        # causality of the CURRENT pairing rule, per band
        epochs = [r["epoch"] for r in recs]
        step = PERIOD / K
        for target_h, (lo, hi) in sorted(BANDS.items()):
            n_pairs = n_stale_unavail = n_ref_already_avail = 0
            for j in range(len(recs)):
                i = R.select_stale_partner(epochs, j, float(target_h), lo, hi)
                if i is None:
                    continue
                n_pairs += 1
                cs = parse(recs[i]["creation_date"])
                cr = parse(recs[j]["creation_date"])
                t0 = epochs[j]                       # first sampled t_abs
                t_last = epochs[j] + dt.timedelta(seconds=(K - 1) * step)
                if cs and cs > t0:
                    n_stale_unavail += 1             # terminal could not hold it
                if cr and cr <= t_last:
                    n_ref_already_avail += 1         # fresher element already out
            if n_pairs:
                viol.append({
                    "satellite": sat.name, "target_h": target_h,
                    "pairs": n_pairs,
                    "stale_not_yet_available_pct":
                        round(100 * n_stale_unavail / n_pairs, 2),
                    "reference_already_available_pct":
                        round(100 * n_ref_already_avail / n_pairs, 2),
                })

    lags.sort()
    summary = {
        "creation_minus_epoch_hours": {
            "n_elements": len(lags), "min": round(lags[0], 3),
            "p10": round(lags[int(0.10 * (len(lags) - 1))], 3),
            "p50": round(statistics.median(lags), 3),
            "p90": round(lags[int(0.90 * (len(lags) - 1))], 3),
            "p99": round(lags[int(0.99 * (len(lags) - 1))], 3),
            "max": round(lags[-1], 3),
            "negative_count": sum(1 for x in lags if x < 0),
        },
        "per_satellite": per_sat,
        "current_pairing_causality": viol,
    }
    out = Path(__file__).with_name("E0_availability_result.json")
    out.write_text(json.dumps(summary, indent=2))

    s = summary["creation_minus_epoch_hours"]
    print("=== availability lag (CREATION_DATE - EPOCH), hours ===")
    print(f"  n={s['n_elements']}  min={s['min']}  p10={s['p10']}  p50={s['p50']}  "
          f"p90={s['p90']}  p99={s['p99']}  max={s['max']}  neg={s['negative_count']}")
    print("\n=== current pairing rule: causality violations ===")
    print("  (stale element not yet AVAILABLE at the first sampled transmission)")
    worst = sorted(viol, key=lambda v: -v["stale_not_yet_available_pct"])[:8]
    for v in worst:
        print(f"  {v['satellite']:14} @{v['target_h']:>3}h  pairs={v['pairs']:>5}  "
              f"stale_unavailable={v['stale_not_yet_available_pct']:>6.2f}%  "
              f"ref_already_out={v['reference_already_available_pct']:>6.2f}%")
    allp = sum(v["pairs"] for v in viol)
    wsum = sum(v["pairs"] * v["stale_not_yet_available_pct"] / 100 for v in viol)
    rsum = sum(v["pairs"] * v["reference_already_available_pct"] / 100 for v in viol)
    print(f"\n  ALL BANDS: pairs={allp}  stale-unavailable={wsum:.0f} "
          f"({100*wsum/allp:.2f}%)  reference-already-available={rsum:.0f} "
          f"({100*rsum/allp:.2f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
