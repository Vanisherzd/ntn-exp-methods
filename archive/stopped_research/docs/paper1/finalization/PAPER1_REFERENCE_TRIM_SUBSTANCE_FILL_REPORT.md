# Paper 1 Reference Trim and Substance Fill Report

## Scope

Performed a conservative bibliography trim and used the freed space for
reviewer-defense text in `paper/icc_main.tex`.

No experiments, hardware actions, figure changes, numerical-result changes,
conducted-IQ text, MCU estimates, or hardware/link-validation claims were added.

## References Removed

Removed four active references from the manuscript and deleted their BibTeX
entries from `paper/refs.bib`:

- `vallado2007fundamentals` - SGP4 support is retained through
  `hoots1980models`.
- `boquet2021lrfhss` - LR-FHSS background remains supported by Semtech,
  Ullah WCL, and Ullah OJ-COMS.
- `jung2023lrfhss` - transceiver design is no longer part of the main
  contribution path.
- `bukhari2023lrfhss` - packet-trace work is no longer central because the
  paper does not claim packet or link validation.

## References Kept

The generated paper reference list now contains 9 entries:

- `hurn2023lrfhss`
- `semtech2023lrfhss`
- `hoots1980models`
- `ullah2022lrfhss`
- `3gpp2019tr38821`
- `peng2019gp`
- `acciarini2025dsgp4`
- `caldas2024mlorbit`
- `alvarez2022uplink`

## Body Text Added

Added compact reviewer-defense text in three places:

- Introduction: explicitly states the paper is intentionally conservative and
  does not argue that residual learning improves current BLACK KITE operation.
- Conclusion: reframes the Evidence Gate as an audit rule, not a guaranteed
  improvement mechanism; on BLACK KITE, choosing never-learn is the safe action.
- Limitations: separates orbital uncertainty from oscillator offset, receiver
  synchronization, and channel effects; notes the need to combine the gate with
  oscillator calibration and tail-aware deployment loss.

## Build and Page Check

- Command: `tectonic --keep-logs paper/icc_main.tex`
- Result: success.
- Page count: 6 pages including references.
- Undefined references/citations: none found.
- Overfull boxes: none found.
- References: 9 entries, all on page 6.

## Remaining Whitespace Assessment

Page 6 is more substantively filled than before: the conclusion now occupies
more of the left column, and the right-column reference list is shorter and less
dominant. Some normal bottom whitespace remains, but the ending is no longer
reference-heavy.

## Claim-Boundary Scan

Risky terms remain in acceptable contexts:

- `packet`, `PER`, `PDR`, `CRC`, `gateway`, `OTA`, `live-satellite`, and
  `link validation` appear as exclusions, future work, related work, or
  explicit non-claim/proxy context.
- `measured Doppler` appears only in explicit non-claim boundaries.
- `software-only`, `synthetic`, and `reference_is_measured_truth=false` remain
  active claim-boundary language.

No conducted-IQ contribution, MCU estimate, hardware validation, RF validation,
or ambiguous packet/link validation claim was introduced.
