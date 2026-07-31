# Review ledger — final workshop-salvage loop

Reviewers dispatched in pairs, at most two concurrently. Every finding below was
**independently verified before being acted on**; where a reviewer's count differed from
mine, the reviewer's was checked against the source and adopted or corrected explicitly.

| reviewer | scope | verdict | BLOCKERs |
|---|---|---|---|
| R3F | experimental methodology, focused re-review | WEAK ACCEPT | none |
| R4F | artifact / reproducibility, focused re-review | WEAK ACCEPT | none |
| R5 | adversarial flagship-workshop reject advocate | pending | — |
| R6 | six-page camera-ready | pending | — |

## Convergence on the contribution

Both reviewers independently described the contribution as an executable
deployment-causality contract with a curated regression suite, and neither described it as
an internal bug report. That was the framing test from the previous round, and it passes:

- R3F: "An executable 19-rule deployment-causality contract that turns availability-clock,
  row-membership, hidden-state and statistical-unit assumptions of satellite communication
  experiments into per-commit CI checks."
- R4F: "A deployment-causality and falsifiability contract (19 executable rules over six
  protected objects) that catches leakage classes chronological splitting is not designed to
  detect, shipped as an 833-line numpy-only toolkit with a curated 17-class fault-injection
  regression suite and a build gate that mechanically ties every manuscript number to one
  artifact."

## BLOCKER

None from either reviewer.

## MAJOR — all resolved

### M1. The injection-level disclosure understated the weakness by 3–5× (R3F F1)

The single sentence whose job was to bound the evaluation said two mutated objects are
consumed only by their own detector. R3F traced every one; I verified against
`run_matrix.py:62–129` and `tests/fixtures/pipelines.py`. The fixtures are **check-scoped by
construction** — each rule receives its own input attribute — so only six of seventeen
mutated objects reach more than one consumer (schedule, closure and fold arrays also feed the
chronological baseline; `run_fn` feeds L3.1 and L3.2). Eleven reach only their own detector.

This was the most serious finding of the round, because under-reporting one's own weakness is
the same error as over-reporting one's strength, and it appeared in the sentence written to
prevent exactly that. **Resolved** — the threats section now states the measured count, names
the criterion, and says why the regression claim survives it. `commit 3899f63`.

### M2. L4.3 still ships the uncalibrated construction the paper criticises (R3F F2)

§III argues that a fixed threshold controls the null mean and not the tail, citing a measured
size of 0.17 at a fixed 0.2 — and `check_repeated_measures` still thresholds the same
estimator at a hardcoded `icc_warn=0.2`. I reproduced the size curve: **0.167** at eight
groups of three, 0.064 at twenty, **0.000** at the ninety-six the fixture happens to have. So
L4.3's clean pass is a property of the fixture, which is precisely the objection the paper
raises against its own predecessor rule. Its decision is additionally gated on a self-reported
`aggregated` flag.

**Resolved by disclosure, not repair**, and the reason is itself methodological: editing a
detector after its outcome is known is what voided L4.7's standing. Repairing L4.3 now would
void D11's the same way. Stated in the threats section with the measured numbers; the null
size is recorded in the artifact. `commits 3899f63`, `34740ce`.

### M3. No rule detects covariate-coupled label missingness (R3F F3)

Advertised in the threat model as "the harder failure", named as the third defect of case
study 1 and in the conclusion — with no rule, no fault class, and no entry in the gaps list.
Verified: `grep -rni "censor"` finds only the reference-ensemble diagnostic status, which by
design never drops a row. **Resolved** — the threats section now states plainly that the
contract has no missingness rule and that the defect was found by inspection rather than by a
check, and the conclusion no longer implies detection. `commit 3899f63`.

### M4. Semantic residue of the withdrawn claim (R3F F4)

"drawn from the defects that motivated the rules **plus several written for propositions no
predecessor detector covered**" restates the pre-registration's own definition of *held out* in
words the banlist does not match, and contradicts the threats section's "only one". The same
sentence also claimed the suite is "one per violation the contract names", contradicted two
sentences later. **Resolved** — both clauses deleted. `commit 3899f63`.

### M5. Claim gate defeatable three ways (R4F, three MAJORs)

R4F defeated the gate without touching a detector. For a paper whose contribution *is*
mechanical enforcement, this was the most consequential finding of the round.

| hole | how it was defeated | fix |
|---|---|---|
| negation bypass | `We do not overstate this: the contract generalises to unseen faults.` passed — only `.` `;` and a blank line counted as clause boundaries, and a negation up to 120 chars back was accepted | boundaries now include `:` `,` and em-dash; negation must be within 60 chars |
| unguarded counts | `\b19\b\|nineteen` and `\b16\b\|[Ss]ixteen` are always satisfied by the prose, so those artifact values could drift freely | spelled forms derived from the artifact; bare digit dropped (it matched TikZ coordinates and a BibTeX `number = {12}`) |
| unscanned surface | `README.md` and `paper/submission/*.md` were never scanned — including the file advertising the gate, and CLAIMS.md | 11 files scanned; exemptions printed with reasons rather than applied silently |

Verified with ten attacks (plain claim, negation bypass, comma bypass, four artifact drifts,
plants in README and CLAIMS.md, a banned legacy result). Three previously passed; all ten now
fire. `commit e8fff4b`.

### M6. `matrix_sha256` was permanently unmatchable, and its divergence was hidden (R4F)

`compare_summaries.py` promised excluded fields are "reported separately rather than silently
ignored", then dropped `matrix_sha256` and `commit` from the report — the same
docstring-versus-implementation divergence that got `build_label` flagged, relocated into the
reproducibility checker. And the checksum could never match: it hashed `matrix_result.json`
whole, which embeds per-row `runtime_s`. **Resolved** — hash taken over the canonical
timing-stripped result; `commit` moved into the compared set. `make gate-twice` now reports 25
fields identical *including* both. `commit 34740ce`.

### M7. Scheduler: provenance claimed but not implemented; one parameter fixed, its siblings not (R4F)

`PassFinderConfig` asserted its solver settings "belong in the provenance manifest" and no code
emitted them. Separately, `coarse_step_s` was declared and swept while `bisect_tol_s` and
`bisect_max_iter` — which move the same quantity — had no declared range and no test: the
instance was fixed, the defect class was not. **Resolved** — `provenance()` implemented with a
test asserting field completeness and that a solver change moves the manifest hash; convergence
test extended to sweep all three settings; `coarse_step_s <= 0` rejected. The residual
dependence of row membership on `bisect_tol_s` (the `min_pass_s` filter tests a conservative
under-estimate) is **disclosed in the docstring** rather than repaired, because fixing it would
change a published schedule. `commit 125ec7d`.

## MINOR — all resolved

| id | finding | resolution |
|---|---|---|
| R3F F5 | "the one class" ordering catches; artifact says two (D5, D13) | "one of the two", body and Fig. 1 caption |
| R3F F6 | 450 paths are Case-B-only, L4.7-only, never described as such | now "450 clean evaluations of this rule alone (150 seeds × 3 environments)" |
| R3F F7 | 0.042 quoted without uncertainty, inviting "better than nominal" | now 19/450 with Wilson interval [0.027, 0.066], "consistent with, not better than" |
| R3F F8 | the 0.17 null size had no artifact field | `l47_calibration.discarded_fixed_threshold_null_size`, reproduced by `calibrate_l47.py` |
| R3F F9 | L4.7's abstention exercised by no condition or test | stated as implemented but unexercised |
| R3F F10 | fixtures share names with case studies; no artifact for the case studies | ARTIFACTS.md states they are not independent evidence |
| R3F F12 | line referencing a "qualification" the reader never hears about; 30 ms overstates 26.8 | line deleted; 27 ms |
| R4F | `latex_errors` invariant never fired (`-file-line-error` drops the `! ` prefix) | regex matches both forms |
| R4F | `COMPLETE` conflated checked / unchecked / non-finite; NaN stamped COMPLETE | `INVALID_SOURCE_METADATA` for non-finite, `UNCLASSIFIED_NO_CEILING` for no ceiling, `member_ids` validated |
| R4F | `coarse_step_s <= 0` unguarded (zero divides, negative builds a descending grid) | rejected at construction |
| R4F | `test_suite_loc` excluded the fault-injection suite while the test count included it | both cover the active suite; `test_count` now in the artifact |
| R4F | ARTIFACTS.md claimed 23 and 27 tests, outside the gate's glob | states no counts; glob extended |
| R4F | ASSET_MANIFEST.md presented `salvage/` paths as current, LOC drifted up to 91 lines | repointed at `src/orbit_evidence/**`, authority delegated to the artifact |
| R4F | root README had no install command; `uv.lock` undocumented | `pip install -e '.[test]'` added; uv.lock labelled as the archived stack |

## DISAGREEMENT

**Injection-level count.** R3F reported 11 of 17 single-consumer objects on its primary
criterion and 7 on a stricter "hand-built inputs only" reading. I verified the architecture is
check-scoped and adopted **11**, with the six multi-consumer cases named, because that is the
count a reader can reproduce from `run_matrix.py`. R3F's stricter figure of 7 is defensible but
depends on a judgement about which pipeline computations count as real.

## REJECTED_FINDING

**R4F's characterisation of the runtime bound as possibly "evasive."** R4F itself measured ten
runs spanning 1.382–1.504 s against a stated bound of 2 s and concluded the bound is honest. No
change; recording it because the question was asked and answered against the concern.

## Notes on process

- Three commits landed *during* R4F's review, so it re-verified its findings against the moved
  HEAD and said so. Its ARTIFACTS.md finding was already being fixed as it wrote.
- The manuscript's R3F prose fixes were committed inside `3899f63`, which is labelled `docs:`.
  That mislabels 241 lines of manuscript change. History is not rewritten, so it is recorded
  here rather than hidden.

---

# Novelty-rebalance cycle — R-N1 to R-N4

Four fresh reviewers, none from any earlier loop. R-N1 and R-N2 read the implementation;
R-N3 and R-N4 received only the PDF and the artifact summary a real reviewer would get.

| reviewer | scope | verdict | N | S | T | E | C |
|---|---|---|---|---|---|---|---|
| R-N1 | novelty and positioning, code-reading | WEAK ACCEPT | 2 | 3 | 3 | 4 | 3 |
| R-N2 | statistics and experimental methodology | WEAK ACCEPT | 3 | 3 | 4 | 2 | 4 |
| R-N3 | satellite / NTN | **WEAK REJECT** | 2.5 | 2.5 | 3.5 | 2 | 3 |
| R-N4 | flagship-workshop reject advocate | **WEAK REJECT** | 2 | 2 | 4 | 2 | 3 |

R-N3 also scored venue fit 2.5. Both saw only the PDF and the artifact summary.

**The internal-debugging-report question split.** R-N3 answered **NO** ("Sections I-A, I-C and
II are roughly two and a half pages of transferable formulation with an explicit prior-art
delta, and a reader with no knowledge of the authors' programme can take the protected-object
decomposition, the relational-versus-predicate distinction, and the three-valued unit gate and
use them"). R-N4 answered **YES**, on the grounds that the *claim* is field-directed while the
*support* is entirely internal. That is the first time this question has drawn a NO.

## R-N2 verified the core statistics line by line and found them correct

Worth recording because it is the load-bearing part of the paper and it was checked rather
than trusted. R-N2 reproduced both headline numbers from a clean `git archive HEAD`, and
independently confirmed:

- ICC(1) from variance components is correctly derived; the null expectation is 0 at every
  group size; truncation at 0 is conservative (a point mass at p = 1 in 53.6% of clean
  replicates, never a manufactured rejection);
- repeated in-place `rng.shuffle` *looks* like a random walk over permutations but is not —
  composing a fresh uniform permutation onto any prior arrangement is uniform and
  independent of the history, so the B draws are i.i.d.;
- the finite-B p-value is exactly valid: attainable size at B = 400, alpha = 0.05 is
  20/401 = 0.04988;
- the whole lower tail is calibrated, not just the reported point:
  P(p ≤ alpha) = 0.0067, 0.0244, 0.0422, 0.0800, 0.1822 at alpha = 0.010, 0.025, 0.050,
  0.100, 0.200 — uniformly mildly conservative;
- the 450 replicates are **not** pseudoreplicated: per-seed halt counts [136, 14, 0, 0]
  against Binom(3, p) expectation [136.4, 13.1, 0.4, 0.0], and the ICC of the halt indicator
  grouped by seed is 0.0, so the Wilson interval's independence assumption holds;
- Wilson (uncorrected) for 19/450 is [0.0272, 0.0650], matching what the paper quoted.

## The most serious finding: neither headline error rate was inside the gate

Verified and reproduced. `make_final_summary.py` carried the calibration as hand-typed
literals, so `check_banlist.py` compared the manuscript against a transcription. R-N2
observed the consequence live: an uncommitted edit rederiving the permutation stream moved
the measured false-halt rate from 19/450 = 0.042 to 14/450 = 0.031, and `make gate` still
reported `SUBMISSION GATE: PASS` with 0.042.

That edit was mine, made earlier in this same cycle to fix a platform-dependent seed. So the
defect and its demonstration both belong to this cycle.

**Worse than reported.** Fixing the transcription was not sufficient. The gate's binding was
required-*presence*: it asked whether the artifact's value appeared anywhere in the sources.
Two independent bypasses, both confirmed by direct attack after the artifact was bound:

1. the count 17 was satisfied by the seventeen fault classes, whatever the field had drifted
   to;
2. with the artifact carrying 0.038, the check *still passed* — Fig. 2 contains the ICC
   coordinate `(0.038,0.05)`.

Required-presence also cannot express the opposite direction at all: a correct artifact and
a wrong manuscript. Replaced with `\artv{key}{rendered}` claim sites and per-claim agreement.
Eleven attacks now fire, four of which the previous gate accepted.

**Consequence for the paper.** The 19/450 = 0.042, its Wilson interval, and Fig. 2's power
points were all stale. Corrected everywhere to 14/450 = 0.031, Wilson [0.018, 0.052]. Both
values lie inside the interval and both are at or below nominal 0.05, so no conclusion moved
— but the paper now claims the interval, and `CLAIMS.md` records the count as
implementation-conditional.

## R-N2's other confirmed findings

| finding | status |
|---|---|
| §II specified the 1-alpha quantile rule the code explicitly discards, and never named the +1/(B+1) correction | fixed — the required camera-ready item |
| Fig. 2 plotted at x = 5·ICC while ticking in ICC: "0.5" at ICC 0.4, "0.8" at ICC 0.6; curve ran past its axis; `\clip` issued after `\draw`; the headline ICC 0.8 point had no marker | fixed — the second required item; x is now ICC itself |
| "estimator and reference distribution are both load-bearing" is wrong for size — under the permutation null the two estimators are monotone transforms and give identical p-values | fixed |
| the abstention floor counted labelled coarser groups; `within_group_icc` drops groups with fewer than 2 members, so 4 labels including 2 singletons cleared a floor of 4 and reported `n_coarser_groups: 4` on an ICC estimated from 2 | fixed, with a regression test on the reviewer's exact case |
| `coarse_of.setdefault` silently accepted a unit assigned to two coarser groups | now raises, with a test |
| exchangeability named but its failure modes not: unequal replicate counts per unit, heteroscedastic coarser groups — both inflate size with no unit error present, both surface as the same misdiagnosis, neither can appear in the balanced fixture | documented in the docstring |
| the floor is a power precondition, not a validity one — the test is size-valid at k = 2 | corrected in §II |
| §VI implied the six multi-consumer faults catch a defect in a working pipeline; in all six the second consumer is another check, never a reported number | fixed |
| `CLAIMS.md` named runtime as the only non-bit-reproducible figure | fixed — the false-halt count is implementation-conditional |
| "measured rather than assumed" overstates what was measured: the clean fixture satisfies the permutation null by construction, so the measurement checks the implementation | Fig. 2 caption and §II both rewritten |
| power is n = 40 per point, one synthetic Gaussian design, no intervals, while the size point carries a Wilson interval in the same figure | disclosed in the caption ("one synthetic design", "each over 40 seeds"); intervals on the power points would need page budget the six-page limit does not have |
| `m̄ = n/k` is the plain mean, not the standard unbalanced `m₀` | harmless for the decision (any permutation-invariant statistic gives a valid test); the balance caveat is in the code comment |
| the fixture's injected point sits at ICC ≈ 0.956, not the ≈ 0.8 the artifact note claimed | the paper's claim is that 150/150 is saturated, which is if anything understated; noted here rather than adding a number to the manuscript |

## Declined, with reasons

**L4.3 should be wired to the permutation null 60 lines below it (R-N2 §5).** R-N2 is right
that the repair is small and that a gate halting one correct design in six will be switched
off. Declined under the explicit governing instruction for this cycle: *"Do not repair it
now. Repairing it after seeing its behaviour would open another detector-design cycle."*
L4.3 is classified as a cheap self-reported guard, its 0.17 null size is disclosed in the
manuscript and in Table I's caption, and L4.7 is the calibrated decision. This is a deferral
on process grounds, not a disagreement on the statistics.

**Reporting the full lower tail (five alpha levels) instead of the single 0.042.** R-N2 is
right that it is stronger evidence. It would need regenerating under the current seeding and
would cost prose in a paper already at exactly six pages. Not done; the measured tail is
recorded above so it is not lost.

**Adding size under mild exchangeability violations, or a second (k, m̄).** This is new
measurement, forbidden this cycle. The gap is now stated in the manuscript rather than left
for a reader to find.


## R-N3 (satellite / NTN) — confirmed findings

Verified independently before acting. R-N3 also checked the orbital content and found the
sharp parts correct: the two-clock semantics and the `CREATION_DATE` field name against CCSDS
502.0-B and Space-Track GP; predicted- versus truth-visible sampling ("the paper gets the
subtle version right"); the along-track argument for the element set as exchangeable unit
("orbital physics doing real statistical work"); state surviving a nominal freeze; and every
reference real and correctly attributed, with no citation padding. It recomputed the Wilson
interval and confirmed [0.018, 0.052] as a conservative rendering of [0.0186, 0.0515].

| finding | status |
|---|---|
| `CREATION_DATE` is a lower bound on retrievability, not the publication time; batch publication and reprocessing add unmeasured lag, so L1 has **one-sided error** | fixed — named in the limitations. The most consequential of the four, because it is the instrument for the paper's first protected object |
| the 27.6% epoch-ahead figure is a **unit error by the paper's own §I-A(v)**: pooled over records across eleven objects with unequal counts | fixed, and it changed the paper in our favour — see the commit. Per object the figure is 0 in ten of eleven; the object-level median lag is 6.36 h against the pooled 1.68 h |
| L4.7 presumes a unique next coarser level; element sets and deployment episodes cross-cut rather than nest, and the paper never said what happens then | fixed |
| the space-weather level is absent entirely — drag driven by solar and geomagnetic activity is common-mode across every object and element set in an interval, and the words drag, B*, F10.7, Ap appear nowhere | fixed in prose |
| the 27.6% anomaly is undiagnosed | left undiagnosed and now reported per object; diagnosing it would need the ingest pipeline, which is not in scope |
| swap test: **~2 of 9 obligations are genuinely satellite-load-bearing** (v fully, iii and L4.7's level choice partially); 7 of 9 are domain-neutral with satellite examples | consistent with R-SA3's earlier ~2 of 19 by a different accounting. The paper's weaker in-text claim (the domain gives each object an *operational meaning*) is what we retain; we did not write the stronger one |
| 16 of 20 references are software engineering or statistics | recorded, not changed — it is an accurate reflection of where the prior art is, and the paper says so |

**Declined: retire L2.2, L2.3, L4.5 and ship sixteen rules.** R-N3 is right that by our own
stated standard three shipped rules are untrusted, and right that this is the most visible
self-inconsistency. Declined because the governing constraint for this cycle forbids modifying
the evaluation denominators, and 19 → 16 moves every one of them. The gap is disclosed in the
abstract-adjacent text, in Table I's caption, in §VI and in the artifact
(`detectors_without_red_fixture`).

**Declined: run L4.7 on the eleven-object dataset and report measured ICC.** This is R-N3's
single best suggestion and I want to record that plainly — it uses data already committed and
would tell a reader whether the rule's blind zone below ICC 0.1 is even relevant to the
flagship use case. It is a new measurement, which this cycle forbids. Recorded as the first
thing to do next.

**Declined: one link-layer rule, or a link-budget scope statement.** The paper already states
that no radio-frequency or packet-level result is established. A new rule is a new detector
family, forbidden.

## R-N4 (reject advocate) — confirmed findings

R-N4 found no overclaim and no substantive inconsistency: it reconciled every headline number
in the PDF against the artifact summary independently, including Table I summing to 19 rules
and 16 red fixtures with the missing entries matching L2.2, L2.3 and L4.5 exactly. Three
findings stood.

| finding | status |
|---|---|
| "six probed channels" enumerated as **five** in two places, omitting the feature tensor, while three other sites assert six | fixed — `STATE_CHANNELS` has six entries |
| the nineteen rules are **not enumerable from the submission**: Table I is a four-row aggregate and only ~14 identifiers appear in the text; L1.2, L2.1, L2.4, L4.1 never defined | fixed — the rule column carries ID ranges. This was a regression introduced by compressing Table I earlier in this same cycle |
| the abstract kept the flattering power point (1.00 at ICC 0.8) and omitted 0.25 at 0.2 | fixed |

R-N4's arithmetic on the novelty claim is worth recording because it is the sharpest version
of the criticism: the relational class covers **5 of 19 rules**, every member has a conceded
antecedent, and what survives subtraction is a taxonomy, the INDETERMINATE outcome, and the
two-clock observation — of which it grants only INDETERMINATE as genuinely absent from the
cited literature. It is one sentence long and it is real.

## Why the loop stops here

Both reject verdicts turn on the same thing, and it is the one thing this cycle forbids:

- R-N3: "One revision cycle adding a third-party artifact study and L4.7 results on the
  eleven-object dataset would move this to ACCEPT, and I would want to see it again."
- R-N4: "Run the contract, unmodified, against at least one pipeline the authors did not
  write... **Yes, this requires new experiments.**"

Neither asked for a reframing. Across eight reviewers over three cycles the request has been
identical and unchanging: contact with an artifact the authors did not produce. Presentation
work cannot supply it, and the standing instruction for every cycle has been that new
scientific experiments are out of scope.
