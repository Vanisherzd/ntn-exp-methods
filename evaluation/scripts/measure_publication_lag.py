#!/usr/bin/env python3
"""Measure the epoch-to-publication gap in the public catalogue records used here.

The paper's motivating premise is that an element set carries an element epoch and a
separate publication time. That premise was asserted against the standards that DEFINE the
fields (CCSDS 502.0-B, Space-Track GP) rather than measured, and a second statement --
that epoch <= publication is an assumption rather than an invariant -- was written as a
hypothetical. It is not: in these records the epoch leads publication in 27.6 % of cases.

This script measures both so the manuscript can cite numbers rather than intuitions. It
reads only timestamps. It computes no residual, fits no model, and touches no contract
rule, fault or denominator -- the stopped residual-learning line stays stopped.

    python evaluation/scripts/measure_publication_lag.py
"""
from __future__ import annotations

import glob
import json
import statistics as st
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "dataraw" / "spacetrack"
OUT = ROOT / "evaluation" / "results" / "publication_lag.json"


def _parse(s: str) -> datetime | None:
    s = s.replace("Z", "")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None


def main() -> int:
    gaps: list[float] = []
    per_sat: dict[str, list[float]] = {}
    for fp in sorted(glob.glob(str(DATA / "*" / "*.json"))):
        try:
            recs = json.load(open(fp))
        except Exception:
            continue
        if isinstance(recs, dict):
            recs = [recs]
        sat = Path(fp).parent.name
        for r in recs:
            e, c = r.get("EPOCH"), r.get("CREATION_DATE")
            if not (e and c):
                continue
            de, dc = _parse(e), _parse(c)
            if not (de and dc):
                continue
            h = (dc - de).total_seconds() / 3600.0
            gaps.append(h)
            per_sat.setdefault(sat, []).append(h)
    if not gaps:
        print("no records with both EPOCH and CREATION_DATE found")
        return 1
    ahead = [g for g in gaps if g < 0]
    s = {
        "source": "dataraw/spacetrack (Space-Track GP records, untracked local data)",
        "n_records": len(gaps),
        "n_satellites": len(per_sat),
        "median_lag_h": round(st.median(gaps), 2),
        "frac_over_24h": round(sum(g > 24 for g in gaps) / len(gaps), 4),
        "frac_epoch_ahead_of_publication": round(len(ahead) / len(gaps), 4),
        "median_lead_when_ahead_h": round(abs(st.median(ahead)), 2) if ahead else None,
        "per_satellite": {k: {"n": len(v),
                              "median_lag_h": round(st.median(v), 2),
                              "frac_epoch_ahead": round(sum(x < 0 for x in v) / len(v), 4)}
                          for k, v in sorted(per_sat.items())},
    }
    OUT.write_text(json.dumps(s, indent=1) + "\n")
    for k, v in s.items():
        if k != "per_satellite":
            print(f"  {k:34s} {v}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
