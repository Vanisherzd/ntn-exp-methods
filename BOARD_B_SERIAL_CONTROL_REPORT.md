# Board B Serial / Control Investigation Report

**Agent:** Agent 2 (Board B serial/control, READ-ONLY)
**Date:** 2026-06-26
**Board:** Board B, NUCLEO-L476RG, ST-LINK SN 066CFF3031454D3043073845

## Connection used

- **Port:** `/dev/cu.usbmodem1303`
- **Baud:** `115200` (8N1)
- **Mode:** Read-only. DTR and RTS deasserted on open (no board reset asserted). No bytes were ever written to the port.
- **Capture duration:** 25 s primary + 18 s confirmation pass.

## Observed serial output (quoted, verbatim)

The board streams a continuous, repeating block of three lines per iteration:

```
Packet to send: 000102030405060708090a
RF=868000000 Hz, PWR=10 dBm, payload_len=11
Packet sent!
Packet to send: 000102030405060708090a0b
RF=868000000 Hz, PWR=10 dBm, payload_len=12
Packet sent!
...
Packet to send: 000102030405060708090a0b0c0d0e0f1011121314151617
RF=868000000 Hz, PWR=10 dBm, payload_len=24
Packet sent!
```

Across two separate captures the `payload_len` counter rose monotonically (11 -> 24 in the
first pass, then 33 -> 40 in the second pass), confirming a **free-running auto-loop** that
increments the payload by one byte each iteration. The payload is a fixed incrementing byte
pattern `00 01 02 03 ...`.

## CLI vs. boot/status log

- **No CLI / no interactive prompt.** No `>` prompt, no menu, no banner inviting input was
  ever printed. Output is a **periodic auto-loop**, not one-shot, not request/response.
- **No boot banner** was captured (the board was already running mid-loop; reset cannot be
  pressed remotely). Output is purely the repeating TX status block above.

## Frequency / TX power query

- These values are **not queryable on demand** — there is no command interface. They are
  **printed unconditionally on every loop iteration** as part of the status line.
- **Observed frequency:** `RF=868000000 Hz` (868.000 MHz) — constant on every line.
- **Observed TX power:** `PWR=10 dBm` — constant on every line.

## Can frequency be reconfigured WITHOUT flashing?

**NO — no evidence of any settable/runtime-configurable parameter.**
There is no command parser, no prompt, and no input path of any kind. RF frequency (868 MHz)
and TX power (10 dBm) are hard-coded constants emitted by firmware. Changing them requires
**re-flashing** the firmware. They cannot be altered over the serial CDC link.

## Non-TX query command attempted

**None.** Per the safety gate, a query is permitted only if a clear interactive prompt/menu
is observed. No prompt was present, so **no bytes were written to the port at all**. The
capture was 100% passive.

## IMPORTANT safety note (autonomous TX)

The firmware **transmits autonomously**: each loop iteration prints `Packet sent!`, meaning
the board is keying RF TX on its own at 868 MHz / 10 dBm with an ever-growing payload, with
**no command or button trigger required**. This TX is initiated entirely by the firmware, not
by this agent. (This agent issued no commands and triggered nothing.) If RF emission must be
stopped, the board has to be powered down or re-flashed — there is no serial "stop" command.

## Flash-dump cross-confirmation (2026-06-26)

A read-only flash dump (STM32CubeProgrammer v2.21.0, connect-under-reset, no erase)
confirms the serial behavior at the firmware level. Dump strings include:
`LR11XX-LR-FHSS Ping Init`, `RF=%lu Hz, PWR=%d dBm, payload_len=%u`, `Packet sent!`,
`Packet to send:`, `lr1121_xtal`. This is the **stock Semtech SWDM001
`lr11xx_lr_fhss_ping` demo**. The frequency/power are runtime format args
(`%lu`/`%d`) — i.e. compiled constants, which is why the serial offers no way to
change them. Confirms: reconfiguration to 923.2 MHz / lowest power requires reflash.
- Device: STM32L476 (ID `0x415`, Rev 4), 1 MB flash
- SHA-256: `c1a7402d6c2429372c57f9cae02e176d7c9b0461c9aae3383be85148a6bc870c`

## Artifacts

- Raw captured serial bytes: `/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/board_inventory/board_b_serial_raw.log`
- Flash dump + strings + sha256: `hardware_conducted_iq/board_inventory/board_B_flash_dump_20260626_001321/`
