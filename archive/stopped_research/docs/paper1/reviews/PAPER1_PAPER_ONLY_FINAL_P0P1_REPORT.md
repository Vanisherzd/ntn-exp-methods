# Paper 1 — Paper-Only Final P0/P1 Revision Report

Date: 2026-07-26
Scope: `paper/icc_main.tex` **only**. `paper/slides_overview.tex` and all slide
figures were not opened for editing in this pass. No experiment run, no
hardware/RF/USRP/firmware/OTA, no numerical result changed, no figure added, no
reference added.

Binding constraint again: **the paper had zero page slack.** Every addition was
paid for by a matched compression of pre-existing restatement. Result still
builds to exactly 6 pages with the full bibliography inside page 6.

Prior fixes explicitly preserved and re-verified in the rendered PDF: gate
protocol (train → validation decides `G` → test reports consequence), RMSE as
diagnostic only, oscillator/RF caveat near Eq. (2), reject-rule limitation near
the `|r| > 1500 Hz` rule, Table I caption `n/24` note.

---

## 1. Task 1 — Abstract cross-satellite weight: **downgraded**

**Before**

> …with strict chronological leakage-free splits, a learned inter-TLE residual
> does *not* beat SGP4 **at any tested staleness (8–168 h), target-specific or
> cross-satellite.**

**After**

> …with strict chronological leakage-free splits, a learned inter-TLE residual
> does *not* beat SGP4 **in any reported target-specific point estimate
> (8–168 h), and limited BK1→BK2 transfer checks give the same closed-gate
> decision.**

The cross-satellite rows no longer sit as a co-equal clause. They are named as
what they are — *limited transfer checks* — which matches the artifact reality
that the compact cross-transfer summary did not preserve per-split counts.
Abstract grew by ~1 line.

---

## 2. Task 2 — Point-estimate wording: **added, at four sites**

Used deliberately sparingly. The negative finding is intact and still stated
assertively; what changed is that the paper now says once, plainly, that these
are point estimates rather than pair-clustered inference.

| Site | Before | After |
|---|---|---|
| Abstract | "at any tested staleness … target-specific or cross-satellite" | "in any reported target-specific point estimate … limited transfer checks" (§1) |
| Intro §3 | "does not beat the open-loop SGP4 / stale-TLE baseline **at any tested staleness**" | "…**in any reported row**" |
| Contribution 1 | "learned inter-TLE residuals **never beat** SGP4" | "**the reported learned inter-TLE point estimates are worse in every row**" |
| Sec. IV-B (opening) | "the learned inter-TLE residual is **worse at every tested staleness**, both target-specific and cross-satellite" | "**the reported point estimates place** the learned inter-TLE residual **above the baseline in every row**, target-specific (BK1, 8–168 h) and in **the limited BK1→BK2 transfer checks**" |
| Sec. IV-B (new clause) | — | "**…closes in all cases; these are point estimates under the leakage-free protocol of Sec. III-D, not pair-clustered inference.**" |
| Conclusion | "the learned correction **never beats** the baseline" | "the learned correction **is worse in every reported row**" |

Left assertive on purpose: the Fig. 2 caption ("degradation positive
everywhere"), Table II, Table IV, and the "always-learn is unsafe" clause. The
paper does not read timid.

---

## 3. Task 3 — Contribution #3 reframed as secondary/illustrative

**Before**

> *Endpoint-budget software proxy:* Eqs. (10)–(13) connect timing/frequency
> uncertainty to guard and energy proxies (Fig. 3); these are software-only
> control proxies, not packet or link validation.

**After**

> *Illustrative endpoint-budget proxy (secondary):* Eqs. (10)–(13) map
> timing/frequency uncertainty to guard and energy proxies (Fig. 3) **only to
> show how residual evidence would pressure endpoint resources**; software-only
> control proxies, not packet or link validation.

The "(secondary)" tag plus "only to show how" removes any reading in which the
proxy study stands beside the real negative finding as a co-equal result.

---

## 4. Task 4 — BK-scale avoided-harm interpretation

**Location: Sec. IV-B, immediately after the 26.9 Hz vs `F_tol` = 500 Hz
sentence** — exactly where a reader would otherwise start converting the MAE
gap into an outage or energy story.

Added:

> Because the 168 h baseline (26.9 Hz) and learned (45.3 Hz) errors both sit far
> below that representative tolerance, the row is not an outage or energy-saving
> comparison; its role is diagnostic. At the observed BLACK KITE residual scale
> a learned correction has no justified endpoint-budget role, so the deployable
> policy is refusal unless future validation evidence changes — the "when not to
> learn" case.

This does three things at once: it forecloses the over-read, it converts the
"avoided harm is unquantified" reviewer risk into an explicit *scale* argument
rather than an unmade quantitative claim, and it ties the result back to the new
title.

The now-redundant sentence it replaced ("The negative result is therefore a
warning against deploying residual ML by default: a residual learner is not an
enhancement module but an untrusted candidate whose deployment burden exceeds
the SGP4 baseline…") was dropped; its surviving half ("the gate keeps validation
noise from becoming extra guard, frequency margin, or retransmission pressure")
is retained verbatim.

---

## 5. Task 5 — Protected content: verified present

Re-checked in the rendered PDF, not just the source:

| Item | Status |
|---|---|
| Oscillator/RF caveat near Eq. (2) — "does not claim it is the dominant RF error source" | ✅ present |
| Reject-rule limitation — "maneuver/outlier-focused extension" | ✅ present |
| Table I caption — "about n/24 per split" | ✅ present |
| Gate protocol — "pre-decided policy", "never decides the gate" | ✅ present |
| RMSE — "corroborating diagnostic, not part of Eq. (6)" | ✅ present |
| `reference_is_measured_truth=false` | ✅ present |
| "no measured Doppler truth, live-satellite contact, … PER/BER/CRC/PDR, or gateway acknowledgement" | ✅ present |

None of these were touched. All compression came from elsewhere.

---

## 6. Task 6 — Compression applied (to pay for §§1–4)

Additions totalled ~9 column-lines and initially pushed five references onto
page 7. Reclaimed by compressing restatement only:

| # | Where | What was compressed | ~lines |
|---|---|---|---:|
| 1 | Intro §§3–4 | merged into one paragraph; dropped the clause restating "the learned branch must demonstrate chronological utility", already stated one sentence earlier | 4 |
| 2 | Conclusion opening | "We recast PHY-layer Doppler compensation as timing- and frequency-uncertainty-aware endpoint control for LR-FHSS D2S IoT under stale orbital information…" → shortened; the full framing already opens the Introduction | 2 |
| 3 | Conclusion | "The controlled synthetic result is a mechanism check showing that the same rule can open under dominant systematic evidence, not a real-data improvement claim." → "The synthetic result is a mechanism check, not a real-data improvement claim." (Sec. IV-C and Table II carry the detail) | 1 |
| 4 | Conclusion | reproducibility-artifact sentence turned into a parenthetical | 1 |
| 5 | Conclusion | "As noted in Sec. II, this isolates the TLE-driven component…" folded into the preceding clause | 1 |
| 6 | Sec. IV-A | the `C1`/`C2`/`C3`/`C4` labels were defined but **never cross-referenced anywhere in the paper**; replaced with a plain list, same content | 1.5 |
| 7 | Sec. IV-B | "Both `D_ref` and `f_phys` are SGP4 propagations: a model-to-model inter-TLE residual, not a measured RF-channel residual." → same statement, pointer to Sec. II-B | 1.5 |
| 8 | Sec. III-C | dropped the inline `erfc(3/√2) ≈ 0.3%` restatement; Sec. IV-E states the 0.3 % floor with its sweep numbers | 1 |
| 9 | Sec. III-D | merged the one-sentence trailing paragraph into the Datasets paragraph; "no receiver feedback" kept | 1.5 |
| 10 | Sec. IV-E | "On the real data, the gate stays closed and the controller equals the baseline (Sec. IV-B)." folded into the preceding clause | 1 |
| 11 | Sec. V | future-work sentence compressed; every boundary term kept | 1 |

**No claim, boundary statement, number, citation, or limitation was removed** —
only sentences restating something the paper says elsewhere. The `balance`
package was **not** added.

---

## 7. Task 7 — Build and QA

| Check | Result |
|---|---|
| `tectonic --keep-logs paper/icc_main.tex` | ✅ builds |
| Page count | ✅ **exactly 6** |
| Overfull boxes | ✅ **0** |
| Undefined refs / citations / multiply-defined labels | ✅ **0** |
| References inside page 6 | ✅ [1]–[9] all on page 6; page 7 does not exist |
| Citation count | ✅ 9, unchanged — no reference added |
| Figures | ✅ 3, unchanged — none added |
| `paper/slides_overview.tex` | ✅ not edited in this pass |
| Slide figures | ✅ not edited in this pass |
| `pytest tests/test_slides_claims.py` + `tests/test_paper1_software_extension.py` | ✅ 12 passed (run as a regression guard; slides unchanged) |

### Claim-boundary scan (`paper/icc_main.pdf`, rendered text)

| Token | Hits | Context |
|---|---:|---|
| conducted, spectrum, USRP, LR1131, hop-center, "hardware validation", PGRL, OTA, "measured Doppler" as a claim | **0** | — |
| over-the-air (4) | 4 | all negation or future-work: abstract "no packet, link-layer, over-the-air, or live-satellite result is claimed"; Sec. II-B "not an RF or over-the-air measurement"; Sec. IV-A "not RF, packet, or over-the-air measurements"; Sec. V "…are future work" |
| live-satellite (2), gateway (1), PER (1), PDR (1), CRC (1) | 6 | all inside the abstract and Sec. V negation lists |
| CFO (2) | 2 | Eq. (2) residual-CFO definition; NTN related-work ToA/CFO sentence |
| LR1121 (1) | 1 | modem block label in the Fig. 1 system diagram — component name, not a measurement claim; **not** LR1131 |

No new hardware / RF / packet / OTA claim. No conducted-IQ or spectrum evidence.

---

## 8. Remaining risks

1. **"Worse in every reported row" still has no attached uncertainty.** The paper
   now says explicitly that these are point estimates, not pair-clustered
   inference — which converts an unstated weakness into a stated scope, but does
   not close it. A pair-clustered sign test needs the raw-TLE rerun.
2. **Maneuver-rejection circularity remains disclosed but unquantified.** Sec.
   III-D names the screening and the follow-up; the residual mass removed by the
   `|r| > 1500 Hz` rule is still unknown.
3. **`F_tol` = 500 Hz is still asserted, not derived** from the LR-FHSS
   sub-channel raster — and §4's new "far below the representative tolerance"
   argument now leans on it a little harder than before. If a reviewer attacks
   the tolerance, the avoided-harm interpretation moves with it.
4. **The proxy scale gap is explained but still visually jarring**: Fig. 3's
   ablation uses a much larger error scale than Table I. Sec. IV-E says so; a
   fast reader can still mis-carry the numbers.
5. **Two satellites, one orbit regime, one carrier.**
6. **Slides now lag the paper slightly.** The deck still says "Learned correction
   is worse at every tested staleness" on slide 7 and "never beats SGP4" on
   slide 12, where the paper now says "in every reported row". Not wrong, but a
   later slides-only pass should sync the phrasing. Out of scope here by
   instruction.

Risks 1, 2 and 3 all resolve with the same action: restore
`dataraw/spacetrack/`, rerun the real pipeline with pair-level prediction
export, and derive `F_tol` from the LR-FHSS grid.

---

## 9. Commit recommendation

**Not committed** (per instruction). Tree is coherent and verified.
