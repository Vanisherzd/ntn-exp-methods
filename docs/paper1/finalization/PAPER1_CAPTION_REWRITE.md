# Paper 1 — Academic Caption Rewrite

> Final captions as applied in `paper/icc_main.tex`. Design rules: concise,
> claim-bounded, evidence-oriented; explicit "software-only / model-derived",
> "synthetic sanity check", or "conducted IQ-level only" markers.

## Fig. 1 (architecture)

> Evidence-gated timing/frequency endpoint control. The stale-TLE SGP4 prediction
> is the deployed default; a learned residual is selected only when the Evidence
> Gate's chronological held-out window V shows a margin-γ improvement, and the
> resulting f̂ drives the endpoint's TX timing guard, frequency margin, and energy
> policy.

- Marker: scope footer inside the figure — "software / model-derived control;
  reference_is_measured_truth=false; conducted IQ-level hardware evidence reported
  separately (Sec. VI)".
- Was: formula-heavy vertical block diagram caption; now names the three endpoint
  outputs and the deployment rule only.

## Fig. 2 (evidence-gate behaviour, composite)

> Evidence-gate behaviour. (a,b) *Real* BLACK KITE result (software-only,
> model-derived; no measured Doppler): learned held-out MAE lies above the
> baseline and degradation is positive at every staleness, so the gate closes
> everywhere. (c,d) *Synthetic sanity check* (not BLACK KITE evidence): the gate
> opens only in the systematic regime and is γ-insensitive except at the margin;
> dashed line marks the systematic gate-closed baseline.

- Markers: "software-only, model-derived; no measured Doppler" (real panels);
  "synthetic sanity check (not BLACK KITE evidence)" (synthetic panels) — also in
  panel titles.

## Fig. 3 (endpoint-control proxies, composite)

> Timing/frequency endpoint-control proxies (software-only coverage proxies; not
> measured packet outcomes). (a,b) Timing sensitivity under the adaptive 3σ
> guard: miss and guard-overhead proxies, and energy per successful burst, vs.
> residual timing offset σ_t; markers place the SGP4 open-loop staleness curve
> (TLE age 24/168 h). (c,d) Control ablation (log axes). \*The learned-predictor
> configuration is the gate-open synthetic regime; on real BLACK KITE the gate
> closes (Sec. V-B).

- Markers: "software-only coverage proxies; not measured packet outcomes";
  the PGRL bar carries an in-figure \* tied to the gate-open-synthetic caveat.

## Fig. 4 (conducted IQ evidence)

> Conducted IQ-level measurement-path evidence (canonical run): max-hold TX-ON
> vs. TX-OFF spectra near 923.2 MHz over a 50 dB attenuated coaxial path (no
> antenna); inset: repeatability across four runs. Conducted IQ-level evidence
> only—no packet decode, no over-the-air claim.

- Markers: "conducted IQ-level … only", "no packet decode, no over-the-air
  claim"; inset carries 41.25 ± 0.36 dB (4 runs) + no clipping/saturation.

## Table captions (unchanged numbers, already bounded)

- Table I keeps `reference_is_measured_truth=false` and "Gate closes in every
  row."
- Table II keeps "Controlled synthetic stress (NOT real BLACK KITE evidence)".

## Rules applied

1. No plot-internal verbose titles carry claims; captions explain.
2. Every synthetic panel labelled synthetic in the caption AND the panel title.
3. Hardware caption stays at conducted IQ-level with the negative claim boundary.
4. No caption asserts packet/PER/OTA/live-satellite performance.
