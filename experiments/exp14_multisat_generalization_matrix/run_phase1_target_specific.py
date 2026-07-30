#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "sgp4>=2.23"]
# ///
"""Phase-1 target-specific learnability across the heterogeneous LEO dataset.

Question: is target-specific inter-TLE residual learnability satellite/regime
dependent?

Runs A -> A ONLY, for every retained non-BLACK-KITE satellite, at all six
staleness bands. No cross-satellite transfer. No reject sensitivity.

Targets are read from the authoritative qualification artifact
(`dataset_qualification.json` retained_keys) and identities come from canonical
ingestion, which resolves names from the preserved SATCAT responses. Nothing is
hard-coded by name.

Protocol is imported wholesale from the Phase-0 evaluator, which in turn imports
the unified pipeline, so pairing rule, feature schema, reject rule, ground
station, carrier, sampling schedule, candidate set, gamma and chronological
split logic are identical to every cell run so far -- by construction, not by
convention.

  train_A      fits the candidates
  validation_A selects the model AND decides the preregistered MAE gate
  test_A       reports consequences only -- never selects, never gates

A real-data candidate regime requires BOTH:
  1. the preregistered MAE gate OPENs on validation, AND
  2. held-out learned MAE beats SGP4.

reference_is_measured_truth = false. Model-derived inter-TLE residuals only; no
measured RF truth, no packet, error-rate, receiver-acknowledgement,
over-the-air, or on-orbit result.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import run_multisat_generalization_matrix as pipeline  # noqa: E402
import run_phase0_black_kite as phase0  # noqa: E402

BLACK_KITE = {phase0.BK1, phase0.BK2}


def retained_targets(qualification_json: Path) -> list[int]:
    """Retained non-BLACK-KITE NORAD ids, from the authoritative artifact."""
    payload = json.loads(qualification_json.read_text(encoding="utf-8"))
    norads = []
    for key in payload["retained_keys"]:
        norad = int(key.replace("NORAD", ""))
        if norad not in BLACK_KITE:
            norads.append(norad)
    return sorted(norads)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tle-dir", type=Path, default=ROOT / "dataraw" / "spacetrack")
    parser.add_argument(
        "--qualification",
        type=Path,
        default=HERE / "dataset_qualification.json",
    )
    parser.add_argument("--gs-lat", type=float, default=24.0)
    parser.add_argument("--gs-lon", type=float, default=121.0)
    parser.add_argument("--gs-alt", type=float, default=100.0)
    parser.add_argument("--carrier-hz", type=float, default=868e6)
    parser.add_argument(
        "--staleness", type=int, nargs="+", default=sorted(pipeline.STALENESS_BANDS)
    )
    parser.add_argument("--reject-hz", type=float, default=1500.0)
    parser.add_argument("--gamma", type=float, default=0.95)
    parser.add_argument("--f-tol-hz", type=float, default=500.0)
    parser.add_argument("--alpha-g", type=float, default=1.0)
    parser.add_argument("--hop-bandwidth-hz", type=float, default=137e3)
    parser.add_argument("--primary-gate", default="mae")
    parser.add_argument("--n-boot", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260727)
    parser.add_argument(
        "--only-norad",
        type=int,
        nargs="+",
        default=None,
        help="restrict to these NORAD ids (chunked execution; results merge later)",
    )
    parser.add_argument("--out-dir", type=Path, default=HERE / "phase1_target_specific")
    args = parser.parse_args(argv)

    targets = retained_targets(args.qualification)
    if args.only_norad:
        requested = set(args.only_norad)
        unknown = requested - set(targets)
        if unknown:
            print(f"ABORT: {sorted(unknown)} are not retained targets", file=sys.stderr)
            return 2
        targets = [n for n in targets if n in requested]
    sats = {s.norad: s for s in pipeline.discover_satellites(args.tle_dir)}
    missing = [n for n in targets if n not in sats]
    if missing:
        print(f"ABORT: no canonical history for NORAD {missing}", file=sys.stderr)
        return 2

    print(f"Phase-1 target-specific: {len(targets)} satellites x "
          f"{len(args.staleness)} bands (A->A only)")
    for norad in targets:
        sat = sats[norad]
        gaps = sat.gap_stats_h()
        print(f"  {sat.key:12} {sat.name:22} records={sat.n_records:>6} "
              f"median_gap={gaps['median_gap_h']}h")

    cache: dict = {}
    rows: list[dict[str, Any]] = []
    for norad in targets:
        sat = sats[norad]
        gaps = sat.gap_stats_h()
        for band in args.staleness:
            row = phase0.evaluate_phase0_cell(sat, sat, band, args, cache)
            row["canonical_records"] = sat.n_records
            row["median_gap_h"] = gaps["median_gap_h"]
            row["epoch_start"] = sat.epochs()[0].isoformat()
            row["epoch_end"] = sat.epochs()[-1].isoformat()
            rows.append(row)
            if row["status"] != "evaluated":
                print(f"  {sat.name:22} {band:>4}h  {row['status']}")
                continue
            print(
                f"  {sat.name:22} {band:>4}h "
                f"gate={row['gate_decision']:<6} "
                f"dMAE={row['test_delta_mae_hz']:+9.4f}Hz "
                f"deg={row['test_degradation_pct']:+8.2f}% "
                f"win={row['learned_pair_win_rate']:.3f} "
                f"p={row['sign_test_p']:.3g}"
            )

    problems = phase0.check_integrity(rows, {n: sats[n] for n in targets})
    if problems:
        print("INTEGRITY FAILURE -- no scientific conclusion emitted:", file=sys.stderr)
        for item in problems:
            print(f"  - {item}", file=sys.stderr)
        return 3

    # A real-data candidate regime: MAE gate OPEN on validation AND held-out win.
    candidates = [
        r
        for r in rows
        if r["status"] == "evaluated"
        and r["gate_decision"] == "open"
        and r["test_delta_mae_hz"] < 0
    ]
    gate_opens = [
        r for r in rows if r["status"] == "evaluated" and r["gate_decision"] == "open"
    ]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    pair_rows, gate_rows, deltas_by_cell = [], [], {}
    for row in rows:
        pairs = row.pop("_pairs", None)
        if row["status"] != "evaluated":
            continue
        pair_rows.append(row)
        gate_rows.append(row)
        deltas_by_cell[f"{row['cell']}|{row['staleness_h']}"] = (
            pairs["deltas"].tolist() if pairs is not None else []
        )

    _write(args.out_dir / "target_specific_results.csv", rows, RESULT_HEADER)
    _write(
        args.out_dir / "target_specific_pair_statistics.csv", pair_rows, PAIR_HEADER
    )
    _write(
        args.out_dir / "target_specific_gate_diagnostics.csv", gate_rows, GATE_HEADER
    )
    (args.out_dir / "target_specific_results.json").write_text(
        json.dumps(
            {
                "metadata": {
                    "campaign": "paper1_plus_phase1_target_specific",
                    "question": (
                        "is target-specific inter-TLE residual learnability "
                        "satellite/regime dependent?"
                    ),
                    "design": "A->A only; no cross-satellite transfer",
                    "targets": [f"NORAD{n}" for n in targets],
                    "target_source": str(args.qualification.name),
                    "reference_is_measured_truth": False,
                    "hardware_used": False,
                    "rf_used": False,
                    "canonical_input": "GP_HISTORY JSON only; TLE archival only",
                    "gate_protocol": (
                        "train fits; validation selects and decides G; "
                        "test reports consequences only"
                    ),
                    "candidate_criterion": (
                        "preregistered MAE gate OPEN on validation AND held-out "
                        "learned MAE below SGP4"
                    ),
                    "integrity_checks_passed": True,
                    "gamma": args.gamma,
                    "reject_hz": args.reject_hz,
                    "f_tol_hz": args.f_tol_hz,
                    "n_boot": args.n_boot,
                    "seed": args.seed,
                    "n_mae_gate_open": len(gate_opens),
                    "n_real_candidate_regimes": len(candidates),
                },
                "satellites": {
                    str(n): {
                        "key": sats[n].key,
                        "name": sats[n].name,
                        "canonical_records": sats[n].n_records,
                        "epoch_start": sats[n].epochs()[0].isoformat(),
                        "epoch_end": sats[n].epochs()[-1].isoformat(),
                        **sats[n].gap_stats_h(),
                        **sats[n].ingestion_audit,
                    }
                    for n in targets
                },
                "rows": rows,
                "per_pair_delta_mae_hz": deltas_by_cell,
                "candidate_regimes": [
                    {
                        "satellite": r["target_name"],
                        "staleness_h": r["staleness_h"],
                        "selected_model": r["selected_model"],
                        "test_delta_mae_hz": r["test_delta_mae_hz"],
                        "test_degradation_pct": r["test_degradation_pct"],
                        "pair_win_rate": r["learned_pair_win_rate"],
                        "sign_test_p": r["sign_test_p"],
                    }
                    for r in candidates
                ],
            },
            indent=2,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    if candidates:
        print("*** REAL-DATA CANDIDATE REGIME(S) FOUND ***")
        for r in candidates:
            print(
                f"    {r['target_name']} @ {r['staleness_h']}h  "
                f"model={r['selected_model']}  "
                f"test dMAE={r['test_delta_mae_hz']:+.4f} Hz "
                f"({r['test_degradation_pct']:+.2f}%)  "
                f"win={r['learned_pair_win_rate']:.3f} p={r['sign_test_p']:.3g}"
            )
        print("    STOP: do not start cross-satellite experiments.")
    else:
        print(
            f"No real-data candidate regime: MAE gate opened in "
            f"{len(gate_opens)} of {len(rows)} rows; none combined an open gate "
            "with a held-out win."
        )
    return 0


def _write(path: Path, rows, header) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


RESULT_HEADER = [
    "target_satellite", "target_name", "staleness_h", "status",
    "canonical_records", "median_gap_h", "epoch_start", "epoch_end",
    "reject_hz", "gamma", "f_tol_hz",
    "n_train_pairs", "n_validation_pairs", "n_test_pairs",
    "rejected_train_pairs", "rejected_validation_pairs", "rejected_test_pairs",
    "reject_rate_target_pct",
    "selected_model", "ridge_alpha",
    "val_sgp4_mae_hz", "val_learned_mae_hz", "val_degradation_pct", "gate_decision",
    "test_sgp4_mae_hz", "test_learned_mae_hz", "test_delta_mae_hz",
    "test_degradation_pct", "deployed_test_mae_hz",
]

PAIR_HEADER = [
    "target_name", "staleness_h", "n_unique_test_pair_ids",
    "learned_wins", "sgp4_wins", "ties", "learned_pair_win_rate",
    "median_pair_delta_mae_hz", "mean_pair_delta_mae_hz",
    "boot_ci_low_hz", "boot_ci_high_hz", "sign_test_p",
]

GATE_HEADER = [
    "target_name", "staleness_h", "selected_model", "gate_decision",
    "gate_mae", "gate_p95", "gate_p99", "gate_outage", "gate_guard_cost",
    "val_sgp4_mae_hz", "val_learned_mae_hz",
    "test_sgp4_p95_hz", "test_learned_p95_hz",
    "test_sgp4_p99_hz", "test_learned_p99_hz",
    "test_sgp4_outage_proxy", "test_learned_outage_proxy",
]


if __name__ == "__main__":
    sys.exit(main())
