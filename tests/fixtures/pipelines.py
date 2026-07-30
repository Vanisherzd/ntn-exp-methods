"""Two minimal deterministic pipelines plus the frozen fault injectors.

These are FIXTURES, not simulators. They exist only to exercise contract rules and
carry no physical claim. The stopped project's generative model is not used.

CASE A -- retrospective orbital-label pipeline: held orbital state, visible-pass
scheduling, frozen registry, later reference construction, label closure.

CASE B -- controlled learning/gating pipeline: physics baseline, optional learned
branch, validation selection, frozen model/scaler/gate state, later deployment window.

Fault identifiers are frozen in PREREGISTRATION.md. `None` is the clean path.
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SRC = HERE.parents[1] / "src"
sys.path.insert(0, str(SRC))

from orbit_evidence.experiment_contract import experiment_contract as EC   # noqa: E402
from orbit_evidence.causal_registry import causal_registry as CR       # noqa: E402
from orbit_evidence.pass_scheduler import visible_pass as VP         # noqa: E402

MU = 398600.4418
STATION = VP.Station(24.0, 121.0, 100.0)
MASK_DEG = 10.0
OFFSETS = (0.2, 0.5, 0.8)
T0 = (2460000.5 - 2440587.5) * 86400.0

# D12 was removed: its injector was the same branch as D3 and produced a
# byte-identical registry, so it was one fault counted twice. The distinction it
# claimed (window from the LABEL source rather than the ROW source) was never
# implemented.
#
# The suite is 17 CURATED fault classes. It is split below only for provenance: the
# first group was frozen in the pre-registration's first batch, the second group later.
# That split carries NO evidential weight and must not be reported as a held-out or
# generalisation result -- see the withdrawal notice at the top of
# evaluation/mutations/PREREGISTRATION.md. LS1/LS2 are consumed only by their own
# detector, and LS3's detector was rewritten after its outcome was inspected.
DEV_FAULTS = ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10",
              "D11", "D13", "D14")
LATE_SPECIFIED = ("HO1", "HO2", "HO3", "HO4")
ALL_FAULTS = DEV_FAULTS + LATE_SPECIFIED


@dataclass
class Env:
    """A deterministic environment. Varies only reproducibility-relevant settings."""
    name: str
    rng_family: str = "PCG64"
    dtype: str = "float64"
    config_order: int = 0

    def rng(self, seed: int) -> np.random.Generator:
        bg = {"PCG64": np.random.PCG64, "SFC64": np.random.SFC64,
              "Philox": np.random.Philox}[self.rng_family]
        return np.random.Generator(bg(seed))


ENVS = (Env("E1", "PCG64", "float64", 0),
        Env("E2", "SFC64", "float64", 1),
        Env("E3", "Philox", "float64", 2))


def analytic_propagator(a_km: float, incl_deg: float, raan_deg: float = 40.0,
                        phase0: float = 0.0) -> Callable:
    n = math.sqrt(MU / a_km ** 3)
    i, om = math.radians(incl_deg), math.radians(raan_deg)

    def prop(jd, fr):
        t = ((np.asarray(jd) + np.asarray(fr)) - 2451545.0) * 86400.0
        u = phase0 + n * t
        xo, yo = a_km * np.cos(u), a_km * np.sin(u)
        vxo, vyo = -a_km * n * np.sin(u), a_km * n * np.cos(u)

        def rot(x, y):
            y2, z2 = y * math.cos(i), y * math.sin(i)
            return (x * math.cos(om) - y2 * math.sin(om),
                    x * math.sin(om) + y2 * math.cos(om), z2)

        rx, ry, rz = rot(xo, yo)
        vx, vy, vz = rot(vxo, vyo)
        return (np.zeros(np.shape(t), dtype=int),
                np.stack([rx, ry, rz], -1), np.stack([vx, vy, vz], -1))
    return prop


# ==========================================================================
# CASE A
# ==========================================================================

@dataclass
class CaseA:
    fault: str | None
    env: Env
    seed: int
    elevations: np.ndarray = field(default_factory=lambda: np.zeros(0))
    t_tx: np.ndarray = field(default_factory=lambda: np.zeros(0))
    pass_ids: np.ndarray = field(default_factory=lambda: np.zeros(0))
    episode_ids: np.ndarray = field(default_factory=lambda: np.zeros(0))
    descriptive: np.ndarray = field(default_factory=lambda: np.zeros(0))
    published: np.ndarray = field(default_factory=lambda: np.zeros(0))
    selected_index: int = -1
    t_decision: float = 0.0
    closure: np.ndarray = field(default_factory=lambda: np.zeros(0))
    used_mask: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=bool))
    residual: np.ndarray = field(default_factory=lambda: np.zeros(0))
    reference_mag: np.ndarray = field(default_factory=lambda: np.zeros(0))
    window: Any = None
    build_fn: Any = None
    full_source: Any = None
    trunc_source: Any = None
    feature_fn: Any = None
    truncate_at: Any = None
    restore: Any = None
    admit_fn: Any = None
    declared: Any = None
    implemented: Any = None
    domain: tuple[float, float] = (0.0, 1.0)
    state_times: np.ndarray = field(default_factory=lambda: np.zeros(0))
    state_quantity: np.ndarray = field(default_factory=lambda: np.zeros(0))
    manifest_variations: Any = None
    manifest_run_fn: Any = None


def build_case_a(fault: str | None, env: Env, seed: int = 20260731) -> CaseA:
    f = fault
    c = CaseA(fault=f, env=env, seed=seed)
    prop = analytic_propagator(6878.0, 97.4)

    # ---- scheduling -------------------------------------------------------
    cfg = VP.PassFinderConfig(mask_deg=MASK_DEG)
    intervals = VP.find_passes(prop, STATION, T0, T0 + 4 * 86400.0, cfg)
    if f == "D4":
        # below-horizon transmissions: sample a clock grid and keep everything
        ts = T0 + np.arange(0, 4 * 86400.0, 900.0)
        pid = np.arange(ts.size) // 3
    else:
        sched = VP.sample_passes(intervals, OFFSETS)
        ts = np.array([t for _, _, t in sched])
        pid = np.array([p for p, _, _ in sched])
    el, rng_km, _, _ = VP.look_angles(prop, STATION, ts, 1.0)
    c.elevations, c.t_tx, c.pass_ids = el, ts, pid
    c.episode_ids = ((ts - T0) // 86400.0).astype(int)

    # ---- availability clocks ---------------------------------------------
    n_items = 8
    c.descriptive = T0 + np.arange(n_items) * 43200.0
    c.published = c.descriptive + 21600.0          # published 6 h after it describes
    c.t_decision = float(c.descriptive[4] + 3600.0)
    if f == "D2":
        c.selected_index = int(np.searchsorted(c.descriptive, c.t_decision) - 1)
    else:
        c.selected_index = int(np.searchsorted(c.published, c.t_decision) - 1)

    # L1.5 boundary predicate
    if f == "HO1":
        c.admit_fn = lambda pub, dec: pub < dec        # strict: rejects equality
    else:
        c.admit_fn = lambda pub, dec: pub <= dec

    # ---- label closure ----------------------------------------------------
    c.closure = c.t_tx + 48.0 * 3600.0
    if f == "D5":
        c.used_mask = np.ones(c.t_tx.size, dtype=bool)
        c.t_decision_labels = float(c.t_tx.min())
        c.used_mask &= c.closure > c.t_tx.min()
        c.closure_decision = float(c.t_tx.min())
    else:
        c.closure_decision = float(c.closure.max() + 1.0)
        c.used_mask = c.closure <= c.closure_decision

    # ---- row membership ---------------------------------------------------
    c.window = CR.FreezeWindow(T0, T0 + 4 * 86400.0)
    full = list(ts) + [T0 + 9 * 86400.0]
    trunc = list(ts)

    def mk_rows(src, w):
        return [{"tx_id": f"tx{i}", "pass_id": f"p{i // 3}", "episode_id": float(i // 3),
                 "t_tx": float(t)} for i, t in enumerate(src)
                if w.t_start <= t <= w.t_end]

    if f == "D3":
        def build(src, _w):
            # D3: window end from the data. D12: window end from the LABEL source's
            # extent, which is a distinct object from the row source.
            w = CR.FreezeWindow(T0, max(src))
            return CR.build_registry(mk_rows(src, w), w)
    else:
        def build(src, w):
            return CR.build_registry(mk_rows(src, w), w)
    c.build_fn, c.full_source, c.trunc_source = build, full, trunc

    # ---- feature availability --------------------------------------------
    path = np.arange(200.0)

    def feat(t):
        i = int(t)
        if f == "D1":
            return np.array([path[i], path[min(i + 5, 199)]])   # reads the future
        return np.array([path[i], path[max(i - 5, 0)]])

    def trunc_at(t):
        saved = path.copy()
        path[int(t) + 1:] = np.nan
        return saved

    c.feature_fn, c.truncate_at = feat, lambda t: trunc_at(t)
    c.restore = lambda saved: path.__setitem__(slice(None), saved)

    # ---- residual scale ---------------------------------------------------
    g = env.rng(seed)
    c.reference_mag = np.full(ts.size, 10000.0)
    c.residual = np.abs(g.normal(0.0, 40.0, ts.size)) + 20.0

    # ---- bounded state ---------------------------------------------------
    c.state_times = ts
    c.state_quantity = np.full(ts.size, 5.0) + g.normal(0, 0.1, ts.size)

    # ---- declared relation (L2.4) ----------------------------------------
    c.domain = (0.0, 1.0)
    c.declared = lambda x: 2.0 * x + 1.0
    if f == "HO4":
        c.implemented = lambda x: 2.0 * x + 1.0 + 0.02 * x ** 2   # agrees on [0,1]
    else:
        c.implemented = lambda x: 2.0 * x + 1.0

    # ---- provenance completeness (L4.6) ----------------------------------
    def run_with(cfgv):
        scale = float(cfgv.get("scale", 1.0))
        env_extra = os.environ.get("ORBIT_EVIDENCE_PROBE", "")
        bump = 0.5 if env_extra == "on" else 0.0
        out = np.array([scale + bump, 2.0 * scale])
        files = {"pipelines.py": hashlib.sha256(b"fixed").hexdigest()}
        man: dict[str, Any] = {"files": files}
        if f != "HO2":
            man["covered_inputs"] = {"scale": scale, "ORBIT_EVIDENCE_PROBE": env_extra}
        else:
            man["covered_inputs"] = {"scale": scale}     # omits the env variable
        man["manifest_sha256"] = hashlib.sha256(
            repr(sorted(man["covered_inputs"].items())).encode()).hexdigest()
        return out, man

    c.manifest_run_fn = run_with
    c.manifest_variations = ({"scale": 1.0, "_env": ""}, {"scale": 1.0, "_env": "on"})
    return c


# ==========================================================================
# CASE B
# ==========================================================================

@dataclass
class CaseB:
    fault: str | None
    env: Env
    X: np.ndarray = field(default_factory=lambda: np.zeros((0, 0)))
    y: np.ndarray = field(default_factory=lambda: np.zeros(0))
    fold: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=int))
    times: np.ndarray = field(default_factory=lambda: np.zeros(0))
    pass_ids: np.ndarray = field(default_factory=lambda: np.zeros(0))
    episode_ids: np.ndarray = field(default_factory=lambda: np.zeros(0))
    run_fn: Any = None
    seed_registry: Any = None
    about_to_run: tuple = ()
    paired: Any = None
    paired_mask: Any = None
    control_rates: Any = None
    aggregated: bool = True
    unit_ids: np.ndarray = field(default_factory=lambda: np.zeros(0))
    coarser_ids: np.ndarray = field(default_factory=lambda: np.zeros(0))
    manifest: Any = None


def build_case_b(fault: str | None, env: Env, seed: int = 20260731) -> CaseB:
    f = fault
    c = CaseB(fault=f, env=env)
    g = env.rng(seed)
    # 24 episodes gives 8 coarser blocks of 3, which meets L4.7's estimability
    # precondition, so the clean path genuinely exercises the rule instead of being
    # waved through as indeterminate.
    n_ep, n_pass, n_rep = 24, 4, 3
    n = n_ep * n_pass * n_rep

    ep = np.repeat(np.arange(n_ep), n_pass * n_rep)
    pa = np.repeat(np.arange(n_ep * n_pass), n_rep)
    t = np.arange(n, dtype=float)
    age = np.tile(np.linspace(1.0, 4.0, n_pass * n_rep), n_ep)
    ddot = g.normal(0.0, 5.0, n)
    # episode-level shared state: this is what makes the EPISODE the exchangeable unit
    ep_effect = np.repeat(g.normal(0.0, 3.0, n_ep), n_pass * n_rep)
    pass_noise = np.repeat(g.normal(0.0, 0.2, n_ep * n_pass), n_rep)
    y = 0.5 * age + 0.1 * ddot + ep_effect + pass_noise + g.normal(0, 0.05, n)

    c.X = np.column_stack([age, ddot])
    c.y, c.times, c.pass_ids, c.episode_ids = y, t, pa, ep
    cut1, cut2 = int(0.6 * n), int(0.8 * n)
    c.fold = np.zeros(n, dtype=int)
    c.fold[cut1:cut2] = 1
    c.fold[cut2:] = 2
    if f == "D13":
        c.fold = g.permutation(c.fold)

    # ---- state channels ---------------------------------------------------
    def run(mutate):
        base = {"val_ratio": 0.50, "gate": 1, "m_star": "M2"}
        if mutate is None:
            return base
        leaky = {"feature_tensor": {"val_ratio": 0.10, "gate": 1, "m_star": "M2"},
                 "scaler": {"val_ratio": 0.40, "gate": 1, "m_star": "M2"},
                 "model_coefficients": {"val_ratio": 0.20, "gate": 1, "m_star": "M2"},
                 "tracker_state": {"val_ratio": 0.50, "gate": 1, "m_star": "M3"},
                 "selected_model_metadata": {"val_ratio": 0.50, "gate": 1, "m_star": "M1"},
                 "gate_state": {"val_ratio": 0.50, "gate": 0, "m_star": "M2"}}
        if f == "D6" and mutate in ("scaler", "model_coefficients", "tracker_state"):
            return base                       # channel unguarded: mutation invisible
        if f == "D9" and mutate == "selected_model_metadata":
            return base
        if f == "D10" and mutate == "gate_state":
            return base
        return leaky[mutate]

    c.run_fn = run

    # ---- seeds ------------------------------------------------------------
    # NOTE: the clean path must not be about to execute an EVALUATION seed -- that is
    # itself a contract violation. The first matrix run fired L4.4 on every clean row
    # because this fixture asked to run seed 12 while 12 was in the evaluation set.
    # The detector was correct; the fixture was wrong. Fixed here; no detector changed.
    if f == "D14":
        c.seed_registry = EC.SeedRegistry(burned={11}, evaluation={11, 12},
                                          debug={99})
        c.about_to_run = (99,)
    else:
        c.seed_registry = EC.SeedRegistry(burned={11}, evaluation={12, 13},
                                          debug={99})
        c.about_to_run = (99,)

    # ---- pairing ----------------------------------------------------------
    base_mat = np.arange(24.0).reshape(8, 3)
    if f == "D7":
        alt = base_mat.copy()
        alt[3, 1] += 0.7                     # different realisation per condition
        c.paired = {"C1": base_mat, "C2": alt}
    else:
        c.paired = {"C1": base_mat, "C2": base_mat.copy()}
    c.paired_mask = None

    # ---- negative control -------------------------------------------------
    if f == "D8":
        c.control_rates = {"R1|S1": 0.10, "R1|S2": 0.35, "R1|S3": 1.00}
    else:
        c.control_rates = {"R1|S1": 0.00, "R1|S2": 0.05, "R1|S3": 0.08}

    # ---- repeated measures / statistical unit -----------------------------
    c.aggregated = not (f == "D11")
    if f == "HO3":
        # replicates correctly aggregated to the PASS, but the pass is then treated as
        # the exchangeable unit although passes share an episode-level state
        c.unit_ids, c.coarser_ids = c.pass_ids, c.episode_ids
    else:
        # Clean path: the EPISODE is the exchangeable unit by construction (ep_effect is
        # drawn iid per episode), and the coarser grouping is a genuine block of three
        # consecutive episodes that share no state. This must be NON-DEGENERATE: the
        # previous fixture passed `zeros_like`, a single group, which made
        # within_group_icc return nan and short-circuit the check -- so the clean path
        # never exercised L4.7's null behaviour at all and could not have revealed the
        # estimator defect that this fixture now guards.
        c.unit_ids, c.coarser_ids = c.episode_ids, c.episode_ids // 3

    c.manifest = EC.provenance_manifest([Path(__file__)],
                                        {"env": env.name, "seed": seed})
    return c
