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

---

# Group 5 — stopped-research consolidation (2026-07-31)

743 tracked files at this point. Scratch directories (`tmp/`, `build/`, `outputs/`,
`local_archive/`, `hardware/`, `dataraw/`, `logs/`, `validation_runs/`) hold **no tracked
files** — already ignored, no action needed.

Every move uses `git mv`. **No file is deleted.** Nothing already under `archive/` is
touched. Committed separately from all prose and evidence changes.

## Stays in place — the active submission

| path | tracked | role |
|---|---|---|
| `paper/` | 14 | manuscript, figures, tables, submission docs, Makefile, scripts |
| `src/orbit_evidence/` | 10 | the toolkit |
| `tests/{regression,fault_injection,fixtures}/` | 10 | tests and the two pipelines |
| `evaluation/{scripts,results,mutations}/` | 12 | contract rules, artifacts, pre-registration |
| `submission_finalization/` | 12 | this finalization's records |
| `archive/` | 167 | already archival — untouched |
| `docs/{CASE_STUDIES,DEVELOPMENT,FAILURE_TAXONOMY,FUTURE_MEASUREMENT_PROTOCOL,REPRODUCIBILITY}.md` | 5 | active documentation |
| `README.md`, `Makefile`, `pyproject.toml`, `uv.lock`, `.gitignore` | 5 | root |
| `scripts/compare_summaries.py`, `scripts/__init__.py` | 2 | used by `make gate-twice` |

## Moves into `archive/`

Stopped research is preserved, not deleted, and kept out of the active tree so a reader
cannot mistake it for current evidence.

| from | to | tracked |
|---|---|---|
| `experiments/` | `archive/stopped_research/experiments/` | 165 |
| `hardware_conducted_iq/` | `archive/hardware_validation/conducted_iq/` | 157 |
| `docs/paper1/` | `archive/stopped_research/docs/paper1/` | 71 |
| `docs/paper1_plus/` | `archive/stopped_research/docs/paper1_plus/` | 18 |
| `docs/review/` | `archive/stopped_research/docs/review/` | 17 |
| `docs/thesis_extension/` | `archive/stopped_research/docs/thesis_extension/` | 1 |
| `docs/TLE_AGING_METHODOLOGY.md`, `docs/uncertainty_*`, `docs/risk_aware_control_stage4_results.txt` | `archive/stopped_research/docs/` | 6 |
| 17 root legacy reports (`BOARD_*`, `FIRMWARE_*`, `HARDWARE_*`, `PAPER1_*`, `PAPER_HARDWARE_*`, `CONDUCTED_IQ_*`, `DETERMINISTIC_LR1121_TX_PLAN.md`, `READONLY_FLASH_TOOLING_PLAN.md`, `RECOVERED_FIRMWARE_CANDIDATES.md`, `VALIDATION_STATUS_FOR_SLIDES.md`, `COMMIT_PLAN.md`) | `archive/stopped_research/reports/` | 17 |
| `scripts/` (16 remaining: conducted-IQ analysis, uncertainty calibration, USRP capture, pretrain/validate) | `archive/stopped_research/scripts/` | 16 |
| `tools/` | `archive/stopped_research/tools/` | 5 |
| `data/`, `configs/`, `controller/`, `physics_ml/`, `models/` | `archive/stopped_research/` | 28 |
| `firmware_patches/`, `recovered_firmware_candidates/` | `archive/hardware_validation/` | 12 |

Total moved: **~513** tracked files. Total deleted: **0**.

## Verification after each move group

Rule 10 requires build and tests to pass after *each* structural move. After every group:

```
make gate     # tests, matrix, claim gate, six-page paper build
```

The predictable breakage is an import path or a doc cross-reference. A previous restructure
broke toolkit imports and was caught exactly this way.

## Deliberate gaps — not created

**`evaluation/configs/`** is not created. The three deterministic environments are defined
in `tests/fixtures/pipelines.py` (`ENVS`) and contract thresholds are rule arguments; there
is no separate config file. An empty directory would be decoration.

**`paper/sections/`** is not created. The manuscript is a single `icc_main.tex` with figures
and tables as `\input` files.

**`LICENSE`** is absent and is **not** added. Choosing a licence is the author's decision,
not a finalization step; inventing one would be a substantive act disguised as cleanup.
Flagged in the final dossier as an open submission item.

## Duplicate manuscripts and temporary PDFs

None in the active tree. `paper/icc_main.tex` is the sole manuscript source; no `main.tex`,
`main.pdf`, `main(N).pdf` or `icc_main(N).pdf` variant exists. Both retired manuscripts stay
under `archive/retired_manuscript/{snapshot,paper_tree_committed}`. `paper/build/` is
gitignored.
