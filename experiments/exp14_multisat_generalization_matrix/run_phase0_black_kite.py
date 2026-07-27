#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "sgp4>=2.23"]
# ///
"""Phase-0 BLACK KITE re-derivation under the unified protocol (Paper 1+).

Runs EXACTLY four ordered cells, all supported staleness bands:

    BK1 -> BK1,  BK2 -> BK2,  BK1 -> BK2,  BK2 -> BK1

Purpose: re-derive the frozen Paper 1 objects under the new leakage-free
pair-level protocol before any broader generalization claim. This is the
scientific checksum, not the generalization experiment.

Every protocol primitive is imported from the unified pipeline
(`run_multisat_generalization_matrix`) rather than reimplemented, so the
pairing rule, feature schema, reject rule, ground station, carrier, sampling
schedule, candidate set, gamma and chronological split logic are identical to
every other cell by construction.

  source train      fits the candidates
  target validation selects the model AND decides the Evidence Gate G
  target test       reports consequences only -- never selects, never decides G

Pair-level integrity invariants are asserted BEFORE any result is written. If
one fails the run aborts and no scientific conclusion is emitted.

reference_is_measured_truth = false. Model-derived inter-TLE residuals only; no
measured RF truth, and no packet, error-rate, receiver-acknowledgement,
over-the-air, or on-orbit result.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import run_multisat_generalization_matrix as pipeline  # noqa: E402

BK1, BK2 = 66741, 68474
CELLS: tuple[tuple[int, int], ...] = ((BK1, BK1), (BK2, BK2), (BK1, BK2), (BK2, BK1))


class IntegrityError(RuntimeError):
    """A pair-level invariant failed; no scientific conclusion may be drawn."""


def _split_rejected(
    rejected: list[dict[str, Any]], t_train: dt.datetime, t_val: dt.datetime
) -> dict[str, int]:
    """Count rejected pairs per chronological segment by reference epoch."""
    counts = {"train": 0, "validation": 0, "test": 0}
    for row in rejected:
        ref = dt.datetime.fromisoformat(row["ref_epoch_utc"])
        if ref < t_train:
            counts["train"] += 1
        elif ref < t_val:
            counts["validation"] += 1
        else:
            counts["test"] += 1
    return counts


def _per_pair_delta(
    pairs: list[dict[str, Any]], phys, learned, f_tol_hz: float
) -> np.ndarray:
    """learned minus SGP4 per-pair MAE. One value per accepted TLE pair."""
    return np.array(
        [
            pipeline.pair_metrics(p["y"] - learned(p["x"]), f_tol_hz)["mae_hz"]
            - pipeline.pair_metrics(p["y"] - phys(p["x"]), f_tol_hz)["mae_hz"]
            for p in pairs
        ]
    )


def evaluate_phase0_cell(
    source, target, staleness_h: int, args, cache: dict
) -> dict[str, Any]:
    """One Phase-0 cell. Protocol primitives come from the unified pipeline."""
    gs = (args.gs_lat, args.gs_lon, args.gs_alt)
    key_src = (source.key, staleness_h)
    key_tgt = (target.key, staleness_h)
    if key_src not in cache:
        cache[key_src] = pipeline.build_pairs(
            source, staleness_h, args.reject_hz, gs, args.carrier_hz
        )
    if key_tgt not in cache:
        cache[key_tgt] = pipeline.build_pairs(
            target, staleness_h, args.reject_hz, gs, args.carrier_hz
        )
    src_acc, src_rej, src_stats = cache[key_src]
    tgt_acc, tgt_rej, tgt_stats = cache[key_tgt]

    t_tr_s, t_va_s = pipeline.split_boundaries(source)
    t_tr_t, t_va_t = pipeline.split_boundaries(target)
    src_train, _, _ = pipeline.split_pairs(src_acc, t_tr_s, t_va_s)
    _, tgt_val, tgt_test = pipeline.split_pairs(tgt_acc, t_tr_t, t_va_t)

    rej_src = _split_rejected(src_rej, t_tr_s, t_va_s)
    rej_tgt = _split_rejected(tgt_rej, t_tr_t, t_va_t)

    row: dict[str, Any] = {
        "cell": f"{source.key}->{target.key}",
        "source_satellite": source.key,
        "source_name": source.name,
        "target_satellite": target.key,
        "target_name": target.name,
        "relation": (
            "target_specific" if source.key == target.key else "cross_satellite"
        ),
        "staleness_h": staleness_h,
        "reject_hz": args.reject_hz,
        "gamma": args.gamma,
        "f_tol_hz": args.f_tol_hz,
        "n_train_pairs": len(src_train),
        "n_validation_pairs": len(tgt_val),
        "n_test_pairs": len(tgt_test),
        "rejected_train_pairs": rej_src["train"],
        "rejected_validation_pairs": rej_tgt["validation"],
        "rejected_test_pairs": rej_tgt["test"],
        "reject_rate_source_pct": src_stats["reject_rate_pct"],
        "reject_rate_target_pct": tgt_stats["reject_rate_pct"],
    }

    if (
        len(src_train) < pipeline.MIN_TRAIN_PAIRS
        or len(tgt_val) < pipeline.MIN_VAL_PAIRS
        or len(tgt_test) < pipeline.MIN_TEST_PAIRS
    ):
        row.update({"status": "insufficient_pairs", "gate_decision": "unavailable"})
        return row

    x_tr, y_tr = pipeline.stack(src_train)
    x_va, y_va = pipeline.stack(tgt_val)
    models = pipeline.fit_correctors(x_tr, y_tr, x_va, y_va)

    val_agg = {
        name: pipeline.aggregate_pair_metrics(tgt_val, models[name], args.f_tol_hz)
        for name in pipeline.REFERENCE_MODELS + pipeline.LEARNED_MODELS
    }
    selected = min(pipeline.LEARNED_MODELS, key=lambda n: val_agg[n]["mae"])
    gates = pipeline.evaluate_gates(val_agg["zero"], val_agg[selected], args)
    gate = gates[args.primary_gate]

    test_agg = {
        name: pipeline.aggregate_pair_metrics(tgt_test, models[name], args.f_tol_hz)
        for name in pipeline.REFERENCE_MODELS + pipeline.LEARNED_MODELS
    }
    stats = pipeline.paired_pair_level_test(
        tgt_test,
        models["zero"],
        models[selected],
        args.f_tol_hz,
        args.n_boot,
        args.seed,
    )
    deltas = _per_pair_delta(
        tgt_test, models["zero"], models[selected], args.f_tol_hz
    )

    base_mae, ml_mae = test_agg["zero"]["mae"], test_agg[selected]["mae"]
    row.update(
        {
            "status": "evaluated",
            "selected_model": selected,
            "ridge_alpha": models["_alphas"].get(selected),
            "val_sgp4_mae_hz": round(val_agg["zero"]["mae"], 6),
            "val_learned_mae_hz": round(val_agg[selected]["mae"], 6),
            "val_degradation_pct": round(
                (val_agg[selected]["mae"] / val_agg["zero"]["mae"] - 1.0) * 100.0, 4
            )
            if val_agg["zero"]["mae"] > 0
            else None,
            "gate_decision": gate,
            **{f"gate_{g}": gates[g] for g in pipeline.GATE_OBJECTIVES},
            "test_sgp4_mae_hz": round(base_mae, 6),
            "test_learned_mae_hz": round(ml_mae, 6),
            "test_delta_mae_hz": round(ml_mae - base_mae, 6),
            "test_degradation_pct": round((ml_mae / base_mae - 1.0) * 100.0, 4)
            if base_mae > 0
            else None,
            "deployed_test_mae_hz": round(
                ml_mae if gate == "open" else base_mae, 6
            ),
            "n_unique_test_pair_ids": len({p["pair_id"] for p in tgt_test}),
            "learned_wins": stats["pair_wins_learned"],
            "sgp4_wins": stats["pair_losses_learned"],
            "ties": stats["pair_ties"],
            "learned_pair_win_rate": stats["pair_win_rate"],
            "median_pair_delta_mae_hz": round(float(np.median(deltas)), 6),
            "mean_pair_delta_mae_hz": stats["mean_pair_mae_delta_hz"],
            "boot_ci_low_hz": stats["boot_ci_low_hz"],
            "boot_ci_high_hz": stats["boot_ci_high_hz"],
            "sign_test_p": stats["sign_test_p"],
            "test_sgp4_p95_hz": round(test_agg["zero"]["p95"], 6),
            "test_learned_p95_hz": round(test_agg[selected]["p95"], 6),
            "test_sgp4_p99_hz": round(test_agg["zero"]["p99"], 6),
            "test_learned_p99_hz": round(test_agg[selected]["p99"], 6),
            "test_sgp4_outage_proxy": round(test_agg["zero"]["outage"], 6),
            "test_learned_outage_proxy": round(test_agg[selected]["outage"], 6),
        }
    )
    for name in pipeline.REFERENCE_MODELS + pipeline.LEARNED_MODELS:
        row[f"val_mae_{name}"] = round(val_agg[name]["mae"], 6)
        row[f"test_mae_{name}"] = round(test_agg[name]["mae"], 6)

    row["_pairs"] = {
        "train_ids": [p["pair_id"] for p in src_train],
        "val_ids": [p["pair_id"] for p in tgt_val],
        "test_ids": [p["pair_id"] for p in tgt_test],
        "test_satellites": {p["satellite"] for p in tgt_test},
        "val_satellites": {p["satellite"] for p in tgt_val},
        "deltas": deltas,
    }
    return row


def check_integrity(rows: list[dict[str, Any]], sats: dict[int, Any]) -> list[str]:
    """Hard invariants. Any failure aborts before conclusions are drawn."""
    problems: list[str] = []
    for row in rows:
        if row["status"] != "evaluated":
            continue
        tag = f"{row['cell']}@{row['staleness_h']}h"
        p = row["_pairs"]
        test_ids, val_ids, train_ids = p["test_ids"], p["val_ids"], p["train_ids"]

        if len(test_ids) != len(set(test_ids)):
            problems.append(f"{tag}: duplicate test pair_id")
        if len(val_ids) != len(set(val_ids)):
            problems.append(f"{tag}: duplicate validation pair_id")
        if set(val_ids) & set(test_ids):
            problems.append(f"{tag}: validation/test pair overlap")
        if set(train_ids) & set(test_ids):
            problems.append(f"{tag}: train/test pair overlap")
        if set(train_ids) & set(val_ids):
            problems.append(f"{tag}: train/validation pair overlap")
        if row["n_unique_test_pair_ids"] != len(set(test_ids)):
            problems.append(f"{tag}: unique test pair count mismatch")

        n_stat = row["learned_wins"] + row["sgp4_wins"] + row["ties"]
        if n_stat != len(set(test_ids)):
            problems.append(
                f"{tag}: sign-test N={n_stat} != unique test pairs "
                f"{len(set(test_ids))}"
            )
        if len(p["deltas"]) != len(set(test_ids)):
            problems.append(f"{tag}: bootstrap unit is not the pair")

        if p["test_satellites"] != {row["target_satellite"]}:
            problems.append(f"{tag}: test pairs not drawn from target")
        if p["val_satellites"] != {row["target_satellite"]}:
            problems.append(f"{tag}: validation pairs not drawn from target")

        # G must be reproducible from validation alone.
        base, cand = row["val_sgp4_mae_hz"], row["val_learned_mae_hz"]
        expected = "closed"
        if base > 0 and cand < row["gamma"] * base:
            expected = "open"
        if row["gate_mae"] != expected:
            problems.append(f"{tag}: MAE gate not reproducible from validation")

    for norad, sat in sats.items():
        if sat.ingestion_audit.get("tle_used_for_science"):
            problems.append(f"NORAD {norad}: TLE archive used as science input")
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tle-dir", type=Path, default=ROOT / "dataraw" / "spacetrack")
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
    parser.add_argument("--out-dir", type=Path, default=HERE / "phase0_black_kite")
    args = parser.parse_args(argv)

    all_sats = {s.norad: s for s in pipeline.discover_satellites(args.tle_dir)}
    missing = [n for n in (BK1, BK2) if n not in all_sats]
    if missing:
        print(f"ABORT: no canonical history for NORAD {missing}", file=sys.stderr)
        return 2
    sats = {n: all_sats[n] for n in (BK1, BK2)}

    cache: dict = {}
    rows = [
        evaluate_phase0_cell(sats[src], sats[tgt], band, args, cache)
        for src, tgt in CELLS
        for band in args.staleness
    ]

    problems = check_integrity(rows, sats)
    if problems:
        print("INTEGRITY FAILURE -- no scientific conclusion emitted:", file=sys.stderr)
        for item in problems:
            print(f"  - {item}", file=sys.stderr)
        return 3

    args.out_dir.mkdir(parents=True, exist_ok=True)
    pair_rows, gate_rows = [], []
    for row in rows:
        pairs = row.pop("_pairs", None)
        if row["status"] != "evaluated":
            continue
        pair_rows.append({k: row[k] for k in PAIR_HEADER if k in row})
        gate_rows.append({k: row[k] for k in GATE_HEADER if k in row})
        row["_deltas"] = pairs["deltas"] if pairs else None

    deltas_by_cell = {
        f"{r['cell']}|{r['staleness_h']}": (
            r.pop("_deltas").tolist() if r.get("_deltas") is not None else []
        )
        for r in rows
        if r["status"] == "evaluated"
    }

    _write(args.out_dir / "phase0_results.csv", rows, RESULT_HEADER)
    _write(args.out_dir / "phase0_pair_statistics.csv", pair_rows, PAIR_HEADER)
    _write(args.out_dir / "phase0_gate_diagnostics.csv", gate_rows, GATE_HEADER)
    (args.out_dir / "phase0_results.json").write_text(
        json.dumps(
            {
                "metadata": {
                    "campaign": "paper1_plus_phase0_black_kite",
                    "purpose": (
                        "re-derive the frozen Paper 1 objects under the unified "
                        "leakage-free pair-level protocol"
                    ),
                    "cells": [f"NORAD{a}->NORAD{b}" for a, b in CELLS],
                    "reference_is_measured_truth": False,
                    "hardware_used": False,
                    "rf_used": False,
                    "canonical_input": "GP_HISTORY JSON only; TLE archival only",
                    "gate_protocol": (
                        "source train fits; target validation selects and decides G; "
                        "target test reports consequences only"
                    ),
                    "legacy_cross_transfer_superseded": (
                        "old BK1->BK2 values (73.7/275.1/18.1 %) used a different "
                        "reject threshold, features, pairing, and test-based "
                        "selection; they are NOT comparable and are not reused"
                    ),
                    "integrity_checks_passed": True,
                    "gamma": args.gamma,
                    "reject_hz": args.reject_hz,
                    "f_tol_hz": args.f_tol_hz,
                    "n_boot": args.n_boot,
                    "seed": args.seed,
                },
                "satellites": {
                    str(n): {
                        "key": s.key,
                        "name": s.name,
                        "canonical_records": s.n_records,
                        "epoch_start": s.epochs()[0].isoformat(),
                        "epoch_end": s.epochs()[-1].isoformat(),
                        **s.gap_stats_h(),
                        **s.ingestion_audit,
                    }
                    for n, s in sats.items()
                },
                "rows": rows,
                "per_pair_delta_mae_hz": deltas_by_cell,
            },
            indent=2,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Phase-0 complete: {len(rows)} cells, integrity checks passed.")
    for row in rows:
        if row["status"] != "evaluated":
            print(f"  {row['cell']:26} {row['staleness_h']:>4}h  {row['status']}")
            continue
        print(
            f"  {row['cell']:26} {row['staleness_h']:>4}h "
            f"gate={row['gate_decision']:<6} "
            f"dMAE={row['test_delta_mae_hz']:+9.4f}Hz "
            f"deg={row['test_degradation_pct']:+8.2f}% "
            f"win={row['learned_pair_win_rate']:.3f} "
            f"p={row['sign_test_p']:.3g}"
        )
    return 0


def _write(path: Path, rows, header) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


RESULT_HEADER = [
    "cell", "source_satellite", "source_name", "target_satellite", "target_name",
    "relation", "staleness_h", "status", "reject_hz", "gamma", "f_tol_hz",
    "n_train_pairs", "n_validation_pairs", "n_test_pairs",
    "rejected_train_pairs", "rejected_validation_pairs", "rejected_test_pairs",
    "reject_rate_source_pct", "reject_rate_target_pct",
    "selected_model", "ridge_alpha",
    "val_sgp4_mae_hz", "val_learned_mae_hz", "val_degradation_pct", "gate_decision",
    "test_sgp4_mae_hz", "test_learned_mae_hz", "test_delta_mae_hz",
    "test_degradation_pct", "deployed_test_mae_hz",
]

PAIR_HEADER = [
    "cell", "staleness_h", "n_unique_test_pair_ids",
    "learned_wins", "sgp4_wins", "ties", "learned_pair_win_rate",
    "median_pair_delta_mae_hz", "mean_pair_delta_mae_hz",
    "boot_ci_low_hz", "boot_ci_high_hz", "sign_test_p",
]

GATE_HEADER = [
    "cell", "staleness_h", "selected_model", "gate_decision",
    "gate_mae", "gate_p95", "gate_p99", "gate_outage", "gate_guard_cost",
    "val_sgp4_mae_hz", "val_learned_mae_hz",
    "test_sgp4_p95_hz", "test_learned_p95_hz",
    "test_sgp4_p99_hz", "test_learned_p99_hz",
    "test_sgp4_outage_proxy", "test_learned_outage_proxy",
]


if __name__ == "__main__":
    sys.exit(main())
