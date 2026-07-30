#!/usr/bin/env python3
"""
exp9 — PGRL footprint profile (software-only, deployment accounting)
====================================================================
Profiles the deployable PGRL predictor (TrajectoryPINN, the SGP4-anchored
residual corrector) for embedded-terminal feasibility:

  - parameter count                       (exact, from the model)
  - MACs / FLOPs per inference            (exact, summed over Linear layers)
  - estimated RAM / Flash footprint       (fp32 and int8)
  - offline-training / endpoint inference-only statement
  - conservative comparison vs LR-FHSS TX energy per burst

SCOPE: software-only accounting. MCU energy uses a published Cortex-M4-class
power figure; it is an order-of-magnitude feasibility estimate, not a measured
on-device number.

Outputs:
  experiments/exp9_pgrl_footprint/results.json
  experiments/exp9_pgrl_footprint/footprint_report.md
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import torch
import torch.nn as nn

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from physics_ml.pinn_core import TrajectoryPINN, count_parameters
from controller.energy_model import tx_energy

HERE = os.path.dirname(__file__)

# ── MCU / radio assumptions (documented, conservative) ─────────────────────────
MCU_NAME            = "Cortex-M4F @ 80 MHz (e.g. STM32L4)"
MCU_CLOCK_HZ        = 80e6
MCU_ACTIVE_MW       = 86.0      # ~26 mA @ 3.3 V active (STM32L4 datasheet order)
CYCLES_PER_MAC      = 3.0       # conservative M4 MAC+load/store (no CMSIS-NN SIMD)
BYTES_FP32          = 4
BYTES_INT8          = 1

# Radio: LR-FHSS uplink burst (consistent with exp2 / proxy model)
TX_POWER_DBM        = 14.0
TX_BURST_S          = 0.200
PA_EFFICIENCY       = 0.30      # conservative PA wall-plug efficiency


def count_linear_macs(model: nn.Module) -> int:
    """Sum MACs over all nn.Linear layers (batch=1). MACs ≈ in_features*out_features."""
    macs = 0
    for m in model.modules():
        if isinstance(m, nn.Linear):
            macs += m.in_features * m.out_features
    return macs


def main():
    model = TrajectoryPINN(
        orbital_elem_dim=6, hidden_dim=256, num_layers=6,
        fourier_features=128, output_uncertainty=True,
    )
    total_params = sum(p.numel() for p in model.parameters())
    trainable = count_parameters(model)
    macs = count_linear_macs(model)
    flops = 2 * macs   # 1 MAC = 1 mul + 1 add

    per_module = {n: sum(p.numel() for p in mod.parameters())
                  for n, mod in model.named_children()}

    # ── Memory footprint ───────────────────────────────────────────────────────
    flash_fp32_kb = total_params * BYTES_FP32 / 1024
    flash_int8_kb = total_params * BYTES_INT8 / 1024
    # Working RAM ≈ 2 largest activation buffers (hidden_dim) + I/O, int8.
    ram_int8_kb = (2 * 256 * BYTES_INT8 + 512) / 1024  # ~ <1 KB activations

    # ── Inference cost / energy ────────────────────────────────────────────────
    cycles = macs * CYCLES_PER_MAC
    infer_time_s = cycles / MCU_CLOCK_HZ
    infer_energy_mj = MCU_ACTIVE_MW * 1e-3 * infer_time_s * 1e3  # mJ

    # ── LR-FHSS TX energy per burst ────────────────────────────────────────────
    tx_radiated_j = tx_energy(TX_POWER_DBM, TX_BURST_S)            # radiated
    tx_draw_j = tx_radiated_j / PA_EFFICIENCY                      # wall-plug draw
    tx_radiated_mj = tx_radiated_j * 1e3
    tx_draw_mj = tx_draw_j * 1e3

    ratio_per_burst = infer_energy_mj / tx_draw_mj
    # One inference produces the whole-pass schedule; amortise over ~N bursts/pass.
    bursts_per_pass = 20
    ratio_per_pass = infer_energy_mj / (tx_draw_mj * bursts_per_pass)

    results = {
        "_reproducibility": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "validation_type": "static_accounting",
            "script": "experiments/exp9_pgrl_footprint/run_footprint.py",
            "model": "physics_ml/pinn_core.py :: TrajectoryPINN",
            "mcu": MCU_NAME, "cycles_per_mac": CYCLES_PER_MAC,
            "limitations": (
                "Order-of-magnitude embedded feasibility estimate. MACs exact; "
                "MCU energy uses datasheet-order power, not a measured on-device "
                "number. No hardware inference was run."
            ),
        },
        "experiment": "exp9_pgrl_footprint",
        "model_config": {"hidden_dim": 256, "num_layers": 6,
                         "fourier_features": 128, "output_uncertainty": True},
        "parameters": {"total": total_params, "trainable": trainable,
                       "per_module": per_module},
        "compute": {"macs_per_inference": macs, "flops_per_inference": flops,
                    "cycles_per_mac": CYCLES_PER_MAC,
                    "est_inference_time_ms": infer_time_s * 1e3,
                    "est_inference_energy_mj": infer_energy_mj},
        "memory": {"flash_fp32_kb": flash_fp32_kb, "flash_int8_kb": flash_int8_kb,
                   "working_ram_int8_kb": ram_int8_kb},
        "energy_vs_lrfhss": {
            "tx_radiated_mj_per_burst": tx_radiated_mj,
            "tx_draw_mj_per_burst": tx_draw_mj,
            "pa_efficiency": PA_EFFICIENCY,
            "infer_energy_mj": infer_energy_mj,
            "infer_to_tx_ratio_per_burst": ratio_per_burst,
            "infer_to_tx_ratio_per_pass": ratio_per_pass,
            "bursts_per_pass": bursts_per_pass,
        },
        "deployment_model": (
            "Offline training on a host/training machine; the endpoint runs "
            "inference-only (frozen weights, no gradient, no optimizer state). "
            "One forward pass per satellite pass produces the timing + Doppler "
            "schedule, amortised over all bursts in that pass."
        ),
    }
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    # ── Markdown report ────────────────────────────────────────────────────────
    md = f"""# PGRL Footprint Profile (software-only accounting)

> Model: `physics_ml/pinn_core.py :: TrajectoryPINN`
> (hidden 256, 6 layers, 128 Fourier features, Gaussian-NLL uncertainty head).
> Software-only static accounting — no on-device inference was run. MAC/param
> counts are exact; MCU energy is a datasheet-order feasibility estimate.

## Parameters
- **Total parameters:** {total_params:,}
- Trainable: {trainable:,}
- Per module: """ + ", ".join(f"`{k}`={v:,}" for k, v in per_module.items()) + f"""

## Compute per inference
- **MACs / inference:** {macs:,}
- **FLOPs / inference:** {flops:,} (1 MAC = 2 FLOPs)
- Est. inference time: **{infer_time_s*1e3:.1f} ms** on {MCU_NAME}
  ({CYCLES_PER_MAC:.0f} cycles/MAC, no CMSIS-NN SIMD)
- Est. inference energy: **{infer_energy_mj:.2f} mJ**

## Memory footprint
- **Flash (fp32 weights):** {flash_fp32_kb:.0f} KB
- **Flash (int8 quantised):** {flash_int8_kb:.0f} KB
- **Working RAM (int8 activations):** < {ram_int8_kb:.1f} KB
- MCU-class feasible when sufficient Flash is available (the int8 weights need
  ≥{flash_int8_kb:.0f} KB Flash). Not claimed to fit ultra-minimal M0-class nodes;
  that would require separate on-device validation.

## Training / inference split
{results['deployment_model']}

## Conservative comparison vs LR-FHSS TX energy
- LR-FHSS burst radiated energy ({TX_POWER_DBM:.0f} dBm, {TX_BURST_S*1e3:.0f} ms): **{tx_radiated_mj:.2f} mJ**
- Wall-plug TX draw (PA η={PA_EFFICIENCY:.0%}): **{tx_draw_mj:.2f} mJ / burst**
- PGRL inference (**estimated**, not measured on-device): **{infer_energy_mj:.2f} mJ**, run **once per pass**.
- Inference / TX-draw, even charged **per single burst**: **{ratio_per_burst*100:.1f}%**
- Inference / TX-draw, amortised over **{bursts_per_pass} bursts/pass**: **{ratio_per_pass*100:.2f}%**

**Takeaway:** training is offline; the endpoint runs inference only. The estimated
per-pass inference overhead is **bounded** (a single-digit-percent fraction of one
LR-FHSS burst's transmit draw, smaller once amortised over a pass) and can be
**outweighed by avoiding the missed or repeated transmissions** quantified in
exp7/exp8. The MCU energy figure is an estimate, not a measured on-device value.
"""
    with open(os.path.join(HERE, "footprint_report.md"), "w") as f:
        f.write(md)

    # ── console ────────────────────────────────────────────────────────────────
    print("=" * 72)
    print("exp9 — PGRL footprint profile")
    print("=" * 72)
    print(f"  params              : {total_params:,}")
    print(f"  MACs / inference    : {macs:,}")
    print(f"  FLOPs / inference   : {flops:,}")
    print(f"  inference time (est) : {infer_time_s*1e3:.1f} ms @ {MCU_NAME}")
    print(f"  inference energy(est): {infer_energy_mj:.2f} mJ")
    print(f"  Flash fp32 / int8   : {flash_fp32_kb:.0f} KB / {flash_int8_kb:.0f} KB")
    print(f"  working RAM (int8)  : < {ram_int8_kb:.1f} KB")
    print(f"  LR-FHSS TX draw/burst: {tx_draw_mj:.2f} mJ  (radiated {tx_radiated_mj:.2f} mJ)")
    print(f"  infer/TX per burst  : {ratio_per_burst*100:.1f}%")
    print(f"  infer/TX per pass   : {ratio_per_pass*100:.2f}%  ({bursts_per_pass} bursts)")
    print("\nWrote results.json + footprint_report.md")


if __name__ == "__main__":
    main()
