#!/usr/bin/env python3
"""R0 + R1 -- visible-pass transmission scheduling and the frozen row registry.

Transmissions are GENERATED from passes predicted by the held stale TLE. They are
never sampled on a UTC grid and filtered by elevation afterwards: that is the
defect which left 96.58 percent of the previous pilot below the endpoint horizon.

This module is deliberately ignorant of later catalogue solutions. It consults
only the held element, the transmission UTC, and the fixed ground station, so the
schedule it produces cannot move when the future catalogue changes (test V1).

Usage:
    python build_visible_registry.py --scenario NOMINAL
    python build_visible_registry.py --scenario DEGRADED
"""

from __future__ import annotations

import argparse
import bisect
import datetime as dt
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from sgp4.api import Satrec, jday

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "exp14_multisat_generalization_matrix"))
import run_multisat_generalization_matrix as pipe  # noqa: E402  (physics + ingestion)

SCHED = json.loads((HERE / "schedule_config.json").read_text())

PRIMARY_THRESHOLD_DEG = SCHED["visibility"]["primary_threshold_deg"]
DIAGNOSTIC_THRESHOLD_DEG = SCHED["visibility"]["diagnostic_threshold_deg"]
NORMALIZED_OFFSETS = tuple(SCHED["sampling"]["normalized_offsets"])
COARSE_STEP_S = SCHED["pass_finder"]["coarse_step_s"]
BISECT_TOL_S = SCHED["pass_finder"]["bisection_tolerance_s"]
BISECT_MAX = SCHED["pass_finder"]["bisection_max_iter"]
MIN_PASS_S = SCHED["pass_finder"]["min_pass_duration_s"]
TRUST_MIN_YEAR = SCHED["availability_clock"]["trust_min_epoch_year"]

FIXED = SCHED["fixed_config"]
GS = (FIXED["gs_lat_deg"], FIXED["gs_lon_deg"], FIXED["gs_alt_m"])
CARRIER_HZ = FIXED["carrier_hz"]
SCENARIOS = {s["name"]: s["refresh_interval_h"] for s in SCHED["scenarios"]}

EPOCH0 = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)

REGISTRY_FIELDS = (
    "tx_id", "pass_id", "episode_id", "satellite", "scenario",
    "t_refresh", "t_tx", "held_tle_id", "held_tle_epoch", "held_tle_creation",
    "pred_elevation_deg", "pred_range_km", "pred_stale_doppler_hz", "age_tx_s",
    "provisioning_policy", "sin_phase", "cos_phase",
    "stale_mean_motion_rad_min", "stale_bstar", "stale_ecc",
)


def _unix(when: dt.datetime) -> float:
    return (when - EPOCH0).total_seconds()


# --------------------------------------------------------------------------
# vectorized geometry -- the coarse scan must be cheap, per R0's no-brute-force
# --------------------------------------------------------------------------


def _jd_split(unix_s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    jd_total = unix_s / 86400.0 + 2_440_587.5
    jd = np.floor(jd_total - 0.5) + 0.5
    return jd, jd_total - jd


def _gs_teme_batch(jd: np.ndarray, fr: np.ndarray
                   ) -> tuple[np.ndarray, np.ndarray]:
    """Ground-station position and velocity in TEME km, vectorized over time."""
    lat, lon = math.radians(GS[0]), math.radians(GS[1])
    n = pipe.WGS84_A / math.sqrt(1.0 - pipe.WGS84_E2 * math.sin(lat) ** 2)
    r_ecef = np.array([
        (n + GS[2]) * math.cos(lat) * math.cos(lon),
        (n + GS[2]) * math.cos(lat) * math.sin(lon),
        (n * (1.0 - pipe.WGS84_E2) + GS[2]) * math.sin(lat),
    ])
    d = (jd + fr) - 2_451_545.0
    theta = np.radians((280.46061837 + 360.98564736629 * d) % 360.0)
    ct, st = np.cos(theta), np.sin(theta)
    x = (ct * r_ecef[0] - st * r_ecef[1]) * 1e-3
    y = (st * r_ecef[0] + ct * r_ecef[1]) * 1e-3
    z = np.full_like(x, r_ecef[2] * 1e-3)
    r = np.stack([x, y, z], axis=1)
    v = np.stack([-pipe.OMEGA_EARTH * y, pipe.OMEGA_EARTH * x,
                  np.zeros_like(x)], axis=1)
    return r, v


def geometry_series(satrec: Satrec, unix_s: np.ndarray
                    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(elevation_deg, range_km, doppler_hz, ok) from the HELD element only."""
    jd, fr = _jd_split(unix_s)
    err, r, v = satrec.sgp4_array(jd, fr)
    gs_r, gs_v = _gs_teme_batch(jd, fr)
    dr = r - gs_r
    rmag = np.linalg.norm(dr, axis=1)
    ok = (err == 0) & (rmag > 1.0) & np.isfinite(rmag)
    rmag_safe = np.where(ok, rmag, 1.0)
    rhat = dr / rmag_safe[:, None]
    up = gs_r / (np.linalg.norm(gs_r, axis=1)[:, None] + 1e-9)
    sin_e = np.clip(np.einsum("ij,ij->i", rhat, up), -1.0, 1.0)
    elev = np.degrees(np.arcsin(sin_e))
    rrate = np.einsum("ij,ij->i", v - gs_v, rhat)
    dopp = -CARRIER_HZ * rrate * 1e3 / pipe.C_LIGHT
    return elev, rmag, dopp, ok


def _elev_at(satrec: Satrec, t: float) -> float:
    e, _, _, ok = geometry_series(satrec, np.array([t]))
    return float(e[0]) if ok[0] else -90.0


# --------------------------------------------------------------------------
# R0 -- event-driven pass finder
# --------------------------------------------------------------------------


def pass_intervals(satrec: Satrec, t0: float, t1: float,
                   threshold_deg: float) -> list[tuple[float, float]]:
    """Predicted-visible intervals in [t0, t1), from the held element only.

    Coarse vectorized scan locates sign changes of (elevation - threshold); each
    crossing is then bisected to BISECT_TOL_S. Only intervals whose entry AND
    exit crossings both fall inside the window are returned: a pass truncated by
    the episode boundary has no observed crossing, so the pre-registered
    normalized offsets would not be well defined for it.
    """
    n = max(int(math.ceil((t1 - t0) / COARSE_STEP_S)) + 1, 2)
    grid = t0 + np.arange(n) * COARSE_STEP_S
    grid = grid[grid <= t1]
    if grid.size < 2:
        return []
    elev, _, _, ok = geometry_series(satrec, grid)
    f = np.where(ok, elev - threshold_deg, -1e3)

    def refine(t_below: float, t_above: float) -> float:
        """Bisect the threshold crossing bracketed by (below, above).

        Order-agnostic in time: `t_below` is the endpoint where elevation is under
        the threshold and `t_above` the one where it is over, whichever comes
        first chronologically. Returns the ABOVE-threshold side of the final
        bracket, so a sample placed at a normalized offset inside the interval can
        never fall below the threshold through bisection error alone.
        """
        lo, hi = t_below, t_above
        for _ in range(BISECT_MAX):
            if abs(hi - lo) <= BISECT_TOL_S:
                break
            m = 0.5 * (lo + hi)
            if _elev_at(satrec, m) - threshold_deg >= 0.0:
                hi = m
            else:
                lo = m
        return hi

    up = np.flatnonzero((f[:-1] < 0.0) & (f[1:] >= 0.0))
    dn = np.flatnonzero((f[:-1] >= 0.0) & (f[1:] < 0.0))
    out: list[tuple[float, float]] = []
    for i in up:
        # entry: grid[i] is below, grid[i+1] is above
        entry = refine(float(grid[i]), float(grid[i + 1]))
        later = dn[dn > i]
        if later.size == 0:
            continue                      # pass truncated by the episode boundary
        j = int(later[0])
        # exit: grid[j+1] is below, grid[j] is above
        exit_ = refine(float(grid[j + 1]), float(grid[j]))
        if exit_ - entry >= MIN_PASS_S:
            out.append((entry, exit_))
    return out


def schedule_transmissions(intervals: list[tuple[float, float]]
                           ) -> list[tuple[int, int, float]]:
    """(pass_index, offset_index, t_tx) at the pre-registered normalized offsets."""
    rows = []
    for p, (a, b) in enumerate(intervals):
        span = b - a
        for k, frac in enumerate(NORMALIZED_OFFSETS):
            rows.append((p, k, a + frac * span))
    return rows


# --------------------------------------------------------------------------
# availability and provisioning
# --------------------------------------------------------------------------


def load_satellites() -> list[pipe.SatelliteData]:
    return pipe.discover_satellites(ROOT / "dataraw" / "spacetrack")


def availability_index(sat: pipe.SatelliteData) -> list[dict[str, Any]]:
    """Records usable under the availability clock, ordered by CREATION_DATE."""
    usable = []
    for rec in sat.records:
        if rec["epoch"].year < TRUST_MIN_YEAR:
            continue
        created = rec.get("creation_date")
        if not created:
            continue
        when = (created if isinstance(created, dt.datetime)
                else pipe._parse_epoch(created))
        usable.append({**rec, "creation_dt": when})
    usable.sort(key=lambda r: (r["creation_dt"], r["epoch"]))
    return usable


def refresh_schedule(avail: list[dict[str, Any]], interval_h: float,
                     t_end: dt.datetime | None) -> list[dt.datetime]:
    if not avail:
        return []
    first = avail[0]["creation_dt"]
    t0 = first.replace(minute=0, second=0, microsecond=0) + dt.timedelta(hours=1)
    last = t_end or avail[-1]["creation_dt"]
    step = dt.timedelta(hours=interval_h)
    out, t = [], t0
    while t <= last:
        out.append(t)
        t += step
    return out


def held_element(avail: list[dict[str, Any]], creations: list[dt.datetime],
                 t_refresh: dt.datetime) -> dict[str, Any] | None:
    idx = bisect.bisect_right(creations, t_refresh) - 1
    return avail[idx] if idx >= 0 else None


# --------------------------------------------------------------------------
# R1 -- the frozen registry
# --------------------------------------------------------------------------


def build_registry(sat: pipe.SatelliteData, avail: list[dict[str, Any]],
                   scenario: str, t_end: dt.datetime | None = None,
                   threshold_deg: float | None = None) -> dict[str, np.ndarray]:
    """Schedule every transmission for one satellite under one scenario.

    Nothing in this function consults a later solution. Row membership is fixed
    here and is never revisited.
    """
    thr = PRIMARY_THRESHOLD_DEG if threshold_deg is None else threshold_deg
    interval_h = SCENARIOS[scenario]
    creations = [r["creation_dt"] for r in avail]
    sched = refresh_schedule(avail, interval_h, t_end)
    cache: dict[str, Satrec] = {}
    cols: dict[str, list] = {f: [] for f in REGISTRY_FIELDS}
    policy = f"periodic_{int(interval_h)}h_frozen_openloop"

    for ep_idx, t_refresh in enumerate(sched):
        stale = held_element(avail, creations, t_refresh)
        if stale is None:
            continue
        key = stale["line1"] + stale["line2"]
        rec = cache.get(key)
        if rec is None:
            try:
                rec = Satrec.twoline2rv(stale["line1"], stale["line2"])
            except Exception:
                continue
            cache[key] = rec
        t0 = _unix(t_refresh)
        t1 = t0 + interval_h * 3600.0
        intervals = pass_intervals(rec, t0, t1, thr)
        if not intervals:
            continue
        sched_rows = schedule_transmissions(intervals)
        times = np.array([t for _, _, t in sched_rows])
        elev, rng, dopp, ok = geometry_series(rec, times)
        ep_unix = _unix(stale["epoch"])
        cr_unix = _unix(stale["creation_dt"])
        tle_id = f"{sat.key}|{stale['epoch'].isoformat()}|{stale['physical_key'][:16]}"
        for (p, k, t_tx), e, rr, dd, good in zip(sched_rows, elev, rng, dopp, ok):
            if not good:
                continue
            age_s = t_tx - ep_unix
            phase = (stale["mean_anomaly_rad"]
                     + stale["mean_motion_rad_min"] * age_s / 60.0) % (2 * math.pi)
            pid = f"{sat.key}|{scenario}|{ep_idx}|{p}"
            cols["tx_id"].append(f"{pid}|{k}")
            cols["pass_id"].append(pid)
            cols["episode_id"].append(ep_idx)
            cols["satellite"].append(sat.name)
            cols["scenario"].append(scenario)
            cols["t_refresh"].append(t0)
            cols["t_tx"].append(t_tx)
            cols["held_tle_id"].append(tle_id)
            cols["held_tle_epoch"].append(ep_unix)
            cols["held_tle_creation"].append(cr_unix)
            cols["pred_elevation_deg"].append(e)
            cols["pred_range_km"].append(rr)
            cols["pred_stale_doppler_hz"].append(dd)
            cols["age_tx_s"].append(age_s)
            cols["provisioning_policy"].append(policy)
            cols["sin_phase"].append(math.sin(phase))
            cols["cos_phase"].append(math.cos(phase))
            cols["stale_mean_motion_rad_min"].append(stale["mean_motion_rad_min"])
            cols["stale_bstar"].append(stale["bstar"])
            cols["stale_ecc"].append(stale["ecc"])

    out: dict[str, np.ndarray] = {}
    for f, vals in cols.items():
        if f in ("tx_id", "pass_id", "satellite", "scenario", "held_tle_id",
                 "provisioning_policy"):
            out[f] = np.array(vals, dtype=object)
        elif f == "episode_id":
            out[f] = np.array(vals, dtype=np.int64)
        else:
            out[f] = np.array(vals, dtype=np.float64)
    return out


def registry_hash(reg: dict[str, np.ndarray]) -> str:
    """SHA-256 over a canonical serialization. Freezes row membership."""
    h = hashlib.sha256()
    for f in sorted(reg):
        h.update(f.encode())
        a = reg[f]
        if a.dtype == object:
            h.update("\x00".join(str(x) for x in a).encode())
        else:
            h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


def save_registry(reg: dict[str, np.ndarray], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {k: (v.astype(str) if v.dtype == object else v)
               for k, v in reg.items()}
    np.savez_compressed(path, **payload)
    return registry_hash(reg)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", choices=sorted(SCENARIOS), required=True)
    ap.add_argument("--threshold-deg", type=float, default=None)
    ap.add_argument("--out", type=Path, default=HERE / "registry")
    args = ap.parse_args()

    thr = args.threshold_deg or PRIMARY_THRESHOLD_DEG
    tag = f"{args.scenario}_thr{int(thr)}"
    summary: dict[str, Any] = {"scenario": args.scenario, "threshold_deg": thr,
                              "config_sha256": hashlib.sha256(
                                  (HERE / "schedule_config.json").read_bytes()
                              ).hexdigest(), "satellites": []}
    for sat in load_satellites():
        avail = availability_index(sat)
        if len(avail) < 30:
            print(f"  skip {sat.name}: {len(avail)} availability-clean elements",
                  flush=True)
            continue
        reg = build_registry(sat, avail, args.scenario, threshold_deg=thr)
        if reg["tx_id"].size == 0:
            print(f"  skip {sat.name}: no predicted-visible passes", flush=True)
            continue
        h = save_registry(reg, args.out / tag / f"{sat.key}.npz")
        n_pass = len(set(reg["pass_id"].tolist()))
        n_ep = len(set(reg["episode_id"].tolist()))
        print(f"  {sat.name[:22]:22s} tx={reg['tx_id'].size:7d} passes={n_pass:6d} "
              f"episodes={n_ep:5d} elev[min/med]="
              f"{reg['pred_elevation_deg'].min():5.2f}/"
              f"{np.median(reg['pred_elevation_deg']):5.2f} sha={h[:12]}", flush=True)
        summary["satellites"].append({
            "satellite": sat.name, "key": sat.key,
            "n_transmissions": int(reg["tx_id"].size), "n_passes": n_pass,
            "n_episodes": n_ep, "registry_sha256": h,
            "elev_min": round(float(reg["pred_elevation_deg"].min()), 4),
            "elev_median": round(float(np.median(reg["pred_elevation_deg"])), 4),
            "age_h_p50": round(float(np.percentile(reg["age_tx_s"], 50)) / 3600.0, 3),
            "age_h_p90": round(float(np.percentile(reg["age_tx_s"], 90)) / 3600.0, 3),
            "age_h_max": round(float(reg["age_tx_s"].max()) / 3600.0, 3),
        })
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / f"R1_registry_summary_{tag}.json").write_text(
        json.dumps(summary, indent=1))
    print(f"wrote {args.out / f'R1_registry_summary_{tag}.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
