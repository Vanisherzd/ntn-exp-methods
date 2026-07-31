# Strong-accept gap analysis

Four fresh reviewers, none of whom participated in earlier review loops. Each received only
`paper/icc_main.pdf` plus the artifact summary a real reviewer would get, and was barred from
`submission_finalization/`, `archive/` and git history. All four ran `make gate`; three read the
implementation; one checked the orbital mathematics numerically.

## Verdicts — SA0 (baseline `31e8dde`)

| | R-SA1 area chair | R-SA2 trustworthy ML | R-SA3 satellite/NTN | R-SA4 acceptance bar |
|---|---|---|---|---|
| **verdict** | WEAK ACCEPT | WEAK ACCEPT | WEAK ACCEPT | **WEAK REJECT** |
| novelty | 3 | **2** | 3 | — |
| significance | 3 | 3 | 3 | — |
| soundness | 4 | 4 | 4 | — |
| evidence | 3 | 3 | 3 | — |
| clarity | 3 | 3 | 3 | — |
| venue fit | 4 | — | 3 | — |

### One-sentence contribution, as each reviewer stated it

- **R-SA1** — an executable data-validation contract, satellite-instantiated, whose claims and
  evidence are in exact correspondence, with L4.7 as the one reusable technical result.
- **R-SA2** — "one model + two new checks + a disclosed hygiene layer": the L1/L3 timeline, plus
  differential provenance completeness and a size-controlled statistical-unit test.
- **R-SA3** — nineteen mechanically checkable rules with a red-fixture requirement, whose
  irreducibly orbital content is the predicted-visible row-membership framing.
- **R-SA4** — a well-tested 833-line CI library with a defensible taxonomy and two real ideas
  inside it: the availability clock and L4.7's null construction.

### Strongest acceptance argument, per reviewer

- **R-SA1** — claims and evidence correspond exactly, verified mechanically rather than trusted.
- **R-SA2** — honesty enforced in code, and two genuinely transferable checks.
- **R-SA3** — the orbital mathematics is correct (checked numerically) and the traps are real.
- **R-SA4** — the two-clock observation is correct, non-obvious, and structurally invisible to
  chronological splitting.

### Strongest rejection argument, per reviewer

- **R-SA1** — no contact with any artifact the authors did not write.
- **R-SA2** — leads with its weakest material; closest prior art uncited.
- **R-SA3** — satellite framing load-bearing for ~2 of 19 rules; the one irreducibly orbital
  component has never been run against SGP4 or a real catalogue.
- **R-SA4** — no independent anchor anywhere in the evidence chain; the paper's own §VI retracts
  the abstract's headline.

## Classification

**A. NOVELTY NOT VISIBLE — unanimous, and the dominant finding.**
All four said the paper leads with the wrong material. R-SA2 and R-SA4 independently named the
same two ideas as the only non-standard content: differential provenance completeness (L4.6) and
the permutation-referenced statistical-unit test with an explicit abstention (L4.7). R-SA2's
structural evidence: the six protected objects do **not** partition the nineteen rules — only six
rules name one of the six as their protected object, and Table I's own column contradicted the
abstract. *Addressed in cycle 1.*

**B. SATELLITE RELEVANCE NOT LOAD-BEARING — confirmed, and quantified.**
R-SA3 applied the swap test object by object: **~2 of 19 rules (L2.1, L2.2) would need rewriting
to leave the domain**; two more need re-instantiation; fifteen are domain-neutral. It also noted
the sting — L2.2 and L2.3, two of the three rules with no red fixture, are the physics layer. The
paper's actual in-text claim (satellite gives each object an *operational meaning*) is defensible;
the stronger reading is not supported. *Partly addressed; the honest weaker claim retained.*

**C. EVALUATION LOOKS SELF-CONFIRMING — unanimous, and unfixable within this loop.**
R-SA4 checked the fixtures directly: `HO1` is `pub < dec` instead of `pub <= dec`; `D11` flips a
self-reported boolean, so L4.3 detects a *declaration* of non-aggregation. Its conclusion: strip
the check-scoped classes and "even weak evidence covers about 6 of 17." R-SA1: the 2/17 baseline
is "close to definitional rather than empirical." *Not addressable without new evidence.*

**D. LIMITATIONS OVERWHELM CONTRIBUTION — confirmed by R-SA4, who quoted the specific paragraph.**
The check-scoped-injection paragraph "dissolves the paper's headline," and the abstract still led
with a number §VI had retracted. *Addressed: 17/17 removed from the abstract.*

**E. SIX-PAGE READABILITY — minor.** R-SA1: §III near-telegraphic, Fig. 2 close to unreadable at
print size, abstract carried eight numbers. *Addressed: engineering demoted to one paragraph,
abstract reduced to one principal quantitative sentence.*

**F. CLAIM OR TECHNICAL DEFECT — three found, all real, all fixed.**

| defect | found by | status |
|---|---|---|
| Ref [3] (Vallado) cited for a publication-time claim it does not contain — the paper's single load-bearing orbital fact | R-SA3 | fixed: CCSDS 502.0-B + Space-Track GP |
| `CLAIMS.md` stated 655 lines / 32 tests against an artifact reporting 877 / 51 | R-SA1, R-SA2 independently | fixed: table generated from the artifact |
| Statistical unit named as the pass; the exchangeable unit is the **element set** | R-SA3 | fixed |
| "833 lines across four modules" counted eight files | R-SA2 | fixed |
| `epoch <= publication` asserted as invariant; it is not | R-SA3 | now named as a missing twentieth rule |
| Bisection caveat's proposed repair under-corrects by one tolerance (`2·tol`, not `tol`) | R-SA3 | docstring, artifact-only |

## Why the proxy cannot be met in this loop

Two disqualifiers fired at SA0 and neither is a framing problem:

1. **A verdict below WEAK ACCEPT** (R-SA4).
2. **R-SA4 answered "yes"** to whether the paper reads primarily as an internal debugging report,
   quoting §V's opening.

Every reviewer's route to a higher grade required the same thing, and it is the one thing this
loop forbids:

- R-SA1: an external audit of 4–6 published NTN papers replacing §V.
- R-SA3: one real-SGP4 delta in Hz of residual Doppler and µs of timing error.
- R-SA4: "one instance where L1.2 or L4.7 moves a reported number."

**The optional microcheck does not bridge this.** Its gate requires three reviewers naming lack of
independent application as the *sole* barrier; R-SA2's barrier is emphasis, so the gate fails. More
decisively, the microcheck's permitted output — which contract assumptions a repository declares,
omits, or leaves indeterminate — is **not what any of the three asked for**. None would be moved by
it. The gate and the remedy do not match, so it was not started.

## What cycle 1 could and could not change

Reframing can make the novelty visible, correct a miscitation, and stop the abstract quoting a
retracted number. It cannot make a curated suite independent of its authors. R-SA4's objection is
about evidence that does not exist, not presentation that can be repaired — and the evidence that
would answer it is forbidden here for good reason: the authors' own prior results are in
`archive/KNOWN_INVALID_RESULTS.md`.
