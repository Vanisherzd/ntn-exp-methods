# Paper 1 Final Hygiene Report

Date: 2026-07-11

## Source/PDF Consistency

Checked `paper/icc_main.tex` and rebuilt `paper/icc_main.pdf`.

- Section V is `Preliminary Conducted-IQ Evidence`.
- Table IV is `Conducted-IQ sanity check summary`.
- The conclusion includes the cross-satellite generalization limitation sentence:
  cross-satellite generalization remains the main limitation and evaluating the
  gate as a constellation-scale safeguard is future work.
- Main paper keeps Table IV as the conducted-IQ sanity summary.
- The conducted-IQ spectrum figure is not reintroduced into the main paper.

Build:

- Command: `tectonic paper/icc_main.tex`
- Result: success.
- Paper page count: 6 pages including references.
- Undefined refs/citations: none found in `paper/icc_main.log`.
- Overfull boxes: none found in `paper/icc_main.log`.
- Remaining warnings: existing underfull boxes and package/PDF object warnings.

## Cross-Reference Check

Rendered-text/source checks confirm:

- `Sec. IV-D` resolves to Sensitivity.
- `Sec. IV-E` resolves to Endpoint-Control Proxies.
- `Sec. V` resolves to Preliminary Conducted-IQ Evidence.
- `Table IV` is referenced from the conducted-IQ section and renders as the
  conducted-IQ sanity summary.
- No active `Fig. 4` reference remains in the main paper.
- No active `fig:hw`, `fig_conducted_iq_evidence`, or `fig_hw` reference remains
  in `paper/icc_main.tex`.

## Fig. 1 Bug Check

Inspected the Fig. 1 TikZ source and rendered page 3 of the paper.

- Removed the `$G$` node label from the green Evidence Gate -> selector arrow.
- Kept the same figure structure; no redesign.
- Rendered Fig. 1 now shows a clean green control arrow without overlapping text.

## MAE Notation Check

Searched for `MAEphys`, `MAEml`, `MAE_phys`, and `MAE_ml`.

- No flat MAE notation remains in `paper/icc_main.tex`.
- Equations use `\mathrm{MAE}_{\mathrm{phys}}` and
  `\mathrm{MAE}_{\mathrm{ml}}`.
- No layout-impacting notation edit was needed beyond verification.

## Slides Check

Rebuilt `paper/slides_overview.tex`.

- Command: `tectonic paper/slides_overview.tex`
- Result: success.
- Slide count: 13.
- Includes `Main Limitation: Cross-Satellite Generalization`.
- The limitation slide frames the cross-satellite campaign as future work, not
  completed work.
- Slide 11 keeps conducted-IQ spectrum as advisor discussion/supporting trace
  only and keeps the no packet/PER/PDR/CRC/gateway ACK/OTA/live-satellite or
  link-layer validation boundary.

Remaining slide warnings are minor Beamer overfull/underfull boxes and existing
included-PDF version warnings.

## Remaining Blockers

- Submission author block / venue anonymity policy remains unresolved.
- Optional reference `[7]` metadata verification remains optional.
- Cross-satellite generalization remains future work.
- Existing uncommitted advisor-slide/generalization changes and unrelated
  coauthor-review files remain in the working tree.
- No commit was made.
