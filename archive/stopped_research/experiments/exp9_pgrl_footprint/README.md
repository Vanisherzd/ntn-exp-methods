# exp9 — PGRL footprint profile

Software-only static accounting for the deployable PGRL predictor
(`TrajectoryPINN`, SGP4-anchored residual corrector):

- exact parameter count and MACs / FLOPs per inference
- estimated RAM / Flash footprint (fp32 and int8)
- offline-training / endpoint inference-only statement
- conservative comparison vs LR-FHSS TX energy per burst

Run:
```bash
python experiments/exp9_pgrl_footprint/run_footprint.py
```
Outputs `results.json` and `footprint_report.md`.

**Scope.** Param/MAC counts are exact. MCU inference time/energy use a
datasheet-order Cortex-M4F figure — an order-of-magnitude feasibility estimate,
**not** a measured on-device number. No hardware inference was run.
