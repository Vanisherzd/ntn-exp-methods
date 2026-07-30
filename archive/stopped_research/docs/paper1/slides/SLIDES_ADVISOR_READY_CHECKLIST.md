# Slides Advisor-Ready Checklist

## Build

- [x] `paper/slides_overview.tex` builds.
- [x] `paper/slide_figures/fig_conducted_iq_setup.tex` builds.
- [x] Deck has 14 slides.
- [x] No undefined references/citations.
- [x] No overfull boxes.

## Visual QA

- [x] Contact sheet rendered at `tmp/pdfs/slides_advisor_ready/contact_sheet.png`.
- [x] NTHU logo is visible.
- [x] Main result table is readable.
- [x] Policy and synthetic mechanism tables are readable.
- [x] Main takeaway appears before all backup material.
- [x] Slides 12-14 are explicitly marked as backup slides.
- [x] Current manual-QA evidence is refreshed in `.omo/evidence/deck_visual_review/`.

## Claim Boundary

- [x] Real evidence remains model-derived inter-TLE residual evidence.
- [x] Synthetic result is mechanism-check only.
- [x] Endpoint proxy material is backup-scoped and software-only.
- [x] Conducted-IQ is backup artifact sanity only.
- [x] No LR1131/CFO/hop-center terminology remains.
- [x] No positive packet/PER/PDR/CRC/gateway ACK/OTA/live-satellite validation claim.
- [x] No conducted-IQ main-paper contribution claim.

## Tests And Scans

- [x] `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q tests/test_slides_claims.py` passes: 5 tests.
- [x] `uvx ruff check tests/test_slides_claims.py` passes, with only a project-level deprecation warning.
- [x] No tracked raw IQ artifacts found by `git ls-files '*.cf32' '*.fc32' '*.npy'`.
- [x] Build logs contain no undefined refs/citations, overfull boxes, LaTeX/package errors, emergency stop, or fatal errors.

## Paper Consistency

- [x] No paper edit was needed for slide consistency.
- [x] Existing dirty `paper/icc_main.tex` edits were preserved and not staged.

## Current Recommendation

Ready for final independent gate rerun. If that rerun reports zero blockers, the slide package is advisor-ready.
