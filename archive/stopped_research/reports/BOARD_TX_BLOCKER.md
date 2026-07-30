# BOARD TX Blocker

Deterministic LR1121 TX bring-up is currently blocked because the repo does not contain the actual board-control path.

Missing pieces:

1. Firmware source or binary provenance for the active NUCLEO-L476RG + LR1121 image.
2. Build instructions for that firmware.
3. Flash/upload instructions for that firmware.
4. A repo-local command or script that starts LR1121 TX at `923200000 Hz`.
5. A repo-local command or script that stops LR1121 TX.
6. A repo-local command or script that prints live board status:
   - configured frequency
   - TX power
   - TX start time
   - TX done time
7. Any repo-local documentation confirming which physical RF connector on the current board assembly is the active TX path.

Available evidence is historical only:

- UART logs show past TX attempts at `868000000 Hz` / `10 dBm`.
- Historical sweep summaries mention `firmware_tx_reported_but_no_rf_detected`.
- The current repo contains only an example TX config JSON, not the uploader or control path that applies it to the board.

Until those missing pieces are added, LR1121 TX timing remains unverified during conducted IQ capture windows.
