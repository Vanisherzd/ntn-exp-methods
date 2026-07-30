"""The chronological-split baseline, implemented rather than asserted.

The paper compares its contract against what a careful practitioner doing
chronological train/validation/test splitting would already catch. That baseline was
previously hand-assigned per fault, which made the comparison's denominator an
assertion. This module implements it, so the number is measured on the same fixtures
and in the same sweep as the contract.

Scope is deliberately narrow, because chronological splitting IS narrow. It is a
protocol property, not a detector suite: it constrains the ORDER of quantities that
are present in the dataset. The three checks below are what that property yields when
applied conscientiously.

  B1  folds are time-ordered and mutually disjoint
  B2  no row assigned to a fold carries a timestamp belonging to a later fold
  B3  no label used at a decision point carries a timestamp after that decision point

A fault is counted as caught by the baseline if any of B1-B3 fires. Nothing here is
tuned to produce a particular count; each check is the plain reading of the property.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class BaselineFinding:
    check: str
    detail: str


def check_fold_order(fold: np.ndarray, times: np.ndarray) -> BaselineFinding | None:
    """B1 -- folds must be ordered in time and must not overlap."""
    f, t = np.asarray(fold, dtype=int), np.asarray(times, dtype=float)
    spans = {}
    for k in sorted(set(f.tolist())):
        m = f == k
        if m.any():
            spans[k] = (float(t[m].min()), float(t[m].max()))
    keys = sorted(spans)
    for a, b in zip(keys, keys[1:]):
        if spans[a][1] > spans[b][0]:
            return BaselineFinding(
                "B1", f"fold {a} ends at {spans[a][1]:.6g} but fold {b} starts at "
                      f"{spans[b][0]:.6g}; folds overlap in time")
    return None


def check_row_fold_membership(fold: np.ndarray, times: np.ndarray) -> BaselineFinding | None:
    """B2 -- no row sits in a fold whose time span it does not belong to."""
    f, t = np.asarray(fold, dtype=int), np.asarray(times, dtype=float)
    keys = sorted(set(f.tolist()))
    if len(keys) < 2:
        return None
    bounds = {k: (float(t[f == k].min()), float(t[f == k].max()))
              for k in keys if (f == k).any()}
    for k in keys:
        later = [j for j in keys if j > k]
        if not later:
            continue
        start_of_next = min(bounds[j][0] for j in later)
        bad = int(np.sum((f == k) & (t > start_of_next)))
        if bad:
            return BaselineFinding(
                "B2", f"{bad} row(s) in fold {k} carry timestamps after fold "
                      f"{min(later)} begins")
    return None


def check_label_not_future(closure: np.ndarray, decision_time: float,
                          used: np.ndarray) -> BaselineFinding | None:
    """B3 -- a label used at a decision point must not be dated after it."""
    c = np.asarray(closure, dtype=float)
    u = np.asarray(used, dtype=bool)
    if not u.any():
        return None
    bad = int(np.sum(c[u] > decision_time))
    if bad:
        return BaselineFinding(
            "B3", f"{bad} label(s) used at decision time {decision_time:.6g} carry "
                  f"timestamps after it")
    return None


def run_baseline_case_a(case: Any) -> list[str]:
    """Apply the baseline to a CASE A fixture. Returns the checks that fired."""
    fired: list[str] = []
    # CASE A has no learner folds; the ordering property applicable to it is B3.
    r = check_label_not_future(case.closure, case.closure_decision, case.used_mask)
    if r:
        fired.append(r.check)
    return fired


def run_baseline_case_b(case: Any) -> list[str]:
    """Apply the baseline to a CASE B fixture. Returns the checks that fired."""
    fired: list[str] = []
    for r in (check_fold_order(case.fold, case.times),
              check_row_fold_membership(case.fold, case.times)):
        if r:
            fired.append(r.check)
    return fired


BASELINE_CHECKS = ("B1", "B2", "B3")
BASELINE_SCOPE = (
    "Chronological splitting is a protocol property constraining the order of "
    "quantities present in the dataset. It is not a competing detector suite, and the "
    "comparison in the paper is not tool-versus-tool: it measures how much of the "
    "fault space that property covers when applied conscientiously."
)
