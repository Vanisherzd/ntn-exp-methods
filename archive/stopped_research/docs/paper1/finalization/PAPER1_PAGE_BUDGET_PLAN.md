# Paper 1 — Page-Budget Plan

## Current state (after academic-polish pass)

- **Current total: 7 pages including references** (`tectonic paper/icc_main.tex`).
- Body text ends on **page 6**; page 7 = Fig. 4 + Sec. VI tail + VII/VIII + all
  references (references end with ~⅓ column spare).
- Figure blocks: 4 (architecture wide-flat 2-col; gate-evidence 2×2 composite;
  endpoint-proxies 2×2 composite; conducted-IQ single-column).
- 0 overfull boxes; all refs resolve.

## Variant A — venue allows 6 pages body + references overflow

**Target: all non-reference content within 6 pages.** Current gap: Sec. VI tail
(+Fig. 4) and VII/VIII occupy ~1 column on page 7.

Exact changes (apply in order until content fits 6; no numbers change):

1. Fig. 2 / Fig. 3 composite height 3.6→3.3 in (`generate_paper_final_figures.py`,
   two `figsize` lines) — saves ~0.2 page.
2. Fig. 4 width 0.9→0.8 columnwidth — saves ~3 lines.
3. Shorten Fig. 2/3 captions to one sentence + panel list (drafts in
   `PAPER1_CAPTION_REWRITE.md` can lose their second sentence; keep the
   synthetic/proxy markers) — saves ~6 lines.
4. Compress Sec. VII paragraph 2 into paragraph 1 (single limitations paragraph)
   — saves ~8 lines.

**Do NOT cut:** core contribution sentence (Sec. I), BK negative result
(Table I + Fig. 2a,b + Sec. V-B), Evidence Gate definition (Eqs. 4–7),
timing/frequency proxy explanation (Sec. IV-C + V-E), conducted-IQ claim boundary
(Sec. VI last sentence), future-work sentence.

## Variant B — hard 6 pages including references

**Gap: ~1 page.** Apply Variant A steps 1–4, plus:

5. Merge Table II into text: three regimes → one sentence with the six numbers
   (base→ML MAE, guard 14 120→950 Hz, outage 0.814→0.008); delete the table
   float and its caption — saves ~0.35 page. (Redundant narrative around
   Table II was already removed in this pass; key numbers stay in Sec. V-C and
   V-F.)
6. Drop Fig. 3 panel (a) (its two headline numbers — miss ≈3σ floor, overhead
   0.03→2.5% — are quoted verbatim in Sec. V-E text); regenerate as 1×3 or 2+1
   layout — saves ~0.15 page.
7. Compress Sec. II-A/II-C by one sentence each and Sec. V-F paragraph 1 —
   saves ~0.15 page.
8. If still >6: shrink Table I to \scriptsize with 3 pt tabcolsep (numbers
   unchanged) — saves ~6 lines.

**Never (any budget):** remove the real BLACK KITE negative result, remove the
conducted-IQ evidence entirely, unlabel the synthetic panels, or weaken any claim
boundary.

## Venue decision table

| Venue policy | Status | Action |
|---|---|---|
| 7 pages incl. refs (e.g., 6+1 overlength) | ✅ compliant now | none |
| 6 pages + unlimited refs | ~0.5 col over | Variant A steps 1–4 |
| Hard 6 incl. refs | ~1 page over | Variant A + B steps 5–8 |
