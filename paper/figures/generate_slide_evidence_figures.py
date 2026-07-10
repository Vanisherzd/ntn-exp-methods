#!/usr/bin/env python3
"""Generate talk-optimized evidence figures for the slide deck.

This script preserves the same underlying values as the paper figures, but
uses wider layouts and larger typography for presentation readability.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent


# Real BLACK KITE negative result.
stale_bk1 = [8, 24, 48, 72, 96, 168]
mae_base_bk1 = [0.2430, 0.8161, 1.9433, 4.8947, 10.1153, 26.9243]
mae_ml_bk1 = [0.3501, 0.9109, 2.8608, 5.9092, 11.7663, 45.2629]
dpct_bk1 = [44.1, 11.6, 47.2, 20.7, 16.3, 68.1]
stale_x = [8, 24, 48]
mae_base_x = [0.1877, 0.4969, 2.4092]
mae_ml_x = [0.3261, 1.8639, 2.8458]
dpct_x = [73.7, 275.1, 18.1]

fig, (axa, axb) = plt.subplots(
    2, 1, figsize=(5.75, 4.65), sharex=True, constrained_layout=True
)

axa.plot(
    stale_bk1,
    mae_base_bk1,
    "o-",
    color="#1f4e79",
    lw=2.3,
    ms=5.6,
    label="baseline (BK1)",
)
axa.plot(
    stale_bk1,
    mae_ml_bk1,
    "s--",
    color="#b23a3a",
    lw=2.3,
    ms=5.6,
    label="learned (BK1)",
)
axa.plot(
    stale_x,
    mae_base_x,
    "^:",
    color="#3d7fb3",
    lw=1.8,
    ms=5.2,
    alpha=0.9,
    label="baseline (BK1→BK2)",
)
axa.plot(
    stale_x,
    mae_ml_x,
    "v:",
    color="#ef6b62",
    lw=1.8,
    ms=5.2,
    alpha=0.9,
    label="learned (BK1→BK2)",
)
axa.set_yscale("log")
axa.set_ylabel("held-out test MAE [Hz]", fontsize=11)
axa.set_title("(a) learned residual never beats baseline", fontsize=11, pad=6)
axa.tick_params(labelsize=10)
axa.legend(fontsize=8.8, loc="upper left", frameon=True)
axa.grid(True, which="both", ls=":", alpha=0.35)

axb.axhline(0, color="0.45", lw=1.1)
axb.plot(stale_bk1, dpct_bk1, "s-", color="#d62728", lw=2.2, ms=5.4, label="BK1")
axb.plot(
    stale_x,
    dpct_x,
    "v:",
    color="#8c564b",
    lw=2.0,
    ms=5.2,
    label="BK1→BK2",
)
axb.set_xscale("log")
axb.set_xlabel("stale-TLE age [h]", fontsize=11)
axb.set_ylabel("degradation vs baseline [%]", fontsize=11)
axb.set_title("(b) degradation remains positive across cases", fontsize=11, pad=6)
axb.set_xticks(stale_bk1)
axb.set_xticklabels([str(s) for s in stale_bk1], fontsize=10)
axb.tick_params(labelsize=10)
axb.legend(fontsize=8.8, loc="lower left", frameon=True)
axb.grid(True, which="both", ls=":", alpha=0.35)

out_bk = HERE / "fig_bk_residual_talk.pdf"
fig.savefig(out_bk, bbox_inches="tight")
print(f"wrote {out_bk}")


# Synthetic gate behavior.
gamma = [0.90, 0.95, 0.99, 1.00]
gate_fresh = [0, 0, 0, 0]
gate_moderate = [0, 0, 1, 1]
gate_extreme = [1, 1, 1, 1]
dep_fresh = [9.558, 9.558, 9.558, 9.558]
dep_moderate = [63.174, 63.174, 60.176, 60.176]
dep_extreme = [99.748, 99.748, 99.748, 99.748]
base_extreme = 1859.296

fig2, (axt, axb2) = plt.subplots(
    2, 1, figsize=(5.45, 4.45), sharex=True, constrained_layout=True
)

axt.step(
    gamma,
    gate_extreme,
    where="mid",
    marker="o",
    ms=5.4,
    lw=2.2,
    color="#2e7d32",
    label="strong systematic",
)
axt.step(
    gamma,
    gate_moderate,
    where="mid",
    marker="s",
    ms=5.4,
    lw=2.2,
    color="#c46a1a",
    label="weak / moderate",
)
axt.step(
    gamma,
    gate_fresh,
    where="mid",
    marker="^",
    ms=5.4,
    lw=2.2,
    color="#1f4e79",
    label="noise-dominated",
)
axt.set_yticks([0, 1])
axt.set_yticklabels(["closed", "open"], fontsize=10)
axt.set_ylim(-0.25, 1.25)
axt.set_ylabel("gate decision", fontsize=11)
axt.set_title("Evidence gate vs threshold γ (synthetic)", fontsize=11, pad=6)
axt.tick_params(labelsize=10)
axt.legend(fontsize=8.8, loc="center left", frameon=True)
axt.grid(True, ls=":", alpha=0.35)

axb2.plot(
    gamma,
    dep_extreme,
    "o-",
    color="#2e7d32",
    lw=2.2,
    ms=5.4,
    label="strong systematic",
)
axb2.plot(
    gamma,
    dep_moderate,
    "s-",
    color="#c46a1a",
    lw=2.2,
    ms=5.4,
    label="weak / moderate",
)
axb2.plot(
    gamma,
    dep_fresh,
    "^-",
    color="#1f4e79",
    lw=2.2,
    ms=5.4,
    label="noise-dominated",
)
axb2.axhline(base_extreme, color="#2e7d32", ls="--", lw=1.2, alpha=0.7)
axb2.text(
    0.901,
    base_extreme * 0.58,
    "systematic baseline (gate closed)",
    fontsize=8.0,
    color="#2e7d32",
)
axb2.set_yscale("log")
axb2.set_xlabel("gate threshold γ", fontsize=11)
axb2.set_ylabel("deployed MAE [Hz]", fontsize=11)
axb2.set_xticks(gamma)
axb2.tick_params(labelsize=10)
axb2.grid(True, which="both", ls=":", alpha=0.35)

out_gate = HERE / "fig_gate_behavior_talk.pdf"
fig2.savefig(out_gate, bbox_inches="tight")
print(f"wrote {out_gate}")
