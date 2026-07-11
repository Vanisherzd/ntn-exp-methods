# Paper 1 P1a NUCLEO Footprint Plan

## Current paper estimate

The current MCU-footprint paragraph in `paper/icc_main.tex` reports:

- 333,720 parameters
- 332,288 MACs per inference
- about 326 KB int8 Flash
- less than 1 KB model working RAM
- estimated 12.5 ms / 1.07 mJ on a Cortex-M4F-class core

These numbers currently come from `experiments/exp9_pgrl_footprint/run_footprint.py`.
That script instantiates:

`physics_ml/pinn_core.py :: TrajectoryPINN(orbital_elem_dim=6, hidden_dim=256, num_layers=6, fourier_features=128, output_uncertainty=True)`

The parameter and MAC counts are exact for that PyTorch model. The latency and
energy are not measured on a board; they are computed from an 80 MHz Cortex-M4F
clock, 3 cycles/MAC, and a datasheet-order active-power estimate.

## Current implementation status

- Generated C/C++ inference code: not found.
- Generated quantized int8 weights: not found.
- CMSIS-NN / TFLite Micro project for this model: not found.
- Buildable NUCLEO-L476RG project: yes, via Arduino STM32 core, but existing
  firmware sketches are LR1121 RF/TX sketches and must not be reused for this
  task.
- Current exp9 evidence before this pass: Python-side static accounting only.

## Feasible measurement path

Chosen safe path for this pass: **Path A, compile-time footprint only**.

The added sketch is:

`firmware_patches/nucleo_footprint_benchmark/nucleo_footprint_benchmark.ino`

It does not include RadioLib, does not initialize LR1121, does not configure RF
pins, and does not transmit. It reserves the exact exp9 int8 model-storage
envelope in Flash and compiles a no-radio loop shaped by the counted MAC
structure.

Path B, latency measurement, requires flashing and running the NUCLEO. That was
not performed. If latency is needed, stop for explicit operator confirmation
before flashing.

## Safe compile command

Compile only:

```sh
rm -rf /tmp/p1a_nucleo_footprint_build /tmp/p1a_nucleo_footprint_out
arduino-cli compile \
  --fqbn 'STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_L476RG,xserial=generic,usb=none,upload_method=MassStorage' \
  --build-path /tmp/p1a_nucleo_footprint_build \
  --output-dir /tmp/p1a_nucleo_footprint_out \
  firmware_patches/nucleo_footprint_benchmark
```

Parse ELF sections:

```sh
/Users/laizhendong/Library/Arduino15/packages/STMicroelectronics/tools/xpack-arm-none-eabi-gcc/14.2.1-1.1/bin/arm-none-eabi-size \
  /tmp/p1a_nucleo_footprint_build/nucleo_footprint_benchmark.ino.elf

/Users/laizhendong/Library/Arduino15/packages/STMicroelectronics/tools/xpack-arm-none-eabi-gcc/14.2.1-1.1/bin/arm-none-eabi-size -A \
  /tmp/p1a_nucleo_footprint_build/nucleo_footprint_benchmark.ino.elf
```

## Flashing gate

Flashing is needed only for latency measurement. It was not performed.

If explicitly approved later, the operator should use an upload/flash command
only after confirming that no radio board, antenna, or RF path is connected.
This benchmark has no RF code, but the flash step still touches hardware and
requires explicit confirmation.

Not executed in this pass, but the exact gated command would be:

```sh
arduino-cli compile --upload \
  --fqbn 'STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_L476RG,xserial=generic,usb=none,upload_method=MassStorage' \
  firmware_patches/nucleo_footprint_benchmark
```

## Paper update path if compile-only evidence is used

Safe update:

- Keep parameter and MAC counts as exact static model accounting.
- Replace or support the Flash sentence with NUCLEO-L476RG compile-only storage
  evidence: the reserved int8 weight object is 333,720 bytes, matching about
  326 KiB.
- State that the full no-radio Arduino firmware image uses 350,136 bytes of
  program storage on STM32L476RG in the compile-only build.
- Keep latency and energy as estimates, or remove them from the main paper if
  reviewers demand board evidence.

Recommended conservative paper wording after P1a:

> A compile-only NUCLEO-L476RG storage-envelope build reserves 333,720 bytes for
> int8 model weights (about 326 KiB) and builds as a 350,292-byte no-radio
> firmware image; latency and energy remain estimates until a gated on-device
> timing run is approved.

## Paper update path if measurement is required

If the paper needs measured latency/energy rather than compile-only footprint,
do not use the current 12.5 ms / 1.07 mJ sentence as measured evidence. Either:

1. run an explicitly approved no-radio flash/timing pass on NUCLEO, or
2. delete or further downgrade the latency/energy sentence to a static estimate
   outside the contribution path.
