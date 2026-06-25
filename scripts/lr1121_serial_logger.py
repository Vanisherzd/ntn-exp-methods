#!/usr/bin/env python3
"""Read-only serial logger for LR1121 board inventory.

This script never writes to the serial port. It only enumerates candidate ports,
opens a selected port, and records received bytes to a text log.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import serial
from serial.tools import list_ports


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        required=True,
        help="Path to the serial log text file.",
    )
    parser.add_argument(
        "--port",
        default=None,
        help="Serial port to use. If omitted, the first candidate port is used.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=20.0,
        help="Seconds to listen on each baud-rate attempt.",
    )
    parser.add_argument(
        "--baud-rates",
        default="115200,57600,38400,19200,9600",
        help="Comma-separated baud rates to try, in order.",
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only list candidate ports and exit.",
    )
    return parser.parse_args()


def candidate_ports() -> list[serial.tools.list_ports_common.ListPortInfo]:
    ports = list(list_ports.comports())
    scored = []
    for port in ports:
        score = 0
        text = " ".join(
            x for x in [port.device, port.description or "", port.manufacturer or ""] if x
        ).lower()
        if "usbmodem" in port.device.lower():
            score += 30
        if "st" in text or "stm" in text or "stlink" in text:
            score += 20
        if "usb" in text:
            score += 10
        scored.append((score, port))
    return [port for _, port in sorted(scored, key=lambda item: (-item[0], item[1].device))]


def list_candidates() -> str:
    lines = ["Candidate serial ports:"]
    ports = candidate_ports()
    if not ports:
        lines.append("(none found)")
        return "\n".join(lines)
    for port in ports:
        lines.append(
            f"- {port.device} | desc={port.description!r} | hwid={port.hwid!r} | manufacturer={port.manufacturer!r}"
        )
    return "\n".join(lines)


def read_once(port_name: str, baud_rate: int, duration: float) -> tuple[bytes, str | None]:
    started = time.time()
    chunks: list[bytes] = []
    error: str | None = None
    try:
        with serial.Serial(
            port=port_name,
            baudrate=baud_rate,
            timeout=0.2,
            write_timeout=0.2,
            rtscts=False,
            dsrdtr=False,
            exclusive=True,
        ) as ser:
            # Keep lines deasserted after open; this is read-only logging.
            try:
                ser.dtr = False
                ser.rts = False
            except Exception:
                pass
            while time.time() - started < duration:
                data = ser.read(4096)
                if data:
                    chunks.append(data)
    except Exception as exc:  # pragma: no cover - hardware dependent
        error = f"{type(exc).__name__}: {exc}"
    return b"".join(chunks), error


def printable_ratio(blob: bytes) -> float:
    if not blob:
        return 0.0
    printable = sum(1 for b in blob if b in b"\r\n\t" or 32 <= b < 127)
    return printable / len(blob)


def main() -> int:
    args = parse_args()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ports = candidate_ports()
    listing = list_candidates()
    print(listing)
    if args.list_only:
        out_path.write_text(listing + "\n", encoding="utf-8")
        return 0

    if not ports and not args.port:
        print("No candidate serial ports found.", file=sys.stderr)
        out_path.write_text(listing + "\nNo candidate serial ports found.\n", encoding="utf-8")
        return 1

    port_name = args.port or ports[0].device
    baud_rates = [int(part.strip()) for part in args.baud_rates.split(",") if part.strip()]

    lines = [listing, "", f"Selected port: {port_name}", f"Duration per baud attempt: {args.duration}s", ""]
    best_blob = b""
    best_baud: int | None = None
    best_error: str | None = None
    best_ratio = -1.0

    print(f"\nListening on {port_name}. If the board has a reset button, press reset now.")
    for baud in baud_rates:
        print(f"Trying baud {baud}...")
        blob, error = read_once(port_name, baud, args.duration)
        ratio = printable_ratio(blob)
        lines.append(f"## Baud {baud}")
        lines.append(f"bytes_received={len(blob)}")
        lines.append(f"printable_ratio={ratio:.3f}")
        if error:
            lines.append(f"error={error}")
        if blob:
            decoded = blob.decode("utf-8", errors="replace")
            lines.append("--- BEGIN LOG ---")
            lines.append(decoded.rstrip("\n"))
            lines.append("--- END LOG ---")
        lines.append("")
        if len(blob) > len(best_blob) or (len(blob) == len(best_blob) and ratio > best_ratio):
            best_blob = blob
            best_baud = baud
            best_error = error
            best_ratio = ratio

    lines.append("## Best attempt")
    lines.append(f"best_baud={best_baud}")
    lines.append(f"bytes_received={len(best_blob)}")
    lines.append(f"printable_ratio={best_ratio:.3f}")
    if best_error:
        lines.append(f"best_error={best_error}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved serial log to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
