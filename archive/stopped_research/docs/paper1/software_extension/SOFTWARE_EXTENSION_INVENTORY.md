# Paper 1 Software Extension Inventory

## Existing pipeline

The real BLACK KITE pipeline is implemented in:

- `tools/bk1_target_specific_residual_experiment.py`: BK1 target-specific chronological 60/20/20 split, 24 samples per accepted pair, 8/24/48/72/96/168 h windows, zero/median/ridge/RF/GBR/MLP comparison, and MAE/RMSE gate decision.
- `tools/bk_tle_residual_experiment.py`: BK1-to-BK2 transfer experiment for 8/24/48 h windows.
- `tools/evidence_gate_stress_experiment.py`: controlled synthetic gate mechanism check.
- `docs/review/black_kite_1_target_specific_residual_experiment.md`: current BK1 summary, selected model identities, test distributions, counts, and reject counts.
- `docs/review/black_kite_tle_history_residual_experiment.md`: BK1-to-BK2 transfer summary.
- `docs/review/bk_negative_result_compact.csv`: compact real-result summary used by the paper figures.
- `docs/review/gate_stress_compact.csv`: compact synthetic mechanism summary.

Raw TLE inputs are expected at
`dataraw/spacetrack/black_kite_1_66741/gp_history_66741.json` and
`dataraw/spacetrack/black_kite_2_68474/gp_history_68474.json`. Those files are
absent from the current workspace. No external download was attempted.

## Regeneration commands

With the local raw TLE archive restored:

```bash
uv run python tools/bk1_target_specific_residual_experiment.py
uv run python tools/bk_tle_residual_experiment.py
uv run python tools/evidence_gate_stress_experiment.py
```

Summary/table and figure regeneration commands are:

```bash
uv run python experiments/summary_table.py
uv run python paper/figures/generate_evidence_gate_figures.py
uv run python paper/figures_final/generate_paper_final_figures.py
```

The first two real experiment commands are currently blocked by the missing
local `dataraw/` inputs. The summary and figure commands consume committed
summary/proxy artifacts and do not recreate sample-level residuals.

## Availability matrix

| Evidence | Available now | Notes |
|---|---:|---|
| BK1 test MAE at six ages | yes | 0.2430 to 26.9243 Hz baseline; selected learned model remains worse |
| BK1 n(tr/va/te) | yes | 2712/2520/1968 through 2448/3168/2640 |
| BK1 reject counts | yes | 0, 6, 5, 11, 13, 19 |
| BK1 selected model identity | yes | MLP at 8/24/48 h; ridge at 72/96/168 h |
| BK1 sample residual sequence | no | report contains aggregates only |
| BK1 train/validation distributions | no | only held-out distribution is reported |
| BK1-to-BK2 per-split counts | no | compact summary has MAE only |
| BK1-to-BK2 selected model identity | yes | MLP, MLP, ridge at 8/24/48 h |

The 24 in-pass samples per accepted TLE pair are temporally correlated and are
reproducibility counts, not independent statistical trials.
