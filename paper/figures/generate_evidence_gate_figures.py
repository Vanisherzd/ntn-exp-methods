#!/usr/bin/env python3
"""Generate Fig.2 (real BK negative result) and Fig.3 (gate behavior).

SOFTWARE-ONLY. Every number is copied verbatim from existing repo artifacts;
NOTHING is invented, simulated, or re-fit. Both figures are single-column.

Sources:
  Fig.2  baseline-vs-learned held-out test MAE and relative degradation Delta%:
         docs/review/bk_negative_result_compact.{md,csv}
  Fig.3  gate decision + deployed MAE vs gamma (synthetic stress):
         docs/review/gate_stress_compact.{md,csv} and
         docs/review/evidence_gate_stress_experiment.md (gamma sweep, val n=3000)

NOTE: sample-level BK1/BK2 residual arrays do NOT exist in the artifacts (only
summary statistics), so Fig.2 does NOT plot an empirical CDF; it shows the
reported MAE and Delta% only. reference_is_measured_truth=false; no measured
Doppler, no hardware.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- Fig. 2 ----
# baseline vs learned held-out test MAE [Hz]; Delta% = learned change vs baseline.
stale_bk1 = [8, 24, 48, 72, 96, 168]
mae_base_bk1 = [0.2430, 0.8161, 1.9433, 4.8947, 10.1153, 26.9243]
mae_ml_bk1   = [0.3501, 0.9109, 2.8608, 5.9092, 11.7663, 45.2629]
dpct_bk1     = [-44.1, -11.6, -47.2, -20.7, -16.3, -68.1]
stale_x = [8, 24, 48]
mae_base_x = [0.1877, 0.4969, 2.4092]
mae_ml_x   = [0.3261, 1.8639, 2.8458]
dpct_x     = [-73.7, -275.1, -18.1]

fig, (axa, axb) = plt.subplots(2, 1, figsize=(3.45, 3.7), sharex=True)

# (a) MAE vs staleness
axa.plot(stale_bk1, mae_base_bk1, "o-", color="#1f77b4", lw=1.5, ms=4,
         label="baseline (BK1)")
axa.plot(stale_bk1, mae_ml_bk1, "s--", color="#d62728", lw=1.5, ms=4,
         label="learned (BK1)")
axa.plot(stale_x, mae_base_x, "^:", color="#1f77b4", lw=1.0, ms=4, alpha=0.7,
         label="baseline (BK1$\\to$BK2)")
axa.plot(stale_x, mae_ml_x, "v:", color="#d62728", lw=1.0, ms=4, alpha=0.7,
         label="learned (BK1$\\to$BK2)")
axa.set_yscale("log")
axa.set_ylabel("held-out test MAE [Hz]", fontsize=8)
axa.set_title("(a) learned never beats baseline", fontsize=8)
axa.legend(fontsize=6.0, loc="upper left", ncol=1)
axa.grid(True, which="both", ls=":", alpha=0.4)

# (b) Delta% vs staleness (negative = worse)
axb.axhline(0, color="0.5", lw=0.8)
axb.plot(stale_bk1, dpct_bk1, "s-", color="#d62728", lw=1.5, ms=4, label="BK1")
axb.plot(stale_x, dpct_x, "v:", color="#8c564b", lw=1.3, ms=4, label="BK1$\\to$BK2")
axb.set_xscale("log")
axb.set_xlabel("stale-TLE age [h]", fontsize=8)
axb.set_ylabel("learned $\\Delta$\\% vs baseline", fontsize=8)
axb.set_title("(b) relative degradation (all $<0$)", fontsize=8)
axb.set_xticks(stale_bk1)
axb.set_xticklabels([str(s) for s in stale_bk1], fontsize=7)
axb.legend(fontsize=6.5, loc="lower left")
axb.grid(True, which="both", ls=":", alpha=0.4)

fig.tight_layout()
out2 = os.path.join(HERE, "fig_bk_residual.pdf")
fig.savefig(out2, bbox_inches="tight")
print("wrote", out2)

# ---------------------------------------------------------------- Fig. 3 ----
gamma = [0.90, 0.95, 0.99, 1.00]
gate_fresh    = [0, 0, 0, 0]
gate_moderate = [0, 0, 1, 1]
gate_extreme  = [1, 1, 1, 1]
dep_fresh    = [9.558, 9.558, 9.558, 9.558]
dep_moderate = [63.174, 63.174, 60.176, 60.176]
dep_extreme  = [99.748, 99.748, 99.748, 99.748]
base_extreme = 1859.296

fig3, (axt, axb3) = plt.subplots(2, 1, figsize=(3.45, 3.5), sharex=True)

axt.step(gamma, gate_extreme, where="mid", marker="o", ms=4, lw=1.6,
         color="#2ca02c", label="systematic")
axt.step(gamma, gate_moderate, where="mid", marker="s", ms=4, lw=1.6,
         color="#ff7f0e", label="moderate")
axt.step(gamma, gate_fresh, where="mid", marker="^", ms=4, lw=1.6,
         color="#1f77b4", label="noise-dom. (real-like)")
axt.set_yticks([0, 1]); axt.set_yticklabels(["closed", "OPEN"], fontsize=7)
axt.set_ylim(-0.25, 1.25)
axt.set_ylabel("gate decision", fontsize=8)
axt.set_title("Evidence gate vs threshold $\\gamma$ (synthetic)", fontsize=8)
axt.legend(fontsize=6.3, loc="center left")
axt.grid(True, ls=":", alpha=0.4)

axb3.plot(gamma, dep_extreme, "o-", color="#2ca02c", lw=1.5, ms=4, label="systematic")
axb3.plot(gamma, dep_moderate, "s-", color="#ff7f0e", lw=1.5, ms=4, label="moderate")
axb3.plot(gamma, dep_fresh, "^-", color="#1f77b4", lw=1.5, ms=4, label="noise-dom.")
axb3.axhline(base_extreme, color="#2ca02c", ls="--", lw=0.9, alpha=0.6)
axb3.text(0.90, base_extreme * 0.55, "systematic baseline (gate-closed)",
          fontsize=6, color="#2ca02c")
axb3.set_yscale("log")
axb3.set_xlabel("gate threshold $\\gamma$", fontsize=8)
axb3.set_ylabel("deployed MAE [Hz]", fontsize=8)
axb3.set_xticks(gamma)
axb3.grid(True, which="both", ls=":", alpha=0.4)

fig3.tight_layout()
out3 = os.path.join(HERE, "fig_gate_behavior.pdf")
fig3.savefig(out3, bbox_inches="tight")
print("wrote", out3)
