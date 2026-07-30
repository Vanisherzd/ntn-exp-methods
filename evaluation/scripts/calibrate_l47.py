#!/usr/bin/env python3
"""Measure L4.7's clean-path false-halt rate and injected detection rate.

Specificity is reported as a RATE over repeated clean fixtures, never inferred from a
single clean run. Reproduces the l47_calibration block of final_summary.json.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for sub in ("evaluation/scripts", "src", "tests/fixtures"):
    sys.path.insert(0, str(ROOT / sub))

import contract_layers as CL   # noqa: E402
import pipelines as P          # noqa: E402

N_SEEDS = 150
BASE = 20260731


def sweep(fault):
    halts = total = 0
    for sd in range(N_SEEDS if fault is None else N_SEEDS // 3):
        for env in P.ENVS:
            c = P.build_case_b(fault, env, seed=BASE + sd)
            total += 1
            try:
                CL.check_statistical_unit(c.y, c.unit_ids, c.coarser_ids)
            except CL.ContractViolation:
                halts += 1
    return halts, total


def main() -> int:
    fh, n = sweep(None)
    det, m = sweep("HO3")
    print(f"clean paths      : {n}  false halts {fh}  rate {fh/n:.3f}  (nominal 0.05)")
    print(f"injected paths   : {m}  detected    {det}  rate {det/m:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
