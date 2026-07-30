#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "sgp4>=2.23", "matplotlib>=3.8", "pyyaml>=6"]
# ///
"""Dataset qualification gate for the Paper 1+ generalization campaign.

Answers one question and nothing else: **is the acquired archive good enough to
run generalization science on?** It computes no model, fits nothing, and makes
no scientific claim.

Qualification rule (not weakened silently -- change it here and the report says
so):

  1. >= MIN_SATELLITES real satellites usable
  2. >= MIN_REGIMES distinct orbital regimes represented
  3. every retained satellite has meaningful chronological train/val/test pair
     support in >= MIN_BANDS staleness bands

Regimes are derived from the ingested elements (altitude x inclination bands),
not from the catalog's intent, so a slot that resolved to the wrong object
cannot inflate the regime count.

reference_is_measured_truth = false throughout. No hardware, RF, packet,
error-rate, receiver-acknowledgement, over-the-air, or on-orbit content.

Run:
  uv run experiments/exp14_multisat_generalization_matrix/qualify_dataset.py \
      --tle-dir dataraw/spacetrack
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

# Phase-0 continuity: the two frozen-Paper-1 objects must both be re-derivable
# under the unified protocol before any continuity claim. Identifiers come from
# the committed BLACK KITE inventory; they are never guessed or substituted.
BLACK_KITE_NORAD = (66741, 68474)

MIN_SATELLITES = 6
MIN_REGIMES = 3
MIN_BANDS_PER_SATELLITE = 2
MIN_PAIRS_PER_SPLIT = 3

ALTITUDE_BANDS = ((300, 500), (500, 700), (700, 900), (900, 1400))
INCLINATION_BANDS = ((0, 60), (60, 90), (90, 100), (100, 145))

QUAL_HEADER = [
    "satellite_key",
    "satellite_name",
    "norad_id",
    "constellation_family",
    "regime",
    "records",
    "epoch_start_utc",
    "epoch_end_utc",
    "epoch_span_days",
    "median_gap_h",
    "p10_gap_h",
    "p90_gap_h",
    "mean_altitude_km",
    "min_altitude_km",
    "max_altitude_km",
    "mean_inclination_deg",
    "mean_eccentricity",
    "min_eccentricity",
    "max_eccentricity",
    "mean_bstar",
    "min_bstar",
    "max_bstar",
    "staleness_h",
    "accepted_pairs",
    "rejected_pairs",
    "reject_rate_pct",
    "train_pairs",
    "val_pairs",
    "test_pairs",
    "band_supported",
]


def _band_label(value: float, bands) -> str:
    for lo, hi in bands:
        if lo <= value < hi:
            return f"{lo}-{hi}"
    return "out_of_range"


def regime_of(orbit: dict[str, Any]) -> str:
    """Regime derived from ingested elements, never from catalog intent."""
    if not orbit:
        return "unknown"
    alt = _band_label(orbit.get("mean_altitude_km", -1), ALTITUDE_BANDS)
    inc = _band_label(orbit.get("mean_inclination_deg", -1), INCLINATION_BANDS)
    return f"alt{alt}km_inc{inc}deg"


def qualify(sats, args) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    gs = (args.gs_lat, args.gs_lon, args.gs_alt)
    rows: list[dict[str, Any]] = []
    per_sat: dict[str, dict[str, Any]] = {}

    for sat in sats:
        orbit = sat.orbit_stats()
        gaps = sat.gap_stats_h()
        regime = regime_of(orbit)
        epochs = sat.epochs()
        t_tr, t_va = pipeline.split_boundaries(sat)
        supported_bands = []
        for band in args.staleness:
            accepted, rejected, stats = pipeline.build_pairs(
                sat, band, args.reject_hz, gs, args.carrier_hz
            )
            tr, va, te = pipeline.split_pairs(accepted, t_tr, t_va)
            ok = (
                len(tr) >= MIN_PAIRS_PER_SPLIT
                and len(va) >= MIN_PAIRS_PER_SPLIT
                and len(te) >= MIN_PAIRS_PER_SPLIT
            )
            if ok:
                supported_bands.append(band)
            rows.append(
                {
                    "satellite_key": sat.key,
                    "satellite_name": sat.name,
                    "norad_id": sat.norad,
                    "constellation_family": args.family_hint.get(
                        str(sat.norad), "unknown"
                    ),
                    "regime": regime,
                    "records": sat.n_records,
                    "epoch_start_utc": epochs[0].isoformat(),
                    "epoch_end_utc": epochs[-1].isoformat(),
                    "epoch_span_days": round(
                        (epochs[-1] - epochs[0]).total_seconds() / 86400.0, 3
                    ),
                    "median_gap_h": gaps["median_gap_h"],
                    "p10_gap_h": gaps["p10_gap_h"],
                    "p90_gap_h": gaps["p90_gap_h"],
                    **{k: orbit.get(k) for k in QUAL_HEADER[12:22]},
                    "staleness_h": band,
                    "accepted_pairs": stats["accepted_pairs"],
                    "rejected_pairs": stats["rejected_pairs"],
                    "reject_rate_pct": stats["reject_rate_pct"],
                    "train_pairs": len(tr),
                    "val_pairs": len(va),
                    "test_pairs": len(te),
                    "band_supported": ok,
                }
            )
        per_sat[sat.key] = {
            "satellite_key": sat.key,
            "satellite_name": sat.name,
            "norad_id": sat.norad,
            "regime": regime,
            "supported_bands": supported_bands,
            "n_supported_bands": len(supported_bands),
            "retained": len(supported_bands) >= MIN_BANDS_PER_SATELLITE,
        }

    return rows, evaluate_qualification(per_sat)


def evaluate_qualification(per_sat: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Apply the preregistered qualification rule to per-satellite results.

    Preregistered rule:
      retained = satellites supporting >= MIN_BANDS_PER_SATELLITE staleness
                 bands, where a band counts only with >= MIN_PAIRS_PER_SPLIT
                 train AND validation AND test pairs
      qualified = len(retained) >= MIN_SATELLITES
                  AND distinct regimes among RETAINED >= MIN_REGIMES

    A satellite that fails the per-satellite rule is simply not retained. It
    does NOT fail the dataset -- dropping weak candidates is the intended
    behaviour of a retention rule. Requiring every ingested satellite to be
    retained would be stricter than the preregistration.
    """
    retained = [s for s in per_sat.values() if s["retained"]]
    dropped = [s for s in per_sat.values() if not s["retained"]]
    regimes = sorted({s["regime"] for s in retained})
    checks = {
        "min_satellites": {
            "required": MIN_SATELLITES,
            "observed": len(retained),
            "pass": len(retained) >= MIN_SATELLITES,
        },
        "min_regimes": {
            "required": MIN_REGIMES,
            "observed": len(regimes),
            "regimes": regimes,
            "pass": len(regimes) >= MIN_REGIMES,
        },
        "retention_rule_applied": {
            "required_bands_per_satellite": MIN_BANDS_PER_SATELLITE,
            "min_pairs_per_split": MIN_PAIRS_PER_SPLIT,
            "satellites_ingested": len(per_sat),
            "satellites_retained": len(retained),
            "satellites_dropped": len(dropped),
            "dropped_keys": sorted(s["satellite_key"] for s in dropped),
            # Invariant, not a dataset gate: nothing below the per-satellite
            # band rule may ever enter the retained set.
            "pass": all(
                s["n_supported_bands"] >= MIN_BANDS_PER_SATELLITE for s in retained
            ),
        },
    }
    return {
        "qualified": all(c["pass"] for c in checks.values()) and bool(retained),
        "checks": checks,
        "retained_keys": sorted(s["satellite_key"] for s in retained),
        "per_satellite": list(per_sat.values()),
        "thresholds_note": (
            "Thresholds are fixed in qualify_dataset.py "
            f"(MIN_SATELLITES={MIN_SATELLITES}, MIN_REGIMES={MIN_REGIMES}, "
            f"MIN_BANDS_PER_SATELLITE={MIN_BANDS_PER_SATELLITE}, "
            f"MIN_PAIRS_PER_SPLIT={MIN_PAIRS_PER_SPLIT}). "
            "They were not relaxed to obtain this verdict."
        ),
        "reference_is_measured_truth": False,
    }


def black_kite_continuity(per_sat: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Phase-0 continuity, reported SEPARATELY from dataset qualification.

    A qualifying heterogeneous dataset says nothing about whether the frozen
    Paper 1 objects can be re-derived; merging the two into one PASS/FAIL would
    hide exactly the fact that matters.
    """
    objects = {}
    for norad in BLACK_KITE_NORAD:
        entry = per_sat.get(f"NORAD{norad}")
        objects[str(norad)] = {
            "norad_id": norad,
            "canonical_history_available": entry is not None,
            "supported_bands": entry["supported_bands"] if entry else [],
            "n_supported_bands": entry["n_supported_bands"] if entry else 0,
            "sufficient_for_phase0": bool(entry and entry["retained"]),
        }
    both = all(o["sufficient_for_phase0"] for o in objects.values())
    missing = [k for k, o in objects.items() if not o["canonical_history_available"]]
    return {
        "continuity_qualified": both,
        "objects": objects,
        "missing_norad_ids": missing,
        "blocking_reason": (
            ""
            if both
            else (
                f"no canonical history for NORAD {', '.join(missing)}"
                if missing
                else "history present but insufficient band support"
            )
        ),
        "note": (
            "Phase-0 requires BK1->BK1, BK2->BK2, BK1->BK2 and BK2->BK1 to be "
            "re-derived under the unified protocol before any Paper 1+ claim. "
            "No substitute satellite may be used."
        ),
    }


def coverage_figure(rows, verdict, out_dir: Path) -> list[Path]:
    """Coverage figure. Emitted only when at least one satellite was ingested."""
    if not rows:
        return []
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    sats = sorted({r["satellite_key"] for r in rows})
    bands = sorted({int(r["staleness_h"]) for r in rows})
    grid = np.full((len(sats), len(bands)), np.nan)
    supported = np.zeros((len(sats), len(bands)), dtype=bool)
    for row in rows:
        i, j = sats.index(row["satellite_key"]), bands.index(int(row["staleness_h"]))
        grid[i, j] = row["accepted_pairs"]
        supported[i, j] = bool(row["band_supported"])

    fig, axes = plt.subplots(
        1, 2, figsize=(6.2 + 0.5 * len(bands), 1.6 + 0.45 * len(sats)),
        gridspec_kw={"width_ratios": [1.5, 1.0]},
    )
    ax = axes[0]
    im = ax.imshow(grid, cmap="YlGnBu", aspect="auto")
    ax.set_xticks(range(len(bands)))
    ax.set_xticklabels([f"{b} h" for b in bands], fontsize=7)
    ax.set_yticks(range(len(sats)))
    ax.set_yticklabels(sats, fontsize=7)
    for i in range(len(sats)):
        for j in range(len(bands)):
            val = "n/a" if np.isnan(grid[i, j]) else f"{int(grid[i, j])}"
            ax.text(j, i, val, ha="center", va="center", fontsize=6,
                    color="black" if supported[i, j] else "#B23A3A")
            if supported[i, j]:
                ax.add_patch(
                    plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False,
                                  edgecolor="#2E7D32", lw=1.4)
                )
    ax.set_title(
        "(a) accepted TLE pairs per staleness band\n"
        "green box = train/val/test all supported; red text = unsupported",
        fontsize=8,
    )
    fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)

    ax = axes[1]
    seen: dict[str, tuple[list, list]] = {}
    for row in rows:
        alt, inc = row.get("mean_altitude_km"), row.get("mean_inclination_deg")
        if alt is None or inc is None:
            continue
        xs, ys = seen.setdefault(row["regime"], ([], []))
        xs.append(inc)
        ys.append(alt)
    for regime, (xs, ys) in sorted(seen.items()):
        ax.scatter(xs, ys, s=22, label=regime, alpha=0.8)
    for lo, hi in ALTITUDE_BANDS:
        ax.axhline(lo, color="#C8CDD4", lw=0.6, ls=":")
    ax.set_xlabel("inclination [deg]", fontsize=8)
    ax.set_ylabel("mean altitude [km]", fontsize=8)
    ax.set_title("(b) regime coverage", fontsize=8)
    ax.legend(fontsize=5, frameon=False)
    ax.grid(True, ls=":", alpha=0.3)

    status = "QUALIFIED" if verdict["qualified"] else "NOT QUALIFIED"
    fig.suptitle(
        f"Paper 1+ dataset coverage -- {status} "
        f"({verdict['checks']['min_satellites']['observed']} retained / "
        f"{verdict['checks']['min_satellites']['required']} required, "
        f"{verdict['checks']['min_regimes']['observed']} regimes / "
        f"{verdict['checks']['min_regimes']['required']} required)",
        fontsize=9,
    )
    fig.text(
        0.5, -0.02,
        "Software-only orbital metadata (reference_is_measured_truth = false); "
        "not measured RF truth.",
        ha="center", fontsize=6, color="#666666",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    written = []
    for ext in ("pdf", "png"):
        path = out_dir / f"fig_dataset_coverage.{ext}"
        fig.savefig(path, bbox_inches="tight", dpi=200 if ext == "png" else None)
        written.append(path)
    plt.close(fig)
    return written


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
    parser.add_argument("--family-hint-json", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=HERE)
    args = parser.parse_args(argv)
    args.family_hint = (
        json.loads(args.family_hint_json.read_text(encoding="utf-8"))
        if args.family_hint_json and args.family_hint_json.exists()
        else {}
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    sats = pipeline.discover_satellites(args.tle_dir)
    rows, verdict = qualify(sats, args)
    verdict["tle_dir"] = str(args.tle_dir)
    verdict["satellites_ingested"] = len(sats)
    per_sat = {s["satellite_key"]: s for s in verdict["per_satellite"]}
    verdict["black_kite_continuity"] = black_kite_continuity(per_sat)
    verdict["ingestion_audit"] = pipeline.ingestion_audit_rows(sats, args.tle_dir)

    with (args.out_dir / "ingestion_audit.csv").open(
        "w", newline="", encoding="utf-8"
    ) as fh:
        writer = csv.DictWriter(
            fh, fieldnames=pipeline.INGESTION_AUDIT_HEADER, extrasaction="ignore"
        )
        writer.writeheader()
        for row in verdict["ingestion_audit"]:
            writer.writerow(row)

    with (args.out_dir / "dataset_qualification.csv").open(
        "w", newline="", encoding="utf-8"
    ) as fh:
        writer = csv.DictWriter(fh, fieldnames=QUAL_HEADER, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    (args.out_dir / "dataset_qualification.json").write_text(
        json.dumps(verdict, indent=2, default=str) + "\n", encoding="utf-8"
    )

    figures = coverage_figure(rows, verdict, args.out_dir)
    for path in figures:
        print(f"wrote {path}")
    if not figures:
        print(
            "no coverage figure emitted: zero satellites ingested. "
            "An empty figure would misrepresent the dataset."
        )

    continuity = verdict["black_kite_continuity"]
    print()
    print("A. HETEROGENEOUS DATASET QUALIFICATION")
    print(
        f"   retained satellites : "
        f"{verdict['checks']['min_satellites']['observed']} / {MIN_SATELLITES}"
    )
    print(f"   retained regimes    : {verdict['checks']['min_regimes']['observed']}"
          f" / {MIN_REGIMES}")
    print(f"   dropped satellites  : "
          f"{verdict['checks']['retention_rule_applied']['dropped_keys']}")
    print()
    print("B. PAPER-1 CONTINUITY (BLACK KITE)")
    for norad, obj in continuity["objects"].items():
        print(f"   NORAD {norad}: history={obj['canonical_history_available']} "
              f"bands={obj['n_supported_bands']} "
              f"phase0_ready={obj['sufficient_for_phase0']}")
    if not continuity["continuity_qualified"]:
        print(f"   blocking reason     : {continuity['blocking_reason']}")
    print()

    if not verdict["qualified"]:
        print("DATASET NOT QUALIFIED")
        for name, check in verdict["checks"].items():
            if not check["pass"]:
                print(f"  - {name}: {check}")
        return 1
    if continuity["continuity_qualified"]:
        print("DATASET QUALIFIED - BLACK KITE CONTINUITY QUALIFIED")
    else:
        print("DATASET QUALIFIED - BLACK KITE CONTINUITY BLOCKED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
