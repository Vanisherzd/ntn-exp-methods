# Orbit-Evidence — speaker outline (8–10 min)

**Deck:** `talk/orbit_evidence_talk.pdf` · 12 slides + 2 backup · slide 5 builds in 4 clicks.
**Every number on a slide is generated from `evaluation/results/final_summary.json`.** Do not quote a figure that is not on a slide.

| # | ⏱ | The one message | Say roughly this |
|---|---|---|---|
| 1 | 0:20 | Ordering ≠ validity. | "A chronological split constrains order *inside one dataset*. Some deployment-validity conditions are not in that dataset at all." |
| 2 | 0:45 | Necessary, not sufficient. | Learning sits inside satellite software; we evaluate temporally, and that is right. The claim is that it is not enough — and the gap is one of **kind**, not degree. |
| 3 | 1:00 | Four obligations live outside the table. | Walk the table, then the four boxes: availability, row membership, hidden state, statistical unit. "The split can adjudicate everything inside this frame. None of these four is inside it." |
| 4 | 1:00 | **The pivot.** Relational, not row-local. | Three panels left to right. "Each counterexample exists only in another execution, another source state, or another aggregation level." Land the row-local/relational distinction — this is the paper's foundation. |
| 5 | 1:15 | Validity as an executable contract. | Click 1 experiment → 2 the 19-rule contract → 3 the two relational checks → 4 the verdict. On click 4: "a design that cannot support a decision returns INDETERMINATE — never PASS." |
| 6 | 1:00 | Two checks, one judgement. | L4.6: same manifest, different output ⇒ incomplete — falsifiable *without enumerating* what a manifest might omit. L4.7: does dependence survive one level coarser, and it **abstains**. "Neither can be certified, so we accept checks that can only refuse." |
| 7 | 0:50 | Calibrated before trusted. | "14 halts in 450 clean evaluations. The interval, not the point, is the claim — and it contains α." Then power rises with ICC; low ρ has low power. If asked about INDETERMINATE → backup slide 1. |
| 8 | 1:10 | Yes, on real catalogue data. | ρ̂ = 0.501, p = 0.0025, HALT — and the element set halts too, so *no level tested here is exchangeable*. **Then immediately give the three "does not mean"s.** Do not skip them. |
| 9 | 1:15 | The frozen contract runs elsewhere. | Frozen commit chosen before inspection. Five categories — three verdicts, two dispositions; N/OBS is never compliance. Intervention: HALT→PASS, checkpoint changes 5/5. Downstream: **not estimable**, not a null. |
| 10 | 0:45 | The novelty is the conversion. | Not ICC, not permutation, not a checklist. Identify what is relational → choose the falsifying counterfactual → encode it, and let an undecidable case abstain. "Change what is tested, not how much." |
| 11 | 0:40 | State the boundaries. | Read them briskly; do not soften. "A validity paper that overstates its own evidence has refuted itself." |
| 12 | 0:20 | Close. | "Chronological separation remains necessary. It is not sufficient. Some assumptions must become executable, falsifiable, and allowed to refuse." |

**Running long?** Cut slide 2 to one sentence and take slide 10 at half speed. Never cut slide 8's "what it does not mean" or slide 11.

## Do not say

- Nothing about Doppler-residual learning, LR-FHSS, link budget, packet or RF performance — the paper claims none of it, and the earlier programme's numbers are withdrawn.
- Never "the split was wrong", "Telemanom's published result is invalid", "the correction improves detection", or "chronological validation improves F1".
- Never "PASS means valid" — PASS means **not rejected**.
- Never call the downstream endpoint a null result. It is not estimable at five paired seeds.
- Never call the along-track quantity orbital truth error. It is an **update increment**.

## Likely questions

| Asked | Answer |
|---|---|
| "Isn't this just ICC plus a permutation test?" | Those are primitives we did not propose. The method is choosing *which* obligations are relational and what counterfactual falsifies each. The gate — operating characteristic plus abstention — is what a plain analysis step is not. |
| "Why does INDETERMINATE exist? Isn't it just low power?" | **Backup slide 1.** Three groups of two admit 15 assignments; the smallest reachable p is 0.067 > α. No such design can reject at *any* effect size. That is attainability, not power. |
| "Only one third-party artifact?" | Correct, and one channel. It partially breaks the loop; it does not close it. Slide 11 says so. |
| "Can I reproduce the third-party study?" | **Backup slide 2.** `make external-consequence-verify` checks it against the frozen commit, the detector hash and the recorded data hashes — 16 checks, no training. `make external-consequence-run` retrains, fail-closed. |
| "Where did the telemetry data come from?" | A checksum-verified mirror after the upstream endpoint went away; hashes matched two independently published sources. That is mirror concordance, **not** verification by the original publisher. Say this plainly. |
| "Does the element set generalise as the right unit?" | No — and our own D3 analysis halts on it. The rule adjudicates the level it is *given*, never which level is right. |

## Build

```
make -C talk          # regenerates numbers from the artifact, then builds the PDF
make -C talk check    # fails if any slide number has drifted from final_summary.json
```
