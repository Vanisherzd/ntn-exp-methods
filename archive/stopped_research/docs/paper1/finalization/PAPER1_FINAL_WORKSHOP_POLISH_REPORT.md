# Paper 1 Final Workshop Polish Report

## Contribution reorder summary

Reordered the contribution bullets in `paper/icc_main.tex` to match the
negative-result framing:

1. Real-data negative finding on BLACK KITE: learned inter-TLE residuals never
   beat SGP4 at tested staleness, always-learn is unsafe, and the gate closes.
2. Evidence-gated deploy/no-deploy rule: chronological validation rejects
   unsupported learning on real data and opens only under controlled systematic
   synthetic evidence.
3. Endpoint-budget software proxy: Eqs. (10)--(13) connect timing/frequency
   uncertainty to guard and energy proxies; software-only, not packet/link
   validation.

No numerical results were changed.

## Table I n clarification

Added the Table I caption clarification:

`n` counts 24 in-pass samples per accepted TLE pair, and those samples are
temporally correlated.

This reports the saved sample accounting for reproducibility without treating
in-pass samples as independent statistical trials.

## P1a report relocation

Moved the P1a NUCLEO footprint reports into `docs/paper1/finalization/`:

- `docs/paper1/finalization/PAPER1_P1A_NUCLEO_FOOTPRINT_PLAN.md`
- `docs/paper1/finalization/PAPER1_P1A_FOOTPRINT_COMPILE_REPORT.md`

The firmware patch directory remains at
`firmware_patches/nucleo_footprint_benchmark/`.

P1a results were not added to the main paper.

## Build status

- `tectonic --keep-logs paper/icc_main.tex`: passed.
- `tectonic --keep-logs paper/slides_overview.tex`: passed.
- Paper page count: 6 pages.
- Slide count: 14 pages.
- Undefined references/citations: none found in the final log scan.
- Overfull boxes: none found in the final paper/slide log scan.

## Claim-boundary scan

- No conducted-IQ text in the main paper.
- No MCU latency/energy estimate in the main paper.
- No `90%` or `90.4%` main-paper claim found.
- Remaining packet/PER/PDR/OTA/live-satellite terms are limitations,
  future-work, related-work, or non-claim contexts.

## Remaining blockers

- Submission metadata / author-anonymity policy remains external.
- Cross-transfer per-split counts were not present in the compact saved artifact,
  so Table I keeps those rows as `--`.
- NUCLEO measured latency is still not claimed in the main paper.

