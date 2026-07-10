# Paper Build Report (Paper 1 finalization)

> **Superseded in part by `PAPER1_ACADEMIC_POLISH_REPORT.md` (title/figure/writing
> pass):** title is now "Evidence-Gated Timing/Frequency Control for LR-FHSS
> Direct-to-Satellite IoT"; figures consolidated to 4 blocks (architecture
> wide-flat, gate-evidence 2×2, endpoint-proxies 2×2, conducted-IQ); still
> 7 pages including references, but body text now ends on page 6 and references
> end on page 7. Page-budget fallbacks: `PAPER1_PAGE_BUDGET_PLAN.md`.

## Command

```bash
tectonic paper/icc_main.tex
```

(latexmk/pdflatex/xelatex also present on this machine; tectonic is the repo's
documented builder — see README.)

## Result

- **Status:** SUCCESS (exit 0, PDF written)
- **Output:** `paper/icc_main.pdf` (~242 KB)
- **Page count:** **7 pages including references** (references end ~1/3 into the
  final column; body content ends near the top of page 7)
- **Unresolved references/citations:** none (all `\ref`/`\cite` resolve; 13 bib
  entries render)
- **Overfull boxes:** none
- **Underfull boxes:** 5 minor Underfull `\hbox`/`\vbox` warnings (contribution
  list and two justified paragraphs) — cosmetic only
- **Other warnings:** benign `algorithm.sty` UTF-8 byte warning (package file,
  not ours); xdvipdfmx `Object @figure.N already defined` warnings from
  hyperref+IEEEtran interaction — no visual effect

## Structure (final)

I Introduction · II Related Work · III Background and System Model (=
Background/Motivation + System Model & Problem Formulation) · IV Evidence-Gated
Endpoint Control · V Evaluation (incl. V-E Timing/Frequency Sensitivity,
Ablation, and Endpoint Footprint) · VI Preliminary Conducted-IQ Evidence ·
VII Limitations and Future Work · VIII Conclusion

Figures: 1 architecture (TikZ) · 2 BK negative result · 3 gate vs γ ·
4 timing sensitivity (exp7) · 5 control ablation (exp8) · 6 conducted IQ
TX-ON/TX-OFF. Tables: I BK held-out MAE · II synthetic stress.

## Next fixes required

1. **SUBMISSION BLOCKER (pre-existing TODO in tex):** placeholder author block
   must be replaced with real authors, or the venue's anonymous format.
2. **Page budget:** currently 7 pages incl. references after aggressive
   trimming. If the target venue enforces a hard 6 pages *including* references,
   the documented fallback (in priority order, no numbers changed):
   - move Fig. 3 (gate vs γ) to a supplement and keep the one-sentence summary
     already in Sec. V-D (saves ~0.5 col);
   - merge Table II into text (three regimes, six numbers) (saves ~0.4 col);
   - shrink Fig. 2 to 0.8 columnwidth (saves ~0.15 col).
   If the venue allows 6 pages + references overflow, the current build already
   complies.
3. Optional polish: resolve the two cosmetic underfull paragraphs.

## Numerical integrity

No numerical results were changed during finalization. Tables I/II carried over
verbatim; new Sec. V-E numbers come from committed
`experiments/exp{7,8,9}_*/results.json`; Sec. VI numbers match
`PAPER_HARDWARE_EVIDENCE_TEXT.md` (41.25 ± 0.36 dB, 43.76 dB control, ~0.5 dB
negative control, 41.1 dB artifact-masked).
