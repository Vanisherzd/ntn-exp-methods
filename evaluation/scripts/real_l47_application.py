#!/usr/bin/env python3
"""Apply the FROZEN L4.7 rule to real Space-Track catalogue data.

Protocol declared in evaluation/real_data/PREREGISTRATION.md, committed before this file
existed. Nothing here is tunable: the window, ground station, elevation mask, sample interval,
propagation horizon and the observable for each analysis all come from that document.

L4.7 is imported from contract_layers unchanged and called with its defaults. No argument is
overridden. If a design cannot support a decision the reported result is INDETERMINATE.

SGP4 is used for GEOMETRY ONLY -- to decide when an object is above the elevation mask and at
what elevation. No propagation error, truth reference, residual or model is computed anywhere in
this file. It does not reopen the stopped residual-learning line.

Run: python evaluation/scripts/real_l47_application.py
Writes: evaluation/real_data/l47_real_application.json
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evaluation" / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import contract_layers as CL          # noqa: E402  -- FROZEN, imported unchanged
import numpy as np                    # noqa: E402
from sgp4.api import Satrec, SatrecArray  # noqa: E402

DATA = ROOT / "dataraw" / "spacetrack"
OUT = ROOT / "evaluation" / "real_data" / "l47_real_application.json"

# ---- everything below is fixed by PREREGISTRATION.md ------------------------------
WINDOW = ("2026-07-22", "2026-07-27")     # [inclusive, exclusive) on EPOCH
STATION_LAT_DEG = 24.7961                 # Hsinchu, Taiwan
STATION_LON_DEG = 120.9967
STATION_ALT_M = 100.0
ELEV_MASK_DEG = 10.0
SAMPLE_S = 30
HORIZON_H = 24
WGS84_A_KM = 6378.137
WGS84_F = 1.0 / 298.257223563
# ----------------------------------------------------------------------------------


def _iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "")).replace(tzinfo=timezone.utc)


def load_records() -> dict[str, list[dict]]:
    """Element sets per object whose EPOCH falls in the declared window."""
    out: dict[str, list[dict]] = {}
    for d in sorted(glob.glob(str(DATA / "*/"))):
        obj = os.path.basename(d.rstrip("/"))
        hits = glob.glob(os.path.join(d, "gp_history_*.json"))
        if not hits:
            continue
        recs = [r for r in json.load(open(hits[0]))
                if WINDOW[0] <= r["EPOCH"][:10] < WINDOW[1]]
        recs.sort(key=lambda r: r["EPOCH"])
        if recs:
            out[obj] = recs
    return out


def station_ecef_km() -> np.ndarray:
    lat, lon = np.radians(STATION_LAT_DEG), np.radians(STATION_LON_DEG)
    e2 = WGS84_F * (2 - WGS84_F)
    n = WGS84_A_KM / np.sqrt(1 - e2 * np.sin(lat) ** 2)
    h = STATION_ALT_M / 1000.0
    return np.array([(n + h) * np.cos(lat) * np.cos(lon),
                     (n + h) * np.cos(lat) * np.sin(lon),
                     (n * (1 - e2) + h) * np.sin(lat)])


def gmst_rad(jd: np.ndarray) -> np.ndarray:
    """IAU-82 GMST, adequate for an above-mask visibility decision."""
    t = (jd - 2451545.0) / 36525.0
    s = (67310.54841 + (876600.0 * 3600 + 8640184.812866) * t
         + 0.093104 * t * t - 6.2e-6 * t ** 3)
    return np.radians((s % 86400.0) / 240.0)


def elevations_deg(rec: dict) -> tuple[np.ndarray, np.ndarray]:
    """Elevation of the object above the declared station, sampled over the horizon.

    Returns (elevation_deg, seconds_since_epoch). TEME -> ECEF by GMST rotation only;
    polar motion and nutation are far below the resolution an elevation mask needs.
    """
    sat = Satrec.twoline2rv(rec["TLE_LINE1"], rec["TLE_LINE2"])
    n = int(HORIZON_H * 3600 // SAMPLE_S)
    secs = np.arange(n, dtype=float) * SAMPLE_S
    jd0 = sat.jdsatepoch + sat.jdsatepochF
    jd = jd0 + secs / 86400.0
    e, r, _ = SatrecArray([sat]).sgp4(jd, np.zeros_like(jd))
    r = r[0]                                    # (n, 3) TEME km
    ok = e[0] == 0
    th = gmst_rad(jd)
    c, s = np.cos(th), np.sin(th)
    ecef = np.column_stack([c * r[:, 0] + s * r[:, 1],
                            -s * r[:, 0] + c * r[:, 1],
                            r[:, 2]])
    site = station_ecef_km()
    los = ecef - site
    lat, lon = np.radians(STATION_LAT_DEG), np.radians(STATION_LON_DEG)
    up = np.array([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])
    rng = np.linalg.norm(los, axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        el = np.degrees(np.arcsin(np.clip(los @ up / rng, -1.0, 1.0)))
    el[~ok] = np.nan
    return el, secs


def passes_for(rec: dict) -> list[np.ndarray]:
    """Contiguous above-mask runs. Each run is one visible pass; its samples are its rows."""
    el, _ = elevations_deg(rec)
    above = np.nan_to_num(el, nan=-90.0) >= ELEV_MASK_DEG
    out, start = [], None
    for i, a in enumerate(above):
        if a and start is None:
            start = i
        elif not a and start is not None:
            out.append(el[start:i]); start = None
    if start is not None:
        out.append(el[start:])
    # A single sample is not a pass at 30 s resolution.
    return [p for p in out if p.size >= 2]


def run_l47(values, unit_ids, coarser_ids, label: str) -> dict:
    """Call the FROZEN rule. A raised ContractViolation is a HALT, which is a result."""
    n_units = len(set(unit_ids))
    base = {"analysis": label, "n_samples": len(values), "n_units": n_units,
            "n_labelled_coarser": len(set(coarser_ids))}
    if n_units == 0:
        return {**base, "verdict": "INDETERMINATE", "icc": None, "p_value": None,
                "reason": "no units in this design"}
    try:
        v = CL.check_statistical_unit(values, unit_ids, coarser_ids)
        return {**base, **v}
    except CL.ContractViolation as exc:
        # The rule fired. Recompute the statistic for the record -- the exception carries it
        # as text, and a number parsed out of a message is not evidence.
        import orbit_evidence.experiment_contract.experiment_contract as EC
        u, agg = EC.aggregate_repeated_measures(list(values), list(unit_ids))
        cmap: dict = {}
        for a, b in zip(unit_ids, coarser_ids):
            cmap.setdefault(a, b)
        grp = np.array([cmap[k] for k in u.tolist()])
        icc = float(EC.within_group_icc(agg, grp))
        return {**base, "verdict": "HALT", "icc": round(icc, 4),
                "n_coarser_groups": len({str(g) for g in grp.tolist()
                                         if np.sum(grp.astype(str) == str(g)) >= 2}),
                "message": str(exc)}


def main() -> int:
    recs = load_records()
    manifest = {
        "protocol": "evaluation/real_data/PREREGISTRATION.md",
        "contract_layers_sha256": hashlib.sha256(
            (ROOT / "evaluation" / "scripts" / "contract_layers.py").read_bytes()).hexdigest(),
        "l47_defaults_used": {"alpha": 0.05, "n_perm": 400,
                              "min_coarser_groups": 4, "seed": 0},
        "window_epoch": list(WINDOW),
        "station": {"lat_deg": STATION_LAT_DEG, "lon_deg": STATION_LON_DEG,
                    "alt_m": STATION_ALT_M, "elev_mask_deg": ELEV_MASK_DEG},
        "sample_interval_s": SAMPLE_S, "horizon_h": HORIZON_H,
        "objects": {k: len(v) for k, v in recs.items()},
        "n_objects": len(recs),
        "n_element_sets": sum(len(v) for v in recs.items().__iter__().__next__()[1:][0:0]) or
                          sum(len(v) for v in recs.values()),
    }

    results: dict = {"manifest": manifest, "analyses": {}}

    # ---- A: unit = element set, coarser = object, observable = publication lag -----
    vals, units, coarse = [], [], []
    for obj, rs in recs.items():
        for r in rs:
            lag = (_iso(r["CREATION_DATE"]) - _iso(r["EPOCH"])).total_seconds() / 3600.0
            vals.append(lag)
            units.append(f"{obj}|{r['EPOCH']}")
            coarse.append(obj)
    results["analyses"]["A_elementset_in_object__publication_lag"] = run_l47(
        vals, units, coarse, "A: element set -> object, publication lag (h)")

    # ---- B and C: passes from SGP4 geometry ----------------------------------------
    pass_rows: list[dict] = []
    for obj, rs in recs.items():
        for r in rs:
            for j, p in enumerate(passes_for(r)):
                pass_rows.append({"object": obj, "elset": f"{obj}|{r['EPOCH']}",
                                  "pass_id": f"{obj}|{r['EPOCH']}|{j}",
                                  "elev": p})
    manifest["n_passes_total"] = len(pass_rows)
    manifest["n_pass_samples_total"] = int(sum(p["elev"].size for p in pass_rows))

    def flatten(rows, coarser_key):
        v, u, c = [], [], []
        for row in rows:
            v.extend(row["elev"].tolist())
            u.extend([row["pass_id"]] * row["elev"].size)
            c.extend([row[coarser_key]] * row["elev"].size)
        return v, u, c

    # B pooled and per object
    results["analyses"]["B_pass_in_elementset__elevation_pooled"] = run_l47(
        *flatten(pass_rows, "elset"), "B pooled: pass -> element set, elevation (deg)")
    per_b = {}
    for obj in recs:
        rows = [p for p in pass_rows if p["object"] == obj]
        per_b[obj] = run_l47(*flatten(rows, "elset"), f"B[{obj}]: pass -> element set")
    results["analyses"]["B_per_object"] = per_b

    # C: same units, DIFFERENT declared coarser level -- the sensitivity analysis
    results["analyses"]["C_pass_in_object__elevation_pooled"] = run_l47(
        *flatten(pass_rows, "object"), "C pooled: pass -> object, elevation (deg)")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=1, default=str) + "\n")

    # ---- report -------------------------------------------------------------------
    def line(tag, r):
        icc = "n/a" if r.get("icc") is None else f"{r['icc']:.3f}"
        pv = r.get("p_value")
        pv = "n/a" if pv is None else f"{pv:.4f}"
        print(f"  {tag:34s} {r['verdict']:14s} units={r['n_units']:5d} "
              f"groups={r.get('n_coarser_groups', '-'):>3} ICC={icc:>7s} p={pv:>7s}")

    print(f"objects {manifest['n_objects']}  element sets {manifest['n_element_sets']}  "
          f"passes {manifest['n_passes_total']}  "
          f"pass samples {manifest['n_pass_samples_total']}")
    print("\nfrozen L4.7 on real catalogue data:")
    line("A elset->object (pub lag)", results["analyses"]["A_elementset_in_object__publication_lag"])
    line("B pass->elset (elev, pooled)", results["analyses"]["B_pass_in_elementset__elevation_pooled"])
    line("C pass->object (elev, pooled)", results["analyses"]["C_pass_in_object__elevation_pooled"])
    print("\nB per object:")
    for obj, r in per_b.items():
        line(obj, r)
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
