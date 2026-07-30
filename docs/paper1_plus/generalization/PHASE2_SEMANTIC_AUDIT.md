# Phase-2 Semantic Audit

Date: 2026-07-27
Scope: presentation and claim correctness only. **No underlying numeric result
was changed.** No re-run of any model. Frozen Paper 1 and slides untouched.
All values remain model-derived inter-TLE residuals with
`reference_is_measured_truth = false`; no measured RF truth is involved.

---

## 1. Sign convention — standardized

Canonical definitions, now used everywhere and recorded in
`reject_sensitivity_results.json` under `metadata.sign_convention`:

```
delta_mae_hz    = learned_mae - sgp4_mae
degradation_pct = 100 * (learned_mae - sgp4_mae) / sgp4_mae     # + = learned WORSE
improvement_pct = -degradation_pct                              # + = learned BETTER
```

**Neither is ever labelled "Delta%".** Column headers now read
`degradation_pct` or `improvement_pct` explicitly, and figure axes state the
direction in words ("above 0 = learned better" / "positive = learned worse").

Changes made:

| Item | Action |
|---|---|
| `run_phase2_reject_sensitivity.py` | `test_improvement_pct` is now *derived by negation* from `test_degradation_pct`, so the two can never disagree through independent rounding |
| `reject_sensitivity_results.{csv,json}` | re-derived; **0 of 270 values changed** — the fields were already exact negations, confirming the underlying numbers were self-consistent |
| Phase-1 artifacts | already carried only `test_degradation_pct` (positive = learned worse); no ambiguity existed, nothing changed |
| Figures | Phase-1 gate map annotates "held-out degradation (positive = learned worse)"; Phase-2 curves annotate "held-out improvement (above 0 = learned better)". Each figure states its own direction. |

Verification: `improvement_pct == -degradation_pct` holds for all 270 Phase-2
rows.

## 2. Over-strong claims — corrected

Two forbidden framings were present in `PHASE2_SCREENING_VERDICT.md`. Both were
written by me in the previous pass and are now replaced.

| Was | Now |
|---|---|
| "model-derived inter-TLE residual learning **never reaches a deployable margin** over SGP4" | "the preregistered Evidence Gate opened in **0 of 54** target-specific cells at the preregistered 1500 Hz screening rule. Across a five-threshold screening sweep, **exactly 1 of 270** cells opened (IRIDIUM 177 @ 168 h under 150 Hz screening); that opening is screening-sensitive, contradicted by adjacent thresholds, and does not survive multiple-comparison correction." |
| "the Evidence Gate ... **refuses all of them**" | "the Evidence Gate ... **declines these** from validation evidence alone" |

The required framing is now used verbatim in both Phase-2 documents:

- **At the preregistered 1500 Hz screening rule: 0/54 target-specific
  satellite × band cells open.**
- **Across the five-threshold sensitivity sweep: exactly 1/270 cells opens —
  IRIDIUM 177 @ 168 h under 150 Hz screening — and that opening is
  screening-sensitive and not robust to adjacent thresholds.**

## 3. "Three staleness decades" — replaced

Replaced with **"six staleness bands spanning 8–168 h"**. The original phrasing
was wrong on its face: 8 h to 168 h is a factor of 21, i.e. ~1.3 decades, not
three. One occurrence, in `PHASE2_SCREENING_VERDICT.md`; now corrected.

## 4. Direction of screening bias — quantified

Comparison per satellite × band of **no screening** against the **preregistered
1500 Hz** rule, in canonical units:

```
shift_pp = degradation_pct(1500 Hz) - degradation_pct(none)
shift < 0  =>  screening makes the learned branch relatively BETTER
```

### Aggregate over all 54 cells

| Outcome | Cells |
|---|---:|
| Screening makes learned relatively **better** | **36** |
| Screening makes learned relatively **worse** | **3** |
| Effectively unchanged (\|shift\| < 0.1 pp) | 15 |
| — of which screening removes **no pairs at all** | 14 |

Median shift **−1.259 pp**, IQR **[−9.265, 0.000]**, mean −159.2 pp (the mean is
dominated by SENTINEL-6B outliers and is reported only for completeness).
Directional sign test on the 39 cells that move at all: **36 vs 3**.

### Per satellite

| Satellite | better | worse | unchanged | median shift (pp) |
|---|---:|---:|---:|---:|
| SENTINEL-6B | 3 | 0 | 3 | −442.910 |
| ONEWEB-0015 | 5 | 1 | 0 | −147.393 |
| BLACK KITE-1 | 5 | 0 | 1 | −8.361 |
| FLOCK 4H 2 | 6 | 0 | 0 | −4.929 |
| IRIDIUM 181 | 4 | 0 | 2 | −2.162 |
| IRIDIUM 177 | 5 | 0 | 1 | −1.745 |
| ISS (ZARYA) | 5 | 0 | 1 | −0.337 |
| FLOCK 4H 1 | 3 | 2 | 1 | −0.197 |
| BLACK KITE-2 | 0 | 0 | 6 | 0.000 |

### Conclusion on direction

**The aggregate supports the claim.** Screening improves the learned branch's
relative standing in 36 cells and worsens it in 3; every satellite that moves at
all has a negative median shift. BLACK KITE-2 is entirely unaffected because
screening removes no pairs from it at any band.

Wording adopted: *"screening improves the learned branch's relative
performance"*, with the counts attached. The looser rhetorical phrasing
("flatters the learner") has been removed from both documents.

**What this does not say.** It does not establish that screening circularity is
solved. It establishes the *direction* of the bias on these nine objects at
these five thresholds. Training-set composition still changes the fitted learner
in every cell, and that channel was not causally decomposed.

## 5. Files touched

| File | Change |
|---|---|
| `run_phase2_reject_sensitivity.py` | canonical sign relation enforced by negation |
| `phase2_reject_sensitivity/reject_sensitivity_results.{csv,json}` | field re-derived (0 numeric changes); `metadata.sign_convention` added |
| `PHASE2_REJECT_SENSITIVITY_REPORT.md` | §2 heading and conclusion replaced with quantified direction |
| `PHASE2_SCREENING_VERDICT.md` | forbidden claims replaced; "three staleness decades" corrected; screening counts added |

No result, figure datum, gate decision, threshold or γ was altered.
