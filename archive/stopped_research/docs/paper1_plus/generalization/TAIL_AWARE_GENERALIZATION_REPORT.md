# Tail-Aware Gating and Generalization (Phase 7)

Date: 2026-07-27
Status: **method fixed and implemented; results blocked on data acquisition.**

Scope: software-only, model-derived inter-TLE residuals,
`reference_is_measured_truth = false`; no measured RF truth, no packet,
error-rate, receiver-acknowledgement, over-the-air, or on-orbit result.

---

## 1. What changed structurally

Paper 1 and the earlier exp12 audit could not evaluate tail-aware gates at all:
per-sample learned predictions were never archived, so p95/p99/outage gates were
recorded as `unavailable` rather than as decisions. That limitation is now
**structural rather than accidental** — the Phase 2 pair-level data model keeps
every prediction, so all five gate objectives are computed in the same pass.

The frozen Paper 1 wording ("Tail-aware or cost-aware gates … are left for
future work") remains accurate for the paper. This document is that future work.

---

## 2. Gate objectives compared

All five are evaluated on the **target validation** segment with the same margin
γ = 0.95, exactly as Eq. (6) prescribes for the MAE case:

| Objective | Test | Endpoint meaning |
|---|---|---|
| `mae` | MAE_ml(V) < γ·MAE_phys(V) | average frequency error; stable on small windows |
| `p95` | p95_ml(V) < γ·p95_phys(V) | typical worst-case within a pass |
| `p99` | p99_ml(V) < γ·p99_phys(V) | drives the guard band, g = 2·p99 |
| `outage` | Pr(\|e\|>F_tol)_ml < γ·Pr(\|e\|>F_tol)_phys | fraction of hops outside tolerance |
| `guard_cost` | E_ml < γ·E_phys, E = (1+α_g·2·p99/B)(1+ρ) | combined guard + retransmission pressure |

Defaults: F_tol = 500 Hz, α_g = 1, B = 137 kHz. All are proxy parameters, not
receiver specifications.

**No objective is asserted superior.** The MAE gate is the *primary* only in the
sense that `--primary-gate` defaults to it for continuity with Paper 1; the flag
switches the deployed policy to any other objective without a rerun.

### Degenerate case, handled explicitly

If the physics metric is exactly zero the learned branch cannot beat it by a
margin, so the gate is recorded **closed**. This is not a corner case for this
data: on BLACK KITE the residuals sit far below F_tol = 500 Hz, so the outage
proxy is expected to be 0 for both branches, and the outage gate will report
`closed` for lack of anything to improve — **not** because the learner failed.
Any interpretation must distinguish "closed because the learner lost" from
"closed because the baseline was already perfect on this metric".

---

## 3. What will be reported

`gate_metric_agreement.csv` — every unordered pair of objectives over evaluated
cells:

| Column | Meaning |
|---|---|
| `n_comparable_cells` | cells where both objectives produced a decision |
| `n_agree`, `agreement_pct` | how often the two objectives coincide |
| `a_open_b_closed` | A would deploy, B would refuse |
| `b_open_a_closed` | B would deploy, A would refuse |

Figure: `fig_gate_metric_agreement.pdf/png`, a symmetric agreement heatmap.

Interpretation categories, defined in advance:

- **False-open-style case**: an objective opens on validation while the test
  consequence is a degradation. Counted per objective; the objective with the
  most such cases is the least safe on this data.
- **Missed-open-style case**: an objective stays closed while another objective
  opens *and* the test consequence is an improvement.
- **Target-specific vs transfer split**: agreement is reported separately for
  diagonal and off-diagonal cells. The interesting hypothesis is that tail
  objectives are more conservative than MAE precisely under domain shift, where
  a learner can improve the average while inflating the tail. That is a
  hypothesis, not a finding.

---

## 4. Why this matters to the endpoint argument

The frozen Paper 1 argues that a residual learner should not consume guard,
frequency margin, or energy without evidence, but its gate is MAE-only — the
statistic least sensitive to the tail the endpoint actually pays for. The BK1
diagnostics show p99/median ≈ 12 at every staleness, so an MAE-gated policy and
a p99-gated policy could plausibly disagree.

If they never disagree on real data, the MAE gate is vindicated as a cheap
proxy. If they disagree, the endpoint story needs the tail objective, and that
becomes a genuine Paper 1+ contribution rather than a limitation entry.

Either outcome is publishable; neither is assumed.

---

## 5. Current state

| Item | State |
|---|---|
| Five gate objectives implemented, all on validation | ✅ |
| Per-pair predictions retained | ✅ |
| Agreement matrix implemented | ✅ |
| `gate_metric_agreement.csv` | present, header only |
| `fig_gate_metric_agreement` | not emitted (below satellite threshold) |
| Real-data tail-gate conclusion | ❌ blocked — no raw TLE archive |

Blocking requirement: Phase 1 acquisition. Until then, no tail-aware claim about
real BLACK KITE data may be made, and the frozen Paper 1's statement that
tail-aware gates are future work remains the correct description.
