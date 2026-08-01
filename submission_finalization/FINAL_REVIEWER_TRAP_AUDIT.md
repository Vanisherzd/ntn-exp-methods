# Final reviewer-trap and claim-consistency audit

One correction cycle plus one verification cycle, against baseline
`paper/orbit-evidence-workshop-final-candidate-2026-08` (tag `4384e24`, commit `13ea573`).
No new experiment, dataset, training run, detector change, statistical redesign, fault, or claim.

## 0. Baseline inventory

| | baseline `13ea573` | after this audit |
|---|---|---|
| `paper/icc_main.pdf` | `ca87420b8486a335…` | `a0ba53b6a44c2f38…` |
| `paper/icc_main.tex` | `18ca49955437d768…` | `4295b9c60c2647a4…` |
| **detector** `contract_layers.py` | `07baad27026ebc22…` | `07baad27026ebc22…` **unchanged** |
| named claim sites | 38 | **41** |
| evidence artifacts (6) | — | **all byte-identical** |
| `matrix_sha256` | — | **identical** |

The six evidence artifacts held byte-identical: `l47_alongtrack.json`, `l47_real_application.json`,
`paired.json`, `mechanical.json`, `l47_power_curve.json`, `l47_calibration.json`. The only
non-volatile `final_summary.json` fields that differ are the five **new** count-ledger fields; no
pre-existing field changed value.

## 1–2. Abstract and Conclusion entailment

| clause | supported exactly? | action |
|---|---|---|
| "test whether declared provenance is behaviourally complete" | **no** — L4.6 refutes, never certifies | → "make provenance incompleteness differentially falsifiable" |
| "whether the chosen statistical unit remains exchangeable" | **no** — PASS means not rejected | → "test for residual dependence at the next coarser physical level" |
| "false-halt rate of 0.031 against a nominal 0.05" | point only; body says the interval is the claim | → adds Wilson `[0.018,0.052]`, "consistent with … rather than better" |
| "detects substantial within-group dependence" | **no** — true of one observable; elevation gave `ρ̂=0.000` | → "a fit-update observable shows within-group dependence and a geometric one shows none" |
| "downstream endpoint remains statistically unresolved" | inconsistent with three other terms | → one term, *not observable*, everywhere |
| **"Both fire on real orbital structure"** | **BLOCKER** | see below |

**The Conclusion blocker.** `Both` = L4.6 + L4.7. L4.6 never ran on orbital data: neither
`l47_real_application.json` nor `l47_alongtrack.json` contains the string `L4.6`, and L4.6 is not
among the third-party halts (`L2.4`, `L4.1`, `L4.5`). Corrected to *"The unit gate fires on real
orbital structure, and the contract containing both operates unchanged on a frozen third-party
artifact."*

## 3. Terminology ledger — verdict versus disposition

A **rule verdict** is what a rule returns once its obligation applies: `PASS` / `HALT` /
`INDETERMINATE`. An **audit disposition** precedes any verdict: `NOT APPLICABLE` (the obligation
does not arise) and `NOT OBSERVABLE` (it arises but the artifact does not expose enough, **or the
design cannot attain the nominal level** — clause widened this cycle so one term covers the
downstream endpoint).

- Table II no longer says "five-valued decisions"; it records "three rule verdicts and two
  applicability dispositions".
- §III said "The contract is therefore three-valued" — true of `L4.7` only. Now "The rule".
- Four competing terms for the downstream endpoint (*unresolved*, *indeterminate*, *not
  observable*, *undecidable*) reduced to one: **not observable**, matching the frozen artifact's
  own `outcome_label`.

## 4. Count ledger — machine-readable and gate-verified

The manuscript said "six protected objects" while §II-A enumerated five. Neither reviewers nor the
gate could tell which was wrong. Resolved from the **frozen detector**, not by choosing a number:
`Rule.protected_object` over the six directly-enforcing rules gives six distinct objects.

| protected object | enforcing rule |
|---|---|
| feature availability | `L1.1` |
| availability clock | `L1.2` |
| label closure | `L1.3` |
| row membership | `L1.4` |
| state channels | `L3.1` |
| statistical unit | `L4.7` |

Six rules, six objects. §II-A named only five because the *availability clock* was folded into the
feature-availability sentence; it is now named. `make_final_summary.py` derives
`protected_object_count`, `protected_objects`, `direct_enforcing_rules`, `state_channels` and
`state_channel_count` from the detector and raises if a named rule is absent from it; both counts
are now `\artv` sites, so a prose count that drifts fails the gate.

Contribution 2 listed "predicted visibility" as a protected object and silently omitted the
statistical unit — the object carrying one of the two central checks. Predicted visibility is a
`L2` *support* obligation (Table I). Corrected.

## 5. Figure and table semantics

- **Table I** listed `HALT / LABEL` as `L2`'s decision. No `LABEL` outcome exists in the detector:
  `v['label']` at `contract_layers.py:197` is a descriptive word inside an `L2.2` halt message. A
  fourth decision value contradicted the paper's three-valued semantics. Removed.
- **Table I** used `core / support / mixed` with no definition anywhere in the paper. Defined in
  the table note.
- **Table II** now states the verdict, not the raw `3/5 → 4/5`; the observable is named
  ("in-track update increment").
- **Fig. 2** caption said the plateau approaches "the false-halt rate" (0.031, a 450-evaluation
  quantity) when it sits at the nominal level (0.05, a 40-seed quantity). Corrected.
- **Fig. 1** re-checked: L1.3 is the ordering-catchable contrast (blue), L1.1/L1.4/L3.1 are
  chronologically consistent, observation connectors imply no exclusive ownership, `PASS`/`HALT`/
  `INDETERMINATE` are rule verdicts. No change needed.

## 6. Statistical language

**Directly refuted by simulation.** The manuscript claimed the estimator has "expectation 0 under
independence at every group size". The implemented statistic truncates negative estimates to zero
(`experiment_contract.py:256`), so under independence:

| design | mean `ρ̂` | fraction at exactly 0 |
|---|---|---|
| k=8, m=3 | **+0.079** | 0.53 |
| k=20, m=3 | +0.051 | 0.52 |
| k=90, m=3 | +0.024 | 0.50 |

Expectation 0 holds for the **numerator**, not the truncated ratio. No result changes — the
decision runs on the permutation null, which uses the same truncated statistic on both sides — so
this is a wording correction. It also removed a self-contradiction with §V's "the estimator
truncating at zero".

Other statistical corrections: "Failures are then proofs" was false for `L4.7`, whose halt is a
rejection at a measured 3.1 % false-halt rate; `INDETERMINATE` was re-described as "underpowered"
three sentences after the paper correctly calls the floor an *attainability* precondition; the
abstention floor's second clause (eight units) was missing from the body; `exact for any B` → `valid
for any B`; `0.0095` attributed to its exhaustive-enumeration basis.

**Answers to the five questions.** (1) No sentence implies acceptance of the null. (2) No sentence
implies the test proves exchangeability — the error ran the other way and is fixed. (3) No sentence
treats absence of detection as evidence of validity. (4) Every bound is on the correct side; the
along-track HALT quotes the **lower** bound 0.376, and the gate records why the upper bound is
deliberately not required. (5) After the pass-accounting fix, every p-value and bound is tied to
the analysis its sentence describes.

**Two reviewer findings rejected on evidence.**

- *Claim: the Wilson interval treats 450 correlated evaluations as 450 independent trials, because
  the three environments share one seed's data.* **False here.** `build_case_b` draws from
  `env.rng(seed)`, and different bit-generator families produce different streams: at seed
  20260731 the three environments give `ρ̂` = 0.3413 / 0.2882 / 0.1604. The 450 are 450 distinct
  datasets. (The reviewer generalised §IV's "bit-identical across environments for fourteen
  classes", which is about the fault matrix, not this fixture.)
- *Claim: `0.0095` is unattainable under a B=400 sampled reference (severity MAJOR).* **Overstated.**
  Simulated on maximally grouped data over four groups of two, the sampled reference attains a
  median p of 0.00998 and reaches ≤0.0095 in 30 % of trials. Attainability is properly an
  exhaustive-enumeration property — the same frame the paper uses for `1/15` — so this is a
  one-clause attribution fix, not a defect. Downgraded to MINOR and applied as such.

## 7. Satellite-domain precision

**The sharpest finding of the cycle.** §I-A(iv) asserted "the exchangeable unit is usually the
element set, not the pass — §V measures this", pointing forward at evidence that **contradicts it**:
`D3_elementset_in_object` **HALTS** at `ρ̂ = 0.284`, `p = 0.0025`, one-sided lower bound 0.124. Element
sets within an object are not exchangeable either. Rewritten to claim only that the pass is too fine
when the observable carries the fit signature, and §V now states that no level tested there is
exchangeable.

Also corrected: `CREATION_DATE` is described at **first use** as a message-creation stamp and an
optimistic lower bound on retrievability, not as publication time (the caveat previously appeared
300 lines later); the along-track increment now names its common evaluation instant (both fits
propagated to the pass midpoint), without which the quantity is not well posed; the headline result
names its observable where it is first reported, and its 90-element-set denominator; "the link is
predicted visible" → "the geometry is predicted above an elevation mask", since a 10° mask is
geometric and the paper claims no RF result; the elevation argument was **backwards** — a
deterministic function of the grouping would give `ρ̂ → 1`, not the measured 0.000 — and now reads
"near-invariant to which element set propagated a pass"; median 0.22 → 0.226.

Verified clean: update-increment framing, manoeuvre tail disclosure, cross-cutting hierarchies,
per-object lag reporting, element-set republication collapse, and the absence of any RF, link,
packet or propagator-accuracy claim.

## 8. External-artifact claims

Verified present and correctly scoped: repository frozen before inspection; detector frozen and
hash-asserted; mechanical HALT; pre-registered intervention; deterministic selection consequence;
downstream endpoint not observable. Verified absent: any claim that telemanom's result is invalid,
that detection improved, or that `NOT OBSERVABLE` means non-compliant.

Two uncited population claims removed: *"the practice is common in this literature"* (deleted) and
*"would fire on most research repositories"* (→ "provenance obligations research code is not
generally written to satisfy"). One repository was audited; nothing here samples a population.

## 9. Runtime and build dependency

**Build-order defect, fixed.** `gate: test matrix claims verify` ran `test` — which executes the
claim gate against the committed tree — **before** `matrix` regenerated the artifact it reads. On a
loaded machine this produced a state no re-run could clear: the stale runtime failed the gate, and
re-running failed at step 1 before `matrix` could refresh it. This cost a real debugging cycle
during the previous session. Now `gate: matrix test claims verify`, with the failure recorded in the
Makefile comment and in `docs/REPRODUCIBILITY.md`.

**Runtime claim narrowed.** "under 3 s on one laptop core, under 60 ms per condition **on an
otherwise loaded machine**" was a portable worst-case claim, and a loaded machine measured
3.537 s / 65.5 ms — the manuscript's own claim, falsified. Now: "completes inside the repository's
3 s and 60 ms-per-condition regression guards — thresholds for one environment, not portable
guarantees". `README.md`, `paper/submission/README.md` and `docs/REPRODUCIBILITY.md` were carrying
the withdrawn claim and a falsified 1.39–1.55 s envelope; all corrected. Thresholds themselves
**unchanged**, as instructed.

## 10. Citations

`ccsds502omm` and `spacetrackgp` define the `CREATION_DATE` field; they do not support an empirical
lag distribution. "They typically differ by hours with a tail to days" is now bound to our own
object-level median of 6.36 h. `bergmeir2012crossval`, `just2014mutants`, `jia2011mutation`,
`hurlbert1984pseudoreplication`, `winkler2014permutation`, `mokhov2018buildsystems` and
`cawley2010selection` each support the exact proposition attached to them. No citation added for
topical adjacency.

## 11. Logical asymmetry

Both directions were already stated for `L4.6` (§I contribution 1, §III, §VI) and for `L4.7`
(three-valued paragraph). The **abstract** was where the asymmetry was lost, and it is the fix in
§1 above. The `L4.1` intervention already claims only what it establishes.

## Findings by severity

**BLOCKER (4, all fixed).** Conclusion subject claims L4.6 fired on orbital data; "Failures are then
proofs" false for a test with a measured false-halt rate; pass accounting contradicted the artifact
(`331 = 272 + 59 + 0`, stated as if 272 were pre-drop); §I-A(iv) claimed the element set is the
exchangeable unit against the paper's own D3 halt.

**BLOCKER, artifact (2, fixed).** `README.md` and `paper/submission/README.md` published the
**stale** false-halt rate `0.042` — the pre-correction value the project's own `CLAIMS.md` names as
a caught defect and the test suite plants as a drift — while the artifact says `0.031`. Markdown was
inside the banlist scan but outside `\artv` binding, so nothing caught it; a `W7` withdrawn-claim
pattern now does. And `real_pass` / `real_halt` were bound **only** in
`tables/external_validation_MERGED.tex`, a file `icc_main.tex` does not `\input`: the gate reported
two numbers as bound while they appeared nowhere in the six pages. The artifact-site check now reads
only files the document actually includes, and both numbers are bound at the live §V sentence.

**MAJOR (18, fixed).** Listed under sections 1–10 above.

**MINOR (11, fixed).** `exact` → `valid for any B`; `0.22` → `0.226`; abstention floor's second
clause; `L4.3`'s one-in-six qualified to eight groups; "the fault space" → "the curated suite";
"cannot silently return" → "do not … in the form the suite injects"; "its environments" →
"the curated environments" (referential slip inflating the external study); point estimate → interval
in §IV; the `0.51` multiplicity denominator made reconstructable (eleven per object plus three
pooled); `at_icc_d2` bound; "are not exchangeable" → "exchangeability … is rejected".

**REJECTED AS NOT AN ISSUE (2).** The Wilson-independence objection and the `0.0095`-attribution
severity, both refuted by direct measurement above.

## Unresolved, requiring evidence this cycle forbids

1. **Three counts remain unbindable**: "bit-identical across environments for fourteen classes"
   (the justification for reporting 17 computations rather than 51), "eleven of the seventeen
   mutated objects", and Fig. 2's "each over 40 seeds". No artifact field carries them. Binding them
   needs new fields in `matrix_result.json` and `l47_power_curve.json`, i.e. regenerating evidence.
2. **The third-party study's input data came from a mirror**, and the manuscript does not say so.
   `data_gate.json` records `matches_two_independent_lfs_oids: true` — mirror concordance, not
   verification against the original publisher. Disclosing this in the six pages costs space the
   page budget does not have; it is recorded in `DATA_PROVENANCE.md` and
   `FINAL_SUBMISSION_MANIFEST.md`. **This is the most likely remaining reviewer objection.**
3. **The consequence experiment has no reproduction path**: `external_consequence.py` has no Make
   target and needs the mirror data plus a multi-hour training loop.
4. **A loaded machine still cannot build the PDF.** The runtime check is a hard failure inside
   `check_banlist.py`, which is a prerequisite of the PDF target. Converting it to a warning would
   loosen the gate, which this cycle forbids, so it is recorded rather than changed. The build-order
   fix removes the unrecoverable variant of this trap; the plain failure remains.

## Cross-version diff classification versus `4384e24`

| class | count |
|---|---|
| CLAIM NARROWING | 14 |
| TERMINOLOGY CONSISTENCY | 7 |
| COUNT CORRECTION | 5 |
| CITATION CORRECTION | 1 |
| ARTIFACT CONSISTENCY | 6 |
| BUILD DEPENDENCY FIX | 1 |
| TYPOGRAPHY / COMPRESSION | 21 |
| **CLAIM EXPANSION** | **0** |
| **NEW EVIDENCE** | **0** |
| **DETECTOR CHANGE** | **0** |
| **STATISTICAL CHANGE** | **0** |

The 21 compression edits exist because the corrections were net-additive and the paper must hold
six pages. Each removes wording, never a claim, and several remove genuine duplication the audit
surfaced (`L4.3`'s null size stated twice, the abstention-on-third-party fact stated twice, the
`CREATION_DATE` lower bound and the 6.36 h median each stated twice).

## Final gate

| requirement | result |
|---|---|
| pages | **6** |
| tests | **61 passed, 1 skipped** |
| LaTeX errors | **0** |
| undefined refs / cites | **0 / 0** |
| overfull boxes | **0 hbox, 0.0 pt vbox** |
| minimum author-set glyph | **≥ 6.4 pt** (22 class-set spans at 5.98 / 6.38 pt) |
| banlist | **clean** — 11 banned + 18 withdrawn patterns |
| named numeric claims bound | **41** |
| detector | **byte-identical** |
| evidence artifacts | **all six byte-identical** |
| `matrix_sha256` | **stable** |
| `gate-twice` | **PASS TWICE**, 36 fields identical |
| stale artifact consumed before regeneration | **no** — `matrix` now runs first |
