#!/usr/bin/env python3
"""Assert two final_summary.json artifacts agree on every non-volatile field.

Used by `make gate-twice`. The reproducibility claim in the paper is that the
RESULTS reproduce, not that wall-clock timings do, so the fields below are
excluded and reported separately rather than silently ignored.
"""
from __future__ import annotations

import json
import sys

# Only wall-clock is genuinely volatile. `commit` is `git rev-parse HEAD`, constant
# across two runs in one tree; `matrix_sha256` now hashes the timing-stripped result and
# is stable. Both were previously excluded AND omitted from the report -- silently
# ignored, which is exactly what this module's docstring promised not to do.
VOLATILE = {"runtime_seconds", "runtime_ms_per_condition"}


def main(a: str, b: str) -> int:
    x, y = (json.load(open(p)) for p in (a, b))
    keys = sorted(set(x) | set(y))
    diffs = [(k, x.get(k, "<absent>"), y.get(k, "<absent>"))
             for k in keys if k not in VOLATILE and x.get(k) != y.get(k)]
    if diffs:
        print("SUMMARY ARTIFACT DID NOT REPRODUCE:")
        for k, u, v in diffs:
            print(f"  {k}: run1={u!r} run2={v!r}")
        return 1
    compared = [k for k in keys if k not in VOLATILE]
    print(f"summary reproduced: {len(compared)} field(s) identical, "
          f"including matrix_sha256 and commit")
    for k in sorted(VOLATILE):
        if k in x or k in y:
            print(f"   volatile {k}: run1={x.get(k)} run2={y.get(k)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:3]))
