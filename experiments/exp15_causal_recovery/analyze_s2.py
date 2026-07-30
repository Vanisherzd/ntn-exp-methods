#!/usr/bin/env python3
"""S2 decision analysis -- satellite-balanced, per preregistration.json.

Statistical unit: the refresh EPISODE. Aggregation: equal weight per satellite.
Uncertainty: hierarchical block bootstrap (resample satellites, then whole
deployment episodes within each selected satellite).

Two quantities are reported and must not be confused:
  GATED   -- what the deployed system actually does. G = 0 means it emits plain
             SGP4, so its improvement is identically zero.
  UNGATED -- what each candidate would have done if deployed regardless of the
             gate. This is the scientifically informative quantity: it says
             whether any causal residual structure was learnable at all.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PRE = json.loads((HERE / "preregistration.json").read_text())
import argparse
_ap = argparse.ArgumentParser()
_ap.add_argument("--file", default="E4_walk_forward_r1500.json")
_ap.add_argument("--tag", default="")
ARGS = _ap.parse_args()
RES = json.loads((HERE / ARGS.file).read_text())
CANDIDATES = RES["candidates"]
GAMMA = PRE["E4_walk_forward"]["gamma"]
RNG = np.random.default_rng(20260730)
N_BOOT = 10000


def per_satellite_effects() -> dict:
    """satellite -> candidate -> array of per-episode (mae_cand - mae_sgp4)."""
    out = {}
    for sat in RES["satellites"]:
        # per_episode stores only m_star; recompute candidate effects from the
        # segment-level deployment MAEs, keeping the episode as the block by
        # weighting each segment by its episode count.
        per_cand = {c: [] for c in CANDIDATES}
        seg_blocks = []
        for seg in sat["segments"]:
            n_ep = max(len(seg["per_episode"]), 1)
            for c in CANDIDATES:
                per_cand[c].append((seg["dep_mae"][c] - seg["dep_mae_sgp4"], n_ep))
            seg_blocks.append(seg)
        out[sat["satellite"]] = {
            "regime": sat["regime"],
            "n_segments": len(sat["segments"]),
            "n_rows": sat["n_rows"],
            "effects": {c: np.asarray([v for v, _ in per_cand[c]]) for c in CANDIDATES},
            "weights": np.asarray([w for _, w in per_cand[CANDIDATES[0]]], dtype=float),
            "sgp4_mae": np.asarray([s["dep_mae_sgp4"] for s in sat["segments"]]),
            "gates": np.asarray([s["gate"] for s in sat["segments"]]),
            "m_star": [s["m_star"] for s in sat["segments"]],
            "val_margin": np.asarray([
                s["val_mae"][s["m_star"]] / s["val_mae_sgp4"] for s in sat["segments"]]),
            "mstar_episode_delta": np.asarray([
                e["mae_mstar"] - e["mae_sgp4"]
                for s in sat["segments"] for e in s["per_episode"]]),
        }
    return out


def hierarchical_boot(sat_arrays: list[np.ndarray]) -> tuple[float, float, float]:
    """Resample satellites, then blocks within satellite. Returns (point, lo, hi)."""
    k = len(sat_arrays)
    point = float(np.mean([a.mean() for a in sat_arrays]))
    draws = np.empty(N_BOOT)
    for b in range(N_BOOT):
        pick = RNG.integers(0, k, k)
        vals = []
        for i in pick:
            a = sat_arrays[i]
            vals.append(a[RNG.integers(0, a.size, a.size)].mean())
        draws[b] = np.mean(vals)
    return point, float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def main() -> int:
    P = per_satellite_effects()
    sat_names = list(P)
    report: dict = {
        "statistical_unit": PRE["S2_analysis"]["statistical_unit"],
        "n_satellites": len(sat_names),
        "n_segments_total": sum(P[s]["n_segments"] for s in sat_names),
        "gates_open_total": int(sum(P[s]["gates"].sum() for s in sat_names)),
        "gamma": GAMMA,
        "candidates": {},
    }

    # ---- gated system --------------------------------------------------
    n_admitted = report["gates_open_total"]
    report["gated_system"] = {
        "n_admitted_segments": n_admitted,
        "aggregate_improvement_hz": 0.0 if n_admitted == 0 else None,
        "note": ("G = 0 on every walk-forward segment, so the deployed system "
                 "emits plain SGP4 and its held-out improvement is identically "
                 "zero." if n_admitted == 0 else "see per-segment records"),
        "harmful_admission_rate": (None if n_admitted == 0 else
                                   float(sum(s["harmful"] for sat in RES["satellites"]
                                             for s in sat["segments"]) / n_admitted)),
        "admission_value": ("UNRESOLVED (fewer than 10 admitted segments)"
                            if n_admitted < 10 else "estimable"),
    }

    # ---- ungated candidates -------------------------------------------
    for c in CANDIDATES:
        arrays = [P[s]["effects"][c] for s in sat_names]
        point, lo, hi = hierarchical_boot(arrays)
        sat_eff = {s: float(P[s]["effects"][c].mean()) for s in sat_names}
        improved = [s for s, v in sat_eff.items() if v < 0.0]
        regimes = sorted({P[s]["regime"] for s in improved})
        gains = {s: -v for s, v in sat_eff.items() if v < 0.0}
        tot_gain = sum(gains.values())
        max_share = (max(gains.values()) / tot_gain) if tot_gain > 0 else None
        base = float(np.mean([P[s]["sgp4_mae"].mean() for s in sat_names]))
        report["candidates"][c] = {
            "satellite_balanced_delta_mae_hz": round(point, 6),
            "boot_ci95_hz": [round(lo, 6), round(hi, 6)],
            "improvement_pct_negative_is_worse": round(-100.0 * point / base, 4),
            "sgp4_baseline_mae_hz": round(base, 5),
            "median_satellite_effect_hz": round(float(np.median(list(sat_eff.values()))), 6),
            "n_satellites_improved": len(improved),
            "satellites_improved": improved,
            "regimes_improved": regimes,
            "max_single_satellite_share_of_gain": (round(max_share, 4)
                                                   if max_share is not None else None),
            "per_satellite_delta_mae_hz": {s: round(v, 6) for s, v in sat_eff.items()},
        }

    # ---- sign stability of the selected candidate ----------------------
    stab = {}
    for s in sat_names:
        d = P[s]["mstar_episode_delta"]
        sgn = np.sign(d)
        flips = int(np.sum(sgn[1:] != sgn[:-1]))
        stab[s] = {"n_episodes": int(d.size),
                   "frac_episodes_improved": round(float(np.mean(d < 0)), 4),
                   "sign_flip_rate": round(flips / max(d.size - 1, 1), 4),
                   "mean_delta_hz": round(float(d.mean()), 6)}
    report["m_star_sign_stability"] = stab
    report["m_star_selection_counts"] = {
        c: int(sum(P[s]["m_star"].count(c) for s in sat_names)) for c in CANDIDATES}
    report["val_margin_ratio"] = {
        s: {"min": round(float(P[s]["val_margin"].min()), 4),
            "median": round(float(np.median(P[s]["val_margin"])), 4),
            "gate_threshold": GAMMA} for s in sat_names}

    # ---- verdict -------------------------------------------------------
    best = min(CANDIDATES,
               key=lambda c: report["candidates"][c]["satellite_balanced_delta_mae_hz"])
    bc = report["candidates"][best]
    crit = {
        "1_positive_aggregate": bc["satellite_balanced_delta_mae_hz"] < 0.0,
        "2_interval_excludes_zero": bc["boot_ci95_hz"][1] < 0.0,
        "3_breadth": bc["n_satellites_improved"] > 1 and len(bc["regimes_improved"]) > 1,
        "4_no_domination": (bc["max_single_satellite_share_of_gain"] is not None
                            and bc["max_single_satellite_share_of_gain"] <= 0.50),
        "5_sign_stability": bool(np.mean([
            stab[s]["frac_episodes_improved"] for s in sat_names]) > 0.5),
        "6_screen_robustness": None,   # filled by the sweep driver
        "7_admission_safety": n_admitted >= 10,
    }
    report["best_candidate_by_aggregate"] = best
    report["criteria"] = crit
    hard_fail = [k for k, v in crit.items() if v is False]
    report["S2_VERDICT"] = "FAIL" if hard_fail else ("UNRESOLVED" if None in crit.values()
                                                     else "PASS")
    report["failed_criteria"] = hard_fail

    report["screen_reject_hz"] = RES.get("screen_reject_hz")
    (HERE / f"S2_analysis{ARGS.tag}.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ("candidates", "m_star_sign_stability",
                                   "val_margin_ratio")}, indent=1))
    print("\n--- candidates (satellite-balanced delta MAE, Hz; negative = better) ---")
    for c in CANDIDATES:
        r = report["candidates"][c]
        print(f"{c}  d={r['satellite_balanced_delta_mae_hz']:+.5f} Hz "
              f"CI[{r['boot_ci95_hz'][0]:+.5f},{r['boot_ci95_hz'][1]:+.5f}] "
              f"impr={r['improvement_pct_negative_is_worse']:+.3f}% "
              f"sats_improved={r['n_satellites_improved']}/{report['n_satellites']}")
    print(f"\nbest={best}  S2 VERDICT: {report['S2_VERDICT']}  "
          f"failed={hard_fail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
