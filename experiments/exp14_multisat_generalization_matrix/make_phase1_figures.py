#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "matplotlib>=3.8"]
# ///
"""Phase-1 target-specific figures. Reads target_specific_results.json only.

Software-only, model-derived inter-TLE residuals; no measured RF truth.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path(__file__).resolve().parent / "phase1_target_specific"
C_PHYS, C_ML, C_GRAY = "#1F4E79", "#C46A1A", "#666666"
C_OPEN, C_CLOSED = "#2F6F3E", "#EEF4FA"
NOTE = (
    "Software-only model-derived inter-TLE residuals "
    "(reference_is_measured_truth = false); not measured RF truth."
)


def main() -> int:
    payload = json.loads((OUT / "target_specific_results.json").read_text())
    rows = [r for r in payload["rows"] if r["status"] == "evaluated"]
    names = sorted({r["target_name"] for r in rows})
    bands = sorted({r["staleness_h"] for r in rows})
    idx = {(r["target_name"], r["staleness_h"]): r for r in rows}

    # Fig 1: SGP4 vs learned held-out MAE per satellite
    ncol = min(4, len(names))
    nrow = int(np.ceil(len(names) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.6 * ncol, 3.0 * nrow),
                             squeeze=False)
    for k, name in enumerate(names):
        ax = axes[k // ncol][k % ncol]
        x = np.arange(len(bands))
        base = [idx[(name, b)]["test_sgp4_mae_hz"] for b in bands]
        ml = [idx[(name, b)]["test_learned_mae_hz"] for b in bands]
        gates = [idx[(name, b)]["gate_decision"] for b in bands]
        ax.plot(x, base, "o-", color=C_PHYS, lw=1.8, ms=5, label="SGP4")
        ax.plot(x, ml, "s--", color=C_ML, lw=1.5, ms=4, label="learned")
        for xi, g in zip(x, gates):
            if g == "open":
                ax.axvspan(xi - 0.4, xi + 0.4, color=C_OPEN, alpha=0.18)
        ax.set_yscale("log")
        ax.set_xticks(x)
        ax.set_xticklabels(bands, fontsize=7)
        ax.set_title(f"{name}\n{sum(g == 'open' for g in gates)}/6 gates open",
                     fontsize=8)
        ax.set_xlabel("staleness [h]", fontsize=8)
        ax.grid(True, ls=":", alpha=0.35)
    for k in range(len(names), nrow * ncol):
        axes[k // ncol][k % ncol].axis("off")
    axes[0][0].set_ylabel("held-out pair-level MAE [Hz] (log)", fontsize=8)
    axes[0][0].legend(fontsize=6, frameon=False)
    fig.suptitle(
        "Phase-1 target-specific (A->A): held-out MAE, SGP4 vs validation-"
        "selected learned branch", fontsize=10
    )
    fig.text(0.5, -0.01, NOTE, ha="center", fontsize=6, color=C_GRAY)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_target_specific_mae.{ext}", bbox_inches="tight",
                    dpi=200 if ext == "png" else None)
    plt.close(fig)

    # Fig 2: gate map, satellite x band, annotated with held-out degradation
    grid = np.full((len(names), len(bands)), np.nan)
    labels = [[""] * len(bands) for _ in names]
    for i, name in enumerate(names):
        for j, band in enumerate(bands):
            r = idx[(name, band)]
            grid[i, j] = 1.0 if r["gate_decision"] == "open" else 0.0
            deg = r["test_degradation_pct"]
            mark = "O" if r["gate_decision"] == "open" else "C"
            labels[i][j] = f"{mark}\n{deg:+.1f}%"
    fig, ax = plt.subplots(figsize=(1.6 + 1.15 * len(bands), 1.4 + 0.62 * len(names)))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "gate", [C_CLOSED, C_OPEN]
    )
    ax.imshow(grid, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")
    ax.set_xticks(range(len(bands)))
    ax.set_xticklabels([f"{b} h" for b in bands], fontsize=8)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8)
    for i in range(len(names)):
        for j in range(len(bands)):
            ax.text(j, i, labels[i][j], ha="center", va="center", fontsize=6,
                    color="black")
    ax.set_title(
        "Phase-1 Evidence Gate map (preregistered MAE gate, decided on target "
        "validation)\nO = open, C = closed; annotation is held-out degradation "
        "(positive = learned worse)", fontsize=8
    )
    fig.text(0.5, -0.04, NOTE, ha="center", fontsize=6, color=C_GRAY)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_target_specific_gate_map.{ext}",
                    bbox_inches="tight", dpi=200 if ext == "png" else None)
    plt.close(fig)
    print("wrote 4 figure files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
