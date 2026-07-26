# Paper 1 — Protocol-Consistency and Reviewer-Defense Patch Report

Date: 2026-07-26
Scope: text-only patch to `paper/icc_main.tex` and `paper/slides_overview.tex`.
No experiment was run, no hardware/RF/USRP/firmware/OTA touched, no numerical
result changed, no figure added, no reference added.

Constraint that shaped every edit: **the paper had zero page slack.** Every
addition below was paid for by a matched trim of pre-existing redundancy, and
the result still builds to exactly 6 pages.

---

## 1. Task 1 — Gate protocol consistency

### 1.1 The defect

`Sec. IV-A (Experimental Setup)` asserted that the gate was decided on the test
segment, which directly contradicted Eq. (6), where `G` is defined on the
validation window `V`. A methodology reviewer would read this as either
test-set leakage into the deploy decision, or as an undefined second gate.

**Before** (`paper/icc_main.tex`, Sec. IV-A):

> Learned candidates are ridge regression, random forest, gradient boosting, and
> a small MLP, selected on the chronological validation segment with **the gate
> evaluated once on the held-out test segment**. A window is supported only if
> the selected model beats the zero-residual baseline on **held-out MAE** by the
> gate margin (γ = 0.95) **and also improves RMSE**.

**After**:

> Learned candidates are ridge regression, random forest, gradient boosting, and
> a small MLP. **Training fits the candidates; the model family and the gate
> decision are fixed on the chronological validation segment; the held-out test
> segment reports the consequence of that pre-decided policy and never decides
> the gate.** A window is supported only if the selected model beats the
> zero-residual baseline on *validation* MAE by the gate margin (γ = 0.95);
> RMSE is a corroborating diagnostic, not part of Eq. (6).

### 1.2 Companion consistency edits

Three further sites used "held-out" where "validation" is the precise word, and
two implied the test values caused the gate to close.

| Site | Before | After |
|---|---|---|
| Abstract | "a chronological **held-out window** beats the baseline by a margin γ" | "a chronological **validation window** beats the baseline by a margin γ" |
| Sec. IV-B, first sentence | "…**so the gate** of Eq. (6) **closes** in all cases." | "…and the **validation-decided gate** of Eq. (6) closes in all cases." |
| Table I caption | "The gate closes in every row **because the learned inter-TLE residual is worse than the physics baseline**." | "The gate **is decided on the validation segment** and closes in every row; **the test columns report the consequence of that decision.**" |
| Table II header | "**Held-out** evidence (γ = 0.95)" | "**Validation** evidence (γ = 0.95)" |
| Conclusion | "deployed only when a chronological **held-out window** beats the baseline" | "deployed only when a chronological **validation window** beats the baseline" |

Left unchanged because already correct: Sec. III-A ("Let `V` be a chronological
*validation* window, strictly later than the training span and strictly earlier
than the held-out test span, so that no future TLE leaks into model selection"),
the Fig. 1 caption, the contribution bullet, and Sec. III-D.

**Resulting semantics, now stated consistently in all six places:** train fits →
validation selects the family *and* computes `G` via Eq. (6) → test reports the
consequence of an already-fixed policy. No future/test TLE enters selection or
the gate.

### 1.3 Note on the artifacts

Table I's `Gate` column is unaffected: the learner is worse on both validation
and test at every row, so the decision recorded in the committed artifacts is
identical under the corrected description. This patch fixes the *description* of
the protocol, not the protocol or any number.

---

## 2. Task 2 — RMSE: **demoted, not silently deleted**

The gate is now **MAE-only**, matching Eq. (6) exactly.

RMSE was not simply deleted, because `docs/paper1/software_extension/SOFTWARE_EXTENSION_INVENTORY.md`
records the implementation as making an "MAE/RMSE gate decision" — deleting all
mention would have made the paper describe a *more permissive* criterion than
the code without saying so. The chosen wording keeps the paper truthful in both
directions:

> …beats the zero-residual baseline on *validation* MAE by the gate margin
> (γ = 0.95); **RMSE is a corroborating diagnostic, not part of Eq. (6)**.

Since every row fails the MAE test alone, no reported decision depends on which
reading is taken. `RMSE` now appears exactly once in the rendered paper, in the
sentence above.

---

## 3. Task 3 — Oscillator / RF caveat moved earlier

**Placement: end of Sec. II-A, immediately after Eq. (2)** — the first point in
the paper where `f_osc` appears, so the scoping lands before the reader can form
the wrong expectation.

Added:

> Equation (2) separates the orbital-prediction term from endpoint RF errors.
> Oscillator offset, receiver synchronisation, and channel effects can dominate
> the absolute RF residual; this paper isolates only the TLE-driven inter-TLE
> component and does not claim it is the dominant RF error source.

**Duplication control:** the near-identical two-sentence version in the
conclusion was collapsed to a back-reference, so the caveat is stated once in
full and pointed at once:

- Before: "This separates orbital uncertainty from other endpoint RF errors. Oscillator offset, receiver synchronization, and channel effects may dominate the absolute RF residual; our experiments isolate only the TLE-driven component observable from public orbital data. A practical stack should combine this gate with oscillator calibration and a tail-aware deployment loss."
- After: "As noted in Sec. II, this isolates the TLE-driven component from other endpoint RF errors; a practical stack should combine the gate with oscillator calibration and a tail-aware deployment loss."

Net page cost of Task 3: approximately zero.

---

## 4. Task 4 — Reject-rule limitation

**Placement: Sec. III-D (Datasets and Splits)**, immediately after the causality
sentence and in the same paragraph that introduces the screening rule — so the
limitation is adjacent to the rule it qualifies rather than buried in Sec. V.

Added:

> The negative finding is thus conditional on accepted non-outlier inter-TLE
> pairs under this |r| > 1500 Hz screening; rejected high-residual pairs are
> treated as non-nominal and left for a maneuver/outlier-focused extension.

One sentence, no apology, no universal-unlearnability claim, and it names the
follow-up rather than conceding the point. This is the paper's answer to the
sharpest available attack (the screening removes exactly the maneuver-like
events that are most plausibly learnable) — see
`PAPER1_MULTIREVIEW_SUMMARY.md` §Reviewer 4, Risk 1.

---

## 5. Task 5 — Effective sample transparency

Table I caption only; no column added, table width unchanged.

- Before: "$n$ counts 24 in-pass samples per accepted TLE pair; samples are temporally correlated."
- After: "$n$ counts 24 in-pass samples per accepted TLE pair, **so the independent TLE-pair count is about $n/24$ per split** and samples within a pair are temporally correlated."

Reader can now convert e.g. the 168 h row (2448/3168/2640) to roughly
102/132/110 independent TLE pairs without arithmetic guesswork.

---

## 6. Task 6 — Title decision: **changed**

| | |
|---|---|
| Before | Evidence-Gated Residual Learning for LR-FHSS Direct-to-Satellite IoT Endpoint Control |
| After | **When Not to Learn: Evidence-Gated Residuals for LR-FHSS D2S IoT** |

Rationale:

1. **Consistency.** The old title promises "Residual Learning … Endpoint
   Control"; the paper's primary result is a refusal to learn. The new title
   states the contribution the evidence actually supports.
2. **Layout.** Shorter, and it renders cleanly in the IEEEtran title block. The
   6-page budget was verified after the change.
3. `D2S` is expanded in the abstract's first sentence and the keyword list
   retains the full "Direct-to-Satellite IoT" for indexing.

No reference, label, or cross-reference depends on the title. Slides synced (§7).

---

## 7. Task 7 — Slide changes

| Slide | Change |
|---|---|
| 1 (title) | Title synced to "When Not to Learn: / Evidence-Gated Residuals for LR-FHSS D2S IoT". The negative-result line promoted from `\large` plain to `\Large\bfseries` in Navy, so it now outranks the author block visually. Closing line shortened to stop it wrapping to two lines. |
| 7 (Main Real Result) | Cross-satellite number de-emphasised: 275.1 % moved out of the headline clause into a parenthetical, followed by "Cross-satellite rows (up to 275.1 %) are transfer checks; per-split counts were not preserved." Figure height 0.72 → 0.66 `\textheight` to fit the added line without an overfull box. |
| 10 (Endpoint Implications) | Caveat box extended: the required contract fragment "Software-only control proxy; not a packet result." is preserved verbatim, followed by "Proxy scale is illustrative: it is not the BLACK KITE residual scale and not a link result." |
| 15 (Backup: Software Extension Diagnostics) | Unchanged. Verified it still states the tail-aware real gate "needs per-sample prediction export; not claimed here" and "no new generalization claim". |
| 16 (Backup: What This Work Does Not Claim) | Unchanged. Verified against the forbidden-token contract. |

**Slide 1 note:** the instruction's subtitle ("When not to learn residuals from
BLACK KITE TLE history.") was conditional on the title staying unchanged. Since
the title now opens with "When Not to Learn", adding that subtitle would have
repeated the title on the same slide, so the negative-result line was made
prominent instead. Say the word and it can be added back.

Deck remains **16 slides = 12 main + 4 backup**; the main talk still ends at
slide 12.

---

## 8. Task 8 — Build and QA

| Check | Result |
|---|---|
| `tectonic --keep-logs paper/icc_main.tex` | ✅ builds |
| Paper page count | ✅ **exactly 6** |
| Paper overfull boxes | ✅ **0** |
| `tectonic --keep-logs paper/slides_overview.tex` | ✅ builds |
| Slides page count | ✅ **16** |
| Slides overfull boxes | ✅ **0** |
| Undefined refs / citations / multiply-defined labels (both logs) | ✅ **0** |
| `pytest tests/test_slides_claims.py` | ✅ 6 passed |
| `pytest tests/test_paper1_software_extension.py` | ✅ 6 passed |
| `uvx ruff check` (tests + exp10–exp13) | ✅ All checks passed — only the pre-existing project-level `'select' -> 'lint.select'` deprecation warning |

### Claim-boundary scan (rendered PDFs)

`paper/slides_overview.pdf`: **zero** hits for conducted, spectrum, USRP, LR1131,
LR1121, hop-center, "hardware validation", PGRL, OTA, live-satellite, gateway,
CFO, PER, PDR, CRC.

`paper/icc_main.pdf`:

| Token | Hits | Context — all verified |
|---|---:|---|
| conducted, spectrum, USRP, LR1131, hop-center, "hardware validation", PGRL, OTA | **0** | — |
| live-satellite (2), gateway (1), PER (1), PDR (1), CRC (1) | 5 | every one inside an explicit negation ("no packet, link-layer, over-the-air, or live-satellite result is claimed"; "no measured Doppler truth, live-satellite contact, standards-compliant LR-FHSS decoding, PER/BER/CRC/PDR, or gateway acknowledgement") |
| CFO (2) | 2 | legitimate: Eq. (2) residual-CFO definition, and the NTN related-work sentence on ToA/CFO estimation |
| LR1121 (1) | 1 | modem block label in the Fig. 1 system diagram — a component name, not a measurement claim; **not** LR1131 |

Improvement over the previous pass: the token "conducted" is now **0** in the
paper (it previously appeared once in a future-work sentence, since compressed).

No new hardware / RF / packet / OTA claim was introduced. No conducted-IQ or
spectrum evidence reintroduced. No new reference added.

---

## 9. Page-budget accounting

Additions (Tasks 1, 3, 4, 5) totalled roughly 12 lines of column text and
initially pushed the bibliography onto page 7. Paid for by:

| Trim | Lines |
|---|---:|
| Intro §4 paragraph compressed (dropped a sentence duplicating the "always learn" gap paragraph) | ~3 |
| Conclusion: removed the sentence duplicating Sec. III-A's re-check/revert statement; compressed the audit-rule sentence | ~4 |
| Conclusion: oscillator caveat replaced by a back-reference (Task 3) | ~3 |
| Sec. II-B: merged the two overlapping "not an RF measurement" sentences | ~1.5 |
| Limitations: compressed the future-work ordering sentence | ~1 |
| Title shortened | ~0–1 |

**No claim, boundary statement, or number was removed** — only restatements of
claims made elsewhere in the paper.

---

## 10. Remaining reviewer risks

Ranked by how likely a referee is to raise them.

1. **Maneuver-rejection circularity (partially addressed).** Sec. III-D now
   discloses the conditionality and names the follow-up, but the paper still
   does not quantify what fraction of the residual mass was screened out. The
   reject counts (0, 6, 5, 11, 13, 19) are reported, but not the residual energy
   they carried. Requires a raw-TLE rerun.
2. **No uncertainty on "never beats".** The caption now lets a reader compute
   ≈ `n/24` independent pairs, but there is still no pair-clustered error bar or
   sign test. "Worse at every staleness" remains a table observation, not a
   statistical statement.
3. **`F_tol = 500 Hz` is asserted, not derived** from the LR-FHSS sub-channel
   raster, and both the outage proxy `ρ` and the success proxy `S` depend on it.
4. **Avoided harm is never expressed in guard or energy units** — the gate's
   payoff is argued in MAE, not in the mJ/guard terms the endpoint cares about.
5. **Two satellites, one orbit regime, one carrier.** Conceded in the paper;
   still the weakest axis of a negative result.
6. **Proxy-scale confusion (mitigated, not eliminated).** Sec. IV-E and slide 10
   now both state the ablation uses a deliberately larger error scale than
   Table I, but a fast reader can still carry Fig. 3's numbers into a BLACK KITE
   reading.

Risks 1, 2 and 4 all resolve with the same action: restore
`dataraw/spacetrack/`, rerun the real pipeline, and export pair-level
predictions and pair identifiers.

---

## 11. Commit recommendation

**Not committed** (per instruction). Tree is coherent and fully verified. When
committing, this patch and the preceding multi-review pass form one logical
change: protocol wording, RMSE demotion, two new caveats, title change, slide
sync, and the review documents.
