# Paper 1 Software-only Strengthening Campaign

## What was run

The campaign was intentionally limited to committed software artifacts and did
not access hardware, RF, USRP, firmware, OTA, or external TLE services.

Commands run:

```bash
uv run experiments/exp10_residual_learnability/run_residual_learnability.py
uv run experiments/exp11_stronger_baselines/run_stronger_baselines.py
uv run experiments/exp12_tail_aware_gate/run_tail_aware_gate.py
uv run experiments/exp13_multisat_generalization/run_multisat_generalization.py --dry-run
```

The raw TLE archive expected by the original real-data scripts is absent, so no
new pair-level propagation or retraining was performed.

Verification commands:

```bash
uv run python -m pytest -q tests/test_paper1_software_extension.py
uvx ruff check experiments/exp10_residual_learnability \
  experiments/exp11_stronger_baselines \
  experiments/exp12_tail_aware_gate \
  experiments/exp13_multisat_generalization \
  tests/test_paper1_software_extension.py
```

The contract suite passed all six tests. Ruff passed; it emitted only the
repository's existing warning that top-level linter settings are deprecated.

## Key findings

1. Existing BK1 aggregate residual summaries are near zero mean, with p99
   absolute residual increasing from 1.658 Hz at 8 h to 191.260 Hz at 168 h;
   the reported 168 h maximum is 519.419 Hz. The p99 values are below the
   500 Hz tolerance, but the missing sequence prevents autocorrelation, sign,
   PSD, and learned-tail claims.
2. The existing model family remains unfavorable to learning: median bias,
   ridge, RF, GBR, and MLP all have higher reported BK1 test MAE than the zero
   residual SGP4 baseline at every listed staleness. Selected model identities
   are available, but this is a summary reparse, not a fresh retraining run.
3. The real MAE gate is closed in every reported row. The synthetic mechanism
   check closes in fresh/moderate cases and opens in the extreme systematic
   case. Real p95/p99, guard-cost, and outage gates remain unavailable.
4. The multi-satellite output is a `summary_only` BK1/BK2 dry-run, not a new
   generalization result.

## Claim impact

The current negative-result story is not contradicted and is modestly supported
against the "weak model" objection by the existing lightweight comparison. It is
not strengthened enough to add new paper claims: the campaign did not recover
raw sequences, perform fresh training, or evaluate tail-aware real decisions.

Every real result remains model-derived with `reference_is_measured_truth=false`.
Synthetic rows remain mechanism checks only. No measured Doppler, packet,
PER/PDR/CRC, gateway ACK, OTA, or live-satellite result is produced.

## Recommended next action

- **B. Keep as artifact:** retain these reports and figures as an auditable
  software-extension record; do not modify the current paper or slides.
- **C. Defer to Paper 1+:** restore raw TLE inputs, export pair-level predictions,
  and rerun the tail-aware and multi-satellite analyses before claiming broader
  generalization or tail safety.

The current paper and slide sources were not modified.
