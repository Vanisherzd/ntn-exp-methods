#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "matplotlib>=3.8"]
# ///
"""Paper 1+ generalization figures (Phases 5-7).

Reads `results.json` produced by `run_multisat_generalization_matrix.py` and
renders the campaign figures. Emits NOTHING unless the run contains at least
`min_satellites_for_generalization_claim` satellites, so a dry run cannot
accidentally produce a figure that looks like multi-satellite evidence.

All values are model-derived inter-TLE residuals; no measured RF truth.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent

C_PHYS = "#1F4E79"
C_ML = "#C46A1A"
C_GATE = "#2E7D32"
C_BAD = "#B23A3A"
C_GRAY = "#666666"

SCOPE_NOTE = (
    "Software-only, model-derived inter-TLE residuals "
    "(reference_is_measured_truth = false); not measured RF truth."
)


def _save(fig, out_dir: Path, stem: str) -> list[Path]:
    written = []
    for ext in ("pdf", "png"):
        path = out_dir / f"{stem}.{ext}"
        fig.savefig(path, bbox_inches="tight", dpi=200 if ext == "png" else None)
        written.append(path)
    plt.close(fig)
    return written


def _sat_order(rows: list[dict[str, Any]]) -> list[str]:
    keys: list[str] = []
    for row in rows:
        for key in (row["train_source"], row["deploy_target"]):
            if key not in keys:
                keys.append(key)
    return sorted(keys)


def _cell_value(
    rows: list[dict[str, Any]], src: str, tgt: str, field: str, staleness=None
) -> float:
    vals = [
        row[field]
        for row in rows
        if row["train_source"] == src
        and row["deploy_target"] == tgt
        and row["status"] == "evaluated"
        and row.get(field) is not None
        and (staleness is None or row["staleness_h"] == staleness)
    ]
    return float(np.mean([float(v) for v in vals])) if vals else float("nan")


def _gate_label(
    rows: list[dict[str, Any]], src: str, tgt: str, staleness=None
) -> str:
    vals = [
        row["gate_decision"]
        for row in rows
        if row["train_source"] == src
        and row["deploy_target"] == tgt
        and (staleness is None or row["staleness_h"] == staleness)
    ]
    if not vals:
        return "-"
    if all(v == "closed" for v in vals):
        return "C"
    if all(v == "open" for v in vals):
        return "O"
    if all(v == "unavailable" for v in vals):
        return "-"
    return "M"  # mixed across staleness


def _heatmap(ax, grid, sats, cmap, vmin, vmax, annot=None, fmt="{:.0f}"):
    im = ax.imshow(grid, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(sats)))
    ax.set_yticks(range(len(sats)))
    ax.set_xticklabels(sats, rotation=45, ha="right", fontsize=6)
    ax.set_yticklabels(sats, fontsize=6)
    for i in range(len(sats)):
        for j in range(len(sats)):
            if np.isnan(grid[i, j]):
                ax.text(j, i, "n/a", ha="center", va="center", fontsize=5,
                        color=C_GRAY)
                continue
            text = fmt.format(grid[i, j])
            if annot is not None:
                text = f"{text}\n{annot[i][j]}"
            ax.text(j, i, text, ha="center", va="center", fontsize=5,
                    color="black")
    for i in range(len(sats)):
        ax.add_patch(
            plt.Rectangle((i - 0.5, i - 0.5), 1, 1, fill=False,
                          edgecolor=C_PHYS, lw=1.2)
        )
    return im


def fig_generalization_matrix(payload, out_dir: Path) -> list[Path]:
    """Headline: degradation % per cell, gate annotated, one panel per staleness."""
    rows = payload["matrix_rows"]
    sats = _sat_order(rows)
    stales = sorted({r["staleness_h"] for r in rows})
    ncol = min(3, len(stales))
    nrow = int(np.ceil(len(stales) / ncol))
    fig, axes = plt.subplots(
        nrow, ncol, figsize=(4.0 * ncol, 3.6 * nrow), squeeze=False
    )
    for idx, staleness in enumerate(stales):
        ax = axes[idx // ncol][idx % ncol]
        grid = np.array(
            [
                [_cell_value(rows, s, t, "degradation_pct", staleness) for t in sats]
                for s in sats
            ]
        )
        annot = [[_gate_label(rows, s, t, staleness) for t in sats] for s in sats]
        finite = grid[np.isfinite(grid)]
        lim = float(np.max(np.abs(finite))) if finite.size else 1.0
        _heatmap(ax, grid, sats, "coolwarm", -lim, lim, annot, "{:+.0f}%")
        ax.set_title(f"{staleness} h staleness", fontsize=8)
        ax.set_ylabel("train source", fontsize=7)
        ax.set_xlabel("deploy target", fontsize=7)
    for idx in range(len(stales), nrow * ncol):
        axes[idx // ncol][idx % ncol].axis("off")
    fig.suptitle(
        "Cross-satellite generalization: learned vs SGP4 degradation "
        "(positive = learned worse). O=gate open, C=closed, M=mixed, -=unavailable",
        fontsize=9,
    )
    fig.text(0.5, -0.01, SCOPE_NOTE, ha="center", fontsize=6, color=C_GRAY)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return _save(fig, out_dir, "fig_cross_satellite_generalization_matrix")


def fig_gate_matrix(payload, out_dir: Path) -> list[Path]:
    rows = payload["matrix_rows"]
    sats = _sat_order(rows)
    codes = {"C": 0.0, "M": 0.5, "O": 1.0, "-": np.nan}
    grid = np.array(
        [[codes[_gate_label(rows, s, t)] for t in sats] for s in sats]
    )
    annot = [[_gate_label(rows, s, t) for t in sats] for s in sats]
    fig, ax = plt.subplots(figsize=(1.0 + 0.7 * len(sats), 1.0 + 0.6 * len(sats)))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "gate", [C_PHYS, "#DDDDDD", C_GATE]
    )
    _heatmap(ax, grid, sats, cmap, 0.0, 1.0, annot, "")
    ax.set_title(
        "Evidence Gate decision, aggregated over staleness\n"
        "(C = closed in every row, O = open in every row, M = mixed)",
        fontsize=8,
    )
    ax.set_ylabel("train source", fontsize=7)
    ax.set_xlabel("deploy target", fontsize=7)
    fig.text(0.5, -0.04, SCOPE_NOTE, ha="center", fontsize=6, color=C_GRAY)
    fig.tight_layout()
    return _save(fig, out_dir, "fig_gate_decision_matrix")


def fig_winrate_matrix(payload, out_dir: Path) -> list[Path]:
    rows = payload["matrix_rows"]
    sats = _sat_order(rows)
    grid = np.array(
        [
            [100.0 * _cell_value(rows, s, t, "pair_win_rate") for t in sats]
            for s in sats
        ]
    )
    fig, ax = plt.subplots(figsize=(1.0 + 0.7 * len(sats), 1.0 + 0.6 * len(sats)))
    _heatmap(ax, grid, sats, "PuOr", 0.0, 100.0, None, "{:.0f}%")
    ax.set_title(
        "Pair-level win rate of the learned branch vs SGP4\n"
        "(fraction of accepted TLE pairs where learned MAE < baseline MAE)",
        fontsize=8,
    )
    ax.set_ylabel("train source", fontsize=7)
    ax.set_xlabel("deploy target", fontsize=7)
    fig.text(0.5, -0.04, SCOPE_NOTE, ha="center", fontsize=6, color=C_GRAY)
    fig.tight_layout()
    return _save(fig, out_dir, "fig_pair_winrate_matrix")


def fig_reject_sensitivity(payload, out_dir: Path) -> list[Path]:
    rows = payload["reject_sensitivity_rows"]
    if not rows:
        return []
    sats = sorted({r["satellite"] for r in rows})
    thresholds = sorted({float(r["reject_hz"]) for r in rows})
    labels = ["none" if not np.isfinite(t) else f"{t:.0f}" for t in thresholds]
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.4))
    for sat in sats:
        sub = {float(r["reject_hz"]): r for r in rows if r["satellite"] == sat}
        axes[0].plot(
            range(len(thresholds)),
            [sub.get(t, {}).get("reject_rate_pct", np.nan) for t in thresholds],
            marker="o", ms=3, lw=1.2, label=sat,
        )
        axes[1].plot(
            range(len(thresholds)),
            [sub.get(t, {}).get("residual_mae_hz", np.nan) for t in thresholds],
            marker="s", ms=3, lw=1.2, label=sat,
        )
        axes[2].plot(
            range(len(thresholds)),
            [sub.get(t, {}).get("degradation_pct", np.nan) for t in thresholds],
            marker="^", ms=3, lw=1.2, label=sat,
        )
    for ax, title, ylab in zip(
        axes,
        ("(a) pairs removed", "(b) retained residual scale", "(c) learnability"),
        ("reject rate [%]", "residual MAE [Hz]", "degradation [%]"),
    ):
        ax.set_xticks(range(len(thresholds)))
        ax.set_xticklabels(labels, fontsize=7)
        ax.set_xlabel("reject threshold |r| [Hz]", fontsize=8)
        ax.set_ylabel(ylab, fontsize=8)
        ax.set_title(title, fontsize=9)
        ax.grid(True, ls=":", alpha=0.35)
    axes[2].axhline(0.0, color=C_BAD, lw=1.0, ls="--")
    axes[0].legend(fontsize=6, frameon=False)
    fig.suptitle(
        "Reject-threshold sensitivity: does screening manufacture the negative "
        "result? (c) above 0 = learned still worse after relaxing the screen",
        fontsize=9,
    )
    fig.text(0.5, -0.02, SCOPE_NOTE, ha="center", fontsize=6, color=C_GRAY)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    return _save(fig, out_dir, "fig_reject_threshold_sensitivity")


def fig_gate_agreement(payload, out_dir: Path) -> list[Path]:
    rows = payload["gate_agreement_rows"]
    if not rows:
        return []
    gates = sorted({r["gate_a"] for r in rows} | {r["gate_b"] for r in rows})
    grid = np.full((len(gates), len(gates)), np.nan)
    for row in rows:
        i, j = gates.index(row["gate_a"]), gates.index(row["gate_b"])
        val = row["agreement_pct"]
        grid[i, j] = grid[j, i] = np.nan if val is None else float(val)
    np.fill_diagonal(grid, 100.0)
    fig, ax = plt.subplots(figsize=(5.2, 4.4))
    _heatmap(ax, grid, gates, "YlGnBu", 0.0, 100.0, None, "{:.0f}%")
    ax.set_title(
        "Gate-objective agreement over evaluated cells\n"
        "(no objective is asserted superior; disagreement is the finding)",
        fontsize=8,
    )
    fig.text(0.5, -0.04, SCOPE_NOTE, ha="center", fontsize=6, color=C_GRAY)
    fig.tight_layout()
    return _save(fig, out_dir, "fig_gate_metric_agreement")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=HERE / "results.json")
    parser.add_argument("--out-dir", type=Path, default=HERE / "figures")
    parser.add_argument("--force", action="store_true",
                        help="render even below the satellite threshold")
    args = parser.parse_args(argv)

    payload = json.loads(args.results.read_text(encoding="utf-8"))
    meta = payload["metadata"]
    found = int(meta["satellites_found"])
    minimum = int(meta["min_satellites_for_generalization_claim"])
    if found < minimum and not args.force:
        print(
            f"no figures emitted: {found} satellite(s) < {minimum} required. "
            "A dry run must not produce multi-satellite figures."
        )
        return 0

    args.out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    written += fig_generalization_matrix(payload, args.out_dir)
    written += fig_gate_matrix(payload, args.out_dir)
    written += fig_winrate_matrix(payload, args.out_dir)
    written += fig_reject_sensitivity(payload, args.out_dir)
    written += fig_gate_agreement(payload, args.out_dir)
    for path in written:
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
