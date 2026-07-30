# DECISION RECORDS

## D1 (Loop 0) — deployable feature set
DEPLOYABLE_FEATURE_INDICES = (0,2,3,4,5,6,7,8,9); only index 1 (t_gap_s) removed.
Rationale: full dependency trace in evidence/L0_feature_manifest.md. Nine of ten
features resolve to (stale TLE, current UTC, fixed GS, carrier). This is the
MINIMUM correction and adds no new feature. Consistent with I3.

## D2 (Loop 0) — evaluation-window anchoring retained
t_abs remains epochs[j] + k*step_s. Changing the anchor would alter the cohort
(I3) and is NOT required by I1/I2, because at any evaluated instant the retained
features depend only on deployable inputs. Recorded as a caveat, not a fix.

## D3 (Loop 2) — no git branch/worktree used
The working tree carries many uncommitted modifications from earlier phases.
Switching branches would risk those changes. Implementation therefore proceeded
in place, with loop_engineering/snapshots/pipeline_pre_L2.py as the rollback
point. Old artifacts are untouched; the rerun writes to a NEW namespace.

## D4 (Loop 2) — mechanical evidence substituted for unavailable review
Both L0 verifier agents were killed by an account session limit. Rather than
transition on my own assertion, T1 (reference-epoch perturbation) was written to
EMPIRICALLY decide the manifest: swap only the reference element, hold every
deployment input fixed, observe which feature indices move. Result: exactly
index 1, on all 9 satellites. Lifecycle may therefore reach
MECHANICALLY_VERIFIED but NOT REVIEWED. Independent review remains owed.
