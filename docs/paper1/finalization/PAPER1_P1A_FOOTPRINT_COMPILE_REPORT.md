# Paper 1 P1a Footprint Compile Report

## Scope

This pass produced compile-only NUCLEO-L476RG evidence for the PGRL footprint
storage envelope. No RF code was used. No LR1121 initialization was present. No
USRP, OTA, packet, or transmit path was run. The board was not flashed.

## Build target

- Sketch: `firmware_patches/nucleo_footprint_benchmark/nucleo_footprint_benchmark.ino`
- Board: `STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_L476RG,xserial=generic,usb=none,upload_method=MassStorage`
- Tool: `arduino-cli 1.5.1`
- STM32 core: `STMicroelectronics:stm32 2.12.0`
- Build output directory: `/tmp/p1a_nucleo_footprint_build`

## Build result

Arduino CLI completed successfully:

```text
Sketch uses 350292 bytes (33%) of program storage space. Maximum is 1048576 bytes.
Global variables use 1980 bytes (2%) of dynamic memory, leaving 96324 bytes for local variables. Maximum is 98304 bytes.
```

ELF section summary:

```text
text   data  bss   dec     hex
350588 128   3392  354108  5673c
```

Detailed sections:

```text
.isr_vector             392 bytes
.text                15,416 bytes
.rodata             334,748 bytes
.data                   128 bytes
.bss                  1,852 bytes
._user_heap_stack      1,540 bytes
```

The reserved model-weight symbol is:

```text
pgrl_int8_weight_store: 0x51798 bytes = 333,720 bytes
```

## Consistency with the 326 KB int8 claim

The compile-only NUCLEO build supports the storage part of the current estimate:

- exp9 int8 weight accounting: 333,720 bytes = 325.9 KiB
- NUCLEO compile-only reserved weight object: 333,720 bytes
- full no-radio Arduino firmware image: 350,292 bytes program storage, 33% of
  STM32L476RG 1 MiB Flash

This is consistent with a "about 326 KiB int8 model storage" claim. It does not
prove a production quantized inference implementation, because generated int8
weights and CMSIS-NN/TFLite kernels are not present in the repo.

## RAM interpretation

The benchmark reserves 768 bytes for model activation/scratch buffers. The full
Arduino runtime reports 1,980 bytes of global dynamic memory and the ELF reports
1,852 bytes of `.bss` plus 128 bytes `.data`.

This supports a sub-kilobyte model-working-buffer envelope, but total firmware
RAM is larger once the Arduino/Serial runtime is included.

## Latency and energy

No latency or energy measurement was performed. The current 12.5 ms / 1.07 mJ
figures remain estimates from `experiments/exp9_pgrl_footprint/run_footprint.py`.

Measured latency would require flashing and running the no-radio benchmark on
NUCLEO. That was intentionally not done in this pass.

## Limitations

- Compile-only evidence; no board execution.
- Storage-envelope benchmark; not a generated production inference kernel.
- No quantized model export pipeline was found.
- No current measurement was taken.
- No RF, no TX, no USRP, no OTA.

## Recommendation

Use the new compile-only result only to support the Flash feasibility wording.
Keep latency and energy explicitly estimated, or remove those numbers from the
main paper if the venue expects measured firmware evidence.
