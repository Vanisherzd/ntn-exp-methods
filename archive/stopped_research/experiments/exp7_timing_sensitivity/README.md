# exp7 — Timing-offset sensitivity analysis

Software-only guard-coverage proxy. Two sweeps:

- **(A) residual timing-offset sweep** — timing 1σ from 5 ms to 2 s → TX-window
  hit/miss rate, guard overhead, energy per successful burst (adaptive k-σ guard).
- **(B) TLE-age sweep** — TLE staleness 8–168 h mapped to the open-loop SGP4
  along-track timing 1σ (1.5 km/day rule-of-thumb ÷ orbital speed), with a PGRL
  gate-open synthetic clamp overlaid.

Run:
```bash
python experiments/exp7_timing_sensitivity/run_timing_sensitivity.py
```
Outputs `results.json` and `figures/fig_timing_sensitivity.{pdf,png}`.

**Scope.** Hit/miss is the analytic guard-coverage probability
`P(|offset| > guard)`, **not** a measured LR-FHSS packet outcome. No hardware,
RF, PER/PDR/CRC, OTA, or live-satellite data. Constants come from
`experiments/paper1_proxy_model.py` (consistent with exp2/exp3 and icc_main.tex).
The PGRL clamp is the gate-open synthetic regime; on real BLACK KITE the evidence
gate closes and PGRL does not beat SGP4.
