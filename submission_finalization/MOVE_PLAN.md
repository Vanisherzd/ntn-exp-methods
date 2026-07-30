# MOVE PLAN

Every move below uses `git mv` where the source is tracked. Build and tests are
re-run after each structural group, not only at the end.

## Group 1 — active paper

| from | to | note |
|---|---|---|
| `submission_recovery/manuscript/main.tex` | `paper/icc_main.tex` | sole entry point |
| `submission_recovery/manuscript/refs.bib` | `paper/refs.bib` | |
| `submission_recovery/manuscript/check_banlist.py` | `paper/scripts/check_banlist.py` | build gate |
| (extract from `main.tex`) | `paper/figures/fig_contract.tex` | inline TikZ split out |
| (extract from `main.tex`) | `paper/figures/fig_fault_matrix.tex` | |
| (extract from `main.tex`) | `paper/figures/fig_case_studies.tex` | |
| (extract from `main.tex`) | `paper/tables/contract_rules.tex` | |
| new | `paper/Makefile`, `paper/.latexmkrc` | canonical build |
| new | `paper/submission/{README,CLAIMS,ARTIFACTS,CHECKLIST}.md` | packaging |

Figures are inline TikZ, so `paper/figures/` would otherwise not exist. Splitting them
into `\input` files satisfies the target layout without creating an empty directory, and
makes each figure independently editable.

## Group 2 — toolkit to src

| from | to |
|---|---|
| `salvage/orbit-evidence-toolkit/scheduler/` | `src/orbit_evidence/pass_scheduler/` |
| `salvage/orbit-evidence-toolkit/registry/` | `src/orbit_evidence/causal_registry/` |
| `salvage/orbit-evidence-toolkit/ensemble/` | `src/orbit_evidence/label_ensemble/` |
| `salvage/orbit-evidence-toolkit/contract/` | `src/orbit_evidence/experiment_contract/` |
| `salvage/orbit-evidence-toolkit/README.md` | `src/orbit_evidence/README.md` |

## Group 3 — tests

| from | to |
|---|---|
| `salvage/orbit-evidence-toolkit/tests/test_regressions.py` | `tests/regression/test_regressions.py` |
| new | `tests/fault_injection/test_matrix.py` (asserts the matrix reproduces) |
| `submission_recovery/evaluation/pipelines.py` | `tests/fixtures/pipelines.py` |

## Group 4 — evaluation

| from | to |
|---|---|
| `submission_recovery/evaluation/contract_layers.py` | `evaluation/scripts/contract_layers.py` |
| `submission_recovery/evaluation/run_matrix.py` | `evaluation/scripts/run_matrix.py` |
| `submission_recovery/evaluation/MATRIX_RESULT.json` | `evaluation/results/matrix_result.json` |
| `submission_recovery/evaluation/MATRIX_RESULT_prefix_fixture_bug.json` | `evaluation/results/matrix_result_prefix_fixture.json` |
| `submission_recovery/evaluation/PREREGISTRATION.md` | `evaluation/mutations/PREREGISTRATION.md` |
| `submission_recovery/evaluation/EVALUATION_RESULT.md` | `evaluation/results/EVALUATION_RESULT.md` |
| new | `evaluation/README.md` |

## Group 5 — docs and ledgers

| from | to |
|---|---|
| `submission_recovery/CLAIM_LEDGER.md` | `submission_finalization/CLAIM_LEDGER.md` |
| `submission_recovery/evaluation/CASE_STUDIES.md` | `docs/CASE_STUDIES.md` |
| `submission_recovery/{ASSET_MANIFEST,INVALID_RESULT_BANLIST,OPEN_FINDINGS,STATE}.*` | `submission_finalization/` |
| new | `docs/REPRODUCIBILITY.md`, `docs/DEVELOPMENT.md` |

`docs/FAILURE_TAXONOMY.md` and `docs/FUTURE_MEASUREMENT_PROTOCOL.md` are already in place.

## Group 6 — deletions (see DELETE_PLAN.md)

Only the two byte-identical macOS duplicates, plus regenerable LaTeX intermediates.
`submission_recovery/` is emptied by the moves above and then removed.

## Preserved untouched

`archive/real_tle_causality_audit/`, `archive/retired_manuscript/`,
`archive/KNOWN_INVALID_RESULTS.md`. Brought onto this branch so a single checkout is
self-describing and the links in `KNOWN_INVALID_RESULTS.md` resolve. Not modified.
