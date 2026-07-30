#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.7"]
# ///

# How to run:
#   uv run experiments/exp10_residual_learnability/run_residual_learnability.py

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/review/black_kite_1_target_specific_residual_experiment.md"
COMPACT = ROOT / "docs/review/bk_negative_result_compact.csv"
OUT = Path(__file__).resolve().parent
ROW = re.compile(
    r"\|\s*(\d+)h\s*\|\s*(\d+)\s*\|\s*([+\-0-9.]+)\s*\|"
    r"\s*([+\-0-9.]+)\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|"
    r"\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|"
)


def read_report_rows() -> list[dict[str, float | int]]:
    """Read only the reported BK1 held-out distribution summaries."""
    rows: list[dict[str, float | int]] = []
    text = REPORT.read_text(encoding="utf-8")
    for match in ROW.finditer(text):
        age, count, mean, std, p50, p90, p99, maximum = match.groups()
        rows.append(
            {
                "staleness_h": int(age),
                "n_test_samples": int(count),
                "mean_hz": float(mean),
                "std_hz": float(std),
                "p50_abs_hz": float(p50),
                "p90_abs_hz": float(p90),
                "p99_abs_hz": float(p99),
                "max_abs_hz": float(maximum),
            }
        )
    if len(rows) != 6:
        raise RuntimeError(f"expected six BK1 distribution rows, found {len(rows)}")
    return rows


def read_transfer_rows() -> list[dict[str, str | float]]:
    """Read cross-satellite summary rows without treating them as samples."""
    lines = [
        line
        for line in COMPACT.read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    rows: list[dict[str, str | float]] = []
    for row in csv.DictReader(lines):
        if row["experiment"] != "bk1_to_bk2_crosssat":
            continue
        rows.append(
            {
                "staleness_h": float(row["staleness_h"]),
                "baseline_mae_hz": float(row["zero_baseline_mae_hz"]),
                "learned_mae_hz": float(row["learned_test_mae_hz"]),
                "selected_model": row["selected_learned_model"],
                "gate_decision_mae": "closed",
            }
        )
    return rows


def save_figures(rows: list[dict[str, float | int]]) -> None:
    """Render summary-only figures with their availability limits visible."""
    ages = [float(row["staleness_h"]) for row in rows]
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    for key, label, style in (
        ("p50_abs_hz", "median |r|", "o-"),
        ("p90_abs_hz", "p90 |r|", "s-"),
        ("p99_abs_hz", "p99 |r|", "^-"),
        ("max_abs_hz", "max |r|", "d--"),
    ):
        ax.plot(ages, [float(row[key]) for row in rows], style, label=label)
    ax.axhline(500.0, color="black", linestyle=":", label="F_tol = 500 Hz")
    ax.set(xlabel="stale-TLE age [h]", ylabel="reported absolute residual [Hz]")
    ax.set_title("BK1 reported residual quantiles (summary-only)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "fig_residual_distribution.pdf")
    fig.savefig(OUT / "fig_residual_distribution.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.0, 2.6))
    ax.axis("off")
    ax.text(0.02, 0.78, "NOT AVAILABLE", fontsize=18, weight="bold", color="#9b2c2c")
    ax.text(
        0.02,
        0.55,
        "Sample-level residual sequence was not committed.",
        fontsize=12,
    )
    ax.text(
        0.02,
        0.38,
        "Autocorrelation, sign stability, and PSD cannot be computed",
        fontsize=12,
    )
    ax.text(
        0.02,
        0.21,
        "without regenerating from the local raw TLE archive.",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(OUT / "fig_residual_autocorrelation.pdf")
    fig.savefig(OUT / "fig_residual_autocorrelation.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    ax.plot(
        ages,
        [0.2430, 0.8161, 1.9433, 4.8947, 10.1153, 26.9243],
        "o-",
        label="SGP4 baseline MAE",
    )
    ax.plot(
        ages,
        [0.3501, 0.9109, 2.8608, 5.9092, 11.7663, 45.2629],
        "s--",
        label="selected learned MAE",
    )
    ax.set(xlabel="stale-TLE age [h]", ylabel="held-out MAE [Hz]")
    ax.set_title("Reported held-out comparison; split distributions unavailable")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "fig_train_val_test_shift.pdf")
    fig.savefig(OUT / "fig_train_val_test_shift.png", dpi=180)
    plt.close(fig)


def main() -> None:
    rows = read_report_rows()
    transfer = read_transfer_rows()
    payload = {
        "metadata": {
            "scope": "software-only model-derived inter-TLE residual diagnostics",
            "reference_is_measured_truth": False,
            "source": str(REPORT.relative_to(ROOT)),
            "sample_level_arrays_available": False,
            "temporal_correlation_note": (
                "24 in-pass samples are temporally correlated."
            ),
        },
        "bk1_target_specific": rows,
        "bk1_to_bk2_transfer_summary": transfer,
        "unavailable_diagnostics": [
            "residual sign stability",
            "sample-level autocorrelation",
            "cross-pair autocorrelation",
            "train/validation/test distribution statistics",
            "baseline-vs-learned residual distributions",
            "residual PSD",
        ],
    }
    (OUT / "results.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    with (OUT / "residual_learnability_summary.csv").open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    save_figures(rows)
    print(f"wrote {OUT / 'results.json'}")


if __name__ == "__main__":
    main()
