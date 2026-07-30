# Paper 1 Review-Driven Fix Report

Date: 2026-07-10

## Review Files Read

- `REVIEW_A_COMMUNICATIONS.md`
- `REVIEW_B_ORBIT_ML.md`
- `REVIEW_C_HARDWARE_EMBEDDED.md`
- `REVIEW_D_META_WORKSHOP.md`
- `PAPER1_REVIEW_MODE_SUMMARY.md`

## Must-Fix Items Applied

- Replaced placeholder author names/affiliations in `paper/icc_main.tex` with an
  anonymous author block:
  `Anonymous Authors / Affiliations omitted for double-blind review`.
- Updated `PAPER1_FINALIZATION_STATUS.md` so the remaining author issue is a
  venue-policy decision, not a final-PDF placeholder-author defect.
- Tightened the abstract so the `<1%` to `~90%` proxy-success statement is
  explicitly limited to the controlled synthetic gate-open regime.
- Added the packet/link/OTA boundary in the abstract by naming "no packet,
  link-layer, over-the-air, or live-satellite result."
- Added a concise `F_{\mathrm{tol}}=500` Hz justification: representative
  sub-kHz hop-bin/control proxy, not a standard receiver threshold.
- Added the MAE-gate rationale: MAE is stable on small chronological windows;
  tail/outage proxies are reported after gating and do not override the
  deploy/no-deploy decision.
- Tightened Fig. 3 caption and nearby endpoint-proxy text to say "controlled
  gate-open synthetic" and that the real gate stays closed.
- Softened MCU/PGRL footprint wording: inference-only estimate, mid-range
  MCU-class when Flash suffices, not ultra-minimal or M0-class nodes.
- Added hardware boundary text near Table IV: the 923.2 MHz local AS923 conducted
  run is separate from the 868 MHz software metrics and does not exercise Doppler
  correction, evidence gating, packet decode, or OTA behavior.
- Replaced "safe fallback" and "viable endpoint" wording in the conclusion with
  conservative/proxy-only language.

No numerical results, tables of evidence, references, hardware evidence scope, or
figure assets were changed.

## Issues Left For Rebuttal/Defense

- Gaussian/independence proxy assumptions are not packet-trace validation; defend
  as explicitly labeled coverage proxies.
- Synthetic systematic residual is a gate sanity/stress check, not evidence that
  the target BLACK KITE distribution contains learnable structure.
- Conducted-IQ evidence is intentionally thin measurement-path sanity evidence.
- Threshold sensitivity beyond the existing `\gamma`/window sensitivity was not
  added because it would add or change numerical evidence.
- Published metadata for reference `[7]` was not changed; arXiv entry retained.

## Build And Page Count

- Command run: `tectonic --keep-logs paper/icc_main.tex`
- Output PDF: `paper/icc_main.pdf`
- Page count: 6 pages including references (`pdfinfo`)
- Undefined refs/citations: none found in `paper/icc_main.log`
- Overfull boxes: none found in `paper/icc_main.log`
- Remaining warnings: underfull boxes, font-substitution warnings, and an
  `algorithm.sty` UTF-8 warning; no build failure.

## No-Overclaim Scan

Scanned `paper/icc_main.tex` and rendered PDF text for:

`17 dBm`, `RF validation`, `end-to-end`, `packet`, `PER`, `PDR`, `CRC`,
`gateway`, `ACK`, `OTA`, `live satellite`, `decoded`, `measured Doppler`,
`truth`, `reference_is_measured_truth`.

Classification:

- `RF validation`, `end-to-end`: no hits.
- `-17 dBm`: OK non-claim hardware setup/table value for configured conducted
  firmware.
- `packet`, `PER`, `PDR`, `CRC`, `gateway`, `ACK`, `OTA`, `decoded`: OK
  limitation, Table IV boundary, related work, or future work; no positive
  validation claim.
- `measured Doppler`, `truth`, `reference_is_measured_truth`: OK limitation or
  model-derived-reference disclosure.
- `live-satellite`: OK limitation/no-claim wording.

Result: no ambiguous positive claim found.

## Manual QA

Rendered all six PDF pages to PNG with `pdftoppm` and visually inspected them.
The anonymous block, captions, tables, Table IV boundary, conclusion, and
references render without overlap or unreadable layout defects. The paper remains
visually dense but within the 6-page workshop constraint.

## Remaining Blockers

- Confirm venue policy: keep anonymous block for double-blind submission or
  replace with real authors/affiliations for non-anonymous submission.
- Advisor should review the revised framing before submission.
- No commit was made, per instruction.

## Readiness

- Ready for advisor review: yes.
- Ready for submission: not until advisor/venue confirms author policy and final
  human submission metadata.
