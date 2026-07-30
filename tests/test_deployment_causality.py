"""Deployment-causality test suite (loop-engineering invariants I1-I4, T2-T7).

These tests exist to make the t_gap_s class of bug mechanically impossible to
reintroduce. T1 (reference-epoch perturbation) lives in
loop_engineering/evidence/ because it needs the raw archive; everything here
runs without network or raw data.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "exp14_multisat_generalization_matrix"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, EXP / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load("run_multisat_generalization_matrix")


# ---------------------------------------------------------------- T3 / T4 ----
def test_t3_every_deployable_index_is_known_and_disjoint():
    """T3: the deployable/non-deployable partition is total and disjoint."""
    dep = set(R.DEPLOYABLE_FEATURE_INDICES)
    non = set(R.NON_DEPLOYABLE_FEATURE_INDICES)
    assert dep | non == set(range(len(R.FEATURE_NAMES)))
    assert dep & non == set()
    assert non == {1}, "t_gap_s is the only non-deployable feature"
    assert R.FEATURE_NAMES[1] == "t_gap_s"


def test_t4_every_candidate_uses_only_deployable_features():
    """T4: model manifest is a subset of DEPLOYABLE_FEATURE_INDICES."""
    for name, idx in (("age_ridge", R.AGE_ONLY_FEATURES),
                      ("deployable_ridge", R.DEPLOYABLE_RIDGE_FEATURES),
                      ("linear_age", (0,))):
        assert set(idx) <= set(R.DEPLOYABLE_FEATURE_INDICES), name


def test_t4_learned_model_names_do_not_imply_removed_features():
    """A name must not advertise a feature the model no longer consumes."""
    for name in R.LEARNED_MODELS:
        assert "gap" not in name
        assert name != "stale_age_ridge", "stale_age implied the (age,gap) pair"


# ---------------------------------------------------------------- T6 ---------
@pytest.mark.parametrize("bad", [(1,), (0, 1), tuple(range(10))])
def test_t6_checker_rejects_the_old_bug(bad):
    """T6: reconstructing the old t_gap_s dependency must be rejected."""
    with pytest.raises(ValueError, match="deployment-causality violation"):
        R.assert_deployable(bad, "old_stale_age_ridge")


def test_t6_checker_accepts_deployable_sets():
    assert R.assert_deployable((0,), "ok") == (0,)
    assert R.assert_deployable(R.DEPLOYABLE_FEATURE_INDICES, "ok")


# ---------------------------------------------------------------- T2 ---------
def test_t2_feature_manifest_marks_reference_dependency():
    """T2 (static form): the manifest itself denies index 1 at deployment."""
    man = {m["index"]: m for m in R.feature_manifest()}
    assert man[1]["deployable"] is False
    assert all(man[i]["deployable"] for i in R.DEPLOYABLE_FEATURE_INDICES)
    assert len(man) == len(R.FEATURE_NAMES)


# ---------------------------------------------------------------- T5 ---------
def test_t5_gate_reads_only_validation_quantities():
    """T5: evaluate_gates must be callable from validation aggregates alone."""
    import inspect
    src = inspect.getsource(R.evaluate_gates)
    for forbidden in ("test", "held", "_te"):
        assert forbidden not in src.lower().replace("latest", ""), forbidden


# ---------------------------------------------------------------- T7 ---------
def test_t7_feature_partition_is_deterministic():
    """T7: constants are derived, not hand-listed, so they cannot drift."""
    expect = tuple(i for i in range(len(R.FEATURE_NAMES))
                   if i not in R.NON_DEPLOYABLE_FEATURE_INDICES)
    assert R.DEPLOYABLE_FEATURE_INDICES == expect
