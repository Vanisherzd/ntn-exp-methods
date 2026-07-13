# Slides Academic V2 Report

## Summary

Rebuilt `paper/slides_overview.tex` as a 12-slide academic advisor presentation plus 2 backup slides. The deck now foregrounds the BLACK KITE real-data negative finding, treats the Evidence Gate as a chronological deploy/no-deploy audit rule, and keeps synthetic/proxy material visibly secondary.

## Old-to-new slide mapping

| New slide | Role |
|---|---|
| 1 | Title, subtitle, anonymous authors, one thesis sentence |
| 2 | Motivation and pre-transmission endpoint decision |
| 3 | Related-work gap across LR-FHSS, NTN synchronization, and orbit/physics-ML correction |
| 4 | Residual-learning hypothesis and chronological failure risk |
| 5 | Evidence Gate method and validation-window rule |
| 6 | Experimental protocol: BLACK KITE records, staleness, split, samples, reject rule, model candidates |
| 7 | Main real result with large BLACK KITE MAE/degradation plot |
| 8 | Why a closed gate matters: always-learn vs never-learn vs Evidence Gate |
| 9 | Controlled software-only synthetic mechanism check |
| 10 | Endpoint implications: uncertainty to guard/frequency margin to energy proxy |
| 11 | Limitations and next software campaign |
| 12 | Contributions and final takeaway in paper order |
| Backup 1 | Detailed endpoint proxy ablation |
| Backup 2 | Experimental counts and gate sensitivity |

## Slides removed

- Removed title/footline/top-right/bottom-left NTHU logo usage and watermarks.
- Removed the conducted-IQ artifact backup slide.
- Removed waveform/spectrum/TX-ON/TX-OFF material and conducted-path discussion.
- Removed hardware-demo framing because it does not support the paper's Evidence Gate or residual-learning claims.

## Visual QA scores

Scores are out of 10 across academic clarity, visual hierarchy, projector readability, scientific accuracy, story contribution, and claim-boundary correctness.

| Slide | Score | Note |
|---|---:|---|
| 1 | 9 | Clean title, no logo, no diagram clutter |
| 2 | 8 | Compact endpoint decision diagram and citation footer |
| 3 | 8 | Related-work gap is readable and academic |
| 4 | 8 | Timeline/failure-risk story is clear |
| 5 | 8 | Equation and audit-rule interpretation are central |
| 6 | 9 | Protocol details are readable without the paper |
| 7 | 9 | Real negative result is the visual/narrative peak |
| 8 | 8 | Policy columns avoid table-heavy framing |
| 9 | 8 | Synthetic check is clearly secondary and software-only |
| 10 | 8 | Proxy chain is concise and boundary-labeled |
| 11 | 9 | Limitations and next campaign are direct |
| 12 | 9 | Contribution order matches the paper |
| Backup 1 | 8 | Detailed proxy ablation kept out of main story |
| Backup 2 | 8 | Counts and sensitivity support Q&A |

## Final counts

- Main slides: 12
- Backup slides: 2
- Total PDF pages: 14

## Claim-boundary scan

- Logo references removed from the deck.
- Conducted-IQ, waveform, spectrum, TX-ON, and TX-OFF content removed from the deck.
- Real result described as model-derived inter-TLE residual evidence.
- Synthetic result labeled as controlled software-only mechanism check.
- Endpoint proxy labeled as software-only and not a packet result.
- No packet/PER/PDR/CRC/ACK/OTA/live-satellite/gateway validation claims.
- No edits made to `paper/icc_main.tex`.

## Verification

- `tectonic --keep-logs paper/slides_overview.tex` passed.
- `pytest tests/test_slides_claims.py` passed with 6 tests.
- `uvx ruff check tests/test_slides_claims.py` passed.
- Rendered all 14 slides to PNG and inspected the contact sheet plus key slides 1, 6, 7, 9, 10, 12, and backup 1.
- LaTeX log has no overfull boxes, undefined references, or citation errors. Remaining warnings are underfull line-break warnings on dense explanatory slides.

## Remaining risks

- Slide 7 depends on the existing `fig_bk_residual_talk.pdf`; if that source figure is regenerated with smaller labels, projector readability should be rechecked.
- Backup 1 remains intentionally detailed and should stay backup-only in a 12-15 minute talk.
