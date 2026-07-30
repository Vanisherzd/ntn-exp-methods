#!/usr/bin/env python3
"""v2.2 controlled evidence-gate benchmark simulator.

Implements `physical_config.json` v2.2 exactly. Written for the FINAL MECHANICAL
QUALIFICATION PROBE: it answers only whether the benchmark is mechanically
coherent, falsifiable, causal, paired and physically bounded.

The residual is never prescribed in the frequency domain. It exists only as

    r(t) = D(truth, t) - D(held, t)

with truth and held propagated independently by SGP4.

ONE truth stream. The shift is a step in the persistent OD error carried by the
held element, not a change to the truth, so nothing accumulates without bound and
no absorption rule is needed.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from sgp4.api import Satrec, WGS72

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "physical_config.json").read_text())

MU = 398600.4418
J2 = 1.08262668e-3
RE = 6378.137
WGS84_A = 6378137.0
WGS84_E2 = 0.006694379990141317
WGS84_F = 1.0 / 298.257223563
OMEGA_E = 7.292115e-5
C_LIGHT = 299792458.0

FX = CFG["fixed_config"]
GS = (FX["gs_lat_deg"], FX["gs_lon_deg"], FX["gs_alt_m"])
CARRIER = FX["carrier_hz"]
MASK = FX["elevation_mask_deg"]
MIN_PASS_S = FX["min_pass_duration_s"]
COARSE_S = FX["coarse_scan_step_s"]
BISECT_TOL_S = FX["bisection_tolerance_s"]
OFFSETS = tuple(CFG["within_pass_sampling"]["offsets"])
REFRESH_H = CFG["refresh_semantics"]["refresh_interval_h"]
RUN_DAYS = FX["run_duration_days"]
SPLIT = FX["split"]
GAMMA = FX["gamma"]
DOPPLER_RATE_STEP_S = CFG["features"]["doppler_rate_audit"]["frozen_numerical_settings"]["step_s"]

TP = CFG["true_element_process"]
GRID_H = TP["true_element_interval_h"]
NDOT_SEC = TP["secular_ndot_rev_per_day2"]
OU_N_SIG = TP["ou_n_sigma_rev_per_day"]
OU_N_TAU_H = TP["ou_n_tau_h"]
OU_B_SIG = TP["ou_b_sigma_frac"]
OU_B_TAU_H = TP["ou_b_tau_h"]

DELTA = CFG["injected_od_error_Delta"]["nominal_magnitudes"]
DV_CM_S = CFG["shift_manoeuvre"]["delta_v_cm_s"]
REGIMES = CFG["regimes"]
STALENESS_H = CFG["staleness_levels_h"]
TL = CFG["timeline"]

FEATURE_NAMES = tuple(f["name"] for f in CFG["features"]["static_deployable"])
EPOCH_JD_0 = 2460000.5


# --------------------------------------------------------------------------
# geometry -- geodetic vertical, vectorized
# --------------------------------------------------------------------------


def _jd_split(unix_s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    jt = unix_s / 86400.0 + 2440587.5
    jd = np.floor(jt - 0.5) + 0.5
    return jd, jt - jd


def _gmst(jd: np.ndarray, fr: np.ndarray) -> np.ndarray:
    d = (jd + fr) - 2451545.0
    return np.radians((280.46061837 + 360.98564736629 * d) % 360.0)


def _gs_teme(jd: np.ndarray, fr: np.ndarray
             ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Ground station position, velocity, and GEODETIC up-vector, all TEME km."""
    lat, lon = math.radians(GS[0]), math.radians(GS[1])
    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * math.sin(lat) ** 2)
    r_ecef = np.array([(n + GS[2]) * math.cos(lat) * math.cos(lon),
                       (n + GS[2]) * math.cos(lat) * math.sin(lon),
                       (n * (1.0 - WGS84_E2) + GS[2]) * math.sin(lat)])
    # geodetic normal in ECEF: the ellipsoid normal at geodetic latitude
    up_ecef = np.array([math.cos(lat) * math.cos(lon),
                        math.cos(lat) * math.sin(lon),
                        math.sin(lat)])
    th = _gmst(jd, fr)
    ct, st = np.cos(th), np.sin(th)

    def rot(v):
        return np.stack([ct * v[0] - st * v[1], st * v[0] + ct * v[1],
                         np.full_like(ct, v[2])], axis=1)

    r = rot(r_ecef) * 1e-3
    up = rot(up_ecef)
    v = np.stack([-OMEGA_E * r[:, 1], OMEGA_E * r[:, 0], np.zeros_like(ct)], axis=1)
    return r, v, up


def geometry(sat: Satrec, unix_s: np.ndarray
             ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(elevation_deg, range_km, doppler_hz, ok). Geodetic elevation."""
    jd, fr = _jd_split(np.atleast_1d(unix_s))
    err, r, v = sat.sgp4_array(jd, fr)
    r, v = np.asarray(r), np.asarray(v)
    gr, gv, up = _gs_teme(jd, fr)
    dr = r - gr
    rm = np.linalg.norm(dr, axis=1)
    ok = (np.asarray(err) == 0) & (rm > 1.0) & np.isfinite(rm)
    rh = dr / np.where(ok, rm, 1.0)[:, None]
    el = np.degrees(np.arcsin(np.clip(np.einsum("ij,ij->i", rh, up), -1.0, 1.0)))
    rr = np.einsum("ij,ij->i", v - gv, rh)
    return el, rm, -CARRIER * rr * 1e3 / C_LIGHT, ok


def doppler_rate(sat: Satrec, t: np.ndarray) -> np.ndarray:
    """Central finite difference, frozen step. Held state + UTC + GS only."""
    h = DOPPLER_RATE_STEP_S
    _, _, dp, _ = geometry(sat, np.asarray(t) + h)
    _, _, dm, _ = geometry(sat, np.asarray(t) - h)
    return (dp - dm) / (2.0 * h)


# --------------------------------------------------------------------------
# event-driven pass finder
# --------------------------------------------------------------------------


def pass_intervals(sat: Satrec, t0: float, t1: float,
                   thr: float = MASK) -> list[tuple[float, float]]:
    n = max(int(math.ceil((t1 - t0) / COARSE_S)) + 1, 2)
    g = t0 + np.arange(n) * COARSE_S
    g = g[g <= t1]
    if g.size < 2:
        return []
    el, _, _, ok = geometry(sat, g)
    f = np.where(ok, el - thr, -1e3)

    def bisect(below: np.ndarray, above: np.ndarray) -> np.ndarray:
        lo, hi = below.copy(), above.copy()
        for _ in range(30):
            if np.all(np.abs(hi - lo) <= BISECT_TOL_S):
                break
            m = 0.5 * (lo + hi)
            el_m, _, _, ok_m = geometry(sat, m)
            up_side = ok_m & (el_m - thr >= 0.0)
            hi = np.where(up_side, m, hi)
            lo = np.where(up_side, lo, m)
        return hi                      # always the above-threshold side

    ui = np.flatnonzero((f[:-1] < 0.0) & (f[1:] >= 0.0))
    di = np.flatnonzero((f[:-1] >= 0.0) & (f[1:] < 0.0))
    if ui.size == 0 or di.size == 0:
        return []
    pairs = [(int(i), int(di[di > i][0])) for i in ui if np.any(di > i)]
    if not pairs:
        return []
    entry = bisect(g[[p[0] for p in pairs]], g[[p[0] + 1 for p in pairs]])
    exit_ = bisect(g[[p[1] + 1 for p in pairs]], g[[p[1] for p in pairs]])
    return [(float(a), float(b)) for a, b in zip(entry, exit_)
            if b - a >= MIN_PASS_S]


# --------------------------------------------------------------------------
# OU and the truth element sequence
# --------------------------------------------------------------------------


def ou_path(n: int, dt_h: float, sigma: float, tau_h: float,
            rng: np.random.Generator) -> np.ndarray:
    """Exact discrete Ornstein-Uhlenbeck, stationary variance sigma^2."""
    a = math.exp(-dt_h / tau_h)
    s = sigma * math.sqrt(max(1.0 - a * a, 1e-15))
    x = np.empty(n)
    x[0] = rng.normal(0.0, sigma)
    e = rng.normal(0.0, 1.0, n)
    for i in range(1, n):
        x[i] = a * x[i - 1] + s * e[i]
    return x


def _secular_rates(n_rad_min: float, ecc: float, incl_rad: float
                   ) -> tuple[float, float]:
    """J2 secular dRAAN/dt and dargp/dt, rad per minute."""
    a = (MU / ((n_rad_min / 60.0) ** 2)) ** (1.0 / 3.0)
    p = a * (1.0 - ecc * ecc)
    k = 1.5 * J2 * (RE / p) ** 2 * n_rad_min
    ci = math.cos(incl_rad)
    return -k * ci, 0.5 * k * (5.0 * ci * ci - 1.0)


def _mk(n_rev_day: float, incl_deg: float, ecc: float, bstar: float,
        ma_rad: float, raan_rad: float, argp_rad: float,
        epoch_jd: float) -> Satrec:
    s = Satrec()
    s.sgp4init(WGS72, 'i', 99999, epoch_jd - 2433281.5, bstar, 0.0, 0.0,
               ecc, argp_rad % (2 * math.pi), math.radians(incl_deg),
               ma_rad % (2 * math.pi), n_rev_day * 2 * math.pi / 1440.0,
               raan_rad % (2 * math.pi))
    return s


@dataclass
class TruthSequence:
    """Truth elements on a 6 h grid. M integrated continuously; RAAN/argp at J2."""
    regime: str
    epochs_unix: np.ndarray
    sats: list = field(repr=False)
    n_series: np.ndarray = field(repr=False)
    ma: np.ndarray = field(repr=False, default=None)
    raan: np.ndarray = field(repr=False, default=None)
    argp: np.ndarray = field(repr=False, default=None)

    def at(self, t: np.ndarray) -> np.ndarray:
        """Index of the element whose epoch is nearest each t."""
        return np.clip(np.searchsorted(self.epochs_unix, t) , 0,
                       self.epochs_unix.size - 1)


def build_truth(regime: str, seed: int, ou_on: bool = True) -> TruthSequence:
    rg = REGIMES[regime]
    rng = np.random.default_rng(seed)
    # The grid must start early enough to cover every held-element epoch
    # t_ep = t_q - S, whose minimum is t0 - max(staleness).
    lead_h = max(STALENESS_H.values()) + 2 * GRID_H
    n_steps = int((RUN_DAYS * 24.0 + lead_h) / GRID_H) + 2
    t0 = (EPOCH_JD_0 - 2440587.5) * 86400.0
    grid0 = t0 - lead_h * 3600.0
    eps = grid0 + np.arange(n_steps) * GRID_H * 3600.0

    days = (eps - t0) / 86400.0
    n_ser = rg["n_rev_day"] + NDOT_SEC * days
    b_ser = np.full(n_steps, rg["bstar"])
    if ou_on:
        n_ser = n_ser + ou_path(n_steps, GRID_H, OU_N_SIG, OU_N_TAU_H, rng)
        b_ser = b_ser * (1.0 + ou_path(n_steps, GRID_H, OU_B_SIG, OU_B_TAU_H, rng))

    incl = math.radians(rg["incl_deg"])
    ma, raan, argp = math.radians(10.0), math.radians(40.0), math.radians(30.0)
    sats, ma_s, ra_s, ap_s = [], [], [], []
    # angles are initialised at the GRID start (before t0) and integrated forward
    step_min = GRID_H * 60.0
    for k in range(n_steps):
        n_rad_min = n_ser[k] * 2 * math.pi / 1440.0
        sats.append(_mk(n_ser[k], rg["incl_deg"], rg["ecc"], b_ser[k],
                        ma, raan, argp, 2440587.5 + eps[k] / 86400.0))
        ma_s.append(ma); ra_s.append(raan); ap_s.append(argp)
        dr, da = _secular_rates(n_rad_min, rg["ecc"], incl)
        ma += n_rad_min * step_min       # continuous mean-anomaly integration
        raan += dr * step_min
        argp += da * step_min
    return TruthSequence(regime, eps, sats, n_ser,
                         np.asarray(ma_s), np.asarray(ra_s), np.asarray(ap_s))


def held_element(regime: str, epoch_unix: float, delta_n_eff: float,
                 signs: dict[str, float], truth: "TruthSequence") -> Satrec:
    """Fitted OD solution at epoch_unix.

    An orbit-determination solution knows WHERE the satellite is at its own epoch;
    its error is in the RATE. So the held element inherits the truth's mean anomaly,
    node and perigee at its own epoch and carries error only in mean motion, drag and
    inclination. NO OU sample enters the mean motion -- a catalogue element's n is a
    fitted quantity, not an instantaneous drag-state reading.

    Refresh (24 h), the truth grid (6 h) and every staleness level (6/24/72 h) are
    commensurate, so epoch_unix always lands exactly on a truth grid point.
    """
    rg = REGIMES[regime]
    t0 = (EPOCH_JD_0 - 2440587.5) * 86400.0
    days = (epoch_unix - t0) / 86400.0
    k = int(round((epoch_unix - truth.epochs_unix[0]) / (GRID_H * 3600.0)))
    k = max(0, min(k, truth.epochs_unix.size - 1))
    assert abs(truth.epochs_unix[k] - epoch_unix) < 1.0, "held epoch off the truth grid"
    n_held = rg["n_rev_day"] + NDOT_SEC * days + delta_n_eff
    b_held = rg["bstar"] * (1.0 + signs["b"] * DELTA["delta_bstar_frac"])
    i_held = rg["incl_deg"] + signs["i"] * DELTA["delta_incl_deg"]
    return _mk(n_held, i_held, rg["ecc"], b_held,
               float(truth.ma[k]), float(truth.raan[k]), float(truth.argp[k]),
               EPOCH_JD_0 + days)


# --------------------------------------------------------------------------
# run construction
# --------------------------------------------------------------------------

META = ("t_tx", "pass_id", "episode", "age_s", "fold", "post_onset")


def delta_n_true(regime: str) -> float:
    rg = REGIMES[regime]
    a = (MU / ((rg["n_rev_day"] * 2 * math.pi / 86400.0) ** 2)) ** (1.0 / 3.0)
    v = math.sqrt(MU / a)
    dv = DV_CM_S / 1e5                        # cm/s -> km/s
    da = 2.0 * a * dv / v
    return -1.5 * rg["n_rev_day"] * da / a


def build_run(regime: str, staleness: str, condition: str, base_seed: int
              ) -> dict[str, Any]:
    """One run. C1/C2/C3 share everything but the onset; N0 sets Delta = 0."""
    S_h = STALENESS_H[staleness]
    rng = np.random.default_rng(base_seed)
    sgn = {k: float(rng.choice([-1.0, 1.0])) for k in ("n", "b", "i")}
    rng_state_hash = hashlib.sha256(
        f"{sgn['n']}|{sgn['b']}|{sgn['i']}".encode()).hexdigest()[:16]

    is_n0 = condition == "N0"
    truth = build_truth(regime, base_seed, ou_on=True)
    dn0 = 0.0 if is_n0 else sgn["n"] * DELTA["delta_n_rev_per_day"]
    dn_post = dn0 - delta_n_true(regime) if condition in ("C2", "C3") else dn0
    zero_signs = {"n": 0.0, "b": 0.0, "i": 0.0}
    use_signs = zero_signs if is_n0 else sgn

    t0 = (EPOCH_JD_0 - 2440587.5) * 86400.0
    t_onset = {"C2": t0 + TL["t_shift_C2"] * 86400.0,
               "C3": t0 + TL["t_shift_C3"] * 86400.0}.get(condition, math.inf)
    t_va0 = t0 + TL["t_validation_start"] * 86400.0
    t_frz = t0 + TL["t_freeze"] * 86400.0
    t_end = t0 + TL["t_deployment_end"] * 86400.0

    X, y, meta = [], [], []
    n_ep = int(RUN_DAYS * 24.0 / REFRESH_H)
    for q in range(n_ep):
        t_q = t0 + q * REFRESH_H * 3600.0
        t_ep = t_q - S_h * 3600.0
        # held element for THIS episode; delta steps at onset
        dn_eff = dn_post if t_q >= t_onset else dn0
        held = held_element(regime, t_ep, dn_eff, use_signs, truth)
        for (pa, pb) in pass_intervals(held, t_q, t_q + REFRESH_H * 3600.0):
            for oi, frac in enumerate(OFFSETS):
                t = pa + frac * (pb - pa)
                if t > t_end:
                    continue
                # boundary rule: a sample after the freeze instant never joins validation
                fold = 0 if t < t_va0 else (1 if t < t_frz else 2)
                el, rk, dh, okh = geometry(held, np.array([t]))
                if not okh[0]:
                    continue
                ti = int(truth.at(np.array([t]))[0])
                _, _, dt_, okt = geometry(truth.sats[ti], np.array([t]))
                if not okt[0]:
                    continue
                dr = float(doppler_rate(held, np.array([t]))[0])
                age = t - t_ep
                phase = 2 * math.pi * ((age / 86400.0) * REGIMES[regime]["n_rev_day"] % 1.0)
                X.append([age, float(dh[0]), dr, math.sin(phase), math.cos(phase),
                          float(el[0]), float(rk[0]),
                          held.no_kozai * 1440.0 / (2 * math.pi),
                          held.bstar, held.ecco])
                y.append(float(dt_[0]) - float(dh[0]))
                meta.append([t, q * 1000 + int(pa) % 1000, q, age, fold,
                             1.0 if t >= t_onset else 0.0])
    return {"regime": regime, "staleness": staleness, "condition": condition,
            "base_seed": base_seed, "signs": sgn, "rng_state_hash": rng_state_hash,
            "X": np.asarray(X), "y": np.asarray(y), "M": np.asarray(meta),
            "feature_names": FEATURE_NAMES, "meta_names": META}


# --------------------------------------------------------------------------
# candidates and the gate
# --------------------------------------------------------------------------


def _ridge(Xtr, ytr, Xva, yva, alphas=(0.01, 0.1, 1.0, 10.0, 100.0, 1000.0)):
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd[sd < 1e-12] = 1.0
    A = (Xtr - mu) / sd
    b = ytr - ytr.mean()
    best = None
    for al in alphas:
        w = np.linalg.solve(A.T @ A + al * np.eye(A.shape[1]), A.T @ b)
        m = float(np.mean(np.abs(yva - (((Xva - mu) / sd) @ w + ytr.mean()))))
        if best is None or m < best[0]:
            best = (m, w, al)
    _, w, al = best
    return (lambda Xq: ((Xq - mu) / sd) @ w + ytr.mean()), {"alpha": al,
                                                            "mu": mu, "sd": sd, "w": w}


def fit_candidates(run: dict[str, Any], mutate: str | None = None
                   ) -> dict[str, Any]:
    """M0-M3. All state frozen at t_freeze; nothing observes deployment."""
    X, y, M = run["X"], run["y"], run["M"]
    fold = M[:, 4]
    tr, va, de = fold == 0, fold == 1, fold == 2
    out: dict[str, Any] = {"folds": (int(tr.sum()), int(va.sum()), int(de.sum()))}
    if tr.sum() < 60 or va.sum() < 20 or de.sum() < 20:
        return {**out, "degenerate": True}

    age = X[:, 0]
    A1 = np.column_stack([np.ones(tr.sum()), age[tr]])
    c1 = np.linalg.lstsq(A1, y[tr], rcond=None)[0]
    m1 = lambda idx: c1[0] + c1[1] * age[idx]

    p2, i2 = _ridge(X[tr], y[tr], X[va], y[va])
    if mutate == "scaler":
        i2["mu"] = i2["mu"] + 1e-6 * np.median(np.abs(y[de]))
    if mutate == "coeff":
        i2["w"] = i2["w"] * (1.0 + 1e-6 * np.median(np.abs(y[de])))
    m2 = lambda idx: ((X[idx] - i2["mu"]) / i2["sd"]) @ i2["w"] + y[tr].mean()

    # M3: two-state Kalman on pass-mean residual, advanced ONLY up to t_freeze
    closed = tr | va
    pids = M[closed, 1]
    order = np.argsort(M[closed, 0], kind="stable")
    pv = y[closed][order]
    pp = pids[order]
    x = np.zeros(2)
    P = np.eye(2) * 1e2
    Q = np.diag(CFG["candidates"].get("kalman_Q_diag", [1e-6, 1e-9])
                if isinstance(CFG["candidates"].get("kalman_Q_diag"), list)
                else [1e-6, 1e-9])
    for u in dict.fromkeys(pp.tolist()):
        z = float(np.mean(pv[pp == u]))
        x = x.copy()
        P = P + Q
        R = max(float(np.var(pv)), 1e-9)
        K = P[:, 0] / (P[0, 0] + R)
        x = x + K * (z - x[0])
        P = P - np.outer(K, P[0, :])
    if mutate == "tracker":
        x = np.array([float(np.median(y[de])), x[1]])
    m3_state = x.copy()
    m3 = lambda idx: np.full(idx.sum() if idx.dtype == bool else len(idx), m3_state[0])

    cands = {"M1": m1, "M2": m2, "M3": m3}
    val = {k: float(np.mean(np.abs(y[va] - f(va)))) for k, f in cands.items()}
    base_va = float(np.mean(np.abs(y[va])))
    m_star = min(val, key=val.get)
    if mutate == "selmeta":
        m_star = min(("M1", "M2", "M3"),
                     key=lambda k: float(np.mean(np.abs(y[de] - cands[k](de)))))
    gate = int(val[m_star] < GAMMA * base_va)
    if mutate == "gate":
        gate = int(float(np.mean(np.abs(y[de] - cands[m_star](de))))
                   < float(np.mean(np.abs(y[de]))))

    pred = cands[m_star](de)
    mae_A = float(np.mean(np.abs(y[de])))
    mae_B = float(np.mean(np.abs(y[de] - pred)))
    mae_C = float(np.mean(np.abs(y[de] - gate * pred)))
    return {**out, "degenerate": False, "val_mae": val, "val_base": base_va,
            "val_ratio": val[m_star] / base_va, "m_star": m_star, "gate": gate,
            "mae_A": mae_A, "mae_B": mae_B, "mae_C": mae_C,
            "harm_B": int(mae_B > mae_A), "harm_C": int(mae_C > mae_A),
            "m3_state": m3_state.tolist(), "ridge_alpha": i2["alpha"]}


def pass_aggregate(run: dict[str, Any], fold: int = 2) -> dict[str, np.ndarray]:
    """Aggregate the 3 within-pass offsets BEFORE any metric (Q7)."""
    M = run["M"]
    sel = M[:, 4] == fold
    pid = M[sel, 1]
    y = run["y"][sel]
    uniq = np.unique(pid)
    return {"pass_ids": uniq,
            "abs_r": np.array([np.mean(np.abs(y[pid == u])) for u in uniq])}
