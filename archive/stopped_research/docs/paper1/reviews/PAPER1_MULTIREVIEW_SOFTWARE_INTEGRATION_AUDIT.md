# Paper 1 — Multi-Review Software-Evidence Integration Audit

Date: 2026-07-26
Scope: software artifacts only. No hardware, RF, USRP, firmware, OTA, or
live-satellite activity was performed or claimed. All real values are
model-derived inter-TLE residuals with `reference_is_measured_truth=false`.

Inputs inspected:

- `paper/icc_main.tex`, `paper/slides_overview.tex`
- `docs/paper1/software_extension/SOFTWARE_EXTENSION_MASTER_REPORT.md`
- `docs/paper1/software_extension/RESIDUAL_LEARNABILITY_REPORT.md`
- `docs/paper1/software_extension/STRONGER_BASELINES_REPORT.md`
- `docs/paper1/software_extension/TAIL_AWARE_GATE_REPORT.md`
- `docs/paper1/software_extension/MULTISAT_GENERALIZATION_PLAN.md`
- `docs/paper1/software_extension/PAPER1_SOFTWARE_EXTENSION_INTEGRATION_PLAN.md`
- `docs/paper1/software_extension/SOFTWARE_EXTENSION_INVENTORY.md`
- `experiments/exp10_residual_learnability/{results.json,residual_learnability_summary.csv}`
- `experiments/exp11_stronger_baselines/{results.json,stronger_baselines_summary.csv}`
- `experiments/exp12_tail_aware_gate/{results.json,tail_gate_summary.csv}`
- `experiments/exp13_multisat_generalization/{results.json,generalization_matrix.csv}`

---

## 1. What the software extension results actually support

### 1.1 The "weak learner" objection is materially weakened (exp11)

`stronger_baselines_summary.csv` shows that at **all six** BK1 staleness values
the zero-residual SGP4 baseline has the lowest held-out test MAE of the entire
lightweight family:

| Age | zero | median bias | ridge | RF | GBR | MLP | selected |
|---:|---:|---:|---:|---:|---:|---:|---|
| 8 h | **0.2430** | 0.2438 | 2.4941 | 1.8807 | 4.3976 | 0.3501 | MLP |
| 24 h | **0.8161** | 0.8250 | 4.0449 | 15.8441 | 20.6578 | 0.9109 | MLP |
| 48 h | **1.9433** | 1.9576 | 14.1854 | 21.3059 | 19.9189 | 2.8608 | MLP |
| 72 h | **4.8947** | 4.9404 | 5.9092 | 12.7209 | 15.2894 | 9.3962 | ridge |
| 96 h | **10.1153** | 10.1320 | 11.7663 | 120.5161 | 156.5905 | 22.0370 | ridge |
| 168 h | **26.9243** | 30.2474 | 45.2629 | 62.6705 | 227.7139 | 89.3023 | ridge |

Critically, even the **constant validation-median bias** — the weakest possible
"learned" correction, with essentially no variance cost — loses to zero at every
age. That is the strongest single fact the extension adds: the failure is not a
capacity or tuning artifact.

### 1.2 The residual scale/tail profile is now stated explicitly (exp10)

`residual_learnability_summary.csv` gives the held-out inter-TLE residual profile:
mean stays within ±0.081 Hz at every age while std grows 0.419 → 45.383 Hz and
p99 grows 1.658 → 191.260 Hz over 8 → 168 h; the 168 h max is 519.419 Hz.
This supports two statements already in the paper: the residual is near
zero-mean from the terminal-feature perspective, and it is small relative to
`F_tol = 500 Hz` for the overwhelming majority of samples.

### 1.3 The MAE gate decision is confirmed closed everywhere (exp12)

`tail_gate_summary.csv` reports `mae_gate=closed` for all six real BK1 rows,
`closed` for the two benign synthetic regimes, and `open` only for
`synthetic_extreme_systematic`. No contradiction with the paper.

### 1.4 A multi-satellite pipeline contract now exists (exp13)

`generalization_matrix.csv` reproduces the nine committed rows (six BK1 target,
three BK1→BK2) with degradation recomputed: BK1 spans 11.616 % (24 h) to
68.112 % (168 h); the cross-satellite maximum is 275.106 % (BK1→BK2, 24 h).
Every row is tagged `status=summary_only`.

---

## 2. What the software extension results do **not** support

1. **No fresh training.** exp11 is a re-parse of the committed BK1 report, not a
   retraining run. `dataraw/spacetrack/...` is absent; no propagation was rerun.
2. **No tail-aware real gate.** Learned per-sample predictions and validation
   tails were never archived, so p95/p99, `2·p99` guard-cost, and outage gates
   are `unavailable` on real BK1 — not "also closed".
3. **No autocorrelation / sign-persistence / PSD / train-vs-validation shift.**
   The committed artifacts hold aggregates only; exp10's autocorrelation and
   shift figures are explicit *unavailable-data* panels, not results.
4. **No multi-satellite generalization result.** exp13 is a `--dry-run` over the
   same two satellites; `raw_tle_inputs_available=false`, `dry_run=true`.
5. **No universal unlearnability.** Two satellites, one feature set, one
   staleness grid, one carrier. Richer features or longer arcs could still expose
   structure — that is exactly the case the gate is designed to admit.
6. **No RF/link evidence of any kind.** Nothing in exp10–exp13 touches packets,
   error rates, receiver acknowledgement, over-the-air, or on-orbit contact.

---

## 3. Placement decision: paper / slides / Paper 1+

| Result | Paper | Slides main | Slides backup | Paper 1+ |
|---|:--:|:--:|:--:|:--:|
| Lightweight family (incl. median bias) all worse than SGP4 (exp11) | ✅ one sentence | — | ✅ | — |
| Real MAE gate closed in every row (exp12) | ✅ already present | ✅ already present | ✅ | — |
| Degradation range 11.6–68.1 % BK1, 275.1 % cross-sat (exp13 recompute) | already in Table I | ✅ one line | ✅ | — |
| Residual quantile profile / p99 growth (exp10) | ❌ (no new table) | ❌ | ⚠️ only if asked | ✅ |
| Autocorrelation / sign / PSD | ❌ | ❌ | ❌ (state as unavailable) | ✅ |
| Tail-aware / cost-aware real gate | ❌ | ❌ | ✅ as *not claimed* | ✅ |
| Multi-satellite matrix | ❌ | ❌ | ✅ as *future work* | ✅ |

Rationale for keeping exp10's quantile table out of the paper: it is a
**per-row aggregate of the same held-out set already summarised in Table I**, and
adding it would invite a tail-safety reading that the artifacts cannot support.

---

## 4. Contradictions and risks found

**No contradictions** between the extension artifacts and the manuscript were
found. Every extension row agrees with Table I of `icc_main.tex` to the reported
precision.

Risks identified and their disposition:

| # | Risk | Severity | Disposition |
|---|---|---|---|
| R1 | Reader infers "all gates close on real data" from the MAE result | High | Slides backup slide states the tail gate is *not claimed*; paper limitations already say tail-aware gates are future work |
| R2 | exp11 could be read as a fresh model bake-off | Medium | Paper sentence says "summary-level"; backup slide says "not fresh retraining" |
| R3 | exp13 dry-run could be read as a generalization result | Medium | Rows tagged `summary_only`; contract test enforces it; backup slide says "no new generalization claim" |
| R4 | `PGRL*` in figures reads as an undefined product brand | Medium | Axis label regenerated to `t+f+synth.` from the committed exp8 JSON; captions reworded; `PGRL` no longer appears in either source or either PDF |
| R5 | exp10 p99 = 191 Hz at 168 h vs `F_tol` = 500 Hz invites a "so learning is unnecessary" over-read | Low | Kept out of the paper; the 168 h max (519 Hz) does exceed `F_tol`, so no tolerance-safety claim is made anywhere |
| R6 | 24 in-pass samples per pair are temporally correlated, so `n` is not an independent-trial count | Low | Already disclosed in the Table I caption |

---

## 5. Bottom line

The extension is **corroborating audit evidence, not new evidence**. It earns
exactly one compact sentence in the paper (the "your learner was too weak"
rebuttal) and two backup slides. Everything requiring raw-TLE reruns —
tail-aware gates, autocorrelation, multi-satellite generalization — stays in
Paper 1+.
