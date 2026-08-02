# Orbit-Evidence — speaker outline (8–10 min)

**Deck:** `talk/orbit_evidence_talk.pdf` · **13 main slides** + 2 backup · slide 5 builds in 4 clicks.
Every number on a slide is generated from `evaluation/results/final_summary.json`; `make -C talk check` fails if one drifts. Claim licences: `talk/TALK_CLAIM_LEDGER.md`.

| # | ⏱ | The one question it answers | Say roughly this |
|---|---|---|---|
| 1 | 0:15 | What is the thesis? | "A chronological split constrains order *inside one dataset*. Some deployment-validity conditions are not in that dataset at all." |
| 2 | 0:30 | Why is ordering alone insufficient? | Learning sits inside satellite software; we evaluate temporally, and that is right. The claim is that it is not enough — the gap is one of **kind**, not degree. |
| 3 | 0:40 | Which four obligations lie outside one realised dataset? | Walk the table, then the four boxes: availability, row membership, hidden state, statistical unit. "The split adjudicates everything inside this frame. None of these four is inside it." |
| 4 | 1:00 | What does relational validity mean? | Three panels, left to right. "Each counterexample exists only in another execution, another source state, or another aggregation level." Land the row-local/relational distinction — this is the paper's foundation. |
| 5 | 1:05 | How is it operationalised? | Click 1 experiment → 2 the 19-rule contract → 3 the two relational checks → 4 the verdict. On click 4: "a design that cannot support a decision returns INDETERMINATE — never PASS." |
| 6 | 0:55 | What do the two checks do? | L4.6: same manifest hash, different output — a counterexample to a claim of completeness. **"Failure is evidence; success is not certification."** L4.7: does dependence survive one declared level coarser, and it abstains below the registered resolution floor. |
| 7 | 0:45 | Is the gate calibrated before use? | "14 halts in 450 clean evaluations — 0.031, Wilson 0.018 to 0.052. The interval, not the point, is the claim, and it contains α." Seven evaluated points, 40 seeds each; the line only guides the eye. |
| 8 | 1:05 | Does the unit problem appear in real orbital data? | **Name both denominators.** "Cohort: 331 passes, 109 element-set records, 11 objects. The primary in-track analysis uses 272 passes in 90 successor-paired element sets — 59 have no successor." Then ρ̂ = 0.501, p = 0.0025, HALT. **Then the limits, spoken:** an update increment, *not truth error*; the element set halts too at 0.284, so no level tested here is exchangeable; **for this observable and declared hierarchy** only. |
| 9 | 0:45 | Can the frozen contract be applied externally? | Commit chosen before inspection, detector hash unchanged. Five categories — but say it precisely: "three **rule verdicts**, two **applicability dispositions**. N/OBS is never scored as compliance." |
| 10 | 0:55 | Does correcting a violation change the experiment? | Pre-registered L4.1 fix, overlap 100% → 0, HALT → PASS. Selected checkpoint changes 5/5, rerun bit-identical. Downstream moved both directions on three seeds — **"not estimable at this paired-run resolution"**, min two-sided p = 0.0625. Say plainly: no claim the upstream result is invalid, none that detection improved. |
| 11 | 0:35 | What is actually new? | Not ICC, not permutation, not a checklist. Identify what is relational → choose the falsifying counterfactual → encode it, and let an undecidable case abstain. |
| 12 | 0:30 | What does the paper not establish? | Read briskly; do not soften. Say **"represented-fault regression coverage"** out loud. "A validity method must apply the same evidence discipline to its own claims." |
| 13 | 0:15 | Takeaway. | "Chronological separation remains necessary. It is not sufficient. Some assumptions must become executable, falsifiable, and allowed to refuse." |

**Budget 9:15** (sum of the column; slides 4--6 hold the most conceptual time). These are budgets checked by summation, not stopwatch rehearsals. Running long? Cut slide 2 to one sentence and slide 11 to its three verbs. **Never cut** slide 8's limits, slide 12, or slide 13.

## Required spoken qualifiers

Each of these must be said aloud at least once; the first four are also on the slides.

- "for this observable and declared hierarchy" (slide 8)
- "failure is evidence; success is not certification" (slide 6)
- "represented-fault regression coverage" (slide 12)
- "not estimable at this paired-run resolution" (slide 10)
- "rule verdict versus applicability disposition" (slide 9)
- "message-creation time is a lower bound on retrievability" (only if the two clocks come up in Q&A)

## Never say

- "the manifest is complete" · "PASS means valid" · "we found the correct statistical unit"
- "the orbit prediction error is 0.501" · "the update increment is truth error"
- "the external paper is invalid" · "the correction improves anomaly detection"
- "the downstream result is null" · "all faults are detected" · "the 19 rules are complete"
- "the mirror is verified by the original publisher"
- "ICC or permutation inference is our new statistical method"
- Anything about Doppler-residual learning, LR-FHSS, link budget, packet or RF performance — the paper claims none of it, and the earlier programme's numbers are withdrawn.

## Q&A — each answer ≤ 20 seconds, none beyond the paper

| # | Question | Answer |
|---|---|---|
| 1 | Why a communications paper, not just software testing? | The obligations are supplied by satellite operations in a form generic tooling does not have: two clocks (element epoch versus message-creation time), rows generated by predicted geometry, retrospective labels, and repeated measures nesting inside an element set. That is where we found them and where they bite. |
| 2 | Why is chronological splitting not enough? | A split is a predicate over the rows of one realised dataset. Availability, row membership, hidden state and unit choice each have a counterexample that exists only outside that dataset. |
| 3 | Is L4.6 merely metamorphic testing? | The relation is metamorphic; the target is not. We apply it to declared provenance, where tracking systems record parameters without testing whether the declaration is behaviourally complete. |
| 4 | Is L4.7 merely ICC plus permutation? | Both are established and we propose neither. What is new is using the permutation reference to calibrate a **gate** — with an operating characteristic and an abstention state — rather than as an analysis step. |
| 5 | Why not always choose object as the unit? | Because the rule adjudicates the level it is given, never which level is right — and on our own data the element-set-to-object grouping halts too. Element sets and deployment episodes cross-cut, so there is no unique next coarser level. |
| 6 | How is PASS useful if it proves nothing? | It is a regression guard. A represented violation, once fixed, cannot silently return in the form the suite injects. That is the whole claim. |
| 7 | Why is INDETERMINATE not just low power? | **Backup slide 1.** Three coarser groups of two units admit 15 assignments, so the smallest attainable p is 0.067 — that design cannot reject at any effect size. Low power is about ρ; this is about the design's resolution. |
| 8 | Why 272 passes rather than 331? | 59 of the 331 have no successor element set, so no in-track increment can be formed. The cohort is 331; the primary analysis is 272 in 90 element sets. Both are on the slide. |
| 9 | Does ρ̂ = 0.501 measure orbit truth error? | No. It is the intraclass correlation of an **update increment** between consecutive fits sharing most of their observation arc — median 0.226 km. No truth reference is involved. |
| 10 | Did correcting Telemanom improve detection? | We do not claim that and the data could not support it. Model selection changed in 5 of 5 seeds; the downstream metric moved in both directions and is not estimable at five paired seeds. |
| 11 | Why trust a checksum mirror? | We do not claim publisher verification. The upstream endpoint became unavailable; per-file hashes matched two independently published checksum sources. That is mirror concordance, and the deck says so. |
| 12 | What would a main-track or journal version need? | Independent replication across faults and pipelines authored outside this work, and a downstream endpoint with enough resolution to decide. Both need new experiments, which this submission does not have. |

## Build

```
make -C talk          # regenerates numbers from the artifact, then builds the PDF
make -C talk check    # numbers, semantic lint, required qualifiers, 13-frame count
```
