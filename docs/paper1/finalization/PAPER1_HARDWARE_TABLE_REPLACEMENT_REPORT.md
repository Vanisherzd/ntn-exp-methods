# Paper 1 Hardware Table Replacement Report

## Build
note: Running TeX ...
warning: algorithm.sty:11: 
Invalid UTF-8 byte or sequence at line 11 replaced by U+FFFD.
warning: icc_main.tex:167: Underfull \hbox (badness 3375) in paragraph at lines 150--167
warning: icc_main.tex:167: Underfull \hbox (badness 2042) in paragraph at lines 150--167
warning: icc_main.tex:167: Underfull \hbox (badness 1715) in paragraph at lines 150--167
warning: icc_main.tex:173: Underfull \hbox (badness 3623) in paragraph at lines 168--173
warning: icc_main.tex:425: Underfull \hbox (badness 2717) in paragraph at lines 422--425
warning: icc_main.tex:600: Underfull \hbox (badness 10000) in paragraph at lines 593--600
warning: icc_main.tex:617: Underfull \vbox (badness 10000) has occurred while \output is active
warning: icc_main.tex:647: Underfull \hbox (badness 1622) in paragraph at lines 646--647
warning: icc_main.tex:647: Underfull \hbox (badness 10000) in paragraph at lines 647--647
warning: icc_main.tex:691: Underfull \hbox (badness 2469) in paragraph at lines 678--691
note: Running BibTeX on icc_main.aux ...
note: Rerunning TeX because bibtex was run ...
warning: algorithm.sty:11: 
Invalid UTF-8 byte or sequence at line 11 replaced by U+FFFD.
warning: icc_main.tex:167: Underfull \hbox (badness 3375) in paragraph at lines 150--167
warning: icc_main.tex:167: Underfull \hbox (badness 2042) in paragraph at lines 150--167
warning: icc_main.tex:167: Underfull \hbox (badness 1715) in paragraph at lines 150--167
warning: icc_main.tex:173: Underfull \hbox (badness 3623) in paragraph at lines 168--173
warning: icc_main.tex:425: Underfull \hbox (badness 2717) in paragraph at lines 422--425
warning: icc_main.tex:617: Underfull \vbox (badness 10000) has occurred while \output is active
warning: icc_main.tex:647: Underfull \hbox (badness 1622) in paragraph at lines 646--647
warning: icc_main.tex:647: Underfull \hbox (badness 10000) in paragraph at lines 647--647
warning: icc_main.tex:691: Underfull \hbox (badness 2469) in paragraph at lines 678--691
note: Rerunning TeX because "icc_main.aux" changed ...
warning: algorithm.sty:11: 
Invalid UTF-8 byte or sequence at line 11 replaced by U+FFFD.
warning: icc_main.tex:167: Underfull \hbox (badness 3375) in paragraph at lines 150--167
warning: icc_main.tex:167: Underfull \hbox (badness 2042) in paragraph at lines 150--167
warning: icc_main.tex:167: Underfull \hbox (badness 1715) in paragraph at lines 150--167
warning: icc_main.tex:173: Underfull \hbox (badness 3623) in paragraph at lines 168--173
warning: icc_main.tex:425: Underfull \hbox (badness 2717) in paragraph at lines 422--425
warning: icc_main.tex:617: Underfull \vbox (badness 10000) has occurred while \output is active
warning: icc_main.tex:647: Underfull \hbox (badness 1622) in paragraph at lines 646--647
warning: icc_main.tex:647: Underfull \hbox (badness 10000) in paragraph at lines 647--647
warning: icc_main.tex:691: Underfull \hbox (badness 2469) in paragraph at lines 678--691
warning: warnings were issued by the TeX engine; use --print and/or --keep-logs for details.
note: Running xdvipdfmx ...
warning: Object @figure.1 already defined.
warning: Object @table.1 already defined.
warning: Object @table.2 already defined.
warning: Object @table.3 already defined.
warning: Object @figure.2 already defined.
warning: Object @figure.3 already defined.
warning: Object @table.4 already defined.
note: Writing `paper/icc_main.pdf` (168.515625 KiB)
note: Skipped writing 3 intermediate files (use --keep-intermediates to keep them)

Page count: 6

## Fig. 4 removal check
Source hits:

PDF text hits:

## Table IV check

## Generated files
- PAPER1_HARDWARE_TABLE_REPLACEMENT_REPORT.md
- PAPER1_HARDWARE_TABLE_RISKY_TERM_SCAN.md

## Interpretation
- Fig. 4 should be removed from the main manuscript.
- Table IV should summarize conducted-IQ sanity evidence.
- Generated Fig. 4 files may remain for slides/supplement but are not used in the main paper.
- Hardware result remains conducted IQ-level measurement-path evidence only.
- No commit was made by this script.

## Git status
 M paper/icc_main.tex
 M paper/refs.bib
?? NO_OVERCLAIM_SCAN.md
?? PAPER1_ACADEMIC_POLISH_REPORT.md
?? PAPER1_ARTIFACT_MANIFEST.md
?? PAPER1_CAMERA_READY_POLISH_REPORT.md
?? PAPER1_CAMERA_READY_V2_REPORT.md
?? PAPER1_CAPTION_REWRITE.md
?? PAPER1_CITATION_SUPPORT_AUDIT.md
?? PAPER1_FIG4_REDRAW_REPORT.md
?? PAPER1_FIG4_V3_EVIDENCE_MATRIX_REPORT.md
?? PAPER1_FINALIZATION_STATUS.md
?? PAPER1_FINAL_COMMIT_PLAN.md
?? PAPER1_GATE_AND_CARRIER_FIX_REPORT.md
?? PAPER1_HARD6_COMPRESSION_REPORT.md
?? PAPER1_HARD6_SUBSTANCE_FILL_REPORT.md
?? PAPER1_HARDWARE_TABLE_REPLACEMENT_REPORT.md
?? PAPER1_HARDWARE_TABLE_RISKY_TERM_SCAN.md
?? PAPER1_PAGE_BUDGET_PLAN.md
?? PAPER1_POSITIONING_PASS_REPORT.md
?? PAPER1_REFERENCE_AUDIT.md
?? PAPER1_RELATED_WORK_POSITIONING.md
?? PAPER1_REPRODUCIBILITY.md
?? PAPER1_TITLE_AND_FIGURE_STRATEGY.md
?? PAPER_BUILD_REPORT.md
?? SLIDES_BUILD_REPORT.md
?? paper/assets_external/
?? paper/figures/fig_bk_residual_talk.pdf
?? paper/figures/fig_gate_behavior_talk.pdf
?? paper/figures/generate_slide_evidence_figures.py
?? paper/figures_final/
?? paper/nthu_logo.png
?? paper/slide_figures/
?? paper/slides_overview.tex

## Git diff stat
 paper/icc_main.tex | 872 +++++++++++++++++++++++++++--------------------------
 paper/refs.bib     |  12 +-
 2 files changed, 459 insertions(+), 425 deletions(-)
