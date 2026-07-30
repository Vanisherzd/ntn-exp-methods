#!/usr/bin/env python3
"""
exp7 — Timing-offset sensitivity analysis (software-only proxy)
==============================================================
Two sweeps over the analytic TX-window guard-coverage proxy:

  (A) residual timing-offset sweep : sweep timing 1-sigma sigma_t and report
      TX-window hit/miss rate, guard overhead, energy per successful burst,
      under the adaptive (k-sigma) guard policy.

  (B) TLE-age sweep : map TLE staleness (8-168 h) to the open-loop SGP4
      along-track timing 1-sigma, then report the same metrics. A PGRL
      (gate-open synthetic) clamp curve is overlaid for context.

SCOPE: software-only, model-derived. The "hit/miss" is an analytic guard-coverage
proxy, not a measured LR-FHSS packet outcome. See experiments/paper1_proxy_model.py.

Outputs:
  experiments/exp7_timing_sensitivity/results.json
  experiments/exp7_timing_sensitivity/figures/fig_timing_sensitivity.pdf
  experiments/exp7_timing_sensitivity/figures/fig_timing_sensitivity.png
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from experiments.paper1_proxy_model import (
    SIGMA_T_S, PASS_DURATION_S, BASE_GUARD_S, K_SIGMA, F_CARRIER_HZ,
    BK_STALENESS_H, ALONG_TRACK_KM_PER_DAY, V_ORBITAL_KMS,
    evaluate_window, sgp4_timing_sigma_from_age,
)

HERE = os.path.dirname(__file__)
FIGDIR = os.path.join(HERE, "figures")


def sweep_residual_offset():
    """(A) sweep timing sigma_t from 5 ms to 2 s under the adaptive guard."""
    sigmas = np.geomspace(0.005, 2.0, 40)
    rows = []
    for s in sigmas:
        o = evaluate_window(float(s), adaptive=True)
        rows.append({
            "sigma_t_s": float(s),
            "guard_s": o.guard_s,
            "miss_rate": o.miss_rate,
            "hit_rate": o.hit_rate,
            "guard_overhead": o.guard_overhead,
            "energy_per_success_j": o.energy_per_success_j,
        })
    return rows


def named_configs():
    """Evaluate the named control configs at their calibrated timing sigma."""
    out = {}
    for name, s in SIGMA_T_S.items():
        o = evaluate_window(float(s), adaptive=True)
        out[name] = {
            "sigma_t_s": o.sigma_t_s,
            "guard_s": o.guard_s,
            "miss_rate": o.miss_rate,
            "hit_rate": o.hit_rate,
            "guard_overhead": o.guard_overhead,
            "energy_per_success_j": o.energy_per_success_j,
        }
    return out


def sweep_tle_age():
    """(B) TLE-age sweep: open-loop SGP4 timing sigma vs staleness + PGRL clamp."""
    ages_h = [8, 24, 48, 72, 96, 120, 168]
    # PGRL gate-open synthetic clamp: caps residual timing sigma at the calibrated
    # PGRL-uncertainty floor when learnable structure exists (exp2). Honestly
    # labelled: on real BLACK KITE the gate CLOSES and PGRL == SGP4.
    pgrl_floor = SIGMA_T_S["pgrl_uncert"]
    rows = []
    for a in ages_h:
        s_sgp4 = sgp4_timing_sigma_from_age(a)
        s_pgrl = min(s_sgp4, pgrl_floor)
        o_sgp4 = evaluate_window(s_sgp4, adaptive=True)
        o_pgrl = evaluate_window(s_pgrl, adaptive=True)
        rows.append({
            "tle_age_h": a,
            "sgp4": {
                "sigma_t_s": s_sgp4, "guard_s": o_sgp4.guard_s,
                "miss_rate": o_sgp4.miss_rate, "hit_rate": o_sgp4.hit_rate,
                "guard_overhead": o_sgp4.guard_overhead,
                "energy_per_success_j": o_sgp4.energy_per_success_j,
            },
            "pgrl_gate_open": {
                "sigma_t_s": s_pgrl, "guard_s": o_pgrl.guard_s,
                "miss_rate": o_pgrl.miss_rate, "hit_rate": o_pgrl.hit_rate,
                "guard_overhead": o_pgrl.guard_overhead,
                "energy_per_success_j": o_pgrl.energy_per_success_j,
            },
        })
    return rows


def make_figure(sweep_a, configs, sweep_b):
    fig, axes = plt.subplots(2, 2, figsize=(9.5, 7.0))

    sg = np.array([r["sigma_t_s"] for r in sweep_a])
    miss = np.array([r["miss_rate"] for r in sweep_a])
    ovh = np.array([r["guard_overhead"] for r in sweep_a]) * 100
    eps = np.array([r["energy_per_success_j"] for r in sweep_a])

    # (a) miss rate vs sigma_t
    ax = axes[0, 0]
    ax.semilogx(sg, miss * 100, "-", color="C3", lw=2)
    for name, c in configs.items():
        ax.plot(c["sigma_t_s"], c["miss_rate"] * 100, "o", ms=6, label=name)
    ax.set_xlabel(r"residual timing $\sigma_t$ [s]")
    ax.set_ylabel("TX-window miss rate [%]")
    ax.set_title("(a) Miss rate vs timing offset (adaptive guard)")
    ax.legend(fontsize=7, loc="upper left")
    ax.grid(True, alpha=0.3)

    # (b) guard overhead vs sigma_t
    ax = axes[0, 1]
    ax.semilogx(sg, ovh, "-", color="C0", lw=2)
    ax.set_xlabel(r"residual timing $\sigma_t$ [s]")
    ax.set_ylabel("guard overhead [% of pass]")
    ax.set_title("(b) Guard overhead vs timing offset")
    ax.grid(True, alpha=0.3)

    # (c) energy per successful burst vs sigma_t
    ax = axes[1, 0]
    ax.loglog(sg, eps * 1e3, "-", color="C2", lw=2)
    ax.set_xlabel(r"residual timing $\sigma_t$ [s]")
    ax.set_ylabel("energy / successful burst [mJ]")
    ax.set_title("(c) Energy per successful burst")
    ax.grid(True, alpha=0.3, which="both")

    # (d) TLE-age sweep: miss rate vs staleness
    ax = axes[1, 1]
    ages = [r["tle_age_h"] for r in sweep_b]
    miss_sgp4 = [r["sgp4"]["miss_rate"] * 100 for r in sweep_b]
    miss_pgrl = [r["pgrl_gate_open"]["miss_rate"] * 100 for r in sweep_b]
    ax.plot(ages, miss_sgp4, "s-", color="C1", label="SGP4 open-loop")
    ax.plot(ages, miss_pgrl, "^--", color="C4", label="PGRL (gate-open synth.)")
    ax.set_xlabel("TLE age [h]")
    ax.set_ylabel("TX-window miss rate [%]")
    ax.set_title("(d) Miss rate vs TLE staleness")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    fig.suptitle("exp7 — Timing-offset sensitivity (software-only guard-coverage proxy)",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    os.makedirs(FIGDIR, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIGDIR, f"fig_timing_sensitivity.{ext}"), dpi=150)
    plt.close(fig)


def main():
    sweep_a = sweep_residual_offset()
    configs = named_configs()
    sweep_b = sweep_tle_age()
    make_figure(sweep_a, configs, sweep_b)

    results = {
        "_reproducibility": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "validation_type": "simulation_proxy",
            "script": "experiments/exp7_timing_sensitivity/run_timing_sensitivity.py",
            "model": "experiments/paper1_proxy_model.py",
            "carrier_hz": F_CARRIER_HZ,
            "pass_duration_s": PASS_DURATION_S,
            "base_guard_s": BASE_GUARD_S,
            "k_sigma": K_SIGMA,
            "along_track_km_per_day": ALONG_TRACK_KM_PER_DAY,
            "v_orbital_kms": V_ORBITAL_KMS,
            "limitations": (
                "Software-only guard-coverage proxy. Hit/miss is analytic "
                "P(|offset|>guard), NOT a measured LR-FHSS packet outcome. "
                "PGRL clamp is the gate-open synthetic regime; on real BLACK KITE "
                "the gate closes and PGRL does not beat SGP4."
            ),
        },
        "experiment": "exp7_timing_sensitivity",
        "residual_offset_sweep": sweep_a,
        "named_configs": configs,
        "tle_age_sweep": sweep_b,
    }
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    # ── console summary ────────────────────────────────────────────────────────
    print("=" * 72)
    print("exp7 — Timing-offset sensitivity (software-only proxy)")
    print("=" * 72)
    print(f"\nNamed control configs (adaptive guard, base={BASE_GUARD_S}s, k={K_SIGMA}):")
    print(f"  {'config':<14}{'sigma_t':>9}{'guard':>9}{'miss%':>9}{'hit%':>8}"
          f"{'ovh%':>8}{'E/succ[mJ]':>12}")
    for n, c in configs.items():
        print(f"  {n:<14}{c['sigma_t_s']:>9.3f}{c['guard_s']:>9.3f}"
              f"{c['miss_rate']*100:>9.3f}{c['hit_rate']*100:>8.2f}"
              f"{c['guard_overhead']*100:>8.2f}{c['energy_per_success_j']*1e3:>12.3f}")
    print(f"\nTLE-age sweep (open-loop SGP4 vs PGRL gate-open synthetic):")
    print(f"  {'age_h':>6}{'sgp4_sigma':>12}{'sgp4_miss%':>12}{'pgrl_miss%':>12}")
    for r in sweep_b:
        print(f"  {r['tle_age_h']:>6}{r['sgp4']['sigma_t_s']:>12.3f}"
              f"{r['sgp4']['miss_rate']*100:>12.3f}"
              f"{r['pgrl_gate_open']['miss_rate']*100:>12.3f}")
    print(f"\nWrote results.json + figures/fig_timing_sensitivity.{{pdf,png}}")


if __name__ == "__main__":
    main()
