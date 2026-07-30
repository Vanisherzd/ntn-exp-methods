# exp8 — Timing / frequency / PGRL control ablation

Software-only coverage proxy over five control configurations:

| config | timing guard | Doppler pre-comp | predictor |
|---|---|---|---|
| `no_control` | fixed base | none | SGP4 |
| `timing_only` | adaptive k-σ | none | SGP4 |
| `frequency_only` | fixed base | SGP4 | SGP4 |
| `timing_frequency` | adaptive k-σ | SGP4 | SGP4 |
| `timing_freq_pgrl` | adaptive k-σ | PGRL | PGRL |

Metrics: timing-miss rate, frequency-miss rate, joint success/hit rate, guard
overhead, energy per successful burst.

Run:
```bash
python experiments/exp8_control_ablation/run_control_ablation.py
```
Outputs `results.json` and `figures/fig_control_ablation.{pdf,png}`.

**Scope.** timing-miss = `P(|offset| > guard)`, frequency-miss =
`P(|residual Doppler| > F_tol=500 Hz)`; joint success assumes independence. These
are analytic coverage proxies, **not** measured LR-FHSS packet outcomes. No
hardware/RF/PER/OTA. The `timing_freq_pgrl` row is the gate-open synthetic
regime; on real BLACK KITE the gate closes and PGRL does not beat SGP4.
