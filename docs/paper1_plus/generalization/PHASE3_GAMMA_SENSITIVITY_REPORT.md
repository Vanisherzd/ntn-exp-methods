# Phase-3 γ Sensitivity Report

Date: 2026-07-27
**γ = 0.95 remains the primary preregistered rule. No new γ is chosen.**
This is a declared diagnostic, reported alongside the primary result — never a
replacement for it.

Dataset: the preregistered **1500 Hz** screening rule, **54** target-specific
satellite × band cells (9 satellites × 6 bands). Gate recomputed from the
already-recorded validation metrics; no model was refit and no numeric result
changed.

Software-only, `reference_is_measured_truth = false`.

---

## 1. Frontier

A cell opens when `MAE_ml(V) < γ · MAE_phys(V)`. "Improves" / "worsens" is the
held-out consequence, which the gate never sees.

| γ | required margin | cells opening | opened & **improves** held-out | opened & **worsens** held-out | precision | median held-out degradation of opened cells |
|---:|---|---:|---:|---:|---:|---:|
| 1.000 | none | **24** | 16 | 8 | 66.7 % | −0.275 % |
| 0.990 | 1 % | 7 | 4 | 3 | 57.1 % | −0.219 % |
| 0.980 | 2 % | 5 | 2 | 3 | 40.0 % | +0.516 % |
| 0.975 | 2.5 % | 4 | 1 | 3 | 25.0 % | +1.998 % |
| **0.950** | **5 %** | **0** | **0** | **0** | — | — |
| 0.900 | 10 % | 0 | 0 | 0 | — | — |

## 2. What the frontier shows

**Direction, stated correctly.** The gate is `learned_MAE < γ · SGP4_MAE`, so a
**larger γ is a looser gate** (γ = 1.00 demands no margin at all) and a **smaller
γ is stricter** (γ = 0.95 demands a 5 % improvement).

**Increasing the required validation margin does NOT monotonically improve
held-out selection precision. On this data it degrades it.**

Reading the table from loosest to strictest, the fraction of opened cells that
actually help on held-out data falls monotonically:

| direction | γ | required margin | precision |
|---|---:|---:|---:|
| loosest | 1.000 | 0 % | **66.7 %** |
| ↓ | 0.990 | 1 % | 57.1 % |
| ↓ | 0.980 | 2 % | 40.0 % |
| ↓ | 0.975 | 2.5 % | **25.0 %** |
| strictest tested that opens nothing | 0.950 | 5 % | — (0 open) |

At γ = 0.975 three of four deployments would have been harmful. The median
opened cell flips from helping (−0.275 %) to hurting (+1.998 %) between γ = 0.99
and γ = 0.975.

This contradicts the natural intuition that demanding a larger validation margin
selects better candidates. It does not, because a large *validation* margin is
not evidence of generalization here: the cells with the biggest validation gains
are BLACK KITE-2's, and those gains do not transfer to held-out data.

**What tightening the margin does buy is absolute harm reduction**, which is the
property that actually matters for a deployment gate:

| γ | harmful deployments |
|---:|---:|
| 1.000 | 8 |
| 0.990 | 3 |
| 0.980 | 3 |
| 0.975 | 3 |
| **0.950** | **0** |

Precision and absolute harm are different quantities. The preregistered γ = 0.95
is not justified by having the best hit rate — it has no hit rate, because it
admits nothing — it is justified by admitting **zero harmful deployments** on
this data.

**The worst deployments avoided.** γ = 0.99 and γ = 0.975 would both deploy
BLACK KITE-2 @ 24 h (**+6.27 %** held-out degradation) and @ 48 h (+3.48 %).
Those are the two largest harms in the whole 54-cell set, and both are on cells
whose validation evidence looked *better* than average.

**Even γ = 1.00 is a coin flip.** With no margin at all, 24 cells open and 8 of
them worsen. A gate with zero margin is not a filter.

## 3. Which cells open, and where

At γ = 1.00, the 16 improving cells are led by IRIDIUM 181 (168 h −2.23 %, 8 h
−1.94 %, 96 h −1.64 %, 72 h −0.99 %, 48 h −0.44 %) and IRIDIUM 177 (168 h
−1.30 %, 96 h −0.52 %). The 8 worsening cells are led by BLACK KITE-2 (24 h
+6.27 %, 48 h +3.48 %, 72 h +0.52 %).

As γ tightens, the Iridium cells drop out **before** the BLACK KITE-2 cells do,
because Iridium's validation margins are small (0.6–2.0 %) while BLACK KITE-2's
are larger but do not generalize. The harmful trio — BLACK KITE-2 @ 24 h
(+6.27 %), @ 48 h (+3.48 %), @ 72 h (+0.52 %) — persists unchanged from γ = 0.99
through γ = 0.975, while the last Iridium cell (IRIDIUM 177 @ 168 h) is gone by
γ = 0.975.

**So no γ in [0.90, 1.00] cleanly separates the improving Iridium cells from the
harmful BLACK KITE-2 cells.** Every γ that admits any Iridium cell also admits
all three harmful BLACK KITE-2 cells, and the first γ that excludes the harmful
cells (0.95) excludes everything.

## 4. Endpoint value of the opened cells

Phase-3's endpoint closure applies directly:

- IRIDIUM 181 @ 8 h — the strongest improving cell at γ = 1.00 — produces
  **zero** change in energy-per-success and a 0.031 Hz guard change against a
  137 kHz bandwidth (`PHASE3_ENDPOINT_VALUE_REPORT.md` §2).
- SENTINEL-6B @ 96 h shows a **+30.6 %** degradation that is *also* endpoint-null.

Since every opened cell in this table has |degradation| ≤ 6.27 % on residuals of
order 0.2–0.6 Hz, and a 30.6 % change was already shown to be endpoint-invisible
at that scale, **the endpoint value of every cell on this frontier is nil**,
whichever γ is used.

That is the decisive point: the γ question is **moot**. No setting of γ in
[0.90, 1.00] converts this data into an operationally meaningful deployment,
because the underlying residual is ~650 σ below the tolerance that would make
any of it matter.

## 5. Three axes, kept separate

| Axis | Status on this data |
|---|---|
| **Statistical detectability** | Real. IRIDIUM 181 @ 8 h: +1.94 %, win rate 0.615, survives Holm at all five screening thresholds, block-bootstrap CI excludes zero. |
| **Deployment margin (γ)** | Not met. 1.94 % against the 5 % the preregistered rule requires; 0 of 54 cells open at γ = 0.95. |
| **Endpoint value** | Nil. Zero change in energy-per-success; guard change 2.3e−7 of the hop bandwidth. |

These are independent. A result can be detectable and margin-failing and
endpoint-null simultaneously — and here it is all three. Conflating the first
with the third is the error the Evidence Gate exists to prevent.

## 6. Conclusion

γ = 0.95 is **not** shown to be the optimal margin by this analysis, and no such
claim is made. What is shown is narrower and more useful:

1. **Increasing the required validation margin does not monotonically improve
   held-out selection precision.** Precision falls from 66.7 % (γ = 1.00) to
   25.0 % (γ = 0.975) as the margin tightens.
2. Tightening the margin does monotonically reduce the *absolute* number of
   harmful deployments (8 → 3 → 3 → 3 → 0), which is the property a deployment
   gate is for.
3. The largest held-out harms (+6.27 %, +3.48 %) would be deployed by every
   γ ≥ 0.975 tested, and are eliminated only at γ = 0.95.
4. No γ in the tested range separates the improving cells from the harmful ones.
5. Every cell on the frontier is endpoint-null regardless, so the choice of γ
   has no operational consequence on this dataset.

γ was not re-chosen. The primary result stands at γ = 0.95: **0 of 54 cells
open at the preregistered 1500 Hz screening rule.**

Outputs: `phase3_endpoint_value/gamma_frontier.json`,
`fig_gamma_deployment_frontier.pdf/png`.
