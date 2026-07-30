# Paper 1 Fig. 4 V3 Evidence Matrix Report

## Why Fig. 4 was replaced

The previous Fig. 4 still read as a lab-note composite: a setup sketch, an awkward before/after bar plus text block, and a small spectrum trace. That made the spectrum look like the main proof object even though the intended claim is narrower: conducted IQ-level measurement-path sanity evidence.

## Final layout choice

The new figure is a single-column conducted-IQ measurement-path evidence matrix with three horizontal blocks:

- Block A: measurement protocol chain from deterministic firmware through LR1121/NUCLEO, 50 dB attenuated coax, USRP B210 RX2 A, and artifact-aware IQ analysis.
- Block B: aligned evidence matrix covering serial verification, before/after control, repeatability, 2 MS/s sanity, artifact-aware result, and scope boundary.
- Block C: subordinate supporting trace.

The before/after bar chart and raw run-list text were removed. Repeatability is reported only as `41.25 +/- 0.36 dB`.

## Spectrum thumbnail

The artifact-masked TX-ON/TX-OFF max-hold spectrum thumbnail was kept, but it is visually subordinate to the evidence matrix. It supports the artifact-aware row without making the spectrum the main validation object.

## Source artifacts used

- `hardware_conducted_iq/repeatability_summary.csv`
- `hardware_conducted_iq/before_after_reflash_summary.csv`
- `hardware_conducted_iq/overflow_sanity_summary.md`
- `hardware_conducted_iq/20260626_003643_gain20_50db/artifact_masked_signal_detection_summary.json`
- `hardware_conducted_iq/20260626_003643_gain20_50db/artifact_masked_maxhold_txon_vs_noise.png`
- `hardware_conducted_iq/board_inventory/board_B_flash_9232_20260626_002829/post_flash_serial_log.txt`
- `hardware_conducted_iq/board_inventory/board_B_flash_9232_20260626_002829/post_flash_serial_log_fullwindow.txt`

## Raw IQ use

No raw IQ was used. No `.npy`, `.fc32`, `.cfile`, or flash dump `.bin` was read or committed. No hardware, firmware flashing, USRP capture, or OTA action was run.

## Page count and build

- Build command: `tectonic paper/icc_main.tex`
- Output: `paper/icc_main.pdf`
- Page count: 6 pages including references
- Existing warnings remain: `algorithm.sty` invalid UTF-8 and underfull boxes. The build exits successfully.

## No-overclaim scan

`RF validation` is absent. The risky-term scan for `packet`, `PER`, `PDR`, `CRC`, `gateway`, `ACK`, `OTA`, `live-satellite`, `decoded`, `measured Doppler`, and `truth` shows hits only in literature context, proxy labels, explicit non-claim statements, limitations, or future-work text. The new Fig. 4 wording remains a conducted measurement-path sanity check only.

## Minus-sign check

Targeted scan found no bare positive `17 dBm` in the hardware context in `paper/icc_main.tex` or the figure generator. The manuscript uses `$-17$~dBm`; the generated figure uses `-17 dBm`.

## Remaining visual risks

The supporting trace remains a raster thumbnail from an existing processed PNG, so its axis text is less sharp than the vector protocol and matrix. This is intentional: the figure now treats the spectrum as subordinate evidence, not the primary proof object.
