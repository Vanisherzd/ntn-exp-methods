# Submission checklist

## Paper
- [x] `paper/icc_main.tex` is the sole active entry point
- [x] `paper/icc_main.pdf` builds from a clean checkout via `make -C paper`
- [x] six pages
- [x] zero LaTeX errors, zero undefined references, zero undefined citations
- [x] zero overfull boxes
- [x] banlist clean (6 source files, 11 patterns)
- [x] three figures and one table, all generated from `\input` sources
- [x] anonymous author block, no acknowledgements
- [x] every headline number traced to an artifact in `CLAIMS.md`
- [ ] six adversarial reviewers completed and converged
- [ ] final human approval before the submission tag

## Repository
- [x] active code under `src/`, tests under `tests/`, evaluation under `evaluation/`
- [x] stopped work confined to `archive/`, unread by build or tests
- [x] no duplicate active manuscript
- [x] retired manuscript preserved, including the committed variant absent from the
      original freeze snapshot
- [x] regenerable LaTeX and Python products gitignored
- [x] branch inventory documented and obsolete branches removed
- [x] remote verified after push

## Anonymity — the repository rename is NOT anonymisation

The repository is named `ntn-exp-methods` rather than for the paper or the stopped programme. That
is hygiene, not blinding, and the distinction matters before submission:

- [x] repository name carries no paper title and no stopped-programme term
- [ ] **if the target venue is double-blind, do NOT link this repository.** It sits under a personal
      GitHub account and is public, so the account name deanonymises the authors regardless of what
      the repository is called, and its commit history carries author identity and dates.
- [ ] for a double-blind venue, prepare an **anonymous artifact mirror** (or the venue's approved
      anonymised-artifact mechanism) and cite that instead
- [ ] confirm the manuscript's availability paragraph points at the anonymous mechanism, not at the
      personal repository

Repository visibility was deliberately left unchanged during the rename; changing it is a
submission decision, not a cleanup one.
