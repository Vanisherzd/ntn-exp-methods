#!/usr/bin/env python3
"""Deterministic COMMON-RANDOM-NUMBERS derivation of EVALUATION_SEEDS_V2.

Two generations of seeds are now retired:

  1001-1012, 90001-90003  -- executed and inspected (reviewer emulation, author probes)
  the first v2 manifest    -- keyed on scenario_key INCLUDING the condition, so C1/C2/C3
                              received DIFFERENT physical realisations. That silently
                              violated the design's central claim that C2 and C3 differ
                              only in shift timing. Never executed, so retired at no
                              scientific cost.

Common random numbers:

    base_seed(regime, staleness, index)
        = int(sha256("exp16-v2-base" | regime | staleness | index).hexdigest()[:8], 16)

For fixed (regime, staleness, index), conditions C1/C2/C3 share ONE base seed and
therefore one base orbit, one OD-error draw and sign, one OU trajectory, one pass
schedule, one model initialisation and one train/validation/deployment row split.
Only the condition's intervention differs.

N0 uses a separate namespace so it cannot alias a treatment realisation.

Run IDs remain unique per (regime, staleness, condition, index) for bookkeeping, but
carry NO randomness.

THESE SEEDS ARE NOT RUN until the reviewer approves implementation.
"""
import hashlib, json
from pathlib import Path

BASE_PREFIX = "exp16-v2-base"
N0_PREFIX = "exp16-v2-negative-control"
REGIMES = ("R1_low_sso", "R2_mid_polar", "R3_upper_polar")
STALENESS = ("S1_short", "S2_medium", "S3_long")
CONDITIONS = ("C1", "C2", "C3")
N_INDEX = 12


def _seed(prefix: str, *parts) -> int:
    key = "|".join([prefix, *map(str, parts)])
    return int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)


def base_seed(regime: str, staleness: str, index: int) -> int:
    """One physical realisation shared by C1, C2 and C3."""
    return _seed(BASE_PREFIX, regime, staleness, index)


def n0_seed(regime: str, staleness: str, index: int) -> int:
    return _seed(N0_PREFIX, regime, staleness, index)


def main() -> int:
    base: dict[str, list[int]] = {}
    base_order: list[str] = []
    for rg in REGIMES:
        for st in STALENESS:
            k = f"{rg}|{st}"
            base_order.append(k)
            base[k] = [base_seed(rg, st, i) for i in range(N_INDEX)]

    # N0 at ALL THREE staleness levels: the leak it must detect is monotone in
    # staleness (gate-open 0.00-0.17 at S2 versus 0.83-1.00 at S3), so scheduling
    # the control only at S2 placed it where the effect is smallest.
    n0: dict[str, list[int]] = {}
    for rg in REGIMES:
        for st in STALENESS:
            n0[f"{rg}|{st}|N0"] = [n0_seed(rg, st, i) for i in range(N_INDEX)]

    run_ids = [f"{rg}|{st}|{cd}|{i}"
               for rg in REGIMES for st in STALENESS
               for cd in CONDITIONS for i in range(N_INDEX)]

    out = {
        "scheme": "COMMON RANDOM NUMBERS -- one base seed per (regime, staleness, index), shared by C1/C2/C3",
        "base_derivation": "base_seed(regime,staleness,index) = int(sha256('exp16-v2-base'|regime|staleness|index).hexdigest()[:8],16)",
        "n0_derivation": "n0_seed(regime,staleness,index) = int(sha256('exp16-v2-negative-control'|regime|staleness|index).hexdigest()[:8],16)",
        "condition_is_NOT_in_the_seed_key": True,
        "shared_across_C1_C2_C3_for_fixed_base_seed": [
            "base orbit", "OD-error draw and component signs", "OU trajectory",
            "pass schedule", "model initialisation",
            "train/validation/deployment row split"],
        "shared_across_C2_C3_additionally": [
            "manoeuvre magnitude", "manoeuvre direction", "state-update equation",
            "deployment exposure"],
        "only_difference_C2_vs_C3": "manoeuvre onset relative to freeze",
        "index_range": [0, N_INDEX - 1],
        "regime_order": list(REGIMES),
        "staleness_order": list(STALENESS),
        "condition_order": list(CONDITIONS),
        "base_cell_order": base_order,
        "n_base_cells": len(base_order),
        "n_base_seeds": len(base_order) * N_INDEX,
        "n_n0_seeds": len(n0) * N_INDEX,
        "n_formal_runs": len(run_ids),
        "run_ids_carry_no_randomness": True,
        "retired_manifests": {
            "executed": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009,
                         1010, 1011, 1012, 90001, 90002, 90003,
                         7, 11,
                         777001, 777002, 777003, 777004, 777005, 777006,
                         777007, 777008, 777009, 777010, 777011, 777012,
                         811001, 811002, 811003, 811004, 811005, 811006,
                         811007, 811008, 811009, 811010, 811011, 811012],
            "executed_note": "1001-1012 + 90001-90003: first review emulation and author probes. 7 and 11: numpy default_rng seeds in the author's shift/manoeuvre probes. 777001-777012 and 811001-811012: the SECOND review's v2/v2.1 emulation, on which harm outcomes, gate decisions, valratios and floor verdicts were inspected -- exactly the contamination that retired 1001-1012.",
            "unexecuted_scenario_keyed": "first v2 manifest, keyed on scenario_key including condition; retired for violating common random numbers"},
        "never_run_before_approval": True,
        "base_seeds": base,
        "n0_seeds": n0,
    }
    body = json.dumps(out, indent=1, sort_keys=False)
    out["self_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    Path("evaluation_seeds_v2.json").write_text(json.dumps(out, indent=1))

    flat = [s for v in base.values() for s in v] + [s for v in n0.values() for s in v]
    print(f"base cells={len(base_order)}  base seeds={len(base_order)*N_INDEX}  "
          f"N0 seeds={len(n0)*N_INDEX}  formal runs={len(run_ids)}")
    print(f"distinct={len(set(flat))} of {len(flat)}   "
          f"collision with burned={set(flat) & set(out['retired_manifests']['executed'])}")
    print(f"manifest_sha256={out['self_sha256'][:16]}")
    for k in base_order[:2]:
        print(f"  {k:28s} {base[k][:3]}  <- shared by C1, C2, C3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
