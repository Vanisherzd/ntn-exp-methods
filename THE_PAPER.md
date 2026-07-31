# Where is the paper?

**Source:** `paper/icc_main.tex`
**PDF:** `paper/icc_main.pdf`
**Build it:** `make paper` (from the repository root)
**Verify it:** `make gate`

That is the only manuscript under active work. Everything else that looks like a paper is
listed below with the reason it is not.

Current state: *Orbit-Evidence: Relational Validity Checks for Learning-Assisted Satellite
Communication Experiments*, 6 pages, on branch `submission/orbit-evidence-workshop`.

## How to tell at a glance whether a PDF is the current one

| check | the current paper says |
|---|---|
| title | "Orbit-Evidence: Relational Validity Checks…" |
| L4.7 false-halt rate | **14/450 = 0.031**, Wilson [0.018, 0.052] |

Any PDF titled "Beyond Chronological Splits…" or quoting **0.042** / **19/450** is superseded.
Those numbers were measured before the permutation stream was rederived, and the gate could not
catch the drift because the calibration was transcribed rather than read — see
`submission_finalization/REVIEW_LEDGER.md`.

## Every other `icc_main.*` in this repository

| path | what it is | tracked? | may I submit it? |
|---|---|---|---|
| `paper/icc_main.tex` | **the manuscript** | yes | — this is the source |
| `paper/icc_main.pdf` | **the submission PDF**, copied out of `paper/build/` by `make paper` | no (gitignored, regenerable) | **yes** |
| `paper/build/icc_main.pdf` | the latexmk build target; byte-identical to the above | no (gitignored) | same file, prefer the one above |
| `submission_finalization/baseline/icc_main.{tex,pdf}` | frozen rollback point from before this revision cycle. Old title, stale 0.042 | **yes**, deliberately | no — it exists so the cycle can be reverted |
| `archive/retired_manuscript/snapshot/paper/icc_main.tex` | the retired Doppler/residual-learning manuscript | yes | no — that research line is stopped |
| `archive/retired_manuscript/paper_tree_committed/` | the retired manuscript's full tree, including its slides and result tables | yes | no — same stopped line |
| `local_archive/stale_builds/` | build products whose filenames looked like the submission | no | no — see its README |
| `local_archive/build_artifacts/` | ~20 dated PDFs from June 2026, kept for provenance | no | no |
| `advisor_package/` | an advisor review draft from an earlier phase | no | no |

## Directory map for the parts that matter to the paper

```
paper/
  icc_main.tex            the manuscript — the only .tex you edit
  refs.bib                bibliography
  figures/                Fig. 1 contract, Fig. 2 operating curve, Fig. 3 case studies
                          (fig_coverage_matrix_ARCHIVED.tex is the replaced Fig. 2, kept not deleted)
  tables/                 Table I
  scripts/                check_banlist.py, verify_build.py, check_glyphs.py
  submission/             CLAIMS.md, ARTIFACTS.md, README.md — the reviewer-facing docs
  build/                  latexmk scratch (gitignored)

evaluation/
  scripts/                contract_layers.py (the 19 rules), calibrate_l47.py, run_matrix.py
  results/                final_summary.json — every number the paper quotes comes from here

submission_finalization/  review ledger, cycle returns, the frozen baseline
archive/                  stopped research lines and the retired manuscript (never deleted)
```

## The rule that makes the numbers trustworthy

Every headline number in the manuscript is written `\artv{key}{value}`. `make gate` parses those
sites and refuses to build if a value disagrees with `evaluation/results/final_summary.json`, if a
number has no claiming sentence, or if a retracted claim reappears. So if `make gate` passes, the
PDF and the artifact agree by construction — you do not have to check by hand.
