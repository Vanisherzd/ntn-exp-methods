#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "sgp4>=2.23"]
# ///
"""Unified multi-satellite inter-TLE residual generalization pipeline (Paper 1+).

Research question
-----------------
When does model-derived inter-TLE residual structure generalize across LEO
satellites, and can a validation-gated endpoint policy safely refuse residual
learning under satellite/domain shift?

Unified protocol (Phase 0) -- identical for every cell
------------------------------------------------------
  target-specific A->A :  train_A -> validation_A -> test_A
  transfer        A->B :  train_A -> validation_B -> test_B

The TARGET validation segment selects the candidate and computes every gate.
The TARGET test segment reports consequences only: it never selects a model and
never decides G. Pairing rule, feature schema, reject threshold, staleness
bands, ground station, carrier, sampling schedule, candidate set and validation
logic are shared by all cells by construction -- there is one code path.

Pair-level data model (Phase 2)
-------------------------------
The independent experimental unit is the accepted TLE pair, never the 24 in-pass
samples. Pair identity is preserved in every export.

Claim boundary
--------------
reference_is_measured_truth = false. The "reference" Doppler is the SGP4
propagation of a later TLE for the same object, not an RF measurement. No
packet, error-rate, receiver-acknowledgement, over-the-air, or on-orbit result
is produced or implied.

Run:
  uv run experiments/exp14_multisat_generalization_matrix/\
run_multisat_generalization_matrix.py --tle-dir dataraw/spacetrack
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import itertools
import json
import math
import os
import statistics
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import numpy as np
from sgp4.api import Satrec, jday

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

C_LIGHT = 299_792_458.0
WGS84_A = 6_378_137.0
WGS84_E2 = 0.006694379990141317
OMEGA_EARTH = 7.292115e-5
MU_EARTH_KM3_S2 = 398_600.4418

K_SAMPLES_PER_PAIR = 24
PERIOD_SAMPLE_S = 5_700.0

TRAIN_FRAC = 0.60
VAL_FRAC = 0.20

MIN_TRAIN_PAIRS = 3
MIN_VAL_PAIRS = 3
MIN_TEST_PAIRS = 3

# (target_h, min_gap_h, max_gap_h) -- shared by every cell.
STALENESS_BANDS: dict[int, tuple[float, float]] = {
    8: (4, 14),
    24: (16, 36),
    48: (36, 60),
    72: (60, 84),
    96: (84, 120),
    168: (144, 192),
}

# Constant-offset references. Never eligible to open a gate: a constant bias is
# not a learned residual correction (same rule as Paper 1).
REFERENCE_MODELS = ("zero", "mean_bias", "median_bias")
# Fitted correctors. The validation-best of these is the gated candidate.
LEARNED_MODELS = ("linear_bias_rate", "stale_age_ridge", "ridge")

RIDGE_ALPHAS = (1e-2, 1e-1, 1.0, 1e1, 1e2, 1e3)

GATE_OBJECTIVES = ("mae", "p95", "p99", "outage", "guard_cost")

FEATURE_NAMES = (
    "t_age_s",
    "t_gap_s",
    "stale_doppler_hz",
    "sin_phase",
    "cos_phase",
    "elevation_deg",
    "range_km",
    "stale_mean_motion_rad_min",
    "stale_bstar",
    "stale_ecc",
)
# Feature indices used by the deliberately restricted stale-age-only corrector.
STALE_AGE_FEATURES = (0, 1)

WIN_TOLERANCE_HZ = 1e-9

# Above this many trials, 2.0**trials overflows a double; switch to log space.
EXACT_BINOM_MAX = 1000


# --------------------------------------------------------------------------
# TLE ingestion (Phase 1)
# --------------------------------------------------------------------------


@dataclass
class SatelliteData:
    """One satellite's normalized TLE history."""

    key: str
    name: str
    norad: int
    source_path: str
    records: list[dict[str, Any]] = field(repr=False, default_factory=list)
    ingestion_audit: dict[str, Any] = field(repr=False, default_factory=dict)

    @property
    def n_records(self) -> int:
        return len(self.records)

    def epochs(self) -> list[dt.datetime]:
        return [r["epoch"] for r in self.records]

    def gaps_h(self) -> list[float]:
        eps = self.epochs()
        return [
            (b - a).total_seconds() / 3600.0 for a, b in zip(eps[:-1], eps[1:])
        ]

    def gap_stats_h(self) -> dict[str, float | None]:
        gaps = sorted(self.gaps_h())
        if not gaps:
            return {
                "median_gap_h": None,
                "mean_gap_h": None,
                "p10_gap_h": None,
                "p90_gap_h": None,
                "max_gap_h": None,
            }
        return {
            "median_gap_h": round(statistics.median(gaps), 3),
            "mean_gap_h": round(statistics.fmean(gaps), 3),
            "p10_gap_h": round(gaps[int(0.10 * (len(gaps) - 1))], 3),
            "p90_gap_h": round(gaps[int(0.90 * (len(gaps) - 1))], 3),
            "max_gap_h": round(gaps[-1], 3),
        }

    def orbit_stats(self) -> dict[str, float | None]:
        """Altitude / inclination / eccentricity / B* summary for the manifest."""
        if not self.records:
            return {}

        def _summary(values: list[float]) -> tuple[float, float, float]:
            vals = sorted(values)
            return (
                round(statistics.fmean(vals), 6),
                round(vals[0], 6),
                round(vals[-1], 6),
            )

        alts, incs, eccs, bstars = [], [], [], []
        for rec in self.records:
            n_rad_s = rec["mean_motion_rad_min"] / 60.0
            if n_rad_s <= 0:
                continue
            semi_major_km = (MU_EARTH_KM3_S2 / (n_rad_s**2)) ** (1.0 / 3.0)
            alts.append(semi_major_km - WGS84_A / 1000.0)
            incs.append(math.degrees(rec["inclination_rad"]))
            eccs.append(rec["ecc"])
            bstars.append(rec["bstar"])
        if not alts:
            return {}
        alt_mean, alt_min, alt_max = _summary(alts)
        inc_mean, inc_min, inc_max = _summary(incs)
        ecc_mean, ecc_min, ecc_max = _summary(eccs)
        bs_mean, bs_min, bs_max = _summary(bstars)
        return {
            "mean_altitude_km": alt_mean,
            "min_altitude_km": alt_min,
            "max_altitude_km": alt_max,
            "mean_inclination_deg": inc_mean,
            "min_inclination_deg": inc_min,
            "max_inclination_deg": inc_max,
            "mean_eccentricity": ecc_mean,
            "min_eccentricity": ecc_min,
            "max_eccentricity": ecc_max,
            "mean_bstar": bs_mean,
            "min_bstar": bs_min,
            "max_bstar": bs_max,
        }


def _parse_epoch(value: str) -> dt.datetime:
    text = value.replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _satrec_epoch(sat: Satrec) -> dt.datetime:
    jd_total = sat.jdsatepoch + sat.jdsatepochF
    unix_s = (jd_total - 2_440_587.5) * 86400.0
    return dt.datetime.fromtimestamp(unix_s, tz=dt.timezone.utc)


def physical_element_key(line1: str, line2: str) -> str:
    """Identity of the *physical* orbit solution carried by a TLE line pair.

    Uses only the mean-element and drag columns: ndot / nddot / bstar /
    ephemeris type on line 1, and inclination / RAAN / eccentricity / argument
    of perigee / mean anomaly / mean motion on line 2. Element-set number,
    revolution number and the line checksums are deliberately excluded: they are
    publication bookkeeping, not orbit state, so two rows differing only in them
    describe the same solution.
    """
    return f"{line1[33:63]}|{line2[8:63]}"


def _normalize(line1: str, line2: str, name: str, epoch: str | None) -> dict | None:
    """Build one record, deriving mean elements from the TLE lines themselves.

    Deriving from Satrec (rather than Space-Track JSON columns) keeps JSON and
    three-line text sources on identical footing. Units differ from the
    Space-Track columns (rad, rad/min); every feature is standardized before
    fitting, so the fit is unaffected.
    """
    try:
        sat = Satrec.twoline2rv(line1, line2)
    except Exception:
        return None
    return {
        "epoch": _parse_epoch(epoch) if epoch else _satrec_epoch(sat),
        "line1": line1,
        "line2": line2,
        "name": name,
        "norad": int(sat.satnum),
        "mean_anomaly_rad": float(sat.mo),
        "mean_motion_rad_min": float(sat.no_kozai),
        "inclination_rad": float(sat.inclo),
        "bstar": float(sat.bstar),
        "ecc": float(sat.ecco),
        "physical_key": physical_element_key(line1, line2),
        "gp_id": None,
        "creation_date": None,
        "file": None,
    }


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _records_from_json(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(payload, dict):
        payload = payload.get("data") or payload.get("records") or []
    if not isinstance(payload, list):
        return []
    out = []
    for row in payload:
        if not isinstance(row, dict):
            continue
        line1 = row.get("TLE_LINE1") or row.get("tle_line1")
        line2 = row.get("TLE_LINE2") or row.get("tle_line2")
        if not line1 or not line2:
            continue
        rec = _normalize(
            line1,
            line2,
            str(row.get("OBJECT_NAME") or row.get("object_name") or path.stem),
            row.get("EPOCH") or row.get("epoch"),
        )
        if rec:
            rec["gp_id"] = _as_str(row.get("GP_ID"))
            rec["creation_date"] = _as_str(row.get("CREATION_DATE"))
            rec["file"] = _as_str(row.get("FILE"))
            out.append(rec)
    return out


def _records_from_text(path: Path) -> list[dict[str, Any]]:
    lines = [
        ln.rstrip()
        for ln in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    ]
    out: list[dict[str, Any]] = []
    i = 0
    name = path.stem
    while i < len(lines):
        if lines[i].startswith("1 ") and i + 1 < len(lines):
            rec = _normalize(lines[i], lines[i + 1], name, None)
            if rec:
                out.append(rec)
            i += 2
        elif i + 2 < len(lines) and lines[i + 1].startswith("1 "):
            name = lines[i].strip()
            rec = _normalize(lines[i + 1], lines[i + 2], name, None)
            if rec:
                out.append(rec)
            i += 3
        else:
            i += 1
    return out


def authoritative_name(archive_path: Path, norad: int) -> str | None:
    """OBJECT_NAME from the sibling satcat response, if one was preserved.

    gp_history records carry the OBJECT_NAME in force at each epoch, so a newly
    catalogued object reads "TBA - TO BE ASSIGNED" for its earliest records.
    The satcat response is the authoritative identity and is preferred.
    """
    satcat = archive_path.parent / f"satcat_{norad}.json"
    if not satcat.is_file():
        return None
    try:
        payload = json.loads(satcat.read_text(encoding="utf-8"))
    except Exception:
        return None
    rows = payload if isinstance(payload, list) else [payload]
    for row in rows:
        if isinstance(row, dict) and str(row.get("OBJECT_NAME", "")).strip():
            return str(row["OBJECT_NAME"]).strip()
    return None


EPOCH_QUANTUM_US = 1000  # 1 ms -- deterministic epoch normalization quantum


def normalize_epoch(when: dt.datetime) -> str:
    """Deterministic canonical epoch key.

    GP JSON carries EPOCH as a text field; a TLE line carries it as a packed
    float that round-trips through a Julian date. Both are quantized to 1 ms so
    the same physical element set produces the same key regardless of source.
    """
    aware = when.astimezone(dt.timezone.utc)
    micro = (aware.microsecond // EPOCH_QUANTUM_US) * EPOCH_QUANTUM_US
    return aware.replace(microsecond=micro).isoformat(timespec="milliseconds")


def element_id(norad: int, when: dt.datetime) -> str:
    """Stable identity of one GP element solution: NORAD + normalized epoch."""
    return f"{norad}|{normalize_epoch(when)}"


# --------------------------------------------------------------------------
# Same-epoch revision policy
# --------------------------------------------------------------------------
# Space-Track republishes an epoch when the orbit solution is re-fitted. Rows
# sharing (NORAD, normalized epoch) are therefore of two kinds:
#   * equivalent duplicates -- identical physical elements, differing only in
#     publication bookkeeping; these are collapsed;
#   * same-epoch revisions  -- genuinely different orbit solutions for one
#     epoch; one must be selected, and the selection rule is scientific.
#
# The canonical rule is EARLIEST-PUBLISHED: the first revision Space-Track
# released for that epoch, ordered by CREATION_DATE, then FILE, then GP_ID.
# The choice is an availability argument, not a performance one. A publication-
# time audit of the 884 conflicting groups in this archive found that the
# latest-published revision was created after the *next* element set's epoch in
# 237 groups, and later than the shortest admissible pairing gap (4 h) in 568;
# the earliest-published revision violates the same two conditions in 84 and 186
# groups. Selecting the last revision would therefore let a terminal use an
# orbit solution that did not exist when it had to transmit. Neither rule
# changes the recorded conclusions -- see the canonicalization sensitivity --
# so the causally admissible one is used.
SAME_EPOCH_POLICIES = ("earliest_published", "latest_published", "drop_conflicting")
SAME_EPOCH_POLICY = os.environ.get(
    "MULTISAT_SAME_EPOCH_POLICY", "earliest_published"
)
if SAME_EPOCH_POLICY not in SAME_EPOCH_POLICIES:
    raise SystemExit(f"unknown MULTISAT_SAME_EPOCH_POLICY: {SAME_EPOCH_POLICY}")


def _publication_order(rec: dict[str, Any]) -> tuple:
    """Sort key implementing CREATION_DATE, then FILE, then GP_ID.

    Missing metadata sorts first and is therefore preferred by the canonical
    earliest-published rule only when no dated row exists in the group.
    """
    created = rec.get("creation_date") or ""
    def _num(value: Any) -> tuple[int, float | str]:
        if value is None:
            return (0, "")
        try:
            return (1, float(value))
        except (TypeError, ValueError):
            return (1, str(value))
    return (created, _num(rec.get("file")), _num(rec.get("gp_id")))


def resolve_same_epoch_group(
    members: list[dict[str, Any]], policy: str = SAME_EPOCH_POLICY
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Reduce one (NORAD, normalized epoch) group to at most one record.

    Returns the retained record (or None when the group is dropped) together
    with a provenance dictionary describing how the group was resolved.
    """
    distinct = {m["physical_key"] for m in members}
    equivalent = len(distinct) == 1
    resolution = "equivalent_duplicate_collapse" if equivalent else "same_epoch_revision"

    if equivalent or policy == "earliest_published":
        chosen = min(members, key=_publication_order)
    elif policy == "latest_published":
        chosen = max(members, key=_publication_order)
    elif policy == "drop_conflicting":
        chosen = None
        resolution = "dropped_conflicting_epoch"
    else:                                        # pragma: no cover - guarded above
        raise ValueError(policy)

    provenance = {
        "same_epoch_rows": len(members),
        "distinct_physical_solutions": len(distinct),
        "resolution": resolution,
        "policy": policy,
    }
    if len(distinct) > 1:
        provenance["competing_gp_ids"] = [m.get("gp_id") for m in members]
    if chosen is not None:
        provenance.update({
            "gp_id": chosen.get("gp_id"),
            "creation_date": chosen.get("creation_date"),
            "file": chosen.get("file"),
        })
    return chosen, provenance


def _canonical_sources(tle_dir: Path) -> dict[int, dict[str, Any]]:
    """Group archive files per NORAD and choose ONE canonical science source.

    GP_HISTORY JSON is canonical whenever present. The TLE archive of the same
    object is an immutable provenance copy and is never ingested as an
    independent observation: it holds the same element history, so ingesting
    both doubles the record count and collapses the apparent update cadence
    toward zero.
    """
    groups: dict[int, dict[str, Any]] = {}
    for path in sorted(tle_dir.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix == ".json":
            if path.name.startswith(("satcat_", "fetch_manifest")):
                continue
            records, kind = _records_from_json(path), "json"
        elif suffix in {".txt", ".tle", ".3le"}:
            records, kind = _records_from_text(path), "tle"
        else:
            continue
        if not records:
            continue
        for norad in {r["norad"] for r in records}:
            own = [r for r in records if r["norad"] == norad]
            group = groups.setdefault(norad, {"json": [], "tle": []})
            group[kind].append({"path": path, "records": own})
    return groups


def discover_satellites(tle_dir: Path) -> list[SatelliteData]:
    """Build one canonical element sequence per satellite.

    Canonical input is GP_HISTORY JSON. Duplicate element solutions are removed
    by `element_id`; the TLE archive is counted for audit but excluded from the
    scientific sequence whenever a JSON history exists.
    """
    if not tle_dir.is_dir():
        return []
    usable: list[SatelliteData] = []
    for norad, group in _canonical_sources(tle_dir).items():
        chosen_kind = "json" if group["json"] else "tle"
        chosen = max(group[chosen_kind], key=lambda c: len(c["records"]))
        raw = sorted(chosen["records"], key=lambda r: r["epoch"])

        grouped: dict[str, list[dict[str, Any]]] = {}
        for rec in raw:
            grouped.setdefault(element_id(norad, rec["epoch"]), []).append(rec)

        canonical: list[dict[str, Any]] = []
        equivalent_collapsed = 0     # rows discarded as exact/equivalent duplicates
        revision_groups = 0          # epochs with >1 distinct physical solution
        revision_rows_discarded = 0
        dropped_epochs = 0
        for eid, members in grouped.items():
            keep, prov = resolve_same_epoch_group(members)
            extra = len(members) - 1
            if prov["distinct_physical_solutions"] > 1:
                revision_groups += 1
                if keep is None:
                    dropped_epochs += 1
                    continue
                revision_rows_discarded += extra
            else:
                equivalent_collapsed += extra
            keep["element_id"] = eid
            keep["source_path"] = str(chosen["path"])
            keep["revision_provenance"] = prov
            canonical.append(keep)
        canonical.sort(key=lambda r: r["epoch"])
        duplicates = equivalent_collapsed + revision_rows_discarded

        sat = SatelliteData(
            key=f"NORAD{norad}",
            name=canonical[0]["name"] if canonical else str(norad),
            norad=norad,
            source_path=str(chosen["path"].relative_to(tle_dir.parent)),
            records=canonical,
        )
        official = authoritative_name(chosen["path"], norad)
        if official:
            sat.name = official
        sat.ingestion_audit = {
            "canonical_source": chosen_kind,
            "canonical_source_path": sat.source_path,
            "raw_json_rows": sum(len(c["records"]) for c in group["json"]),
            "raw_tle_rows": sum(len(c["records"]) for c in group["tle"]),
            "raw_rows_from_canonical_source": len(raw),
            "duplicate_rows_in_canonical_source": duplicates,
            "canonical_unique_rows": len(canonical),
            "tle_used_for_science": chosen_kind == "tle",
            "same_epoch_policy": SAME_EPOCH_POLICY,
            "equivalent_duplicate_rows_collapsed": equivalent_collapsed,
            "same_epoch_revision_groups": revision_groups,
            "same_epoch_revision_rows_discarded": revision_rows_discarded,
            "conflicting_epochs_dropped": dropped_epochs,
        }
        if sat.n_records >= 2:
            usable.append(sat)
    return sorted(usable, key=lambda s: s.norad)


def legacy_ingestion_stats(tle_dir: Path) -> dict[int, dict[str, Any]]:
    """Reproduce the pre-repair (JSON+TLE both ingested) counts for audit only.

    This exists solely so the integrity report can state before/after numbers.
    It is never used as a scientific input.
    """
    out: dict[int, dict[str, Any]] = {}
    for norad, group in _canonical_sources(tle_dir).items():
        merged: list[dict[str, Any]] = []
        for kind in ("json", "tle"):
            for chunk in group[kind]:
                merged.extend(chunk["records"])
        merged.sort(key=lambda r: r["epoch"])
        seen, deduped = set(), []
        for rec in merged:
            stamp = rec["epoch"].isoformat()   # the old, precision-sensitive key
            if stamp in seen:
                continue
            seen.add(stamp)
            deduped.append(rec)
        gaps = sorted(
            (b["epoch"] - a["epoch"]).total_seconds() / 3600.0
            for a, b in zip(deduped[:-1], deduped[1:])
        )
        out[norad] = {
            "legacy_records": len(deduped),
            "legacy_median_gap_h": round(statistics.median(gaps), 3) if gaps else None,
        }
    return out


REVISION_MANIFEST_HEADER = (
    "satellite", "satellite_name", "norad_id", "element_id", "epoch_utc",
    "same_epoch_rows", "distinct_physical_solutions", "policy", "resolution",
    "chosen_gp_id", "chosen_creation_date", "chosen_file", "competing_gp_ids",
)


def revision_manifest_rows(sats: list["SatelliteData"]) -> list[dict[str, Any]]:
    """Every same-epoch group that needed a revision decision, and its outcome.

    Groups whose members were physically identical are not listed: collapsing
    them is provable from the elements themselves and needs no adjudication.
    Only the genuinely competing revisions are recorded, one row each, so the
    canonicalization can be re-checked without the raw archive.
    """
    rows: list[dict[str, Any]] = []
    for sat in sats:
        for rec in sat.records:
            prov = rec.get("revision_provenance") or {}
            if prov.get("distinct_physical_solutions", 1) <= 1:
                continue
            rows.append({
                "satellite": sat.key,
                "satellite_name": sat.name,
                "norad_id": sat.norad,
                "element_id": rec["element_id"],
                "epoch_utc": rec["epoch"].isoformat(),
                "same_epoch_rows": prov["same_epoch_rows"],
                "distinct_physical_solutions": prov["distinct_physical_solutions"],
                "policy": prov["policy"],
                "resolution": prov["resolution"],
                "chosen_gp_id": prov.get("gp_id"),
                "chosen_creation_date": prov.get("creation_date"),
                "chosen_file": prov.get("file"),
                "competing_gp_ids": ";".join(
                    sorted(str(g) for g in prov.get("competing_gp_ids", []))
                ),
            })
    return rows


def ingestion_audit_rows(
    sats: list[SatelliteData], tle_dir: Path
) -> list[dict[str, Any]]:
    """Task-1 audit table: what canonicalization removed, per satellite."""
    legacy = legacy_ingestion_stats(tle_dir)
    rows = []
    for sat in sats:
        audit = sat.ingestion_audit
        before = legacy.get(sat.norad, {})
        rows.append(
            {
                "satellite": sat.key,
                "satellite_name": sat.name,
                "norad_id": sat.norad,
                "canonical_source": audit.get("canonical_source"),
                "raw_json_rows": audit.get("raw_json_rows"),
                "duplicate_json_rows": audit.get(
                    "duplicate_rows_in_canonical_source"
                ),
                "same_epoch_policy": audit.get("same_epoch_policy"),
                "equivalent_duplicate_rows_collapsed": audit.get(
                    "equivalent_duplicate_rows_collapsed"
                ),
                "same_epoch_revision_groups": audit.get(
                    "same_epoch_revision_groups"
                ),
                "same_epoch_revision_rows_discarded": audit.get(
                    "same_epoch_revision_rows_discarded"
                ),
                "conflicting_epochs_dropped": audit.get("conflicting_epochs_dropped"),
                "canonical_unique_rows": audit.get("canonical_unique_rows"),
                "raw_tle_rows": audit.get("raw_tle_rows"),
                "tle_used_for_science": audit.get("tle_used_for_science"),
                "records_before": before.get("legacy_records"),
                "records_after": sat.n_records,
                "median_gap_before_h": before.get("legacy_median_gap_h"),
                "median_gap_after_h": sat.gap_stats_h()["median_gap_h"],
            }
        )
    return rows


INGESTION_AUDIT_HEADER = [
    "satellite",
    "satellite_name",
    "norad_id",
    "canonical_source",
    "raw_json_rows",
    "duplicate_json_rows",
    "same_epoch_policy",
    "equivalent_duplicate_rows_collapsed",
    "same_epoch_revision_groups",
    "same_epoch_revision_rows_discarded",
    "conflicting_epochs_dropped",
    "canonical_unique_rows",
    "raw_tle_rows",
    "tle_used_for_science",
    "records_before",
    "records_after",
    "median_gap_before_h",
    "median_gap_after_h",
]


def build_data_manifest(sats: list[SatelliteData], args) -> list[dict[str, Any]]:
    """Phase 1 data manifest, one entry per ingested satellite."""
    manifest = []
    for sat in sats:
        usable_bands = []
        epochs = sat.epochs()
        for band, (lo, hi) in STALENESS_BANDS.items():
            n_pairs = sum(
                1
                for j in range(len(epochs))
                if select_stale_partner(epochs, j, float(band), lo, hi) is not None
            )
            if n_pairs >= (MIN_TRAIN_PAIRS + MIN_VAL_PAIRS + MIN_TEST_PAIRS):
                usable_bands.append(band)
        manifest.append(
            {
                "satellite_name": sat.name,
                "norad_id": sat.norad,
                "satellite_key": sat.key,
                "constellation_family": args.family_hint.get(str(sat.norad), "unknown"),
                "source_path": sat.source_path,
                "tle_record_count": sat.n_records,
                "epoch_start_utc": epochs[0].isoformat(),
                "epoch_end_utc": epochs[-1].isoformat(),
                "epoch_span_days": round(
                    (epochs[-1] - epochs[0]).total_seconds() / 86400.0, 3
                ),
                **sat.gap_stats_h(),
                **sat.orbit_stats(),
                "usable_staleness_bands_h": usable_bands,
                "reference_is_measured_truth": False,
            }
        )
    return manifest


# --------------------------------------------------------------------------
# Geometry / Doppler
# --------------------------------------------------------------------------


def _gmst_rad(jd: float, fr: float) -> float:
    d = (jd + fr) - 2_451_545.0
    return math.radians((280.46061837 + 360.98564736629 * d) % 360.0)


def _gs_teme_km(
    jd: float, fr: float, lat_deg: float, lon_deg: float, alt_m: float
) -> tuple[np.ndarray, np.ndarray]:
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * math.sin(lat) ** 2)
    r_ecef = np.array(
        [
            (n + alt_m) * math.cos(lat) * math.cos(lon),
            (n + alt_m) * math.cos(lat) * math.sin(lon),
            (n * (1.0 - WGS84_E2) + alt_m) * math.sin(lat),
        ]
    )
    theta = _gmst_rad(jd, fr)
    ct, st = math.cos(theta), math.sin(theta)
    rot = np.array([[ct, -st, 0.0], [st, ct, 0.0], [0.0, 0.0, 1.0]])
    r_teme = (rot @ r_ecef) * 1e-3
    v_teme = np.array([-OMEGA_EARTH * r_teme[1], OMEGA_EARTH * r_teme[0], 0.0])
    return r_teme, v_teme


def _jd_of(when: dt.datetime) -> tuple[float, float]:
    return jday(
        when.year,
        when.month,
        when.day,
        when.hour,
        when.minute,
        when.second + when.microsecond * 1e-6,
    )


def _doppler_and_geom(
    sat_r: np.ndarray,
    sat_v: np.ndarray,
    gs_r: np.ndarray,
    gs_v: np.ndarray,
    carrier_hz: float,
) -> tuple[float, float, float]:
    dr = sat_r - gs_r
    r_mag = float(np.linalg.norm(dr))
    if r_mag < 1.0:
        return 0.0, -90.0, r_mag
    r_hat = dr / r_mag
    range_rate = float(np.dot(sat_v - gs_v, r_hat))
    doppler_hz = -carrier_hz * range_rate * 1e3 / C_LIGHT
    gs_up = gs_r / (float(np.linalg.norm(gs_r)) + 1e-9)
    sin_e = float(np.dot(r_hat, gs_up))
    elev = math.degrees(math.asin(max(-1.0, min(1.0, sin_e))))
    return doppler_hz, elev, r_mag


# --------------------------------------------------------------------------
# Pair construction (Phase 2)
# --------------------------------------------------------------------------


def select_stale_partner(
    epochs: list[dt.datetime], j: int, target_h: float, lo_h: float, hi_h: float
) -> int | None:
    """Index of the older TLE inside the gap band whose gap is closest to target.

    Operational pairing: the terminal holds a TLE roughly target_h old and
    propagates it open-loop. Consecutive TLEs are not required. This is the ONE
    pairing rule; every cell uses it.
    """
    best_i: int | None = None
    best_d: float | None = None
    for i in range(j - 1, -1, -1):
        gap_h = (epochs[j] - epochs[i]).total_seconds() / 3600.0
        if gap_h < lo_h:
            continue
        if gap_h > hi_h:
            break
        d = abs(gap_h - target_h)
        if best_d is None or d < best_d:
            best_d, best_i = d, i
    return best_i


def build_pairs(
    sat: SatelliteData,
    target_h: int,
    reject_hz: float,
    gs: tuple[float, float, float],
    carrier_hz: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Build (accepted_pairs, rejected_pairs, stats) for one staleness band.

    Every pair keeps its identity: satellite, both epochs, actual staleness,
    band, all 24 in-pass timestamps, residuals and features.
    """
    lo_h, hi_h = STALENESS_BANDS[target_h]
    epochs = sat.epochs()
    records = sat.records
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    n_no_partner = 0
    step_s = PERIOD_SAMPLE_S / K_SAMPLES_PER_PAIR

    for j in range(len(records)):
        i = select_stale_partner(epochs, j, float(target_h), lo_h, hi_h)
        if i is None:
            n_no_partner += 1
            continue
        old, new = records[i], records[j]
        pair_id = f"{sat.key}|{target_h}h|{epochs[j].isoformat()}"
        actual_h = (epochs[j] - epochs[i]).total_seconds() / 3600.0
        base = {
            "pair_id": pair_id,
            "satellite": sat.key,
            "satellite_name": sat.name,
            "stale_epoch_utc": epochs[i].isoformat(),
            "ref_epoch_utc": epochs[j].isoformat(),
            "actual_staleness_h": round(actual_h, 4),
            "band_h": target_h,
        }
        try:
            sat_old = Satrec.twoline2rv(old["line1"], old["line2"])
            sat_new = Satrec.twoline2rv(new["line1"], new["line2"])
        except Exception:
            rejected.append({**base, "reject_reason": "tle_parse_error"})
            continue

        gap_s = actual_h * 3600.0
        rows_x: list[list[float]] = []
        rows_y: list[float] = []
        stamps: list[str] = []
        max_abs = 0.0
        sgp4_failed = False
        for k in range(K_SAMPLES_PER_PAIR):
            t_abs = epochs[j] + dt.timedelta(seconds=k * step_s)
            age_s = (t_abs - epochs[i]).total_seconds()
            jd, fr = _jd_of(t_abs)
            gs_r, gs_v = _gs_teme_km(jd, fr, *gs)
            e_old, r_old, v_old = sat_old.sgp4(jd, fr)
            e_new, r_new, v_new = sat_new.sgp4(jd, fr)
            if e_old != 0 or e_new != 0:
                sgp4_failed = True
                break
            d_stale, elev, rng = _doppler_and_geom(
                np.array(r_old), np.array(v_old), gs_r, gs_v, carrier_hz
            )
            d_ref, _, _ = _doppler_and_geom(
                np.array(r_new), np.array(v_new), gs_r, gs_v, carrier_hz
            )
            residual = d_ref - d_stale
            max_abs = max(max_abs, abs(residual))
            mean_anom = (
                old["mean_anomaly_rad"] + old["mean_motion_rad_min"] * age_s / 60.0
            )
            phase = mean_anom % (2.0 * math.pi)
            rows_x.append(
                [
                    age_s,
                    gap_s,
                    d_stale,
                    math.sin(phase),
                    math.cos(phase),
                    elev,
                    rng,
                    old["mean_motion_rad_min"],
                    old["bstar"],
                    old["ecc"],
                ]
            )
            rows_y.append(residual)
            stamps.append(t_abs.isoformat())

        if sgp4_failed:
            rejected.append({**base, "reject_reason": "sgp4_propagation_error"})
            continue
        if max_abs > reject_hz:
            rejected.append(
                {
                    **base,
                    "reject_reason": "residual_cap",
                    "max_abs_residual_hz": round(max_abs, 4),
                    "reject_threshold_hz": reject_hz,
                }
            )
            continue
        accepted.append(
            {
                **base,
                "ref_epoch": epochs[j],
                "timestamps_utc": stamps,
                "x": np.asarray(rows_x, dtype=float),
                "y": np.asarray(rows_y, dtype=float),
                "max_abs_residual_hz": round(max_abs, 4),
            }
        )

    stats = {
        "accepted_pairs": len(accepted),
        "rejected_pairs": len(rejected),
        "no_partner": n_no_partner,
        "reject_rate_pct": round(
            100.0 * len(rejected) / max(1, len(accepted) + len(rejected)), 3
        ),
    }
    return accepted, rejected, stats


def split_boundaries(sat: SatelliteData) -> tuple[dt.datetime, dt.datetime]:
    """Global chronological 60/20/20 boundaries from the record epoch span."""
    eps = sat.epochs()
    t0, t1 = eps[0], eps[-1]
    span = (t1 - t0).total_seconds()
    return (
        t0 + dt.timedelta(seconds=span * TRAIN_FRAC),
        t0 + dt.timedelta(seconds=span * (TRAIN_FRAC + VAL_FRAC)),
    )


def split_pairs(
    pairs: list[dict[str, Any]], t_train_end: dt.datetime, t_val_end: dt.datetime
) -> tuple[list[dict], list[dict], list[dict]]:
    train = [p for p in pairs if p["ref_epoch"] < t_train_end]
    val = [p for p in pairs if t_train_end <= p["ref_epoch"] < t_val_end]
    test = [p for p in pairs if p["ref_epoch"] >= t_val_end]
    return train, val, test


def stack(pairs: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    if not pairs:
        return np.zeros((0, len(FEATURE_NAMES))), np.zeros((0,))
    return (
        np.concatenate([p["x"] for p in pairs], axis=0),
        np.concatenate([p["y"] for p in pairs], axis=0),
    )


# --------------------------------------------------------------------------
# Models (Phase 3)
# --------------------------------------------------------------------------


def _ridge_weights(x: np.ndarray, y: np.ndarray, alpha: float) -> np.ndarray:
    xb = np.hstack([x, np.ones((x.shape[0], 1))])
    reg = alpha * np.eye(xb.shape[1])
    reg[-1, -1] = 0.0
    return np.linalg.solve(xb.T @ xb + reg, xb.T @ y)


def _mae(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a - b))) if a.size else float("nan")


def _fit_ridge_on(
    columns: tuple[int, ...],
    x_tr: np.ndarray,
    y_tr: np.ndarray,
    x_va: np.ndarray,
    y_va: np.ndarray,
) -> tuple[Callable[[np.ndarray], np.ndarray], float]:
    """Ridge on a column subset, alpha chosen on the TARGET validation split."""
    sub_tr = x_tr[:, columns]
    mu = sub_tr.mean(axis=0)
    sig = sub_tr.std(axis=0)
    sig[sig < 1e-12] = 1.0

    def _design(x: np.ndarray) -> np.ndarray:
        z = (x[:, columns] - mu) / sig
        return np.hstack([z, np.ones((z.shape[0], 1))])

    best_alpha, best_score, best_w = RIDGE_ALPHAS[0], None, None
    for alpha in RIDGE_ALPHAS:
        w = _ridge_weights((sub_tr - mu) / sig, y_tr, alpha)
        score = _mae(_design(x_va) @ w, y_va)
        if best_score is None or score < best_score:
            best_alpha, best_score, best_w = alpha, score, w
    weights = best_w
    return (lambda x: _design(x) @ weights), best_alpha


def fit_correctors(
    x_tr: np.ndarray, y_tr: np.ndarray, x_va: np.ndarray, y_va: np.ndarray
) -> dict[str, Any]:
    """Fit every lightweight corrector on TRAIN; tune only on TARGET validation."""
    models: dict[str, Any] = {
        "zero": lambda x: np.zeros(x.shape[0]),
        "mean_bias": (lambda c: (lambda x: np.full(x.shape[0], c)))(
            float(np.mean(y_tr))
        ),
        "median_bias": (lambda c: (lambda x: np.full(x.shape[0], c)))(
            float(np.median(y_tr))
        ),
    }
    age = x_tr[:, 0]
    design = np.stack([age, np.ones_like(age)], axis=1)
    coef, *_ = np.linalg.lstsq(design, y_tr, rcond=None)
    models["linear_bias_rate"] = (lambda c: (lambda x: c[0] * x[:, 0] + c[1]))(coef)

    models["stale_age_ridge"], alpha_age = _fit_ridge_on(
        STALE_AGE_FEATURES, x_tr, y_tr, x_va, y_va
    )
    all_cols = tuple(range(len(FEATURE_NAMES)))
    models["ridge"], alpha_full = _fit_ridge_on(all_cols, x_tr, y_tr, x_va, y_va)
    models["_alphas"] = {"stale_age_ridge": alpha_age, "ridge": alpha_full}
    return models


# --------------------------------------------------------------------------
# Pair-level metrics and gates (Phase 2, 7)
# --------------------------------------------------------------------------


def pair_metrics(err: np.ndarray, f_tol_hz: float) -> dict[str, float]:
    """Error metrics for ONE pair's 24 in-pass samples."""
    abs_err = np.abs(err)
    return {
        "mae_hz": float(np.mean(abs_err)),
        "medae_hz": float(np.median(abs_err)),
        "p95_hz": float(np.percentile(abs_err, 95)),
        "p99_hz": float(np.percentile(abs_err, 99)),
        "max_hz": float(np.max(abs_err)),
        "outage_proxy": float(np.mean(abs_err > f_tol_hz)),
    }


def pair_abs_error_matrix(
    pairs: list[dict[str, Any]], predict: Callable[[np.ndarray], np.ndarray]
) -> np.ndarray:
    """(n_pairs, K) absolute errors. One row per accepted TLE pair.

    Vectorized over pairs; every pair carries exactly K_SAMPLES_PER_PAIR
    samples by construction, so the reshape is exact. Same arithmetic as the
    per-pair loop it replaces, evaluated in one pass.
    """
    if not pairs:
        return np.zeros((0, K_SAMPLES_PER_PAIR))
    lengths = {len(p["y"]) for p in pairs}
    if lengths != {K_SAMPLES_PER_PAIR}:
        raise ValueError(f"ragged pairs: sample counts {sorted(lengths)}")
    x = np.concatenate([p["x"] for p in pairs], axis=0)
    y = np.concatenate([p["y"] for p in pairs], axis=0)
    return np.abs(y - predict(x)).reshape(len(pairs), K_SAMPLES_PER_PAIR)


def per_pair_mae(
    pairs: list[dict[str, Any]], predict: Callable[[np.ndarray], np.ndarray]
) -> np.ndarray:
    """One MAE per accepted TLE pair -- the campaign's statistical unit."""
    err = pair_abs_error_matrix(pairs, predict)
    return err.mean(axis=1) if err.size else np.zeros(0)


def aggregate_pair_metrics(
    pairs: list[dict[str, Any]],
    predict: Callable[[np.ndarray], np.ndarray],
    f_tol_hz: float,
) -> dict[str, float]:
    """Pair-level aggregate: every pair contributes exactly one observation."""
    if not pairs:
        return {k: float("nan") for k in ("mae", "p95", "p99", "outage", "medae")}
    err = pair_abs_error_matrix(pairs, predict)
    return {
        "mae": float(np.mean(err.mean(axis=1))),
        "medae": float(np.mean(np.median(err, axis=1))),
        "p95": float(np.mean(np.percentile(err, 95, axis=1))),
        "p99": float(np.mean(np.percentile(err, 99, axis=1))),
        "outage": float(np.mean((err > f_tol_hz).mean(axis=1))),
    }


def guard_cost(p99_hz: float, outage: float, alpha_g: float, band_hz: float) -> float:
    """Energy/overhead proxy E ~ (1 + alpha_g * g/B)(1 + rho) with g = 2*p99."""
    return (1.0 + alpha_g * (2.0 * p99_hz) / band_hz) * (1.0 + outage)


def evaluate_gates(
    phys: dict[str, float], learned: dict[str, float], args
) -> dict[str, str]:
    """Every gate objective, all decided on the TARGET validation segment.

    A gate opens only on a proven margin. If the physics metric is already zero
    the learned branch cannot beat it by a margin, so the gate stays closed.
    """
    decisions: dict[str, str] = {}
    for objective in GATE_OBJECTIVES:
        if objective == "guard_cost":
            base = guard_cost(
                phys["p99"], phys["outage"], args.alpha_g, args.hop_bandwidth_hz
            )
            cand = guard_cost(
                learned["p99"], learned["outage"], args.alpha_g, args.hop_bandwidth_hz
            )
        else:
            base, cand = phys[objective], learned[objective]
        if not (math.isfinite(base) and math.isfinite(cand)):
            decisions[objective] = "unavailable"
        elif base <= 0.0:
            decisions[objective] = "closed"
        else:
            decisions[objective] = "open" if cand < args.gamma * base else "closed"
    return decisions


def _binom_two_sided_p(wins: int, trials: int) -> float:
    """Two-sided sign-test p-value under H0: win probability = 1/2.

    Exact rational arithmetic up to EXACT_BINOM_MAX trials; log-space beyond
    that, because ``2.0 ** trials`` overflows a double above 1023 trials and a
    large satellite easily exceeds that many accepted pairs.
    """
    if trials == 0:
        return float("nan")
    k = min(wins, trials - wins)
    if trials <= EXACT_BINOM_MAX:
        tail = Fraction(sum(math.comb(trials, i) for i in range(k + 1)), 1 << trials)
        return float(min(1.0, 2.0 * float(tail)))
    log2 = math.log(2.0)
    log_terms = [
        math.lgamma(trials + 1)
        - math.lgamma(i + 1)
        - math.lgamma(trials - i + 1)
        - trials * log2
        for i in range(k + 1)
    ]
    peak = max(log_terms)
    tail = math.exp(peak) * sum(math.exp(t - peak) for t in log_terms)
    return float(min(1.0, 2.0 * tail))


def paired_pair_level_test(
    pairs: list[dict[str, Any]],
    phys: Callable[[np.ndarray], np.ndarray],
    learned: Callable[[np.ndarray], np.ndarray],
    f_tol_hz: float,
    n_boot: int,
    seed: int,
) -> dict[str, Any]:
    """Paired sign test + bootstrap CI on the per-pair MAE difference."""
    if not pairs:
        return {}
    diffs = per_pair_mae(pairs, learned) - per_pair_mae(pairs, phys)
    wins = int(np.sum(diffs < -WIN_TOLERANCE_HZ))
    losses = int(np.sum(diffs > WIN_TOLERANCE_HZ))
    ties = int(len(diffs) - wins - losses)
    rng = np.random.default_rng(seed)
    boot = np.array(
        [
            float(np.mean(rng.choice(diffs, size=len(diffs), replace=True)))
            for _ in range(n_boot)
        ]
    )
    return {
        "n_pairs": int(len(diffs)),
        "pair_wins_learned": wins,
        "pair_losses_learned": losses,
        "pair_ties": ties,
        "pair_win_rate": round(wins / len(diffs), 6),
        "mean_pair_mae_delta_hz": round(float(np.mean(diffs)), 6),
        "boot_ci_low_hz": round(float(np.percentile(boot, 2.5)), 6),
        "boot_ci_high_hz": round(float(np.percentile(boot, 97.5)), 6),
        "sign_test_p": round(_binom_two_sided_p(wins, wins + losses), 6),
    }


# --------------------------------------------------------------------------
# Matrix cell (Phase 4, 5)
# --------------------------------------------------------------------------


def _cache_pairs(sat, staleness_h, reject_hz, args, cache):
    key = (sat.key, staleness_h, reject_hz)
    if key not in cache:
        cache[key] = build_pairs(
            sat,
            staleness_h,
            reject_hz,
            (args.gs_lat, args.gs_lon, args.gs_alt),
            args.carrier_hz,
        )
    return cache[key]


def evaluate_cell(
    source: SatelliteData,
    target: SatelliteData,
    staleness_h: int,
    reject_hz: float,
    args,
    cache: dict,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """One matrix cell: train_source -> validation_target -> test_target."""
    src_acc, _, src_stats = _cache_pairs(source, staleness_h, reject_hz, args, cache)
    tgt_acc, _, tgt_stats = _cache_pairs(target, staleness_h, reject_hz, args, cache)

    src_tr, _, _ = split_pairs(src_acc, *split_boundaries(source))
    _, tgt_va, tgt_te = split_pairs(tgt_acc, *split_boundaries(target))

    relation = "target_specific" if source.key == target.key else "cross_satellite"
    row: dict[str, Any] = {
        "train_source": source.key,
        "train_source_name": source.name,
        "deploy_target": target.key,
        "deploy_target_name": target.name,
        "relation": relation,
        "staleness_h": staleness_h,
        "reject_hz": reject_hz,
        "gamma": args.gamma,
        "f_tol_hz": args.f_tol_hz,
        "n_train_pairs": len(src_tr),
        "n_val_pairs": len(tgt_va),
        "n_test_pairs": len(tgt_te),
        "rejected_pairs_source": src_stats["rejected_pairs"],
        "rejected_pairs_target": tgt_stats["rejected_pairs"],
        "reject_rate_source_pct": src_stats["reject_rate_pct"],
        "reject_rate_target_pct": tgt_stats["reject_rate_pct"],
    }

    if (
        len(src_tr) < MIN_TRAIN_PAIRS
        or len(tgt_va) < MIN_VAL_PAIRS
        or len(tgt_te) < MIN_TEST_PAIRS
    ):
        row.update(
            {
                "status": "insufficient_pairs",
                "selected_model": None,
                "gate_decision": "unavailable",
                **{f"gate_{g}": "unavailable" for g in GATE_OBJECTIVES},
            }
        )
        return row, []

    x_tr, y_tr = stack(src_tr)
    x_va, y_va = stack(tgt_va)
    models = fit_correctors(x_tr, y_tr, x_va, y_va)

    # Selection: validation pair-level MAE among LEARNED candidates only.
    val_agg = {
        name: aggregate_pair_metrics(tgt_va, models[name], args.f_tol_hz)
        for name in REFERENCE_MODELS + LEARNED_MODELS
    }
    selected = min(LEARNED_MODELS, key=lambda n: val_agg[n]["mae"])
    gates = evaluate_gates(val_agg["zero"], val_agg[selected], args)
    primary_gate = gates[args.primary_gate]

    test_agg = {
        name: aggregate_pair_metrics(tgt_te, models[name], args.f_tol_hz)
        for name in REFERENCE_MODELS + LEARNED_MODELS
    }
    stats_test = paired_pair_level_test(
        tgt_te, models["zero"], models[selected], args.f_tol_hz, args.n_boot, args.seed
    )

    row.update(
        {
            "status": "evaluated",
            "selected_model": selected,
            "ridge_alpha": models["_alphas"].get(selected),
            "val_mae_phys_hz": round(val_agg["zero"]["mae"], 6),
            "val_mae_ml_hz": round(val_agg[selected]["mae"], 6),
            "val_p95_phys_hz": round(val_agg["zero"]["p95"], 6),
            "val_p95_ml_hz": round(val_agg[selected]["p95"], 6),
            "val_p99_phys_hz": round(val_agg["zero"]["p99"], 6),
            "val_p99_ml_hz": round(val_agg[selected]["p99"], 6),
            "val_outage_phys": round(val_agg["zero"]["outage"], 6),
            "val_outage_ml": round(val_agg[selected]["outage"], 6),
            "gate_decision": primary_gate,
            **{f"gate_{g}": gates[g] for g in GATE_OBJECTIVES},
            "baseline_test_mae_hz": round(test_agg["zero"]["mae"], 6),
            "learned_test_mae_hz": round(test_agg[selected]["mae"], 6),
            "degradation_pct": round(
                (test_agg[selected]["mae"] / test_agg["zero"]["mae"] - 1.0) * 100.0, 4
            )
            if test_agg["zero"]["mae"] > 0
            else None,
            "p95_degradation_pct": round(
                (test_agg[selected]["p95"] / test_agg["zero"]["p95"] - 1.0) * 100.0, 4
            )
            if test_agg["zero"]["p95"] > 0
            else None,
            "p99_degradation_pct": round(
                (test_agg[selected]["p99"] / test_agg["zero"]["p99"] - 1.0) * 100.0, 4
            )
            if test_agg["zero"]["p99"] > 0
            else None,
            "deployed_test_mae_hz": round(
                test_agg[selected]["mae"]
                if primary_gate == "open"
                else test_agg["zero"]["mae"],
                6,
            ),
            **stats_test,
        }
    )
    for name in REFERENCE_MODELS + LEARNED_MODELS:
        row[f"val_mae_{name}"] = round(val_agg[name]["mae"], 6)
        row[f"test_mae_{name}"] = round(test_agg[name]["mae"], 6)

    pair_rows: list[dict[str, Any]] = []
    for split_name, split_pair_list in (("validation", tgt_va), ("test", tgt_te)):
        for pair in split_pair_list:
            base_m = pair_metrics(pair["y"] - models["zero"](pair["x"]), args.f_tol_hz)
            ml_m = pair_metrics(
                pair["y"] - models[selected](pair["x"]), args.f_tol_hz
            )
            delta = ml_m["mae_hz"] - base_m["mae_hz"]
            pair_rows.append(
                {
                    "pair_id": pair["pair_id"],
                    "train_source": source.key,
                    "deploy_target": target.key,
                    "relation": relation,
                    "split": split_name,
                    "satellite": pair["satellite"],
                    "stale_epoch_utc": pair["stale_epoch_utc"],
                    "ref_epoch_utc": pair["ref_epoch_utc"],
                    "actual_staleness_h": pair["actual_staleness_h"],
                    "band_h": pair["band_h"],
                    "n_samples": len(pair["y"]),
                    "first_sample_utc": pair["timestamps_utc"][0],
                    "last_sample_utc": pair["timestamps_utc"][-1],
                    "max_abs_residual_hz": pair["max_abs_residual_hz"],
                    "selected_model": selected,
                    "gate_decision": primary_gate,
                    "baseline_mae_hz": round(base_m["mae_hz"], 6),
                    "learned_mae_hz": round(ml_m["mae_hz"], 6),
                    "baseline_medae_hz": round(base_m["medae_hz"], 6),
                    "learned_medae_hz": round(ml_m["medae_hz"], 6),
                    "baseline_p95_hz": round(base_m["p95_hz"], 6),
                    "learned_p95_hz": round(ml_m["p95_hz"], 6),
                    "baseline_p99_hz": round(base_m["p99_hz"], 6),
                    "learned_p99_hz": round(ml_m["p99_hz"], 6),
                    "baseline_max_hz": round(base_m["max_hz"], 6),
                    "learned_max_hz": round(ml_m["max_hz"], 6),
                    "baseline_outage_proxy": round(base_m["outage_proxy"], 6),
                    "learned_outage_proxy": round(ml_m["outage_proxy"], 6),
                    "pair_outcome": (
                        "learned_win"
                        if delta < -WIN_TOLERANCE_HZ
                        else "learned_loss"
                        if delta > WIN_TOLERANCE_HZ
                        else "tie"
                    ),
                    "reject_reason": "",
                }
            )
    return row, pair_rows


# --------------------------------------------------------------------------
# Phase 6 / Phase 7 aggregates
# --------------------------------------------------------------------------


def reject_sensitivity(sats, args, cache) -> list[dict[str, Any]]:
    """Re-run selection and gating at every reject threshold (Phase 6)."""
    rows: list[dict[str, Any]] = []
    for sat in sats:
        for staleness_h in args.staleness:
            for threshold in args.reject_sweep:
                acc, rej, stats = _cache_pairs(sat, staleness_h, threshold, args, cache)
                _, y = stack(acc)
                cell, _ = evaluate_cell(sat, sat, staleness_h, threshold, args, cache)
                rows.append(
                    {
                        "satellite": sat.key,
                        "satellite_name": sat.name,
                        "staleness_h": staleness_h,
                        "reject_hz": threshold,
                        "accepted_pairs": stats["accepted_pairs"],
                        "rejected_pairs": stats["rejected_pairs"],
                        "reject_rate_pct": stats["reject_rate_pct"],
                        "residual_mae_hz": round(float(np.mean(np.abs(y))), 6)
                        if y.size
                        else None,
                        "residual_p99_hz": round(
                            float(np.percentile(np.abs(y), 99)), 6
                        )
                        if y.size
                        else None,
                        "status": cell["status"],
                        "selected_model": cell.get("selected_model"),
                        "gate_decision": cell.get("gate_decision"),
                        "degradation_pct": cell.get("degradation_pct"),
                        "pair_win_rate": cell.get("pair_win_rate"),
                        "top_rejected_max_abs_hz": sorted(
                            (
                                r.get("max_abs_residual_hz", 0.0)
                                for r in rej
                                if r["reject_reason"] == "residual_cap"
                            ),
                            reverse=True,
                        )[:5],
                    }
                )
    return rows


def gate_agreement(matrix_rows) -> list[dict[str, Any]]:
    """Pairwise agreement between gate objectives over evaluated cells."""
    evaluated = [r for r in matrix_rows if r["status"] == "evaluated"]
    rows: list[dict[str, Any]] = []
    for a, b in itertools.combinations(GATE_OBJECTIVES, 2):
        comparable = [
            r
            for r in evaluated
            if r[f"gate_{a}"] in {"open", "closed"}
            and r[f"gate_{b}"] in {"open", "closed"}
        ]
        agree = sum(1 for r in comparable if r[f"gate_{a}"] == r[f"gate_{b}"])
        a_open_b_closed = sum(
            1
            for r in comparable
            if r[f"gate_{a}"] == "open" and r[f"gate_{b}"] == "closed"
        )
        b_open_a_closed = sum(
            1
            for r in comparable
            if r[f"gate_{b}"] == "open" and r[f"gate_{a}"] == "closed"
        )
        rows.append(
            {
                "gate_a": a,
                "gate_b": b,
                "n_comparable_cells": len(comparable),
                "n_agree": agree,
                "agreement_pct": round(100.0 * agree / len(comparable), 3)
                if comparable
                else None,
                "a_open_b_closed": a_open_b_closed,
                "b_open_a_closed": b_open_a_closed,
            }
        )
    return rows


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------


def write_csv(path: Path, rows, header: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_metadata(args, sats, status: str) -> dict[str, Any]:
    return {
        "campaign": "paper1_plus_multisat_generalization",
        "research_question": (
            "When does model-derived inter-TLE residual structure generalize "
            "across LEO satellites, and can a validation-gated endpoint policy "
            "safely refuse residual learning under satellite/domain shift?"
        ),
        "status": status,
        "dry_run": status != "evaluated",
        "raw_tle_inputs_available": bool(sats),
        "satellites_found": len(sats),
        "min_satellites_for_generalization_claim": args.min_satellites,
        "reference_is_measured_truth": False,
        "scope": (
            "software-only model-derived inter-TLE residuals; not measured RF truth"
        ),
        "hardware_used": False,
        "rf_used": False,
        "unified_protocol": {
            "target_specific": "train_A -> validation_A -> test_A",
            "transfer": "train_A -> validation_B -> test_B",
            "selection_split": "target validation",
            "gate_split": "target validation",
            "test_role": "reports consequences only; never selects, never decides G",
            "experimental_unit": "accepted TLE pair",
            "single_code_path": True,
        },
        "tle_dir": str(args.tle_dir),
        "ground_station": {
            "lat_deg": args.gs_lat,
            "lon_deg": args.gs_lon,
            "alt_m": args.gs_alt,
        },
        "carrier_hz": args.carrier_hz,
        "staleness_targets_h": list(args.staleness),
        "staleness_bands_h": {str(k): list(v) for k, v in STALENESS_BANDS.items()},
        "reject_hz": args.reject_hz,
        "reject_sweep_hz": list(args.reject_sweep),
        "gamma": args.gamma,
        "f_tol_hz": args.f_tol_hz,
        "alpha_g": args.alpha_g,
        "hop_bandwidth_hz": args.hop_bandwidth_hz,
        "primary_gate": args.primary_gate,
        "gate_objectives": list(GATE_OBJECTIVES),
        "samples_per_pair": K_SAMPLES_PER_PAIR,
        "split": "chronological 60/20/20 by reference epoch",
        "reference_models": list(REFERENCE_MODELS),
        "learned_models": list(LEARNED_MODELS),
        "heavy_models_excluded": "random forest / gradient boosting / MLP",
        "feature_names": list(FEATURE_NAMES),
        "bootstrap_resamples": args.n_boot,
        "seed": args.seed,
        "supersedes": (
            "old BK1 target-specific and BK1->BK2 transfer protocols are NOT "
            "reused; their numbers are not comparable to this pipeline"
        ),
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Paper 1+ generalization matrix")
    parser.add_argument("--tle-dir", type=Path, default=ROOT / "dataraw" / "spacetrack")
    parser.add_argument("--gs-lat", type=float, default=24.0)
    parser.add_argument("--gs-lon", type=float, default=121.0)
    parser.add_argument("--gs-alt", type=float, default=100.0)
    parser.add_argument("--carrier-hz", type=float, default=868e6)
    parser.add_argument(
        "--staleness",
        type=int,
        nargs="+",
        default=sorted(STALENESS_BANDS),
        choices=sorted(STALENESS_BANDS),
    )
    parser.add_argument("--reject-hz", type=float, default=1500.0)
    parser.add_argument(
        "--reject-sweep",
        type=float,
        nargs="+",
        default=[150.0, 500.0, 1500.0, 3000.0, float("inf")],
        help="reject thresholds for Phase 6; inf means no screening",
    )
    parser.add_argument("--gamma", type=float, default=0.95)
    parser.add_argument("--f-tol-hz", type=float, default=500.0)
    parser.add_argument("--alpha-g", type=float, default=1.0)
    parser.add_argument("--hop-bandwidth-hz", type=float, default=137e3)
    parser.add_argument(
        "--primary-gate", default="mae", choices=sorted(GATE_OBJECTIVES)
    )
    parser.add_argument("--min-satellites", type=int, default=3)
    parser.add_argument("--n-boot", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260727)
    parser.add_argument("--family-hint-json", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=HERE)
    args = parser.parse_args(argv)
    args.family_hint = (
        json.loads(args.family_hint_json.read_text(encoding="utf-8"))
        if args.family_hint_json and args.family_hint_json.exists()
        else {}
    )
    return args


def _write_all(out_dir: Path, payload: dict[str, Any]) -> None:
    (out_dir / "results.json").write_text(
        json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8"
    )
    write_csv(
        out_dir / "multisat_generalization_matrix.csv",
        payload["matrix_rows"],
        MATRIX_HEADER,
    )
    write_csv(
        out_dir / "TARGET_SPECIFIC_LEARNABILITY.csv",
        [r for r in payload["matrix_rows"] if r.get("relation") == "target_specific"],
        MATRIX_HEADER,
    )
    write_csv(
        out_dir / "pair_level_metrics.csv", payload["pair_rows"], PAIR_HEADER
    )
    write_csv(
        out_dir / "rejected_pairs.csv", payload["rejected_rows"], REJECT_PAIR_HEADER
    )
    write_csv(
        out_dir / "per_satellite_summary.csv",
        payload["per_satellite_rows"],
        PER_SAT_HEADER,
    )
    write_csv(
        out_dir / "reject_sensitivity_summary.csv",
        payload["reject_sensitivity_rows"],
        REJECT_HEADER,
    )
    write_csv(
        out_dir / "gate_metric_agreement.csv",
        payload["gate_agreement_rows"],
        GATE_AGREE_HEADER,
    )
    (out_dir / "data_manifest.json").write_text(
        json.dumps(payload["data_manifest"], indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def main(argv=None) -> int:
    args = parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    sats = discover_satellites(args.tle_dir)

    if not sats:
        payload = {
            "metadata": build_metadata(args, sats, "insufficient_data"),
            "data_manifest": [],
            "matrix_rows": [],
            "pair_rows": [],
            "rejected_rows": [],
            "per_satellite_rows": [],
            "reject_sensitivity_rows": [],
            "gate_agreement_rows": [],
            "notes": [
                "No usable historical TLE archive was found under --tle-dir.",
                "No residual was computed and no generalization claim is made.",
                "Restore the raw TLE archive and rerun to populate every matrix.",
            ],
        }
        _write_all(args.out_dir, payload)
        print(
            f"insufficient_data: no usable TLE history under {args.tle_dir}; "
            "wrote empty artifacts, no claim made."
        )
        return 0

    cache: dict = {}
    matrix_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    for src, tgt, staleness_h in itertools.product(sats, sats, args.staleness):
        row, prows = evaluate_cell(src, tgt, staleness_h, args.reject_hz, args, cache)
        matrix_rows.append(row)
        pair_rows.extend(prows)

    rejected_rows: list[dict[str, Any]] = []
    for sat in sats:
        for staleness_h in args.staleness:
            _, rej, _ = _cache_pairs(sat, staleness_h, args.reject_hz, args, cache)
            rejected_rows.extend(rej)

    per_sat_rows = []
    for sat in sats:
        own = [
            r
            for r in matrix_rows
            if r["train_source"] == sat.key
            and r["deploy_target"] == sat.key
            and r["status"] == "evaluated"
        ]
        closed = [r for r in own if r["gate_decision"] == "closed"]
        per_sat_rows.append(
            {
                "satellite": sat.key,
                "satellite_name": sat.name,
                "norad": sat.norad,
                "n_records": sat.n_records,
                "median_gap_h": sat.gap_stats_h()["median_gap_h"],
                "epoch_start": sat.epochs()[0].isoformat(),
                "epoch_end": sat.epochs()[-1].isoformat(),
                "target_specific_rows": len(own),
                "target_specific_gate_closed": len(closed),
                "target_specific_gate_open": len(own) - len(closed),
                "mean_pair_win_rate": round(
                    float(
                        np.mean(
                            [r["pair_win_rate"] for r in own if "pair_win_rate" in r]
                        )
                    ),
                    6,
                )
                if own
                else None,
                "rejected_pairs_total": sum(r["rejected_pairs_target"] for r in own),
            }
        )

    meta = build_metadata(args, sats, "evaluated")
    meta["generalization_claim_supported"] = len(sats) >= args.min_satellites
    payload = {
        "metadata": meta,
        "data_manifest": build_data_manifest(sats, args),
        "matrix_rows": matrix_rows,
        "pair_rows": pair_rows,
        "rejected_rows": rejected_rows,
        "per_satellite_rows": per_sat_rows,
        "reject_sensitivity_rows": reject_sensitivity(sats, args, cache),
        "gate_agreement_rows": gate_agreement(matrix_rows),
        "notes": [
            "All values are model-derived inter-TLE residuals; no measured RF truth.",
            "Gates are decided on the target validation segment; test reports only.",
            "The experimental unit is the accepted TLE pair.",
        ]
        + (
            []
            if len(sats) >= args.min_satellites
            else [
                f"Only {len(sats)} satellite(s) available; below the "
                f"{args.min_satellites}-satellite threshold, so no multi-satellite "
                "generalization claim is made and no matrix figure is emitted."
            ]
        ),
    }
    _write_all(args.out_dir, payload)
    print(
        f"evaluated {len(matrix_rows)} cells / {len(pair_rows)} pair rows over "
        f"{len(sats)} satellite(s); generalization claim supported: "
        f"{meta['generalization_claim_supported']}"
    )
    return 0


MATRIX_HEADER = (
    [
        "train_source",
        "train_source_name",
        "deploy_target",
        "deploy_target_name",
        "relation",
        "staleness_h",
        "reject_hz",
        "gamma",
        "f_tol_hz",
        "status",
        "n_train_pairs",
        "n_val_pairs",
        "n_test_pairs",
        "rejected_pairs_source",
        "rejected_pairs_target",
        "reject_rate_source_pct",
        "reject_rate_target_pct",
        "selected_model",
        "ridge_alpha",
        "val_mae_phys_hz",
        "val_mae_ml_hz",
        "val_p95_phys_hz",
        "val_p95_ml_hz",
        "val_p99_phys_hz",
        "val_p99_ml_hz",
        "val_outage_phys",
        "val_outage_ml",
        "gate_decision",
    ]
    + [f"gate_{g}" for g in GATE_OBJECTIVES]
    + [
        "baseline_test_mae_hz",
        "learned_test_mae_hz",
        "degradation_pct",
        "p95_degradation_pct",
        "p99_degradation_pct",
        "deployed_test_mae_hz",
        "n_pairs",
        "pair_wins_learned",
        "pair_losses_learned",
        "pair_ties",
        "pair_win_rate",
        "mean_pair_mae_delta_hz",
        "boot_ci_low_hz",
        "boot_ci_high_hz",
        "sign_test_p",
    ]
    + [
        f"{split}_mae_{name}"
        for split in ("val", "test")
        for name in REFERENCE_MODELS + LEARNED_MODELS
    ]
)

PAIR_HEADER = [
    "pair_id",
    "train_source",
    "deploy_target",
    "relation",
    "split",
    "satellite",
    "stale_epoch_utc",
    "ref_epoch_utc",
    "actual_staleness_h",
    "band_h",
    "n_samples",
    "first_sample_utc",
    "last_sample_utc",
    "max_abs_residual_hz",
    "selected_model",
    "gate_decision",
    "baseline_mae_hz",
    "learned_mae_hz",
    "baseline_medae_hz",
    "learned_medae_hz",
    "baseline_p95_hz",
    "learned_p95_hz",
    "baseline_p99_hz",
    "learned_p99_hz",
    "baseline_max_hz",
    "learned_max_hz",
    "baseline_outage_proxy",
    "learned_outage_proxy",
    "pair_outcome",
    "reject_reason",
]

REJECT_PAIR_HEADER = [
    "pair_id",
    "satellite",
    "satellite_name",
    "stale_epoch_utc",
    "ref_epoch_utc",
    "actual_staleness_h",
    "band_h",
    "reject_reason",
    "max_abs_residual_hz",
    "reject_threshold_hz",
]

PER_SAT_HEADER = [
    "satellite",
    "satellite_name",
    "norad",
    "n_records",
    "median_gap_h",
    "epoch_start",
    "epoch_end",
    "target_specific_rows",
    "target_specific_gate_closed",
    "target_specific_gate_open",
    "mean_pair_win_rate",
    "rejected_pairs_total",
]

REJECT_HEADER = [
    "satellite",
    "satellite_name",
    "staleness_h",
    "reject_hz",
    "accepted_pairs",
    "rejected_pairs",
    "reject_rate_pct",
    "residual_mae_hz",
    "residual_p99_hz",
    "status",
    "selected_model",
    "gate_decision",
    "degradation_pct",
    "pair_win_rate",
    "top_rejected_max_abs_hz",
]

GATE_AGREE_HEADER = [
    "gate_a",
    "gate_b",
    "n_comparable_cells",
    "n_agree",
    "agreement_pct",
    "a_open_b_closed",
    "b_open_a_closed",
]


if __name__ == "__main__":
    sys.exit(main())
