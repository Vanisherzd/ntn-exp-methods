# Paper 1 — Academic Polish Report (title / figures / writing pass)

_Build commands: `tectonic paper/icc_main.tex` · `tectonic paper/slides_overview.tex` — both SUCCESS._

## Chosen title

**"Evidence-Gated Timing/Frequency Control for LR-FHSS Direct-to-Satellite IoT"**
(ranked decision + 4 alternatives in `PAPER1_TITLE_AND_FIGURE_STRATEGY.md`).
Applied to manuscript and deck title slide. Renders in two lines (was four).

## Page count

- **7 pages including references.** Body text ends page 6; page 7 = Fig. 4 +
  Secs. VI(tail)/VII/VIII + complete references (~⅓ column spare).
- **Hard-6 incl. refs: NOT satisfied** (~1 page over) — exact fallback in
  `PAPER1_PAGE_BUDGET_PLAN.md` Variant B (no evidence block removed).
- **6 body + refs-overflow: nearly satisfied** (~½ column of non-ref content on
  p. 7) — Variant A steps 1–4 close it.
- 0 overfull boxes; all refs/citations resolve.

## Figure blocks (4, none deleted — reorganised)

| # | Block | File | Notes |
|---|---|---|---|
| 1 | Architecture | in-TeX TikZ | redesigned **wide-flat 2-column**: stale TLE → SGP4 ∥ learned candidate → Evidence Gate → selector → endpoint outputs (TX timing guard · frequency margin · energy policy); formulas reduced to gate rule + selector; scope footer kept |
| 2 | Evidence-gate behaviour | `figures_final/fig_gate_evidence.pdf` | 2×2 composite: real BK MAE + degradation (gate closes) ∥ synthetic decision + deployed MAE vs γ; synthetic panels labelled in-panel |
| 3 | Endpoint-control proxies | `figures_final/fig_endpoint_proxies.pdf` | 2×2 composite: exp7 timing sensitivity ∥ exp8 ablation; PGRL bar starred as gate-open synthetic |
| 4 | Conducted IQ | `figures_final/fig_hw_evidence.pdf` | committed max-hold PNG (pixels verbatim, in-image title cropped) + repeatability inset 41.25 ± 0.36 dB / no clip |

Color semantics unified to the deck palette (blue=SGP4, orange=learned,
green=gate, red=unsafe, gray=scope). Old single figures removed from
`figures_final/` (regenerable; BK/gate originals still in `paper/figures/`).

## What was compressed (no numbers changed, no claims weakened)

- Title 17→10 words; abstract trimmed; contributions 7→5 bullets (earlier pass).
- Related Work ~25% total (redundant closing summaries, prior-art sentence merges).
- Background III-A: removed repeated Doppler magnitudes (now cites Sec. I).
- Gate section: "Scope of the gate property" ~40%; stat-role para 2 condensed;
  per-epoch procedure compacted; equations untouched.
- Sec. V: experimental-setup and datasets paragraphs tightened; Table II
  redundant narrative removed (key numbers kept in V-C/V-F); design rules
  compacted.
- Sec. VI hardware: narrative ~25% shorter; all key numbers kept (41.25 ± 0.36,
  43.76, 41.1, ~0.5 dB, −17 dBm, 50 dB, 923.2 MHz).
- Limitations merged into one tight paragraph + one hardware-boundary paragraph.
- refs.bib: dropped 2-line URL from the Semtech tech-report entry.
- Fig. 4 caption/captions rewritten per `PAPER1_CAPTION_REWRITE.md`.

## Guard rails held

- No new experiments; no hardware touched; no numerical result changed
  (figures read committed CSV/JSON/PNG verbatim).
- BK negative result, Evidence Gate definition, proxy explanation, conducted-IQ
  claim boundary, future-work sentence all intact.
- **No-overclaim scan: PASS** (re-run post-edit; 21 paper + 3 slide hits, all
  negations/limitations/future-work/prior-art — `NO_OVERCLAIM_SCAN.md`).

## Slides

Rebuilt (title slide synced to new title; talk figures regenerated in place,
paths unchanged). 12 slides, compiles clean.

## Unresolved / remaining

1. Placeholder author block (pre-existing SUBMISSION BLOCKER).
2. Venue page policy decision → apply Variant A or B from
   `PAPER1_PAGE_BUDGET_PLAN.md` if needed.
3. Cosmetic: Fig. 2(d) legend label "noise-dom." sits near the right axis edge.
4. Commits D–G (`PAPER1_FINAL_COMMIT_PLAN.md`) still not executed; this polish
   pass adds/updates files that fold into commits D/E/F/G naturally.
