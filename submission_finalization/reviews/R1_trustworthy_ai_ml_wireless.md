# R1 — TRUSTWORTHY AI / ML-FOR-WIRELESS

**VERDICT: WEAK REJECT**

**One-sentence contribution (reviewer's words):** A 19-rule executable checklist for
temporal-experiment validity in catalogue-fed learning pipelines, whose most defensible
content is the procedural discipline that a validity check must be demonstrated capable of
failing.

## Findings

| # | severity | finding | status |
|---|---|---|---|
| 1 | **BLOCKER** | "chronological checks detect 2/18" is not measured; no baseline implemented; cited artifact `fig2_data.json` absent | **FIXED** `7035eb7` — baseline implemented, measured 2/18, artifact emitted |
| 2 | **BLOCKER** | L4.7's `within_group_icc` is a biased variance ratio, null mean ≈ 1/m, threshold 0.2 below its own null mean for m ≤ 4; fixture uses m = 3 | **FIXED** `7035eb7` — unbiased ICC(1) + estimability precondition |
| 3 | MAJOR | "every detector carries a two-sided test" false for 5 of 19 (L1.5, L2.4, L4.6, L4.7 no unit test; L4.5 fires nowhere) | OPEN |
| 4 | MAJOR | pre-registration ordering unverifiable — all evaluation files landed in one commit; PREREGISTRATION froze 12 dev faults, paper reports 14 | OPEN |
| 5 | MAJOR | HO4 does not exercise L2.4's novel component — divergence is 5× tolerance *inside* the declared domain | OPEN |
| 6 | MAJOR | L4.6's "checkable without enumerating every input" conflates verdict soundness with coverage | OPEN |
| 7 | MAJOR | `sample_passes` docstring instructs the user to commit the exact error HO3 injects | OPEN |
| 8 | MAJOR | "availability" is a relabelling of bitemporal / point-in-time correctness; uncited | OPEN |
| 9 | MAJOR | 14/18 faults drawn from the defects that motivated the detectors; injection at fixture-input not program level | OPEN |
| 10 | MAJOR | `build_label` implements the outcome-dependent status its own docstring forbids | OPEN |
| 11 | MINOR | 812 LOC counts a tracked macOS duplicate; real 710 | **FIXED** `7035eb7` |
| 12 | MINOR | two decorative citations (`vallado2006revisiting`, `lin2021ntn` mis-supports its sentence); five missing threads | OPEN |
| 13 | MINOR | banlist docstring names a source-of-truth file that does not exist | OPEN |
| 14 | MINOR | Table I presents 19 uniform rules; only 15 can fire | OPEN |

**Top rejection argument:** the paper's thesis is that a check which cannot go red is not
evidence, and it fails that standard in both directions at once — a flagship rule that
fires on correct designs, a rule that goes red nowhere, four detectors with no unit test,
and a headline baseline that was never run.

**Verified sound by R1:** the repurposing is legitimate not salvage; the banlist is a real
build prerequisite with no banned quantity present; the reclassification of three suggested
held-out mutations was honest and self-penalising; the L4.4 fixture disclosure is exemplary;
27 tests pass; the matrix reproduces with only runtime fields differing; the pass scheduler
is the best engineering in the submission.
