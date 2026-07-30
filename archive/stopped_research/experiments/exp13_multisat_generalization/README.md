# Multi-satellite generalization skeleton

This is a Paper 1+ pipeline skeleton. It accepts a summary CSV with one row per
train-source/deploy-target/staleness setting and emits a generalization matrix.
It does not download TLEs or infer missing pair counts.

Dry-run using the committed BLACK KITE summary:

```bash
uv run experiments/exp13_multisat_generalization/run_multisat_generalization.py --dry-run
```

Future input columns:

`train_source, deploy_target, staleness_h, baseline_mae_hz, learned_mae_hz,
p95_abs_error_hz, p99_abs_error_hz, n_pairs, reject_count`

The current dry-run is `summary_only`: it contains BK1 target-specific and BK1
to BK2 summary rows, but no raw TLE-derived pair arrays. All missing tail and
count fields remain blank.
