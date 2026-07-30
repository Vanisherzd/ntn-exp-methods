# Slides Review Loop Report

Status: current local build, tests, scans, and visual QA pass. Final independent gate rerun is still pending.

## Scope

- Rebuilt `paper/slides_overview.tex` using the existing Beamer slide base and tracked `paper/nthu_logo.png`.
- Kept the paper claim boundary: real evidence is model-derived inter-TLE residual evidence; synthetic evidence is mechanism-check only; conducted-IQ is backup artifact sanity only.
- Did not run experiments, transmit RF, touch hardware, change paper numerical results, or edit `paper/icc_main.tex` for slide consistency.

## Main Changes

- Added NTHU logo use on the title slide, frame title, and footline.
- Reframed the deck around the real BLACK KITE negative finding.
- Replaced small result plots with readable tables for the real result, policy comparison, and synthetic mechanism check.
- Moved endpoint proxy, proxy ablation, and conducted-IQ content after the main takeaway as explicit backup slides.
- Corrected conducted-IQ figure terminology from LR1131/CFO/hop-center wording to LR1121/frequency-proxy wording.
- Removed unused local icon macros from `paper/slides_overview.tex`.
- Replaced weak claim scanners with focused PDF/source tests for narrative order, boundary language, forbidden terms, LR1121 consistency, and conducted-IQ backup scoping.

## Review Loop

- Round 1 found visual crowding, duplicate backup slide, LR1121/LR1131 mismatch, CFO/hop-center wording, weak claim tests, and backup material interrupting the close.
- Round 1 fixes removed the duplicate backup, enlarged/readjusted tables, fixed LR1121 terminology, removed CFO/hop-center wording, and scoped conducted-IQ as artifact-only.
- Round 2 found remaining blockers: synthetic/proxy material still too prominent, endpoint proxy still before the main takeaway, stale manual-QA evidence, weak tests, ruff failures, and unused macros.
- Round 2 fixes moved endpoint proxy/proxy ablation/conducted-IQ to backup slides 12-14, removed unused macros, refreshed visual QA evidence, and made tests outcome-oriented.

## Current Verification

- `tectonic --keep-logs paper/slides_overview.tex`: PASS; underfull hbox warnings only.
- `tectonic --keep-logs paper/slide_figures/fig_conducted_iq_setup.tex`: PASS.
- `pdfinfo paper/slides_overview.pdf`: 14 pages.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q tests/test_slides_claims.py`: PASS, 5 tests.
- `uvx ruff check tests/test_slides_claims.py`: PASS, with a project-level deprecation warning about top-level ruff settings.
- Log scan: no undefined references/citations, overfull boxes, LaTeX/package errors, emergency stop, or fatal errors.
- Claim scan: no LR1131, CFO, hop-center, positive hardware/RF validation, packet success, gateway ACK evidence, OTA evidence, live-satellite evidence, or measured Doppler truth.
- Raw artifact tracking check: `git ls-files '*.cf32' '*.fc32' '*.npy'` returned no tracked raw IQ artifacts.

## Final Slide Order

1. Title / real TLE-history negative finding
2. Endpoint control problem
3. Always-learn residual risk
4. Falsification-oriented deployment framing
5. Evidence gate rule
6. Real negative finding
7. Policy comparison
8. Synthetic mechanism check only
9. Limitations
10. Next software campaign
11. Takeaway
12. Backup: endpoint proxy scope
13. Backup: proxy ablation scope
14. Backup: artifact sanity only

## Remaining Risks

- Backup plot axis labels remain small at projection distance.
- Underfull hbox warnings remain but do not create overfull or blocking visual defects.
- `paper/icc_main.tex` has unrelated pre-existing dirty edits; this slide pass preserved them.
