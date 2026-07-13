# Residual Learnability Diagnostics

## Scope

This is a software-only, summary-level diagnostic of model-derived inter-TLE
residuals. `reference_is_measured_truth=false`; no measured Doppler truth or RF
observation is used. The committed artifacts contain aggregate BK1 test
statistics but not the sample-level residual sequence. Therefore autocorrelation,
sign persistence, PSD, train/validation shift, and learned-vs-baseline residual
distribution comparisons are explicitly unavailable rather than reconstructed.

## Reported BK1 diagnostics

| Staleness | mean [Hz] | std [Hz] | p50 | p90 | p99 | max | n(test) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 8 h | +0.004 | 0.419 | 0.136 | 0.575 | 1.658 | 3.217 | 1968 |
| 24 h | -0.006 | 1.413 | 0.458 | 1.815 | 5.401 | 12.961 | 2376 |
| 48 h | -0.003 | 3.252 | 1.219 | 4.323 | 12.563 | 41.941 | 2520 |
| 72 h | +0.018 | 8.473 | 2.982 | 11.020 | 33.250 | 98.635 | 2640 |
| 96 h | -0.081 | 19.455 | 5.606 | 22.434 | 79.681 | 257.543 | 2616 |
| 168 h | +0.035 | 45.383 | 15.874 | 57.607 | 191.260 | 519.419 | 2640 |

The residual mean stays near zero while scale grows with staleness. The p99
remains below the 500 Hz tolerance in the reported BK1 test summaries; the
168 h maximum is slightly above it. This supports a cautious interpretation:
the residual is small relative to the tolerance for most samples, but the tail
is not zero and is not characterized well enough to support a tail claim.

## Interpretation

The available evidence is consistent with the current negative result: at every
reported BK1 age, the selected learned model has higher held-out MAE than the
zero-residual SGP4 baseline. It supports "do not deploy residual ML by default"
as a policy conclusion. It does not prove that the residual is universally
unlearnable, because the raw sequence, pair-level dependence, and all validation
distributions are not present in the committed artifact.

Generated outputs:

- `experiments/exp10_residual_learnability/results.json`
- `experiments/exp10_residual_learnability/residual_learnability_summary.csv`
- `fig_residual_distribution.{pdf,png}`: reported quantile profiles, not a histogram.
- `fig_residual_autocorrelation.{pdf,png}`: explicit unavailable-data panel.
- `fig_train_val_test_shift.{pdf,png}`: reported held-out comparison with split-data limitation.
