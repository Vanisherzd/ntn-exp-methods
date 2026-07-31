#!/usr/bin/env python3
"""Analysis D: the frozen L4.7 on the along-track observable, plus the reporting three
reviewers asked for -- a one-sided upper confidence bound on each ICC, and multiplicity.

Registered in the addendum to evaluation/real_data/PREREGISTRATION.md before this file existed.

WHY THIS EXISTS. Analyses A-C used publication lag and pass elevation. Two reviewers made the
same correct objection: elevation is a deterministic function of the grouping, so on that
observable a PASS and a HALT are both uninformative about the claim in section I-A(v), which is
about along-track prediction ERROR. This measures that.

NO MODEL IS FITTED. For consecutive element sets k and k+1 of one object, SGP4 propagates both to
a common time and the in-track component of the position difference is taken. Both states come
from the catalogue. This is the standard element-set-to-element-set consistency residual, measured
and grouped -- not the stopped residual-learning line, which fitted a correction to it.

THE DETECTOR IS NOT TOUCHED. The upper confidence bound and the multiplicity arithmetic are
computed HERE, in reporting, not added to contract_layers.py. Adding them to the rule after seeing
external outcomes is exactly the detector-design cycle this campaign forbids, and the gate asserts
the rule's hash against the pre-registration.

Run: python evaluation/scripts/real_l47_alongtrack.py
Writes: evaluation/real_data/l47_alongtrack.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from math import comb, factorial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evaluation" / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import contract_layers as CL          # noqa: E402  -- FROZEN
import numpy as np                    # noqa: E402
import orbit_evidence.experiment_contract.experiment_contract as EC  # noqa: E402
from sgp4.api import Satrec           # noqa: E402

import real_l47_application as RA     # noqa: E402  -- reuse the registered geometry

OUT = ROOT / "evaluation" / "real_data" / "l47_alongtrack.json"
PREREG_SHA = "07baad27026ebc2242706dd5f542609b80ccb8ab706cba12c0fb2ce15521e58b"


def rtn_intrack_km(rec_a: dict, rec_b: dict, jd: float) -> float | None:
    """In-track component of (state from A) - (state from B), both propagated to jd.

    RTN basis is built from A's own state: radial along r, cross-track along r x v,
    in-track completing the triad. No truth reference and no fit -- two catalogue states
    differenced at one instant.
    """
    sa = Satrec.twoline2rv(rec_a["TLE_LINE1"], rec_a["TLE_LINE2"])
    sb = Satrec.twoline2rv(rec_b["TLE_LINE1"], rec_b["TLE_LINE2"])
    ea, ra, va = sa.sgp4(jd, 0.0)
    eb, rb, _ = sb.sgp4(jd, 0.0)
    if ea != 0 or eb != 0:
        return None
    ra, va, rb = np.array(ra), np.array(va), np.array(rb)
    radial = ra / np.linalg.norm(ra)
    cross = np.cross(ra, va)
    cross /= np.linalg.norm(cross)
    intrack = np.cross(cross, radial)
    return float((ra - rb) @ intrack)


def _stream(agg: np.ndarray, grp: np.ndarray) -> int:
    """The frozen rule's own design-specific seed derivation, so p matches its decision."""
    import hashlib
    n_groups = len({str(g) for g in grp.tolist()})
    key = f"0|{n_groups}|{agg.size}|{np.round(float(np.sum(agg)) * 1e6):.0f}"
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], "big")


def icc_bound(agg: np.ndarray, grp: np.ndarray, side: str = "upper", alpha: float = 0.05,
              n_boot: int = 2000, seed: int = 20260731) -> float:
    """One-sided 1-alpha bound on ICC by resampling coarser GROUPS with replacement.

    A permutation reference tests a null; it does not bound an effect. The claim a PASS wants
    to support is an equivalence claim -- dependence small enough that the unit is adequate --
    so an upper bound is the right object, and a reviewer was right that the paper had none.
    Groups are the resampling unit because they are the exchangeable blocks.
    """
    rng = np.random.default_rng(seed)
    labels = np.unique(grp.astype(str))
    if labels.size < 2:
        return float("nan")
    draws = []
    for _ in range(n_boot):
        pick = rng.choice(labels, size=labels.size, replace=True)
        vals, gs = [], []
        for j, g in enumerate(pick):
            m = grp.astype(str) == g
            vals.append(agg[m])
            gs.append(np.full(m.sum(), f"b{j}"))
        v = np.concatenate(vals)
        gg = np.concatenate(gs)
        if np.unique(gg).size < 2:
            continue
        r = EC.within_group_icc(v, gg)
        if np.isfinite(r):
            draws.append(float(r))
    if not draws:
        return float("nan")
    return float(np.quantile(draws, 1.0 - alpha if side == "upper" else alpha))


def min_attainable_p(n_groups: int, per_group: int) -> float:
    """Smallest p the permutation reference can attain for a balanced design.

    This is why the abstention floor sits where it does, and a reviewer correctly pointed out
    the paper mislabelled it a POWER precondition. It is an ATTAINABILITY one: with three groups
    of two the design admits 6!/(2!^3 3!) = 15 distinct assignments, so the smallest possible
    p is 1/15 = 0.067 > 0.05 and the nominal level cannot be reached at all. Four groups of two
    admit 105, giving 1/105 = 0.0095.
    """
    n = n_groups * per_group
    ways = factorial(n)
    for _ in range(n_groups):
        ways //= factorial(per_group)
    ways //= factorial(n_groups)
    return 1.0 / ways


def run(values, unit_ids, coarser_ids, label: str) -> dict:
    base = {"grouping": label, "n_units": len(set(unit_ids)),
            "n_labelled_coarser": len(set(coarser_ids))}
    u, agg = EC.aggregate_repeated_measures(list(values), list(unit_ids))
    cmap: dict = {}
    for a, b in zip(unit_ids, coarser_ids):
        cmap.setdefault(a, b)
    grp = np.array([cmap[k] for k in u.tolist()])
    eff = sum(1 for g in np.unique(grp.astype(str))
              if np.sum(grp.astype(str) == g) >= 2)
    try:
        v = CL.check_statistical_unit(values, unit_ids, coarser_ids)
        out = {**base, **v}
    except CL.ContractViolation as exc:
        # Recompute p with the FROZEN rule's own permutation helper, at its own defaults, so the
        # reported statistic is the one the decision was made on rather than parsed from a string.
        icc_h = float(EC.within_group_icc(agg, grp))
        pv, crit = CL._icc_permutation_pvalue(icc_h, agg, grp, 400,
                                              np.random.default_rng(_stream(agg, grp)))
        out = {**base, "verdict": "HALT", "icc": round(icc_h, 4),
               "p_value": round(float(pv), 4), "permutation_critical": round(float(crit), 4),
               "n_coarser_groups": eff, "message": str(exc)}
    icc = out.get("icc")
    out["icc_truncated_at_zero"] = (icc is not None and icc == 0.0)
    # Three decimals: the precision a paper quotes, so the manuscript and the artifact can be
    # required to agree exactly rather than approximately.
    out["icc_upper_95_one_sided"] = (None if icc is None else
                                     round(icc_bound(agg, grp, "upper"), 3))
    # A HALT is an argument that rho exceeds zero, so it needs the LOWER bound; the upper bound is
    # what a PASS needs. Two reviewers flagged that only the upper was reported. Both now are.
    out["icc_lower_95_one_sided"] = (None if icc is None else
                                     round(icc_bound(agg, grp, "lower"), 3))
    if icc is not None:
        out["icc"] = round(float(icc), 3)
    return out


def main() -> int:
    have = hashlib.sha256(
        (ROOT / "evaluation" / "scripts" / "contract_layers.py").read_bytes()).hexdigest()
    if have != PREREG_SHA:
        raise SystemExit(f"contract_layers.py is {have[:12]}, pre-registered {PREREG_SHA[:12]} "
                         "-- the rule changed, so this analysis is not the registered one")

    recs = RA.load_records()
    rows, dropped, sgp4_fail = [], 0, 0
    for obj, rs in recs.items():
        for i, r in enumerate(rs):
            nxt = rs[i + 1] if i + 1 < len(rs) else None
            if nxt is None or nxt["EPOCH"] == r["EPOCH"]:
                # No successor element set in the window, or a republication of the same one.
                dropped += len(RA.passes_for(r))
                continue
            sat = Satrec.twoline2rv(r["TLE_LINE1"], r["TLE_LINE2"])
            jd0 = sat.jdsatepoch + sat.jdsatepochF
            el, secs = RA.elevations_deg(r)
            above = np.nan_to_num(el, nan=-90.0) >= RA.ELEV_MASK_DEG
            start = None
            for k, a in enumerate(above):
                if a and start is None:
                    start = k
                elif not a and start is not None:
                    if k - start >= 2:
                        mid = (secs[start] + secs[k - 1]) / 2.0
                        d = rtn_intrack_km(r, nxt, jd0 + mid / 86400.0)
                        if d is None:
                            # SGP4 error code at the midpoint. Counted, not silently skipped:
                            # three reviewers independently found that 269 + 59 did not reconcile
                            # to 331, and this is the missing three.
                            sgp4_fail += 1
                        else:
                            rows.append({"object": obj, "elset": f"{obj}|{r['EPOCH']}",
                                         "pass_id": f"{obj}|{r['EPOCH']}|{start}",
                                         "intrack_km": d})
                    start = None
            # A run still above the mask when the 24 h window ends. passes_for() closes it and
            # counts it; this loop only appended on a falling edge, so those passes were silently
            # absent -- exactly the 331 - 328 that three reviewers independently found did not
            # reconcile. Closed the same way passes_for does.
            if start is not None and len(above) - start >= 2:
                mid = (secs[start] + secs[len(above) - 1]) / 2.0
                d = rtn_intrack_km(r, nxt, jd0 + mid / 86400.0)
                if d is None:
                    sgp4_fail += 1
                else:
                    rows.append({"object": obj, "elset": f"{obj}|{r['EPOCH']}",
                                 "pass_id": f"{obj}|{r['EPOCH']}|{start}",
                                 "intrack_km": d})

    v = [x["intrack_km"] for x in rows]
    res = {
        "manifest": {
            "protocol": "evaluation/real_data/PREREGISTRATION.md (addendum, analysis D)",
            "contract_layers_sha256": have,
            "observable": "in-track component of the position difference between an element set "
                          "and its successor, both propagated to the pass midpoint, km. "
                          "No model is fitted.",
            "n_passes_used": len(rows),
            "n_passes_dropped_no_successor": dropped,
            "n_passes_dropped_sgp4_error": sgp4_fail,
            "n_passes_raw": len(rows) + dropped + sgp4_fail,
            "pass_accounting": "raw = used + dropped_no_successor + dropped_sgp4_error",
            "n_objects": len({r["object"] for r in rows}),
            "n_elsets": len({r["elset"] for r in rows}),
            "intrack_abs_km": {"median": round(float(np.median(np.abs(v))), 3),
                               "p90": round(float(np.percentile(np.abs(v), 90)), 3),
                               "max": round(float(np.max(np.abs(v))), 3)},
        },
        "analyses": {
            "D1_pass_in_elementset": run(v, [r["pass_id"] for r in rows],
                                         [r["elset"] for r in rows],
                                         "D1: pass -> element set, in-track residual (km)"),
            "D2_pass_in_object": run(v, [r["pass_id"] for r in rows],
                                     [r["object"] for r in rows],
                                     "D2: pass -> object, in-track residual (km)"),
        },
        "attainability_floor": {
            "note": "The abstention floor is an ATTAINABILITY precondition, not a power one: "
                    "below it the nominal level cannot be reached by any permutation reference. "
                    "The paper previously mislabelled it.",
            "min_p_3_groups_of_2": round(min_attainable_p(3, 2), 4),
            "min_p_4_groups_of_2": round(min_attainable_p(4, 2), 4),
            "alpha": 0.05,
        },
    }
    # D3: element set -> object, on the per-set mean residual.
    byset: dict[str, list[float]] = {}
    setobj: dict[str, str] = {}
    for r in rows:
        byset.setdefault(r["elset"], []).append(r["intrack_km"])
        setobj[r["elset"]] = r["object"]
    ks = list(byset)
    res["analyses"]["D3_elementset_in_object"] = run(
        [float(np.mean(byset[k])) for k in ks], ks, [setobj[k] for k in ks],
        "D3: element set -> object, mean in-track residual (km)")

    # Multiplicity, which a reviewer correctly noted was missing for the A-C per-object tests.
    n_tests = 14
    res["multiplicity"] = {
        "n_decisions_in_analyses_A_to_C": n_tests,
        "p_at_least_one_halt_under_global_null": round(1 - 0.95 ** n_tests, 3),
        "note": "Eleven per-object tests plus three pooled. One halt is at chance level under "
                "the global null, so the single halt in analyses A-C is not evidence of "
                "dependence and the paper must not present it as such.",
    }
    OUT.write_text(json.dumps(res, indent=1) + "\n")

    m = res["manifest"]
    print(f"passes used {m['n_passes_used']}  dropped (no successor) "
          f"{m['n_passes_dropped_no_successor']}  objects {m['n_objects']}  "
          f"element sets {m['n_elsets']}")
    print(f"|in-track| median {m['intrack_abs_km']['median']} km  "
          f"p90 {m['intrack_abs_km']['p90']} km  max {m['intrack_abs_km']['max']} km\n")
    for k, r in res["analyses"].items():
        icc = r.get("icc")
        pv = r.get("p_value")
        ub = r.get("icc_upper_95_one_sided")
        print(f"  {k:28s} {r['verdict']:14s} units={r['n_units']:4d} "
              f"groups={r.get('n_coarser_groups','-'):>4} "
              f"ICC={'n/a' if icc is None else f'{icc:.3f}':>7s} "
              f"p={'n/a' if pv is None else f'{pv:.4f}':>7s} "
              f"ICC95up={'n/a' if ub is None else f'{ub:.3f}'}")
    a = res["attainability_floor"]
    print(f"\nattainability: min p at 3 groups of 2 = {a['min_p_3_groups_of_2']} > alpha; "
          f"at 4 groups of 2 = {a['min_p_4_groups_of_2']}")
    print(f"multiplicity: P(>=1 halt | global null) over {n_tests} tests = "
          f"{res['multiplicity']['p_at_least_one_halt_under_global_null']}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
