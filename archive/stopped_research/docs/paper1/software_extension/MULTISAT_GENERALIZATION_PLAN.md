# Multi-satellite Generalization Plan (Paper 1+)

## Current status

No additional satellite TLE archive is present and no external download was
performed. The dry-run uses only the committed BK1 target-specific and BK1 to
BK2 summary rows. They are tagged `summary_only`; no new generalization result
is claimed.

## Pipeline contract

Input is a historical TLE-derived CSV with one row per train-source/deploy-target
and staleness setting:

`train_source, deploy_target, staleness_h, baseline_mae_hz, learned_mae_hz,
p95_abs_error_hz, p99_abs_error_hz, n_pairs, reject_count`

The output matrix must report baseline MAE, learned MAE, degradation, MAE gate,
p95/p99 error, accepted-pair count, and rejection count. Splits remain
chronological within each satellite; no future TLE may enter training.

## Required future campaign

1. Restore or obtain raw TLE histories through an approved local data path.
2. Export pair-level residual arrays and pair identifiers for every satellite.
3. Run within-satellite target-specific and cross-satellite train/deploy rows.
4. Add residual autocorrelation, tail metrics, and model identity to each row.
5. Audit the matrix for satellite-specific failures before making any universal
   claim.

Run the current dry-run with:

```bash
uv run experiments/exp13_multisat_generalization/run_multisat_generalization.py --dry-run
```
