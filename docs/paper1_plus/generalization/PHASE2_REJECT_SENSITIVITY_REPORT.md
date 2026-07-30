# Phase-2 Reject-Threshold Sensitivity Report

Date: 2026-07-27
Design: 9 retained satellites × 6 bands × 5 thresholds = **270 cells**,
target-specific A → A only. No cross-satellite transfer.

Thresholds: **none / 150 / 500 / 1500 / 3000 Hz**. 1500 Hz is the preregistered
value used in Phase-0 and Phase-1.

Per threshold the pipeline is re-executed end to end — re-screened,
re-split, **re-fit**, re-selected on validation, re-gated on validation, then
evaluated on held-out test. No model, scaler or alpha is reused across
thresholds. Models, features, pairing, chronological splits, γ and the gate
definition are unchanged from Phase-0/1.

Vocabulary, per instruction: gate-closed cells with a held-out improvement are
**sub-margin / conservative-refusal** cases. They are not "missed opens".

Software-only, `reference_is_measured_truth = false`. No hardware, RF, packet,
error-rate, receiver-acknowledgement, over-the-air or on-orbit content.

---

## 1. Primary question and answer

> Are the small Iridium residual improvements robust to the |r| screening rule,
> or are they induced by residual filtering?

**Mostly induced by filtering.** Four of the five priority cells change sign or
evidence materially when the screen is removed. The one cell that is stable is
stable only because screening removes essentially nothing there.

| Priority cell | Verdict | Improving at | Note |
|---|---|---|---|
| IRIDIUM 181 @ 8 h | **ROBUST SUB-MARGIN SIGNAL** | 5/5 thresholds | screening removes 0.00–0.05 % of pairs here |
| IRIDIUM 181 @ 96 h | SCREENING-SENSITIVE | 4/5 | `none` → **−18.88 %** |
| IRIDIUM 181 @ 168 h | SCREENING-SENSITIVE | 4/5 | `none` → **−4.75 %**, p = 0.49 |
| IRIDIUM 177 @ 96 h | SCREENING-SENSITIVE | 3/5 | `none` → −2.09 %, 150 Hz → **−18.73 %** |
| IRIDIUM 177 @ 168 h | SCREENING-SENSITIVE | 3/5 | gate **opens at 150 Hz only** (§4) |

### The five priority cells in full

**IRIDIUM 181 @ 8 h — the only robust cell**

| T | accepted | val imp % | test imp % | win rate | p | Holm p | block CI excl. 0 | gate |
|---|---:|---:|---:|---:|---:|---:|:--:|:--:|
| none | 1902 | +1.37 | +1.94 | 0.615 | <1e-15 | <1e-15 | yes | closed |
| 150 | 1901 | +1.39 | +1.90 | 0.641 | <1e-15 | <1e-15 | yes | closed |
| 500 | 1902 | +1.37 | +1.94 | 0.615 | <1e-15 | <1e-15 | yes | closed |
| 1500 | 1902 | +1.37 | +1.94 | 0.615 | <1e-15 | <1e-15 | yes | closed |
| 3000 | 1902 | +1.37 | +1.94 | 0.615 | <1e-15 | <1e-15 | yes | closed |

Screening is a **no-op** in this cell: at most one pair of 1902 is ever removed.
So "robust to screening" here means "screening never happened", not "the signal
survived a stress test". That distinction is essential and is not a strength of
the finding.

**IRIDIUM 181 @ 96 h and @ 168 h — sign flips when screening is removed**

| T | 96 h test imp % | 168 h test imp % |
|---|---:|---:|
| none | **−18.88** | **−4.75** (p = 0.49, n.s.) |
| 150 | +1.22 | +4.14 |
| 500 | +1.71 | +1.90 |
| 1500 | +1.63 | +2.23 |
| 3000 | +1.54 | +2.21 |

Removing the screen — which discards under 1 % of pairs at 1500 Hz — turns a
+1.6 % improvement into a −18.9 % degradation at 96 h. The Phase-1 improvement
in these cells exists **only inside the screened population**.

**IRIDIUM 177 @ 96 h — non-monotone and unstable**

`none` −2.09 % → 150 Hz **−18.73 %** → 500 Hz +0.81 % → 1500 Hz +0.52 % →
3000 Hz +0.12 %. No coherent trend; the sign depends on the threshold in both
directions.

**IRIDIUM 177 @ 168 h — see §4.**

## 2. The dominant global finding: screening improves the learned branch's relative standing

Across all 54 satellite × band combinations:

| | count |
|---|---:|
| sign-stable positive (learned better at every threshold) | **3** |
| sign-stable negative (learned worse at every threshold) | 21 |
| **sign flips across thresholds** | **30 / 54** |

And the direction of the effect is consistent: removing the screen almost always
makes the learned branch *worse*, often catastrophically.

Largest `none` → 1500 Hz swings in held-out improvement:

| Satellite | Band | `none` | 1500 Hz | swing | rejected at 1500 Hz |
|---|---:|---:|---:|---:|---:|
| SENTINEL-6B | 72 h | **−4417.8 %** | −14.5 % | 4403 | 1.16 % |
| SENTINEL-6B | 96 h | −2376.5 % | −30.7 % | 2346 | 2.01 % |
| SENTINEL-6B | 168 h | −907.1 % | −21.3 % | 886 | 2.33 % |
| ONEWEB-0015 | 72 h | −260.5 % | −1.1 % | 259 | 9.30 % |
| ONEWEB-0015 | 96 h | −224.2 % | +0.4 % | 225 | 11.19 % |
| FLOCK 4H 2 | 8 h | −47.0 % | −2.5 % | 44.5 | 0.63 % |
| BLACK KITE-1 | 24 h | −35.3 % | −1.7 % | 33.6 | 1.26 % |
| IRIDIUM 181 | 96 h | −18.9 % | +1.6 % | 20.5 | 0.38 % |

Removing **1–2 %** of pairs changes SENTINEL-6B's held-out result by three
orders of magnitude. The mechanism is not subtle: outlier pairs enter the
*training* segment and wreck the fit, and enter the *test* segment where the
learner's error on them dominates the mean. SGP4, having no fitted parameters,
is unaffected by the first channel.

**So the screen is not neutral, and it does not favour the negative result.**
Comparing no screening against the preregistered 1500 Hz rule across all 54
satellite x band cells: screening makes the learned branch relatively better in
**36** cells, worse in **3**, and effectively unchanged in **15** (14 of which
are cells where screening removes no pairs at all). Median shift **-1.26
percentage points**, IQR [-9.27, 0.00]. The aggregate direction therefore
supports the statement that the preregistered 1500 Hz choice is generous to
learning; the unscreened result is worse for learning in the large majority of
cells.

This addresses the circularity objection in the opposite direction to the one
originally feared: screening was suspected of manufacturing the *negative*
result; on the aggregate it suppresses an even more negative one. Stated
carefully: **screening generally improves the learned branch's relative
performance, while many apparent gains are screening-sensitive.**

## 3. ISS: the split-membership caveat, quantified

ISS is the only object where screening removes a large share of *held-out*
pairs (28.5 % at 168 h, 1500 Hz). Its threshold curve therefore mixes a
different-learner effect with a different-sample effect.

| T | accepted | reject % | val imp % | test imp % | win rate | p |
|---|---:|---:|---:|---:|---:|---:|
| none | 46 733 | 0.03 | −0.87 | −0.34 | 0.318 | <1e-15 |
| 150 | 13 211 | 71.74 | +0.00 | +0.03 | 0.519 | 0.039 |
| 500 | 23 753 | 49.19 | −0.00 | −0.03 | 0.471 | 7.5e-05 |
| 1500 | 33 411 | 28.52 | −0.28 | −0.13 | 0.445 | <1e-15 |
| 3000 | 37 555 | 19.66 | −0.49 | −0.20 | 0.416 | <1e-15 |

ISS never improves by more than 0.03 %, and its gate is closed at every
threshold. Its curve is reported for completeness but is the least
interpretable of the nine, exactly as flagged before the run.

## 4. The one gate opening in 270 cells

**IRIDIUM 177 @ 168 h, threshold 150 Hz: gate OPEN.**
Validation improvement +18.36 %, held-out improvement +5.14 %, win rate 0.559,
raw p = 0.0075.

This is the only real-data MAE-gate opening observed. Cell accounting is given
in §4a — the phases overlap, so they must not be summed. It requires four
qualifications, all of which matter:

1. **It is not at the preregistered threshold.** 150 Hz is the tightest screen
   tested, and it discards **40.34 %** of candidate pairs (2610 → 1557).
2. **It is produced by *tightening*, not relaxing.** The pre-registered
   definition of SCREENING-REVEALED LEARNABILITY requires relaxing the screen to
   expose deployable learnability. This is the opposite direction, so the cell is
   classified **SCREENING-SENSITIVE**, not revealed learnability.
3. **It does not survive multiple-comparison correction.** Holm-adjusted
   p = **1.00**; BH q is likewise non-significant. Raw p = 0.0075 across a family
   of 270 sign tests is unremarkable.
4. **The neighbouring thresholds contradict it.** 500 Hz gives −2.16 %
   (held-out *worse*), `none` gives −0.07 %. Only the 150 Hz point is positive
   above the margin.

Reported prominently because a gate opening is exactly the kind of result that
must not be buried — but it is **not** evidence of deployable learnability.

## 5. Multiple-comparison diagnostic

Holm and Benjamini-Hochberg computed across the family of Phase-2 sign tests
(diagnostic only; the Evidence Gate is never altered by significance).

Effects on interpretation:

- IRIDIUM 181 @ 8 h survives Holm at every threshold (p and Holm p both far
  below any threshold) — it is a *statistically detectable* improvement.
- IRIDIUM 177 @ 96 h at 3000 Hz: raw p = 0.0027 but Holm p = 0.41 — not
  detectable once corrected.
- IRIDIUM 177 @ 168 h at 150 Hz (the gate-open cell): raw p = 0.0075, Holm
  p = 1.00.

**Statistically detectable ≠ deployment-worthy.** Even IRIDIUM 181 @ 8 h, which
is detectable under every threshold and every correction, delivers +1.94 % — far
below the 5 % that γ = 0.95 requires, on a baseline MAE of ~0.17 Hz. The gate
correctly refuses it. These two axes are independent and are kept separate
throughout.

## 6. Temporal dependence diagnostic

A block bootstrap over reference-epoch **day** blocks is reported alongside the
preregistered i.i.d. pair bootstrap; it never replaces it.

Adjacent TLE pairs share overlapping element sets, so the pair bootstrap can
understate uncertainty. Effects:

- **IRIDIUM 181 @ 8 h**: block CI excludes zero at all five thresholds. The
  strongest cell survives the temporal diagnostic.
- **IRIDIUM 177 @ 96 h**: block CI *includes* zero at 1500 and 3000 Hz, despite
  raw p = 3e-06 and 0.0027. Temporal dependence explains part of that apparent
  significance.
- **IRIDIUM 177 @ 168 h**: block CI includes zero at `none`, 150 and 500 Hz;
  excludes zero only at 1500 and 3000 Hz.

So the tiny-but-highly-significant pattern flagged before the run is real: for
IRIDIUM 177 several cells lose their evidence once temporal blocks are
respected. IRIDIUM 181 @ 8 h does not.

## 7. Gate decisions overall

| | count |
|---|---:|
| closed | **269 / 270** |
| open | 1 (IRIDIUM 177 @ 168 h @ 150 Hz) |

At the preregistered 1500 Hz threshold specifically: **0 of 54 cells open**,
reproducing Phase-0 and Phase-1 exactly.

## 8. What this does and does not establish

**Established:**

- The Iridium improvements at 96 h and 168 h are screening-dependent; the sign
  flips when the screen is removed.
- Screening systematically *helps* the learned branch, so the preregistered
  negative result is not an artifact of over-aggressive filtering — the opposite.
- One cell (IRIDIUM 181 @ 8 h) shows a small, threshold-stable, temporally
  robust, multiple-comparison-surviving improvement of ~1.9 %, far below the
  deployment margin.

**Not established:**

- That screening circularity is "solved". It is answered for the *direction* of
  bias on these nine objects and five thresholds. Training-set composition still
  changes the fitted learner in every cell, and no causal decomposition of that
  channel was attempted.
- Any deployable learnability anywhere.
- Anything about cross-satellite transfer, which was not run.

## 9. Outputs

`experiments/exp14_multisat_generalization_matrix/phase2_reject_sensitivity/`:
`reject_sensitivity_results.csv` (270 rows, all requested columns),
`reject_sensitivity_results.json` (rows + priority classification),
`fig_reject_threshold_sensitivity.pdf/png`,
`fig_iridium_screening_sensitivity.pdf/png`.

Execution note: cells were computed in per-satellite and per-band chunks purely
for runtime. Screening is a pure post-filter on each pair's max |r|, so pairs
were propagated once per (satellite, band) and subset per threshold; this was
verified identical to direct rebuilds by comparing pair-id sets at every
threshold before any result was produced.
