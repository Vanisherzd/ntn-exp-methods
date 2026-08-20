# Advisor-review notes — Orbit-Evidence

**Deck:** `talk/advisor_review/advisor_deck.pdf` · 27 main + 12 appendix · 39 pages, no overlays.
**Not the workshop talk.** The reviewer-proof workshop deck is `talk/orbit_evidence_talk.pdf`
(tag `talk/orbit-evidence-reviewer-proof-2026-08`) and is untouched.

Budget ≈ 20–30 minutes **with interruption**. This is an explanation deck: if the advisor stops you
on slide 5, that is the deck working. Slides 4, 5, 8, 13, 16, 19 and 24 are the ones worth losing
time on; slides 10, 17 and 18 compress safely.

**The advisor is not a satellite person — so teach the system, do not analogise it away.** Slides
2–5 exist to give him the real background in order: what the experiment does, where its input comes
from, how one record becomes many passes, and the two clocks. Every satellite term is defined at
first use and then used normally: *object* and *element set* on slide 3, *orbital propagation* and
*pass* on slide 4, *epoch* and *catalogue creation time* on slide 5, *along-track update increment*
on slide 19. Do not avoid the vocabulary after it is defined — the goal is that he learns it.

Every number on a slide is generated from the frozen artifacts by `gen_numbers.py`.
`make -C talk/advisor_review check` fails if a slide or these notes disagree with the artifact, and
it also fails if this file's declared deck shape stops matching the deck.

**Four slides answer questions the earlier deck left implicit** and are the ones to protect if you
run short: **16** (the tradeoff), **23** (how an engineer uses it), **25** (the quantified benefit),
and **4** (why several passes are not independent observations).

---

## ACT I — why this paper exists

### Slide 1 — Title and thesis
**Purpose.** Put the whole claim on the table before any machinery.
**Say.** "A chronological split checks ordering inside one realised dataset. Some
deployment-validity assumptions can only be falsified by comparing another execution, another
source state, or another physical aggregation level." Then stop. Do not mention the rule count.
**Likely question.** *So this is a testing paper?*
**Answer.** "It is a paper about what an experiment's evaluation establishes. The obligations come
from satellite operations; the contribution is making them falsifiable."
**Prohibited.** Do not open with the contract, the rule count, or the tooling.

### Slide 2 — The kind of experiment this work audits
**Purpose.** Teach the actual system before any validity problem — and say immediately that this
paper does not build one. Two cross-domain reviewers both stopped here expecting to be told what the
learned component predicts; it is not this paper's model, and the slide now says so.
**Say.** "A published orbit estimate comes in. From it we predict when and where the satellite will
be visible. A learning-assisted component consumes those predictions. That drives a deployment
decision. Later we ask whether that decision was valid." Then the line that matters: the model never
sees the true future orbit — only the orbit information that was actually available at decision time.
**Likely question.** *What is the learned component actually predicting?*
**Answer.** "In this paper, nothing — we train no model. This is the shape of experiment the method
audits. The one real audited model is the frozen third-party artifact on slide 22, where the
correction changed which checkpoint early stopping selected."
**Likely question.** *Then what is the deployment decision?*
**Answer.** "Whatever the audited experiment's decision is. For the third-party case it is which
model checkpoint gets selected. The method does not care what the decision is — it cares whether the
evidence offered for it is valid."
**Prohibited.** Do not describe a learned model as ours; the only learning-assisted line this group
ran was stopped and is withdrawn (A10). Do not introduce element sets, passes, epochs or propagation
yet — slides 3, 4 and 5 do that, in that order.

### Slide 3 — Where the orbital-state records come from
**Purpose.** Teach the input. Three facts on this slide are load-bearing for the rest of the deck:
it is an estimate, it is superseded, and one record feeds many predictions.
**Say.** "A physical satellite is moving — the catalogue calls it an *object*. A catalogue provider
tracks it and *estimates* its orbit. It publishes that estimate as an orbital-state record; the
formal term is an *element set*. Our experiment downloads it." Then read the three facts on the
right: an estimate, not truth; periodically superseded by a newer record; one record predicts many
future events.
**Likely question.** *Is an element set a TLE?*
**Answer.** "Yes, for this cohort that is the form. What matters is that it is somebody else's
estimate, published on their schedule, and later replaced."
**Likely question.** *Why does it get replaced?*
**Answer.** "New tracking observations arrive, so the provider re-estimates. That revision is
exactly what slide 19 measures."
**Prohibited.** Never call the record ground truth. Do not say the catalogue is wrong.

### Slide 4 — One record, many predicted passes
**Purpose.** Teach *propagation* and *pass* physically, and establish the parent-to-many-children
shape that slide 13 will question and slide 20 will test.
**Say.** "Orbital propagation means computing where the satellite is predicted to be at a later
time, from that one record." Point at the horizon and the ground station. "Each hump is an interval
when the satellite is predicted to be above the horizon for that ground station — that is a *pass*.
One record propagated forward gives you several passes."
**Likely question.** *Visible to what?*
**Answer.** "To a ground station. A pass is defined relative to an observer on the ground, which is
why it is a communication opportunity."
**Likely question.** *How far ahead do you propagate?*
**Answer.** "Over the window the experiment plans in. The point here is only that one record yields
many passes, which is where the dependence comes from."
**Prohibited.** No orbital-mechanics detail — no SGP4, no equations. Do not present the humps as
measured elevation data; the shape is a schematic.

### Slide 5 — Two clocks, and a decision between them
**Purpose.** The availability failure, stated as two named clocks. This is the concrete failure the
whole paper generalises from.
**Say.** "Two different times. The record's *epoch* is the time whose satellite state it describes —
twelve o'clock. The *catalogue creation time* is when the provider actually created that record —
nine in the evening. Our decision had to happen at one." Pause. "So the record describes the past,
but it did not exist yet at the decision." Then: "A chronological split sees twelve is before one,
and treats the record as historical input."
**Likely question.** *Is the gap real or a corner case?*
**Answer.** "Publication trails the epoch by a per-satellite median of about six and a third hours
across eleven satellites, with a tail to days. And creation time is itself only a lower bound on
when the record could actually be retrieved, so the real gap is at least that."
**Prohibited.** The three clock times are illustrative; only the median lag comes from the artifact —
do not present the timeline itself as a measured result. Do not say the catalogue is wrong.

### Slide 6 — What a chronological split can see
**Purpose.** Make the limit visible rather than argued.
**Say.** "The split cuts the row sequence in time. It constrains the ordering of observations that
already exist as rows in this table." Pause, point at the dashed box below the table. "What if the
counterexample is not a row in this table?"
**Likely question.** *Isn't that just leakage, already well studied?*
**Answer.** "Leakage work is largely about information that IS in the data crossing the boundary.
Three of our four obligations concern information that is not in the dataset at all."
**Prohibited.** Do not imply the split is unsound.

### Slide 7 — Four questions a split cannot answer
**Purpose.** Generalise the slide before into four questions a split cannot answer.
**Say.** "That was one instance — the first card. Here is the general shape." Walk the four as
questions. Land the closing line: these look different, but in every case the counterexample lies
outside the realised table.
**Likely question.** *Is the list of four complete?*
**Answer.** "No, and we do not claim it is. These are the four we encountered and could make
falsifiable."
**Prohibited.** Never present the four as exhaustive.

### Slide 8 — Relational validity
**Purpose.** The paper's foundation. Spend time here.
**Say.** Row-local validity is decidable from one realised run. Relational validity has a
counterexample that exists only in another execution, another source state, or another aggregation
level. The bracket is the point: each row needs a *second* thing to compare against. "The
contribution begins by changing the object of validation."
**Likely question.** *Is "relational validity" a real distinction or a relabelling?*
**Answer.** "It is a decidability distinction, and it is operational: it tells you what second
thing you must obtain before the property can be tested at all. Every rule in L4 follows from it."
**Prohibited.** Do not claim all validity is relational.

---

## ACT II — the method

### Slide 9 — What Orbit-Evidence does
**Purpose.** One architectural pass, no rule-level detail.
**Say.** A declared experiment goes in; one of three verdicts comes out. HALT refuses the build.
INDETERMINATE is never upgraded to PASS.
**Likely question.** *Why nineteen rules?*
**Answer.** "Nineteen is what the satellite instantiation needed. The number is not the
contribution and we do not claim it is complete."
**Prohibited.** Do not defend the count as principled.

### Slide 10 — The method, in four steps
**Purpose.** The advisor should be able to reproduce the method from this slide alone.
**Say.** Declare, classify, construct the counterexample relation, bind to a verdict. Every step is
fixed before the data is touched. The L1–L4 box on the right is code structure only — say so once and
do not walk it; the full nineteen-rule map is A1. Then read the line under the steps once: the three
rules this talk actually uses are L4.1 partition, L4.6 provenance, L4.7 statistical unit. Reviewers
could not resolve a single rule number without it.
**Likely question.** *What generalises beyond satellites?*
**Answer.** "The four steps. The rules are the instantiation; the procedure is the claim."
**Prohibited.** Do not present the procedure as automated — step 2 is a modelling decision. Do not
walk the four layers; they are not the contribution.

### Slide 11 — Can the provenance declaration be trusted?  `L4.6`
**Purpose.** Establish why enumeration cannot work, and show the trick, on one slide.
**Say.** Left: a manifest cannot prove it contains every behaviour-changing dependency, because the
omitted dependency is exactly what is absent from it — enumeration cannot certify its own coverage.
Right: same manifest hash, different output, therefore something outside the manifest mattered.
"We do not prove completeness. We make incompleteness falsifiable."
**Likely question.** *Is this just metamorphic testing? Don't hermetic builds solve it?*
**Answer.** "The relation is metamorphic; the target is not. Hermetic builds try to prevent
undeclared inputs; L4.6 tests whether a declaration already in use is behaviourally complete."
(Appendix A9.)
**Prohibited.** Never say "falsifies incompleteness". Say "refutes a claim of completeness" or
"exposes incompleteness". Never state the implication without its precondition: it holds only if
execution is deterministic given the manifest. Without that, a HALT is a disjunction — incomplete
manifest OR nondeterministic execution. If asked, point to the byte-identical rerun.

### Slide 12 — How strong is the evidence for that check?  `L4.6`
**Purpose.** Put the weakest part of the paper on the table yourself, and convert it into a
decision. This is advisor decision 1 of 3.
**Say.** "The controlled fixture demonstrates the check. No third-party artifact has exercised it.
That asymmetry is real and I want your call on whether the workshop needs an external case."
Then stop and let them answer.
**Likely question.** *Why has no external case been run?*
**Answer.** "It needs an artifact that varies a dependency outside its own manifest and reruns.
Finding one is a search problem, not a coding problem, and I did not want to claim it before it
exists."
**Prohibited.** Do not present the controlled fixture as external evidence.

### Slide 13 — Are these really independent samples?  `L4.7`
**Purpose.** Show that choosing a unit is an assumption, not a fix.
**Say.** Teach the mechanism, which is on the slide: "the three shaded passes were all propagated
from the *same* orbital-state record, so they inherit that record's estimation error. Displace the
parent estimate and its passes move together — they are siblings, not independent samples." Then the
question that follows: if the passes are dependent, why would aggregating them to element sets create
independence? Physical nesting is real but is not a single chain — deployment episodes cross-cut.
**Likely question.** *Why not just use the satellite as the unit?*
**Answer.** "Because the rule adjudicates the level it is given, never which level is right — and
on our own data the snapshot-to-satellite grouping halts too. There is no unique next coarser
level."
**Prohibited.** Do not say we found the correct statistical unit.

### Slide 14 — The test: shuffle values, keep the groups
**Purpose.** State the mechanism as a picture, and disown the primitives.
**Say.** Plain language first, and do not name the estimator until the picture has landed: "I check
whether values under one parent resemble each other more than chance, then I shuffle the values while
the group boxes never move. If the real clustering beats almost every shuffle, these are not
independent samples." The null is exchangeability across the declared groups. Only then, if asked,
point at the corner: the clustering statistic is ICC(1). ICC is not new, permutation inference is not
new; the novelty is using a calibrated decision as an executable gate.
**Likely question.** *Is L4.7 just ICC with a threshold?*
**Answer.** "Both ingredients are established and we propose neither. What is new is calibrating a
gate — with an operating characteristic and an abstention state — rather than reporting an
analysis."
**Prohibited.** Do not claim ICC or permutation inference as our statistical contribution. Do not
call the ICC a variance share.

### Slide 15 — A design can be too small to test at all
**Purpose.** The distinction most likely to be misread.
**Say.** Lead with the picture, not the number: "three groups of two units is this small." Then:
with that geometry the smallest attainable p exceeds α, so the design cannot reject at any effect
size. The rule returns INDETERMINATE rather than PASS.
**Likely question.** *Isn't INDETERMINATE just low power?*
**Answer.** "No. Low power is about ρ at a fixed design. This is about what the grouping geometry
can attain regardless of ρ — an attainability floor, evaluated before any data is seen."
**Prohibited.** Do not treat insufficient resolution as evidence of validity.

### Slide 16 — The tradeoff is deliberate
**Purpose.** Answer, before it is asked, "did you swap the hard problem for an easier one?" Yes —
and that is the design. This is the slide that names the paper's cleverness.
**Say.** "Certifying that an experiment is valid is not attainable. So both checks relax it the same
way. L4.6 asks for a counterexample instead of a certificate. L4.7 abstains instead of forcing a
pass. If neither fires, PASS — which means not rejected, nothing more." Then the gain and the cost
out loud: a failure becomes constructive evidence; a pass cannot certify validity.
**Likely question.** *So the method can never tell me an experiment is sound?*
**Answer.** "Correct, and no method that works from one realised run can. What it tells you is that
a specific class of invalidity is absent in the form we can falsify — and when it cannot tell you
even that, it says INDETERMINATE instead of PASS."
**Prohibited.** Do not present the relaxation as a limitation discovered late — it is the design
choice. Do not say PASS means valid.

---

## ACT III — does the method behave correctly?

### Slide 17 — A chronological baseline misses most represented faults
**Purpose.** Show the rules fire mechanically, and bound the claim immediately.
**Say.** The chronological baseline catches the ordering faults and is blind to the rest. The
contract catches every represented fault. Then the boundary, in the same breath: this is
represented-fault regression reachability, not unseen-fault sensitivity.
**Likely question.** *So it detects everything?*
**Answer.** "It detects what the suite represents. A violation the suite does not encode is
outside what we measured."
**Prohibited.** Never present the curated ratio as detector accuracy or as all-faults detection.
Do not quote the red-fixture ratio here — it is a different denominator and lives on A1.

### Slide 18 — How often does the check fire when nothing is wrong?  `L4.7`
**Purpose.** Establish the gate is calibrated before any real-data verdict is shown.
**Say.** On data built with no real dependence the gate still halts sometimes; the Wilson interval
contains the nominal α. The interval, not the point, is the claim. Markers are evaluated design
points; the line only guides the eye.
**Likely question.** *Is the gate better calibrated than nominal?*
**Answer.** "We claim consistency with nominal, not improvement on it."
**Prohibited.** Do not read PASS as validity — PASS means not rejected.

---

## ACT IV — evidence outside the synthetic fixtures

### Slide 19 — How much did a later update move the prediction?
**Purpose.** Define the observable on a picture before any verdict uses it. Assume no orbital
dynamics background at all — the slide never says "fit".
**Say.** Top panel: "an older published orbit estimate and a newer one. Both are asked about the
*same* future event." Bottom panel: "each says the event will happen at a slightly different place
along the orbit. The gap between those two predicted positions is the quantity — median about
two-tenths of a kilometre." Then, explicitly: "It is not error against a true orbit. Nothing here is
compared to truth." The formal name, *along-track update increment*, is in the corner; say it once.
**Likely question.** *So what does a large increment mean?*
**Answer.** "That the newer estimate disagreed with the older one about where the satellite would
be. It is a property of the catalogue's own revisions, which is exactly what an experiment consuming
those revisions is exposed to."
**Prohibited.** Never call the increment truth error. Do not say "orbital fit" — the slide
deliberately says "published orbit estimate". The cohort arithmetic is A4; quote it only if asked.

### Slide 20 — The downstream events are not independent  `L4.7`
**Purpose.** The empirical centre, with its scope attached.
**Say.** Lead with the words, not the numbers: "at every grouping we tested, the events are not
independent." Same parent, values still resemble each other. Then the three ρ values as support.
**Do not claim the gate discriminates the observable from geometry using this slide.** The elevation
card is a *ties signature*, not evidence of independence — a reviewer correctly objected that a
control the slide itself flags as degenerate cannot license a discriminant claim. What the three
HALTs license is exactly what the punch line now says: independence is rejected at every grouping
tested.
The elevation card is a control on what the rule can SAY, not on effect size: it is a ties
signature with the estimator truncating at zero, so it licenses only "the rule did not reject". Say
that p-value out loud — the control passed at exactly one, by ties rather than by evidence of
independence.
**Likely question.** *Why is the in-track ICC meaningful?*
**Answer.** "It is the intraclass correlation of an update increment between consecutive fits that
share most of their observation arc. It quantifies how much two passes under one element set
resemble each other — which is exactly the exchangeability assumption."
**Prohibited.** Do not say we found the correct unit, that all satellite data are dependent, that
the ICC is orbit prediction error, that elevation "shows none", or that the effect is
"observable-dependent" — a ties readout at the truncation boundary licenses none of those. Do not
call the three values a variance decomposition.

### Slide 21 — The unchanged contract on a frozen third-party artifact
**Purpose.** Show the contract runs unmodified outside its own project.
**Say.** Commit chosen before inspection; detector hash unchanged. Then read the bar: nineteen rules
partition into nine adjudicated and ten that returned no verdict. Be precise — three rule verdicts
and two applicability dispositions. N/OBS is never scored as compliance.
**Likely question.** *Why only one third-party artifact?*
**Answer.** "One artifact shows the contract is portable and that its verdicts are legible on code
nobody here wrote. It does not establish broad external generalisation, and we do not claim it."
**Prohibited.** Do not call the mirror publisher-verified; it is checksum concordance with two
independently published sources. Do not claim hashing proves correctness.

### Slide 22 — Did train and validation share the same samples?  `L4.1`
**Purpose.** Show a detected violation has a real decision consequence — and stop exactly there.
**Say.** Sliding windows share almost all their samples, so a shuffle-then-split contaminates the
early-stopping support. The correction changed only the partition. Selection changed in every
paired seed; the rerun is bit-identical. Then the limit: the downstream endpoint is not estimable
at this paired-run resolution.
**Likely question.** *Did the correction improve detection?*
**Answer.** "We do not claim that and the data could not support it. The metric moved in both
directions, and with this many paired seeds the smallest attainable two-sided p is above any
conventional threshold."
**Prohibited.** Never say accuracy improved, that the downstream result is null, or that the
upstream published paper is invalid.

### Slide 23 — Where this sits in a real experiment
**Purpose.** Answer the engineer's question: where does this go? Without this slide the verdict
reads as commentary rather than as something that runs.
**Say.** "You declare four things before running — decision time, freeze point, provenance manifest,
unit hierarchy. You run the experiment. The checker adjudicates. PASS lets you report the claim,
HALT stops the build, INDETERMINATE sends you back to redesign the design." Then: the verdict is a
build outcome, not a sentence in a paper.
**Likely question.** *What does this cost a team to adopt?*
**Answer.** "The declaration is the cost, and it is the part people already believe they have
written down. The checker itself is a numpy-only toolkit of under a thousand lines with no service
dependency."
**Prohibited.** Do not claim adoption experience — no team outside this work has run it in CI, and
this slide describes where it attaches, not a deployment study.

---

## ACT V — what is new, what is not, where this sits

### Slide 24 — Prior work supplies the primitives; we change what is tested
**Purpose.** Answer "has anyone done this before, and what did you change" on the main line rather
than in the appendix. Also pre-empts "old method plus a parameter change".
**Say.** Left column briskly — this is what practice already does, and none of it is claimed: a
chronological split checks rows inside one dataset; provenance logging records the declared inputs;
statistical aggregation picks a level. Then the middle: none of them asks what *second* thing would
falsify the validity assumption. Then the right column, which is the method. "Prior work supplies
the primitives. We change what must be tested."
**Likely question.** *What is publishable here beyond a software checker?*
**Answer.** "A checker enforces rules someone already stated. This supplies the step before that:
deciding which obligations are relational, and what comparison would falsify each one. The rules
are a consequence."
**Prohibited.** Do not claim any listed primitive as ours. Full attribution with references is A12.

### Slide 25 — What did we actually gain?
**Purpose.** Answer "so what" in one view. Every number here has already appeared with its context;
this slide only assembles them.
**Say.** Walk the six quickly — every tile carries its own scope line, so read the scope, not just
the number — then land the last line hard: "The benefit is not higher model accuracy. It is that an
invalid experiment cannot support a deployment claim."
**Likely question.** *Which single number would you defend hardest?*
**Answer.** "The five-of-five checkpoint change, because it is the one that shows a detected
violation altered a real decision rather than only a diagnostic — and it is selection changing, not
accuracy improving."
**Prohibited.** Do not present any of these as accuracy improvement, and do not add a number that is
not already on an earlier slide. The clean-path false-halt rate does **not** belong here: it is a
cost of the method, and an earlier draft of this slide wrongly filed it under gains.

### Slide 26 — What this does not establish
**Purpose.** Apply the paper's own discipline to itself. Read briskly; do not soften.
**Say.** Seven boundaries, then: a validity method must apply the same evidence discipline to its own
claims. The last card is the one to volunteer rather than defend — nothing in the method forces the
*finest* grouping, so a claimant could declare a coarse one; the rule adjudicates the grouping it is
handed and never chooses it.
**Likely question.** *Isn't this list a weakness?*
**Answer.** "It is the same standard the method imposes on the experiments it audits. A validity
paper that overclaimed would refute itself."
**Prohibited.** Do not hedge any item into something softer than it is.

### Slide 27 — What I need from you
**Purpose.** Convert the review into concrete guidance. **Never shown publicly.**
**Say.** Ask the three decisions and stop talking: venue and framing, L4.6 evidence depth,
anonymity policy. Name the honest rejection risk once — the communications contribution is indirect
and may read as software methodology.
**Likely question.** *What would make this main-conference quality?*
**Answer.** "Independent replication across faults and pipelines authored outside this work, and a
downstream endpoint with enough resolution to decide. Both need new experiments this submission
does not have."
**Prohibited.** Do not promise new experiments in the room. No experiment is planned unless the
advisor identifies a concrete blocking weakness.

---

## Appendix, if asked

A1 nineteen-rule map and the red-fixture ratio · A2 permutation reference · A3 attainability versus
power · A4 real-data denominators · A5 three clocks · A6 the third-party partition · A7 claim
binding · A8 limitations matrix · A9 neighbouring work · A10 the stopped research line, historical
motivation only · A11 why the obvious repairs do not close the gap · A12 references for the
borrowed primitives.

**A11 is the one to reach for** if the advisor proposes a fix: stricter splits, more single-run
assertions, richer logging and aggregate-first each fail for the same reason — one realised run
cannot supply the comparison.

---

## Anticipated questions — bounded answers

| # | Question | Bounded answer |
|---|---|---|
| 1 | Why is this a communications paper? | The obligations come from satellite operations in a form generic tooling lacks: two clocks, rows generated by predicted geometry, retrospective labels, repeated measures nesting inside an element set. That is where we found them and where they bite. |
| 2 | Why not just chronological split? | A split is a predicate over the rows of one realised dataset. Availability, membership, hidden state and unit choice each have a counterexample that exists only outside it. |
| 3 | Is L4.6 just metamorphic testing? | The relation is metamorphic; the target is not. It is applied to declared provenance, where tracking systems record parameters without testing behavioural completeness. |
| 4 | Is L4.7 just ICC? | ICC(1) and permutation inference are established and neither is proposed here. The novelty is calibrating a gate with an operating characteristic and an abstention state. |
| 5 | Did you swap the hard problem for an easier one? | Yes, deliberately, and slide 16 says so. Certification is not attainable from one realised run, so both checks relax it: a counterexample instead of a certificate, an abstention instead of a forced pass. The cost is that PASS cannot certify validity. |
| 6 | Why one coarser level? | Because that is the level the design declares. Testing further up requires a hierarchy the experiment did not assert, and the rule refuses to invent one. |
| 7 | Why not always use the satellite as the unit? | The rule adjudicates the level it is given, never which is right — and snapshot-to-satellite halts too. Element sets and deployment episodes cross-cut, so there is no unique next level. |
| 8 | Does PASS mean valid? | No. PASS means not rejected. Its value is as a regression guard: a represented violation, once fixed, cannot silently return in the form the suite injects. |
| 9 | Why is the in-track ICC meaningful? | It is the intraclass correlation of an update increment between consecutive fits sharing most of their observation arc — precisely the exchangeability assumption under test. No truth reference is involved. |
| 10 | Why is the analysis denominator smaller than the cohort? | An in-track increment needs two consecutive fits; passes without a successor element set cannot form one. A4 has the arithmetic. |
| 11 | Did the third-party model improve? | We do not claim that and the data could not support it. Selection changed in every paired seed; the downstream metric moved both directions and is not estimable at this resolution. |
| 12 | Why only one third-party artifact? | It shows the frozen contract is portable and its verdicts legible on outside code. It does not establish broad generalisation, and we do not claim it. |
| 13 | What does adoption cost? | The declaration, which teams already believe they have written down. The checker is a numpy-only toolkit of under a thousand lines with no service dependency. No team outside this work has run it in CI. |
| 14 | What makes this publishable beyond a software checker? | A checker enforces stated rules. This supplies the prior step: deciding which obligations are relational and what comparison falsifies each. The rules follow. |
| 15 | What would make it main-conference quality? | Independent replication across faults and pipelines authored elsewhere, plus a downstream endpoint with enough resolution to decide. Both need new experiments. |

## Never say

- "the manifest is complete" · "falsifies incompleteness" · "verifies completeness"
- "PASS means valid" · "we found the correct statistical unit"
- "the in-track increment is truth error" · "the ICC is orbit prediction error"
- "the ICC is a variance share" · "the three ICCs decompose the variance"
- "the downstream result is null" · "no effect" · "accuracy improved"
- "all faults are detected" · "the rules are complete"
- "the mirror was verified by the original publisher"
- "ICC or permutation inference is our new statistical method"
- "a team is using this in CI" — none is
- Anything presenting Doppler-residual learning, LR-FHSS, link budget, packet or RF performance as
  a contribution of this paper. That research line was stopped and its numbers are withdrawn; it
  appears only in appendix A10, labelled as historical motivation.

## Build and verify

```
make -C talk/advisor_review          # regenerate numbers, build the PDF
make -C talk/advisor_review check    # every gate, including stopped-research isolation
make -C talk/advisor_review render   # page images for a visual audit
```
