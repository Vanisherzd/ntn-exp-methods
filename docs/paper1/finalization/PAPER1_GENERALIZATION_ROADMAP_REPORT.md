# Paper 1 Generalization Roadmap Report

Date: 2026-07-11

## What Was Added

- Created `PAPER1_GENERALIZATION_EXTENSION_PLAN.md`.
- Added a cross-satellite generalization limitation and extension roadmap:
  - Experiment 10: cross-satellite transfer matrix.
  - Experiment 11: gate closure under domain shift.
  - Experiment 12: failure taxonomy.
- Added one advisor-deck slide before Contributions:
  "Main Limitation: Cross-Satellite Generalization".

## Paper Change

Changed `paper/icc_main.tex` with one sentence in Conclusion and Limitations:

"Cross-satellite generalization remains the main limitation; evaluating the gate
as a constellation-scale safeguard is future work."

No numerical results, tables, figures, claims of validation, or evidence scope
were changed.

## Slides Change

Changed `paper/slides_overview.tex` by adding a limitation slide near the end.
The slide states:

- Current real-data result is BLACK KITE only.
- This does not prove constellation-wide generalization.
- That limitation is why always-on ML is unsafe.
- The next software campaign should test the Evidence Gate as a cross-satellite
  safety mechanism.

## Build Status

- Ran `tectonic paper/icc_main.tex`: success.
- Ran `tectonic paper/slides_overview.tex`: success.
- Paper page count: 6 pages including references.
- Slide count: 13 slides.

Remaining warnings:

- Paper: existing underfull-box/package warnings; no undefined refs/citations or
  overfull boxes found in the paper log.
- Slides: minor Beamer overfull/underfull warnings and existing included-PDF
  version warnings. Rendered new slide and final paper page were visually checked.

## Claim-Boundary Check

- No new experiment, hardware, measured Doppler, packet, PER/PDR/CRC, gateway
  ACK, OTA, live-satellite, or link-layer validation claim was added.
- Generalization language is explicitly framed as a limitation and future
  software campaign.
- The Evidence Gate remains framed as local chronological deploy/no-deploy
  validation, not train-once-deploy-everywhere generalization.

## Remaining Blockers

- Submission metadata / author anonymity policy remains unresolved.
- Optional reference `[7]` metadata verification remains optional.
- Cross-satellite generalization is future work, not resolved in Paper 1.
- Existing uncommitted advisor-slide revision remains part of the working tree;
  no automatic commit was made.
