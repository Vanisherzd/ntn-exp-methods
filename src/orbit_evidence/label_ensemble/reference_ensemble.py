"""Reference-ensemble labels with published uncertainty.

Third reusable asset. Replaces "pick the first qualifying later solution", whose
arbitrariness moved the target further than the target's own magnitude: the spread
across equally valid references exceeded the label itself in 51.8 % of measured
visible cases, with a ratio of 1.81 at short staleness. The ensemble median plus a
published MAD reduced that ratio to 0.06-0.39.

Known limitation, measured and NOT solved here: when most ensemble members lie on
the same side in time, they share a common propagation error that a mutual MAD
cannot see. A split-half comparison by propagation distance found a hidden
systematic 5-16x larger than a 5 % decision margin. Report `split_half_spread`
alongside `sigma` and treat sigma as a LOWER BOUND on label uncertainty.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np

MAD_TO_SIGMA = 1.4826


@dataclass(frozen=True)
class EnsembleLabel:
    value: float
    sigma: float
    n_members: int
    closure_time: float
    status: str
    member_ids: tuple[str, ...] = ()
    split_half_spread: float | None = None


def canonicalise(members: Sequence[dict], key_fn: Callable[[dict], str],
                 order_fn: Callable[[dict], tuple]) -> list[dict]:
    """Deterministic de-duplication: one member per physical key, earliest by order.

    `key_fn` must identify the physical solution and EXCLUDE bookkeeping fields.
    Historical caution: a key built from element text but excluding the epoch collided
    across distinct epochs, while an epoch quantised to 1 ms let re-publications
    864 us apart survive as separate members -- so two fits of one solution counted as
    independent evidence and drove the uncertainty estimate to near zero. Quantise
    time coarsely enough to absorb print precision, and include it in the key.
    """
    best: dict[str, dict] = {}
    for m in members:
        k = key_fn(m)
        if k not in best or order_fn(m) < order_fn(best[k]):
            best[k] = m
    return [best[k] for k in sorted(best)]


def build_label(member_values: Sequence[float], closure_time: float,
                k_min: int = 2, member_ids: Sequence[str] = (),
                propagation_distance: Sequence[float] | None = None,
                sigma_max: float | None = None) -> EnsembleLabel:
    """Median-of-ensemble label with MAD uncertainty and a COVERAGE-ONLY status.

    The status depends only on how many members were available (`k_min`) and on
    their mutual spread against a DECLARED ceiling (`sigma_max`). It never depends
    on the labelled value, on a physics baseline, or on the residual between them.

    Why this signature has no `baseline`: an earlier version classified COMPLETE by
    comparing sigma to the residual `median - baseline`, which makes the status
    OUTCOME-DEPENDENT -- rows are annotated according to the very quantity under
    study, so every completeness rate computed from it is biased (median target
    inflated 4-11x in one measurement on the stopped line). That predecessor is the
    reason this docstring exists; the parameter is removed so the defect cannot
    return through a default argument.

    `sigma_max` must be declared by the caller from instrument or catalogue knowledge,
    never fitted to the data at hand. Left as None, no spread classification is made and
    the status is UNCLASSIFIED_NO_CEILING -- deliberately NOT COMPLETE, so that a
    completeness rate cannot silently absorb rows whose spread was never checked.

    The four statuses are mutually exclusive and each means exactly one thing:
      COMPLETE                        enough members, spread within a declared ceiling
      AMBIGUOUS_HIGH_SPREAD           enough members, spread exceeds the ceiling
      CENSORED_INSUFFICIENT_REFERENCES  fewer than k_min members
      UNCLASSIFIED_NO_CEILING         enough members, no ceiling declared
      INVALID_SOURCE_METADATA         a member is not finite

    The status is DIAGNOSTIC: it annotates uncertainty. It never creates or deletes
    a row, and it never changes the evaluation population -- AMBIGUOUS_HIGH_SPREAD
    rows are marked and RETAINED, because dropping them selects on the outcome.
    Row membership is owned by the frozen registry, not by this function.
    """
    v = np.asarray(member_values, dtype=float)
    if member_ids and len(member_ids) != v.size:
        raise ValueError(
            f"member_ids has {len(member_ids)} entries for {v.size} values: a label whose "
            "provenance does not enumerate its own members is not auditable")
    if v.size < k_min:
        return EnsembleLabel(math.nan, math.nan, int(v.size), closure_time,
                             LabelStatusName.CENSORED, tuple(member_ids))
    if not np.all(np.isfinite(v)):
        # A non-finite member makes the median and MAD non-finite, and `sigma > sigma_max`
        # is then False -- so the row would be stamped COMPLETE. An unusable label counted
        # as complete biases every completeness rate UPWARD, which is the same class of
        # defect as the outcome-dependent status this function was rewritten to remove.
        return EnsembleLabel(math.nan, math.nan, int(v.size), closure_time,
                             LabelStatusName.INVALID, tuple(member_ids))
    med = float(np.median(v))
    sigma = float(MAD_TO_SIGMA * np.median(np.abs(v - med)))
    shs = None
    if propagation_distance is not None and v.size >= 4:
        d = np.asarray(propagation_distance, dtype=float)
        near, far = v[d <= np.median(d)], v[d > np.median(d)]
        if near.size and far.size:
            shs = float(abs(np.median(near) - np.median(far)))
    # COMPLETE must mean ONE thing: spread was checked against a declared ceiling and
    # passed. Without a ceiling nothing was checked, so the row is UNCLASSIFIED rather
    # than complete -- otherwise a completeness rate silently absorbs unchecked rows.
    if sigma_max is None:
        status = LabelStatusName.UNCLASSIFIED
    elif sigma > sigma_max:
        status = LabelStatusName.AMBIGUOUS
    else:
        status = LabelStatusName.COMPLETE
    return EnsembleLabel(med, sigma, int(v.size), closure_time, status,
                         tuple(member_ids), shs)


class LabelStatusName:
    COMPLETE = "COMPLETE"
    CENSORED = "CENSORED_INSUFFICIENT_REFERENCES"
    AMBIGUOUS = "AMBIGUOUS_HIGH_SPREAD"
    INVALID = "INVALID_SOURCE_METADATA"
    UNCLASSIFIED = "UNCLASSIFIED_NO_CEILING"


def assert_closure_precedes_training(closure_times: np.ndarray,
                                     decision_time: float) -> np.ndarray:
    """Boolean mask of labels admissible at `decision_time`. Strictly causal."""
    c = np.asarray(closure_times, dtype=float)
    return c <= decision_time
