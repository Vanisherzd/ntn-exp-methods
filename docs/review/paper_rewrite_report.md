# Paper Rewrite Report — Simulation / Trace-Driven Evidence-Gated Controller

*Records the pivot of `paper/icc_main.tex` away from hardware validation to a
software-only, model-derived, evidence-gated controller paper. No hardware/RF
command was run for this rewrite; `dataraw/` was not touched.
`reference_is_measured_truth=false`.*

*Generated: 2026-06-14 UTC. Branch `experiment-bk2-tle-residual`.*

---

## 1. New title

`Physics-First Evidence-Gated Uplink Control for LR-FHSS Direct-to-Satellite IoT`

## 2. Sections changed (full-body rewrite of `paper/icc_main.tex`)

| Section | Change |
|---|---|
| Title | Replaced uncertainty-head title with the physics-first evidence-gated title. |
| Abstract | Fully rewritten: stale-TLE / LR-FHSS terminal control problem, SGP4 baseline, evidence-gated learned residual, real BK1/BK2 negative result, controlled synthetic stress, guard/outage/energy proxy, explicit no-hardware/no-measured/no-live non-claims. |
| Keywords | Replaced "calibrated uncertainty, risk-aware control" with "transmitter-side control, stale TLE, Doppler residual, evidence gate, safe-by-default learning". |
| Introduction | Rewritten around transmitter-side control before transmission, when-to-learn vs not, real-TLE evidence that learning may hurt, the gate as a safety mechanism, synthetic stress as conditional benefit. |
| Contributions | Replaced with the 5 new contributions (gated controller; real negative result; controlled stress characterisation; guard/outage/energy proxy formulation; claim-evidence discipline). |
| Fig.~1 (architecture) | TikZ figure rewritten: Prediction (stale TLE→SGP4→$f_{phys}$/$f_{ml}$) → Evidence Gate → terminal control + proxies. Removed the "Conducted IQ Evidence" group and the 9.82 dB box. |
| Related Work | Trimmed calibration framing; re-pointed the ML-orbit subsection to the "is learning justified at all" question; updated positioning table last rows to evidence-gated control. |
| System Model | Kept Doppler / residual-CFO equations; replaced the PGRL uncertainty-head architecture with the stale-TLE open-loop baseline + inter-TLE residual definition $r=D_{ref}-f_{phys}$ (model-derived). |
| Method (new) | Added the formal Evidence Gate: $\mathrm{MAE}_{phys}(V)$, $\mathrm{MAE}_{ml}(V)$, $G=\mathbf{1}[\mathrm{MAE}_{ml}(V)<\gamma\,\mathrm{MAE}_{phys}(V)]$, $\hat f=Gf_{ml}+(1-G)f_{phys}$; honest validation-window-only scope; guard/outage/energy proxies; datasets + chronological splits; control algorithm. |
| Evaluation | Rebuilt: real BK negative table (Tab.~\ref{tab:bk}-equiv), synthetic stress table, $\gamma$/validation-window sensitivity table; software-only scope note. |
| Old eval removed | Removed Stage 3E/3F/4 uncertainty-head/temperature/$\alpha$-sweep tables and figures (tempcal/risk/guardres) and the 5.35 m/Cov68-Cov95 centerpiece. |
| Hardware section | Removed as a results section; converted to a short Limitations/Future-Work paragraph documenting the inconclusive conducted-HIL attempt (missing coax + attenuator). |
| Limitations (new) | Explicit non-claims: no measured Doppler truth, no live satellite, no PER/BER/CRC/PDR/gateway ACK, no standards-compliant LR-FHSS decoding, no valid conducted-HIL evidence yet, synthetic stress is not real evidence, gate is validation-window evidence not a worst-case bound. |
| Conclusion | Rewritten to the safe-by-default, evidence-gated, software-only narrative. |
| Figures | All external `\includegraphics` removed (0 remain); only the self-contained TikZ architecture figure is kept. Orphaned `figures/fig2..5*.pdf` left on disk, unreferenced. |

## 3. Old claims removed

- 5.35 m position RMSE / Cov68=0.713 / Cov95=0.947 / $T=1.0$ as the main result.
- Risk-aware guard $g=g_{base}+\alpha\sigma_r$ and the outage 5.0%→1.7% @ 13.8% overhead $\alpha$-sweep as the centerpiece.
- "Conducted LR1121-to-USRP B210 capture … 9.82 dB TX-ON/OFF margin" as validation evidence.
- LR-FHSS-candidate score 0.76 / 101 candidate bursts / 19 bins IQ-structure evidence.
- Any phrasing implying hardware validation or signal presence.

## 4. New evidence used (all software-only / model-derived, from `docs/review/`)

- `bk_negative_result_compact.md` / `.csv` — real BK1 (8–168 h) + BK1→BK2 negative table.
- `gate_stress_compact.md` / `.csv` — synthetic stress regimes + guard/outage proxies.
- `evidence_gate_stress_experiment.md` — $\gamma$-sweep and validation-window sweep.
- `gate_threshold_interpretation.md` — $\gamma=0.95$ default rationale.
- `validation_window_sensitivity.md` — window-stability interpretation.
- `black_kite_residual_evidence_gate.md` — gate-closes-on-real-data record.
- `black_kite_1_target_specific_residual_experiment.md`, `black_kite_tle_history_residual_experiment.md` — source experiments.
- `claim_evidence_matrix.md`, `paper_reframing_blueprint.md` — wording discipline.
- `mac_conducted_hil_result_summary.md` — inconclusive HIL attempt (limitations paragraph).

## 5. Remaining limitations (as stated in the paper)

- Negative result is for two BLACK KITE satellites, not universal.
- Positive learning benefit is synthetic-only; gate gives a validation-window property, not a held-out/worst-case bound.
- Guard/outage/energy are control proxies, not link-layer measurements.
- No measured Doppler, no live satellite, no decoding, no PER/BER/CRC/PDR/gateway ACK.
- No valid conducted-HIL evidence yet (attempt halted: missing coax + fixed attenuator).

## 6. Compile result

`tectonic paper/icc_main.tex` → **success**, `paper/icc_main.pdf` written (~108.9 KiB).
Remaining warnings are cosmetic only: two small overfull `\hbox` (1.6 pt related-work
table, 4.8 pt BK table) and harmless "Object already defined" notes from the
pre-existing table-note `\patchcmd` hack. No errors.

## 7. Grep audit result

Command (as required):
```
grep -Rni "guarantee\|worst-case\|measured Doppler\|live satellite\|PER\|BER\|CRC\|PDR\|gateway ACK\|can only help\|hardware validates\|hardware-validated\|conducted LR1121-to-USRP capture confirms\|learned residual.*real BLACK KITE" paper/icc_main.tex
```
- Genuine dangerous tokens (`guarantee`, `worst-case`, `can only help`,
  `hardware-validated`, `hardware validates`, `conducted LR1121-to-USRP capture
  confirms`): **0 matches.**
- Word-bounded `PER|BER|CRC|PDR`: only the single Limitations sentence listing
  them as **not measured** (explicit non-claim).
- `measured Doppler` / `live satellite`: only in **"no measured Doppler" / "no
  live-satellite"** non-claim contexts.
- Remaining case-insensitive hits are the substring "per" inside *paper,
  property, percentile, performance, unexplored, Experimental* — false positives.

**Conclusion: no overclaim remains; every flagged token is an honest disclaimer.**

## 8. `git diff --stat`

```
paper/icc_main.tex | 627 +++++++++++++++++++++++++-----------
 1 file changed, 427 insertions(+), 200 deletions(-)
```
(`paper/icc_main.pdf` is git-ignored; not shown.)

## 9. Confirmations

- **No hardware/RF/UART/TX/capture command was run** for this rewrite (edit +
  `grep` + `tectonic` only).
- **`dataraw/` not touched** (`git status` shows no `dataraw` path).
- **LoRa antenna not used as evidence**; the inconclusive HIL attempt is in
  limitations only.
- Paper claim is now **simulation / trace-driven / model-derived only.**
- Not committed.

---

## 10. Final polishing edits (low-risk, narrative unchanged)

Three targeted insertions; no main-narrative change, no hardware/measured/live
claim reintroduced.

1. **§V-B (real BK negative result):** added a cautious physical interpretation of
   why the inter-TLE residual is unpredictable — *consistent with*
   orbit-determination updates, drag-model mismatch, tracking/fit noise, and
   occasional maneuver or bad-fit events, *not exposed as predictable
   terminal-side features*. Explicitly not a propagator-optimality claim; no
   "station-keeping caused", no "guarantees", no "worst-case".
2. **§V-C (extreme synthetic stress):** added a proxy interpretation — guard proxy
   $14.1$~kHz$\to$$950$~Hz means a much smaller reserved frequency margin that can
   lower conservative margin/overhead, stated as an energy/overhead **proxy**, not
   a measured power/battery saving, gateway search-window measurement, or
   link-layer result; benefit is synthetic-only.
3. **§V-A (experimental setup):** added one sentence that 868~MHz is a
   representative carrier for Doppler scaling/reproducibility and the controller is
   frequency-parametric (rescale $f_c$); no NCC/AS923 or regulatory claim.

Hardware attempt **kept** as a limitation/future-work paragraph (not a
contribution).

**Compile:** `tectonic paper/icc_main.tex` → success, `paper/icc_main.pdf`
(~110.5 KiB); only two cosmetic overfull hboxes (1.6 pt, 4.8 pt). No errors.

**Grep (polish pass):**
```
grep -Rni "guarantee\|worst-case\|measured Doppler\|live satellite\|can only help\|hardware validates\|hardware-validated\|conducted LR1121-to-USRP capture confirms\|learned residual.*real BLACK KITE\|battery saving\|power saving\|station-keeping caused" paper/icc_main.tex
```
3 matches, **all explicit non-claims**: "no measured Doppler, no live-satellite…"
(Fig.~1 note), "not a measured power saving, a gateway receiver…" (§V-C
disclaimer), "no measured Doppler truth, no live-satellite…" (limitations). No
"station-keeping caused", no genuine overclaim.

**Confirmations (polish pass):** no hardware/RF command run (edit + grep +
tectonic only); `dataraw/` not touched; paper remains software-only /
model-derived. Not committed.

---

## 11. Finalization pass (parallel tracks A–G, coordinator-applied)

Maximum-depth review across seven tracks; only minimal high-value edits applied.
No narrative pivot; no hardware/measured/live content reintroduced.

- **Track A (overclaim auditor):** whole-paper sweep found no dangerous claim. All
  PER/BER/CRC/PDR/measured-Doppler/live-satellite/power-saving occurrences are
  explicit non-claims/limitations. No edit needed.
- **Track B (narrative):** story chain verified coherent
  (problem $\to$ stale-TLE baseline $\to$ naive-learning failure $\to$ Evidence
  Gate $\to$ real BK negative $\to$ synthetic stress open/close $\to$
  guard/outage/energy proxy $\to$ limitations). One reviewer-facing sentence added
  in §V-B framing the negative result constructively ("a rigorous real-data case
  showing why always-on residual learning is unsafe … why an evidence gate … is
  the appropriate design").
- **Track C (math/method):** notation verified consistent and defined before use:
  $f_{\mathrm{phys}}, D_{\mathrm{ref}}, r, f_{\mathrm{ml}}, G, \gamma,
  \mathrm{MAE}_{\mathrm{phys}}(V), \mathrm{MAE}_{\mathrm{ml}}(V), \hat f, e,
  g=2p_{99}(|e|), \rho=\Pr[|e|>F_{\mathrm{tol}}]$. No edit needed.
- **Track D (evaluation):** real BK table framed as negative evidence; synthetic
  stress labelled controlled simulation / not real BK evidence; $\gamma$ and
  validation-window tables explained as gate behavior, not guarantee; energy
  language kept proxy-only. No further edit needed.
- **Track E (figure):** Fig.~1 already matches the preferred structure (stale TLE
  $\to$ SGP4 baseline + optional ML path $\to$ Evidence Gate central block $\to$
  default-to-physics mux $\hat f=Gf_{\mathrm{ml}}+(1-G)f_{\mathrm{phys}}$ $\to$
  guard/outage/energy proxy; bottom software-only note; no hardware path). Left
  unchanged to avoid risk to a clean-compiling figure.
- **Track F (compile/layout):** `tectonic paper/icc_main.tex` $\to$ success,
  `paper/icc_main.pdf` (~110.8 KiB), **6 pages** (within workshop limit). Only two
  cosmetic overfull hboxes (1.6 pt, 4.8 pt); left per instructions. No undefined
  citations.
- **Track G (references):** citations consistent; no new references added; none
  invented; `refs.bib` untouched.

**Finalization grep (full, incl. PER/BER/CRC/PDR/gateway ACK):** every match is an
explicit non-claim/limitation (e.g.\ "not a measured power saving, a gateway
receiver…", "not link-budget, packet-error rate (PER), …, (PDR) measurements",
"no measured Doppler truth, no live-satellite…"). No "guarantee", "worst-case",
"hardware-validated", "station-keeping caused", or "battery/power saving" claim.
**Zero dangerous overclaims.**

**Confirmations (finalization):** no hardware/RF/UART/TX/capture command run
(edit + grep + tectonic only); `dataraw/` untouched; paper remains
simulation/trace-driven/model-derived only. Not committed.

---

## Body densification pass

Expanded the main body into a full 6-page contribution while keeping the PDF at
**6 pages** (references end on page 6). No narrative pivot; no hardware/PGRL/
measured/live content reintroduced.

**Expansions made:**
- New §IV-B *Statistical Role of the Gate*: false open (Type-I) / missed open
  (Type-II) error modes, $\gamma$ as a conservative knob, $\gamma=0.95$ default.
  Avoids "guarantee/worst-case/bound/can only help/optimal".
- Expanded §IV-C proxies: cross-layer rationale (frequency error $\to$ LR-FHSS
  margin), guard proxy $g=2p_{99}(|e|)$, outage proxy $\rho=\Pr[|e|>F_{\mathrm{tol}}]$,
  and an illustrative overhead proxy $E_{\mathrm{proxy}}\propto(1+\alpha_g g/B)(1+\rho)$
  explicitly labelled not a measured energy/packet model.
- Expanded §V-B physical interpretation: "weakly structured inter-TLE residual";
  cautious wording; not-white-for-all-satellites caveat; no station-keeping-as-fact.
- New §V-E *Implications for Terminal Control* (ties Tables BK/stress/gamma) and
  §V-F *Design Implications* (fresh-TLE hard to beat; stale/biased only if
  validated; deploy with evidence logging, not always-on; practical rule, not a
  guarantee).
- Limitations restructured into a compact itemized scope (model-derived reference;
  no live/link-layer PER/BER/CRC/PDR/gateway ACK; negative result not universal;
  synthetic not real; gate validation-window only; proxies only); hardware kept as
  a limitation/future-work item.

**Layout actions to hold 6 pages:** added `enumitem` tight lists + compact
float/display spacing; shrank Fig.~1 vertical geometry; removed the qualitative
positioning table (content kept in §II-D prose) and the redundant algorithm float
(method fully specified by Eqs.\ and a one-paragraph deployment recipe); trimmed
several verbose sentences. Figure~1 unchanged in structure (no hardware path).

**Compile:** `tectonic paper/icc_main.tex` $\to$ success; `pdfinfo` reports
**Pages: 6**; references end on page 6 (no page-7 overflow). One cosmetic 4.8 pt
overfull hbox (BK table); no errors.

**Grep audit (full, incl. PER/BER/CRC/PDR/gateway ACK):** 5 matches, all explicit
non-claims (Fig.~1 note "no measured Doppler, no live-satellite"; §IV-C "not a
measured power saving, a gateway receiver…"; Limitations "no … PER, BER, CRC,
PDR, or gateway acknowledgement"). No "guarantee", "worst-case",
"hardware-validated", "station-keeping caused", "battery/power saving" claim; no
"learned residual improves real BLACK KITE". **Zero overclaims.**

**Confirmations (densification):** no hardware/RF/UART/TX/capture command run
(edit + grep + tectonic + pdfinfo only); `dataraw/` untouched; paper remains
software-only / model-derived. Not committed.

---

## Final body expansion and page-fill pass

Added the requested reviewer-style depth in claim-safe form and re-fit the paper to
**6 pages** with references ending on page 6 and page 6 substantially filled
(\~9.6k chars).

**Paragraphs added:**
- §IV-B *Statistical Role of the Gate* — OOD / non-stationarity paragraph: residual
  may be non-stationary (drag, OD updates, fit changes); gate acts as an
  evidence-based circuit breaker reverting to physics when recent validation no
  longer supports learning; explicitly a validation-window rule, not a guarantee.
- §IV-C proxies — Doppler-rate/timing-offset coupling
  $\Delta f_D\approx\dot f_D\,\Delta t$ (Eq.) motivating pass-aware guard sizing;
  control-proxy only, no timing-sync/packet claims.
- §V-B — deeper SGP4/TLE interpretation (SGP4 fitted through mean elements;
  successive TLEs are OD updates over different arcs; residual mixes fit
  artifacts/drag mismatch/tracking noise/maneuver-like events; weakly structured
  from the terminal-feature view; regressor may fit validation noise). Conservative
  wording; no station-keeping-as-fact, no white-noise-for-all, no SGP4-optimality.
- §VI — *Future conducted-HIL roadmap*: (i) conducted RF loop (coax, no radiated
  LoRa antenna), (ii) calibrated $50\,\Omega$ attenuation (linear region, no ADC
  clipping), (iii) clock/CFO discipline; IQ-level vs link-layer evidence separated;
  link-layer needs a gateway-class decoder. Explicitly not performed/claimed.

**Layout adjustments:** merged §V-E+§V-F into one *Implications and Design Rules*
subsection; merged two overlapping §V-B interpretation paragraphs; merged the two
trailing Related-Work subsections; tightened `enumitem`/float/display spacing;
shrank Fig.~1 geometry (resizebox 0.82, rows tighter); loosened float specifiers to
`[tb]`; tightened bibliography inter-item spacing (font unchanged); removed the
long 3GPP URL from `refs.bib`; trimmed numerous verbose sentences. No table or
result removed in this pass (positioning table and algorithm float had been
removed earlier); Fig.~1 keeps no hardware path.

**Compile:** `tectonic paper/icc_main.tex` $\to$ success; `pdfinfo` **Pages: 6**;
references end on page 6; page 6 \~9.6k chars (substantially filled). One cosmetic
4.8 pt overfull hbox (BK table); no undefined citations; no errors.

**Grep audit:** 4 matches, all explicit non-claims (Fig.~1 note; §V-C "not a
measured power saving, gateway search-window, or link-layer result"; Limitations
"no … PER, BER, CRC, PDR, or gateway acknowledgement"). No guarantee / worst-case /
hardware-validated / station-keeping-caused / battery-or-power-saving / SGP4-optimal
claim. **Zero overclaims.**

**Confirmations (final expansion):** no hardware/RF/UART/TX/capture command run
(edit + grep + tectonic + pdfinfo only); `dataraw/` untouched; paper remains
software-only / trace-driven / model-derived. Not committed.

---

## Extended full-content draft pass

Reversed the earlier over-compression: produced a full-content working draft where
the body fills page 6 and references continue onto page 7 (7 pages total, which is
acceptable for this draft stage).

**Restored elements:**
- Positioning table (Table~\ref{tab:related}) re-added to Related Work §II-C.
- Algorithm~1 (\texttt{alg:control}) restored in the method (8-line gated-control
  procedure) replacing the one-line deployment recipe.
- 3GPP reference URL restored in `paper/refs.bib`.
- Loosened the over-tight layout: `enumitem` itemsep 1pt$\to$2.5pt; float/display
  spacing relaxed (\~6pt$\to$9pt, display 3pt$\to$4pt); removed the bibliography
  inter-item compaction hack.

**Figure 1 redesign:** replaced the flat 3-row diagram with a clean
double-column (`figure*`) left-to-right fail-safe architecture: input (stale TLE /
onboard state) $\to$ parallel SGP4 physics baseline ($f_{\mathrm{phys}}$) and
learned residual branch ($f_{\mathrm{ml}}=f_{\mathrm{phys}}+\hat r$) $\to$ large
highlighted \emph{Evidence Gate} ($G=\mathbf{1}[\mathrm{MAE}_{\mathrm{ml}}(V)<\gamma\,\mathrm{MAE}_{\mathrm{phys}}(V)]$,
dashed validation-MAE inputs) $\to$ explicit \emph{Selector (MUX)} routing
$G{=}0\!\to\!f_{\mathrm{phys}}$, $G{=}1\!\to\!f_{\mathrm{ml}}$ with output
$\hat f=Gf_{\mathrm{ml}}+(1-G)f_{\mathrm{phys}}$ $\to$ LR-FHSS terminal control
(Doppler pre-comp, guard/outage/overhead proxies). Bottom scope note; no hardware
path. Wrapped in `\resizebox{\textwidth}` to fit the double column cleanly.

**New / expanded technical content:**
- §IV-B OOD / non-stationarity circuit-breaker paragraph (drag, OD updates,
  observation-arc/fit changes; gate re-checks recent validation and reverts to
  physics; explicitly a validation-window rule, not a distribution-shift guarantee).
- §IV-C Doppler-rate/timing coupling $\Delta f_D\approx\dot f_D\,\Delta t$ $\to$
  pass-aware guard motivation (proxy only).
- §V-B SGP4/TLE fitting-artifact interpretation (mean-element fits, OD over
  different arcs, weakly-structured residual, regressor may fit validation noise);
  conservative ``may/consistent with''; no station-keeping-as-fact, no
  white-for-all, no SGP4-optimality.
- §V-E expanded into a fuller systems design-rules discussion + an explicit
  deployment-logging itemize (gate $G$ and $\gamma$; validation MAE pair and $|V|$;
  stale-TLE age / epoch gap).
- §VI roadmap expanded into setup requirements (conducted RF loop; calibrated
  $50\,\Omega$ attenuation; clock/CFO discipline) and three separated evidence
  levels (L1 signal presence, L2 structure/CFO proxy, L3 gateway-class link-layer);
  none performed/claimed.

**Compile / layout:** `tectonic` success; \textbf{7 pages}; body text fills page 6;
Conclusion and References on page 7 (References start page 7). Figure-width overflow
fixed; no serious ($>$15 pt) overfull; no undefined citations.

**Grep audit:** matches are all non-claims (Fig.~1 note; §V-C ``not a measured
power saving, gateway search-window, or link-layer result''; Limitations ``no …
PER, BER, CRC, PDR, or gateway acknowledgement'') or the word ``per'' inside
``per regime''/``per control epoch''. No guarantee / worst-case / hardware-validated
/ station-keeping-caused / SGP4-optimal / battery-power-saving claim. **Zero
overclaims.**

**Confirmations (extended draft):** no hardware/RF/UART/TX/capture command run
(edit + grep + tectonic + pdfinfo only); `dataraw/` untouched; paper remains
software-only / trace-driven / model-derived. Not committed.

---

## Data-visualization pass (3 figures)

Added two data figures generated \emph{only} from existing repo artifacts (no new
experiment, no invented numbers) and kept the redesigned architecture figure, for
**3 figures + 3 tables** total.

**Figures:**
- \textbf{Fig.~1} (architecture, `figure*`): kept the double-column fail-safe
  design (stale TLE $\to$ physics/learned paths $\to$ Evidence Gate $\to$ MUX
  selector $\to$ LR-FHSS control); no hardware path.
- \textbf{Fig.~2} (`figure*`, `figures/fig_bk_residual.pdf`): (a) empirical CDF of
  BK1 SGP4/stale-TLE $|$residual$|$ at 8/48/168~h from the \emph{reported}
  held-out percentiles, with $F_{\mathrm{tol}}=500$~Hz; (b) baseline-vs-learned
  held-out MAE vs.\ staleness (BK1 and BK1$\to$BK2) showing learned $>$ baseline
  everywhere.
- \textbf{Fig.~3} (`figures/fig_gate_behavior.pdf`): gate decision (top) and
  deployed MAE (bottom) vs.\ $\gamma$ for noise-dominated/moderate/systematic
  regimes; replaces the former $\gamma$-sensitivity table.

**Data provenance:** all figure numbers are hardcoded from
`docs/review/black_kite_1_target_specific_residual_experiment.md` (BK1 residual
percentiles), `docs/review/bk_negative_result_compact.{md,csv}` (MAE), and
`docs/review/gate_stress_compact.{md,csv}` + `evidence_gate_stress_experiment.md`
($\gamma$ sweep). Generator: `paper/figures/generate_evidence_gate_figures.py`
(`matplotlib`, software-only). `reference_is_measured_truth=false`.

**Tables:** kept Table~\ref{tab:related} (positioning), Table~\ref{tab:bk} (real
negative result), Table~\ref{tab:stress} (synthetic stress); the $\gamma$
sensitivity table was \emph{converted to Fig.~3}.

**Compile / pages:** `tectonic` success; no undefined citations; no serious
overfull. \textbf{8 pages} total: body + Conclusion through page~7, references
spill onto page~8 (\~3k chars). This exceeds the 6-page ideal because the
explicitly-requested 3 figures + 3 tables + expanded §IV--§VI text genuinely need
$\sim$7--8 pages; per the ``prioritize content/figure quality, report honestly''
guidance it is left extended. Reaching 6 pages would require removing a figure or a
table or cutting the §V--§VI expansions.

**Grep audit:** matches are all non-claims (Fig.~1/§V-C/Limitations disclaimers) or
the token ``per''. No genuine overclaim.

**Confirmations (data-viz):** figures generated by `matplotlib` from existing
artifact numbers; no hardware/RF/UART/TX/capture; `dataraw/` untouched; paper
remains software-only / model-derived. Not committed.

---

## Six-page visualization repair pass

Repaired layout toward a submission-style version: **3 figures + 2 tables + inline
algorithm**.

- \textbf{Fig.~1 redesign}: single-column (\texttt{figure}, not \texttt{figure*})
  \emph{vertical} fail-safe stack: stale TLE $\to$ {SGP4 $f_{\mathrm{phys}}$ |
  learned $f_{\mathrm{ml}}$} $\to$ highlighted Evidence Gate $\to$ MUX selector
  ($G{=}0\!\to\!f_{\mathrm{phys}}$, $G{=}1\!\to\!f_{\mathrm{ml}}$) $\to$ output
  $\hat f$ $\to$ LR-FHSS terminal control; bottom scope note; no hardware path.
- \textbf{Fig.~2 decision}: checked for raw residual samples --- \emph{none exist}
  (artifacts hold only summary percentiles + MAE; the only sample-level CSVs are
  hardware CFO timeseries, off-limits). So Fig.~2 is the \textbf{safer single-column
  plot}, NOT an empirical CDF: (a)~held-out MAE vs.\ staleness, baseline vs.\
  learned; (b)~relative degradation $\Delta\%$ (all $<0$). Caption states
  software-only / model-derived / no measured Doppler / no per-sample distribution.
- \textbf{Fig.~3 kept}: single-column gate-behaviour (gate decision + deployed MAE
  vs.\ $\gamma$); it \emph{replaces} the former $\gamma$-sensitivity table.
- \textbf{Tables}: removed the positioning table (now a Related-Work paragraph) and
  the $\gamma$ table (now Fig.~3). Kept \textbf{Table~I} (real BK negative result)
  and \textbf{Table~II} (synthetic stress) --- 2 compact tables.
- \textbf{Algorithm}: compacted, then converted to a compact inline 4-step
  paragraph to reclaim float space (sanctioned by the "convert if too tall" rule).
- Trimmed repetition in §V-C/§V-E/§VI and limitations (bulleted limitations $\to$
  one compact paragraph).

\textbf{Compile / pages}: `tectonic` success; no undefined citations; no serious
overfull. \textbf{7 pages}: body + Conclusion fit \emph{within page 6};
references (23 entries) spill onto page 7 ($\sim$1.5 columns). Strict 6-pages-incl.-
references is not reachable while keeping all 3 figures + 2 tables + the expanded
§IV--§VI text, because the figure/table floats strand $\sim$1.5 columns that the
trailing bibliography cannot backfill. Reaching strict 6 would require dropping one
figure/table or removing $\sim$6 citations (a scholarship choice left to the
authors).

\textbf{Grep audit}: all matches are non-claims (Fig.~1/2 notes, §V-C disclaimer,
Limitations PER/BER/CRC/PDR/gateway non-claim) or the token ``per''. Zero
overclaims.

\textbf{Confirmations (6-page repair):} no hardware/RF/UART/TX/capture (matplotlib
+ tectonic + pdfinfo only); `dataraw/` untouched; paper remains software-only /
model-derived. Not committed.

---

## Strict six-page submission compression pass

Produced a strict **6-page** version with references ending on page 6, keeping all
3 figures and both core tables.

- \textbf{References reduced 23 $\to$ 14} (cited). Dropped 9 less-central entries
  (vallado2006revisiting; jung2025lrfhss, knop2024header, santana2024acrda,
  rathi2024replication, farhat2025probabilistic; peng2021fusion, caldas2024leo;
  sanchez2024energy) and removed the long 3GPP URL. Kept SGP4 (hoots,
  vallado2007), Semtech + LR-FHSS overview (semtech2023, boquet2021), D2S analysis
  (ullah2022, hurn2023), transceiver + trace (jung2023, bukhari2023), uplink policy
  (alvarez2022), ML orbit (peng2019, acciarini2025, varey2024, caldas2024 survey),
  and 3GPP NTN.
- \textbf{Related Work prose compressed}: dense 6-cite receiver list $\to$ one
  representative cite-pair; ML-orbit list condensed; no paragraph cites $>3$ works.
- \textbf{Abstract} shortened ($\sim$25 words).
- \textbf{Fig.~1} caption cut to 4 lines; figure kept single-column compact
  switch/MUX style (no \texttt{figure*}, no hardware path).
- \textbf{Fig.~2/3 captions} cut to 2--4 lines each.
- \textbf{Limitations} one compact paragraph; \textbf{HIL roadmap} one compact
  paragraph (no itemize); all non-claims retained (no measured Doppler, no live
  satellite, no PER/BER/CRC/PDR/gateway ACK, no hardware validation, HIL missing
  conducted path/attenuator).
- \textbf{Design rules} one paragraph, logging itemize $\to$ inline; the procedure
  is the inline 4-step recipe (algorithm float already removed).

\textbf{Compile / pages}: `tectonic` success; \textbf{6 pages}; references end on
page~6 (no page~7); no undefined citations; no serious ($>$15~pt) overfull. Kept
3 figures (architecture, BK negative, gate behaviour) + 2 tables (real BK,
synthetic stress).

\textbf{Grep audit}: all matches are non-claims (Fig.~1/2 notes, §V-C disclaimer,
Limitations PER/BER/CRC/PDR/gateway non-claim) or the token ``per''. Zero
overclaims.

\textbf{Confirmations (strict-6):} no hardware/RF/UART/TX/capture (tectonic +
pdfinfo only); `dataraw/` untouched; paper remains software-only / model-derived.
Not committed.
