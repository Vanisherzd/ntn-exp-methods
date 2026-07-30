#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.7"]
# ///

# How to run:
#   uv run experiments/exp12_tail_aware_gate/run_tail_aware_gate.py

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
COMPACT = ROOT / "docs/review/bk_negative_result_compact.csv"
GATE = ROOT / "docs/review/gate_stress_compact.csv"
OUT = Path(__file__).resolve().parent


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a repository CSV while preserving its provenance comments."""
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    return list(csv.DictReader(lines))


def main() -> None:
    real = [
        row
        for row in read_csv(COMPACT)
        if row["experiment"] == "bk1_target_specific"
    ]
    synthetic = read_csv(GATE)
    real_rows = [
        {
            "regime": "real_BK1",
            "staleness_h": int(row["staleness_h"]),
            "mae_gate": "closed",
            "p95_gate": "unavailable",
            "p99_gate": "unavailable",
            "guard_cost_gate": "unavailable",
            "outage_proxy_gate": "unavailable",
            "reason": "learned per-sample predictions and validation tails are absent",
        }
        for row in real
    ]
    synthetic_rows = [
        {
            "regime": f"synthetic_{row['regime']}",
            "staleness_h": None,
            "mae_gate": row["gate_g095"],
            "p95_gate": "unavailable",
            "p99_gate": "unavailable",
            "guard_cost_gate": "proxy_only",
            "outage_proxy_gate": "proxy_only",
            "reason": (
                "summary contains guard/outage proxy ordering, not validation "
                "p95/p99 sequences"
            ),
        }
        for row in synthetic
    ]
    payload = {
        "metadata": {
            "scope": "software-only gate-variant audit",
            "reference_is_measured_truth": False,
            "real_source": str(COMPACT.relative_to(ROOT)),
            "synthetic_source": str(GATE.relative_to(ROOT)),
            "synthetic_is_mechanism_check_only": True,
        },
        "real_black_kite": real_rows,
        "synthetic_mechanism": synthetic_rows,
        "gate_definitions": {
            "mae": "reported current gate decision",
            "p95": "requires validation p95 learned and baseline errors; unavailable",
            "p99": "requires validation p99 learned and baseline errors; unavailable",
            "guard_cost": (
                "2*p99(|e|); proxy ordering only where summary guard values exist"
            ),
            "outage": (
                "Pr(|e| > F_tol); proxy ordering only where summary outage values exist"
            ),
        },
    }
    (OUT / "results.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    fields = [
        "regime",
        "staleness_h",
        "mae_gate",
        "p95_gate",
        "p99_gate",
        "guard_cost_gate",
        "outage_proxy_gate",
        "reason",
    ]
    with (OUT / "tail_gate_summary.csv").open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(real_rows + synthetic_rows)

    labels = [row["regime"] for row in real_rows + synthetic_rows]
    colors = [
        "#2f6f3e" if row["mae_gate"] == "open" else "#a23a35"
        for row in real_rows + synthetic_rows
    ]
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    ax.bar(
        range(len(labels)),
        [
            1 if row["mae_gate"] == "open" else 0
            for row in real_rows + synthetic_rows
        ],
        color=colors,
    )
    ax.set(
        xticks=range(len(labels)),
        xticklabels=labels,
        ylabel="MAE gate at gamma=0.95",
    )
    ax.set_yticks([0, 1], ["closed", "open"])
    ax.set_title("Gate metrics: real decisions and synthetic mechanism check")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(OUT / "fig_gate_metric_comparison.pdf")
    fig.savefig(OUT / "fig_gate_metric_comparison.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.axis("off")
    ax.text(0.02, 0.78, "Tail-aware decision status", fontsize=17, weight="bold")
    ax.text(
        0.02,
        0.53,
        "Real BK1 p95/p99/guard/outage gates: unavailable from committed artifacts.",
        fontsize=11,
    )
    ax.text(
        0.02,
        0.34,
        "Synthetic p95/p99 gates: unavailable; guard/outage values remain proxy-only.",
        fontsize=11,
    )
    ax.text(
        0.02,
        0.15,
        "No tail-aware opening or closure is inferred beyond the reported MAE gate.",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(OUT / "fig_tail_gate_policy_table.pdf")
    fig.savefig(OUT / "fig_tail_gate_policy_table.png", dpi=180)
    plt.close(fig)
    print(f"wrote {OUT / 'results.json'}")


if __name__ == "__main__":
    main()
