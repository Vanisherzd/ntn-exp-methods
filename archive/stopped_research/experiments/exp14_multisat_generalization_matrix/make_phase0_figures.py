#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "matplotlib>=3.8"]
# ///
"""Phase-0 BLACK KITE figures. Reads phase0_results.json; renders nothing else.

Software-only, model-derived inter-TLE residuals; no measured RF truth.
"""
import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path("experiments/exp14_multisat_generalization_matrix/phase0_black_kite")
d = json.loads((OUT/"phase0_results.json").read_text())
rows = [r for r in d["rows"] if r["status"] == "evaluated"]
deltas = d["per_pair_delta_mae_hz"]
cells = ["NORAD66741->NORAD66741","NORAD68474->NORAD68474",
         "NORAD66741->NORAD68474","NORAD68474->NORAD66741"]
titles = {
    cells[0]: "BK1 -> BK1 (target-specific)",
    cells[1]: "BK2 -> BK2 (target-specific)",
    cells[2]: "BK1 -> BK2 (transfer)",
    cells[3]: "BK2 -> BK1 (transfer)",
}
bands = [8,24,48,72,96,168]
C_PHYS, C_ML, C_GRAY = "#1F4E79", "#C46A1A", "#666666"
NOTE = ("Software-only model-derived inter-TLE residuals "
        "(reference_is_measured_truth = false); not measured RF truth.")

# Fig 1: SGP4 vs learned test MAE
fig, axes = plt.subplots(1, 4, figsize=(14.5, 3.4), sharex=True)
for ax, cell in zip(axes, cells):
    rs = {r["staleness_h"]: r for r in rows if r["cell"] == cell}
    x = np.arange(len(bands))
    base = [rs[b]["test_sgp4_mae_hz"] for b in bands]
    ml = [rs[b]["test_learned_mae_hz"] for b in bands]
    ax.plot(x, base, "o-", color=C_PHYS, lw=1.8, ms=5, label="SGP4 baseline")
    ax.plot(x, ml, "s--", color=C_ML, lw=1.6, ms=4, label="learned (gated off)")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(bands, fontsize=7)
    ax.set_xlabel("staleness [h]", fontsize=8)
    ax.set_title(titles[cell] + "\nall gates CLOSED", fontsize=8)
    ax.grid(True, ls=":", alpha=0.35)
axes[0].set_ylabel("pair-level test MAE [Hz] (log)", fontsize=8)
axes[0].legend(fontsize=6, frameon=False)
fig.suptitle("Phase-0 BLACK KITE under the unified protocol: learned never "
             "beats SGP4 enough to open the gate", fontsize=10)
fig.text(0.5, -0.03, NOTE, ha="center", fontsize=6, color=C_GRAY)
fig.tight_layout(rect=(0,0,1,0.90))
for ext in ("pdf","png"):
    fig.savefig(OUT/f"fig_phase0_bk_mae.{ext}", bbox_inches="tight",
                dpi=200 if ext=="png" else None)
plt.close(fig)

# Fig 2: per-pair delta MAE distributions
fig, axes = plt.subplots(1, 4, figsize=(14.5, 3.6), sharey=False)
for ax, cell in zip(axes, cells):
    data = [np.array(deltas.get(f"{cell}|{b}", [])) for b in bands]
    bp = ax.boxplot(data, showfliers=False, widths=0.6, patch_artist=True,
                    medianprops=dict(color="black", lw=1.2))
    for patch, arr in zip(bp["boxes"], data):
        med = float(np.median(arr)) if arr.size else 0.0
        patch.set_facecolor("#F9EFE6" if med > 0 else "#EEF4FA")
        patch.set_edgecolor(C_ML if med > 0 else C_PHYS)
    ax.axhline(0.0, color="#B23A3A", lw=1.2, ls="--")
    ax.set_xticklabels(bands, fontsize=7)
    ax.set_xlabel("staleness [h]", fontsize=8)
    ax.set_title(titles[cell], fontsize=8)
    ax.grid(True, axis="y", ls=":", alpha=0.35)
axes[0].set_ylabel("per-pair ΔMAE = learned − SGP4 [Hz]", fontsize=8)
fig.suptitle("Phase-0 per-pair ΔMAE distributions (one observation per accepted "
             "TLE pair). Above the dashed line = learned worse.", fontsize=10)
fig.text(0.5, -0.03, NOTE, ha="center", fontsize=6, color=C_GRAY)
fig.tight_layout(rect=(0,0,1,0.90))
for ext in ("pdf","png"):
    fig.savefig(OUT/f"fig_phase0_pair_delta.{ext}", bbox_inches="tight",
                dpi=200 if ext=="png" else None)
plt.close(fig)
print("wrote 4 figure files")
