# Paper 1 — Hard-6 Compression Report

_Build: `tectonic paper/icc_main.tex` — SUCCESS, 0 overfull boxes, 0 undefined
references/citations._

## Page count

- **Before:** 7 pages including references (body ended p. 6, refs ended p. 7).
- **After:** **6 pages including references** — body (through Conclusion and
  Limitations) ends on page 5; references [1]–[13] end in the upper half of
  page 6 with ~⅔ column spare.
- **Hard-6 including references: SATISFIED**, with margin for the real author
  block (placeholder → real affiliations may add a few lines; the spare absorbs
  it).

## What was cut / merged (numbers unchanged everywhere)

| # | Change | Where |
|---|---|---|
| 1 | Related Work section (II + 3 subsections) **merged into one compact paragraph** at the end of the Introduction; all 13 citations retained | Intro "Related work." |
| 2 | Contribution bullets **5 → 3** (gated controller + BK negative; gate-open characterisation + endpoint proxies + footprint; conducted-IQ evidence) | Intro |
| 3 | **Table II removed**, replaced by the one-sentence inline summary (1859.3→99.8 Hz MAE, 14.1 kHz→950 Hz guard, 0.814→0.008 outage; fresh/moderate closed at γ=0.95) — Fig. 2(c,d) carries the visual | Sec. IV-C |
| 4 | "Statistical Role of the Gate" subsection **collapsed** to three sentences after Eq. (7) (false open / missed open / γ=0.95 + sensitivity pointer) | Sec. III-A |
| 5 | Proxy prose compressed ~50%; **Eqs. (8),(9) kept**; "not packet/link" caveat kept once here + once in limitations | Sec. III-B "Control Proxies" |
| 6 | BK result reduced to **result paragraph + interpretation paragraph**; triplicated "learned is worse" statement removed; Table I + Fig. 2 kept | Sec. IV-B |
| 7 | Sec. IV-E rewritten in claim–evidence–implication form ("timing paid as guard energy" / "joint control dominates" / "footprint bounded, inference-only, MCU-class"); all numbers kept (16 ms→2 s, ~10→~246 mJ, 0.03→2.0→15.8→90.4%, 1.18 J→11.2 mJ, 333,720 params, 0.66 MFLOP, 326 KB int8, <1 KB RAM, ~1.07 mJ estimate) | Sec. IV-E |
| 8 | Conducted-IQ section compressed to **one paragraph + Fig. 4**; kept LR1121/NUCLEO-L476RG, 923.2 MHz/−17 dBm, serial verification, 50 dB coax → B210 RX2 A, 41.25±0.36 dB (4×4 MS/s), 43.76 dB 2 MS/s sanity, artifact-masked 41.1 dB, before/after ~0.5 dB, no clip/sat, claim boundary | Sec. V |
| 9 | "Limitations and Future Work" + "Conclusion" **merged into "Conclusion and Limitations"** (2 paragraphs: conclusion+design rule; limitations+future work) | Sec. VI |
| 10 | "Implications and Design Rules" subsection deleted; its numbers were duplicates of #3, its design rule moved into the Conclusion | — |
| 11 | Captions shortened to 2–4 lines (Fig. 2/3/4, Table I); float spacing 9→7 pt; Fig. 4 width 0.9→0.85 col; section names shortened (System Model / Control Proxies / Synthetic Stress / Sensitivity / Endpoint-Control Proxies) | global |

## Evidence removed?

**None.** Retained in full: BLACK KITE negative result (Table I + Fig. 2a,b +
two paragraphs), Evidence Gate definition (Eqs. 4–7 + Fig. 1), control proxies
(Eqs. 8–9), timing/frequency proxy results (Fig. 3 + all numbers), synthetic
stress numbers (now inline sentence + Fig. 2c,d), conducted-IQ evidence (Sec. V +
Fig. 4 + all numbers), claim boundaries, future-work sentence. Table II's six
numbers survive verbatim in the Sec. IV-C sentence.

## No-overclaim scan

**PASS.** Re-ran the risky-term grep after compression: every remaining
occurrence is a negation ("explicitly below any packet-level or over-the-air
claim", "no packet-decode, PER/PDR/CRC…"), a limitations statement, or the
future-work sentence. No positive packet/PER/PDR/CRC/ACK/OTA/live-satellite
claim.

## Remaining risks

1. **Author block still placeholder** — real affiliations will consume some of
   the p. 6 spare; re-check page count after filling (expected to stay ≤6).
2. Section landscape is denser; a reviewer may ask for the removed Table II —
   the inline sentence + Fig. 2(c,d) + committed
   `docs/review/gate_stress_compact.csv` cover it.
3. Two cross-references now point into merged sections (Sec. III-A carries the
   old `sec:stat` label; `sec:limits` labels a paragraph inside Sec. VI) — both
   resolve, cosmetic only.
4. Slides unaffected (no slide figure paths changed; deck not rebuilt).

## Status vs. venue policies

| Policy | Status |
|---|---|
| Hard 6 incl. refs | ✅ satisfied (≈⅓ page spare) |
| 6 body + refs overflow | ✅ satisfied (body ends p. 5) |
