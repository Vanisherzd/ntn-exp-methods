# Paper 1 — Slides-Only P0 Synchronization Report

Date: 2026-07-26
Scope: `paper/slides_overview.tex` and `tests/test_slides_claims.py` **only**.
`paper/icc_main.tex` was not opened for editing; it was rebuilt as a regression
check only. No paper figure or slide figure was touched (all slide-figure labels
were already correct after the earlier de-branding pass). No experiment run, no
hardware/RF/USRP/firmware/OTA, no numerical result changed, no new claim added.

Purpose: close the phrasing gap opened by the paper-only P0/P1 pass, where the
paper moved to point-estimate language and the deck still said "worse at every
tested staleness" and "never beats SGP4".

---

## 1. Slide-by-slide edits and their paper mapping

### Slide 5 — Method: Evidence Gate

**Added** (small grey note under the chronological-split timeline, left column):

> Training fits the candidates. `G` is fixed on validation; the test segment only
> reports consequences. MAE is the gate loss; RMSE is a diagnostic, not part of
> the rule.

Maps to two paper facts in one line:

- Sec. IV-A: "Training fits the candidates; the model family and the gate
  decision are fixed on the chronological validation segment; the held-out test
  segment reports the consequence of that pre-decided policy and never decides
  the gate."
- Sec. IV-A: "RMSE is a corroborating diagnostic, not part of Eq. (6)."

Placed below the timeline rather than near the equation, so the displayed
`G = 1[...]` stays uncluttered. The pre-existing `γ = 0.95 in all experiments.`
note was kept and its spacing tightened to make room.

### Slide 6 — Experimental Protocol

**Added** (grey note under the protocol flow, directly beneath the
`Reject pair if any |r| > 1500 Hz` box):

> The real claim is conditional on accepted non-outlier pairs; `|r| > 1500 Hz`
> pairs are excluded and left for a maneuver/outlier extension.

Maps to Sec. III-D: "The negative finding is thus conditional on accepted
non-outlier inter-TLE pairs under this |r| > 1500 Hz screening; rejected
high-residual pairs are treated as non-nominal and left for a
maneuver/outlier-focused extension."

Positioned adjacent to the rule it qualifies — same design decision as in the
paper.

### Slide 7 — Main Real Result

| | |
|---|---|
| **Headline before** | "Learned correction is **worse at every tested staleness**. At 168 h: SGP4 26.9 Hz versus 45.3 Hz learned; gate closed, deploy SGP4 / never-learn." |
| **Headline after** | "**All reported BLACK KITE point estimates close the gate**; deploy SGP4 / never-learn." |
| **Sub-line after** | "Reported point estimates are worse in every row; BK1 degradation 11.6 %–68.1 %. **Cross-satellite rows (up to 275.1 %) are a limited transfer check; per-split counts were not preserved.** Point estimates under the leakage-free protocol; **not pair-clustered inference.**" |

Maps to Sec. IV-B: "the reported point estimates place the learned inter-TLE
residual above the baseline in every row … and in the limited BK1→BK2 transfer
checks … these are point estimates under the leakage-free protocol of Sec. III-D,
not pair-clustered inference."

The 275.1 % figure is now inside a subordinate clause explicitly labelled a
limited transfer check with unpreserved counts — it is no longer a headline
number. The 26.9 / 45.3 Hz pair moved off this slide and onto slide 8, where it
now carries the diagnostic punchline instead of reading as a performance gap.

Layout: the sub-line was collapsed from three manually broken lines into one
flowing paragraph (removing two ragged inter-line gaps), and the figure was
returned to `0.66\textheight` after briefly dropping to `0.60`.

### Slide 8 — Why a Closed Gate Matters

**Added** (Navy box between the three policy columns and the takeaway):

> At BK1 168 h, 26.9 → 45.3 Hz is still ≪ `F_tol` = 500 Hz: this is a
> refusal/audit result, not an energy-win claim.

Maps to the Sec. IV-B paragraph added in the paper-only pass: "Because the 168 h
baseline (26.9 Hz) and learned (45.3 Hz) errors both sit far below that
representative tolerance, the row is not an outage or energy-saving comparison;
its role is diagnostic."

This is the single most important addition for advisor Q&A: it pre-empts "so how
much energy does the gate save?" with the correct answer — none, and that is the
point.

### Slide 12 — Contributions and Takeaway

Order unchanged; weight and wording synced to the paper's contribution list.

| # | Before | After |
|---|---|---|
| 1 | **Real-data negative finding.** "…learned inter-TLE residual correction **never beats** SGP4 at tested staleness values." | **Real-data negative finding.** "…**the reported inter-TLE point estimates are worse than SGP4 in every row**." |
| 2 | **Chronological evidence-gated deploy/no-deploy rule.** "On real BLACK KITE data, the gate closes…" | **Evidence-gated deploy/refuse audit rule.** "**`G` is decided on chronological validation**; on real BLACK KITE data the gate closes…" |
| 3 | **Software-only endpoint proxy with explicit limits.** | **Secondary: illustrative endpoint-budget proxy.** "…**software-only** coverage proxies, not packet or field results." |

Maps to the paper's contribution list, where #3 now reads "*Illustrative
endpoint-budget proxy (secondary)*". #3 is now unmistakably subordinate to #1
and #2 on the slide as well.

### Slide 16 — Backup: What This Work Does Not Claim

**Kept unchanged.** Audited against the six required boundaries:

| Required boundary | Slide text | ✓ |
|---|---|:--:|
| no measured Doppler truth | "No measured Doppler truth; the reference is a later TLE propagated by SGP4." | ✅ |
| no packet / error-rate / link validation | "No packet-level, decoding, error-rate, or receiver-acknowledgement outcome." | ✅ |
| no receiver acknowledgement | same bullet | ✅ |
| no over-the-air / on-orbit result | "No over-the-air transmission and no on-orbit result." | ✅ |
| synthetic open is mechanism check only | "The synthetic gate-open case is a mechanism check, not a real-data improvement." | ✅ |
| proxy curves are not link-layer validation | "Endpoint proxy curves are software-only; they are not a link-layer result." | ✅ |

**Deliberate wording note.** The contract test blocks the literal strings
`link validation` and `link-layer validation`, plus `PER`, `PDR`, `CRC`, `ACK`,
`OTA`, `gateway`, and `live-satellite` — *even inside a negation*. The slide
therefore expresses the same six boundaries with spelled-out equivalents
("error-rate", "receiver-acknowledgement", "over-the-air", "on-orbit", "not a
link-layer result"). The semantic boundary is identical; only the literal tokens
differ.

### Contract test — `tests/test_slides_claims.py`

Updated to track the slide edits rather than block them:

- Contribution markers #2 and #3 updated to the new bold headers.
- Three new required fragments added, so a future edit cannot silently drop the
  synced protocol language:
  `"the test segment only reports consequences"`,
  `"not pair-clustered inference"`,
  `"left for a maneuver/outlier extension"`.

Page-count assertion unchanged at 16.

---

## 2. Not changed, and why

| Item | Reason |
|---|---|
| `paper/icc_main.tex` | Out of scope by instruction; rebuilt as regression only |
| Paper figures, slide figures | No slide uses a wrong label — `t+f+synth.` was already corrected in the de-branding pass |
| Slide 11 "MAE gate is not tail-aware" | Already correct and consistent with the paper |
| Slide 15 backup | Already states the tail-aware real gate is not claimed and there is no new generalization claim |
| Slide 9 synthetic mechanism check | Already labelled "Controlled software-only check." |
| Slide 10 proxy-scale caveat | Added in the previous pass; still correct |

---

## 3. Build and QA

| Check | Command | Result |
|---|---|---|
| Slides build | `tectonic --keep-logs paper/slides_overview.tex` | ✅ builds |
| Slide count | `pdfinfo` | ✅ **16** (12 main + 4 backup; ≤ 16 as required) |
| Slides overfull boxes | log scan | ✅ **0** |
| Paper regression build | `tectonic --keep-logs paper/icc_main.tex` | ✅ builds |
| Paper page count | `pdfinfo` | ✅ **exactly 6** |
| Paper overfull boxes | log scan | ✅ **0** |
| Undefined refs / citations / multiply-defined (both logs) | python scan | ✅ **0** |
| `pytest tests/test_slides_claims.py` | — | ✅ 6 passed |
| `pytest tests/test_paper1_software_extension.py` | — | ✅ 6 passed |
| `uvx ruff check tests/test_slides_claims.py` | — | ✅ All checks passed (only the pre-existing project-level `'select' -> 'lint.select'` deprecation warning) |

### Claim-boundary scan — `paper/slides_overview.pdf` (rendered text)

**Zero** hits for: `LR1131`, `LR1121`, `conducted`, `spectrum`,
`hardware validation`, `PGRL`, `OTA`, `live-satellite`, `gateway`, `CFO`,
`PDR`, `CRC`, `hop-center`, `link validation`, `link-layer validation`,
`packet success`.

`PER` as a standalone token: **0**. (A case-insensitive substring search reports
9 hits, all inside ordinary words — "o**per**ation", "ex**per**iments",
"**per** accepted", "**per**-split", "**per** successful". The contract test's
case-sensitive `\bPER\b` pattern returns an empty list.)

No positive packet / error-rate / receiver-acknowledgement / over-the-air /
on-orbit / measured-Doppler claim appears anywhere in the deck.

---

## 4. Deck ↔ paper consistency status

| Paper fact | Deck location |
|---|---|
| Title "When Not to Learn: Evidence-Gated Residuals for LR-FHSS D2S IoT" | Slide 1 ✅ |
| `G` fixed on validation; test reports consequences | Slide 5 ✅ (new), Slide 12 #2 ✅ (new) |
| RMSE diagnostic only | Slide 5 ✅ (new) |
| Reported point estimates, not pair-clustered inference | Slides 7, 12 ✅ (new) |
| Conditional on accepted non-outlier pairs after `|r| > 1500 Hz` | Slide 6 ✅ (new) |
| 26.9 → 45.3 Hz ≪ `F_tol`; refusal/audit, not energy win | Slide 8 ✅ (new) |
| Contribution #3 secondary / illustrative | Slide 12 ✅ (new) |
| Cross-satellite = limited transfer check, counts not preserved | Slide 7 ✅ |
| γ = 0.95 | Slide 5 ✅ |
| `reference_is_measured_truth=false` | Slide 6 ✅ |
| Synthetic = mechanism check only | Slides 9, 16 ✅ |
| Proxy scale illustrative, not BK residual scale | Slide 10 ✅ |

No known remaining paper/deck divergence.

---

## 5. Remaining advisor Q&A risks

1. **"Worse in every reported row" still has no error bar.** The deck now says
   "not pair-clustered inference" out loud, which converts a hidden weakness
   into a stated scope — but a sharp advisor will ask for the sign test anyway.
   Answer: 24 in-pass samples per pair are correlated, ≈ n/24 independent pairs;
   the paired test needs the raw-TLE rerun with pair-level prediction export.
2. **"What did the `|r| > 1500 Hz` screen throw away?"** Slide 6 discloses the
   conditionality but not the removed residual mass. Reject counts are on backup
   slide 14 (0, 6, 5, 11, 13, 19); the energy those pairs carried is unknown.
   Concede it and name the maneuver-aware follow-up — do not defend the filter
   as neutral.
3. **"If everything is ≪ 500 Hz, why does any of this matter?"** This is the
   likeliest question triggered by the new slide 8 box. Answer: it matters
   because an always-learn endpoint would still have shipped the learned branch
   and spent guard/frequency margin on it; the gate is what makes the refusal
   auditable rather than accidental. Slide 8's three-column comparison is the
   visual for this.
4. **`F_tol` = 500 Hz is asserted, not derived** from the LR-FHSS sub-channel
   raster — and slide 8's new punchline leans on it. If the tolerance is
   challenged, the "≪ 500 Hz" framing moves with it.
5. **Slide 7's figure is height-constrained** and renders narrower than the
   slide; internal axis labels are marginal on a large projector. Fixing it
   properly means regenerating `fig_bk_residual_talk.pdf` at a wider aspect
   ratio — out of scope for this pass.
6. **Two satellites, one orbit regime, one carrier.** Unchanged; conceded on
   slide 11.

---

## 6. Commit recommendation

**Not committed** (per instruction). Tree is coherent and fully verified.
