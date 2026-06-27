# PGRL Footprint Profile (software-only accounting)

> Model: `physics_ml/pinn_core.py :: TrajectoryPINN`
> (hidden 256, 6 layers, 128 Fourier features, Gaussian-NLL uncertainty head).
> Software-only static accounting — no on-device inference was run. MAC/param
> counts are exact; MCU energy is a datasheet-order feasibility estimate.

## Parameters
- **Total parameters:** 333,720
- Trainable: 333,592
- Per module: `fourier_embed`=128, `siren_layers`=330,496, `mean_layer`=1,542, `log_var_layer`=1,542

## Compute per inference
- **MACs / inference:** 332,288
- **FLOPs / inference:** 664,576 (1 MAC = 2 FLOPs)
- Est. inference time: **12.5 ms** on Cortex-M4F @ 80 MHz (e.g. STM32L4)
  (3 cycles/MAC, no CMSIS-NN SIMD)
- Est. inference energy: **1.07 mJ**

## Memory footprint
- **Flash (fp32 weights):** 1304 KB
- **Flash (int8 quantised):** 326 KB
- **Working RAM (int8 activations):** < 1.0 KB
- MCU-class feasible when sufficient Flash is available (the int8 weights need
  ≥326 KB Flash). Not claimed to fit ultra-minimal M0-class nodes;
  that would require separate on-device validation.

## Training / inference split
Offline training on a host/training machine; the endpoint runs inference-only (frozen weights, no gradient, no optimizer state). One forward pass per satellite pass produces the timing + Doppler schedule, amortised over all bursts in that pass.

## Conservative comparison vs LR-FHSS TX energy
- LR-FHSS burst radiated energy (14 dBm, 200 ms): **5.02 mJ**
- Wall-plug TX draw (PA η=30%): **16.75 mJ / burst**
- PGRL inference (**estimated**, not measured on-device): **1.07 mJ**, run **once per pass**.
- Inference / TX-draw, even charged **per single burst**: **6.4%**
- Inference / TX-draw, amortised over **20 bursts/pass**: **0.32%**

**Takeaway:** training is offline; the endpoint runs inference only. The estimated
per-pass inference overhead is **bounded** (a single-digit-percent fraction of one
LR-FHSS burst's transmit draw, smaller once amortised over a pass) and can be
**outweighed by avoiding the missed or repeated transmissions** quantified in
exp7/exp8. The MCU energy figure is an estimate, not a measured on-device value.
