# Paper 1 — Final Commit Plan

> Prepared, NOT executed. Four commits, D→G, each independently revertable.
> Nothing here touches raw IQ or ignored binaries.

## Commit D — artifact manifest + finalization docs

```bash
git add PAPER1_ARTIFACT_MANIFEST.md PAPER1_REPRODUCIBILITY.md PAPER1_FINALIZATION_STATUS.md
git commit -m "paper1: add artifact manifest, reproducibility guide, and finalization status"
```

## Commit E — final manuscript + final paper figures

```bash
git add paper/icc_main.tex paper/figures_final/
git commit -m "paper1: finalize manuscript as uncertainty-aware endpoint control with conducted-IQ section and final figures"
```

Covers: title/abstract/contribution reframing, Sec. V-E (exp7/8/9), Sec. VI
conducted-IQ, rewritten limitations, `figures_final/` (5 figures +
`FIGURE_SOURCES.md` + `generate_paper_final_figures.py`).

## Commit F — final slide deck + slide assets (previously held back)

```bash
git add paper/slides_overview.tex paper/slide_figures/ paper/assets_external/ \
        paper/nthu_logo.png paper/figures/fig_bk_residual_talk.pdf \
        paper/figures/fig_gate_behavior_talk.pdf \
        paper/figures/generate_slide_evidence_figures.py
git commit -m "paper1: finalize talk deck with timing/ablation/conducted-IQ result slides and slide assets"
```

## Commit G — build reports + no-overclaim scan

```bash
git add PAPER_BUILD_REPORT.md SLIDES_BUILD_REPORT.md NO_OVERCLAIM_SCAN.md PAPER1_FINAL_COMMIT_PLAN.md
git commit -m "paper1: add paper/slides build reports, no-overclaim scan, and commit plan"
```

## Notes

- `paper/icc_main.pdf` / `paper/slides_overview.pdf` are ignored (`paper/*.pdf`)
  — regenerable via tectonic; not committed.
- Raw IQ (`*.npy`), flash dumps, `output/`, `tmp/`, LaTeX aux stay ignored.
- After G: working tree should be clean except intentionally ignored paths.
