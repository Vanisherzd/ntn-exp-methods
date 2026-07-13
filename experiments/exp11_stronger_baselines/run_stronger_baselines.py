#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.7"]
# ///

# How to run:
#   uv run experiments/exp11_stronger_baselines/run_stronger_baselines.py

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/review/black_kite_1_target_specific_residual_experiment.md"
OUT = Path(__file__).resolve().parent


def parse_rows() -> list[dict[str, str | float | int]]:
    """Parse the existing BK1 model comparison table."""
    rows: list[dict[str, str | float | int]] = []
    active = False
    for line in REPORT.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Window | n(tr/va/te)"):
            active = True
            continue
        if active and line.startswith("|---"):
            continue
        if active and not line.startswith("|"):
            break
        if not active or "h |" not in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 13 or not cells[0].endswith("h"):
            continue
        age = int(cells[0][:-1])
        values = [float(cells[index]) for index in (3, 4, 5, 6, 7, 8, 10)]
        names = [
            "zero_baseline",
            "median_bias",
            "ridge",
            "random_forest",
            "grad_boost",
            "mlp",
            "selected",
        ]
        row: dict[str, str | float | int] = {"staleness_h": age}
        row.update(dict(zip(names, values)))
        row["selected_model"] = cells[9]
        row["reported_gate_mae"] = "closed"
        row["p95_abs_error_hz"] = None
        row["p99_abs_error_hz"] = None
        rows.append(row)
    if len(rows) != 6:
        raise RuntimeError(f"expected six comparison rows, found {len(rows)}")
    return rows


def save_figures(rows: list[dict[str, str | float | int]]) -> None:
    """Render MAE and tail-availability figures from reported values."""
    ages = [float(row["staleness_h"]) for row in rows]
    names = [
        "zero_baseline",
        "median_bias",
        "ridge",
        "random_forest",
        "grad_boost",
        "mlp",
    ]
    labels = ["zero", "median", "ridge", "RF", "GBR", "MLP"]
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    for name, label in zip(names, labels):
        ax.plot(ages, [float(row[name]) for row in rows], marker="o", label=label)
    ax.set(xlabel="stale-TLE age [h]", ylabel="reported held-out MAE [Hz]")
    ax.set_title("Stronger baseline comparison (reported test metrics)")
    ax.legend(ncol=3, fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "fig_model_comparison_mae.pdf")
    fig.savefig(OUT / "fig_model_comparison_mae.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    ax.axis("off")
    ax.text(
        0.02,
        0.78,
        "TAIL METRICS NOT AVAILABLE",
        fontsize=17,
        weight="bold",
        color="#9b2c2c",
    )
    ax.text(
        0.02,
        0.54,
        "The committed report has model MAE and selected-model identity",
        fontsize=12,
    )
    ax.text(
        0.02,
        0.37,
        "but no per-model p95/p99 predictions or validation MAE values.",
        fontsize=12,
    )
    ax.text(
        0.02,
        0.20,
        "No tail gate decision is inferred from MAE alone.",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(OUT / "fig_tail_error_comparison.pdf")
    fig.savefig(OUT / "fig_tail_error_comparison.png", dpi=180)
    plt.close(fig)


def main() -> None:
    rows = parse_rows()
    payload = {
        "metadata": {
            "scope": "software-only summary-level baseline comparison",
            "reference_is_measured_truth": False,
            "source": str(REPORT.relative_to(ROOT)),
            "same_chronological_split": True,
            "per_model_validation_metrics_available": False,
            "per_model_tail_predictions_available": False,
        },
        "rows": rows,
        "interpretation": (
            "All reported selected learned models remain worse than zero-residual "
            "SGP4 at every BK1 staleness row; this is not a fresh retraining run."
        ),
    }
    (OUT / "results.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    fields = [
        "staleness_h",
        "selected_model",
        "zero_baseline",
        "median_bias",
        "ridge",
        "random_forest",
        "grad_boost",
        "mlp",
        "selected",
        "reported_gate_mae",
        "p95_abs_error_hz",
        "p99_abs_error_hz",
    ]
    with (OUT / "stronger_baselines_summary.csv").open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    save_figures(rows)
    print(f"wrote {OUT / 'results.json'}")


if __name__ == "__main__":
    main()
