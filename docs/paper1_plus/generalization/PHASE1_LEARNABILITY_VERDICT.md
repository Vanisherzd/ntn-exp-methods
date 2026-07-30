# Phase-1 Learnability Verdict

Date: 2026-07-27
Evidence: `PHASE1_TARGET_SPECIFIC_REPORT.md` and
`experiments/exp14_multisat_generalization_matrix/phase1_target_specific/`.

Software-only, model-derived inter-TLE residuals,
`reference_is_measured_truth = false`. Frozen Paper 1 untouched.

---

## Verdict

> # NO TARGET-SPECIFIC REAL LEARNABILITY OBSERVED

The preregistered MAE gate opened in **0 of 42** cells across all seven retained
non-BLACK-KITE satellites and all six staleness bands. No cell satisfies the
candidate criterion, which requires **both** an OPEN gate on validation **and** a
held-out learned MAE below SGP4.

Combined with Phase-0 (BLACK KITE, 24 cells, all closed), the campaign now has
**66 real-data cells and zero gate openings.**

---

## Question asked

*Is target-specific inter-TLE residual learnability satellite/regime dependent
across the heterogeneous real LEO dataset?*

## Answer

**Under the preregistered deployment criterion: no — the refusal is uniform.**
Seven satellites spanning five orbital regimes, altitudes 388–1336 km,
inclinations 51.6°–97.4°, B\* across three decades, update cadences 4.5–10.0 h,
and histories from 614 to 46 859 elements all produce the same decision.

**Descriptively, however, the residual behaviour is emphatically not uniform**,
and that heterogeneity is the real Phase-1 finding:

| Satellite | Character of held-out behaviour |
|---|---|
| SENTINEL-6B | learning consistently and significantly harmful (+8 % … +31 %, win rates 0.038–0.321) |
| ONEWEB-0015 | catastrophic at short staleness (+81 %, +122 %), neutral by 72 h |
| ISS | negligible but certainly non-zero harm (+0.08 % … +0.32 %, p ≪ 1e-15 on 14–19 k pairs) |
| FLOCK 4H 1 / 2 | mostly indistinguishable from SGP4; no band significant except FLOCK 1 at 8 h |
| IRIDIUM 181 / 177 | the only objects where learning **helps** — consistently, at long staleness, significantly |

So the answer splits: **the deployment decision is regime-independent; the
residual structure is not.**

---

## The finding that matters most: six significant missed-open-style cells

Gate closed, yet the held-out learned branch beat SGP4 with pair-level
significance:

| Satellite | Band | validation Δ% | held-out Δ% | win rate | 95 % CI [Hz] | p |
|---|---:|---:|---:|---:|---|---:|
| IRIDIUM 181 | 168 h | −0.63 | −2.23 | 0.648 | [−0.2664, −0.1773] | <1e-15 |
| IRIDIUM 181 | 8 h | −1.37 | −1.94 | 0.615 | [−0.0041, −0.0024] | <1e-15 |
| IRIDIUM 181 | 96 h | −0.79 | −1.63 | 0.619 | [−0.0908, −0.0544] | <1e-15 |
| IRIDIUM 177 | 168 h | −2.03 | −1.30 | 0.689 | [−0.6733, −0.4006] | <1e-15 |
| IRIDIUM 177 | 96 h | −1.49 | −0.52 | 0.587 | [−0.1383, −0.0307] | 3e-06 |
| ONEWEB-0015 | 96 h | −0.27 | −0.39 | 0.562 | [−0.0307, +0.0047] | 0.015 |

Five of six are Iridium. All six select `stale_age_ridge` — ridge on TLE age and
epoch gap alone. Validation and test agree in sign in every case. The gate
refused because the improvement never approached the 5 % margin, not because the
evidence contradicted it.

**What this is:** the first real-data evidence in this campaign that a *stable,
reproducible, statistically supported* residual correction exists anywhere.

**What this is not:** a learnability claim, a deployment recommendation, or a
candidate regime. A 1–2 % MAE improvement on a residual already far below the
500 Hz tolerance has no demonstrated endpoint value, and the preregistered
criterion — which was fixed before any data was seen — is not met.

**What it does not license:** relaxing γ. The margin is preregistered. Lowering
it after observing which cells would then open is exactly the post-hoc tuning
this campaign was built to prevent. If γ is ever revisited it must be as a
declared sensitivity analysis with the original result reported alongside.

---

## Cross-check against Phase-0

| | Phase-0 (BLACK KITE) | Phase-1 (heterogeneous) |
|---|---|---|
| Cells | 24 | 42 |
| Gate opens | 0 | 0 |
| Significant learned wins | 0 | **6** |
| Significant learned losses | 3 | many (ISS all 6, SENTINEL all 6, ONEWEB 3, others scattered) |
| Diagnostic gate disagreement | BK2→BK2 p95 opened at 8/24/48 h | **none** |
| Outage proxy | 0 everywhere | non-zero for ISS (3.04 % at 168 h) and four others at 168 h |

Phase-0's p95 disagreement did not recur, so it remains a single-object
observation rather than a pattern.

---

## Recommended next experiment

**Reject-threshold sensitivity (Phase 6), run first on the two Iridium objects,
then across all nine.**

Two independent reasons, in priority order:

1. **It is the pre-committed next step** now that no candidate regime was found —
   the campaign order says reject sensitivity follows the diagonal.
2. **Phase-1 supplied a specific reason to prioritise it.** ISS loses 28.5 % of
   its pairs at 168 h *including 1 459 validation and 3 172 test pairs*, so
   screening directly altered held-out membership for the largest object.
   IRIDIUM 177 loses pairs from held-out at 168 h too — and 168 h is exactly
   where the Iridium missed-open signal is strongest. Whether that signal
   survives, strengthens or vanishes when the screen is relaxed is now a
   concrete, falsifiable question rather than a generic robustness check.

Design note for that run: report the Iridium 96 h and 168 h cells at every
threshold, and state explicitly whether the missed-open pattern is an artifact
of the 1500 Hz screen.

**Do not** run the cross-satellite matrix yet. Phase-1 found no candidate
regime, so there is no learnable structure to test for transferability, and the
Iridium signal should be characterised under the reject sweep before it is
carried into a 9 × 9 design.

---

## Claim boundary

No hardware, RF, USRP, firmware, or over-the-air work. No packet, error-rate,
receiver-acknowledgement, or on-orbit result. All values are model-derived
inter-TLE residuals against a later-TLE SGP4 reference, not measured Doppler.
The frozen Paper 1 at `b529c5e` is unmodified and unaffected by this phase.
