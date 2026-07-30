# Paper 1 Tone-Down / Reviewer-Risk Reduction Report

## Scope

Performed a conservative repositioning pass only. No experiments were run, no hardware
was touched, no numerical results were changed, no references were added, Table IV was
kept, and no Fig. 4 / hardware figure was reintroduced into the main paper.

## Title

Before:

> Evidence-Gated Timing/Frequency Control for LR-FHSS Direct-to-Satellite IoT

After:

> Evidence-Gated Residual Learning for LR-FHSS Direct-to-Satellite IoT Endpoint Control

Rationale: keeps the endpoint-control framing while moving the headline from apparent
full timing/frequency control validation toward evidence-gated residual learning and a
deploy/no-deploy trust decision.

## Abstract Changes

The abstract was rewritten to reduce synthetic and hardware headline risk. It now:

- keeps stale TLE / SGP4 as the deployable baseline;
- frames the core problem as a pre-transmission endpoint deploy/no-deploy decision;
- states the real BLACK KITE result as a negative result: the learned residual does not
  beat SGP4 and the gate closes;
- describes the synthetic result only as a controlled mechanism check;
- describes endpoint results as software-only timing/frequency budget proxies;
- describes the conducted-IQ run only as a cabled transmit/receive measurement-path
  check;
- explicitly disclaims measured Doppler truth, packet, link-layer, OTA, and
  live-satellite results.

The abstract no longer headlines the synthetic "<1% to about 90%" proxy result or the
conducted-IQ TX-ON/TX-OFF separation.

## Contribution Changes

The contribution list was compressed and toned down to three defensible workshop claims:

1. Evidence-gated residual learning as a pre-transmission deploy/no-deploy trust test
   under stale orbital information.
2. Real-data negative control on BLACK KITE plus a controlled synthetic gate-open
   mechanism check.
3. Endpoint-budget proxy model plus bounded conducted-IQ sanity evidence, explicitly
   not packet, link-layer, or OTA validation.

No contribution claims real-data learning improvement, constellation-scale
generalization, packet success/PER/PDR, hardware validation of the Evidence Gate, or
measured Doppler correction.

## Synthetic / Hardware Overclaim Mitigation

Body wording was tightened so synthetic and proxy results are labeled as controlled,
software-only, or coverage-proxy evidence. The 90.4% proxy result remains only in the
body and is explicitly tied to the controlled gate-open synthetic setting.

Section V and Table IV were kept subordinate. The conducted-IQ evidence is framed as a
measurement-path sanity check only. The paper states that it does not exercise Doppler
correction, evidence gating, packet decode, OTA behavior, or link-layer validation.

The cross-satellite limitation was strengthened:

> Cross-satellite generalization is the main limitation and the primary target of the
> next software campaign.

## Slides Alignment

`paper/slides_overview.tex` was aligned with the safer positioning:

- title matches the revised paper title;
- title slide marks the deck as a workshop/advisor-review draft;
- real BLACK KITE result is presented as the strongest real result and a negative
  control;
- synthetic result is labeled as a software-only mechanism check;
- timing/frequency results are labeled as proxy, not packet results;
- conducted-IQ slide remains advisor discussion evidence only and keeps the claim
  boundary;
- cross-satellite generalization and next multi-satellite TLE campaign remain explicit.

Slide card padding and dense frames were also tightened to remove overfull boxes.

## Build Status

Commands run:

- `tectonic paper/icc_main.tex`
- `tectonic paper/slides_overview.tex`
- repeated with `--keep-logs` to refresh logs for scanning

Results:

- Main paper: 6 pages including references.
- Slides: 13 slides.
- Undefined references/citations: none found in refreshed logs.
- Overfull boxes: none found in refreshed logs.
- Remaining warnings: paper has underfull boxes and an existing `algorithm.sty` UTF-8
  warning; slides have two underfull boxes and embedded-PDF version warnings.

## Structural Checks

- Section V `Preliminary Conducted-IQ Evidence`: present.
- Table IV `Conducted-IQ sanity check summary`: present.
- Table IV label `tab:hw`: present.
- No active `Fig. 4`, `fig:hw`, `fig_conducted_iq_evidence`, or `fig_hw` reference in
  `paper/icc_main.tex`.
- Table IV remains the only main-paper hardware evidence.

## Risky-Term Scan

Strict scan terms:

`packet`, `PER`, `PDR`, `CRC`, `gateway ACK`, `OTA`, `live-satellite`, `link validation`,
`RF validation`, `measured Doppler`, `truth`, `end-to-end`, `90%`, `hardware validation`.

Classification:

- OK limitation / boundary: abstract no-claim sentence, Table IV boundary row, Section
  V measurement-path boundary, conclusion limitations, and slide claim-boundary footers.
- OK related work: receiver-side packet-trace mention in related work.
- OK synthetic/proxy context: Fig. 3 caption, endpoint-control proxy subsection, timing
  sensitivity and ablation slides.
- OK future work: packet-level conducted PER/PDR and authorized OTA measurement are
  explicitly future work.
- OK numeric context: 90.4% appears only in the body as the controlled gate-open
  synthetic proxy result; no abstract headline remains.
- FIX ambiguous positive claim: none found.

## Remaining Blockers

- Submission readiness still depends on author block / venue anonymity policy and final
  metadata.
- Optional reference metadata updates should remain deferred unless verified and
  page-safe.

## Readiness

Ready for another strict review as an advisor/workshop draft. Not yet final submission
ready until author policy and metadata are resolved.
