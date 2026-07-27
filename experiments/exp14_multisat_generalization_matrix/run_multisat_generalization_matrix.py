#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "sgp4>=2.23"]
# ///
"""Multi-satellite inter-TLE residual generalization matrix (Paper 1+).

Software-only. Builds a train-source x deploy-target x staleness matrix of
model-derived inter-TLE residual results and applies the Evidence Gate to each
cell.

Protocol (matches the corrected Paper 1 protocol):
  train      fits the candidate correctors
  validation selects the candidate AND decides the gate G (Eq. 6)
  test       only reports the consequence of the already-fixed decision

For a cross-satellite cell (source != target) the corrector is fitted on the
SOURCE train segment but selected and gated on the TARGET validation segment,
which is the deployable semantics: a terminal can only validate against the
satellite it is about to serve.

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
import json
import math
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from sgp4.api import Satrec, jday

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

C_LIGHT = 299_792_458.0
WGS84_A = 6_378_137.0
WGS84_E2 = 0.006694379990141317
OMEGA_EARTH = 7.292115e-5

K_SAMPLES_PER_PAIR = 24
PERIOD_SAMPLE_S = 5_700.0

TRAIN_FRAC = 0.60
VAL_FRAC = 0.20

MIN_TRAIN_SAMPLES = 60
MIN_VAL_SAMPLES = 20
MIN_TEST_SAMPLES = 20

# (target_h, min_gap_h, max_gap_h) -- same bands as the Paper 1 pipeline.
STALENESS_BANDS: dict[int, tuple[float, float]] = {
    8: (4, 14),
    24: (16, 36),
    48: (36, 60),
    72: (60, 84),
    96: (84, 120),
    168: (144, 192),
}

# Constant-offset references. Never eligible to open the gate, matching the
# Paper 1 rule that a constant bias is not a learned residual correction.
REFERENCE_MODELS = ("zero", "mean_bias", "median_bias")
# Fitted correctors. The validation-best of these is the gated candidate.
LEARNED_MODELS = ("linear_bias_rate", "ridge")

RIDGE_ALPHAS = (1e-2, 1e-1, 1.0, 1e1, 1e2, 1e3)

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


# --------------------------------------------------------------------------
# TLE ingestion
# --------------------------------------------------------------------------


@dataclass
class SatelliteData:
    """One satellite's normalized TLE history."""

    key: str
    name: str
    norad: int
    source_path: str
    records: list[dict[str, Any]] = field(repr=False, default_factory=list)

    @property
    def n_records(self) -> int:
        return len(self.records)

    def epochs(self) -> list[dt.datetime]:
        return [r["epoch"] for r in self.records]

    def gap_stats_h(self) -> dict[str, float | None]:
        eps = self.epochs()
        if len(eps) < 2:
            return {"median_h": None, "p10_h": None, "p90_h": None, "max_h": None}
        gaps = [
            (b - a).total_seconds() / 3600.0 for a, b in zip(eps[:-1], eps[1:])
        ]
        gaps.sort()
        return {
            "median_h": round(statistics.median(gaps), 3),
            "p10_h": round(gaps[int(0.10 * (len(gaps) - 1))], 3),
            "p90_h": round(gaps[int(0.90 * (len(gaps) - 1))], 3),
            "max_h": round(gaps[-1], 3),
        }


def _parse_epoch(value: str) -> dt.datetime:
    text = value.replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _satrec_epoch(sat: Satrec) -> dt.datetime:
    """Recover the TLE epoch as UTC from a parsed Satrec."""
    jd_total = sat.jdsatepoch + sat.jdsatepochF
    unix_s = (jd_total - 2_440_587.5) * 86400.0
    return dt.datetime.fromtimestamp(unix_s, tz=dt.timezone.utc)


def _normalize(line1: str, line2: str, name: str, epoch: str | None) -> dict | None:
    """Build one record, deriving mean elements from the TLE lines themselves.

    Deriving from Satrec (rather than Space-Track JSON columns) keeps JSON and
    three-line text sources on an identical footing. Units differ from the
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
        "bstar": float(sat.bstar),
        "ecc": float(sat.ecco),
    }


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


def discover_satellites(tle_dir: Path) -> list[SatelliteData]:
    """Collect every satellite with a usable TLE history under tle_dir."""
    if not tle_dir.is_dir():
        return []
    by_norad: dict[int, SatelliteData] = {}
    for path in sorted(tle_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() == ".json":
            records = _records_from_json(path)
        elif path.suffix.lower() in {".txt", ".tle", ".3le"}:
            records = _records_from_text(path)
        else:
            continue
        for rec in records:
            norad = rec["norad"]
            sat = by_norad.get(norad)
            if sat is None:
                sat = SatelliteData(
                    key=f"NORAD{norad}",
                    name=rec["name"],
                    norad=norad,
                    source_path=str(path.relative_to(tle_dir.parent)),
                )
                by_norad[norad] = sat
            sat.records.append(rec)
    usable = []
    for sat in by_norad.values():
        sat.records.sort(key=lambda r: r["epoch"])
        deduped, seen = [], set()
        for rec in sat.records:
            stamp = rec["epoch"].isoformat()
            if stamp in seen:
                continue
            seen.add(stamp)
            deduped.append(rec)
        sat.records = deduped
        if sat.n_records >= 2:
            usable.append(sat)
    return sorted(usable, key=lambda s: s.norad)


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
# Pair construction
# --------------------------------------------------------------------------


def select_stale_partner(
    epochs: list[dt.datetime], j: int, target_h: float, lo_h: float, hi_h: float
) -> int | None:
    """Index of the older TLE inside the gap band whose gap is closest to target.

    Operational pairing: the terminal holds a TLE that is roughly target_h old
    and propagates it open-loop. Consecutive TLEs are not required.
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
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build accepted (stale, reference) sample blocks for one staleness band."""
    lo_h, hi_h = STALENESS_BANDS[target_h]
    epochs = sat.epochs()
    records = sat.records
    pairs: list[dict[str, Any]] = []
    rejected_mags: list[float] = []
    n_no_partner = n_sgp4_fail = 0
    step_s = PERIOD_SAMPLE_S / K_SAMPLES_PER_PAIR

    for j in range(len(records)):
        i = select_stale_partner(epochs, j, float(target_h), lo_h, hi_h)
        if i is None:
            n_no_partner += 1
            continue
        old, new = records[i], records[j]
        try:
            sat_old = Satrec.twoline2rv(old["line1"], old["line2"])
            sat_new = Satrec.twoline2rv(new["line1"], new["line2"])
        except Exception:
            n_sgp4_fail += 1
            continue

        gap_s = (epochs[j] - epochs[i]).total_seconds()
        rows_x: list[list[float]] = []
        rows_y: list[float] = []
        max_abs = 0.0
        failed = False
        for k in range(K_SAMPLES_PER_PAIR):
            t_abs = epochs[j] + dt.timedelta(seconds=k * step_s)
            age_s = (t_abs - epochs[i]).total_seconds()
            jd, fr = _jd_of(t_abs)
            gs_r, gs_v = _gs_teme_km(jd, fr, *gs)
            e_old, r_old, v_old = sat_old.sgp4(jd, fr)
            e_new, r_new, v_new = sat_new.sgp4(jd, fr)
            if e_old != 0 or e_new != 0:
                failed = True
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

        if failed:
            n_sgp4_fail += 1
            continue
        if max_abs > reject_hz:
            rejected_mags.append(max_abs)
            continue
        pairs.append(
            {
                "ref_epoch": epochs[j],
                "x": np.asarray(rows_x, dtype=float),
                "y": np.asarray(rows_y, dtype=float),
                "max_abs_hz": max_abs,
            }
        )

    stats = {
        "accepted_pairs": len(pairs),
        "rejected_pairs": len(rejected_mags),
        "rejected_max_abs_hz": sorted(
            (round(v, 3) for v in rejected_mags), reverse=True
        )[:10],
        "no_partner": n_no_partner,
        "sgp4_failures": n_sgp4_fail,
    }
    return pairs, stats


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
# Lightweight correctors
# --------------------------------------------------------------------------


def _mae(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a - b))) if a.size else float("nan")


def _standardize(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = x.mean(axis=0)
    sig = x.std(axis=0)
    sig[sig < 1e-12] = 1.0
    return mu, sig


def _ridge_weights(x: np.ndarray, y: np.ndarray, alpha: float) -> np.ndarray:
    xb = np.hstack([x, np.ones((x.shape[0], 1))])
    reg = alpha * np.eye(xb.shape[1])
    reg[-1, -1] = 0.0
    return np.linalg.solve(xb.T @ xb + reg, xb.T @ y)


def fit_correctors(
    x_tr: np.ndarray, y_tr: np.ndarray, x_va: np.ndarray, y_va: np.ndarray
) -> dict[str, Any]:
    """Fit every lightweight corrector. Returns name -> predict callable."""
    mu, sig = _standardize(x_tr)

    def _z(x: np.ndarray) -> np.ndarray:
        return (x - mu) / sig

    models: dict[str, Any] = {
        "zero": lambda x: np.zeros(x.shape[0]),
        "mean_bias": (lambda c: (lambda x: np.full(x.shape[0], c)))(
            float(np.mean(y_tr))
        ),
        "median_bias": (lambda c: (lambda x: np.full(x.shape[0], c)))(
            float(np.median(y_tr))
        ),
    }

    # Linear bias-rate: residual ~ a + b * TLE age.
    age = x_tr[:, 0]
    design = np.stack([age, np.ones_like(age)], axis=1)
    coef, *_ = np.linalg.lstsq(design, y_tr, rcond=None)
    models["linear_bias_rate"] = (
        lambda c: (lambda x: c[0] * x[:, 0] + c[1])
    )(coef)

    # Ridge over the full standardized feature vector; alpha picked on validation.
    best_alpha, best_va, best_w = None, None, None
    for alpha in RIDGE_ALPHAS:
        w = _ridge_weights(_z(x_tr), y_tr, alpha)
        pred_va = np.hstack([_z(x_va), np.ones((x_va.shape[0], 1))]) @ w
        score = _mae(pred_va, y_va)
        if best_va is None or score < best_va:
            best_alpha, best_va, best_w = alpha, score, w
    models["ridge"] = (
        lambda w: (lambda x: np.hstack([_z(x), np.ones((x.shape[0], 1))]) @ w)
    )(best_w)
    models["_ridge_alpha"] = best_alpha
    return models


def _pctl(values: np.ndarray, q: float) -> float | None:
    return float(np.percentile(np.abs(values), q)) if values.size else None


# --------------------------------------------------------------------------
# Matrix cell
# --------------------------------------------------------------------------


def evaluate_cell(
    source: SatelliteData,
    target: SatelliteData,
    staleness_h: int,
    args: argparse.Namespace,
    pair_cache: dict[tuple[str, int], tuple[list[dict], dict]],
) -> dict[str, Any]:
    """Fit on the source train segment; select and gate on target validation."""
    gs = (args.gs_lat, args.gs_lon, args.gs_alt)
    key_src = (source.key, staleness_h)
    if key_src not in pair_cache:
        pair_cache[key_src] = build_pairs(
            source, staleness_h, args.reject_hz, gs, args.carrier_hz
        )
    key_tgt = (target.key, staleness_h)
    if key_tgt not in pair_cache:
        pair_cache[key_tgt] = build_pairs(
            target, staleness_h, args.reject_hz, gs, args.carrier_hz
        )

    src_pairs, src_stats = pair_cache[key_src]
    tgt_pairs, tgt_stats = pair_cache[key_tgt]

    src_tr, _, _ = split_pairs(src_pairs, *split_boundaries(source))
    _, tgt_va, tgt_te = split_pairs(tgt_pairs, *split_boundaries(target))

    row: dict[str, Any] = {
        "train_source": source.key,
        "train_source_name": source.name,
        "deploy_target": target.key,
        "deploy_target_name": target.name,
        "relation": (
            "target_specific" if source.key == target.key else "cross_satellite"
        ),
        "staleness_h": staleness_h,
        "reject_hz": args.reject_hz,
        "n_train_pairs": len(src_tr),
        "n_val_pairs": len(tgt_va),
        "n_test_pairs": len(tgt_te),
        "rejected_pairs_source": src_stats["rejected_pairs"],
        "rejected_pairs_target": tgt_stats["rejected_pairs"],
        "n_train_samples": len(src_tr) * K_SAMPLES_PER_PAIR,
        "n_val_samples": len(tgt_va) * K_SAMPLES_PER_PAIR,
        "n_test_samples": len(tgt_te) * K_SAMPLES_PER_PAIR,
    }

    x_tr, y_tr = stack(src_tr)
    x_va, y_va = stack(tgt_va)
    x_te, y_te = stack(tgt_te)
    if (
        x_tr.shape[0] < MIN_TRAIN_SAMPLES
        or x_va.shape[0] < MIN_VAL_SAMPLES
        or x_te.shape[0] < MIN_TEST_SAMPLES
    ):
        row.update(
            {
                "status": "insufficient_pairs",
                "gate_decision": "unavailable",
                "selected_model": None,
            }
        )
        return row

    models = fit_correctors(x_tr, y_tr, x_va, y_va)
    val_mae: dict[str, float] = {}
    test_mae: dict[str, float] = {}
    for name in REFERENCE_MODELS + LEARNED_MODELS:
        val_mae[name] = _mae(models[name](x_va), y_va)
        test_mae[name] = _mae(models[name](x_te), y_te)

    selected = min(LEARNED_MODELS, key=lambda n: val_mae[n])
    mae_phys_val = val_mae["zero"]
    mae_ml_val = val_mae[selected]
    gate_open = bool(mae_ml_val < args.gamma * mae_phys_val)
    err_test = y_te - models[selected](x_te)

    row.update(
        {
            "status": "evaluated",
            "selected_model": selected,
            "ridge_alpha": models["_ridge_alpha"],
            "gamma": args.gamma,
            "val_mae_phys_hz": round(mae_phys_val, 6),
            "val_mae_ml_hz": round(mae_ml_val, 6),
            "gate_decision": "open" if gate_open else "closed",
            "baseline_test_mae_hz": round(test_mae["zero"], 6),
            "learned_test_mae_hz": round(test_mae[selected], 6),
            "degradation_pct": round(
                (test_mae[selected] / test_mae["zero"] - 1.0) * 100.0, 3
            )
            if test_mae["zero"] > 0
            else None,
            "deployed_test_mae_hz": round(
                test_mae[selected] if gate_open else test_mae["zero"], 6
            ),
            "p95_abs_error_hz": round(_pctl(err_test, 95) or float("nan"), 6),
            "p99_abs_error_hz": round(_pctl(err_test, 99) or float("nan"), 6),
            "p95_abs_residual_hz": round(_pctl(y_te, 95) or float("nan"), 6),
            "p99_abs_residual_hz": round(_pctl(y_te, 99) or float("nan"), 6),
        }
    )
    for name in REFERENCE_MODELS + LEARNED_MODELS:
        row[f"val_mae_{name}"] = round(val_mae[name], 6)
        row[f"test_mae_{name}"] = round(test_mae[name], 6)
    return row


def reject_sensitivity(
    sats: list[SatelliteData], args: argparse.Namespace
) -> list[dict[str, Any]]:
    """Pair acceptance and residual scale as the reject threshold varies."""
    gs = (args.gs_lat, args.gs_lon, args.gs_alt)
    rows: list[dict[str, Any]] = []
    for sat in sats:
        for staleness_h in args.staleness:
            for threshold in args.reject_sweep:
                pairs, stats = build_pairs(
                    sat, staleness_h, threshold, gs, args.carrier_hz
                )
                _, y = stack(pairs)
                rows.append(
                    {
                        "satellite": sat.key,
                        "satellite_name": sat.name,
                        "staleness_h": staleness_h,
                        "reject_hz": threshold,
                        "accepted_pairs": stats["accepted_pairs"],
                        "rejected_pairs": stats["rejected_pairs"],
                        "reject_rate_pct": round(
                            100.0
                            * stats["rejected_pairs"]
                            / max(1, stats["accepted_pairs"] + stats["rejected_pairs"]),
                            3,
                        ),
                        "residual_mae_hz": round(float(np.mean(np.abs(y))), 6)
                        if y.size
                        else None,
                        "residual_p99_hz": round(_pctl(y, 99) or float("nan"), 6)
                        if y.size
                        else None,
                        "top_rejected_max_abs_hz": stats["rejected_max_abs_hz"][:5],
                    }
                )
    return rows


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------


def write_csv(path: Path, rows: list[dict[str, Any]], header: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_metadata(
    args: argparse.Namespace, sats: list[SatelliteData], status: str
) -> dict[str, Any]:
    return {
        "campaign": "paper1_plus_multisat_generalization",
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
        "tle_dir": str(args.tle_dir),
        "ground_station": {
            "lat_deg": args.gs_lat,
            "lon_deg": args.gs_lon,
            "alt_m": args.gs_alt,
        },
        "carrier_hz": args.carrier_hz,
        "staleness_targets_h": list(args.staleness),
        "reject_hz": args.reject_hz,
        "reject_sweep_hz": list(args.reject_sweep),
        "gamma": args.gamma,
        "samples_per_pair": K_SAMPLES_PER_PAIR,
        "split": "chronological 60/20/20 by reference epoch",
        "gate_protocol": (
            "train fits candidates; validation selects the candidate and decides G; "
            "test only reports the consequence"
        ),
        "reference_models": list(REFERENCE_MODELS),
        "learned_models": list(LEARNED_MODELS),
        "heavy_models_excluded": "random forest / gradient boosting / MLP",
        "feature_names": list(FEATURE_NAMES),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tle-dir",
        type=Path,
        default=ROOT / "dataraw" / "spacetrack",
        help="directory of per-satellite historical TLE files (json / txt)",
    )
    parser.add_argument("--gs-lat", type=float, default=24.0)
    parser.add_argument("--gs-lon", type=float, default=121.0)
    parser.add_argument("--gs-alt", type=float, default=100.0)
    parser.add_argument("--carrier-hz", type=float, default=868e6)
    parser.add_argument(
        "--staleness",
        type=int,
        nargs="+",
        default=[8, 24, 48, 72, 96, 168],
        choices=sorted(STALENESS_BANDS),
    )
    parser.add_argument("--reject-hz", type=float, default=1500.0)
    parser.add_argument(
        "--reject-sweep",
        type=float,
        nargs="+",
        default=[150.0, 500.0, 1500.0, 5000.0],
        help="thresholds for the reject-sensitivity sweep",
    )
    parser.add_argument("--gamma", type=float, default=0.95)
    parser.add_argument(
        "--min-satellites",
        type=int,
        default=3,
        help="satellites required before any generalization claim or figure",
    )
    parser.add_argument("--out-dir", type=Path, default=HERE)
    args = parser.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    sats = discover_satellites(args.tle_dir)

    inventory = [
        {
            "key": s.key,
            "name": s.name,
            "norad": s.norad,
            "source_path": s.source_path,
            "n_records": s.n_records,
            "epoch_start": s.epochs()[0].isoformat(),
            "epoch_end": s.epochs()[-1].isoformat(),
            **s.gap_stats_h(),
        }
        for s in sats
    ]

    if not sats:
        meta = build_metadata(args, sats, "insufficient_data")
        payload = {
            "metadata": meta,
            "satellite_inventory": [],
            "matrix_rows": [],
            "per_satellite_rows": [],
            "reject_sensitivity_rows": [],
            "notes": [
                "No usable historical TLE archive was found under --tle-dir.",
                "No residual was computed and no generalization claim is made.",
                "Restore the local raw TLE archive and rerun to populate the matrix.",
            ],
        }
        (args.out_dir / "results.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        for name, header in (
            ("multisat_generalization_matrix.csv", MATRIX_HEADER),
            ("per_satellite_summary.csv", PER_SAT_HEADER),
            ("reject_sensitivity_summary.csv", REJECT_HEADER),
        ):
            write_csv(args.out_dir / name, [], header)
        print(
            f"insufficient_data: no usable TLE history under {args.tle_dir}; "
            "wrote empty artifacts, no claim made."
        )
        return 0

    pair_cache: dict[tuple[str, int], tuple[list[dict], dict]] = {}
    matrix_rows = [
        evaluate_cell(src, tgt, staleness_h, args, pair_cache)
        for src in sats
        for tgt in sats
        for staleness_h in args.staleness
    ]

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
                "median_gap_h": sat.gap_stats_h()["median_h"],
                "epoch_start": sat.epochs()[0].isoformat(),
                "epoch_end": sat.epochs()[-1].isoformat(),
                "target_specific_rows": len(own),
                "target_specific_gate_closed": len(closed),
                "target_specific_gate_open": len(own) - len(closed),
                "rejected_pairs_total": sum(
                    r["rejected_pairs_target"] for r in own
                ),
            }
        )

    reject_rows = reject_sensitivity(sats, args)

    meta = build_metadata(args, sats, "evaluated")
    meta["generalization_claim_supported"] = len(sats) >= args.min_satellites
    payload = {
        "metadata": meta,
        "satellite_inventory": inventory,
        "matrix_rows": matrix_rows,
        "per_satellite_rows": per_sat_rows,
        "reject_sensitivity_rows": reject_rows,
        "notes": [
            "All values are model-derived inter-TLE residuals; no measured RF truth.",
            "The gate is decided on validation; test columns report consequences only.",
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
    (args.out_dir / "results.json").write_text(
        json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8"
    )
    write_csv(
        args.out_dir / "multisat_generalization_matrix.csv", matrix_rows, MATRIX_HEADER
    )
    write_csv(args.out_dir / "per_satellite_summary.csv", per_sat_rows, PER_SAT_HEADER)
    write_csv(
        args.out_dir / "reject_sensitivity_summary.csv", reject_rows, REJECT_HEADER
    )
    print(
        f"evaluated {len(matrix_rows)} cells over {len(sats)} satellite(s); "
        f"generalization claim supported: {meta['generalization_claim_supported']}"
    )
    return 0


MATRIX_HEADER = [
    "train_source",
    "train_source_name",
    "deploy_target",
    "deploy_target_name",
    "relation",
    "staleness_h",
    "reject_hz",
    "status",
    "n_train_pairs",
    "n_val_pairs",
    "n_test_pairs",
    "n_train_samples",
    "n_val_samples",
    "n_test_samples",
    "rejected_pairs_source",
    "rejected_pairs_target",
    "selected_model",
    "ridge_alpha",
    "gamma",
    "val_mae_phys_hz",
    "val_mae_ml_hz",
    "gate_decision",
    "baseline_test_mae_hz",
    "learned_test_mae_hz",
    "degradation_pct",
    "deployed_test_mae_hz",
    "p95_abs_error_hz",
    "p99_abs_error_hz",
    "p95_abs_residual_hz",
    "p99_abs_residual_hz",
] + [
    f"{split}_mae_{name}"
    for split in ("val", "test")
    for name in REFERENCE_MODELS + LEARNED_MODELS
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
    "top_rejected_max_abs_hz",
]


if __name__ == "__main__":
    sys.exit(main())
