# Paper 1 — Revised Core Text (paste-ready)

> Software-only paste-ready paragraphs for the Paper-1 gap closure. All numbers
> below are model-derived proxies (exp7/exp8/exp9) or the committed conducted-IQ
> hardware evidence. Nothing here claims packet decode, PER/PDR/CRC, gateway ACK,
> OTA, live-satellite, or "full RF validation". Regenerate numbers with the three
> `experiments/exp7…exp9` scripts; cross-check the hardware boundary against
> `PAPER_HARDWARE_EVIDENCE_TEXT.md`.

---

## A. Contribution framing (one paragraph)

> We study **pre-transmission** control for a D2S LEO-IoT uplink: an SGP4-anchored
> predictor (PGRL) supplies a per-pass timing and Doppler schedule, and an
> evidence gate admits learned residual correction only on a held-out-proven
> margin. On real historical TLEs of the same object (BLACK KITE), the learned
> residual does **not** beat the stale-TLE SGP4 baseline at any tested staleness
> (8–168 h) and the gate closes — the paper's central negative result. We then
> characterise the control mechanism with transparent software proxies (timing
> guard-coverage, frequency hop-bin tolerance) and an embedded footprint profile,
> and we report conducted IQ-level measurement-path hardware evidence of a
> controlled LR-FHSS transmission.

## B. Timing-offset sensitivity (exp7)

> Under an adaptive 3σ guard, the residual timing offset σ_t sets the guard width,
> the TX-window coverage, and the per-burst energy. Sweeping σ_t from 16 ms to 2 s
> holds the analytic miss rate near the 3σ floor (≈0.3%) but inflates guard
> overhead from 0.03% to ~2.5% of the pass and **energy per successful burst from
> ~10 mJ to ~246 mJ** — i.e. stale-TLE timing error is paid almost entirely in
> reserved guard energy, not in misses. Mapping TLE staleness (8–168 h) to the
> open-loop SGP4 along-track timing offset (≈1.5 km/day ÷ orbital speed) gives σ_t
> ≈ 0.07 s at 8 h rising to ≈1.4 s at 168 h, monotonically widening the required
> guard. *(Software-only guard-coverage proxy; hit/miss is analytic
> P(|offset|>guard), not a measured packet outcome.)*

## C. Timing / frequency / PGRL ablation (exp8)

> Toggling control dimensions over a five-way ablation (independent timing-coverage
> and frequency-tolerance proxies, F_tol = 500 Hz hop-bin) gives a monotone
> picture:
>
> | Config | success/hit | guard ovh | energy / success |
> |---|---|---|---|
> | no control | 0.03% | 0.01% | 25.7 J |
> | timing only | 1.99% | 1.89% | 9.37 J |
> | frequency only | 0.25% | 0.01% | 3.24 J |
> | timing + frequency (SGP4) | 15.8% | 1.89% | 1.18 J |
> | timing + frequency + PGRL | **90.4%** | 0.03% | **11.2 mJ** |
>
> Timing control alone fixes the window but leaves the SGP4 Doppler residual
> (~2.5 kHz) missing the 500 Hz hop bin 84% of the time; the PGRL residual
> (~300 Hz) cuts the frequency miss to ~10%, lifting joint success to ~90% and
> cutting energy per successful burst by **~100×** versus SGP4 timing+frequency.
> *(Software-only coverage proxy; the PGRL row is the gate-open synthetic regime —
> on real BLACK KITE the gate closes and PGRL does not beat SGP4.)*

## D. PGRL footprint (exp9)

> The deployable predictor (TrajectoryPINN; 256-wide, 6-layer, 128 Fourier
> features, Gaussian-NLL head) has **333,720 parameters** and **332,288 MACs
> (≈0.66 MFLOP) per inference**. Quantised to int8 it occupies **≈326 KB Flash**
> and **<1 KB working RAM** — MCU-class feasible when sufficient Flash is available
> (we do not claim a fit on ultra-minimal M0-class nodes without separate on-device
> validation). Training is offline on a host; the **endpoint runs inference only**
> (frozen weights, no optimizer state). One forward pass produces the whole-pass
> schedule: on a Cortex-M4F-class core the **estimated** cost is ~12.5 ms /
> ~1.07 mJ, i.e. **≈6.4% of a single LR-FHSS burst's transmit-draw energy** and
> **≈0.3% amortised over a 20-burst pass**. This inference overhead is bounded and
> can be outweighed by avoiding the missed or repeated transmissions quantified in
> exp7/exp8. *(Param/MAC counts exact; the MCU energy is an estimate, not a
> measured on-device value.)*

## E. Hardware evidence (conducted IQ only)

> A NUCLEO-L476RG + Semtech LR1121 board (Board B) was flashed with a deterministic
> firmware fixed at 923.2 MHz and the lowest transmit power (−17 dBm, Low-Power
> PA), serial-verified (configured frequency/power, TX_START → repeated LR-FHSS
> bursts → TX_DONE). Over a conducted, 50 dB-attenuated coaxial path into a USRP
> B210 (no antenna), the transmit-on capture shows an emission ≈41 dB above the
> transmit-off noise floor (41.25 ± 0.36 dB over four repeats; 43.76 dB on a 2 MS/s
> control), peaking within the LR-FHSS hop grid, with no clipping or saturation; a
> waterfall of the window shows the hopping burst structure, and the per-burst
> peaks are reported as CFO / hop-center proxy candidates. A before/after reflash
> negative control isolates the earlier null to a board-side 868 MHz frequency
> mismatch. **This is conducted IQ-level measurement-path evidence of a controlled
> transmission only — no packet decode, PER/PDR/CRC, gateway ACK, OTA, or
> live-satellite claim.**

## F. Honesty guardrails carried into the text

- The headline empirical result is a **negative** one (gate closes on real TLEs).
- exp7/exp8 PGRL separations are **proxies in the gate-open regime**, always
  labelled as such; they do not contradict the real-data negative result.
- The staleness model is historical-TLE / SGP4-derived, **not Gaussian drift**
  (see `docs/TLE_AGING_METHODOLOGY.md`).
- Hardware stays at the IQ-spectral ceiling (`PAPER_HARDWARE_EVIDENCE_TEXT.md`).
