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
- [ ] branch inventory documented and obsolete branches removed
- [ ] remote verified after push
