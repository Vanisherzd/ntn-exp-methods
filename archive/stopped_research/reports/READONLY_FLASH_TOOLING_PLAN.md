# Read-Only Flash Dump + Fingerprint Plan (PLAN ONLY)

Status: **PLAN ONLY — do not execute connecting/erasing commands without explicit operator go-ahead.**
Date: 2026-06-25
Target board: Board B, NUCLEO-L476RG (STM32L476RG), ST-LINK SN `066CFF3031454D3043073845`
Serial port `/dev/cu.usbmodem1303` is owned by Agent 2 — do not touch it. The SWD debug interface used below is a *separate* USB endpoint from the VCP serial port, but see the HALT warning before connecting.

---

## 0. Recommended tool: STM32CubeProgrammer (ALREADY INSTALLED — no install needed)

Verified present:

- Version: **STM32CubeProgrammer v2.21.0**
- CLI binary (full path):
  ```
  /Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer/STM32CubeProgrammer.app/Contents/Resources/bin/STM32_Programmer_CLI
  ```

To save typing, the operator MAY define a shell alias for the session (read-only, harmless):

```bash
export STM32CLI="/Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer/STM32CubeProgrammer.app/Contents/Resources/bin/STM32_Programmer_CLI"
```

The plan below uses `"$STM32CLI"`. Everything is built on STM32CubeProgrammer; the alternative tools (stlink/pyocd) are documented in section 6 but are **NOT NEEDED**.

---

## 1. CRITICAL WARNING — connecting halts the CPU

Even a pure read connection over SWD will **halt the running firmware** on the target. The act of attaching the debugger stops the CPU; it does NOT erase or modify flash, but the LR-FHSS / board-TX firmware will stop running until the next reset/power-cycle.

Rules:
- Only run any of the connecting commands below when **no board-TX session is needed** (coordinate with Agent 2 — the serial logging session must be idle/stopped).
- Use `mode=HOTPLUG`. HOTPLUG attaches without asserting a hardware reset and without a forced under-reset halt sequence, which is the least disruptive way to connect. (The CPU is still halted by the debug attach itself, but flash content is untouched.)
- Do NOT add `mode=UR` (under-reset) or `mode=POWERDOWN` for a read-only dump — UR resets the MCU.
- After you finish, the firmware resumes only on a reset/power-cycle; plan to power-cycle the board when done if you need TX to resume.

---

## 2. Read chip ID / device fingerprint (READ-ONLY)

This is the safest first step. It connects, reads the device/identification registers, prints them, and exits. No flash read, no write, no erase.

```bash
"$STM32CLI" -c port=SWD mode=HOTPLUG
```

A bare connect (no action command after it) connects, prints the device fingerprint block, then disconnects. Expected output includes:

- ST-LINK serial number (should match `066CFF3031454D3043073845`)
- Device ID (STM32L476 family = `0x415`)
- Flash size, CPU core, Device name / "BoardName : NUCLEO-L476RG"
- Revision ID, Unique device ID (UID, 96-bit)

Optional explicit reads of identity registers (still read-only, `-r32` = read 32-bit words):

```bash
# Unique device ID (UID), 96 bits = 3 words @ 0x1FFF7590
"$STM32CLI" -c port=SWD mode=HOTPLUG -r32 0x1FFF7590 0x0C

# Flash size register (KB), 16-bit @ 0x1FFF75E0  (read 4 bytes is fine)
"$STM32CLI" -c port=SWD mode=HOTPLUG -r32 0x1FFF75E0 0x04

# DBGMCU IDCODE (device + rev id) @ 0xE0042000
"$STM32CLI" -c port=SWD mode=HOTPLUG -r32 0xE0042000 0x04
```

These print words to the console only; nothing is written to disk or to the chip.

---

## 3. Read-only full flash DUMP to .bin (NO ERASE, NO WRITE)

STM32L476RG main flash: base `0x08000000`, size 1 MB = `0x100000` bytes.

Recommended dump command (saves current flash content verbatim to a file — purely a read):

```bash
"$STM32CLI" -c port=SWD mode=HOTPLUG --upload 0x08000000 0x100000 "$HOME/Desktop/LEO-Hybrid-PGRL/output/boardB_flash_dump_$(date +%Y%m%d_%H%M%S).bin"
```

Notes on the read command:
- `--upload <address> <size> <file.bin>` is the STM32CubeProgrammer **read-to-file** command (alias: `-u`). "Upload" here means MCU → host (reading OUT of the chip). It does NOT modify the device.
- `0x08000000` = main flash base for STM32L476.
- `0x100000` = 1,048,576 bytes (full 1 MB). If you only want the used region you can use a smaller size, e.g. `0x40000` (256 KB) — but full dump is safest for a fingerprint baseline.
- Output `.bin` goes under the repo `output/` dir with a timestamp so repeated dumps never overwrite each other.

Console-only inspection variant (no file written), read first words of the vector table / start of flash:

```bash
# Read first 256 bytes of flash and print to console (read-only)
"$STM32CLI" -c port=SWD mode=HOTPLUG -r32 0x08000000 0x100
```

After dumping, fingerprint the file on the host (no board involved):

```bash
shasum -a 256 "$HOME/Desktop/LEO-Hybrid-PGRL/output/"boardB_flash_dump_*.bin
ls -la "$HOME/Desktop/LEO-Hybrid-PGRL/output/"boardB_flash_dump_*.bin
```

---

## 4. FORBIDDEN FLAGS — never type these against this board

These flags (and any command containing them) WRITE, ERASE, or MODIFY the chip and are strictly out of scope for a read-only dump. Do NOT use:

| Forbidden flag / form | What it does (why banned) |
|---|---|
| `-e` , `--erase` | Erase sectors / pages |
| `-e all` , `--erase all` | **Mass erase** entire flash |
| `--mass-erase` , `-me` | Full chip mass erase |
| `-w` , `--write` , `--download` | Write/program a file into flash |
| `-d` , `--download` | Download/program firmware (write) |
| `-v` after a write | (verify is read-only, but only appears in write flows — avoid the write that precedes it) |
| `-ob` , `--obwrite` , `-ob <...>` | Option-byte WRITE (can brick / change RDP/BOR/etc.) |
| `--rdp` , RDP level changes | Readout protection change — can trigger mass erase on level transition |
| `-hardRst` / `-rst` combined with write flows | Reset sequences tied to programming |
| `mode=UR` (under-reset) | Resets the MCU on connect (not a dump need) |
| `mode=POWERDOWN` | Power-cycles target |
| `-tzenreg` / `-swd ... secure` provisioning | Security/TrustZone provisioning writes |
| `--otp` writes | One-time-programmable writes (irreversible) |

Allowed (read-only) flags only: `-c port=SWD mode=HOTPLUG`, `--upload`/`-u`, `-r32`/`-r16`/`-r8`, plain connect for fingerprint. Nothing else.

Rule of thumb: if a command would change bytes on the chip, it is forbidden here. The only writing this plan does is to a `.bin` file **on the host disk**, never to the MCU.

---

## 5. Suggested safe sequence (read-only)

1. Confirm Agent 2's serial/TX session is stopped (board not actively transmitting needed).
2. `export STM32CLI=...` (section 0).
3. Fingerprint: bare connect (section 2) — confirm SN + device ID 0x415.
4. Full dump: `--upload` (section 3).
5. Hash the `.bin` (section 3).
6. Power-cycle the board if TX firmware needs to resume.

---

## 6. Alternative install path — OPTIONAL, NOT NEEDED (Cube already covers this)

Only if STM32CubeProgrammer somehow fails. Both are reversible. These are documented for completeness; **do not install automatically**.

Option A — stlink tools via Homebrew:
```bash
brew install stlink
# read-only dump after install (st-flash read = MCU->file, no erase):
st-flash read "$HOME/Desktop/LEO-Hybrid-PGRL/output/boardB_flash_stlink.bin" 0x08000000 0x100000
st-info --probe   # fingerprint (read-only)
```

Option B — pyOCD via uv (no global Python pollution):
```bash
/Users/laizhendong/.local/bin/uv tool install pyocd
# fingerprint:
pyocd list
# read-only dump (pyocd flash tool supports read; example):
pyocd cmd -c "savemem 0x08000000 0x100000 $HOME/Desktop/LEO-Hybrid-PGRL/output/boardB_flash_pyocd.bin"
```

Reversal if installed and unwanted:
```bash
brew uninstall stlink
/Users/laizhendong/.local/bin/uv tool uninstall pyocd
```

Reminder: these alternatives are **NOT NEEDED** because STM32CubeProgrammer v2.21.0 is already installed and is the recommended path.
