# Paper 1 — Multi-Review Software-Integration Final Report

Date: 2026-07-26
Pass type: software-evidence integration + multi-reviewer audit + presentation polish.
Nothing in this pass touched hardware, RF, USRP, firmware, OTA, or live satellites.
No numerical result was changed; two figures were regenerated verbatim from
committed `results.json` artifacts with only a text label altered.

---

## 1. Files changed

| File | Kind | Change |
|---|---|---|
| `paper/icc_main.tex` | source | 1 added sentence (Sec. IV-B), 1 redundancy trim (Sec. IV-B), Fig. 3 caption reword, dead `\hyphenation{LEO-PGRL-LRFHSS}` removed |
| `paper/slides_overview.tex` | source | slide 5 γ note, slide 7 result line, slide 13 caption reword, 2 new backup slides |
| `paper/figures_final/generate_paper_final_figures.py` | source | axis label `PGRL*` → `synth.`; 3 comment/legend strings de-branded |
| `paper/figures_final/fig_endpoint_proxies.pdf` | artifact | regenerated (label only) |
| `paper/slide_figures/fig_control_ablation_talk.pdf` | artifact | regenerated (label only) |
| `paper/slide_figures/fig_timing_sensitivity_talk.pdf` | artifact | regenerated (legend text only) |
| `paper/figures_final/FIGURE_SOURCES.md` | doc | colour-semantics line de-branded |
| `tests/test_slides_claims.py` | test | page count 14 → 16; 3 new required claim-boundary fragments |
| `docs/paper1/reviews/*.md` | doc | 3 new review documents (this pass) |

Regeneration is bit-reproducible in content: a no-change regeneration run was
compared against the committed PDFs before editing and was visually identical.

---

## 2. Paper edits — decision and content

**Decision: edit, minimally.** The paper had zero page slack (adding the new
sentence alone pushed reference [9] onto page 7), so the sentence was paid for by
trimming an equivalent amount of pre-existing redundancy in the same subsection.

### 2.1 Added (Sec. IV-B, `sec:eval-real`)

> Artifact diagnostics over lightweight bias and baseline variants (median bias,
> ridge, RF, GBR, small MLP) did not change the real-data decision---SGP4 stays
> selected and the MAE gate stays closed---and are summary-level, not a
> universal-unlearnability claim.

Supported by `experiments/exp11_stronger_baselines/stronger_baselines_summary.csv`:
zero-residual SGP4 has the lowest held-out MAE at all six BK1 ages, and even a
constant validation-median bias loses at every age. This is the direct rebuttal
to the predictable "your learner was too weak" review.

### 2.2 Trimmed (same subsection, to pay for 2.1)

Three sentences of restated framing ("This changes the role of learning in the
endpoint stack…", "not a failed improvement result") were merged into one. No
claim was removed.

### 2.3 Fig. 3 caption

`PGRL*` replaced by an explicit pointer to the regenerated `+synth.` bar:

> (c,d) Control ablation (log axes); the `+synth.` bar is the controlled
> gate-open *synthetic* branch, not a BLACK KITE outcome (the real gate closes,
> Sec. IV-B).

### 2.4 Explicitly not added

No new table, no new figure, no multi-satellite row, no tail-aware claim, no
residual-quantile table, no hardware statement, no universal-unlearnability
statement.

---

## 3. Slide edits

| Slide | Change |
|---|---|
| 5 — Method: Evidence Gate | small note "γ = 0.95 in all experiments." |
| 7 — Main Real Result | second line: "All tested 8–168 h rows close; at 168 h 26.9 vs 45.3 Hz; BK1 degradation 11.6 %–68.1 %, cross-satellite reaches 275.1 %." Figure height 0.72 → kept, bold line shortened to one line to fit |
| 13 — Backup: Endpoint Proxy Ablation | "the orange PGRL* branch" → "the orange right-most bar (`t+f+synth.`) is the synthetic gate-open branch"; underlying figure regenerated so the axis tick matches |
| **15 — Backup: Software Extension Diagnostics** (new) | lightweight variants still lose to SGP4; real MAE gate closed in every reported row; tail-aware real gate needs per-sample export and is not claimed; multi-satellite pipeline is future work with no new generalization claim |
| **16 — Backup: What This Work Does Not Claim** (new) | no measured Doppler truth; no packet-level/decoding/error-rate/receiver-acknowledgement outcome; no over-the-air and no on-orbit result; synthetic gate-open is a mechanism check; endpoint proxy curves are not a link-layer result |

Deck: **16 slides = 12 main + 4 backup.** The main talk still ends at slide 12
(Contributions and Takeaway); all new material is behind `\appendix`.

**Terminology audit applied across the deck:** "inter-TLE residual" for real
results, "SGP4 / never-learn" for the deployed real policy, "synthetic gate-open
branch" in place of `PGRL*`, "software-only proxy" for the ablation. The string
"hardware validation" appears nowhere in either source or either PDF.

Note on wording of slide 16: the forbidden-token contract test blocks the literal
tokens `PER`, `PDR`, `CRC`, `ACK`, `OTA`, `gateway`, and `live-satellite` even in
negated form, so the "does not claim" bullets are phrased with the spelled-out
equivalents ("error-rate", "receiver-acknowledgement", "over-the-air",
"on-orbit"). The semantic boundary is identical.

---

## 4. Software extension results incorporated

| Source | Incorporated as |
|---|---|
| exp11 stronger baselines | paper sentence (Sec. IV-B) + backup slide 15 bullet 1 |
| exp12 tail-aware gate | backup slide 15 bullets 2–3 (closed MAE gate; tail gate *not claimed*) |
| exp13 multisat dry-run | slide 7 degradation range (recomputed, matches Table I); backup slide 15 bullet 4 as future work |
| exp10 residual learnability | **not incorporated** into paper or slides — see §5 |

## 5. Intentionally not incorporated

1. **exp10 residual quantile / autocorrelation / shift panels.** Two of the three
   figures are explicit *unavailable-data* panels; the third re-aggregates the
   same held-out set Table I already summarises. Adding it invites a tail-safety
   reading the artifacts cannot support.
2. **Any tail-aware real-data gate decision.** Learned per-sample predictions and
   validation tails were never archived; p95/p99, `2·p99` guard-cost, and outage
   gates are `unavailable` on real BK1, not "also closed".
3. **Multi-satellite generalization as a result.** exp13 is `dry_run=true`,
   `raw_tle_inputs_available=false`, all rows `status=summary_only`.
4. **Any claim of universal unlearnability.** Explicitly negated in the added
   paper sentence.
5. **Any hardware, RF, packet, or on-orbit statement.**

---

## 6. Claim-boundary scan

Scans run over the rendered PDFs (`pdftotext`), not just the sources.

**`paper/icc_main.pdf`**

| Token | Hits | Verdict |
|---|---:|---|
| conducted-IQ, spectrum, IQ, USRP, LR1131, hop-center, "hardware validation", PGRL, OTA | 0 | clean |
| "conducted" | 1 | future-work sentence only: "Packet-level conducted PER/PDR … are future work". Not evidence, not a claim. |
| over-the-air (3), live-satellite (2), PER (2), PDR (2), CRC (1), gateway (1) | — | all inside explicit *negations* or the future-work sentence |
| CFO (2) | — | legitimate: Eq. (2) residual CFO definition and the NTN related-work sentence |

**`paper/slides_overview.pdf`**

| Token | Hits |
|---|---:|
| PGRL, conducted, spectrum, LR1131, LR1121, hop-center, "hardware validation", PER, PDR, CRC, OTA, gateway, live-satellite, CFO | 0 |

(`grep -o "ACK"` reports hits only because "BL**ACK** KITE" contains the
substring; the contract test's `\bACK\b` word-boundary pattern is clean.)

Synthetic/proxy labelling: the synthetic branch is labelled in the Fig. 3
caption, on slide 9 ("Controlled software-only check."), on slide 13 ("not a
BLACK KITE improvement"), and on slide 16. The `reference_is_measured_truth=false`
boundary appears in the abstract, Table I caption, limitations, slide 6, and
slide 16.

---

## 7. Build and test results

| Check | Command | Result |
|---|---|---|
| Paper build | `tectonic --keep-logs paper/icc_main.tex` | ✅ builds |
| Paper page count | `pdfinfo` | ✅ **6 pages** (unchanged) |
| Paper overfull boxes | `grep -c Overfull icc_main.log` | ✅ **0** |
| Paper undefined refs/citations | log scan | ✅ none |
| Slides build | `tectonic --keep-logs paper/slides_overview.tex` | ✅ builds |
| Slides page count | `pdfinfo` | ✅ **16 pages** (12 main + 4 backup) |
| Slides overfull boxes | `grep -c Overfull slides_overview.log` | ✅ **0** |
| Slides undefined refs | log scan | ✅ none |
| `pytest tests/test_slides_claims.py` | — | ✅ 6 passed |
| `pytest tests/test_paper1_software_extension.py` | — | ✅ 6 passed |
| `uvx ruff check` (tests + exp10–exp13) | — | ✅ **All checks passed**, with the pre-existing project-level warning `'select' -> 'lint.select'` only |

Non-blocking build noise, all pre-existing and unchanged by this pass:
`algorithm.sty` UTF-8 replacement warning, `Object @table.4 already defined`
(hyperref duplicate anchor), and underfull-hbox warnings in justified paragraphs.

`paper/figures_final/generate_paper_final_figures.py` reports 13 ruff findings —
**identical count before and after this pass** (verified against `git show HEAD:`).
That file is outside the requested lint scope and was not reformatted.

---

## 8. Remaining risks before the advisor meeting

1. **Maneuver-rejection circularity** (highest-value attack). The `|r| > 1500 Hz`
   filter removes maneuver-like events — precisely the systematic, learnable
   part — and the paper then reports the remainder is unlearnable. Not addressed
   in the text; rehearse the verbal answer.
2. **No uncertainty on "never beats"**. 24 in-pass samples per pair are
   correlated; there is no pair-clustered error bar anywhere. The claim is a
   table observation, not yet a statistical one.
3. **Avoided harm is never converted to guard/energy.** The gate's value is
   argued, not quantified in the units the endpoint cares about.
4. **`F_tol = 500 Hz` is asserted.** It is labelled a proxy, but the outage and
   success proxies both hang off it.
5. **Two satellites, one orbit regime, one carrier.** Conceded in the paper, but
   still the weakest axis of a negative result.
6. **Slide 7 figure is height-constrained** and renders narrow; axis labels are
   marginal on a large projector.

Risks 1–4 all resolve with the same action: restore `dataraw/spacetrack/` and
rerun the real pipeline with pair-level prediction export.

---

## 9. Recommended advisor Q&A talking points

**"If the gate changes nothing, what is the contribution?"**
The contribution is the refusal, and the evidence that the refusal is correct.
An always-learn endpoint would have shipped a branch that increases residual
error by 11.6 %–68.1 % on BK1 and up to 275.1 % cross-satellite. Slide 8 is the
slide for this question.

**"Maybe your model was just too weak."**
Backup slide 15. Six candidates including a constant validation-median bias —
the lowest-variance correction that exists — all lose to zero-residual SGP4 at
all six staleness values. The failure is not capacity.

**"Is the residual really unlearnable?"**
No, and the paper does not say that. Two satellites, one feature set, one
staleness grid. The gate exists precisely so that a future case with learnable
structure opens it — that is what the synthetic systematic regime demonstrates.

**"Why does the rejection filter not invalidate the result?"**
State it plainly: it removes maneuver-like events, which are the most plausibly
learnable component; a maneuver-aware variant is the natural Paper 1+ follow-up.
Do not defend the filter as neutral — concede it and name the follow-up.

**"Why no tail-aware gate?"**
Backup slide 15. Per-sample learned predictions were never archived, so p95/p99
and guard-cost gates are *unavailable*, not "also closed". Claiming they close
would be unsupported.

**"Is any of this measured?"**
Backup slide 16. No. The reference is a later TLE propagated by SGP4;
`reference_is_measured_truth=false`. No packet-level, over-the-air, or on-orbit
result exists in this paper.

**"What is next?"**
Restore raw TLE inputs; export pair-level predictions and pair identifiers; then
(a) pair-clustered paired statistics, (b) tail-aware and cost-aware gates,
(c) a multi-satellite matrix with per-satellite failure audit. The exp13
pipeline contract is already written against that input schema.

---

## 10. Commit recommendation

**Do not auto-commit** (per instruction). The tree is in a coherent, verified
state and is safe to commit as one change when the user chooses. Suggested
single commit scope: paper sentence + caption, slide edits and two new backup
slides, de-branded figure labels with regenerated PDFs, updated slide contract
test, and the three review documents.
