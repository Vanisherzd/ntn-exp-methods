#!/usr/bin/env python3
"""E2 + E3 + E4 -- causal historical state, pre-registered candidates, walk-forward.

Everything here obeys ``preregistration.json``, which was written before any fit.

Causality model. At every refresh the provisioning payload carries (a) the latest
element with CREATION_DATE <= t_refresh, and (b) a summary of residual history
whose labels have all closed by t_refresh. The MODEL, scaler and gate are
re-selected only at decision points, every 30 episodes. Online trackers (M3-M6)
are snapshotted per episode from labels closed by that episode's refresh, so
their prediction is a function of the past only.

Temporal-join test: no historical feature at episode e may draw on a label whose
t_close exceeds t_refresh(e). Enforced by construction and re-checked in
``verify_temporal_join``.
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
PRE = json.loads((HERE / "preregistration.json").read_text())
E2, E3, E4 = PRE["E2_historical_state"], PRE["E3_candidate_family"], PRE["E4_walk_forward"]

HIST_NAMES = tuple(E2["features"])
TREND_N = tuple(E2["trend_windows_N"])
ALPHAS = tuple(E2["ewma_alphas"])
VAR_ALPHA = E2["ewma_variance_alpha"]
RESET_S = 30.0 * 86400.0
GAMMA = E4["gamma"]
STRIDE = E4["decision_point_stride_episodes"]
HORIZON = E4["deployment_horizon_episodes"]
VAL_FRAC = E4["validation_fraction_of_closed_history"]
MIN_TRAIN = E4["minimum_train_observations"]
MIN_VAL = E4["minimum_validation_observations"]
RIDGE_ALPHAS = tuple(E3["ridge_alphas"])
RLS_LAM = E3["rls_forgetting"]
KF_Q = np.diag(E3["kalman_Q_diag"])

CANDIDATES = ("M1", "M2", "M3", "M4", "M5", "M6", "M7")

REGIME = {  # orbital regime, for S2 breadth criterion 3
    "ISS (ZARYA)": "LEO-ISS", "IRIDIUM 181": "LEO-polar-comms",
    "IRIDIUM 177": "LEO-polar-comms", "ONEWEB-0015": "LEO-MEO-transfer",
    "SENTINEL-6B": "LEO-altimetry", "FLOCK 4H 1": "LEO-SSO-cubesat",
    "FLOCK 4H 2": "LEO-SSO-cubesat", "BLACK KITE-1": "LEO-SSO-smallsat",
    "BLACK KITE-2": "LEO-SSO-smallsat", "STARLINK-38128": "LEO-VLEO-constellation",
    "STARLINK-37711": "LEO-VLEO-constellation",
}


# --------------------------------------------------------------------------
# E2 -- causal historical state, one snapshot per episode
# --------------------------------------------------------------------------


def historical_state(M: np.ndarray, y: np.ndarray, cols: dict[str, int],
                     avail_creations: np.ndarray, elements: np.ndarray
                     ) -> tuple[np.ndarray, dict[int, dict[str, Any]]]:
    """Per-row historical features + per-episode online-tracker snapshots.

    Episodes are visited in refresh order. A pointer sweeps the labels in
    CLOSURE order and admits only those with t_close <= t_refresh(e), so the
    state at episode e is a strict function of the past.
    """
    ep = M[:, cols["episode_idx"]].astype(np.int64)
    t_ref, t_tx, t_close = (M[:, cols["t_refresh"]], M[:, cols["t_tx"]],
                            M[:, cols["t_close"]])

    close_order = np.argsort(t_close, kind="stable")
    closed_t = t_close[close_order]

    ep_first_row: dict[int, int] = {}
    for r in np.argsort(t_ref, kind="stable"):
        ep_first_row.setdefault(int(ep[r]), int(r))
    episodes = sorted(ep_first_row, key=lambda e: t_ref[ep_first_row[e]])

    # running state
    ewma_b = {a: 0.0 for a in ALPHAS}
    ewma_a = {a: 0.0 for a in ALPHAS}
    ewma_v = 0.0
    n_obs = 0
    last_close_t = -np.inf
    ep_counts = defaultdict(int)
    ep_sum = defaultdict(float)
    ep_vals: dict[int, list[float]] = defaultdict(list)
    ep_total = defaultdict(int)
    for e in ep:
        ep_total[int(e)] += 1
    done_eps: deque = deque(maxlen=max(TREND_N) + 2)   # (t_tx_mean, mean, median)
    rls_P = np.eye(2) * 1e4
    rls_th = np.zeros(2)
    kf_x = np.zeros(2)
    kf_P = np.eye(2) * 1e2
    kf_R = 1.0
    kf_t = None

    H = np.zeros((M.shape[0], len(HIST_NAMES)))
    snaps: dict[int, dict[str, Any]] = {}
    ptr = 0

    for e in episodes:
        T = t_ref[ep_first_row[e]]
        stop = int(np.searchsorted(closed_t, T, side="right"))
        while ptr < stop:
            r = int(close_order[ptr])
            ptr += 1
            if t_close[r] - last_close_t > RESET_S and n_obs:
                ewma_b = {a: 0.0 for a in ALPHAS}
                ewma_a = {a: 0.0 for a in ALPHAS}
                ewma_v, n_obs = 0.0, 0
                done_eps.clear()
                rls_P, rls_th = np.eye(2) * 1e4, np.zeros(2)
                kf_x, kf_P, kf_t = np.zeros(2), np.eye(2) * 1e2, None
            last_close_t = max(last_close_t, t_close[r])
            v = float(y[r])
            n_obs += 1
            for a in ALPHAS:
                ewma_b[a] = v if n_obs == 1 else (1 - a) * ewma_b[a] + a * v
                ewma_a[a] = (abs(v) if n_obs == 1
                             else (1 - a) * ewma_a[a] + a * abs(v))
            ewma_v = ((v - ewma_b[VAR_ALPHA]) ** 2 if n_obs == 1
                      else (1 - VAR_ALPHA) * ewma_v
                      + VAR_ALPHA * (v - ewma_b[VAR_ALPHA]) ** 2)
            se = int(ep[r])
            ep_counts[se] += 1
            ep_sum[se] += v
            ep_vals[se].append(v)
            if ep_counts[se] == ep_total[se]:
                arr = np.asarray(ep_vals.pop(se))
                done_eps.append((float(t_ref[ep_first_row[se]]),
                                 float(arr.mean()), float(np.median(arr))))
            # RLS on [1, age_h]
            z = np.array([1.0, float(M[r, cols["t_tx"]] - M[r, cols["stale_epoch"]])
                          / 3600.0])
            denom = RLS_LAM + z @ rls_P @ z
            k = (rls_P @ z) / denom
            rls_th = rls_th + k * (v - z @ rls_th)
            rls_P = (rls_P - np.outer(k, z @ rls_P)) / RLS_LAM

        # Kalman update on the newest completed episode mean
        if done_eps:
            t_new, mean_new, _ = done_eps[-1]
            if kf_t is None or t_new > kf_t:
                dtd = 0.0 if kf_t is None else (t_new - kf_t) / 86400.0
                F = np.array([[1.0, dtd], [0.0, 1.0]])
                kf_x = F @ kf_x
                kf_P = F @ kf_P @ F.T + KF_Q
                kf_R = max(ewma_v, 1e-9)
                S = kf_P[0, 0] + kf_R
                Kk = kf_P[:, 0] / S
                kf_x = kf_x + Kk * (mean_new - kf_x[0])
                kf_P = kf_P - np.outer(Kk, kf_P[0, :])
                kf_t = t_new

        valid = 1.0 if n_obs >= E2["minimum_history_for_state_models"][
            "closed_observations"] and len(done_eps) >= 2 else 0.0
        last_mean = done_eps[-1][1] if done_eps else 0.0
        last_med = done_eps[-1][2] if done_eps else 0.0
        trends = {}
        for N in TREND_N:
            if len(done_eps) >= 3:
                sub = list(done_eps)[-N:]
                tt = np.array([s[0] for s in sub]) / 86400.0
                vv = np.array([s[1] for s in sub])
                tt = tt - tt.mean()
                den = float(tt @ tt)
                trends[N] = float(tt @ (vv - vv.mean()) / den) if den > 1e-12 else 0.0
            else:
                trends[N] = 0.0
        ia = avail_creations[avail_creations <= T]
        if ia.size >= 3:
            gaps = np.diff(ia) / 3600.0
            ia_med, ia_last = float(np.median(gaps)), float(gaps[-1])
        else:
            ia_med, ia_last = 0.0, 0.0
        held = int(np.searchsorted(avail_creations, T, side="right")) - 1
        if held >= 1:
            d_mm = float(elements[held, 0] - elements[held - 1, 0])
            d_bs = float(elements[held, 1] - elements[held - 1, 1])
            d_ec = float(elements[held, 2] - elements[held - 1, 2])
        else:
            d_mm = d_bs = d_ec = 0.0

        row = [last_mean, last_med,
               ewma_b[ALPHAS[0]], ewma_b[ALPHAS[1]],
               ewma_a[ALPHAS[0]], ewma_a[ALPHAS[1]], ewma_v,
               trends[TREND_N[0]], trends[TREND_N[1]],
               float(n_obs), 0.0, ia_med, ia_last, d_mm, d_bs, d_ec, valid]
        rows = np.flatnonzero(ep == e)
        H[rows] = row
        # time since last closed label is per row (uses t_tx of that row)
        H[rows, HIST_NAMES.index("time_since_last_closed_label_s")] = (
            0.0 if not np.isfinite(last_close_t) else t_tx[rows] - last_close_t)
        snaps[e] = {
            "last_med": last_med, "last_mean": last_mean,
            "ewma": {a: ewma_b[a] for a in ALPHAS},
            "rls": rls_th.copy(), "kf": kf_x.copy(),
            "kf_t": kf_t, "n_obs": n_obs, "valid": valid,
            "max_closed_t": (last_close_t if np.isfinite(last_close_t) else -np.inf),
            "t_refresh": float(T),
        }
    return H, snaps


def verify_temporal_join(M: np.ndarray, cols: dict[str, int],
                         snaps: dict[int, dict[str, Any]]) -> int:
    """Fail count: any episode whose admitted history closes after its refresh."""
    bad = 0
    for e, s in snaps.items():
        if np.isfinite(s["max_closed_t"]) and s["max_closed_t"] > s["t_refresh"] + 1e-6:
            bad += 1
    return bad


# --------------------------------------------------------------------------
# E3 -- candidates
# --------------------------------------------------------------------------


def _ridge(Xtr: np.ndarray, ytr: np.ndarray, Xva: np.ndarray, yva: np.ndarray):
    """Ridge with alpha chosen on validation. Scaler frozen from train."""
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd[sd < 1e-12] = 1.0
    A = (Xtr - mu) / sd
    b = ytr - ytr.mean()
    best = None
    for al in RIDGE_ALPHAS:
        w = np.linalg.solve(A.T @ A + al * np.eye(A.shape[1]), A.T @ b)
        pv = ((Xva - mu) / sd) @ w + ytr.mean()
        m = float(np.mean(np.abs(yva - pv)))
        if best is None or m < best[0]:
            best = (m, w, al)
    _, w, al = best

    def predict(Xq: np.ndarray) -> np.ndarray:
        return ((Xq - mu) / sd) @ w + ytr.mean()

    return predict, {"alpha": al}


def fit_candidates(Xs: np.ndarray, Hh: np.ndarray, y: np.ndarray, ages: np.ndarray,
                   eps: np.ndarray, snaps: dict[int, dict[str, Any]],
                   tx: np.ndarray, tr: np.ndarray, va: np.ndarray
                   ) -> dict[str, Any]:
    """Return {name: (predict_fn, info)}. Online trackers read their snapshot."""
    out: dict[str, Any] = {}

    # M1 age-only linear
    A = np.column_stack([np.ones(tr.size), ages[tr]])
    coef, *_ = np.linalg.lstsq(A, y[tr], rcond=None)
    out["M1"] = (lambda idx, c=coef: c[0] + c[1] * ages[idx], {"coef": coef.tolist()})

    # M2 static ridge
    p2, i2 = _ridge(Xs[tr], y[tr], Xs[va], y[va])
    out["M2"] = (lambda idx, f=p2: f(Xs[idx]), i2)

    # M3 last closed residual bias / M4 EWMA bias / M5 RLS / M6 Kalman
    def snap_const(idx, key):
        return np.array([snaps[int(e)][key] for e in eps[idx]])

    out["M3"] = (lambda idx: snap_const(idx, "last_med"), {})

    def ewma_pred(idx, a):
        return np.array([snaps[int(e)]["ewma"][a] for e in eps[idx]])

    m4 = min(ALPHAS, key=lambda a: float(np.mean(np.abs(y[va] - ewma_pred(va, a)))))
    out["M4"] = (lambda idx, a=m4: ewma_pred(idx, a), {"alpha": m4})

    def rls_pred(idx):
        th = np.array([snaps[int(e)]["rls"] for e in eps[idx]])
        return th[:, 0] + th[:, 1] * (ages[idx] / 3600.0)

    out["M5"] = (rls_pred, {})

    def kf_pred(idx):
        vals = np.empty(idx.size)
        for n, i in enumerate(idx):
            s = snaps[int(eps[i])]
            dtd = 0.0 if s["kf_t"] is None else (tx[i] - s["kf_t"]) / 86400.0
            vals[n] = s["kf"][0] + s["kf"][1] * dtd
        return vals

    out["M6"] = (kf_pred, {})

    # M7 static + historical ridge
    Xf = np.column_stack([Xs, Hh])
    p7, i7 = _ridge(Xf[tr], y[tr], Xf[va], y[va])
    out["M7"] = (lambda idx, f=p7: f(Xf[idx]), i7)
    return out


# --------------------------------------------------------------------------
# E4 -- walk-forward
# --------------------------------------------------------------------------


def walk_forward(sat: dict[str, Any]) -> dict[str, Any]:
    M, X, cols = sat["M"], sat["X"], sat["cols"]
    y = X[:, -1]
    Xs = X[:, :-1]
    H = sat["H"]
    snaps = sat["snaps"]
    ages = Xs[:, 0]
    eps = M[:, cols["episode_idx"]].astype(np.int64)
    t_ref, t_tx, t_close = (M[:, cols["t_refresh"]], M[:, cols["t_tx"]],
                            M[:, cols["t_close"]])
    band = M[:, cols["band_h"]]

    ep_order = sorted(set(eps.tolist()), key=lambda e: t_ref[np.flatnonzero(eps == e)[0]])
    ep_time = {e: float(t_ref[np.flatnonzero(eps == e)[0]]) for e in ep_order}

    segments: list[dict[str, Any]] = []
    for d in range(STRIDE, len(ep_order) - 1, STRIDE):
        T = ep_time[ep_order[d]]
        closed = np.flatnonzero(t_close <= T)
        if closed.size < MIN_TRAIN + MIN_VAL:
            continue
        closed = closed[np.argsort(t_tx[closed], kind="stable")]
        cut = int(round(closed.size * (1.0 - VAL_FRAC)))
        tr, va = closed[:cut], closed[cut:]
        if tr.size < MIN_TRAIN or va.size < MIN_VAL:
            continue
        dep_eps = ep_order[d + 1: d + 1 + HORIZON]
        if not dep_eps:
            continue
        dep = np.flatnonzero(np.isin(eps, np.asarray(dep_eps)))
        if dep.size == 0:
            continue

        # deployment inference scope must not contain any reference quantity
        assert cols["ref_epoch"] not in (), "meta columns are read only for audit"

        cand = fit_candidates(Xs, H, y, ages, eps, snaps, t_tx, tr, va)
        base_va = float(np.mean(np.abs(y[va])))
        base_dep = float(np.mean(np.abs(y[dep])))
        val_mae, dep_mae = {}, {}
        for name, (fn, _info) in cand.items():
            val_mae[name] = float(np.mean(np.abs(y[va] - fn(va))))
            dep_mae[name] = float(np.mean(np.abs(y[dep] - fn(dep))))
        m_star = min(CANDIDATES, key=lambda n: val_mae[n])
        gate = int(val_mae[m_star] < GAMMA * base_va)

        pred = cand[m_star][0](dep)
        gated_dep = float(np.mean(np.abs(y[dep] - gate * pred)))
        # per deployment episode: delta MAE of the gated predictor vs SGP4
        per_ep = []
        for e in dep_eps:
            r = np.flatnonzero(eps == e)
            if r.size == 0:
                continue
            p = cand[m_star][0](r)
            per_ep.append({
                "episode": int(e), "n": int(r.size),
                "mae_sgp4": float(np.mean(np.abs(y[r]))),
                "mae_mstar": float(np.mean(np.abs(y[r] - p))),
                "mae_gated": float(np.mean(np.abs(y[r] - gate * p))),
                "band_mode": int(np.bincount(band[r].astype(int)).argmax()),
            })
        segments.append({
            "decision_episode": int(ep_order[d]), "t_decision": T,
            "n_train": int(tr.size), "n_val": int(va.size), "n_dep": int(dep.size),
            "val_mae_sgp4": base_va, "dep_mae_sgp4": base_dep,
            "val_mae": val_mae, "dep_mae": dep_mae,
            "m_star": m_star, "gate": gate,
            "dep_mae_gated": gated_dep,
            "harmful": int(gate == 1 and gated_dep > base_dep),
            "per_episode": per_ep,
        })
    return {"satellite": sat["name"], "regime": REGIME.get(sat["name"], "unknown"),
            "n_rows": int(M.shape[0]), "segments": segments}


# --------------------------------------------------------------------------


def load_satellite(path: Path, elem: dict[str, Any],
                   reject_hz: float | None) -> dict[str, Any] | None:
    """Load one satellite and apply the pre-specified plausibility screen.

    The screen is part of the fixed run configuration: a provisioning server
    would not train on a residual that large either. ``reject_hz=None`` means no
    screen, used only for the S2 criterion-6 sensitivity sweep.
    """
    d = np.load(path, allow_pickle=False)
    M, X = d["M"], d["X"]
    if reject_hz is not None:
        keep = np.abs(X[:, -1]) <= reject_hz
        M, X = M[keep], X[keep]
    if M.shape[0] < MIN_TRAIN + MIN_VAL + 24:
        return None
    cols = {c: i for i, c in enumerate([str(s) for s in d["meta_cols"]])}
    return {"key": path.stem, "M": M, "X": X, "cols": cols,
            "avail_creations": elem["creations"], "elements": elem["elements"]}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--reject-hz", type=float,
                    default=E4["fixed_run_configuration"]["screen_reject_hz"])
    ap.add_argument("--no-screen", action="store_true")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    reject = None if args.no_screen else args.reject_hz

    sys.path.insert(0, str(HERE))
    import build_causal_dataset as B

    tle_dir = B.ROOT / "dataraw" / "spacetrack"
    sats = {s.key: s for s in B.pipe.discover_satellites(tle_dir)}
    data_dir = HERE / "causal_dataset" / "periodic_24h"

    results, join_fails = [], 0
    for path in sorted(data_dir.glob("*.npz")):
        sd = sats.get(path.stem)
        if sd is None:
            continue
        avail = B.availability_index(sd)
        creations = np.array([B._unix(r["creation_dt"]) for r in avail])
        elements = np.array([[r["mean_motion_rad_min"], r["bstar"], r["ecc"]]
                             for r in avail])
        sat = load_satellite(path, {"creations": creations, "elements": elements},
                             reject)
        if sat is None:
            print(f"  skip {path.stem}: too few rows", flush=True)
            continue
        sat["name"] = sd.name
        H, snaps = historical_state(sat["M"], sat["X"][:, -1], sat["cols"],
                                    creations, elements)
        join_fails += verify_temporal_join(sat["M"], sat["cols"], snaps)
        sat["H"], sat["snaps"] = H, snaps
        res = walk_forward(sat)
        print(f"  {sd.name[:22]:22s} rows={res['n_rows']:6d} "
              f"segments={len(res['segments']):3d} "
              f"gates_open={sum(s['gate'] for s in res['segments']):3d}", flush=True)
        results.append(res)

    out = {"preregistration_sha256": B._sha256(HERE / "preregistration.json"),
           "screen_reject_hz": reject,
           "temporal_join_failures": join_fails,
           "hist_feature_names": list(HIST_NAMES),
           "candidates": list(CANDIDATES),
           "satellites": results}
    name = f"E4_walk_forward{args.tag}.json"
    (HERE / name).write_text(json.dumps(out, indent=1))
    print(f"temporal-join failures: {join_fails}")
    print(f"wrote {HERE / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
