# Paper 1 IEEE Author / Substance Fill Report

## Author Block

- Replaced the vertically stacked anonymous author block in `paper/icc_main.tex` with a three-column IEEE-style anonymous block.
- The rendered page 1 shows `Anonymous Author 1`, `Anonymous Author 2`, and `Anonymous Author 3` on one row.
- No real names, affiliations, emails, lab names, university names, acknowledgements, or identifying metadata were added.

## Text Added

- Introduction: strengthened the conservative framing by stating that the paper does not claim BLACK KITE improvement, and that small BLACK KITE-like inter-TLE residuals make always-learn unsafe; the gate is framed as a deployment audit rule.
- Section IV-B: added a compact policy interpretation after the 26.9 Hz versus 500 Hz discussion: the correct endpoint action is to refuse unsupported learning rather than tune a larger learner against weak signal.
- Conclusion: strengthened the deployment rule by stating that learned residual branches should remain quarantined until they repeatedly re-earn deployment on fresh chronological evidence, and expanded the audit log list to include stale-TLE age distribution.

## Build / Page Count

- Command run: `tectonic --keep-logs paper/icc_main.tex`
- Result: build completed.
- Page count: 6 pages.
- Log scan: no undefined references, no undefined citations, and no overfull boxes found.

## Visual QA

- Page 1: author block appears as a single three-author row, double-blind safe, with no real metadata.
- Page 6: conclusion and limitations are more substantively filled; references remain inside page 6.

## Claim-Boundary Scan

- No conducted-IQ section was reintroduced.
- No MCU latency or energy estimate was added.
- Remaining hardware/MCU mentions are non-validation artifact or diagram context only.
- Packet/PER/PDR/CRC/gateway/over-the-air terms appear only in negative scope statements or future-work limitations, not as validation claims.
- Main paper still states that results are software-only/model-derived, that `reference_is_measured_truth=false`, and that no measured Doppler truth or live-satellite/link-layer result is claimed.
- Synthetic results remain framed as mechanism checks only.

## Remaining Risks

- Page 6 still contains dense limitation text, but the added material is substantive and the references fit within the 6-page limit.
- The author block uses a compact tabular layout inside IEEE author macros to force the three anonymous placeholders onto one row.
