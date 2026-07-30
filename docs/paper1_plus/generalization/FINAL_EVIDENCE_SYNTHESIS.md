# Paper 1+ Final Evidence Synthesis

Date: 2026-07-27
Status: **audit and synthesis only.** No new experiment, no new data, no model
refit, no threshold or γ change. Frozen Paper 1 and slides untouched.

All values are model-derived inter-TLE residuals with
`reference_is_measured_truth = false`. No hardware, RF, packet-level,
error-rate, receiver-acknowledgement, over-the-air or on-orbit content.

---

## 1. Cell accounting — phases overlap and must not be summed

| Population | Definition | Cells | Gate opens |
|---|---|---:|---:|
| **Primary target-specific** | 9 satellites × 6 bands, preregistered 1500 Hz | **54** | **0 / 54** |
| **Screening sensitivity** | 9 × 6 × 5 thresholds (superset of the row above) | **270** | **1 / 270** |
| **Cross-direction transfer** | BK1→BK2 and BK2→BK1, 2 × 6 bands, 1500 Hz | **12** | **0 / 12** |
| **Unique configurations** | distinct `(source, target, staleness, screening threshold)` keys | **282** | 1 / 282 |

`282 = 270 + 12`. The Phase-0 diagonals (BK1→BK1, BK2→BK2 = 12 cells) and all 42
Phase-1 cells are **contained in** the 54 target-specific cells at 1500 Hz.
Verified: Phase-0 diagonal `test_degradation_pct` matches Phase-2 @ 1500 Hz with
**0 mismatches**, and both Phase-0-diagonal and Phase-1 key sets are strict
subsets of the Phase-2 @ 1500 key set.

The earlier "336 real-data cells" figure double-counted that overlap and has
been removed everywhere.

## 2. γ frontier — corrected interpretation

Gate: `learned_MAE < γ · SGP4_MAE`. **Larger γ = looser gate** (γ = 1.00 demands
no margin); **smaller γ = stricter** (γ = 0.95 demands 5 %).

| γ | required margin | opens / 54 | improves | worsens | precision |
|---:|---:|---:|---:|---:|---:|
| 1.000 | 0 % | 24 | 16 | 8 | **66.7 %** |
| 0.990 | 1 % | 7 | 4 | 3 | 57.1 % |
| 0.980 | 2 % | 5 | 2 | 3 | 40.0 % |
| 0.975 | 2.5 % | 4 | 1 | 3 | **25.0 %** |
| **0.950** | **5 %** | **0** | 0 | 0 | — |
| 0.900 | 10 % | 0 | 0 | 0 | — |

**Increasing the required validation margin does NOT monotonically improve
held-out selection precision — on this data it degrades it**, from 66.7 % at
γ = 1.00 to 25.0 % at γ = 0.975. A large validation margin is not evidence of
generalization here: the biggest validation gains belong to BLACK KITE-2, and
they do not transfer.

What tightening *does* buy is **absolute harm reduction**: harmful deployments
fall 8 → 3 → 3 → 3 → **0**. γ = 0.95 is not justified by having the best hit
rate — it has none, admitting nothing — but by admitting **zero harmful
deployments**.

**No γ in [0.90, 1.00] cleanly separates the improving Iridium cells from the
harmful BLACK KITE-2 cells.** The harmful trio (BK2 @ 24 h +6.27 %, @ 48 h
+3.48 %, @ 72 h +0.52 %) persists unchanged from γ = 0.99 through γ = 0.975,
while the last Iridium cell drops out by γ = 0.975. Every γ admitting any
Iridium cell admits all three harmful BK2 cells; the first γ excluding the
harmful cells excludes everything.

γ was **not** re-chosen.

## 3. Endpoint tail — log domain, not underflow-masked

`P_f = erfc(F_tol / (σ_residual·√2))` underflows to `0.0` in double past
argument ≈ 26.6. Rigorous log-domain upper bound
`log10 erfc(z) ≤ (−z² − ln(z√π))/ln 10`:

| Cell | branch | σ_residual [Hz] | log10 P_f (upper bound) |
|---|---|---:|---:|
| IRIDIUM 181 @ 8 h | SGP4 | 0.545315 | **−182 561** |
| | learned | 0.542026 | **−184 783** |
| SENTINEL-6B @ 96 h | SGP4 | 0.628020 | −137 644 |
| | learned | 0.747398 | −97 186 |

The reported zeros are **true underflow of genuinely negligible quantities**, not
a masked difference. `P_f` differs between branches by 2 222 orders of magnitude
in the primary case — and both are below 10^−182000, so `S`, `E_att` and
`E_succ` are **numerically indistinguishable at double precision** and remain so
under any plausible re-computation.

Wording "exactly zero probability" has been replaced throughout with
"numerically indistinguishable at double precision", with the log-domain values
quoted alongside.

## 4. σ definitions — disambiguated

Three quantities were conflated under "σ". Now named and never sharing a label:

| Name | Definition | IRIDIUM 181 @ 8 h, SGP4 |
|---|---|---:|
| `sigma_residual_hz` | std of the held-out inter-TLE **frequency** residual error | 0.545315 Hz |
| `f_tol_over_sigma_residual` | `F_tol / σ_residual` — a **count of σ** | **916.90** |
| `erfc_argument` | `F_tol / (σ_residual·√2)` — the `erfc` argument, **not** a σ-count | 648.34 |
| `sigma_t_s` | timing dispersion from TLE age — a **separate axis** | 0.0652 s |

`916.90 = 648.34 × √2`. The earlier "648.3 σ away" was wrong; the σ-count is
**916.9**. No value was altered to force agreement — only the labels were
corrected, and the code now emits both fields under unambiguous names.

There is no `sigma_total`: timing and frequency are evaluated independently as
`P_t` and `P_f` and combined multiplicatively in `S = (1−P_t)(1−P_f)`. They are
never summed in quadrature.

## 5. Screening bias — final wording

| Outcome (1500 Hz vs no screening) | Cells |
|---|---:|
| screening improves learned relative performance | **36 / 54** |
| screening worsens it | **3 / 54** |
| effectively unchanged (< 0.1 pp) | **15 / 54** (14 remove no pairs at all) |

Median shift **−1.259 pp**, IQR [−9.265, 0.000].

Adopted framing: **"Screening generally improves the learned branch's relative
performance, while many apparent gains are screening-sensitive."**

The formulation "most improvements are artifacts" has been removed: it is not
directly supported. What is supported is (a) the aggregate direction above, and
(b) that 30 of 54 satellite × band combinations flip the sign of held-out
improvement across thresholds.

## 6. Final evidence table — three independent axes

| Case | A. Statistically detectable | B. Deployment margin (γ = 0.95) | C. Endpoint value |
|---|---|---|---|
| **IRIDIUM 181 @ 8 h**, 1500 Hz | **Yes.** −1.94 % degradation, win rate 0.615, sign-test p < 1e−15, Holm p < 1e−15, block-bootstrap CI excludes zero, sign stable at all five thresholds | **No.** validation gain 1.37 % vs 5 % required; gate **closed** | **Negligible, and resolved.** guard 4.470 → 4.439 Hz (−0.031 Hz, 2.3e−7 of B); outage 0 → 0; E/success delta indistinguishable at double precision (log10 P_f −182 561 → −184 783) |
| **IRIDIUM 177 @ 168 h, 150 Hz screen** | **No.** raw p = 0.0075 but **Holm p = 1.00**; block-bootstrap CI **includes** zero; adjacent thresholds contradict (500 Hz +2.16 % worse, none +0.07 % worse) | **Yes at that sensitivity point only.** validation gain 18.36 % → gate **open**. Not the preregistered threshold; discards 40.3 % of pairs | **Not computed** (Phase-3 evaluated two cells). From stored artifacts: outage **0 for both branches**; guard 2·p99 92.55 → 84.60 Hz (−8.6 %, but 6.8e−4 → 6.2e−4 of B). Full E/success not evaluated. |
| **BLACK KITE-2 @ 24 h**, 1500 Hz (representative harmful) | **Yes, in the harmful direction.** +6.27 % degradation, win rate 0.256, p = 0.0034 (Holm p = 0.497), block CI excludes zero | **No at γ = 0.95** (validation gain 4.93 %, margin 5 % — missed by 0.07 pp). **Would deploy at γ ≥ 0.975** | **Not computed.** outage 0 for both; p95 2.240 → 2.396 Hz, p99 2.901 → 3.076 Hz — worse, but far below `F_tol` |
| **SENTINEL-6B @ 96 h**, 1500 Hz (harmful contrast) | Yes, harmful: +30.65 %, win rate 0.038 | No; gate closed | **Negligible, and resolved.** E/success delta indistinguishable at double precision **despite a 30.6 % worsening** — the proxy is insensitive in *both* directions at this scale |

The SENTINEL-6B row is what makes the IRIDIUM 181 row credible: the endpoint
proxy is not constructed to shrink improvements — it is insensitive to residual
changes of either sign at this residual scale.

## 7. Final Paper 1+ thesis

> Across nine LEO objects spanning five orbital regimes and six staleness bands
> from 8 to 168 h, a validation-gated endpoint policy declined learned inter-TLE
> residual correction in **0 of 54** target-specific configurations at the
> preregistered screening rule, and in **0 of 12** cross-direction transfer
> configurations. Across a five-threshold screening sweep (270 configurations)
> exactly **one** cell opened the gate; that opening is screening-sensitive,
> contradicted by adjacent thresholds, and does not survive multiple-comparison
> correction. Screening generally improves the learned branch's relative
> performance, while many apparent gains are screening-sensitive. Where a
> statistically detectable improvement does survive every diagnostic — IRIDIUM
> 181 at 8 h, ≈1.9 % — it produces **no resolvable endpoint-budget change**: the
> frequency tolerance sits ≈917 residual standard deviations away, and the
> miss-probability differs between branches at the 10^−182000 level.
>
> The contribution is a three-axis separation — **statistical detectability ≠
> deployment-margin satisfaction ≠ endpoint value** — and a gate that declines
> such branches from validation evidence alone, without observing the held-out
> consequence.

This is stronger than a generalization matrix: it converts the frozen Paper 1's
single-family refusal into a nine-object, five-regime, screening-audited result
with a **quantified reason** the refusal is correct rather than merely
conservative.

## 8. Is any further science justified before drafting?

**No.** The remaining questions are writing questions, not measurement
questions.

| Candidate | Verdict |
|---|---|
| Cross-satellite 9 × 9 matrix | **Not justified.** Transfer asks whether learnable structure moves between objects; no deployable structure was found to move. It would take 270 target-specific configurations to ~2430 to test an unsupported premise. |
| Deeper Iridium characterisation | **Not justified now.** §6 already resolves its endpoint value as negligible. Characterising it further has no claim to serve. |
| Endpoint value for the two uncomputed cells | **Optional, low value.** Both have outage identically zero, so the conclusion is already determined; computing them would add two rows, not a finding. |
| More satellites / regimes | **Not justified.** The limiting factor is not sample size — it is that the residual is ~10^2.9 below the tolerance that would make any correction matter. |
| γ re-selection | **Explicitly not.** §2 shows no γ separates the improving from the harmful cells, and every frontier cell is endpoint-null. |

**Recommendation: proceed to Paper 1+ manuscript drafting.** The evidence base is
complete for the thesis in §7, and the two genuinely open items — the
uncomputed endpoint rows and the untested transfer question — are both
answerable in the manuscript as scoped limitations rather than by further
computation.
