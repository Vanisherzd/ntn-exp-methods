#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

# How to run: uv run <this-file> --dry-run or uv run <this-file> INPUT.csv

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "docs/review/bk_negative_result_compact.csv"
OUT = Path(__file__).resolve().parent


def read_summary(path: Path) -> list[dict[str, str]]:
    """Map the current compact summary into the future matrix schema."""
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    result: list[dict[str, str]] = []
    for row in csv.DictReader(lines):
        experiment = row["experiment"]
        source, target = (
            ("BK1", "BK1")
            if experiment == "bk1_target_specific"
            else ("BK1", "BK2")
        )
        degradation = (
            float(row["learned_test_mae_hz"])
            / float(row["zero_baseline_mae_hz"])
            - 1.0
        ) * 100.0
        result.append(
            {
                "train_source": source,
                "deploy_target": target,
                "staleness_h": row["staleness_h"],
                "baseline_mae_hz": row["zero_baseline_mae_hz"],
                "learned_mae_hz": row["learned_test_mae_hz"],
                "degradation_pct": str(round(degradation, 3)),
                "gate_decision": "closed",
                "p95_abs_error_hz": "",
                "p99_abs_error_hz": "",
                "n_pairs": "",
                "reject_count": "",
                "status": "summary_only",
            }
        )
    return result


def main() -> None:
    args = sys.argv[1:]
    input_path = (
        Path(args[0])
        if args and not args[0].startswith("--")
        else DEFAULT_INPUT
    )
    dry_run = "--dry-run" in args
    rows = read_summary(input_path)
    fields = list(rows[0]) if rows else ["train_source", "deploy_target"]
    with (OUT / "generalization_matrix.csv").open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        "metadata": {
            "scope": "Paper 1+ multi-satellite pipeline skeleton",
            "reference_is_measured_truth": False,
            "dry_run": dry_run,
            "input": str(input_path.relative_to(ROOT)),
            "raw_tle_inputs_available": False,
            "additional_satellites_downloaded": False,
        },
        "matrix_rows": rows,
        "required_future_input_columns": [
            "train_source",
            "deploy_target",
            "staleness_h",
            "baseline_mae_hz",
            "learned_mae_hz",
            "p95_abs_error_hz",
            "p99_abs_error_hz",
            "n_pairs",
            "reject_count",
        ],
    }
    (OUT / "results.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT / 'results.json'}")


if __name__ == "__main__":
    main()
