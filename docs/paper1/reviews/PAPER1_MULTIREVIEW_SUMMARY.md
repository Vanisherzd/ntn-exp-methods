# Paper 1 — Multi-Review Summary (5 reviewer personas)

Target venue: IEEE ICC workshop, 6-page systems note.
Artifact under review: `paper/icc_main.tex` (6 pages) + `paper/slides_overview.tex`
(16 slides: 12 main + 4 backup), post software-extension integration pass.

Reviewer decisions are simulated, not real referee reports.

---

## Reviewer 1 — ICC Workshop systems reviewer

**Decision: Weak Accept** (Accept if the negative-result framing is the workshop's stated interest)

Strengths
1. The decision problem — deploy or refuse a learned branch *before* transmission — is genuinely unoccupied by the three cited prior-art layers.
2. The Evidence Gate is 2 equations and a chronological split; it is implementable on an MCU-class endpoint and auditable from a log record.
3. Claim discipline is unusually explicit for a workshop paper: `reference_is_measured_truth=false` appears in the abstract, a table caption, and the limitations.

Risks
1. **The engineering payoff is unquantified.** The gate's benefit is "avoided harm", and the avoided harm is expressed only as inter-TLE MAE (0.24–26.9 Hz), never as guard/energy the terminal actually saves. Reviewers will ask "so what does closing the gate buy me in mJ?"
2. **Two satellites.** The generality of a negative result is its weakest axis, and a workshop reviewer will say so even though the paper concedes it.
3. **The proxies are never validated against anything.** Fig. 3 is a self-consistent model chain; nothing anchors `F_tol = 500 Hz` or the 3σ guard to a receiver.

Recommended fix: one sentence in Sec. IV-B mapping the largest real degradation (168 h, 26.9 → 45.3 Hz) through Eq. (11)–(12) into a guard/energy delta, so the "avoided cost" is a number rather than an argument. Not required for submission; required for the journal version.

Advisor-ready: **yes**.

---

## Reviewer 2 — LR-FHSS / NTN domain reviewer

**Decision: Minor revision**

Strengths
1. The narrow-sub-channel motivation for caring about residual frequency error is correct and correctly scoped to pre-compensation.
2. The paper does not overreach into decoding, hopping-sequence, or gateway behaviour — a common failure mode in D2S IoT papers.
3. The 868 MHz carrier convention plus the linear-in-`f_c` scaling note is the right way to keep the result portable to S-band.

Risks
1. **`F_tol = 500 Hz` is asserted, not derived.** It is labelled a proxy, but the whole outage proxy `ρ` and success proxy `S` hang off it. An LR-FHSS reviewer knows the sub-channel raster and will want the number tied to it.
2. **Doppler-rate coupling is stated (Eq. 10) but never exercised.** The reported guard stays a pass-aggregated `p99` scalar, so the pass-aware allocation the equation motivates is not evaluated.
3. **The residual studied is not the residual that hurts.** Oscillator offset and receiver sync dominate real endpoint frequency error; the paper concedes this in the conclusion, but a domain reviewer will note that the isolated TLE component (≤ 27 Hz MAE) is arguably the *least* interesting term.

Recommended fix: keep Risk 3's concession, but move it earlier — it currently lands in the last paragraph of the conclusion, where a hostile reviewer will read it as damage control rather than scoping.

Advisor-ready: **yes**, with the expectation that the advisor asks about `F_tol`.

---

## Reviewer 3 — ML methodology reviewer

**Decision: Accept**

Strengths
1. Chronological 60/20/20 with model selection on validation and a single gate evaluation on test is the correct protocol for this claim; no leakage path is visible.
2. The gate is honestly characterised as a validation-window property with no distribution-shift guarantee, and its two error modes (false open / missed open) are named.
3. The extension's constant-median-bias baseline is the right control, and it loses too — which rules out "the learner was under-regularised" as an explanation.

Risks
1. **Effective sample size is overstated by construction.** 24 in-pass samples per accepted TLE pair are strongly correlated; the caption discloses this, but no clustered/blocked error bar or pair-level statistic is reported anywhere, so "worse at every staleness" has no uncertainty attached.
2. **MAE-only gating on a heavy-tailed residual.** exp10 shows p99/median ≈ 12 at every age. The gate loss is the one statistic least sensitive to the tail the endpoint actually pays for.
3. **Selection over four model families on a single validation window** is itself a variance source; the selected identity flips MLP → ridge at 72 h, which is a symptom of noise-driven selection rather than a modelling insight.

Recommended fix: for Paper 1+, export pair-level predictions and report a paired, pair-clustered comparison (e.g. per-pair MAE difference with a sign test). That single change converts "never beats" from a table observation into a statistical statement.

Advisor-ready: **yes**.

---

## Reviewer 4 — Astrodynamics / TLE reviewer

**Decision: Minor revision**

Strengths
1. The paper is explicit that both `D_ref` and `f_phys` are SGP4 propagations, so the "residual" is inter-solution, not physical — this is stated in the abstract, Sec. II-B, Table I, and the limitations. That is the single most important honesty requirement for this construction, and it is met.
2. The physical account of the residual (observation-arc differences, drag-term updates, fit artifacts, maneuver-like events) is correct and explains the near-zero mean.
3. The `|r| > 1500 Hz` pair rejection with reported reject counts (0, 6, 5, 11, 13, 19) is a defensible maneuver/bad-fit filter and is disclosed.

Risks
1. **The rejection filter removes exactly the learnable part.** Maneuvers and bad fits are the systematic, plausibly-predictable events; discarding them and then reporting that the remainder is unlearnable is close to circular. This is the sharpest available attack on the negative result and the paper does not address it.
2. **BLACK KITE is a young constellation** with ~6.3 h median TLE refresh; a 168 h staleness row therefore spans ~27 refresh intervals and is an atypical operating point, not a stress case a real terminal would sit in.
3. **No orbit-regime diversity.** Both satellites share a similar orbit; drag environment is nearly constant across the dataset, so the result says little about high-drag or eccentric regimes.

Recommended fix: add one clause acknowledging that the `1500 Hz` rejection removes maneuver-like events and that a maneuver-aware variant is future work. This is a genuine gap, cheaply closed — but it costs a line the 6-page budget does not currently have, so it belongs in the journal version. Have the answer ready verbally.

Advisor-ready: **yes, with Risk 1 rehearsed as a Q&A answer.**

---

## Reviewer 5 — Presentation / advisor-talk reviewer

**Decision: Accept**

Strengths
1. The deck's story order is correct for a negative result: problem → gap → hypothesis → method → protocol → **real result** → why it matters → synthetic mechanism → implications → limits → takeaway. The result lands at slide 7, not slide 11.
2. Slide 8's three-column always-learn / never-learn / gate comparison is the single best artefact in the deck for defending "why is this a contribution if it changes nothing?"
3. The two new backup slides now cover the two questions an advisor reliably asks first ("did you try a simpler model?" and "what exactly are you *not* claiming?").

Risks
1. **Slide 7's figure is height-constrained**, so it renders narrower than the slide and its internal axis labels are small on a projector. It is legible on a laptop, marginal in a large room.
2. **The takeaway now competes with four backup slides.** If the speaker walks into backup during the talk, the negative-result punchline gets diluted; backup must stay Q&A-only.
3. **The word "proxy" carries a lot of load.** It appears on slides 10, 13, and 16 with slightly different scopes (energy proxy, ablation proxy, coverage proxy) and an audience may not track which is which.

Recommended fix: none blocking. If projector legibility matters, regenerate `fig_bk_residual_talk.pdf` at a wider aspect ratio so the height constraint stops binding.

Advisor-ready: **yes**.

---

## Consolidated view

| Reviewer | Decision | Blocking? |
|---|---|:--:|
| ICC workshop systems | Weak Accept | no |
| LR-FHSS / NTN | Minor | no |
| ML methodology | Accept | no |
| Astrodynamics / TLE | Minor | no |
| Presentation / advisor talk | Accept | no |

**No reviewer raised a blocking issue.** The three most valuable follow-ups, in
order of reviewer-weighted importance:

1. Pair-level export → pair-clustered paired statistics (ML) and tail-aware gates (LR-FHSS + ML).
2. Address the maneuver-rejection circularity (astrodynamics).
3. Convert avoided harm into a guard/energy number (systems).

All three require the raw TLE rerun. All three are Paper 1+.

**Current paper and slides are advisor-ready.**
