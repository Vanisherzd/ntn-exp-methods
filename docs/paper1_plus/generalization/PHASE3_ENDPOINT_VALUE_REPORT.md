# Phase-3 Endpoint-Value Closure Report

Date: 2026-07-27
Question: **does a statistically detectable ~2 % residual improvement produce
any practically meaningful endpoint-budget reduction at the actual real-data
residual scale?**

Answer: **No. It produces exactly zero change in the energy-per-success proxy,
and a guard-band change of 0.03 Hz against a 137 kHz hopping bandwidth.**

Software/model-derived endpoint-budget proxy only. Residuals were **not
rescaled**; the synthetic gate-open residual scale was **not** used. No
packet-level, error-rate, receiver-acknowledgement, over-the-air or on-orbit
claim. `reference_is_measured_truth = false`.

---

## 1. Method

Held-out residual errors are taken directly from the real cells at the
preregistered 1500 Hz screen, then pushed through the Paper 1 proxy chain.

Constants are **back-derived from the committed artifact**
`experiments/exp7_timing_sensitivity/results.json` and verified to reproduce its
`energy_per_success_j` exactly:

| Constant | Value |
|---|---|
| `g0`, `k` | 30 ms, 3 |
| `T_pass` | 240 s |
| `t_rx`, `I_rx`, `V` | 50 ms, 12 mA, 3.3 V |
| `P_tx`, `t_tx` | 10^(14/10) mW = 25.12 mW, 200 ms |
| `F_tol` | 500 Hz |
| `B` (hop bandwidth), `α_g` | 137 kHz, 1 |
| TLE age → σ_t | 1.5 km/day ÷ 7.67 km/s |

Chain: `g_t = g0 + k·σ_t`; `P_t = erfc(g_t/(σ_t√2))`;
`P_f = erfc(F_tol/(σ_f√2))`; `S = (1−P_t)(1−P_f)`;
`E_att = I_rx·V·(g_t+t_rx) + P_tx·t_tx`; `E_succ = E_att/S`.
Frequency-domain proxies: `g = 2·p99(|e|)`, `ρ = Pr(|e|>F_tol)`,
`E_proxy ∝ (1+α_g·g/B)(1+ρ)`.

Only `P_f` depends on the residual branch; `E_att` does not. So the entire
endpoint consequence of a frequency-residual improvement flows through `P_f`.

## 2. Primary case — IRIDIUM 181 @ 8 h (633 held-out pairs)

Selected model `stale_age_ridge`; gate **closed**; held-out
`degradation_pct = −1.937 %` (i.e. `improvement_pct = +1.937 %`).

| Metric | SGP4 | learned | Δ | relative |
|---|---:|---:|---:|---:|
| MAE [Hz] | 0.167276 | 0.164036 | **−0.003240** | −1.94 % |
| p95 \|e\| [Hz] | 0.514618 | 0.509841 | −0.004777 | −0.93 % |
| p99 \|e\| [Hz] | 2.235060 | 2.219540 | −0.015520 | −0.69 % |
| **σ_residual** [Hz] | 0.545315 | 0.542026 | −0.003289 | −0.60 % |
| **guard proxy 2·p99 [Hz]** | 4.470130 | 4.439090 | **−0.031040** | −0.69 % |
| guard as fraction of B | 3.263e-05 | 3.240e-05 | −2.27e-07 | — |
| **outage proxy** | **0** | **0** | **0** | — |
| log10 P_f (rigorous upper bound) | **−182 561** | **−184 783** | −2 222 | — |
| S (joint success) | 0.999460 | 0.999460 | **0** | 0 % |
| E_proxy overhead | 1.0000326 | 1.0000324 | −2.27e-07 | −2.3e-05 % |
| **energy / success [J]** | **0.0159448** | **0.0159448** | **0** | **0 %** |

`F_tol / σ_residual` = **916.9 σ** (SGP4) → **922.5 σ** (learned).
The erfc *argument* `F_tol/(σ_residual·√2)` is 648.3 → 652.3; it is smaller than
the σ-count by exactly √2 and is **not** a number of standard deviations. See
§3a for the definitions.

`P_f` underflows to 0.0 in double precision, so `S`, `E_att` and `E_succ` are
bit-identical. In the log domain the two values are **10^−182561** and
**10^−184783** — genuinely negligible, not merely unresolved. **The detectable
improvement buys nothing.**

## 3. Contrast case — SENTINEL-6B @ 96 h (131 held-out pairs)

Selected model `linear_bias_rate`; gate **closed**; held-out
`degradation_pct = +30.647 %` — clearly harmful.

| Metric | SGP4 | learned | Δ |
|---|---:|---:|---:|
| MAE [Hz] | 0.437516 | 0.571600 | **+0.134085** (+30.6 %) |
| p95 \|e\| [Hz] | 1.284490 | 1.514480 | +0.229991 |
| p99 \|e\| [Hz] | 2.299390 | 2.290000 | −0.009398 |
| **σ_residual** [Hz] | 0.628020 | 0.747398 | +0.119378 |
| guard proxy 2·p99 [Hz] | 4.598790 | 4.579990 | −0.018796 |
| outage proxy | 0 | 0 | 0 |
| log10 P_f (rigorous upper bound) | **−137 644** | **−97 186** | +40 458 |
| S (joint success) | 0.997621 | 0.997621 | **0** |
| **energy / success [J]** | **0.101366** | **0.101366** | **0** |

`F_tol / σ_residual` = **796.2 σ** → **669.0 σ** (erfc argument 563.0 → 473.0).
In the log domain `P_f` rises from 10^−137644 to 10^−97186 — a change of
40 458 orders of magnitude that is still operationally meaningless.

**A 30.6 % worsening is also endpoint-invisible.** This is the symmetric half of
the finding and it matters: at this residual scale the endpoint proxy is
insensitive to residual changes **in both directions**. The proxy is not being
gamed to make the improvement look small.

## 4. How far the residual is from mattering

Inverting `P_f = erfc(F_tol/(σ_f√2))` for the σ_f at which the frequency branch
would register at all:

| Target `P_f` | Required σ_residual |
|---|---:|
| 1e−6 | **102.22 Hz** |
| 1e−3 | 151.95 Hz |
| 1e−2 | 194.11 Hz |

Observed σ_residual is **0.545 Hz** (IRIDIUM 181 @ 8 h). The residual would have to be
**≈ 187× larger** before the frequency branch reaches even a one-in-a-million
miss probability — and a residual correction of 1.9 % changes σ_f by 0.003 Hz.

To close the gap by learning alone, a corrector would need to *increase* the
baseline residual by two orders of magnitude and then remove it. That is not a
correction; it is a different problem.

## 3a. Sigma definitions — disambiguated

Three quantities were previously conflated under "σ". They are now named
explicitly and never share a label:

| Name | Definition | IRIDIUM 181 @ 8 h, SGP4 |
|---|---|---:|
| `sigma_residual_hz` | std of the held-out inter-TLE **frequency** residual error | 0.545315 Hz |
| `f_tol_over_sigma_residual` | `F_tol / σ_residual` — a **count of standard deviations** | **916.90** |
| `erfc_argument` | `F_tol / (σ_residual·√2)` — the argument passed to `erfc`, **not** a σ-count | 648.34 |
| `sigma_t_s` | timing dispersion from TLE age, a **separate axis** | 0.0652 s |

`916.90 = 648.34 × √2`. The earlier text reported 648.3 as "σ away", which was
wrong: it is the erfc argument. The corrected σ-count is **916.9**.

There is no `sigma_total` in this chain: the timing and frequency branches are
evaluated independently as `P_t` and `P_f` and combined multiplicatively in
`S = (1−P_t)(1−P_f)`. They are never summed in quadrature.

## 5. Answer to the primary question

**No.** At the actual real-data residual scale:

- the outage proxy is **identically zero** for both branches (no held-out sample
  exceeds `F_tol`);
- `S`, `E_att` and `E_succ` are **numerically indistinguishable at double
  precision**; in the log domain `P_f` is below 10^−182000 for both branches, so
  the equality is not a masked difference but a genuinely negligible one;
- the guard proxy changes by **0.031 Hz**, i.e. 2.3e−7 of the hopping bandwidth;
- the composite energy-overhead proxy changes by **2.3e−5 %**.

A statistically detectable, temporally robust, multiplicity-surviving ~2 %
residual improvement therefore has **no operational endpoint value whatsoever**
on this data.

This is the number that closes the "you refused a real improvement" objection.
The Evidence Gate declined a branch that, had it deployed, would have changed
the terminal's guard, outage and energy budget by nothing measurable — while
carrying the deployment burden, the audit obligation, and the risk of the
distribution shifting.

## 6. Boundaries

- Two cells only; a proxy chain, not a receiver model.
- `F_tol = 500 Hz` is a representative sub-kHz hop-bin proxy, not a
  standards-derived threshold. The conclusion depends on it: at a tolerance
  ~200× tighter the frequency branch would begin to register. The **relative**
  finding — that a 1.9 % change in σ_f is negligible next to a 648σ margin —
  is robust to plausible re-choices of `F_tol`.
- Timing `sigma_t_s` comes from the Paper 1 TLE-age mapping, lives on a separate
  axis from `sigma_residual_hz`, and is unaffected by the residual branch, so
  timing contributes no differential.
- Nothing here is a packet-level, error-rate or link-layer result.

Outputs: `phase3_endpoint_value/endpoint_value_results.json`,
`fig_real_gain_vs_endpoint_value.pdf/png`.
