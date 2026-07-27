# Phase-0 BLACK KITE Re-derivation Report

Date: 2026-07-27
Trust baseline: `62083b5` (canonical orbital-data ingestion and qualification).
Scope: **four ordered cells only.** No 9-satellite diagonal, no full matrix, no
reject-sensitivity sweep.

Software-only. All values are model-derived inter-TLE residuals with
`reference_is_measured_truth = false`; no measured RF truth, and no packet,
error-rate, receiver-acknowledgement, over-the-air, or on-orbit result. Nothing
was tuned after seeing results. Paper 1 and slides untouched.

---

## 1. Inputs

Canonical GP_HISTORY JSON only; the TLE archive is provenance and was verified
never used as a science input.

| | BLACK KITE-1 | BLACK KITE-2 |
|---|---|---|
| NORAD | 66741 | 68474 |
| SATCAT identity | BLACK KITE-1, 2025-276CD, launch 2025-11-28 | BLACK KITE-2, 2026-067BL, launch 2026-03-30 |
| Response states | gp VALID / satcat VALID / tle VALID | gp VALID / satcat VALID / tle VALID |
| Raw JSON rows | 531 | 308 |
| Duplicates removed | 85 | 56 |
| **Canonical elements** | **446** | **252** |
| Epoch span | 2025-12-18 → 2026-07-26 | 2026-04-13 → 2026-07-26 |
| Median update gap | 6.33 h | 8.04 h |
| p90 gap | 22.13 h | 17.70 h |

BK1's 6.33 h median matches the 6.3 h in the frozen paper. BK2 now reads 8.04 h
rather than 6.4 h, because the archive is longer and canonicalized.

## 2. Pair-level integrity — all invariants passed

Checked on all 24 cells **before** any result was written; a failure would have
aborted the run:

- every test `pair_id` unique; every validation `pair_id` unique
- no train/validation, train/test or validation/test pair-ID overlap
- sign-test N equals the number of unique evaluated pairs in every row
- bootstrap resamples per-pair ΔMAE values, one per accepted TLE pair
- validation and test pairs drawn from the **target** satellite in every cell
- the MAE gate is reproducible from validation metrics alone in every row
- `tle_used_for_science = false` for both objects

## 3. Results — every gate CLOSED in all 24 rows

Pair-level test MAE in Hz at 868 MHz. Δ = learned − SGP4; positive = learned
worse. Gate is the preregistered MAE gate at γ = 0.95, decided on target
validation.

### 3.1 BK1 → BK1 (target-specific)

| Band | tr/va/te pairs | rej tr/va/te | selected | val SGP4 | val learned | val Δ% | test SGP4 | test learned | ΔMAE | test Δ% | win rate | sign p | gate |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|:--:|
| 8 h | 166/92/60 | 0/0/0 | stale_age_ridge | 0.2644 | 0.2937 | +11.09 | 0.2115 | 0.2387 | +0.0271 | **+12.82** | 0.367 | 0.052 | closed |
| 24 h | 196/114/82 | 5/0/0 | linear_bias_rate | 0.8405 | 0.8492 | +1.04 | 0.8159 | 0.8295 | +0.0136 | +1.67 | 0.451 | 0.440 | closed |
| 48 h | 188/118/88 | 4/0/0 | stale_age_ridge | 2.1558 | 2.1670 | +0.52 | 2.4081 | 2.4253 | +0.0172 | +0.71 | 0.386 | **0.042** | closed |
| 72 h | 181/124/87 | 9/0/0 | linear_bias_rate | 4.8612 | 4.8531 | −0.17 | 4.8817 | 4.8797 | **−0.0020** | **−0.04** | 0.540 | 0.520 | closed |
| 96 h | 179/123/89 | 12/0/0 | linear_bias_rate | 9.4765 | 9.4548 | −0.23 | 8.6048 | 8.6118 | +0.0070 | +0.08 | 0.517 | 0.832 | closed |
| 168 h | 171/124/93 | 17/0/0 | stale_age_ridge | 27.3819 | 27.3962 | +0.05 | 29.7439 | 29.7785 | +0.0346 | +0.12 | 0.441 | 0.300 | closed |

### 3.2 BK2 → BK2 (target-specific, **new** — absent from the frozen paper**)

| Band | tr/va/te pairs | rej | selected | val Δ% | test SGP4 | test learned | ΔMAE | test Δ% | win rate | sign p | gate |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| 8 h | 126/32/25 | 0/0/0 | stale_age_ridge | −4.45 | 0.2173 | 0.2169 | −0.0005 | −0.22 | 0.440 | 0.690 | closed |
| 24 h | 145/45/39 | 0/0/0 | ridge | **−4.93** | 0.7805 | 0.8294 | +0.0489 | +6.27 | 0.256 | **0.003** | closed |
| 48 h | 138/45/38 | 0/0/0 | ridge | −4.52 | 1.7450 | 1.8057 | +0.0607 | +3.48 | 0.289 | **0.014** | closed |
| 72 h | 141/44/38 | 0/0/0 | stale_age_ridge | −2.70 | 2.5586 | 2.5718 | +0.0132 | +0.52 | 0.421 | 0.418 | closed |
| 96 h | 150/44/41 | 0/0/0 | stale_age_ridge | −0.70 | 3.4149 | 3.4239 | +0.0089 | +0.26 | 0.390 | 0.211 | closed |
| 168 h | 153/46/42 | 0/0/0 | stale_age_ridge | −0.17 | 17.6908 | 17.6880 | −0.0028 | −0.02 | 0.500 | 1.000 | closed |

**Near-miss worth recording:** at 24 h the learned branch beat SGP4 on
validation by 4.93 %, against the 5 % margin γ = 0.95 requires. The gate closed
by 0.07 percentage points — and the held-out test then came in **6.27 % worse**
with a significant pair-level loss (win rate 0.256, p = 0.003). The margin did
exactly the job it was designed for.

### 3.3 BK1 → BK2 (transfer)

| Band | tr/va/te pairs | selected | val Δ% | test SGP4 | test learned | ΔMAE | test Δ% | win rate | sign p | gate |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| 8 h | 166/32/25 | stale_age_ridge | +3.78 | 0.2173 | 0.2870 | +0.0696 | **+32.03** | 0.160 | **0.0009** | closed |
| 24 h | 196/45/39 | linear_bias_rate | −0.51 | 0.7805 | 0.8330 | +0.0525 | +6.73 | 0.205 | **0.0003** | closed |
| 48 h | 188/45/38 | stale_age_ridge | +3.14 | 1.7450 | 1.7602 | +0.0152 | +0.87 | 0.474 | 0.871 | closed |
| 72 h | 181/44/38 | linear_bias_rate | −0.78 | 2.5586 | 2.5650 | +0.0063 | +0.25 | 0.421 | 0.418 | closed |
| 96 h | 179/44/41 | linear_bias_rate | +1.39 | 3.4149 | 3.4509 | +0.0360 | +1.05 | 0.390 | 0.211 | closed |
| 168 h | 171/46/42 | stale_age_ridge | +0.31 | 17.6908 | 17.7096 | +0.0188 | +0.11 | 0.429 | 0.441 | closed |

### 3.4 BK2 → BK1 (transfer, **new** — never in the frozen paper)

| Band | tr/va/te pairs | selected | val Δ% | test SGP4 | test learned | ΔMAE | test Δ% | win rate | sign p | gate |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|
| 8 h | 126/92/60 | stale_age_ridge | −0.11 | 0.2115 | 0.2115 | −0.0001 | −0.03 | 0.500 | 1.000 | closed |
| 24 h | 145/114/82 | stale_age_ridge | −0.45 | 0.8159 | 0.8085 | −0.0075 | −0.92 | 0.573 | 0.224 | closed |
| 48 h | 138/118/88 | stale_age_ridge | −0.50 | 2.4081 | 2.3942 | −0.0139 | −0.58 | 0.523 | 0.749 | closed |
| 72 h | 141/124/87 | stale_age_ridge | −0.68 | 4.8817 | 4.8585 | −0.0232 | −0.47 | 0.517 | 0.830 | closed |
| 96 h | 150/123/89 | stale_age_ridge | −0.31 | 8.6048 | 8.5891 | −0.0157 | −0.18 | 0.472 | 0.672 | closed |
| 168 h | 153/124/93 | stale_age_ridge | −0.22 | 29.7439 | 29.5925 | **−0.1514** | −0.51 | 0.602 | 0.061 | closed |

**All six rows have negative ΔMAE** — the learned branch is marginally *better*
than SGP4 on test — yet the gate correctly closed, because on validation the
improvement never reached the 5 % margin (best: −0.68 %). No row is significant
at p < 0.05 (closest: 168 h, p = 0.061). These are improvements inside the noise
floor, which is precisely what a conservative margin is supposed to refuse.

## 4. Tail metrics and gate-objective diagnostics

The **outage proxy is 0.000 for both branches in all 24 rows**: every residual
sits far below F_tol = 500 Hz, even at 168 h. The outage and guard-cost gates
are therefore closed for lack of anything to improve, not because the learner
lost — a degenerate case the protocol handles explicitly.

p95/p99 track MAE almost everywhere. One exception matters:

| Cell | Band | MAE gate | **p95 gate** | test p95 SGP4 → learned | test MAE Δ% |
|---|---:|:--:|:--:|---|---:|
| BK2→BK2 | 8 h | closed | **open** | 0.6423 → 0.6425 | −0.22 |
| BK2→BK2 | 24 h | closed | **open** | 2.2397 → 2.3958 | **+6.27** |
| BK2→BK2 | 48 h | closed | **open** | 5.2723 → 5.4746 | **+3.48** |

**This is the first real-data false-open-style evidence in the campaign.** A p95
gate would have deployed the learned branch in three BK2 rows; the held-out
consequence at 24 h and 48 h was a *worse* p95 (+7.0 % and +3.8 %) and a
significant pair-level loss. The preregistered MAE gate refused all three.

This is reported **diagnostically only**. The MAE gate remains the preregistered
primary and was not replaced.

## 5. Reject behaviour

| Object | 8 h | 24 h | 48 h | 72 h | 96 h | 168 h |
|---|---:|---:|---:|---:|---:|---:|
| BK1 rejected pairs (train/val/test) | 0/0/0 | 5/0/0 | 4/0/0 | 9/0/0 | 12/0/0 | 17/0/0 |
| BK2 rejected pairs | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |

Two facts, both material:

1. **Rejection rises with staleness on BK1** (0 → 17 pairs), consistent with
   longer propagation exposing manoeuvre and bad-OD epochs.
2. **Every BK1 rejection falls in the training segment; validation and test lose
   zero pairs. BK2 loses none at all.** So for these four cells the
   `|r| > 1500 Hz` screen cannot have manufactured the held-out result — it never
   touched the held-out data. That is a partial, cell-specific answer to the
   reject-circularity objection; the full sweep remains Phase 6 work and was
   **not** run here.

## 6. Legacy cross-transfer values — superseded, not compared

The frozen paper's BK1→BK2 numbers (73.7 %, 275.1 %, 18.1 % at 8/24/48 h) came
from a different reject threshold (150 Hz), 7 features instead of 10, a
different pairing rule, **no target-side validation window**, and model
selection on the BK2 *test* set. They are not numerically comparable to §3.3 and
are recorded in `metadata.legacy_cross_transfer_superseded`. They appear here
only to explain why direct numerical reproduction is not expected, and are used
neither as inputs nor as selection targets.

## 7. What was not run

No 9-satellite diagonal. No full cross-satellite matrix. No reject-sensitivity
sweep. No tail-gate substitution. No parameter was tuned after results were
seen. Outputs live in
`experiments/exp14_multisat_generalization_matrix/phase0_black_kite/`.
