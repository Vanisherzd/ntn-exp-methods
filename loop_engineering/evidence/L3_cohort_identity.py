#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""L3 — OLD vs NEW cohort identity check (invariant I3).

Only model inputs and model-derived results may differ. Everything that defines
the scientific cohort must be bit-identical: satellites, staleness bands, pair
counts, split sizes, screen membership, and the SGP4 baseline metrics (which do
not depend on the learned candidates at all).
"""
from __future__ import annotations
import json, sys
from pathlib import Path

E = Path("/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/experiments/exp14_multisat_generalization_matrix")
OLD = E / "phase2_reject_sensitivity/reject_sensitivity_results.json"
NEW = E / "outputs/deployable_v1/phase2/reject_sensitivity_results.json"

KEY = ("satellite", "staleness_h", "threshold_hz")
# cohort-defining fields: must be identical
COHORT = ["candidate_pairs", "accepted_pairs", "rejected_pairs", "reject_rate_pct",
          "n_train_pairs", "n_validation_pairs", "n_test_pairs", "status"]
# SGP4 baseline is independent of the learned family: must also be identical
BASELINE = ["val_sgp4_mae_hz", "test_sgp4_mae_hz", "test_sgp4_p95_hz",
            "test_sgp4_p99_hz", "test_sgp4_outage_proxy", "block_bootstrap_days"]


def rows(p):
    return {tuple(str(r[k]) for k in KEY): r
            for r in json.loads(p.read_text())["rows"]}


def main() -> int:
    if not NEW.exists():
        print(f"NEW artifact not present yet: {NEW}")
        return 2
    o, n = rows(OLD), rows(NEW)
    fail = []
    if set(o) != set(n):
        fail.append(f"cell key sets differ: only-old={len(set(o)-set(n))} "
                    f"only-new={len(set(n)-set(o))}")
    common = sorted(set(o) & set(n))
    print(f"cells: old={len(o)} new={len(n)} common={len(common)}")
    for grp, fields in (("COHORT", COHORT), ("SGP4 BASELINE", BASELINE)):
        bad = []
        for k in common:
            for f in fields:
                if f in o[k] and f in n[k] and o[k][f] != n[k][f]:
                    bad.append((k, f, o[k][f], n[k][f]))
        print(f"{grp}: {'IDENTICAL' if not bad else f'{len(bad)} MISMATCHES'}")
        for b in bad[:6]:
            print("   ", b)
        if bad:
            fail.append(f"{grp} mismatch x{len(bad)}")
    # model selection is EXPECTED to differ
    import collections
    so = collections.Counter(o[k]["selected_model"] for k in common)
    sn = collections.Counter(n[k]["selected_model"] for k in common)
    print(f"\nselected_model OLD: {dict(so)}")
    print(f"selected_model NEW: {dict(sn)}")
    prim_o = [k for k in common if k[2] == "1500" and o[k]["status"] == "evaluated"]
    print(f"\nprimary cells (1500 Hz): {len(prim_o)}")
    print(f"  gate open OLD: {sum(1 for k in prim_o if o[k]['gate_decision']=='open')}")
    print(f"  gate open NEW: {sum(1 for k in prim_o if n[k]['gate_decision']=='open')}")
    ev = [k for k in common if o[k]["status"] == "evaluated"]
    print(f"screening cells evaluated: {len(ev)}")
    print(f"  gate open OLD: {sum(1 for k in ev if o[k]['gate_decision']=='open')}")
    print(f"  gate open NEW: {sum(1 for k in ev if n[k]['gate_decision']=='open')}")
    for k in ev:
        if n[k]["gate_decision"] == "open":
            print(f"  NEW OPENING: {k} model={n[k]['selected_model']} "
                  f"val={n[k]['val_improvement_pct']}% test={n[k]['test_improvement_pct']}%")
    print("\nL3 COHORT IDENTITY: " + ("PASS" if not fail else "FAIL " + "; ".join(fail)))
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
