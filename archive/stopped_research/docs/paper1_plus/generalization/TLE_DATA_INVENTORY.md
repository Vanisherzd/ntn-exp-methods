# TLE Data Inventory — Paper 1+ Generalization Campaign

Date: 2026-07-27
Scope: software-only. No hardware, RF, USRP, firmware, or over-the-air activity.
No external download was attempted. All figures below are read from committed
artifacts, not recomputed. Every residual referenced here is model-derived with
`reference_is_measured_truth = false`; there is no measured RF truth in this
inventory.

## Headline

**Only two satellites have ever been used by this repository's SGP4 residual
pipeline, both from the same BLACK KITE family, and neither raw archive is
present in the current workspace.** A multi-satellite generalization campaign
cannot be executed until raw TLE histories are restored, and even after
restoration two satellites is below the three-satellite threshold this campaign
requires before any generalization claim.

## 1. What is present in the workspace

| Path | Kind | Usable by the SGP4 residual pipeline? |
|---|---|---|
| `data/examples/sample_tle.txt` | single placeholder TLE, NORAD 99999, explicitly "NOT a real satellite" | **No** — one record, no history, no pairs can be formed |
| `data/manifests/tle_sources.yaml` | catalogue metadata, `example_source` placeholder | No — metadata only, `committed: false` |
| `data/schemas/tle_record.schema.json` | record schema | No — schema only |
| `docs/review/black_kite_1_target_specific_residual_experiment.md` | BK1 summary report | Summary only — aggregates, no per-sample residuals |
| `docs/review/black_kite_tle_history_residual_experiment.md` | BK1→BK2 transfer summary | Summary only |
| `docs/review/bk_negative_result_compact.csv` | compact result summary | Summary only |
| `experiments/exp10…exp13` outputs | derived summaries | Summary only |

## 2. What is absent

| Expected path | Status |
|---|---|
| `dataraw/spacetrack/black_kite_1_66741/gp_history_66741.json` | **absent** |
| `dataraw/spacetrack/black_kite_2_68474/gp_history_68474.json` | **absent** |
| `data_raw/tle/` (manifest's declared local root) | **absent** |

Both roots are git-ignored (`.gitignore:113` `data_raw/`, `.gitignore:127`
`dataraw/`), so this is expected repository hygiene, not data loss — the
archives are local-only and were not present in this workspace.

## 3. Satellites known to the pipeline (from committed reports)

| Satellite | NORAD | Records | Epoch start | Epoch end | Median inter-TLE gap | p90 | Max gap |
|---|---:|---:|---|---|---:|---:|---:|
| BLACK KITE-1 | 66741 | 415 | 2025-12-18 | 2026-06-12 | 6.3 h | 17.4 h | 493.7 h |
| BLACK KITE-2 | 68474 | 184 | 2026-04-13 | 2026-06-13 | 6.4 h | 16.1 h | 70.8 h |

Raw artifact sizes recorded in
`docs/review/black_kite_family_spacetrack_inventory.md`: BK1 58 930 B TLE /
468 458 B JSON; BK2 26 128 B TLE / 207 976 B JSON.

Both objects are BLACK KITE family, launched within months of each other, with
near-identical refresh cadence (~6.3 vs ~6.4 h median). They do **not** span
distinct orbit regimes, drag environments, or operator refresh policies, so even
a restored two-satellite run would test transfer between two similar objects
rather than generalization across orbital regimes.

Chronological overlap is also limited: BK2's history (2026-04-13 → 2026-06-13)
begins after 68 % of BK1's history has already elapsed, and BK1's own validation
segment starts 2026-04-03. Any cross-satellite matrix built from these two
objects is therefore constrained to a ~2-month common window.

## 4. Usability verdict for the exp14 runner

`experiments/exp14_multisat_generalization_matrix/run_multisat_generalization_matrix.py`
ingests either Space-Track GP JSON (`TLE_LINE1` / `TLE_LINE2` / `EPOCH`) or
three-line text, deriving mean elements from the TLE lines themselves so both
formats are on identical footing. Run against the current workspace it reports:

```
insufficient_data: no usable TLE history under .../dataraw/spacetrack;
wrote empty artifacts, no claim made.
```

`results.json` records `status: insufficient_data`, `dry_run: true`,
`raw_tle_inputs_available: false`, `satellites_found: 0`. No residual was
computed. No figure was emitted. No generalization claim is made.

## 5. Protocol discrepancies found while auditing the two existing experiments

These are the campaign's most substantive findings and are independent of data
restoration. The two real experiments behind Paper 1's Table I were run with
**different protocols**, which the paper describes as one.

| Aspect | BK1 target-specific (`tools/bk1_target_specific_residual_experiment.py`) | BK1→BK2 transfer (`tools/bk_tle_residual_experiment.py`) |
|---|---|---|
| Pair reject threshold | `MANEUVER_CAP_HZ = 1500.0` | `max_residual_hz = 150.0` |
| Feature vector | 10 features (incl. stale mean motion, B\*, eccentricity) | 7 features (no stale orbital elements) |
| Stale-partner pairing | older TLE in band **closest to target staleness** | every pair whose gap falls in the window |
| Split | chronological 60/20/20 within BK1 | BK1 entirely train, BK2 entirely test |
| Target-side validation window | yes (132 records) | **none** |
| Reported model selection | best **validation** MAE among learned models | `min(ridge_mae, mlp_mae)` computed on **BK2 test** |

**Materiality.** For the three cross rows every candidate is worse than the zero
baseline on test (8 h: base 0.1877 vs ridge 0.3738 / MLP 0.3261; 24 h: 0.4969 vs
2.5413 / 1.8639; 48 h: 2.4092 vs 2.8458 / 2.9593). The minimum over candidates
is worse than the baseline in every row, so the reported gate decision (closed)
is invariant to the selection rule and no reported decision is inflated. The
defect is in how the protocol is *described*, not in the result. See
`CURRENT_PAPER_INTEGRATION_DECISION.md`.

## 6. Reject-rule evidence recovered

`docs/review/black_kite_1_target_specific_residual_experiment.md` preserves the
magnitudes of the BK1 pairs removed by the 1500 Hz screen:

| Staleness | Removed pairs | Largest removed max\|residual\| [Hz] |
|---:|---:|---|
| 8 h | 0 | — |
| 24 h | 6 | 2326, 2194, 2194, 2072, 2072 |
| 48 h | 5 | 14457, 3028, 2208, 1549, 1549 |
| 72 h | 11 | 26210, 11386, 8388, 8388, 6855 |
| 96 h | 13 | 14755, 14078, 14078, 12500, 6890 |
| 168 h | 19 | 30574, 28081, 22768, 19454, 19263 |

Removed pairs sit 1.4×–20× above the threshold, consistent with manoeuvre or
bad orbit-determination epochs rather than borderline drift. This *partially*
answers the "the screen removes the learnable part" objection — the removed
population is not a marginal tail — but it does not close it, because the
residual energy carried by those pairs and their learnability were never
evaluated. The exp14 runner emits `reject_sensitivity_summary.csv` for exactly
this purpose once raw data is restored.

## 7. What is needed before a generalization campaign can run

1. Restore `dataraw/spacetrack/` (BK1, BK2) through the approved local path.
2. Obtain **at least one additional satellite outside the BLACK KITE family**,
   ideally spanning a different altitude/drag regime and a different operator
   refresh cadence, to reach the three-satellite threshold.
3. Rerun both existing experiments under a **single** protocol (one reject
   threshold, one feature set, one pairing rule, target-side validation for
   every cell) so the matrix is internally comparable.
4. Export pair-level predictions and pair identifiers so tail-aware gates and
   pair-clustered statistics become computable.

Until step 2 is satisfied, this campaign remains explicitly a dry run.
