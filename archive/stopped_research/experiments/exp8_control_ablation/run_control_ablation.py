#!/usr/bin/env python3
"""
exp8 — Timing / frequency / PGRL control ablation (software-only proxy)
======================================================================
Five control configurations, each toggling which control dimensions are active:

  1. no_control        : fixed base guard, no Doppler pre-comp, SGP4 predictor
  2. timing_only       : adaptive (k-sigma) guard, no Doppler pre-comp, SGP4
  3. frequency_only    : fixed base guard, SGP4 Doppler pre-comp
  4. timing_frequency  : adaptive guard + SGP4 Doppler pre-comp
  5. timing_freq_pgrl  : adaptive guard + Doppler pre-comp, PGRL predictor
                         (tighter timing sigma + tighter Doppler residual)

Metrics per config:
  - timing-miss rate     : P(|timing offset| > guard)              [proxy]
  - frequency-miss rate  : P(|residual Doppler| > F_tol)           [proxy]
  - success / hit rate   : (1-timing_miss)*(1-freq_miss)           [independent]
  - guard overhead       : guard / pass_duration
  - energy per successful burst

SCOPE: software-only, model-derived. Miss/success are analytic coverage proxies,
NOT measured LR-FHSS packet outcomes. The PGRL row is the gate-open synthetic
regime; on real BLACK KITE the gate closes and PGRL does not beat SGP4.

Outputs:
  experiments/exp8_control_ablation/results.json
  experiments/exp8_control_ablation/figures/fig_control_ablation.{pdf,png}
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
    SIGMA_T_S, SIGMA_F_HZ, BASE_GUARD_S, K_SIGMA, F_TOL_HZ, PASS_DURATION_S,
    evaluate_window, freq_miss_probability,
)

HERE = os.path.dirname(__file__)
FIGDIR = os.path.join(HERE, "figures")

# config -> (timing-adaptive?, timing sigma key, Doppler-comp key)
CONFIGS = {
    "no_control":       (False, "sgp4_only",   "no_comp"),
    "timing_only":      (True,  "sgp4_only",   "no_comp"),
    "frequency_only":   (False, "sgp4_only",   "sgp4_comp"),
    "timing_frequency": (True,  "sgp4_only",   "sgp4_comp"),
    "timing_freq_pgrl": (True,  "pgrl_uncert", "pgrl_comp"),
}


def evaluate_config(adaptive, sigma_t_key, sigma_f_key):
    sigma_t = SIGMA_T_S[sigma_t_key]
    sigma_f = SIGMA_F_HZ[sigma_f_key]
    w = evaluate_window(sigma_t, adaptive=adaptive, fixed_guard_s=BASE_GUARD_S)
    timing_miss = w.miss_rate
    freq_miss = freq_miss_probability(sigma_f, F_TOL_HZ)
    success = (1.0 - timing_miss) * (1.0 - freq_miss)
    # energy charged per attempted burst, then per *joint* success
    e_per_burst = w.energy_per_burst_j
    e_per_success = e_per_burst / success if success > 1e-9 else float("inf")
    return {
        "sigma_t_s": sigma_t,
        "sigma_f_hz": sigma_f,
        "guard_s": w.guard_s,
        "timing_miss": timing_miss,
        "freq_miss": freq_miss,
        "miss_rate": 1.0 - success,
        "success_rate": success,
        "guard_overhead": w.guard_overhead,
        "energy_per_burst_j": e_per_burst,
        "energy_per_success_j": e_per_success,
    }


def make_figure(results):
    names = list(results.keys())
    x = np.arange(len(names))
    miss = [results[n]["miss_rate"] * 100 for n in names]
    succ = [results[n]["success_rate"] * 100 for n in names]
    ovh = [results[n]["guard_overhead"] * 100 for n in names]
    eps = [min(results[n]["energy_per_success_j"] * 1e3, 1e4) for n in names]

    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    labels = [n.replace("_", "\n") for n in names]

    ax = axes[0, 0]
    ax.bar(x, succ, color="C2")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("success / hit rate [%]")
    ax.set_title("(a) Joint success rate")
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[0, 1]
    ax.bar(x, miss, color="C3")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("miss rate [%]")
    ax.set_title("(b) Combined miss rate")
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[1, 0]
    ax.bar(x, ovh, color="C0")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("guard overhead [% of pass]")
    ax.set_title("(c) Guard overhead")
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[1, 1]
    ax.bar(x, eps, color="C1", log=True)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("energy / successful burst [mJ]")
    ax.set_title("(d) Energy per successful burst (log, capped 10$^4$)")
    ax.grid(True, axis="y", alpha=0.3, which="both")

    fig.suptitle("exp8 — Timing / frequency / PGRL control ablation (software-only proxy)",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    os.makedirs(FIGDIR, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIGDIR, f"fig_control_ablation.{ext}"), dpi=150)
    plt.close(fig)


def main():
    results = {n: evaluate_config(*cfg) for n, cfg in CONFIGS.items()}
    make_figure(results)

    out = {
        "_reproducibility": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "validation_type": "simulation_proxy",
            "script": "experiments/exp8_control_ablation/run_control_ablation.py",
            "model": "experiments/paper1_proxy_model.py",
            "f_tol_hz": F_TOL_HZ,
            "base_guard_s": BASE_GUARD_S,
            "k_sigma": K_SIGMA,
            "pass_duration_s": PASS_DURATION_S,
            "limitations": (
                "Software-only coverage proxy. timing/freq miss are analytic "
                "Gaussian-coverage probabilities, NOT measured LR-FHSS packet "
                "outcomes. timing_freq_pgrl is the gate-open synthetic regime; on "
                "real BLACK KITE the gate closes and PGRL does not beat SGP4."
            ),
        },
        "experiment": "exp8_control_ablation",
        "config_definitions": {
            n: {"timing_adaptive": c[0], "sigma_t_key": c[1], "sigma_f_key": c[2]}
            for n, c in CONFIGS.items()
        },
        "results": results,
    }
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(out, f, indent=2)

    print("=" * 90)
    print("exp8 — Timing / frequency / PGRL control ablation (software-only proxy)")
    print("=" * 90)
    hdr = (f"  {'config':<18}{'guard':>8}{'t-miss%':>9}{'f-miss%':>9}"
           f"{'miss%':>8}{'succ%':>8}{'ovh%':>7}{'E/succ[mJ]':>13}")
    print(hdr)
    for n, r in results.items():
        eps = r["energy_per_success_j"] * 1e3
        eps_s = f"{eps:>13.2f}" if np.isfinite(eps) else f"{'inf':>13}"
        print(f"  {n:<18}{r['guard_s']:>8.3f}{r['timing_miss']*100:>9.3f}"
              f"{r['freq_miss']*100:>9.2f}{r['miss_rate']*100:>8.2f}"
              f"{r['success_rate']*100:>8.2f}{r['guard_overhead']*100:>7.2f}{eps_s}")
    print("\nWrote results.json + figures/fig_control_ablation.{pdf,png}")


if __name__ == "__main__":
    main()
