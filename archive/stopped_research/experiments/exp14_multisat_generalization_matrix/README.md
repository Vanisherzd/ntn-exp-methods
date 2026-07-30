# exp14 — Multi-satellite inter-TLE residual generalization matrix (Paper 1+)

Software-only. Model-derived inter-TLE residuals, `reference_is_measured_truth =
false`. No hardware, RF, USRP, firmware, or OTA. No packet, error-rate,
receiver-acknowledgement, over-the-air, or on-orbit result is produced.

## What it does

Builds a `train_source x deploy_target x staleness` matrix and applies the
Evidence Gate to every cell, following the corrected Paper 1 protocol:

- **train** fits the candidate correctors
- **validation** selects the candidate *and* decides `G` (Eq. 6)
- **test** only reports the consequence of the already-fixed decision

For a cross-satellite cell the corrector is fitted on the **source** train
segment but selected and gated on the **target** validation segment. That is the
deployable semantics — a terminal can only validate against the satellite it is
about to serve — and it is stricter than the original BK1→BK2 experiment, which
had no target-side validation window.

## Models

Lightweight only, no heavy training:

- references (never eligible to open the gate): `zero` (SGP4), `mean_bias`,
  `median_bias`
- learned candidates (gated): `linear_bias_rate`, `ridge`

Random forest / gradient boosting / MLP from `tools/` are **excluded**: scikit-
learn and torch are not installed in this environment, and the campaign brief
restricts it to lightweight baselines.

## Run

```bash
uv run experiments/exp14_multisat_generalization_matrix/run_multisat_generalization_matrix.py \
  --tle-dir dataraw/spacetrack
```

Useful flags: `--gs-lat/--gs-lon/--gs-alt`, `--carrier-hz`, `--staleness`,
`--reject-hz`, `--reject-sweep`, `--gamma`, `--min-satellites`, `--out-dir`.

Accepts Space-Track GP JSON (`TLE_LINE1`/`TLE_LINE2`/`EPOCH`) or three-line
text. Mean elements are derived from the TLE lines via `Satrec`, so both formats
are treated identically.

## Outputs

| File | Contents |
|---|---|
| `results.json` | metadata, satellite inventory, all rows |
| `multisat_generalization_matrix.csv` | one row per source × target × staleness |
| `per_satellite_summary.csv` | records, cadence, epoch span, gate tallies |
| `reject_sensitivity_summary.csv` | acceptance and residual scale vs reject threshold |

## Current state

The workspace has **no** raw TLE archive (`dataraw/`, `data_raw/` are git-ignored
and absent), so the committed artifacts are the `insufficient_data` dry run:
`satellites_found: 0`, `dry_run: true`, empty CSVs, no figure, no claim.

Figures (`fig_generalization_gate_matrix`,
`fig_generalization_degradation_matrix`, `fig_reject_rate_by_satellite`) are
emitted only once `--min-satellites` (default 3) satellites with usable history
are present. Two BLACK KITE objects alone do not qualify.

See `docs/paper1_plus/generalization/` for the inventory, the stress-test report,
and the current-paper integration decision.
