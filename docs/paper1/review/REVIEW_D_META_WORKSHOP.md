# Review D - Meta / Workshop Fit Reviewer

## Recommendation

Score: 3/5, borderline. This is a coherent six-page workshop paper with a defensible negative result and unusually careful caveats. It is not yet a strong accept because the story tries to be three papers at once: evidence-gated ML, endpoint proxy economics, and conducted hardware sanity.

## Major Concerns

1. Coherence is good for six pages, but the contribution hierarchy is still crowded. The paper has a real-data negative result, synthetic gate-open demonstration, proxy energy model, MCU footprint estimate, and conducted-IQ sanity check. Reviewers may leave unsure which item is the actual contribution.

2. The most defensible workshop contribution is: "do not blindly learn residual Doppler correction from stale TLE history; use a chronological evidence gate, which closes on real BLACK KITE data." That is interesting and honest. The manuscript should lead with that, not with the synthetic 90% proxy-success story.

3. The paper is careful about overclaiming, but reviewers often read figures and abstracts first. Fig. 3 and the abstract's `<1%` to `~90%` language may overpower the disclaimers.

4. The title "Evidence-Gated Timing/Frequency Control" is accurate but somewhat positive-sounding. Since the real gate always closes, a reviewer may feel the title promises an operating learned controller rather than a deploy/no-deploy test.

5. The paper lacks author metadata and uses placeholder affiliations. If this is the actual submission PDF, that is a must-fix administrative issue.

## Minor Fixes

- Put "negative real-data result" in the abstract's first half.
- Move one or two limitation sentences earlier, before Fig. 3.
- Reduce acronym density: PGRL, LR-FHSS, D2S, TLE, SGP4, CFO, IQ, PER/PDR/CRC, ACK, OTA appear in a short paper.
- Consider making Table II the central story table and Fig. 3 explicitly secondary.
- Check for typography issues in citations and references; the rendered PDF is legible, but some spacing and line breaks are tight.

## Must Fix Before Submission

- Decide whether the pitch is a negative-result safety gate paper or a proxy endpoint-control paper. The current version tries to sell both.
- Make synthetic-only claims visually and textually subordinate to real-data claims.
- Tighten the abstract to prevent any packet/link/OTA interpretation.
- Replace placeholder author/affiliation fields before submission.

## Likely Workshop Outcome

For a focused ICC/GLOBECOM workshop, I would expect scores around 2.5-3.5 depending on reviewer tolerance for negative results and proxy evidence. The paper can be accepted if the workshop values early-stage NTN IoT methods and honest limitations; it is vulnerable if reviewers expect packet-level LR-FHSS, real Doppler measurements, or an actually deployed learned controller.
