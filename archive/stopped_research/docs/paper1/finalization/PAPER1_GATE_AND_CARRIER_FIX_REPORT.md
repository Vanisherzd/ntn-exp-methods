# Paper 1 — Gate-Evidence & Carrier-Frequency Consistency Report

_Build: `tectonic paper/icc_main.tex` — SUCCESS; 6 pages incl. references;
0 overfull, 0 undefined refs. No hardware run; no numbers changed._

## What changed

### 1. Table I reframed as a real-data negative result

New caption (as required): "Real BLACK KITE negative result: held-out test MAE
[Hz] at the **868 MHz software carrier**, learned residual vs. zero-residual
stale-TLE baseline. Values are **model-derived from TLE/SGP4 and scale linearly
with carrier frequency; no measured Doppler is used**
(reference_is_measured_truth=false). The gate closes in every row **because the
learned residual is worse than the physics baseline**."

### 2. Gate-open evidence now explicit — new Table II "Gate behaviour across regimes"

Compact 4-row table in Sec. IV-C (Tables renumbered: I = BK negative result,
II = gate regimes, III = proxy parameters):

| Regime | Held-out evidence (γ=0.95) | Gate |
|---|---|---|
| BLACK KITE (real) | learned worse, 8–168 h | closed |
| Synth. noise-dom. | no learnable structure | closed |
| Synth. marginal | ~5% gain < margin | closed |
| Synth. systematic | MAE 1859.3→99.8 Hz; guard 14.1 kHz→950 Hz; outage 0.814→0.008 | **open** |

The gate-open case is now visible in Table II, Fig. 2(c,d), the contribution
bullet, and the conclusion — the gate can no longer read as always-closed.

### 3. Deploy/no-deploy framing (Sec. IV-C rewrite)

Inserted the required framing: real BLACK KITE = **negative control for unsafe
learning** (gate correctly retains SGP4); synthetic systematic = complementary
case where the same rule opens and reduces residual/guard/outage proxies; "the
gate is therefore a deploy/no-deploy test, not an always-learn mechanism." No
real-data improvement is claimed anywhere.

### 4. 868 MHz vs 923.2 MHz — carrier convention (Sec. IV-A, first paragraph)

New "Carrier convention." lead-in: software Doppler/control metrics at 868 MHz
(common LR-FHSS D2S evaluation setting; residuals scale linearly with f_c via
Eq. (1)); the conducted-IQ run uses **923.2 MHz for the local AS923 laboratory
setup** and is reported **only as measurement-path evidence, not as measured
Doppler truth for Table I**. No wording anywhere implies hardware validates
Table I.

### 5. Abstract

Added: "—the gate's value is preventing unsupported learning, opening only
under held-out evidence." (compact form of the suggested sentence).

### 6. Conclusion

Now: real data → gate closes → terminal keeps the **safe fallback**; synthetic →
gate opens under systematic residual; "The Evidence Gate is thus a
**trust/deploy decision for learning, not a guaranteed-improvement claim**."

## Where gate-open evidence is shown

Table II (IV-C) · Fig. 2(c,d) panels titled "Synthetic gate decision / deployed
MAE" · contribution bullet 2 · abstract · conclusion.

## Page count / offsets

6 pages including references (refs end near the bottom of p. 6). Additions were
offset by: intro ¶3 trim (gate summary moved to bullets), contribution-bullet
tightening, IV-B interpretation trim, IV-D sensitivity trim, per-epoch-procedure
paragraph collapse, PER/BER/CRC/PDR acronym shortening in limitations.

## No-overclaim scan

**PASS** — 2 residual hits, both negation ("not packet, link-layer, or OTA
validation") or future work.

## Remaining blockers

Unchanged: ① author placeholder ② optional [7] ToSN human check ③ commits D–G.
