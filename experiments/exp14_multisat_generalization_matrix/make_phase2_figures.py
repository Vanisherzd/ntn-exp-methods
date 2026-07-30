#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "matplotlib>=3.8"]
# ///
"""Phase-2 reject-threshold sensitivity figures.

Reads reject_sensitivity_results.json only. Software-only, model-derived
inter-TLE residuals; no measured RF truth.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path(__file__).resolve().parent / "phase2_reject_sensitivity"
ORDER = ["none", "150", "500", "1500", "3000"]
C_GRAY, C_PRE, C_BAD = "#666666", "#2F6F3E", "#B23A3A"
NOTE = (
    "Software-only model-derived inter-TLE residuals "
    "(reference_is_measured_truth = false); not measured RF truth."
)


def main() -> int:
    payload = json.loads((OUT / "reject_sensitivity_results.json").read_text())
    rows = [r for r in payload["rows"] if r["status"] == "evaluated"]
    by_sat = defaultdict(list)
    for r in rows:
        by_sat[r["satellite_name"]].append(r)
    sats = sorted(by_sat)
    bands = sorted({r["staleness_h"] for r in rows})

    # Fig 1: held-out improvement vs threshold, one panel per satellite
    ncol, x = 3, np.arange(len(ORDER))
    nrow = int(np.ceil(len(sats) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.3 * ncol, 3.1 * nrow),
                             squeeze=False)
    cmap = plt.get_cmap("viridis")
    for k, sat in enumerate(sats):
        ax = axes[k // ncol][k % ncol]
        idx = {(r["staleness_h"], r["threshold_hz"]): r for r in by_sat[sat]}
        for bi, band in enumerate(bands):
            ys = [idx[(band, t)]["test_improvement_pct"]
                  if (band, t) in idx else np.nan for t in ORDER]
            ax.plot(x, ys, "o-", ms=3.5, lw=1.3,
                    color=cmap(bi / max(1, len(bands) - 1)), label=f"{band} h")
        ax.axhline(0.0, color=C_BAD, lw=1.1, ls="--")
        ax.axvline(ORDER.index("1500"), color=C_PRE, lw=1.1, ls=":")
        ax.set_xticks(x)
        ax.set_xticklabels(ORDER, fontsize=7)
        ax.set_xlabel("reject threshold |r| [Hz]", fontsize=8)
        ax.set_title(sat, fontsize=9)
        ax.grid(True, ls=":", alpha=0.3)
        lo, hi = ax.get_ylim()
        if hi - lo > 200:                       # tame catastrophic outliers
            ax.set_ylim(max(lo, -60), min(hi, 20))
            ax.text(0.02, 0.03, "y-axis clipped", transform=ax.transAxes,
                    fontsize=5.5, color=C_GRAY)
    for k in range(len(sats), nrow * ncol):
        axes[k // ncol][k % ncol].axis("off")
    axes[0][0].set_ylabel("held-out improvement [%]\n(above 0 = learned better)",
                          fontsize=8)
    axes[0][0].legend(fontsize=5.5, frameon=False, ncol=2)
    fig.suptitle(
        "Phase-2 reject-threshold sensitivity: held-out improvement vs screening "
        "threshold\ndotted green line = preregistered 1500 Hz; every gate stayed "
        "closed except one cell", fontsize=10)
    fig.text(0.5, -0.01, NOTE, ha="center", fontsize=6, color=C_GRAY)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_reject_threshold_sensitivity.{ext}",
                    bbox_inches="tight", dpi=200 if ext == "png" else None)
    plt.close(fig)

    # Fig 2: the five Iridium priority rows
    pri = payload["priority_classification"]
    fig, axes = plt.subplots(1, len(pri), figsize=(3.1 * len(pri), 3.4),
                             squeeze=False)
    for k, cell in enumerate(pri):
        ax = axes[0][k]
        ts = [t["threshold_hz"] for t in cell["per_threshold"]]
        xs = [ORDER.index(t) for t in ts]
        val = [t["val_improvement_pct"] for t in cell["per_threshold"]]
        test = [t["test_improvement_pct"] for t in cell["per_threshold"]]
        ax.plot(xs, val, "s--", color="#1F4E79", ms=4, lw=1.3, label="validation")
        ax.plot(xs, test, "o-", color="#C46A1A", ms=4.5, lw=1.6, label="held-out")
        ax.axhline(0.0, color=C_BAD, lw=1.1, ls="--")
        ax.axhline(5.0, color=C_PRE, lw=1.1, ls="-.")
        ax.axvline(ORDER.index("1500"), color=C_PRE, lw=1.0, ls=":")
        for t, xi in zip(cell["per_threshold"], xs):
            if t["gate_decision"] == "open":
                ax.axvspan(xi - 0.3, xi + 0.3, color=C_PRE, alpha=0.22)
        ax.set_xticks(range(len(ORDER)))
        ax.set_xticklabels(ORDER, fontsize=7)
        ax.set_xlabel("reject threshold [Hz]", fontsize=8)
        ax.set_title(f"{cell['satellite']} @ {cell['staleness_h']} h\n"
                     f"{cell['verdict']}", fontsize=7.5)
        ax.grid(True, ls=":", alpha=0.3)
    axes[0][0].set_ylabel("improvement [%]", fontsize=8)
    axes[0][0].legend(fontsize=6, frameon=False)
    fig.suptitle(
        "Iridium priority cells: is the sub-margin signal robust to screening?\n"
        "dash-dot green = 5 % deployment margin; shaded = gate open", fontsize=9)
    fig.text(0.5, -0.03, NOTE, ha="center", fontsize=6, color=C_GRAY)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_iridium_screening_sensitivity.{ext}",
                    bbox_inches="tight", dpi=200 if ext == "png" else None)
    plt.close(fig)
    print("wrote 4 figure files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
