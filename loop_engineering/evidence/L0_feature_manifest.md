# LOOP 0 — FEATURE AVAILABILITY MANIFEST
Source: experiments/exp14_multisat_generalization_matrix/run_multisat_generalization_matrix.py
Construction site: build_pairs(), rows_x.append([...]) — one row per (pair, k) sample.

Shared symbols:
  epochs[i] = STALE element epoch      (held by terminal)
  epochs[j] = REFERENCE element epoch  (FUTURE publication — not held)
  t_abs     = epochs[j] + k*step_s     (the evaluated transmission instant)
  age_s     = t_abs - epochs[i]
  gap_s     = epochs[j] - epochs[i]
  old       = parsed STALE TLE record
  gs_r,gs_v = _gs_teme_km(jd(t_abs), lat, lon, alt)   [fixed GS config + UTC]
  sat_old   = Satrec.twoline2rv(old.line1, old.line2)

| ix | code name | definition | raw deps | time ref | deployable | reason | unit | consumed by | proving test |
|----|-----------|------------|----------|----------|-----------|--------|------|-------------|--------------|
| 0 | t_age_s | t_abs - epochs[i] | stale epoch, current UTC | now | **YES** | terminal knows its own TLE epoch and the clock | s | linear, age_ridge, full | T1,T3 |
| 1 | t_gap_s | epochs[j] - epochs[i] | **REFERENCE epoch**, stale epoch | future publication | **NO** | epochs[j] does not exist at transmission | s | (removed) | T1,T6 |
| 2 | stale_doppler_hz | -f_c*rangerate(sat_old,gs)/c | stale TLE, UTC, GS, carrier | now | **YES** | pure stale-element propagation | Hz | linear? no — full | T1,T2,T3 |
| 3 | sin_phase | sin((M_old + n_old*age_s/60) mod 2pi) | stale TLE M,n + age_s | now | **YES** | stale mean elements + deployable age | - | full | T1,T3 |
| 4 | cos_phase | cos(same) | as above | now | **YES** | as above | - | full | T1,T3 |
| 5 | elevation_deg | asin(rhat . gs_up) from sat_old | stale TLE, UTC, GS | now | **YES** | stale propagation + fixed GS | deg | full | T1,T3 |
| 6 | range_km | |r_sat_old - r_gs| | stale TLE, UTC, GS | now | **YES** | stale propagation + fixed GS | km | full | T1,T3 |
| 7 | stale_mean_motion_rad_min | old["mean_motion_rad_min"] | stale TLE | static | **YES** | read off the held element | rad/min | full | T3 |
| 8 | stale_bstar | old["bstar"] | stale TLE | static | **YES** | read off the held element | 1/ER | full | T3 |
| 9 | stale_ecc | old["ecc"] | stale TLE | static | **YES** | read off the held element | - | full | T3 |

## VERDICT
DEPLOYABLE_FEATURE_INDICES = (0, 2, 3, 4, 5, 6, 7, 8, 9)   # 9 of 10
NON_DEPLOYABLE_FEATURE_INDICES = (1,)                       # t_gap_s only

## Standardisation
z(.) is fitted on TRAIN and frozen (fit_correctors -> _fit_ridge_on). Frozen
scaler parameters are permitted deployment inputs under I1.

## Documented caveat (NOT a feature-level violation)
The SET of evaluated transmission instants is anchored at epochs[j]
(t_abs = epochs[j] + k*step_s), so the sampled distribution of t_age_s is
determined by reference-element publication times. At any single evaluated
instant the feature values depend only on (stale TLE, that UTC, GS, carrier)
except index 1. This is an evaluation-design property of the dataset, not a
deployment-time dependency of a feature. Recorded here so it is not rediscovered
as a leak.

## Old candidate families vs verdict (fit_correctors L1020-1044)
linear_bias_rate : c0*x[:,0] + c1                  -> feature 0 only   DEPLOYABLE
stale_age_ridge  : _fit_ridge_on((0,1),...)        -> uses t_gap_s     VIOLATION
ridge            : _fit_ridge_on(all 10,...)       -> uses t_gap_s     VIOLATION
