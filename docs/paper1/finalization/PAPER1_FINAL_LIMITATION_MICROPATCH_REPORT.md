# Paper 1 Final Limitation Micropatch Report

## Scope

Applied one final limitation-only micro-patch to `paper/icc_main.tex`.

No experiments, hardware actions, figure changes, numerical-result changes,
conducted-IQ text, MCU latency/energy estimates, section-structure changes, or
new validation claims were introduced.

## Text Added

In the Conclusion and Limitations section:

- Added an RF error-source caveat stating that practical endpoints may be
  dominated by oscillator offset, receiver synchronization, and channel effects,
  and that the paper isolates only the TLE-driven inter-TLE component.
- Replaced the repeated cross-satellite/generalization future-work sentence with
  a tail-aware/cost-aware gate future-work sentence based on p99 error, guard
  cost, or outage proxy.

## Build Checks

- Command: `tectonic --keep-logs paper/icc_main.tex`
- Result: success.
- Page count: 6 pages including references.
- Undefined references/citations: none found.
- Overfull boxes: none found.
- Remaining warnings: existing underfull boxes, font substitution warnings,
  duplicate PDF object warnings from reruns, and existing `algorithm.sty`
  UTF-8 warning.

## Claim-Boundary Checks

- No `conducted-IQ` text appears in the main paper.
- No MCU latency/energy estimate was added.
- Risky packet/PER/PDR/CRC/gateway/OTA/live-satellite/link-validation terms
  remain in limitation, future-work, related-work, or explicit non-claim
  contexts.
- The new RF caveat does not imply RF validation or hardware evidence.

## Remaining Blockers

- None for this limitation micro-patch.
- Submission-level metadata/anonymity policy decisions remain outside this
  patch.
