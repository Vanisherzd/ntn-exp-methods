# Paper 1 Camera-Ready Layout Polish Report

## Scope

Performed a camera-ready layout polish pass on `paper/icc_main.tex` and the
existing Fig. 2/Fig. 3 generator. No experiments, hardware actions, RF, OTA,
USRP capture, numerical-result changes, or scientific-claim changes were made.

## Author Block

- Replaced the single anonymous author line with three IEEEtran-compatible
  anonymous author placeholders.
- The rendered page 1 shows only:
  - Anonymous Author 1
  - Anonymous Author 2
  - Anonymous Author 3
  - affiliation/email omitted text
- No real names, real affiliations, emails, lab names, university names,
  acknowledgements, or identifying metadata were added.

## Fig. 2 / Fig. 3 Legend Fixes

- Regenerated `paper/figures_final/fig_gate_evidence.pdf` and
  `paper/figures_final/fig_endpoint_proxies.pdf` from committed data only.
- Fig. 2:
  - moved real-data series legend outside the upper panels as a shared legend;
  - moved synthetic-regime legend outside the lower panels;
  - moved real/synthetic tags into low-density whitespace;
  - kept the systematic baseline line visible in panel (d).
- Fig. 3:
  - moved timing/marker legend outside panels as a shared legend;
  - shortened TLE marker annotations and removed cluttering arrows;
  - increased bar-label headroom;
  - moved the PGRL* explanation into the caption.

No plotted data values were changed.

## Page 6 Content Additions

Added useful conclusion text only:

- practical takeaway for BLACK KITE-like TLE-only residuals;
- audit/reproducibility artifact sentence for CSVs, scripts, frozen
  tables/figures, and compile-only NUCLEO footprint artifact;
- next software campaign sentence for multi-satellite generalization and
  residual-learnability analysis.

The added text explicitly does not imply hardware or link validation.

## Build Status

- Command: `tectonic --keep-logs paper/icc_main.tex`
- Result: success.
- Page count: 6 pages including references.
- Undefined references/citations: none found.
- Overfull boxes: none found.
- Remaining log warnings: existing underfull boxes, font substitution warnings,
  duplicate PDF object warnings from reruns, and existing `algorithm.sty` UTF-8
  warning.

## Visual QA

Rendered and inspected:

- `tmp/pdfs/icc_main_camera_ready/page-1.png`
- `tmp/pdfs/icc_main_camera_ready/page-5.png`
- `tmp/pdfs/icc_main_camera_ready/page-6.png`

Result:

- Page 1: three anonymous placeholders render clearly.
- Page 5: Fig. 2/Fig. 3 legends and annotations no longer block curves, bars,
  markers, axes labels, or titles.
- Page 6: conclusion and references fit within page 6; page is reasonably
  filled with useful content.

Independent read-only visual QA:

- Reviewer pass B: PASS, high confidence, no findings.
- Replacement reviewer pass: PASS, high confidence, no findings.
- One reviewer returned only `REJECT` without actionable findings and was
  replaced by the passing replacement review above.

## Claim-Boundary Scan

Risky terms were scanned in `paper/icc_main.tex`.

OK contexts:

- `packet`, `PER`, `PDR`, `CRC`, `gateway`, `OTA`, `live-satellite`,
  `link validation`: appear as exclusions, future work, related work, or
  non-claim/proxy context.
- `measured Doppler`: appears only in explicit non-claim boundaries.
- `software-only`, `synthetic`, and `reference_is_measured_truth=false` remain
  active claim-boundary language.

No conducted-IQ contribution, MCU latency/energy estimate, hardware validation,
RF validation, or ambiguous 90% real-result claim was introduced.

## Remaining Risks

- The figure generator remains an existing oversized plotting script; this pass
  changed only the existing Fig. 2/Fig. 3 layout code.
- Page 1 uses IEEEtran's normal wrapping for three anonymous author blocks; the
  third placeholder appears on a second row but remains double-blind safe.
- The main paper remains a software-only negative-result / evidence-gated
  inter-TLE residual learning paper; link-layer and OTA validation remain future
  work.
