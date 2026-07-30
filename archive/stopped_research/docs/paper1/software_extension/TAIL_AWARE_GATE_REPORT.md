# Tail-aware and Cost-aware Gate Audit

## Scope

This is a software-only audit of the current MAE gate and the available
synthetic/proxy summaries. It does not add measured RF, packet, PER, PDR, CRC,
gateway, OTA, or live-satellite evidence. Synthetic rows are mechanism checks
only. The real reference remains model-derived with
`reference_is_measured_truth=false`.

## Decisions supported by current artifacts

| Regime | MAE gate at gamma=0.95 | Tail gate status |
|---|---|---|
| Real BK1, 8--168 h | closed in every reported row | unavailable: learned validation p95/p99 absent |
| Synthetic fresh/low residual | closed | unavailable as a gate; guard/outage proxy only |
| Synthetic moderate staleness | closed | unavailable as a gate; guard/outage proxy only |
| Synthetic extreme systematic | open | unavailable as a gate; guard/outage proxy only |

The synthetic summary does show proxy ordering: guard `62 -> 61`, `412 -> 387`,
and `14120 -> 950` Hz-equivalent for fresh, moderate, and extreme regimes;
outage proxy changes `0 -> 0`, `0 -> 0`, and `0.814 -> 0.008`. These are
software proxy values, not tail-gate decisions or link outcomes.

## Interpretation

The MAE conclusion is unchanged: the real BK1 gate closes and the extreme
systematic synthetic mechanism check opens. The requested p95/p99, `2*p99`
guard-cost, and outage gates cannot be evaluated on real BLACK KITE from the
committed summaries because learned per-sample predictions and validation tails
are missing. It would be incorrect to claim that all tail-aware gates also close
on real data until the raw TLE pipeline is rerun and exports those arrays.

Generated outputs:

- `experiments/exp12_tail_aware_gate/results.json`
- `experiments/exp12_tail_aware_gate/tail_gate_summary.csv`
- `fig_gate_metric_comparison.{pdf,png}`
- `fig_tail_gate_policy_table.{pdf,png}`
