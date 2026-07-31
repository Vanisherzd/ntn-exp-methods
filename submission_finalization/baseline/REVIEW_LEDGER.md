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
