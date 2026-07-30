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
from orbit_evidence.experiment_contract import experiment_contract as EC  # noqa: E402
import numpy as np             # noqa: E402
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
    for k in (8, 20, 96):
        s = fixed_threshold_null_size(k=k)
        print(f"fixed-0.2 null size at {k:3d} groups of 3: {s:.3f}  "
              f"(the construction L4.3 still uses)")
    return 0




def fixed_threshold_null_size(thresh: float = 0.2, k: int = 8, m: int = 3,
                              n_draws: int = 4000, seed: int = 20260731) -> float:
    """P(ICC(1) > thresh) on iid data: the size of the DISCARDED fixed-threshold rule.

    This is the number the paper cites to justify replacing a fixed threshold with a
    permutation null, and it was the only quantitative claim in the paper with no
    artifact field and no regeneration command. Measured here so it is under the same
    gate as everything else.

    L4.3 still ships the fixed-threshold construction, so this also quantifies that
    disclosed limitation rather than leaving it as an assertion.
    """
    rng = np.random.default_rng(seed)
    grp = np.repeat(np.arange(k), m)
    hits = sum(1 for _ in range(n_draws)
               if EC.within_group_icc(rng.standard_normal(k * m), grp) > thresh)
    return hits / n_draws


if __name__ == "__main__":
    raise SystemExit(main())
