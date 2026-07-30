#!/usr/bin/env python3
"""Multi-frequency conducted IQ debug scan for LR1121 -> USRP B210 RX2 A."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_FREQ_LIST = "922000000,923200000,924400000"
DEFAULT_RATE = 4e6
DEFAULT_GAIN = 20.0
DEFAULT_ATTENUATION_DB = 50
DEFAULT_DURATION_OFF = 10.0
DEFAULT_DURATION_ON = 30.0
DEFAULT_CHANNEL = 0
DEFAULT_ANTENNA = "RX2"
DEFAULT_TX_CONTROL = "manual-countdown"
DEFAULT_TX_ON_DELAY = 8.0
VISIBLE_DELTA_DB = 6.0

REPO_ROOT = Path(__file__).resolve().parents[1]
CAPTURE_SCRIPT = REPO_ROOT / "scripts" / "usrp_rx2a_capture.py"
ANALYZE_SCRIPT = REPO_ROOT / "scripts" / "analyze_conducted_iq.py"
RUNS_ROOT = REPO_ROOT / "hardware_conducted_iq"
LATEST_SUMMARY = RUNS_ROOT / "latest_summary.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Conducted IQ debug scan across multiple center frequencies.")
    parser.add_argument("--freq-list", default=DEFAULT_FREQ_LIST)
    parser.add_argument("--rate", type=float, default=DEFAULT_RATE)
    parser.add_argument("--gain", type=float, default=DEFAULT_GAIN)
    parser.add_argument("--attenuation-db", type=int, default=DEFAULT_ATTENUATION_DB)
    parser.add_argument("--duration-off", type=float, default=DEFAULT_DURATION_OFF)
    parser.add_argument("--duration-on", type=float, default=DEFAULT_DURATION_ON)
    parser.add_argument("--channel", type=int, default=DEFAULT_CHANNEL, choices=[0])
    parser.add_argument("--antenna", default=DEFAULT_ANTENNA, choices=["RX2"])
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--confirm-board-freq", type=float, default=None)
    parser.add_argument("--confirm-hardware-ready", action="store_true")
    parser.add_argument("--confirm-lowest-tx-power", action="store_true")
    parser.add_argument("--confirm-conducted-only", action="store_true")
    parser.add_argument("--tx-control", choices=["manual-countdown", "command"], default=DEFAULT_TX_CONTROL)
    parser.add_argument("--tx-on-delay", type=float, default=DEFAULT_TX_ON_DELAY)
    parser.add_argument("--tx-on-cmd", default=None)
    parser.add_argument("--tx-off-cmd", default=None)
    return parser.parse_args()


def rf_path_label(attenuation_db: int) -> str:
    if attenuation_db == 50:
        return "LR1121 RF port -> 30 dB attenuator -> 20 dB attenuator -> SMA coax -> USRP B210 RX2 A"
    if attenuation_db == 60:
        return "LR1121 RF port -> 30 dB attenuator -> 20 dB attenuator -> 10 dB attenuator -> SMA coax -> USRP B210 RX2 A"
    return f"LR1121 RF port -> fixed conducted attenuation chain ({attenuation_db} dB total) -> SMA coax -> USRP B210 RX2 A"


def session_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def parse_freq_list(raw: str) -> list[float]:
    freqs: list[float] = []
    for token in raw.split(","):
        token = token.strip()
        if token:
            freqs.append(float(token))
    if not freqs:
        raise SystemExit("Frequency list is empty.")
    return freqs


def validate_yes_mode(args: argparse.Namespace) -> None:
    if not args.yes:
        return
    missing: list[str] = []
    if args.confirm_board_freq is None:
        missing.append("--confirm-board-freq")
    if not args.confirm_hardware_ready:
        missing.append("--confirm-hardware-ready")
    if not args.confirm_lowest_tx_power:
        missing.append("--confirm-lowest-tx-power")
    if not args.confirm_conducted_only:
        missing.append("--confirm-conducted-only")
    if missing:
        raise SystemExit(f"--yes requires all safety flags: {', '.join(missing)}")
    if args.tx_control == "command" and (not args.tx_on_cmd or not args.tx_off_cmd):
        raise SystemExit("--tx-control command requires both --tx-on-cmd and --tx-off-cmd.")


def print_preflight(args: argparse.Namespace, freqs: list[float]) -> None:
    print("\nPreflight checklist:")
    print("- LR1121 RF port, not GNSS port.")
    print("- 30 dB + 20 dB attenuation installed.")
    print("- 10 dB pad removed.")
    print("- Coax connected to USRP B210 RX2 A.")
    print(f"- USRP channel {args.channel}.")
    print(f"- UHD antenna {args.antenna}.")
    print("- USRP TX disabled.")
    print("- No antenna / no OTA.")
    print(f"- LR1121 firmware/config TX frequency confirmed at {args.confirm_board_freq:.0f} Hz.")
    print("- LR1121 TX power at lowest available setting.")
    print(f"- Debug scan frequencies: {', '.join(f'{f:.0f}' for f in freqs)} Hz.")


def run_subprocess(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, cwd=str(REPO_ROOT))


def run_control_command(label: str, command: str) -> None:
    print(f"\n{label}: {command}")
    subprocess.run(shlex.split(command), check=True, cwd=str(REPO_ROOT))


def countdown(message: str, delay_s: float) -> None:
    seconds = max(0, int(round(delay_s)))
    print(f"\n{message}")
    for remaining in range(seconds, 0, -1):
        print(f"  {remaining}...", flush=True)
        time.sleep(1.0)


def build_capture_cmd(
    *,
    freq: float,
    rate: float,
    gain: float,
    duration: float,
    out: Path,
    metadata: Path,
    antenna: str,
    channel: int,
    rf_path: str,
) -> list[str]:
    return [
        sys.executable,
        str(CAPTURE_SCRIPT),
        "--freq",
        str(freq),
        "--rate",
        str(rate),
        "--gain",
        str(gain),
        "--duration",
        str(duration),
        "--out",
        str(out),
        "--metadata",
        str(metadata),
        "--antenna",
        antenna,
        "--channel",
        str(channel),
        "--rf-path",
        rf_path,
    ]


def build_analyze_cmd(
    *,
    noise_iq: Path,
    txon_iq: Path,
    rate: float,
    freq: float,
    attenuation_db: int,
    outdir: Path,
    rf_path: str,
) -> list[str]:
    return [
        sys.executable,
        str(ANALYZE_SCRIPT),
        "--noise-iq",
        str(noise_iq),
        "--txon-iq",
        str(txon_iq),
        "--rate",
        str(rate),
        "--freq",
        str(freq),
        "--attenuation-db",
        str(attenuation_db),
        "--outdir",
        str(outdir),
        "--rf-path",
        rf_path,
    ]


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def is_visible(summary: dict[str, Any]) -> bool:
    return float(summary.get("txon_minus_noise_db", 0.0)) >= VISIBLE_DELTA_DB


def create_scan_root(stamp: str, attenuation_db: int) -> Path:
    path = RUNS_ROOT / f"{stamp}_debug_scan_{attenuation_db}db"
    path.mkdir(parents=True, exist_ok=False)
    return path


def create_run_dir(scan_root: Path, freq_hz: float, gain_db: float, attenuation_db: int) -> Path:
    freq_tag = str(int(round(freq_hz)))
    gain_tag = str(int(round(gain_db))) if float(gain_db).is_integer() else str(gain_db).replace(".", "p")
    run_dir = scan_root / f"f{freq_tag}_gain{gain_tag}_{attenuation_db}db"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def annotate_summary(summary: dict[str, Any], *, freq_hz: float, gain_db: float, attenuation_db: int) -> dict[str, Any]:
    summary["visible_txon"] = is_visible(summary)
    summary["frequency_hz_scanned"] = freq_hz
    summary["gain_db"] = gain_db
    summary["attenuation_db"] = attenuation_db
    return summary


def write_report(
    path: Path,
    *,
    run_dir: Path,
    freq_hz: float,
    gain_db: float,
    attenuation_db: int,
    summary: dict[str, Any],
) -> None:
    text = f"""# Conducted IQ Debug Report

This report documents receiver-chain debug only.

- conducted IQ bring-up
- TX-ON/TX-OFF spectrum check
- waterfall check
- receiver-chain debug
- LR1121 TX timing verification

## Configuration

- run directory: `{run_dir}`
- center frequency: `{freq_hz:.0f} Hz`
- sample rate: `4000000 sps` if unchanged from the scan command, otherwise see summary JSON
- RX gain: `{gain_db} dB`
- attenuation: `{attenuation_db} dB`
- RF path: `{rf_path_label(attenuation_db)}`

## Summary

- TX-ON minus TX-OFF: `{float(summary.get('txon_minus_noise_db', 0.0)):.3f} dB`
- peak_frequency_hz: `{float(summary.get('peak_frequency_hz', 0.0)):.3f}`
- noise_peak_frequency_hz: `{float(summary.get('noise_peak_frequency_hz', 0.0)):.3f}`
- max_abs_iq: `{float(summary.get('max_abs_iq', 0.0)):.6f}`
- clipping_warning: `{summary.get('clipping_warning')}`
- saturation_warning: `{summary.get('saturation_warning')}`
- visible_txon: `{summary.get('visible_txon')}`
- likely_artifact_warning: `{summary.get('likely_artifact_warning')}`

## Notes

- `psd_noise.png` and `psd_txon.png` provide the TX-ON/TX-OFF spectrum check.
- `waterfall_txon.png` provides the waterfall check.
- This report does not make any packet, link-layer, OTA, or live-satellite claim.
"""
    path.write_text(text, encoding="utf-8")


def write_analyzer_validation(scan_root: Path, run_rows: list[tuple[Path, dict[str, Any]]]) -> None:
    lines = [
        "# Analyzer Validation Note",
        "",
        "This note checks the `rx_samples_to_file` fallback parsing path.",
        "",
        "- Fallback capture command uses `--type float`.",
        "- The parser reads interleaved `float32` IQ pairs and converts them to `complex64`.",
        "- The analyzer loads `.npy` files as `complex64`.",
        "",
        "## Per-run checks",
        "",
    ]
    for run_dir, summary in run_rows:
        metadata = read_json(run_dir / "capture_metadata.json")
        captures = metadata.get("captures", [])
        lines.append(f"### {run_dir.name}")
        for cap in captures:
            debug = cap.get("capture_debug", {})
            lines.append(f"- out: `{Path(cap.get('out', '')).name}`")
            lines.append(f"- backend: `{cap.get('capture_backend')}`")
            lines.append(f"- selected channel: `{cap.get('channel')}`")
            lines.append(f"- selected antenna: `{cap.get('antenna')}`")
            lines.append(f"- tuned frequency: `{cap.get('freq_hz')}`")
            lines.append(f"- RX gain: `{cap.get('gain_db')}`")
            lines.append(f"- sample rate: `{cap.get('rate_sps')}`")
            if debug:
                cmd = debug.get("rx_samples_to_file_cmd")
                lines.append(f"- rx_samples_to_file command: `{json.dumps(cmd) if cmd else ''}`")
                lines.append(f"- output size bytes: `{debug.get('rx_samples_to_file_output_size_bytes')}`")
                lines.append(f"- expected samples: `{debug.get('rx_samples_to_file_expected_samples')}`")
                lines.append(f"- actual parsed samples: `{debug.get('rx_samples_to_file_actual_samples_parsed')}`")
                lines.append(f"- parser dtype: `{debug.get('rx_samples_to_file_parser_dtype')}`")
                lines.append(f"- size matches expected: `{debug.get('rx_samples_to_file_size_matches_expected')}`")
        lines.append("")
    (scan_root / "ANALYZER_VALIDATION.md").write_text("\n".join(lines), encoding="utf-8")


def write_latest_summary(scan_root: Path, run_rows: list[tuple[Path, dict[str, Any]]]) -> None:
    best_dir, best_summary = max(
        run_rows,
        key=lambda item: (
            int(bool(item[1].get("visible_txon"))),
            -int(bool(item[1].get("clipping_warning")) or bool(item[1].get("saturation_warning"))),
            float(item[1].get("txon_minus_noise_db", 0.0)),
        ),
    )
    lines = [
        "# Latest Conducted IQ Summary",
        "",
        "This summary covers conducted IQ bring-up only.",
        "",
        f"- debug scan directory: `{scan_root.name}`",
        f"- best run directory: `{best_dir.name}`",
        f"- TX-ON visible in best run: `{best_summary.get('visible_txon')}`",
        f"- TX-ON minus TX-OFF in best run: `{float(best_summary.get('txon_minus_noise_db', 0.0)):.3f} dB`",
        f"- peak_frequency_hz in best run: `{float(best_summary.get('peak_frequency_hz', 0.0)):.3f}`",
        f"- max_abs_iq in best run: `{float(best_summary.get('max_abs_iq', 0.0)):.6f}`",
        f"- clipping_warning in best run: `{best_summary.get('clipping_warning')}`",
        f"- saturation_warning in best run: `{best_summary.get('saturation_warning')}`",
        f"- likely_artifact_warning in best run: `{best_summary.get('likely_artifact_warning')}`",
        "",
        "## Frequency Runs",
        "",
    ]
    for run_dir, summary in run_rows:
        lines.extend(
            [
                f"### {run_dir.name}",
                f"- visible_txon: `{summary.get('visible_txon')}`",
                f"- TX-ON minus TX-OFF: `{float(summary.get('txon_minus_noise_db', 0.0)):.3f} dB`",
                f"- peak_frequency_hz: `{float(summary.get('peak_frequency_hz', 0.0)):.3f}`",
                f"- max_abs_iq: `{float(summary.get('max_abs_iq', 0.0)):.6f}`",
                f"- clipping_warning: `{summary.get('clipping_warning')}`",
                f"- saturation_warning: `{summary.get('saturation_warning')}`",
                f"- likely_artifact_warning: `{summary.get('likely_artifact_warning')}`",
                "",
            ]
        )
    if not any(bool(summary.get("visible_txon")) for _, summary in run_rows):
        lines.extend(
            [
                "## Diagnostic Note",
                "",
                "- The previous 60 dB and 50 dB conducted sessions had no clipping or saturation, but no visible TX-ON.",
                "- This debug scan is receiver-chain bring-up, not a validation claim.",
                "- Likely next debug targets:",
                "1. LR1121 not actually transmitting during capture",
                "2. wrong RF port",
                "3. firmware TX frequency mismatch",
                "4. TX timing missed the capture window",
                "5. rx_samples_to_file sample format / antenna / tuning issue",
                "",
            ]
        )
    LATEST_SUMMARY.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    validate_yes_mode(args)
    freqs = parse_freq_list(args.freq_list)
    stamp = session_stamp()
    scan_root = create_scan_root(stamp, args.attenuation_db)
    print_preflight(args, freqs)
    if args.yes:
        print("\nOne-shot mode enabled. Safety confirmations accepted via command-line flags.")
    else:
        input("\nPress Enter only after confirming the 50 dB conducted path and LR1121 TX readiness.\n")

    run_rows: list[tuple[Path, dict[str, Any]]] = []
    for freq in freqs:
        run_dir = create_run_dir(scan_root, freq, args.gain, args.attenuation_db)
        metadata_path = run_dir / "capture_metadata.json"
        noise_file = run_dir / f"noise_rx2a_gain{int(round(args.gain))}_{args.attenuation_db}db.npy"
        txon_file = run_dir / f"txon_rx2a_gain{int(round(args.gain))}_{args.attenuation_db}db.npy"

        print(f"\nRun directory: {run_dir}")
        if args.tx_control == "command":
            run_control_command("Setting LR1121 TX-OFF", args.tx_off_cmd or "")
        noise_cmd = build_capture_cmd(
            freq=freq,
            rate=args.rate,
            gain=args.gain,
            duration=args.duration_off,
            out=noise_file,
            metadata=metadata_path,
            antenna=args.antenna,
            channel=args.channel,
            rf_path=rf_path_label(args.attenuation_db),
        )
        run_subprocess(noise_cmd)

        if args.tx_control == "command":
            run_control_command("Setting LR1121 TX-ON", args.tx_on_cmd or "")
        else:
            countdown(
                f"Enable deterministic LR1121 TX now for {freq:.0f} Hz. Capturing TX-ON in {int(round(args.tx_on_delay))} seconds...",
                args.tx_on_delay,
            )

        txon_cmd = build_capture_cmd(
            freq=freq,
            rate=args.rate,
            gain=args.gain,
            duration=args.duration_on,
            out=txon_file,
            metadata=metadata_path,
            antenna=args.antenna,
            channel=args.channel,
            rf_path=rf_path_label(args.attenuation_db),
        )
        run_subprocess(txon_cmd)
        if args.tx_control == "command":
            run_control_command("Returning LR1121 to TX-OFF", args.tx_off_cmd or "")
        else:
            print("\nTX-ON capture complete. Disable LR1121 TX now while analysis runs.")

        analyze_cmd = build_analyze_cmd(
            noise_iq=noise_file,
            txon_iq=txon_file,
            rate=args.rate,
            freq=freq,
            attenuation_db=args.attenuation_db,
            outdir=run_dir,
            rf_path=rf_path_label(args.attenuation_db),
        )
        run_subprocess(analyze_cmd)

        summary = read_json(run_dir / "signal_detection_summary.json")
        summary = annotate_summary(summary, freq_hz=freq, gain_db=args.gain, attenuation_db=args.attenuation_db)
        with (run_dir / "signal_detection_summary.json").open("w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)
            fh.write("\n")
        write_report(
            run_dir / "EXPERIMENT_REPORT.md",
            run_dir=run_dir,
            freq_hz=freq,
            gain_db=args.gain,
            attenuation_db=args.attenuation_db,
            summary=summary,
        )
        run_rows.append((run_dir, summary))

    write_analyzer_validation(scan_root, run_rows)
    write_latest_summary(scan_root, run_rows)

    print(f"\nDebug scan complete: {scan_root}")
    print(f"Latest summary: {LATEST_SUMMARY}")


if __name__ == "__main__":
    main()
