# Paper 1 — Title Decision & Figure Strategy

## 1. Title decision

### Candidates, ranked

| # | Candidate | Words | Keeps gate? | Keeps timing/freq? | Verdict |
|---|---|---|---|---|---|
| 1 | **Evidence-Gated Timing/Frequency Control for LR-FHSS Direct-to-Satellite IoT** | 10 | ✅ | ✅ | **CHOSEN** |
| 2 | Timing/Frequency-Aware LR-FHSS Uplink Control for Direct-to-Satellite IoT | 9 | ❌ | ✅ | loses the paper's core novelty (the gate) |
| 3 | Physics-First Timing/Frequency Control for LR-FHSS Direct-to-Satellite IoT | 9 | partial | ✅ | "physics-first" names the default but not the held-out *test* that is the contribution |
| 4 | Evidence-Gated LR-FHSS Uplink Control for Direct-to-Satellite IoT | 9 | ✅ | ❌ | drops the timing/frequency endpoint-control reframing the paper now leads with |
| 5 | Safe-by-Default LR-FHSS Uplink Control for LEO Direct-to-Satellite IoT | 10 | vague | ❌ | "safe-by-default" is a property, not a mechanism; least searchable |

### Rationale for #1

- Shortest phrase that names **both** pillars: the Evidence Gate (real-data
  negative result + gated deployment) and the timing/frequency endpoint-control
  framing (exp7/exp8 proxies, Fig. 3).
- "under stale orbital information" dropped from the title without loss — the
  abstract's first sentence and Sec. I state it immediately.
- Two-line render in IEEEtran (was four lines), saving title-block height.
- Applied in `paper/icc_main.tex` and `paper/slides_overview.tex` title slide
  should follow at next deck pass (deck currently shows the previous long title —
  see polish report / remaining items).

## 2. Figure strategy (4 evidence blocks, none deleted)

All previous evidence blocks retained; reorganised into composites.

### Fig. 1 — System and evidence-gated control architecture (in-TeX TikZ, 2-col wide-flat)
- **Purpose:** one-glance system story: stale TLE → SGP4 default ∥ learned candidate → Evidence Gate → selector → endpoint outputs (TX timing guard · frequency margin · energy policy).
- **Panels:** single diagram + gray scope footer.
- **Source:** inline TikZ in `icc_main.tex` (redesigned wide-flat; formulas reduced to the gate rule + selector only).
- **Why necessary:** anchors every later section; names the three endpoint outputs the proxies quantify.
- **Reviewer concern answered:** "what exactly is gated, and what does the gate control?"
- **Mandatory.** Compression if page-limited: shrink to 0.85\textwidth (already flat).

### Fig. 2 — Evidence-gate behaviour (composite 2×2, `figures_final/fig_gate_evidence.pdf`)
- **Panels:** (a) real BK held-out MAE baseline vs learned; (b) real degradation all >0 → gate closes; (c) synthetic gate decision vs γ; (d) synthetic deployed MAE vs γ.
- **Source:** `paper/figures_final/generate_paper_final_figures.py`, data verbatim from `docs/review/bk_negative_result_compact.csv` + `gate_stress_compact.csv`.
- **Why necessary:** the paper's headline (real negative result) and the mechanism check in one figure; synthetic panels labelled "synthetic sanity check" in-panel and in caption.
- **Reviewer concern:** "does the gate ever open, and is the real result cherry-picked?"
- **Mandatory** (do not remove the real BLACK KITE panels under any budget).
- Compression: height 3.6 in already; captions carry detail.

### Fig. 3 — Timing/frequency endpoint-control proxies (composite 2×2, `figures_final/fig_endpoint_proxies.pdf`)
- **Panels:** (a) coverage vs σ_t; (b) energy vs σ_t with TLE-age markers; (c) ablation success; (d) ablation energy.
- **Source:** same generator; data verbatim from committed `experiments/exp7…/results.json`, `exp8…/results.json`.
- **Why necessary:** quantifies the endpoint stakes; shows timing uncertainty is paid in guard energy and that joint timing+frequency+learned prediction is the step-change — in the gate-open synthetic regime (marked \*).
- **Reviewer concern:** "why does the terminal care about prediction error at all?"
- **Mandatory.** Compression: drop panel (a) into text (its two numbers are quoted in Sec. V-E).

### Fig. 4 — Conducted IQ-level evidence (`figures_final/fig_hw_evidence.pdf`)
- **Panels:** strongest max-hold TX-ON vs TX-OFF (committed PNG pixels, in-image title strip cropped; no re-analysis) + inset box: "TX-ON − TX-OFF: 41.25 ± 0.36 dB (4 runs), no clipping/saturation".
- **Source:** verbatim `hardware_conducted_iq/figures/fig_hw_maxhold_txon_vs_txoff.png` (committed); inset numbers from committed `repeatability_summary.md`.
- **Why necessary:** the only hardware evidence in the paper; measurement-path proof.
- **Reviewer concern:** "is there any hardware reality behind the proxies?"
- **Mandatory** (do not remove entirely under any budget). PSDs/waterfalls stay in the repo, referenced in text.
- Compression: width 0.9→0.8 columnwidth.

### Page-policy mapping
- **6 pages + references allowed:** keep all 4 blocks (current build).
- **Hard 6 incl. references:** keep all 4 blocks; apply `PAPER1_PAGE_BUDGET_PLAN.md` Variant B (caption shortening, Table II narrative removal, panel drop in Fig. 3) — never remove the real BK panels or Fig. 4.
