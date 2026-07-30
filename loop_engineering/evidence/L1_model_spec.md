# LOOP 1 — MINIMAL DEPLOYABLE MODEL SPECIFICATION
Status: SPEC drafted, NOT yet gated (awaiting L0 independent verification)

## Single source of truth (one constant, not scattered lists)

    DEPLOYABLE_FEATURE_INDICES = (0, 2, 3, 4, 5, 6, 7, 8, 9)
    NON_DEPLOYABLE_FEATURE_INDICES = (1,)   # t_gap_s

Every candidate's index tuple MUST be a subset of DEPLOYABLE_FEATURE_INDICES
(asserted at import time, T4).

## Candidate family — minimum correction, nothing invented

| new name | old name | feature indices | change |
|----------|----------|-----------------|--------|
| linear_age | linear_bias_rate | (0,) | rename only; was already deployable |
| age_ridge | stale_age_ridge | (0,) | t_gap_s REMOVED |
| deployable_ridge | ridge | (0,2,3,4,5,6,7,8,9) | t_gap_s REMOVED |

References (never selected, cannot open the gate) unchanged:
  zero  = SGP4 physics baseline
  mean_bias / median_bias = diagnostic constants

Renames are mandatory: "stale_age" implied the (age,gap) pair and would now be
misleading. No name may imply a removed feature.

## Known consequence to disclose, not hide
age_ridge is a ridge on a single feature, so it is near-degenerate with
linear_age (OLS on the same feature). We keep both because dropping one would be
a change beyond removal of the non-deployable feature (I3). Expect their
validation MAEs to be close; the selection rule (argmin over M_L) is unchanged.

## Artefacts each run must persist (fixes F1)
- per-candidate TRAIN/VALIDATION/TEST MAE for every member of M_L and every
  reference predictor (old runs stored only the selected model's metrics)
- selected m*, gate G, and the selection reason (argmin value + margin)
- feature manifest + model manifest (machine-readable JSON)
- source/data/config hashes

## Explicitly NOT changed (I3)
canonical histories; qualification; satellites; staleness targets and bands;
chronological 60/20/20 boundaries; screening thresholds; pair definition; K=24;
carrier; ground station; metrics; gamma frontier; statistical procedures; seeds.
