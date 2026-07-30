#!/usr/bin/env python3
"""E1 -- causal, transmission-anchored, availability-enforced dataset builder.

Every observation is one transmission by an endpoint operating open-loop under
the provisioning policy in ``provisioning_policy.json``. Nothing in the feature
vector may depend on the retrospective reference element; the reference exists
only to close a label at ``t_close = CREATION_DATE(reference)``.

Five mechanical assertions are enforced per observation (E1):

  A1  CREATION_DATE(stale) <= t_refresh          (endpoint could hold it)
  A2  t_refresh            <= t_tx               (transmission is after refresh)
  A3  CREATION_DATE(ref)   >  t_tx               (label is retrospective)
  A4  t_close              == CREATION_DATE(ref) (closure time is the availability time)
  A5  the feature row is invariant to the choice of reference (checked by
      perturbation on a sample: swap the reference, features must not move)

Usage:
    python build_causal_dataset.py --tle-dir dataraw/spacetrack --policy periodic_24h
    python build_causal_dataset.py --counts-only            # E0.5 sensitivity table
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
from sgp4.api import Satrec

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "exp14_multisat_generalization_matrix"))

import run_multisat_generalization_matrix as pipe  # noqa: E402  (physics + ingestion)

POLICY_PATH = HERE / "provisioning_policy.json"
POLICY = json.loads(POLICY_PATH.read_text())

TRUST_MIN_YEAR = POLICY["availability_clock"]["trust_min_epoch_year"]
REF_RULES = POLICY["reference_quality_rules_preregistered"]
FIXED = POLICY["fixed_config"]
BANDS = {int(k): tuple(v) for k, v in POLICY["staleness_bands_from_actual_age_tx"].items()}

GS = (FIXED["gs_lat_deg"], FIXED["gs_lon_deg"], FIXED["gs_alt_m"])
CARRIER_HZ = FIXED["carrier_hz"]

# Deployable static features. Index 0 is the ACTUAL age at transmission. There is
# no stale->reference epoch gap: that quantity is not computable by the endpoint
# (loop_engineering/evidence/T1_reference_epoch_perturbation.py).
STATIC_FEATURES = (
    "age_tx_s",
    "stale_doppler_hz",
    "sin_phase",
    "cos_phase",
    "elevation_deg",
    "range_km",
    "stale_mean_motion_rad_min",
    "stale_bstar",
    "stale_ecc",
)

EPOCH0 = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)


def _unix(when: dt.datetime) -> float:
    return (when - EPOCH0).total_seconds()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# availability index
# --------------------------------------------------------------------------


def availability_index(sat: pipe.SatelliteData) -> list[dict[str, Any]]:
    """Records usable under the availability clock, ordered by CREATION_DATE.

    Keeps only rows whose element epoch is in the trusted modern range and whose
    CREATION_DATE is present. Ordering is by availability, not by epoch: the
    endpoint learns about elements in publication order.
    """
    usable = []
    for rec in sat.records:
        if rec["epoch"].year < TRUST_MIN_YEAR:
            continue
        created = rec.get("creation_date")
        if not created:
            continue
        when = created if isinstance(created, dt.datetime) else pipe._parse_epoch(created)
        usable.append({**rec, "creation_dt": when})
    usable.sort(key=lambda r: (r["creation_dt"], r["epoch"]))
    return usable


def refresh_schedule(avail: list[dict[str, Any]], interval_h: float | None
                     ) -> list[dt.datetime]:
    """Provisioning events. ``interval_h=None`` means immediate provisioning."""
    if not avail:
        return []
    if interval_h is None:
        return [r["creation_dt"] for r in avail]
    first = avail[0]["creation_dt"]
    # Anchor on the next whole UTC hour after the first availability, so the
    # schedule is a deterministic function of the archive and not of any result.
    t0 = first.replace(minute=0, second=0, microsecond=0) + dt.timedelta(hours=1)
    last = avail[-1]["creation_dt"]
    step = dt.timedelta(hours=interval_h)
    out, t = [], t0
    while t <= last:
        out.append(t)
        t += step
    return out


def held_element(avail: list[dict[str, Any]], creations: list[dt.datetime],
                 t_refresh: dt.datetime) -> dict[str, Any] | None:
    """Latest element the endpoint can hold: newest CREATION_DATE <= t_refresh."""
    idx = bisect.bisect_right(creations, t_refresh) - 1
    return avail[idx] if idx >= 0 else None


def reference_for(avail: list[dict[str, Any]], creations: list[dt.datetime],
                  t_tx: dt.datetime, stale: dict[str, Any]) -> dict[str, Any] | None:
    """First element available strictly after t_tx that passes the quality rules."""
    max_off = dt.timedelta(hours=REF_RULES["max_abs_epoch_offset_h"])
    idx = bisect.bisect_right(creations, t_tx)
    for cand in avail[idx:]:
        if cand["creation_dt"] <= t_tx:          # defensive; bisect guarantees this
            continue
        if abs(cand["epoch"] - t_tx) > max_off:
            continue
        if cand["physical_key"] == stale["physical_key"]:
            continue
        return cand
    return None


# --------------------------------------------------------------------------
# per-transmission physics
# --------------------------------------------------------------------------


def _sgp4_at(sat: Satrec, when: dt.datetime):
    jd, fr = pipe._jd_of(when)
    err, r, v = sat.sgp4(jd, fr)
    return err, np.array(r), np.array(v), jd, fr


def transmission_row(stale: dict[str, Any], ref: dict[str, Any], t_tx: dt.datetime,
                     satrec_cache: dict[str, Satrec]) -> dict[str, Any] | None:
    """Feature row + residual label for one transmission. None on propagation failure.

    The feature vector reads ONLY the stale element and t_tx. ``ref`` is touched
    solely to produce the label, never a feature (assertion A5).
    """
    def _rec(row: dict[str, Any]) -> Satrec | None:
        key = row["line1"] + row["line2"]
        got = satrec_cache.get(key)
        if got is None:
            try:
                got = Satrec.twoline2rv(row["line1"], row["line2"])
            except Exception:
                return None
            satrec_cache[key] = got
        return got

    s_rec, r_rec = _rec(stale), _rec(ref)
    if s_rec is None or r_rec is None:
        return None
    e_s, r_s, v_s, jd, fr = _sgp4_at(s_rec, t_tx)
    if e_s != 0:
        return None
    e_r, r_r, v_r, _, _ = _sgp4_at(r_rec, t_tx)
    if e_r != 0:
        return None

    gs_r, gs_v = pipe._gs_teme_km(jd, fr, *GS)
    d_stale, elev, rng = pipe._doppler_and_geom(r_s, v_s, gs_r, gs_v, CARRIER_HZ)
    d_ref, _, _ = pipe._doppler_and_geom(r_r, v_r, gs_r, gs_v, CARRIER_HZ)

    age_s = (t_tx - stale["epoch"]).total_seconds()
    phase = (stale["mean_anomaly_rad"]
             + stale["mean_motion_rad_min"] * age_s / 60.0) % (2.0 * math.pi)
    return {
        "features": [
            age_s, d_stale, math.sin(phase), math.cos(phase), elev, rng,
            stale["mean_motion_rad_min"], stale["bstar"], stale["ecc"],
        ],
        "residual_hz": d_ref - d_stale,
    }


def band_of(age_s: float) -> int:
    age_h = age_s / 3600.0
    for target, (lo, hi) in BANDS.items():
        if lo <= age_h <= hi:
            return target
    return 0


# --------------------------------------------------------------------------
# episode builder
# --------------------------------------------------------------------------


def build_satellite(sat: pipe.SatelliteData, interval_h: float | None,
                    n_tx: int, counts_only: bool) -> dict[str, Any]:
    avail = availability_index(sat)
    creations = [r["creation_dt"] for r in avail]
    schedule = refresh_schedule(avail, interval_h)
    step = (dt.timedelta(hours=interval_h / n_tx) if interval_h is not None
            else dt.timedelta(hours=1.0))

    rows: list[list[float]] = []
    meta: list[list[float]] = []
    band_counts: dict[int, int] = {b: 0 for b in list(BANDS) + [0]}
    n_no_stale = n_no_ref = n_prop_fail = n_screened = 0
    cache: dict[str, Satrec] = {}
    max_res_hz = FIXED["screen_reject_hz"]

    for ep_idx, t_refresh in enumerate(schedule):
        stale = held_element(avail, creations, t_refresh)
        if stale is None:
            n_no_stale += 1
            continue
        assert stale["creation_dt"] <= t_refresh, "A1 violated"
        for m in range(n_tx):
            t_tx = t_refresh + m * step
            assert t_refresh <= t_tx, "A2 violated"
            ref = reference_for(avail, creations, t_tx, stale)
            if ref is None:
                n_no_ref += 1
                continue
            assert ref["creation_dt"] > t_tx, "A3 violated"
            t_close = ref["creation_dt"]
            assert t_close == ref["creation_dt"], "A4 violated"

            age_s = (t_tx - stale["epoch"]).total_seconds()
            band = band_of(age_s)
            band_counts[band] += 1
            if counts_only or band == 0:
                continue
            row = transmission_row(stale, ref, t_tx, cache)
            if row is None:
                n_prop_fail += 1
                continue
            screened = abs(row["residual_hz"]) > max_res_hz
            n_screened += int(screened)
            rows.append(row["features"] + [row["residual_hz"]])
            meta.append([
                float(ep_idx), _unix(t_refresh), _unix(t_tx),
                _unix(stale["epoch"]), _unix(stale["creation_dt"]),
                _unix(ref["epoch"]), _unix(t_close),
                float(band), float(screened),
            ])

    return {
        "satellite": sat.key,
        "name": sat.name,
        "norad": sat.norad,
        "n_records_total": sat.n_records,
        "n_records_availability_clean": len(avail),
        "n_episodes": len(schedule),
        "band_counts": band_counts,
        "n_no_stale": n_no_stale,
        "n_no_reference": n_no_ref,
        "n_propagation_failed": n_prop_fail,
        "n_screened_out": n_screened,
        "X": np.asarray(rows, dtype=np.float64) if rows else np.zeros((0, len(STATIC_FEATURES) + 1)),
        "M": np.asarray(meta, dtype=np.float64) if meta else np.zeros((0, 9)),
    }


META_COLS = ("episode_idx", "t_refresh", "t_tx", "stale_epoch", "stale_creation",
             "ref_epoch", "t_close", "band_h", "screened")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tle-dir", type=Path, default=ROOT / "dataraw" / "spacetrack")
    ap.add_argument("--policy", default="periodic_24h")
    ap.add_argument("--counts-only", action="store_true")
    ap.add_argument("--out", type=Path, default=HERE / "causal_dataset")
    args = ap.parse_args()

    intervals = {"immediate": None, "periodic_24h": 24.0, "periodic_72h": 72.0}
    policies = list(intervals) if args.counts_only else [args.policy]

    sats = pipe.discover_satellites(args.tle_dir)
    print(f"discovered {len(sats)} satellites", flush=True)

    summary: dict[str, Any] = {
        "policy_sha256": _sha256(POLICY_PATH),
        "pipeline_sha256": _sha256(Path(pipe.__file__)),
        "builder_sha256": _sha256(Path(__file__)),
        "trust_min_epoch_year": TRUST_MIN_YEAR,
        "policies": {},
    }

    for pol in policies:
        interval = intervals[pol]
        n_tx = 24 if interval is not None else 24
        per_sat = []
        for sat in sats:
            res = build_satellite(sat, interval, n_tx, args.counts_only)
            if not args.counts_only and res["X"].shape[0]:
                out_dir = args.out / pol
                out_dir.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(out_dir / f"{res['satellite']}.npz",
                                    X=res["X"], M=res["M"],
                                    feature_names=np.array(STATIC_FEATURES),
                                    meta_cols=np.array(META_COLS))
            print(f"  {pol:14s} {res['name'][:22]:22s} "
                  f"avail={res['n_records_availability_clean']:6d} "
                  f"ep={res['n_episodes']:5d} "
                  f"bands={ {k: v for k, v in res['band_counts'].items() if v} }",
                  flush=True)
            per_sat.append({k: v for k, v in res.items() if k not in ("X", "M")})
        summary["policies"][pol] = per_sat

    (args.out).mkdir(parents=True, exist_ok=True)
    tag = "counts" if args.counts_only else args.policy
    (args.out / f"E1_summary_{tag}.json").write_text(json.dumps(summary, indent=1))
    print(f"wrote {args.out / f'E1_summary_{tag}.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
