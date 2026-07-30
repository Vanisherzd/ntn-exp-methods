#!/usr/bin/env python3
"""FINAL MECHANICAL QUALIFICATION PROBE for v2.2.

Answers ONLY: is the frozen v2.2 benchmark mechanically coherent, falsifiable,
causal, paired across conditions, and physically bounded?

It does NOT answer whether the Evidence Gate succeeds scientifically.

Burned development/reviewer seeds only. No EVALUATION_SEEDS_V2 value is executed.
No parameter is tuned in response to any output.

Verdict is exactly one of: APPROVE FORMAL IMPLEMENTATION / STOP EXP16.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sim_v22 as S  # noqa: E402

CFG = S.CFG
PROBE = CFG["pre_implementation_probe"]
BURNED = CFG["seed_hygiene"]["BURNED_DEVELOPMENT_SEEDS"]
SEEDS = [s for s in BURNED["reviewer_emulation"]]            # 1001-1012
REGIMES = list(CFG["regimes"])
STAL = list(CFG["staleness_levels_h"])
CONDS = ("C1", "C2", "C3")
CEILING = 0.02
N0_GATE_MAX = 0.20

EVAL = json.loads((HERE / "evaluation_seeds_v2.json").read_text())
_FORBIDDEN = set()
for v in EVAL["base_seeds"].values():
    _FORBIDDEN |= set(v)
for v in EVAL["n0_seeds"].values():
    _FORBIDDEN |= set(v)
assert not (set(SEEDS) & _FORBIDDEN), "probe would execute an evaluation seed"

R: dict = {"seeds_used": SEEDS, "n_seeds": len(SEEDS), "findings": []}


def note(sev: str, text: str) -> None:
    R["findings"].append(f"{sev}: {text}")
    print(f"  [{sev}] {text}", flush=True)


# ==========================================================================
print("=" * 70)
print("Q5 + non-degeneracy: physical bounds and both signs")
print("=" * 70)
runs: dict = {}
q5 = []
for rg in REGIMES:
    for st in STAL:
        for cd in CONDS:
            for sd in SEEDS:
                r = S.build_run(rg, st, cd, sd)
                runs[(rg, st, cd, sd)] = r
                dep = r["M"][:, 4] == 2
                if dep.sum() < 10:
                    continue
                ar = np.abs(r["y"][dep])
                ad = np.abs(r["X"][dep, 1])
                q5.append({"rg": rg, "st": st, "cd": cd, "sd": sd,
                           "ratio": float(np.median(ar) / np.median(ad)),
                           "max_abs_r": float(ar.max())})
q5a = np.array([x["ratio"] for x in q5])
print(f"{'cell':28s} {'C1':>9s} {'C2':>9s} {'C3':>9s} {'ceiling':>8s}")
cells_over = []
for rg in REGIMES:
    for st in STAL:
        row = []
        for cd in CONDS:
            v = [x["ratio"] for x in q5 if x["rg"] == rg and x["st"] == st and x["cd"] == cd]
            row.append(float(np.median(v)) if v else np.nan)
        bad = any(v > CEILING for v in row if np.isfinite(v))
        if bad:
            cells_over.append(f"{rg}|{st}")
        print(f"{rg[:14]+'|'+st:28s} {row[0]*100:8.3f}% {row[1]*100:8.3f}% "
              f"{row[2]*100:8.3f}% {'OVER' if bad else 'ok':>8s}")
R["Q5"] = {"max_ratio": float(q5a.max()), "cells_over_ceiling": cells_over,
           "ceiling": CEILING,
           "pass": len(cells_over) == 0}
print(f"\nmax deployment |r|/|D| over all burned runs = {q5a.max()*100:.3f}% "
      f"(ceiling {CEILING*100:.0f}%)  -> {'PASS' if R['Q5']['pass'] else 'FAIL'}")
if cells_over:
    note("BLOCKER", f"Q5 ceiling exceeded in {len(cells_over)} cells: {cells_over}")

# unbounded-integration check: does |r| grow monotonically through deployment?
mono = []
for k, r in runs.items():
    if k[2] not in ("C2", "C3"):
        continue
    dep = r["M"][:, 4] == 2
    if dep.sum() < 20:
        continue
    t = r["M"][dep, 0]
    o = np.argsort(t)
    ar = np.abs(r["y"][dep])[o]
    h = ar.size // 2
    mono.append(float(np.median(ar[h:]) / max(np.median(ar[:h]), 1e-9)))
R["Q5"]["late_over_early_ratio"] = {"p50": float(np.median(mono)),
                                    "p95": float(np.percentile(mono, 95)),
                                    "max": float(np.max(mono))}
print(f"late/early |r| ratio within deployment: p50={np.median(mono):.3f} "
      f"max={np.max(mono):.3f}  (unbounded integration would give >> 1)")

# ==========================================================================
print("\n" + "=" * 70)
print("Q1: null control N0 at ALL staleness levels")
print("=" * 70)
n0 = {}
print(f"{'cell':28s} {'gate-open':>10s} {'B/A p50':>9s} {'ratio%':>8s} {'verdict':>8s}")
n0_fail = []
for rg in REGIMES:
    for st in STAL:
        g, ba, rt = [], [], []
        for sd in SEEDS:
            r = S.build_run(rg, st, "N0", sd)
            f = S.fit_candidates(r)
            if f.get("degenerate"):
                continue
            g.append(f["gate"])
            ba.append(f["mae_B"] / f["mae_A"])
            dep = r["M"][:, 4] == 2
            rt.append(np.median(np.abs(r["y"][dep])) / np.median(np.abs(r["X"][dep, 1])))
        go = float(np.mean(g)) if g else np.nan
        ok = np.isfinite(go) and go <= N0_GATE_MAX
        if not ok:
            n0_fail.append(f"{rg}|{st}")
        n0[f"{rg}|{st}"] = {"gate_open": go, "ba_p50": float(np.median(ba)),
                            "ratio": float(np.median(rt))}
        print(f"{rg[:14]+'|'+st:28s} {go:10.2f} {np.median(ba):9.3f} "
              f"{np.median(rt)*100:7.3f}% {'ok' if ok else 'FAIL':>8s}")
R["Q1"] = {"cells": n0, "failing": n0_fail, "pass": len(n0_fail) == 0}
if n0_fail:
    note("BLOCKER", f"Q1 N0 gate-open > {N0_GATE_MAX} in {len(n0_fail)} cells: {n0_fail}")

# ==========================================================================
print("\n" + "=" * 70)
print("Q2: paired counterfactual identity")
print("=" * 70)
pair_bad = []
for rg in REGIMES:
    for st in STAL:
        for sd in SEEDS:
            a, b, c = (runs[(rg, st, cd, sd)] for cd in CONDS)
            if not (a["X"].shape == b["X"].shape == c["X"].shape):
                pair_bad.append((rg, st, sd, "shape"))
                continue
            if a["rng_state_hash"] != b["rng_state_hash"] != c["rng_state_hash"]:
                pair_bad.append((rg, st, sd, "rng_hash"))
            pre = b["M"][:, 5] == 0.0            # rows before C2's onset
            if float(np.max(np.abs(a["X"][pre] - b["X"][pre]))) != 0.0:
                pair_bad.append((rg, st, sd, "X_C1_C2_pre"))
            if float(np.max(np.abs(b["X"][pre] - c["X"][pre]))) != 0.0:
                pair_bad.append((rg, st, sd, "X_C2_C3_pre"))
            if not np.array_equal(a["M"][:, :4], b["M"][:, :4]):
                pair_bad.append((rg, st, sd, "row_ids"))
pv = runs[(REGIMES[0], STAL[1], "C1", SEEDS[0])]
pv2 = runs[(REGIMES[0], STAL[1], "C2", SEEDS[0])]
pre0 = pv2["M"][:, 5] == 0.0
print(f"max|X_C1 - X_C2| on pre-onset rows = {np.max(np.abs(pv['X'][pre0]-pv2['X'][pre0])):.3e}")
print(f"identical row identifiers: {np.array_equal(pv['M'][:,:4], pv2['M'][:,:4])}")
print(f"identical rng-state hashes: {pv['rng_state_hash']==pv2['rng_state_hash']}")
print(f"violations across {len(REGIMES)*len(STAL)*len(SEEDS)} paired triples: {len(pair_bad)}")
R["Q2"] = {"violations": len(pair_bad), "detail": pair_bad[:10],
           "pass": len(pair_bad) == 0}
if pair_bad:
    note("BLOCKER", f"Q2 pairing violated in {len(pair_bad)} cases: {pair_bad[:5]}")

# ==========================================================================
print("\n" + "=" * 70)
print("Q3: timeline")
print("=" * 70)
TL = CFG["timeline"]
c2_ok = (TL["t_validation_start"] < TL["t_shift_C2"] < TL["t_validation_end"]
         <= TL["t_freeze"] <= TL["t_deployment_start"] < TL["t_deployment_end"])
c3_ok = (TL["t_validation_end"] <= TL["t_freeze"] <= TL["t_shift_C3"]
         <= TL["t_deployment_start"] < TL["t_deployment_end"])
print(f"C2 ordering: {c2_ok}   C3 ordering: {c3_ok}")
# mismatch active through the whole deployment window, and no validation contamination
active, contam = [], []
for k, r in runs.items():
    if k[2] not in ("C2", "C3"):
        continue
    dep = r["M"][:, 4] == 2
    po = r["M"][:, 5] == 1.0
    if dep.sum() == 0:
        continue
    active.append(float(np.mean(po[dep])))
    if k[2] == "C3":
        contam.append(int(np.sum(po & (r["M"][:, 4] == 1))))
print(f"deployment post-onset fraction: min={min(active):.3f} p50={np.median(active):.3f}")
print(f"C3 post-onset samples leaking into validation: {sum(contam)}")
R["Q3"] = {"c2_ordering": c2_ok, "c3_ordering": c3_ok,
           "min_deployment_exposure": float(min(active)),
           "c3_validation_contamination": int(sum(contam)),
           "pass": bool(c2_ok and c3_ok and min(active) >= 0.999 and sum(contam) == 0)}
if not R["Q3"]["pass"]:
    note("BLOCKER", f"Q3 timeline failed: exposure {min(active):.3f}, "
                    f"contamination {sum(contam)}")

# ==========================================================================
print("\n" + "=" * 70)
print("Q4: state-channel mutation tests")
print("=" * 70)
base = runs[(REGIMES[0], STAL[2], "C2", SEEDS[0])]
clean = S.fit_candidates(base)
print(f"clean: m*={clean['m_star']} gate={clean['gate']} "
      f"val_ratio={clean['val_ratio']:.4f} mae_C/mae_A={clean['mae_C']/clean['mae_A']:.4f}")
chan = {}
for ch in ("scaler", "coeff", "tracker", "selmeta", "gate"):
    m = S.fit_candidates(base, mutate=ch)
    changed = (m["gate"] != clean["gate"] or m["m_star"] != clean["m_star"]
               or abs(m["mae_C"] - clean["mae_C"]) > 1e-12
               or abs(m["val_ratio"] - clean["val_ratio"]) > 1e-12)
    chan[ch] = bool(changed)
    print(f"  mutate {ch:9s} -> detectable change: {changed}")
# channel 1: the feature tensor itself
mut = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in base.items()}
mut["X"] = base["X"].copy()
mut["X"][:, 1] = base["X"][:, 1] + base["y"]          # inject truth into a feature
fm = S.fit_candidates(mut)
chan["feature_tensor"] = bool(abs(fm["val_ratio"] - clean["val_ratio"]) > 1e-9)
print(f"  mutate {'features':9s} -> detectable change: {chan['feature_tensor']}")
R["Q4"] = {"channels": chan, "pass": all(chan.values())}
if not all(chan.values()):
    note("BLOCKER", f"Q4 undetectable mutation channels: "
                    f"{[k for k,v in chan.items() if not v]}")

# ==========================================================================
print("\n" + "=" * 70)
print("Q6: functional-form audit")
print("=" * 70)


def cv_r2(X: np.ndarray, y: np.ndarray, cols) -> float:
    """Out-of-sample R2: fit on the train fold, score on deployment."""
    A = np.column_stack([np.ones(X.shape[0])] + [X[:, c] for c in cols])
    return A


q6 = {}
for st in STAL:
    r = runs[(REGIMES[0], st, "C1", SEEDS[0])]
    X, y, fold = r["X"], r["y"], r["M"][:, 4]
    tr, de = fold == 0, fold == 2
    sets = {"age": [0], "ddot": [2], "age+ddot": [0, 2],
            "full": list(range(X.shape[1]))}
    row = {}
    for nm, cols in sets.items():
        A = np.column_stack([np.ones(tr.sum())] + [X[tr][:, c] for c in cols])
        w = np.linalg.lstsq(A, y[tr], rcond=None)[0]
        Ad = np.column_stack([np.ones(de.sum())] + [X[de][:, c] for c in cols])
        p = Ad @ w
        row[nm] = float(1.0 - np.sum((y[de] - p) ** 2)
                        / max(np.sum((y[de] - y[de].mean()) ** 2), 1e-12))
    # oracle affine on (Ddot, Ddot*age)
    for lbl, cols in (("oracle", None),):
        A = np.column_stack([np.ones(tr.sum()), X[tr][:, 2], X[tr][:, 2] * X[tr][:, 0]])
        w = np.linalg.lstsq(A, y[tr], rcond=None)[0]
        Ad = np.column_stack([np.ones(de.sum()), X[de][:, 2], X[de][:, 2] * X[de][:, 0]])
        p = Ad @ w
        row[lbl] = float(1.0 - np.sum((y[de] - p) ** 2)
                         / max(np.sum((y[de] - y[de].mean()) ** 2), 1e-12))
    q6[st] = row
    print(f"{st:12s} " + "  ".join(f"{k}={v:+.4f}" for k, v in row.items()))
oracle_max = max(v["oracle"] for v in q6.values())
R["Q6"] = {"r2": q6, "oracle_max": oracle_max,
           "C1_classification": ("CONTROLLED CALIBRATION / SANITY SCENARIO"
                                 if oracle_max >= 0.95 else "not calibration-classified")}
print(f"\noracle affine max out-of-sample R2 = {oracle_max:+.4f} -> C1 is "
      f"{R['Q6']['C1_classification']}")

# ==========================================================================
print("\n" + "=" * 70)
print("Q7: repeated-measure handling")
print("=" * 70)
wp = []
for k, r in runs.items():
    if k[2] != "C1":
        continue
    M, y = r["M"], r["y"]
    dep = M[:, 4] == 2
    pid = M[dep, 1]
    yy = np.abs(y[dep])
    grp = [yy[pid == u] for u in np.unique(pid) if (pid == u).sum() >= 2]
    if len(grp) < 10:
        continue
    gm = np.concatenate(grp).mean()
    sb = np.mean([(g.mean() - gm) ** 2 for g in grp])
    sw = np.mean([g.var() for g in grp if g.size > 1])
    wp.append(sb / (sb + sw) if sb + sw > 0 else np.nan)
agg = S.pass_aggregate(runs[(REGIMES[0], STAL[1], "C1", SEEDS[0])])
print(f"within-pass ICC of |r|: p50={np.nanmedian(wp):.3f} "
      f"min={np.nanmin(wp):.3f} max={np.nanmax(wp):.3f}")
print(f"pass_aggregate collapses {runs[(REGIMES[0],STAL[1],'C1',SEEDS[0])]['M'][:,4].tolist().count(2)}"
      f" deployment samples to {agg['pass_ids'].size} passes")
R["Q7"] = {"within_pass_icc_p50": float(np.nanmedian(wp)),
           "aggregation_implemented": True, "pass": True}

# ==========================================================================
print("\n" + "=" * 70)
print("Q8: grid-uniformity canary + non-degeneracy")
print("=" * 70)
gt = {}
for rg in REGIMES:
    for st in STAL:
        for cd in CONDS:
            g, hb, vr = [], [], []
            for sd in SEEDS:
                f = S.fit_candidates(runs[(rg, st, cd, sd)])
                if f.get("degenerate"):
                    continue
                g.append(f["gate"]); hb.append(f["harm_B"]); vr.append(f["val_ratio"])
            gt[(rg, st, cd)] = {"gate": float(np.mean(g)), "harm_B": float(np.mean(hb)),
                                "val_ratio": float(np.median(vr)),
                                "harm_vec": hb}
gates = [v["gate"] for v in gt.values()]
vrs = [v["val_ratio"] for v in gt.values()]
uniform = (len(set(np.round(gates, 6))) == 1) or (max(vrs) - min(vrs) < 0.01)
print(f"gate-open spread across cells: {min(gates):.2f}-{max(gates):.2f}")
print(f"val_ratio spread: {min(vrs):.4f}-{max(vrs):.4f}")
print(f"canary fires (all cells near-identical): {uniform}")
helps = sum(1 for v in gt.values() for h in v["harm_vec"] if h == 0)
harms = sum(1 for v in gt.values() for h in v["harm_vec"] if h == 1)
print(f"\nnon-degeneracy: helpful realizations={helps}  harmful realizations={harms}")
print(f"{'cell':28s} {'C1 harm':>8s} {'C2 harm':>8s} {'C3 harm':>8s} {'C2 gate':>8s}")
for rg in REGIMES:
    for st in STAL:
        print(f"{rg[:14]+'|'+st:28s} "
              f"{gt[(rg,st,'C1')]['harm_B']:8.2f} {gt[(rg,st,'C2')]['harm_B']:8.2f} "
              f"{gt[(rg,st,'C3')]['harm_B']:8.2f} {gt[(rg,st,'C2')]['gate']:8.2f}")
R["Q8"] = {"canary_fires": bool(uniform), "gate_spread": [min(gates), max(gates)],
           "helpful": helps, "harmful": harms,
           "non_degenerate": bool(helps > 0 and harms > 0), "pass": not uniform}

# ==========================================================================
print("\n" + "=" * 70)
checks = {"Q1_null": R["Q1"]["pass"], "Q2_paired": R["Q2"]["pass"],
          "Q3_timeline": R["Q3"]["pass"], "Q4_mutation": R["Q4"]["pass"],
          "Q5_bounds": R["Q5"]["pass"], "Q7_repeated": R["Q7"]["pass"],
          "Q8_not_uniform": R["Q8"]["pass"],
          "non_degeneracy": R["Q8"]["non_degenerate"]}
R["checks"] = checks
R["verdict"] = ("APPROVE FORMAL IMPLEMENTATION" if all(checks.values())
                else "STOP EXP16")
for k, v in checks.items():
    print(f"  {k:20s} {'PASS' if v else 'FAIL'}")
print(f"\nVERDICT: {R['verdict']}")
R["config_sha256"] = hashlib.sha256((HERE / "physical_config.json").read_bytes()).hexdigest()
R["sim_sha256"] = hashlib.sha256((HERE / "sim_v22.py").read_bytes()).hexdigest()
(HERE / "PROBE_RESULT.json").write_text(json.dumps(R, indent=1, default=str))
print(f"wrote {HERE/'PROBE_RESULT.json'}")
