"""Regression tests, one per defect discovered in the stopped research line.

Every test is two-sided: it reconstructs the BROKEN historical behaviour and asserts
the check catches it, then asserts the FIXED behaviour passes. A test that only
exercises the fixed path cannot demonstrate that it would have caught anything, and
three historical tests failed exactly that way -- one compared two arrays built from
the same object, one pinned the parameter carrying the dependence it was testing, and
one attached no threshold to the quantity it reported.

Run: pytest tests/regression/test_regressions.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(SRC))

from orbit_evidence.experiment_contract import experiment_contract as EC          # noqa: E402
from orbit_evidence.label_ensemble import reference_ensemble as RE           # noqa: E402
from orbit_evidence.causal_registry import causal_registry as CR              # noqa: E402
from orbit_evidence.pass_scheduler import visible_pass as VP                # noqa: E402

MU = 398600.4418
ST = VP.Station(24.0, 121.0, 100.0)


def circular_propagator(a_km: float, incl_deg: float, raan_deg: float = 40.0,
                        phase0: float = 0.0):
    """Analytic circular-orbit propagator with the sgp4_array signature.

    Dependency-free stand-in so these tests exercise the toolkit rather than SGP4.
    """
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
        return (np.zeros(t.shape, dtype=int), np.stack([rx, ry, rz], -1),
                np.stack([vx, vy, vz], -1))
    return prop


T0 = (2460000.5 - 2440587.5) * 86400.0


# ---------------------------------------------------------------- 1, 2

def test_rejects_future_epoch_feature():
    """A feature must not read anything dated after the decision instant."""
    ou = np.arange(100.0)                      # a state path in time

    def features(t):
        i = int(t)
        # BROKEN: reads the path at t+5, i.e. the future
        return np.array([ou[i], ou[min(i + 5, 99)]])

    def truncate(t):
        saved = ou.copy()
        ou[int(t) + 1:] = np.nan
        return saved

    def restore(saved):
        ou[:] = saved

    with pytest.raises(AssertionError, match="depends on state after"):
        EC.assert_no_future_dependency(features, [10.0, 40.0], truncate, restore)

    def fixed(t):
        return np.array([ou[int(t)], ou[max(int(t) - 5, 0)]])

    EC.assert_no_future_dependency(fixed, [10.0, 40.0], truncate, restore)


def test_publication_time_not_element_epoch():
    """Availability is the publication timestamp, never the element epoch.

    Historical measurement: epoch and publication differed by 24.3 h on a sampled
    record, and using epoch as availability made 15.4 % of pairs hand the endpoint an
    element it could not yet hold.
    """
    epoch = np.array([100.0, 200.0, 300.0])
    published = np.array([124.0, 226.0, 331.0])
    t_provision = 210.0

    held_broken = int(np.searchsorted(epoch, t_provision) - 1)      # by EPOCH
    held_fixed = int(np.searchsorted(published, t_provision) - 1)   # by PUBLICATION
    assert held_broken == 1 and published[held_broken] > t_provision, \
        "epoch-selected element was not yet published"
    assert held_fixed == 0 and published[held_fixed] <= t_provision


# ---------------------------------------------------------------- 3

def _mk_rows(source_times, window):
    return [{"tx_id": f"tx{i}", "pass_id": f"p{i}", "episode_id": float(i),
             "t_tx": float(t)}
            for i, t in enumerate(source_times)
            if window.t_start <= t <= window.t_end]


def test_row_membership_independent_of_future_catalogue():
    win = CR.FreezeWindow(0.0, 50.0)
    full = [10.0, 20.0, 30.0, 60.0, 70.0]
    trunc = [10.0, 20.0, 30.0]

    def broken(src, _win):
        # BROKEN: window end derived from the data on hand, not declared
        w = CR.FreezeWindow(0.0, max(src))
        return CR.build_registry(_mk_rows(src, w), w)

    with pytest.raises(AssertionError, match="row membership changed"):
        CR.assert_membership_independent_of_future(broken, win, full, trunc)

    def fixed(src, w):
        return CR.build_registry(_mk_rows(src, w), w)

    CR.assert_membership_independent_of_future(fixed, win, full, trunc)


# ---------------------------------------------------------------- 4, 5

def test_transmissions_above_visibility_mask():
    """Generating from passes keeps every sample above the mask; filtering a UTC grid
    does not. Historical grid sampling left 96.58 % of rows below the horizon."""
    prop = circular_propagator(6878.0, 97.4)
    cfg = VP.PassFinderConfig(mask_deg=10.0)
    grid = T0 + np.arange(0, 86400, 300.0)
    el_grid, _, _, _ = VP.look_angles(prop, ST, grid, 1.0)
    assert float(np.mean(el_grid < 0.0)) > 0.5, "grid sampling is mostly below horizon"

    iv = VP.find_passes(prop, ST, T0, T0 + 86400.0, cfg)
    assert iv, "no passes found"
    ts = np.array([t for _, _, t in VP.sample_passes(iv, (0.2, 0.5, 0.8))])
    el, _, _, ok = VP.look_angles(prop, ST, ts, 1.0)
    assert ok.all()
    assert float(el.min()) >= cfg.mask_deg - 1e-6, f"min elevation {el.min():.4f}"


def test_exit_crossing_bisection_bracket():
    """The historical exit bisection received (above, below) instead of
    (below, above), so `abs(hi-lo) <= tol` was immediately true and the coarse
    midpoint was returned -- placing the last sample past the true exit."""
    prop = circular_propagator(6878.0, 97.4)
    cfg = VP.PassFinderConfig(mask_deg=10.0, coarse_step_s=60.0)
    iv = VP.find_passes(prop, ST, T0, T0 + 86400.0, cfg)
    assert iv
    for a, b in iv:
        el, _, _, _ = VP.look_angles(prop, ST, np.array([a, b]), 1.0)
        assert el.min() >= cfg.mask_deg - 1e-6, "refined crossing below the mask"
        el_out, _, _, _ = VP.look_angles(
            prop, ST, np.array([a - cfg.bisect_tol_s - 1.0,
                                b + cfg.bisect_tol_s + 1.0]), 1.0)
        assert el_out.max() < cfg.mask_deg + 1e-6, "interval is not maximal"


# ---------------------------------------------------------------- 6, 7

def test_reference_ensemble_uncertainty():
    """Single arbitrary reference vs ensemble median with published uncertainty."""
    members = [100.0, 103.0, 97.0, 101.0]
    lab = RE.build_label(members, closure_time=48.0, k_min=2, sigma_max=10.0)
    assert lab.n_members == 4
    assert lab.value == pytest.approx(float(np.median(members)))
    assert lab.sigma > 0.0
    # BROKEN: the single first-qualifying reference carries NO uncertainty, and which
    # member is "first" is arbitrary -- so the target itself moves with the ordering.
    spread = max(members) - min(members)
    single_choice_swing = max(abs(m - lab.value) for m in members)
    assert single_choice_swing >= spread / 2.0, \
        "an arbitrary single reference sits at least half a spread from the median"
    assert lab.sigma < spread, "ensemble sigma must be smaller than the raw spread"
    # and the ensemble PUBLISHES that uncertainty, which a single reference cannot
    assert math.isfinite(lab.sigma) and lab.sigma > 0.0
    # large spread is RETAINED, not deleted
    amb = RE.build_label([0.0, 200.0], closure_time=48.0, k_min=2, sigma_max=10.0)
    assert amb.status == RE.LabelStatusName.AMBIGUOUS
    assert math.isfinite(amb.value), "ambiguous rows must be retained with a value"
    thin = RE.build_label([5.0], closure_time=48.0, k_min=2, sigma_max=10.0)
    assert thin.status == RE.LabelStatusName.CENSORED


def test_label_status_is_not_outcome_dependent():
    """The status must depend on member coverage and spread ONLY -- never on the
    labelled value or on a physics baseline.

    Predecessor defect (found by review, not by us): status was assigned by
    `sigma > abs(median - baseline)`, i.e. by comparing the uncertainty to the
    RESIDUAL. That makes the annotation a function of the quantity under study, so
    rows with small residuals are preferentially marked ambiguous and any
    completeness rate computed from the status is biased -- 4-11x inflation of the
    median target was measured on the stopped research line.

    Two-sided: the same members under a shifted baseline must yield an IDENTICAL
    status, and the declared ceiling must still be able to produce AMBIGUOUS.
    """
    members = [100.0, 103.0, 97.0, 101.0]
    base = RE.build_label(members, closure_time=1.0, k_min=2, sigma_max=10.0)

    # The residual is the only thing that changes across these; nothing may move.
    for shifted_baseline in (0.0, 90.0, 100.0, 1e6):
        offset = [m - shifted_baseline for m in members]
        got = RE.build_label(offset, closure_time=1.0, k_min=2, sigma_max=10.0)
        assert got.status == base.status, (
            f"status moved with the baseline ({shifted_baseline}): "
            f"{got.status} != {base.status} -- status is outcome-dependent")
        assert got.sigma == pytest.approx(base.sigma), \
            "sigma must be translation-invariant"

    # `baseline` must not be reachable at all, or the defect returns via a default.
    with pytest.raises(TypeError):
        RE.build_label(members, closure_time=1.0, baseline=90.0)

    # Red path: the declared ceiling, and only it, decides AMBIGUOUS.
    assert RE.build_label(members, closure_time=1.0, k_min=2,
                          sigma_max=0.1).status == RE.LabelStatusName.AMBIGUOUS
    # No declared ceiling => no spread classification is invented.
    assert RE.build_label([0.0, 500.0], closure_time=1.0, k_min=2,
                          sigma_max=None).status == RE.LabelStatusName.COMPLETE


def test_label_status_never_changes_row_membership():
    """The status is diagnostic. Every input row must appear in the output
    population regardless of status, including CENSORED and AMBIGUOUS rows."""
    rows = [[100.0, 101.0, 99.0],   # tight     -> COMPLETE
            [0.0, 400.0],           # wide      -> AMBIGUOUS
            [7.0]]                  # too few   -> CENSORED
    out = [RE.build_label(r, closure_time=1.0, k_min=2, sigma_max=10.0) for r in rows]
    assert len(out) == len(rows), "labelling changed the number of rows"
    assert {o.status for o in out} == {RE.LabelStatusName.COMPLETE,
                                       RE.LabelStatusName.AMBIGUOUS,
                                       RE.LabelStatusName.CENSORED}
    # A censored row still occupies its slot: value is nan, the ROW is not dropped.
    assert math.isnan(out[2].value) and out[2].n_members == 1


def test_scheduler_convergence_over_declared_step_range():
    """`coarse_step_s` is a solver setting, so its influence must be bounded by
    measurement over a pre-declared range rather than asserted away.

    Declared range: 10-60 s, i.e. up to `min_pass_s`. Across it the recovered pass
    extents must agree to within the bisection tolerance, and the count must not
    change. Also two-sided: a step COARSER than `min_pass_s` is rejected at
    construction, because a shortest-admissible pass can hide between grid points.
    """
    prop = circular_propagator(6878.0, 97.4)
    declared_steps = (10.0, 15.0, 30.0, 60.0)
    ref = None
    for step in declared_steps:
        cfg = VP.PassFinderConfig(mask_deg=10.0, coarse_step_s=step,
                                  bisect_tol_s=1.0, min_pass_s=60.0)
        iv = VP.find_passes(prop, ST, T0, T0 + 86400.0, cfg)
        assert iv, f"no passes at coarse_step_s={step}"
        # Every reported boundary is inside the true pass, at every step size.
        for a, b in iv:
            el, _, _, _ = VP.look_angles(prop, ST, np.array([a, b]), 1.0)
            assert el.min() >= cfg.mask_deg - 1e-6, \
                f"boundary below mask at step {step}"
        if ref is None:
            ref = iv
            continue
        assert len(iv) == len(ref), \
            f"pass count changed with the solver step: {len(iv)} vs {len(ref)} at {step}"
        for (a, b), (ra, rb) in zip(iv, ref):
            assert abs(a - ra) <= 2 * cfg.bisect_tol_s, \
                f"entry moved {abs(a - ra):.3f} s at step {step}"
            assert abs(b - rb) <= 2 * cfg.bisect_tol_s, \
                f"exit moved {abs(b - rb):.3f} s at step {step}"

    with pytest.raises(ValueError, match="exceeds min_pass_s"):
        VP.PassFinderConfig(mask_deg=10.0, coarse_step_s=120.0, min_pass_s=60.0)


def test_label_closure_precedes_training():
    closure = np.array([10.0, 20.0, 30.0, 40.0])
    ok = RE.assert_closure_precedes_training(closure, decision_time=25.0)
    assert ok.tolist() == [True, True, False, False]
    assert not ok[closure > 25.0].any(), "a label closing after the decision was admitted"


# ---------------------------------------------------------------- 8, 9

def test_common_random_numbers_across_conditions():
    """Including the condition in the seed key silently unpairs the arms."""
    broken = {c: [EC.derive_seed("p", "R1", "S2", c, i) for i in range(4)]
              for c in ("C1", "C2", "C3")}
    assert broken["C1"] != broken["C2"], "condition-keyed seeds differ (the defect)"

    fixed = {c: EC.common_random_numbers("p", ("R1", "S2"), 4)
             for c in ("C1", "C2", "C3")}
    assert fixed["C1"] == fixed["C2"] == fixed["C3"]

    base = np.arange(12.0).reshape(4, 3)
    EC.assert_paired({"C1": base, "C2": base.copy(), "C3": base.copy()})
    moved = base.copy()
    moved[2, 1] += 1e-12
    with pytest.raises(AssertionError, match=r"max\|delta\|"):
        EC.assert_paired({"C1": base, "C2": moved})


def test_burned_seeds_never_enter_evaluation():
    reg = EC.SeedRegistry(evaluation={1, 2, 3}, debug={99})
    reg.assert_clean()
    reg.burn([2], reason="outcomes inspected by a reviewer")
    reg.assert_clean()
    assert 2 not in reg.evaluation and 2 in reg.burned
    with pytest.raises(AssertionError, match="would execute evaluation seeds"):
        reg.assert_not_evaluation([3])
    reg.assert_not_evaluation([2, 99])
    bad = EC.SeedRegistry(burned={5}, evaluation={5, 6})
    with pytest.raises(AssertionError, match="burned seeds present"):
        bad.assert_clean()


# ---------------------------------------------------------------- 10

def test_tracker_state_frozen_after_decision():
    """State must not advance at refreshes that fall after the freeze.

    Historical contradiction: 'advanced ONLY at refresh' plus 'no observation during
    deployment', while twelve refreshes fell inside the deployment window. The leak
    gave 83-92 % admission on a null control.
    """
    refreshes = [10.0, 20.0, 30.0, 40.0]
    t_freeze = 25.0

    def run(freeze_respected: bool) -> list[float]:
        state, hist = 0.0, []
        for t in refreshes:
            if freeze_respected and t > t_freeze:
                hist.append(state)
                continue
            state += 1.0
            hist.append(state)
        return hist

    broken = run(False)
    fixed = run(True)
    assert broken[-1] != broken[1], "unfrozen state kept moving (the defect)"
    assert fixed[1] == fixed[2] == fixed[3], "state advanced after the freeze"


# ---------------------------------------------------------------- 11-15

def _canary_runner(effective: bool):
    """`effective=False` reproduces the historical no-op mutations, which were
    reported as 'undetectable leakage' when they were simply inert."""
    def run(mutate):
        out = {"val_ratio": 0.5, "gate": 1, "m_star": "M2"}
        if mutate is None:
            return out
        if not effective:
            return out                      # no-op: the mutation never bites
        return {"feature_tensor": {"val_ratio": 0.1, "gate": 1, "m_star": "M2"},
                "scaler": {"val_ratio": 0.4, "gate": 1, "m_star": "M2"},
                "model_coefficients": {"val_ratio": 0.2, "gate": 1, "m_star": "M2"},
                "tracker_state": {"val_ratio": 0.5, "gate": 1, "m_star": "M3"},
                "selected_model_metadata": {"val_ratio": 0.5, "gate": 1, "m_star": "M1"},
                "gate_state": {"val_ratio": 0.5, "gate": 0, "m_star": "M2"}}[mutate]
    return run


@pytest.mark.parametrize("channel", list(EC.STATE_CHANNELS))
def test_mutation_canary_channels(channel):
    """One test per state channel. Feature-tensor-only scoping missed five of six."""
    inert = EC.mutation_canary(_canary_runner(False), channels=(channel,))
    assert inert[channel] is False, "an inert mutation must be reported as undetected"
    live = EC.mutation_canary(_canary_runner(True), channels=(channel,))
    assert live[channel] is True, f"channel {channel} leak went undetected"


def test_mutation_canary_covers_all_six_channels():
    assert set(EC.STATE_CHANNELS) == {
        "feature_tensor", "scaler", "model_coefficients", "tracker_state",
        "selected_model_metadata", "gate_state"}
    live = EC.mutation_canary(_canary_runner(True))
    assert all(live.values()), f"undetected: {[k for k, v in live.items() if not v]}"


# ---------------------------------------------------------------- 16

def test_negative_control_has_no_systematic_signal():
    """With the injected effect at zero the gate must stay shut, at EVERY covariate
    level. Historical failure: 1.00 admission in all nine cells, 57-93 % apparent
    gain, from a deterministic secular mismatch surviving zero injection."""
    broken = {"R1|S1": 1.00, "R1|S2": 1.00, "R1|S3": 1.00}
    v = EC.negative_control_verdict(broken)
    assert v["pass"] is False and len(v["failing_cells"]) == 3

    good = {"R1|S1": 0.00, "R1|S2": 0.08, "R1|S3": 0.17}
    assert EC.negative_control_verdict(good)["pass"] is True
    # a control scheduled at only one level hides a covariate-monotone leak
    partial = EC.negative_control_verdict({"R1|S2": 0.05})
    assert partial["pass"] is True and len(partial["failing_cells"]) == 0


# ---------------------------------------------------------------- 17

def test_no_unbounded_state_divergence():
    t = np.arange(100.0)
    integrating = 0.01 * t ** 2                       # the rejected rate-step design
    assert EC.unbounded_divergence_check(t, integrating)["pass"] is False
    bounded = 5.0 + 0.1 * np.sin(t)
    assert EC.unbounded_divergence_check(t, bounded)["pass"] is True


def test_physical_scale_has_both_bounds():
    """A floor alone permitted a 5.8 %-of-signal excursion."""
    d = np.full(100, 10000.0)
    assert EC.physical_scale_check(np.full(100, 1.0), d, 0.002, 0.02)["label"] \
        == "INSUFFICIENT_SCALE"
    assert EC.physical_scale_check(np.full(100, 580.0), d, 0.002, 0.02)["label"] \
        == "EXCEEDS_PHYSICAL_CEILING"
    ok = EC.physical_scale_check(np.full(100, 100.0), d, 0.002, 0.02)
    assert ok["label"] == "IN_RANGE" and ok["pass"]


# ---------------------------------------------------------------- 18

def test_within_pass_samples_are_not_independent():
    """Replicates must be collapsed before any metric. Measured ICC 0.59-0.79, and
    up to 0.999 between symmetric sample positions."""
    gid = np.repeat(np.arange(20), 3)
    vals = np.repeat(np.random.default_rng(0).normal(0, 1, 20), 3) + \
        np.random.default_rng(1).normal(0, 0.05, 60)
    icc = EC.within_group_icc(vals, gid)
    assert icc > 0.8, f"constructed replicate structure not detected (icc={icc:.3f})"
    uniq, agg = EC.aggregate_repeated_measures(vals, gid)
    assert uniq.size == 20 and agg.size == 20, "aggregation did not collapse replicates"
    assert agg.size < vals.size


# ---------------------------------------------------------------- 19

def test_grid_uniformity_warning():
    """One emulation returned 27 of 27 cells identical in both reported quantities."""
    uniform = {f"c{i}": {"gate": 1.0, "val_ratio": 0.50} for i in range(9)}
    w = EC.grid_uniformity_warning(uniform)
    assert w["fires"] is True and w["per_metric_uniform"]["gate"] is True
    varied = {f"c{i}": {"gate": 0.5 + 0.05 * i, "val_ratio": 0.1 + 0.05 * i}
              for i in range(9)}
    assert EC.grid_uniformity_warning(varied)["fires"] is False


# ---------------------------------------------------------------- 20

def test_generator_matches_declared_physics():
    """If an admissible oracle reproduces the generator, the scenario is a
    calibration control. A single-feature guard read 0.66-0.77 while a two-term
    oracle reached 0.998."""
    rng = np.random.default_rng(3)
    n = 400
    age = rng.uniform(0, 3e5, n)
    ddot = rng.normal(0, 50, n)
    y = -ddot * (1e-6 * age + 0.01) + rng.normal(0, 1e-3, n)
    X = np.column_stack([age, ddot])
    tr = np.arange(n) < 300
    te = ~tr

    single = max(abs(np.corrcoef(X[:, c], y)[0, 1]) for c in (0, 1))
    assert single < 0.95, f"single-feature guard reads {single:.3f} and sees nothing"

    m = EC.functional_form_match(
        X, y, tr, te,
        lambda A: np.column_stack([np.ones(A.shape[0]), A[:, 1], A[:, 1] * A[:, 0]]))
    assert m["r2_out_of_sample"] >= 0.95
    assert m["classification"] == "CONTROLLED CALIBRATION / SANITY SCENARIO"

    y2 = rng.normal(0, 1, n)
    m2 = EC.functional_form_match(
        X, y2, tr, te,
        lambda A: np.column_stack([np.ones(A.shape[0]), A[:, 1], A[:, 1] * A[:, 0]]))
    assert m2["classification"] == "not calibration-classified"
