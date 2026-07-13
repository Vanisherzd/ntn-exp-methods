# Paper 1 Final Substance-Fill Report

## Text Added

- Introduction: clarified that the contribution is not a stronger residual predictor, but a falsification-oriented endpoint deployment policy. Added the requirement that learned residual compensation demonstrate chronological utility over the deployable SGP4 baseline before spending guard, frequency margin, or energy.
- Section IV-B: strengthened the policy implication of the BLACK KITE negative result. The residual learner is framed as an untrusted candidate rather than a default enhancement module, and the gate is described as protecting the terminal from converting validation noise into additional guard, frequency margin, or retransmission pressure.
- Conclusion and Limitations: expanded the deployment audit checklist to include stale-TLE identifier, refresh time, validation interval, baseline MAE, learned MAE, `gamma`, `G`, and the resulting guard/frequency policy.

## Build / Page Count

- Command run: `tectonic --keep-logs paper/icc_main.tex`
- Result: build completed.
- Page count: 6 pages.
- Log scan: no undefined references, no undefined citations, and no overfull boxes found.

## Visual QA

- Page 1: three anonymous IEEE-style authors remain in one row.
- Page 6: conclusion/limitations text is more substantive; references remain inside page 6.

## Claim-Boundary Scan

- No new references were added.
- No figures were changed.
- No conducted-IQ section was reintroduced.
- No MCU latency or energy estimate was added.
- Remaining packet/PER/PDR/CRC/gateway/over-the-air/live-satellite terms appear in negative scope statements or future-work limitations, not validation claims.
- Main paper still states that real results are software-only/model-derived inter-TLE residuals, `reference_is_measured_truth=false`, and no measured Doppler truth or link-layer validation is claimed.
- Synthetic results remain framed as mechanism checks only, and Fig. 3 remains a software-only proxy.

## Remaining Risks

- Page 6 is dense, but the added text is reviewer-defense substance rather than filler.
- The final sentence on packet-level and authorized over-the-air measurement remains explicitly future work, not evidence in the paper.
