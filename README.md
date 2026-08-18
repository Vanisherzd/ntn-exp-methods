# Orbit-Evidence

A chronological train/validation/test split constrains the **ordering of rows inside one realised
dataset**. Some deployment-validity assumptions are not in that dataset at all: they can only be
falsified by comparing another execution, another source state, or another physical aggregation
level. Orbit-Evidence makes those assumptions executable, falsifiable, and able to refuse.

## Paper

*Orbit-Evidence: Relational Validity Checks for Learning-Assisted Satellite Communication
Experiments*

| | |
|---|---|
| Source | `paper/icc_main.tex` |
| Bibliography | `paper/refs.bib` |
| Canonical tag | `paper/orbit-evidence-workshop-submission-ready-2026-08` |
| Build | `make paper` |

## Artifact

Frozen evidence lives in `evaluation/results/` and `evaluation/real_data/`. Every headline number
in the manuscript is bound to a field of `evaluation/results/final_summary.json` at a named claim
site, and the build fails if one disagrees.

| | |
|---|---|
| Canonical tag | `artifact/orbit-evidence-workshop-2026-08` |
| Verify | `make gate` |

## Talks

| | Path | Tag |
|---|---|---|
| Workshop | `talk/orbit_evidence_talk.tex` | `talk/orbit-evidence-reviewer-proof-2026-08` |
| Advisor review | `talk/advisor_review/advisor_deck.tex` | *untagged working deliverable* |

The advisor deck is **advisor-only**: its final slide requests supervision decisions and is not for
public presentation.

## Reproduce

```sh
make matrix                        # regenerate the fault matrix and the summary artifact
make gate                          # matrix -> test -> claims -> verify
make gate-twice                    # run the gate twice and compare the two summaries
make external-consequence-verify   # verify the committed third-party artifacts (no training)

make -C talk                       # workshop deck
make -C talk check

make -C talk/advisor_review        # advisor deck
make -C talk/advisor_review check
make -C talk/advisor_review render
```

`make gate` regenerates the fault matrix and the L4.7 calibration on every run. It does **not**
regenerate the two external evidence artifacts, because neither input ships with the repository —
the real-data application needs Space-Track records held locally and untracked, and the third-party
study needs a network clone at a frozen commit. Their artifacts are committed and the gate reads
them, refusing to build if a contract hash or a frozen commit differs from its pre-registration.
That is weaker than regeneration and is stated as such in `docs/REPRODUCIBILITY.md`.

## Repository status

This tree contains **only** the current Orbit-Evidence project: the manuscript, its frozen
evidence, the detector and contract implementation, the gates and tests, and the two current decks.

An earlier learning-assisted Doppler-control research line was stopped after
deployment-causality and falsifiability audits. Its results are withdrawn and are **not evidence
for this paper**. Its files are no longer in this checkout; they remain in Git history and in a
verified pre-cleanup bundle. See [docs/HISTORY.md](docs/HISTORY.md).

| Document | Purpose |
|---|---|
| [docs/REPO_MAP.md](docs/REPO_MAP.md) | what every path is, and what must not move |
| [docs/TAG_MAP.md](docs/TAG_MAP.md) | every retained tag and what it means |
| [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) | how to reproduce and what is not regenerable |
| [docs/HISTORY.md](docs/HISTORY.md) | research lineage, four paragraphs |
| [docs/CLEANUP_RECORD.md](docs/CLEANUP_RECORD.md) | what this cleanup removed, and how to recover it |
| [docs/CASE_STUDIES.md](docs/CASE_STUDIES.md) | the retrospective cases the artifact records |
