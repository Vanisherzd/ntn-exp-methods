#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "sgp4>=2.23"]
# ///
"""E0 part 2 — availability-regime restriction + transmission-anchored sampling.

(a) How much cohort survives restricting to the epoch range where
    CREATION_DATE is a trustworthy availability proxy?
(b) Prototype the causal transmission-anchored rule
        t_tx = epoch_stale + target_age + delta_k
    and measure how it changes cohort membership vs the current
        t_abs = epoch_reference + k*step
"""
from __future__ import annotations
import datetime as dt, json, sys
from pathlib import Path
ROOT = Path("/Users/laizhendong/Desktop/LEO-Hybrid-PGRL")
sys.path.insert(0, str(ROOT / "experiments/exp14_multisat_generalization_matrix"))
import run_multisat_generalization_matrix as R  # noqa: E402

CLEAN_FROM = dt.datetime(2014, 1, 1, tzinfo=dt.timezone.utc)
K, PERIOD = R.K_SAMPLES_PER_PAIR, R.PERIOD_SAMPLE_S


def parse(t):
    if not t:
        return None
    try:
        d = dt.datetime.fromisoformat(str(t))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def main() -> int:
    sats = R.discover_satellites(ROOT / "dataraw" / "spacetrack")
    step = PERIOD / K
    rep = {"clean_from": CLEAN_FROM.isoformat(), "per_satellite": [], "bands": []}

    print("=== (a) cohort cost of restricting to availability-clean epochs (>=2014) ===")
    for s in sats:
        tot = len(s.records)
        keep = [r for r in s.records if r["epoch"] >= CLEAN_FROM]
        rep["per_satellite"].append({
            "satellite": s.name, "elements_total": tot,
            "elements_clean": len(keep),
            "retained_pct": round(100 * len(keep) / tot, 2) if tot else 0.0})
        print(f"  {s.name:15} {len(keep):>6}/{tot:<6} = {100*len(keep)/max(tot,1):>6.2f}% retained")

    print("\n=== (b) transmission-anchored vs reference-anchored pairing ===")
    print("  current : t_abs = epoch_ref   + k*step        (window opens AT the reference)")
    print("  causal  : t_tx  = epoch_stale + target_age + delta_k")
    for target_h, (lo, hi) in sorted(R.STALENESS_BANDS.items()):
        cur = cau = both = cau_avail = 0
        for s in sats:
            recs = [r for r in s.records if r["epoch"] >= CLEAN_FROM]
            if len(recs) < 5:
                continue
            ep = [r["epoch"] for r in recs]
            for j in range(len(recs)):
                i = R.select_stale_partner(ep, j, float(target_h), lo, hi)
                if i is None:
                    continue
                cur += 1
                # causal rule: fix t_tx from the STALE element only
                t_tx0 = ep[i] + dt.timedelta(hours=float(target_h))
                t_tx1 = t_tx0 + dt.timedelta(seconds=(K - 1) * step)
                # the reference must become available only AFTER the window
                cr = parse(recs[j].get("creation_date"))
                cs = parse(recs[i].get("creation_date"))
                ok_stale = (cs is not None and cs <= t_tx0)
                ok_ref_future = (cr is not None and cr > t_tx1)
                # the reference must still post-date the transmission window
                if ep[j] >= t_tx1:
                    cau += 1
                    both += 1
                if ok_stale and ok_ref_future:
                    cau_avail += 1
        rep["bands"].append({
            "target_h": target_h, "pairs_reference_anchored": cur,
            "pairs_transmission_anchored_epoch_only": cau,
            "pairs_transmission_anchored_availability_enforced": cau_avail,
        })
        print(f"  @{target_h:>3}h  ref-anchored={cur:>6}  "
              f"tx-anchored(epoch)={cau:>6} ({100*cau/max(cur,1):>5.1f}%)  "
              f"tx-anchored(+availability)={cau_avail:>6} ({100*cau_avail/max(cur,1):>5.1f}%)")

    Path(__file__).with_name("E0_anchor_result.json").write_text(json.dumps(rep, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
