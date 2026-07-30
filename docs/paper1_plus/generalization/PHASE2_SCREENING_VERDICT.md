# Phase-2 Screening Verdict and Campaign Recommendation

Date: 2026-07-27
Evidence: `PHASE2_REJECT_SENSITIVITY_REPORT.md` and
`experiments/exp14_multisat_generalization_matrix/phase2_reject_sensitivity/`.

Software-only, model-derived inter-TLE residuals,
`reference_is_measured_truth = false`. Frozen Paper 1 untouched. γ unchanged.

---

## Verdict on the primary question

> Are the small Iridium residual improvements robust to the |r| screening rule,
> or are they induced by residual filtering?

**Four of five priority cells: induced by filtering. One: robust but trivially
so.**

| Cell | Classification |
|---|---|
| IRIDIUM 181 @ 8 h | **ROBUST SUB-MARGIN SIGNAL** |
| IRIDIUM 181 @ 96 h | SCREENING-SENSITIVE SIGNAL |
| IRIDIUM 181 @ 168 h | SCREENING-SENSITIVE SIGNAL |
| IRIDIUM 177 @ 96 h | SCREENING-SENSITIVE SIGNAL |
| IRIDIUM 177 @ 168 h | SCREENING-SENSITIVE SIGNAL |

The one robust cell is robust because screening removes at most 1 pair in 1902
there — the stress test was never applied. That is a weak form of robustness and
is reported as such.

## The finding that outranks the primary question

**Screening improves the learned branch's relative performance, not the baseline's.**

- 30 of 54 satellite × band combinations flip the sign of held-out improvement
  across thresholds.
- Comparing no screening against the preregistered 1500 Hz rule: screening makes
  the learned branch relatively **better in 36** cells, **worse in 3**, and
  leaves 15 effectively unchanged (14 of those are cells where screening removes
  no pairs at all). Median shift −1.26 pp, IQR [−9.27, 0.00].
- Removing 1–2 % of pairs moves SENTINEL-6B @ 72 h from −14.5 % to **−4418 %**.
- The direction is nearly universal: unscreened evaluation is *worse* for the
  learned branch.

Mechanism: outliers enter the training segment and corrupt the fit, and enter
the test segment where the learner's error on them dominates. SGP4 has no fitted
parameters and is immune to the first channel.

**Consequence for the campaign's central worry.** The circularity objection was
that screening might manufacture the negative result. It does the opposite: the
preregistered 1500 Hz screen is *generous* to learning, and the unscreened
result is more negative. The negative finding is not an artifact of aggressive
filtering.

This is **not** a claim that screening circularity is "solved". It is answered
for the direction of bias, on nine objects at five thresholds. Training-set
composition still changes the fitted learner everywhere, and that channel was
not causally decomposed.

## The single gate opening, stated plainly

**IRIDIUM 177 @ 168 h at 150 Hz opened the preregistered MAE gate** — the only
opening observed. See the cell accounting below; the phase counts overlap and
must not be summed.

| Population | Definition | Cells | Gate opens |
|---|---|---:|---:|
| Primary target-specific | 9 satellites x 6 bands, preregistered 1500 Hz | **54** | **0/54** |
| Screening sensitivity | 9 x 6 x 5 thresholds (superset of the above) | **270** | **1/270** |
| Cross-direction transfer | BK1->BK2 and BK2->BK1, 2 x 6 bands, 1500 Hz | **12** | **0/12** |
| **Unique configurations** | distinct (source, target, staleness, threshold) keys | **282** | 1/282 |

282 = 270 target-specific across five thresholds + 12 cross-direction transfer
cells. The Phase-0 diagonals and all 42 Phase-1 cells are *contained in* the 54
target-specific cells at 1500 Hz, and were verified numerically identical to
them (0 mismatches), so they add no unique configurations.

It is surfaced, not buried. It is also not evidence of learnability:

- produced by *tightening* the screen to 150 Hz, discarding 40.3 % of pairs —
  the opposite of the "relaxing" direction that would constitute
  SCREENING-REVEALED LEARNABILITY;
- Holm-adjusted p = **1.00**;
- adjacent thresholds contradict it (500 Hz: −2.16 %; none: −0.07 %).

At the preregistered 1500 Hz threshold, **0 of 54** cells open, reproducing
Phase-0 and Phase-1 exactly.

γ was not relaxed and must not be. Lowering it after observing which cells would
open is the post-hoc tuning this campaign exists to prevent.

## Detectable versus deployment-worthy

Kept strictly separate, as required:

| | IRIDIUM 181 @ 8 h |
|---|---|
| Statistically detectable improvement | **Yes** — +1.94 %, win rate 0.615, survives Holm at every threshold, block CI excludes zero at every threshold |
| Deployment-worthy improvement | **No** — 1.94 % against a 5 % margin, on a baseline MAE of ~0.17 Hz, three orders below `F_tol` = 500 Hz |

The temporal diagnostic matters here too: several IRIDIUM 177 cells with raw
p < 0.01 have block-bootstrap CIs that include zero, so part of their apparent
significance is temporal dependence among adjacent TLE pairs, not signal.

## Recommendation

Of the three options offered:

- **A. proceed to cross-satellite transfer** — no.
- **B. investigate Iridium residual structure more deeply first** — no, not as
  the next step.
- **C. revise the generalization hypothesis** — **yes.**

### Why C

The campaign was built on the hypothesis that inter-TLE residual learnability
might be **regime-dependent**, and that a matrix would locate the regimes where
it holds. Three phases of real data do not support that framing:

1. **282 unique real-data configurations, one gate opening**, which does not
   survive multiple comparisons and appears only at a non-preregistered
   threshold. (0/54 at the preregistered operating point; 1/270 across the
   screening sweep; 0/12 cross-direction transfer.)
2. **The one durable positive effect is ~2 % on a sub-Hz residual.** Even taken
   at face value it has no endpoint consequence: the outage proxy is zero
   wherever this effect lives, so the correction buys no guard, no margin, no
   energy.
3. **The apparent regime structure is largely screening-sensitive.** The
   Iridium 96/168 h signals — the entire empirical basis for "some regimes may
   be learnable" — do not survive threshold variation.

Transfer (option A) is not worth running: transfer asks whether learnable
structure moves between satellites, and Phase-1/2 found no deployable structure
to move. A 9 x 9 matrix would take the 270 target-specific configurations to
~2430 and would answer a
question whose premise is unsupported.

Deeper Iridium investigation (option B) is worth doing **eventually**, but not
before the hypothesis is restated. Right now it would be characterising a 1.9 %
effect on one object at one staleness with no known endpoint value — a
measurement in search of a claim.

### Proposed revised hypothesis

Replace *"residual learnability is regime-dependent"* with the sharper claim the
data actually supports:

> Across nine LEO objects spanning five orbital regimes and six staleness bands
> from 8 to 168 h, the preregistered Evidence Gate opened in **0 of 54**
> target-specific cells at the preregistered 1500 Hz screening rule. Across a
> five-threshold screening sweep, **exactly 1 of 270** cells opened
> (IRIDIUM 177 @ 168 h under 150 Hz screening); that opening is
> screening-sensitive, contradicted by adjacent thresholds, and does not survive
> multiple-comparison correction. Where a statistically detectable improvement
> exists it is ~2 % on a residual already far below the endpoint frequency
> tolerance. Screening generally improves the learned branch's relative
> performance, while many apparent gains are screening-sensitive. The Evidence
> Gate's value is that it declines these from validation
> evidence alone, without ever seeing the held-out consequence.

That is a stronger, better-evidenced Paper 1+ than a generalization matrix, and
it converts the frozen Paper 1's single-family negative result into a
nine-object, five-regime, screening-robust one.

### Concrete next step, if a next experiment is wanted

Not the matrix. Two candidates, in order:

1. **Endpoint-consequence analysis of the one durable effect.** Take IRIDIUM 181
   @ 8 h (+1.94 %, robust) and push it through the guard/energy proxy chain to
   show explicitly that a detectable MAE gain of this size produces no change in
   guard, outage or energy. That closes the "you refused a real improvement"
   objection with a number instead of an argument.
2. **A pre-registered γ sensitivity analysis**, reported alongside the γ = 0.95
   result, showing what would have deployed at γ = 0.99 and what it would have
   cost on held-out data. Declared in advance, never as a replacement.

Both are cheap, neither requires new data, and both strengthen the refusal
argument rather than fishing for an opening.

---

## Claim boundary

No hardware, RF, USRP, firmware or over-the-air work. No packet, error-rate,
receiver-acknowledgement or on-orbit result. No cross-satellite transfer was
run. The frozen Paper 1 at `b529c5e` is unmodified.
