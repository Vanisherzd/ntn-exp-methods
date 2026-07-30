# Phase-0 Paper-1 Continuity Audit

Date: 2026-07-27
Question: does the frozen Paper 1 conclusion survive re-derivation under the
unified, leakage-free, pair-level protocol?

Frozen paper: `b529c5e`. **Not modified, regardless of this outcome.**
Evidence: `PHASE0_BLACK_KITE_RERUN_REPORT.md` and
`experiments/exp14_multisat_generalization_matrix/phase0_black_kite/`.

Software-only, model-derived inter-TLE residuals,
`reference_is_measured_truth = false`.

---

## Verdict

> ## CONTINUITY PARTIALLY CHANGED

The **deployable conclusion is fully confirmed**: the Evidence Gate closes in
all 24 rows across all four cells, so the deployed policy is SGP4 / never-learn
everywhere — exactly what the frozen paper claims.

Two specific descriptive claims in the frozen paper **do not survive** the
corrected protocol, which is why this is not a clean "CONFIRMED":

1. **"the reported point estimates place the learned inter-TLE residual above
   the baseline in every row"** — no longer true. BK1 → BK1 at 72 h now gives
   ΔMAE = −0.0020 Hz (−0.04 %), and all six BK2 → BK1 rows are negative.
2. **The magnitude of harm collapses.** BK1 diagonal degradation falls from
   +11.6 … +68.1 % to +0.08 … +12.82 %. The frozen paper's framing — an
   always-on learner "would, if anything, *increase* the frequency error it is
   meant to reduce" — remains directionally right but is now a ~1 % effect on
   most rows, not a tens-of-percent effect.

Nothing **contradicts** the paper: no cell opened, no learned branch won
significantly, and the refusal policy is correct in every row.

---

## A. Does BK1 → BK1 preserve the qualitative Paper 1 conclusion?

**Gate: yes, unchanged.** Closed at all six staleness values, as in the frozen
paper.

**Sign of ΔMAE: 5 of 6 preserved.** Positive at 8/24/48/96/168 h; marginally
negative at 72 h (−0.04 %).

**Pair-level inference: materially weaker than the old descriptive result.**

| Band | old degradation | new degradation | pair win rate | sign-test p | 95 % bootstrap CI of per-pair ΔMAE [Hz] |
|---:|---:|---:|---:|---:|---|
| 8 h | +44.1 % | +12.82 % | 0.367 | 0.052 | crosses/near zero |
| 24 h | +11.6 % | +1.67 % | 0.451 | 0.440 | crosses zero |
| 48 h | +47.2 % | +0.71 % | 0.386 | **0.042** | excludes zero |
| 72 h | +20.7 % | −0.04 % | 0.540 | 0.520 | crosses zero |
| 96 h | +16.3 % | +0.08 % | 0.517 | 0.832 | crosses zero |
| 168 h | +68.1 % | +0.12 % | 0.441 | 0.300 | crosses zero |

Only one of six bands reaches p < 0.05. The old table read as "learning clearly
hurts"; the pair-level view reads as **"learning does nothing measurable, and
what little it does is not an improvement."** The deployment decision is the
same; the evidential story is different and weaker.

Why the magnitudes moved: the old protocol selected among random forest,
gradient boosting and a GPU MLP — models that overfit the near-zero-mean
residual badly (GBR reached 227.7 Hz at 168 h against a 26.9 Hz baseline). The
unified protocol's lightweight family (linear bias-rate, stale-age ridge, full
ridge) barely deviates from SGP4, so it neither helps nor hurts much. That is a
protocol effect, not a new physical finding.

## B. What does the newly clean BK2 → BK2 diagonal show?

The frozen paper never reported this cell. It shows **the same refusal**: closed
at all six bands.

It also produces the campaign's most instructive single row. At 24 h the learned
branch beat SGP4 on validation by 4.93 %, missing the 5 % margin by 0.07 points.
Had it opened, the held-out test would have been **6.27 % worse** with a
significant pair-level loss (win rate 0.256, p = 0.003). The same pattern
repeats at 48 h (+3.48 %, p = 0.014).

**BK2 behaves like BK1.** The negative finding is not a BK1 idiosyncrasy — both
BLACK KITE objects refuse, independently, under identical protocol.

## C. What happens under the new BK1 → BK2 protocol?

Closed at all six bands, and **transfer is the worst-performing cell**: +32.03 %
at 8 h (win rate 0.160, p = 0.0009) and +6.73 % at 24 h (win rate 0.205,
p = 0.0003) are the two most significant learned losses in the whole Phase-0
run.

These are the only rows where "learning actively hurts" is statistically
supported. Note the direction is consistent with the frozen paper's
cross-satellite story, even though the **numbers are not comparable** to the
legacy 73.7 / 275.1 / 18.1 % values (different screen, features, pairing, and
test-based selection).

## D. What happens under BK2 → BK1, absent from the frozen paper?

Closed at all six bands — but with a twist that must not be buried: **every row
has negative ΔMAE.** The learned branch is marginally better on test in all six
bands (−0.03 % to −0.92 %), and the 168 h pair win rate is 0.602 with p = 0.061.

The gate refused because validation improvement never exceeded 0.68 %, far short
of the 5 % margin. Given that no row reaches p < 0.05, refusing was correct:
these are sub-1 % differences inside the noise floor.

Still, this is the closest thing in Phase-0 to a **missed-open candidate**, and
it is asymmetric — BK1 → BK2 hurts significantly while BK2 → BK1 marginally
helps. Transfer between these two objects is not symmetric, which no previous
analysis could have shown because BK2 → BK1 was never run.

## E. Does any Phase-0 result materially contradict the frozen Paper 1 claim?

**No.** No gate opened. No learned branch won significantly anywhere. The
deployed policy is SGP4 / never-learn in all 24 rows, which is precisely the
frozen paper's claim.

What changed is the *strength and universality of the supporting description*,
not the decision.

---

## Consequences for the frozen paper — recorded, not applied

The frozen paper is **not** edited. For the record, if a future correction pass
is ever authorised, two sentences are now known to be too strong:

| Frozen text | Phase-0 status |
|---|---|
| "the reported point estimates place the learned inter-TLE residual above the baseline in **every row**" | false under the unified protocol (BK1 72 h; all BK2 → BK1 rows) |
| Table I degradations of +11.6 … +68.1 % | not reproduced; the unified protocol gives +0.08 … +12.82 % on the same diagonal |

Both are consequences of the old protocol's stronger, overfitting model family
and its sample-level metrics — **not** evidence that the paper's conclusion was
wrong. The paper's own hedging ("not universally", "these are point estimates
under the leakage-free protocol, not pair-clustered inference") already
anticipates most of this.

Paper 1+ should present Phase-0 as *post-hoc validation with a sharper
instrument*: same decision, weaker effect, better statistics.

---

## Outcome classification

Against the pre-registered outcome handling:

- **Outcome 1 — all four cells remain gate-closed.** ✅ This is what happened.
- Outcome 2 (a diagonal opens): did not occur.
- Outcome 3 (diagonal works, transfer fails): did not occur — the diagonal does
  not work either.
- Outcome 4 (transfer succeeds): did not occur; BK2 → BK1's sub-1 % gains are
  not significant.

Interpretation: **the BLACK KITE negative finding survives the stronger unified
protocol**, with the important qualification that the effect size is far smaller
than the frozen paper reports and is mostly statistically indistinguishable from
zero rather than clearly harmful.

## Recommended next experiment

Proceed to step ⑥ of the campaign order: the **7-satellite target-specific
diagonal** (heterogeneous objects, A → A only), still with no cross-satellite
matrix and no reject sweep.

Rationale: Phase-0 shows both BLACK KITE objects refuse, but BLACK KITE is one
family in one regime. The open question the matrix exists to answer — *is
learnability regime-dependent?* — is answered by diagonals across regimes, and
the diagonal is far cheaper and less confounded than the full 81-cell matrix.
If any heterogeneous diagonal opens, that is the Case-B result and the campaign
should stop and analyse before running transfer at all.

Also carry forward as a Phase-7 input: the BK2 → BK2 p95-gate false-open at
8/24/48 h is the first real-data evidence that gate objectives disagree, and it
favours the preregistered MAE gate.
