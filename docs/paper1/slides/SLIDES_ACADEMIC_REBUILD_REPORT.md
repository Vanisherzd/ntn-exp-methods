# Slides Academic Rebuild Report

## Scope

- Rebuilt `paper/slides_overview.tex` into a 14-slide academic advisor-review deck.
- Did not edit `paper/icc_main.tex`.
- Did not change paper results, figures, references, or numerical values.
- Did not run experiments, touch hardware, commit, or push.

## New Deck Structure

1. **Title**: clean academic title slide with workshop/advisor-review subtitle and BLACK KITE LR-FHSS TX / Space-Track/TLE / SGP4 context.
2. **Problem**: endpoint timing/frequency control before transmission.
3. **Temptation**: why always-on residual learning is unsafe.
4. **Paper framing**: falsification-oriented deploy/no-deploy policy, not a stronger residual predictor.
5. **Evidence Gate rule**: equation and gate-open/gate-closed interpretation.
6. **Main result**: real BLACK KITE negative finding; learned inter-TLE residual never beats SGP4.
7. **Policy comparison**: always-learn vs never-learn vs Evidence Gate, emphasizing why a closed real gate is useful.
8. **Synthetic mechanism check**: software-only controlled systematic residual case; not BLACK KITE improvement.
9. **Endpoint proxy model**: timing/frequency uncertainty to guard and energy proxies.
10. **Proxy ablation**: 90% number labeled as controlled synthetic gate-open proxy only.
11. **Limitations**: cross-satellite generalization, RF error sources, tail/cost-aware gates.
12. **Artifact sanity only**: conducted-IQ moved near the end, labeled artifact-only, LR1121 consistently used.
13. **Next software campaign**: multi-satellite TLE stress test, residual learnability, stronger baselines, tail/cost-aware gate.
14. **Takeaway**: contribution order starts with the real negative finding.

## Claim-Boundary Scan

- `LR1131`: no hits.
- `LR1121`: present only on the artifact sanity slide.
- Conducted-IQ appears only on slide 12 and is labeled artifact sanity only.
- No "hardware validation" or "RF validation" language.
- Packet/PER/PDR/CRC/gateway ACK/OTA/live-satellite/link-layer terms appear only in negative-scope statements.
- Synthetic results are labeled as software-only mechanism checks, not real BLACK KITE deployment outcomes.
- Fig. 3/proxy content is labeled as software-only endpoint-control proxy.
- Real results remain framed as model-derived inter-TLE residuals, not measured Doppler truth.

## Build Result

- Command run: `tectonic --keep-logs paper/slides_overview.tex`
- Output: `paper/slides_overview.pdf`
- Slide count: 14.
- Log scan: no undefined references, no undefined citations, no package errors, and no overfull boxes.
- Remaining warnings are underfull hboxes only.

## Visual QA

- Rendered all 14 slides with `pdftoppm`.
- Reviewed a full contact sheet and inspected the policy and conducted-IQ slides individually.
- Title slide now reads as an academic title slide rather than a clipart-heavy flow.
- Slide 7 policy table was enlarged and the only awkward wrap was shortened.
- Slide 12 is visually clean, uses LR1121 only, and marks conducted-IQ as artifact sanity only.
- Slides 10 and 14 clearly label proxy-only / contribution-order boundaries.

## Remaining Risks

- Some figure labels inherit readability limits from the existing figure assets, especially on the synthetic gate plot and proxy ablation, but legends do not cover data and the slide-level caveats are clear.
- The conducted-IQ slide remains in the deck because the requested structure included it as appendix-like artifact sanity; it is explicitly not a paper contribution.
