#!/usr/bin/env python3
"""R2 + R3 + R4 -- reference-ensemble labels, censoring audit, visibility diagnostics.

Runs only AFTER the registry is frozen. It may change a row's label status, value,
uncertainty or closure time; it may never delete a row or alter the schedule.

The label replaces the single arbitrarily-chosen later element -- whose choice moved
the target further than the target's own magnitude -- with the median over every
qualifying later solution, plus a published uncertainty:

    D_ref_ens = median_q D_ref,q(t_tx)
    sigma_ref = 1.4826 * MAD_q D_ref,q(t_tx)
    r         = D_ref_ens - f_phys(t_tx)
    t_close   = t_tx + closure_horizon

Usage:
    python build_ensemble_labels.py --feasibility            # R2 dataset-only sweep
    python build_ensemble_labels.py --scenario NOMINAL --horizon 48 --k-min 2
"""

from __future__ import annotations

import argparse
import bisect
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from sgp4.api import Satrec

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_visible_registry as R  # noqa: E402

SPEC = json.loads((HERE / "label_ensemble_spec.json").read_text())
GATE = SPEC["censoring_gate"]
FEAS = SPEC["feasibility_analysis"]

STATUS_COMPLETE = "COMPLETE"
STATUS_CENSORED = "CENSORED_INSUFFICIENT_REFERENCES"
STATUS_AMBIGUOUS = "AMBIGUOUS_HIGH_SPREAD"
STATUS_INVALID = "INVALID_SOURCE_METADATA"

MAD_SCALE = 1.4826
EPS = 1e-9


def _propagate_doppler(rec: Satrec, t_tx: float) -> float | None:
    elev, rng, dopp, ok = R.geometry_series(rec, np.array([t_tx]))
    return float(dopp[0]) if ok[0] else None


def _elev_of(rec: Satrec, t_tx: float) -> float | None:
    elev, _, _, ok = R.geometry_series(rec, np.array([t_tx]))
    return float(elev[0]) if ok[0] else None


def label_row(reg: dict[str, np.ndarray], i: int, avail: list[dict[str, Any]],
              horizon_h: float, k_min: int,
              creations: list[dt.datetime] | None = None,
              cache: dict[str, Satrec] | None = None) -> dict[str, Any]:
    """Build the ensemble label for registry row i. Never mutates ``reg``."""
    if creations is None:
        creations = [r["creation_dt"] for r in avail]
    if cache is None:
        cache = {}
    t_tx = float(reg["t_tx"][i])
    tx_dt = R.EPOCH0 + dt.timedelta(seconds=t_tx)
    hi = tx_dt + dt.timedelta(hours=horizon_h)

    lo_idx = bisect.bisect_right(creations, tx_dt)
    hi_idx = bisect.bisect_right(creations, hi)
    held_key = reg["held_tle_id"][i]

    seen: set[str] = set()
    members: list[float] = []
    member_ids: list[str] = []
    member_elev: list[float] = []
    bad_meta = 0
    for cand in avail[lo_idx:hi_idx]:
        pk = cand["physical_key"]
        if pk in seen:
            continue
        cid = f"{cand['epoch'].isoformat()}|{pk[:16]}"
        if cid in held_key:
            continue                     # the held element is not its own reference
        key = cand["line1"] + cand["line2"]
        rec = cache.get(key)
        if rec is None:
            try:
                rec = Satrec.twoline2rv(cand["line1"], cand["line2"])
            except Exception:
                bad_meta += 1
                continue
            cache[key] = rec
        d = _propagate_doppler(rec, t_tx)
        if d is None:
            bad_meta += 1
            continue
        seen.add(pk)
        members.append(d)
        member_ids.append(cid)
        member_elev.append(_elev_of(rec, t_tx) or -90.0)

    base = {
        "tx_id": str(reg["tx_id"][i]),
        "n_references": len(members),
        "n_invalid_sources": bad_meta,
        "member_doppler_hz": members,
        "member_ids": member_ids,
        "t_close": t_tx + horizon_h * 3600.0,
    }
    if len(members) < k_min:
        status = STATUS_INVALID if (bad_meta and not members) else STATUS_CENSORED
        return {**base, "status": status, "ref_ensemble_hz": np.nan,
                "sigma_ref_hz": np.nan, "residual_hz": np.nan,
                "ref_consensus_elev_deg": np.nan}

    arr = np.asarray(members)
    med = float(np.median(arr))
    sigma = float(MAD_SCALE * np.median(np.abs(arr - med)))
    resid = med - float(reg["pred_stale_doppler_hz"][i])
    status = STATUS_AMBIGUOUS if sigma > abs(resid) else STATUS_COMPLETE
    return {**base, "status": status, "ref_ensemble_hz": med,
            "sigma_ref_hz": sigma, "residual_hz": resid,
            "ref_consensus_elev_deg": float(np.median(member_elev))}


# --------------------------------------------------------------------------
# R2 feasibility -- dataset-only. Never inspects model performance.
# --------------------------------------------------------------------------


def feasibility(scenario: str, threshold_deg: int, sample_stride: int = 23
                ) -> dict[str, Any]:
    tag = f"{scenario}_thr{threshold_deg}"
    files = sorted((HERE / "registry" / tag).glob("*.npz"))
    sats = {s.key: s for s in R.load_satellites()}
    out: dict[str, Any] = {"scenario": scenario, "threshold_deg": threshold_deg,
                           "grid": []}
    for horizon in FEAS["closure_horizons_h"]:
        for k_min in FEAS["k_min_values"]:
            per_sat = []
            for f in files:
                sd = sats.get(f.stem)
                if sd is None:
                    continue
                reg = {k: v for k, v in np.load(f, allow_pickle=False).items()}
                avail = R.availability_index(sd)
                creations = [r["creation_dt"] for r in avail]
                cache: dict[str, Satrec] = {}
                idx = range(0, reg["t_tx"].size, sample_stride)
                counts = {STATUS_COMPLETE: 0, STATUS_CENSORED: 0,
                          STATUS_AMBIGUOUS: 0, STATUS_INVALID: 0}
                nref, sig, delays = [], [], []
                for i in idx:
                    o = label_row(reg, i, avail, float(horizon), k_min,
                                  creations, cache)
                    counts[o["status"]] += 1
                    nref.append(o["n_references"])
                    if np.isfinite(o["sigma_ref_hz"]):
                        sig.append(o["sigma_ref_hz"])
                    delays.append(horizon)
                n = sum(counts.values())
                labelled = counts[STATUS_COMPLETE] + counts[STATUS_AMBIGUOUS]
                per_sat.append({
                    "satellite": sd.name, "n_sampled": n,
                    "complete_rate": round(counts[STATUS_COMPLETE] / max(n, 1), 4),
                    "labelled_rate": round(labelled / max(n, 1), 4),
                    "censored_rate": round(counts[STATUS_CENSORED] / max(n, 1), 4),
                    "ambiguous_rate": round(counts[STATUS_AMBIGUOUS] / max(n, 1), 4),
                    "n_ref_p50": float(np.percentile(nref, 50)) if nref else 0.0,
                    "sigma_p50": round(float(np.percentile(sig, 50)), 5) if sig else None,
                    "sigma_p90": round(float(np.percentile(sig, 90)), 5) if sig else None,
                })
            comp = [p["complete_rate"] for p in per_sat]
            lab = [p["labelled_rate"] for p in per_sat]
            sg = [p["sigma_p50"] for p in per_sat if p["sigma_p50"] is not None]
            out["grid"].append({
                "closure_horizon_h": horizon, "k_min": k_min,
                "mean_complete_rate": round(float(np.mean(comp)), 4) if comp else 0.0,
                "min_complete_rate": round(float(np.min(comp)), 4) if comp else 0.0,
                "mean_labelled_rate": round(float(np.mean(lab)), 4) if lab else 0.0,
                "min_labelled_rate": round(float(np.min(lab)), 4) if lab else 0.0,
                "sigma_p50_across_satellites": round(float(np.median(sg)), 5) if sg else None,
                "sigma_spread_across_satellites": (
                    round(float(np.max(sg) - np.min(sg)), 5) if sg else None),
                "closure_delay_h": horizon,
                "per_satellite": per_sat,
            })
            print(f"  horizon={horizon:3d}h k_min={k_min}  "
                  f"complete mean={out['grid'][-1]['mean_complete_rate']:.3f} "
                  f"min={out['grid'][-1]['min_complete_rate']:.3f}  "
                  f"labelled mean={out['grid'][-1]['mean_labelled_rate']:.3f} "
                  f"min={out['grid'][-1]['min_labelled_rate']:.3f}  "
                  f"sigma_p50={out['grid'][-1]['sigma_p50_across_satellites']}",
                  flush=True)
    return out


# --------------------------------------------------------------------------
# full labelling pass + R3 censoring audit + R4 visibility diagnostics
# --------------------------------------------------------------------------

LABEL_FIELDS = ("status_code", "n_references", "ref_ensemble_hz", "sigma_ref_hz",
                "residual_hz", "t_close", "ref_consensus_elev_deg")
STATUS_CODES = {STATUS_COMPLETE: 0, STATUS_CENSORED: 1, STATUS_AMBIGUOUS: 2,
                STATUS_INVALID: 3}
CODE_TO_STATUS = {v: k for k, v in STATUS_CODES.items()}


def label_satellite(reg: dict[str, np.ndarray], sd, horizon_h: float, k_min: int
                    ) -> dict[str, np.ndarray]:
    avail = R.availability_index(sd)
    creations = [r["creation_dt"] for r in avail]
    cache: dict[str, Satrec] = {}
    n = reg["t_tx"].size
    cols = {f: np.full(n, np.nan) for f in LABEL_FIELDS}
    ids: list[str] = []
    for i in range(n):
        o = label_row(reg, i, avail, horizon_h, k_min, creations, cache)
        cols["status_code"][i] = STATUS_CODES[o["status"]]
        cols["n_references"][i] = o["n_references"]
        cols["ref_ensemble_hz"][i] = o["ref_ensemble_hz"]
        cols["sigma_ref_hz"][i] = o["sigma_ref_hz"]
        cols["residual_hz"][i] = o["residual_hz"]
        cols["t_close"][i] = o["t_close"]
        cols["ref_consensus_elev_deg"][i] = o["ref_consensus_elev_deg"]
        ids.append("|".join(o["member_ids"]))
    cols["member_ids"] = np.array(ids, dtype=object)
    return cols


def smd(a: np.ndarray, b: np.ndarray) -> float:
    """Absolute standardized mean difference, per the pre-registered formula."""
    if a.size < 2 or b.size < 2:
        return float("nan")
    va, vb = float(np.var(a, ddof=1)), float(np.var(b, ddof=1))
    pooled = np.sqrt((va + vb) / 2.0)
    if pooled < 1e-12:
        return 0.0
    return float(abs(a.mean() - b.mean()) / pooled)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--feasibility", action="store_true")
    ap.add_argument("--scenario", default="NOMINAL")
    ap.add_argument("--threshold-deg", type=int, default=10)
    ap.add_argument("--horizon", type=float, default=None)
    ap.add_argument("--k-min", type=int, default=None)
    args = ap.parse_args()

    if args.feasibility:
        allout = {}
        for sc in ("NOMINAL", "DEGRADED"):
            print(f"=== feasibility {sc} @{args.threshold_deg}deg ===", flush=True)
            allout[sc] = feasibility(sc, args.threshold_deg)
        (HERE / "R2_feasibility.json").write_text(json.dumps(allout, indent=1))
        print(f"wrote {HERE / 'R2_feasibility.json'}")
        return 0

    assert args.horizon and args.k_min, "--horizon and --k-min required"
    tag = f"{args.scenario}_thr{args.threshold_deg}"
    files = sorted((HERE / "registry" / tag).glob("*.npz"))
    sats = {s.key: s for s in R.load_satellites()}
    out_dir = HERE / "labels" / f"{tag}_h{int(args.horizon)}_k{args.k_min}"
    out_dir.mkdir(parents=True, exist_ok=True)

    audit: dict[str, Any] = {"scenario": args.scenario,
                             "threshold_deg": args.threshold_deg,
                             "closure_horizon_h": args.horizon,
                             "k_min": args.k_min,
                             "spec_sha256": hashlib.sha256(
                                 (HERE / "label_ensemble_spec.json").read_bytes()
                             ).hexdigest(),
                             "satellites": []}
    smd_vars = GATE["principal_continuous_variables"]
    for f in files:
        sd = sats.get(f.stem)
        if sd is None:
            continue
        reg = {k: v for k, v in np.load(f, allow_pickle=False).items()}
        h_before = R.registry_hash({k: v for k, v in reg.items()})
        lab = label_satellite(reg, sd, args.horizon, args.k_min)
        h_after = R.registry_hash({k: v for k, v in reg.items()})
        assert h_before == h_after, "labelling mutated the frozen registry"

        code = lab["status_code"]
        n = code.size
        counts = {s: int((code == c).sum()) for s, c in STATUS_CODES.items()}
        labelled = (code == 0) | (code == 2)
        censored = ~labelled

        # R3 selection-bias diagnostic on PRE-TRANSMISSION quantities only
        smds = {}
        for v in smd_vars:
            if v == "abs_pred_stale_doppler_hz":
                x = np.abs(reg["pred_stale_doppler_hz"])
            elif v == "episode_time_s":
                x = reg["t_refresh"]
            else:
                x = reg[v]
            smds[v] = round(smd(x[labelled], x[censored]), 4)

        # R4 visibility disagreement (diagnostic only, deletes nothing)
        rce = lab["ref_consensus_elev_deg"]
        ok = np.isfinite(rce)
        agree = int(np.sum(ok & (rce >= args.threshold_deg)))
        disagree = int(np.sum(ok & (rce < 0.0)))

        np.savez_compressed(
            out_dir / f"{sd.key}.npz",
            **{k: v for k, v in reg.items()},
            **{k: (v.astype(str) if getattr(v, "dtype", None) == object else v)
               for k, v in lab.items()})
        sig = lab["sigma_ref_hz"][labelled]
        res = np.abs(lab["residual_hz"][labelled])
        rec = {
            "satellite": sd.name, "key": sd.key, "n_scheduled": n,
            **{f"n_{k}": v for k, v in counts.items()},
            "complete_rate": round(counts[STATUS_COMPLETE] / max(n, 1), 4),
            "labelled_rate": round(int(labelled.sum()) / max(n, 1), 4),
            "n_ref_p50": float(np.percentile(lab["n_references"], 50)),
            "sigma_ref_p50": round(float(np.percentile(sig, 50)), 5) if sig.size else None,
            "abs_r_p50": round(float(np.percentile(res, 50)), 5) if res.size else None,
            "frac_sigma_gt_r": round(float(np.mean(sig > res)), 4) if sig.size else None,
            "smd_labelled_vs_censored": smds,
            "max_abs_smd": round(float(np.nanmax(list(smds.values()))), 4),
            "ref_consensus_visible": agree,
            "ref_consensus_below_horizon": disagree,
            "visibility_disagreement_rate": round(disagree / max(int(ok.sum()), 1), 4),
            "registry_sha256": h_before,
        }
        audit["satellites"].append(rec)
        print(f"  {sd.name[:22]:22s} n={n:6d} complete={rec['complete_rate']:.3f} "
              f"labelled={rec['labelled_rate']:.3f} sigma_p50={rec['sigma_ref_p50']} "
              f"|r|_p50={rec['abs_r_p50']} maxSMD={rec['max_abs_smd']:.3f} "
              f"visDisagree={rec['visibility_disagreement_rate']:.3f}", flush=True)

    comp = [s["complete_rate"] for s in audit["satellites"]]
    labr = [s["labelled_rate"] for s in audit["satellites"]]
    maxsmd = [s["max_abs_smd"] for s in audit["satellites"]]
    audit["gate"] = {
        "overall_complete_rate": round(float(np.mean(comp)), 4),
        "min_satellite_complete_rate": round(float(np.min(comp)), 4),
        "overall_labelled_rate": round(float(np.mean(labr)), 4),
        "min_satellite_labelled_rate": round(float(np.min(labr)), 4),
        "max_abs_smd_any_satellite": round(float(np.nanmax(maxsmd)), 4),
        "completeness_overall_pass": float(np.mean(comp)) >= GATE["completeness_overall_min"],
        "completeness_per_satellite_pass": float(np.min(comp)) >= GATE["completeness_per_satellite_min"],
        "smd_pass": float(np.nanmax(maxsmd)) <= GATE["smd_max"],
    }
    audit["gate"]["R3_VERDICT"] = (
        "PASS" if all(audit["gate"][k] for k in
                      ("completeness_overall_pass", "completeness_per_satellite_pass",
                       "smd_pass")) else "FAIL")
    name = f"R3_censoring_audit_{tag}_h{int(args.horizon)}_k{args.k_min}.json"
    (HERE / name).write_text(json.dumps(audit, indent=1))
    print(json.dumps(audit["gate"], indent=1))
    print(f"wrote {HERE / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
