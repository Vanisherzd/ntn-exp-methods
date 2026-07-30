# Stronger Lightweight Baseline Comparison

## Scope and provenance

This software-only artifact re-parses the existing BK1 report. It is not a new
retraining run because the raw TLE archive and per-sample features are absent.
All values remain model-derived inter-TLE results with
`reference_is_measured_truth=false`.

## Result

The report already compares zero residual, validation-median bias, ridge, random
forest, gradient boosting, and MLP. The selected model is worse than the zero
residual SGP4 baseline at all six BK1 ages:

| Age | zero | median | ridge | RF | GBR | MLP | selected |
|---:|---:|---:|---:|---:|---:|---:|---|
| 8 h | 0.2430 | 0.2438 | 2.4941 | 1.8807 | 4.3976 | 0.3501 | MLP |
| 24 h | 0.8161 | 0.8250 | 4.0449 | 15.8441 | 20.6578 | 0.9109 | MLP |
| 48 h | 1.9433 | 1.9576 | 14.1854 | 21.3059 | 19.9189 | 2.8608 | MLP |
| 72 h | 4.8947 | 4.9404 | 5.9092 | 12.7209 | 15.2894 | 9.3962 | ridge |
| 96 h | 10.1153 | 10.1320 | 11.7663 | 120.5161 | 156.5905 | 22.0370 | ridge |
| 168 h | 26.9243 | 30.2474 | 45.2629 | 62.6705 | 227.7139 | 89.3023 | ridge |

Thus the "weak model" objection is reduced by the existing lightweight model
family and simple bias baseline. However, the artifact does not expose per-model
validation MAE, p95/p99 predictions, or trained checkpoints, so it cannot claim
fresh model-selection or tail superiority evidence.

Generated outputs:

- `experiments/exp11_stronger_baselines/results.json`
- `experiments/exp11_stronger_baselines/stronger_baselines_summary.csv`
- `fig_model_comparison_mae.{pdf,png}`
- `fig_tail_error_comparison.{pdf,png}`: explicit missing-tail-data panel.
