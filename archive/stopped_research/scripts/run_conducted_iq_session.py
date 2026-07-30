#!/usr/bin/env python3
"""Supervised conducted IQ session runner for LR1121 -> USRP B210 RX2 A."""

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


DEFAULT_RATE = 1e6
DEFAULT_DURATION_OFF = 5.0
DEFAULT_DURATION_ON = 5.0
DEFAULT_GAIN = 0.0
DEFAULT_ATTENUATION_DB = 60
DEFAULT_CHANNEL = 0
DEFAULT_ANTENNA = "RX2"
DEFAULT_TX_ON_DELAY = 8.0
DEFAULT_TX_CONTROL = "manual-countdown"
VISIBLE_DELTA_DB = 6.0
CFO_PROXY_CANDIDATE_DELTA_DB = 10.0

REPO_ROOT = Path(__file__).resolve().parents[1]
CAPTURE_SCRIPT = REPO_ROOT / "scripts" / "usrp_rx2a_capture.py"
ANALYZE_SCRIPT = REPO_ROOT / "scripts" / "analyze_conducted_iq.py"
RUNS_ROOT = REPO_ROOT / "hardware_conducted_iq"
LATEST_SUMMARY = RUNS_ROOT / "latest_summary.md"


def rf_path_label(attenuation_db: int) -> str:
    if attenuation_db == 60:
        return "LR1121 RF port -> 30 dB attenuator -> 20 dB attenuator -> 10 dB attenuator -> SMA coax -> USRP B210 RX2 A"
    if attenuation_db == 50:
        return "LR1121 RF port -> 30 dB attenuator -> 20 dB attenuator -> SMA coax -> USRP B210 RX2 A"
    return f"LR1121 RF port -> fixed conducted attenuation chain ({attenuation_db} dB total) -> SMA coax -> USRP B210 RX2 A"


def attenuation_notes(attenuation_db: int) -> list[str]:
    if attenuation_db == 60:
        return [
            "- 30 dB + 20 dB + 10 dB attenuation installed.",
            "- 10 dB pad installed.",
        ]
    if attenuation_db == 50:
        return [
            "- 30 dB + 20 dB attenuation installed.",
            "- 10 dB pad removed.",
        ]
    return [f"- Fixed conducted attenuation installed: {attenuation_db} dB total."]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Supervised receive-only conducted IQ session for USRP B210 RX2 A."
    )
    parser.add_argument("--freq", type=float, default=None, help="Center frequency in Hz.")
    parser.add_argument("--rate", type=float, default=DEFAULT_RATE)
    parser.add_argument("--duration-off", type=float, default=DEFAULT_DURATION_OFF)
    parser.add_argument("--duration-on", type=float, default=DEFAULT_DURATION_ON)
    parser.add_argument("--gain", type=float, default=DEFAULT_GAIN)
    parser.add_argument("--attenuation-db", type=int, default=DEFAULT_ATTENUATION_DB)
    parser.add_argument("--channel", type=int, default=DEFAULT_CHANNEL, choices=[0])
    parser.add_argument("--antenna", default=DEFAULT_ANTENNA, choices=["RX2"])
    parser.add_argument("--yes", action="store_true", help="Run in one-shot mode with no interactive prompts.")
    parser.add_argument(
        "--confirm-board-freq",
        type=float,
        default=None,
        help="Operator-confirmed LR1121 TX center frequency in Hz.",
    )
    parser.add_argument(
        "--confirm-hardware-ready",
        action="store_true",
        help="Operator confirms the conducted hardware path is installed and ready.",
    )
    parser.add_argument(
        "--confirm-lowest-tx-power",
        action="store_true",
        help="Operator confirms LR1121 TX power is set to the lowest available setting.",
    )
    parser.add_argument(
        "--confirm-conducted-only",
        action="store_true",
        help="Operator confirms this run is conducted-only with no OTA path.",
    )
    parser.add_argument(
        "--tx-control",
        choices=["manual-countdown", "command"],
        default=DEFAULT_TX_CONTROL,
        help="How TX-OFF/TX-ON state is controlled during the session.",
    )
    parser.add_argument(
        "--tx-on-delay",
        type=float,
        default=DEFAULT_TX_ON_DELAY,
        help="Countdown before automatic TX-ON capture in manual-countdown mode.",
    )
    parser.add_argument(
        "--auto-gain-sweep",
        default=None,
        help="Comma-separated RX gain sweep, e.g. 0,10,20.",
    )
    parser.add_argument("--tx-on-cmd", default=None, help="External command that enables LR1121 TX.")
    parser.add_argument("--tx-off-cmd", default=None, help="External command that disables LR1121 TX.")
    return parser.parse_args()


def prompt_if_missing(value: float | None, prompt: str) -> float:
    if value is not None:
        return float(value)
    entered = input(prompt).strip()
    if not entered:
        raise SystemExit("Center frequency is required.")
    return float(entered)


def db_token(value: float | int) -> str:
    if float(value).is_integer():
        return str(int(round(float(value))))
    return str(value).replace(".", "p")


def session_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def create_run_dir(stamp: str, gain_db: float, attenuation_db: int) -> Path:
    run_dir = RUNS_ROOT / f"{stamp}_gain{db_token(gain_db)}_{db_token(attenuation_db)}db"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def parse_gain_sweep(args: argparse.Namespace) -> list[float]:
    if not args.auto_gain_sweep:
        return [float(args.gain)]
    gains: list[float] = []
    for raw in args.auto_gain_sweep.split(","):
        token = raw.strip()
        if not token:
            continue
        gains.append(float(token))
    if not gains:
        raise SystemExit("Auto gain sweep is empty.")
    return gains


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
    if args.freq is None:
        raise SystemExit("--yes mode requires --freq.")
    if abs(float(args.confirm_board_freq) - float(args.freq)) > 0.5:
        raise SystemExit(
            f"Confirmed board frequency {args.confirm_board_freq:.0f} Hz does not match --freq {args.freq:.0f} Hz."
        )
    if args.tx_control == "command" and (not args.tx_on_cmd or not args.tx_off_cmd):
        raise SystemExit("--tx-control command requires both --tx-on-cmd and --tx-off-cmd.")


def print_preflight(args: argparse.Namespace) -> None:
    print("\nPreflight checklist:")
    print("- LR1121 RF port, not GNSS port.")
    for line in attenuation_notes(args.attenuation_db):
        print(line)
    print("- Coax goes to USRP B210 RX2 A.")
    print(f"- USRP channel {args.channel}.")
    print(f"- UHD antenna {args.antenna}.")
    print("- USRP TX disabled.")
    print("- No antenna / no OTA.")
    print(f"- LR1121 configured TX frequency = {args.freq:.0f} Hz.")
    print("- LR1121 TX power = lowest available setting.")
    print(f"- Fixed attenuation for this session = {args.attenuation_db} dB.")


def confirm(message: str) -> None:
    input(f"\n{message}\n")


def run_subprocess(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, cwd=str(REPO_ROOT))


def run_control_command(label: str, command: str) -> None:
    print(f"\n{label}: {command}")
    subprocess.run(shlex.split(command), check=True, cwd=str(REPO_ROOT))


def countdown(message: str, delay_s: float) -> None:
    whole = max(0, int(round(delay_s)))
    print(f"\n{message}")
    if whole <= 0:
        return
    for remaining in range(whole, 0, -1):
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
    outdir: Path,
    attenuation_db: int,
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


def is_txon_visible(summary: dict[str, Any]) -> bool:
    return float(summary.get("txon_minus_noise_db", 0.0)) >= VISIBLE_DELTA_DB


def is_cfo_proxy_candidate(summary: dict[str, Any]) -> bool:
    return (
        float(summary.get("txon_minus_noise_db", 0.0)) >= CFO_PROXY_CANDIDATE_DELTA_DB
        and not bool(summary.get("clipping_warning"))
        and not bool(summary.get("saturation_warning"))
    )


def is_usable(summary: dict[str, Any]) -> bool:
    return is_txon_visible(summary) and not bool(summary.get("clipping_warning")) and not bool(
        summary.get("saturation_warning")
    )


def recommend_next_step(
    summary: dict[str, Any],
    *,
    gain_db: float,
    attenuation_db: int,
    has_next_gain: bool,
) -> str:
    clipping_warning = bool(summary.get("clipping_warning"))
    saturation_warning = bool(summary.get("saturation_warning"))
    visible = is_txon_visible(summary)
    cfo_candidate = is_cfo_proxy_candidate(summary)

    if clipping_warning:
        return (
            f"Clipping warning: keep {attenuation_db} dB attenuation, reduce USRP RX gain or LR1121 TX power, "
            "and do not lower attenuation."
        )
    if saturation_warning:
        return (
            f"Saturation warning: keep {attenuation_db} dB attenuation, do not lower attenuation, "
            "and check LR1121 TX power and the selected RF port."
        )
    if cfo_candidate:
        return (
            "TX-ON/TX-OFF spectrum evidence and waterfall evidence are usable at the current setting. "
            "This run is a CFO / hop-center proxy candidate."
        )
    if visible and has_next_gain:
        return (
            f"TX-ON is visible but still weak for a CFO / hop-center proxy candidate. "
            f"Continue to the next RX gain while keeping {attenuation_db} dB attenuation."
        )
    if visible:
        return (
            "TX-ON is visible and unclipped, but the configured gain sweep is exhausted. "
            "Use this as conducted IQ-level evidence and repeat for stability if needed."
        )
    if has_next_gain:
        return (
            f"TX-ON is too weak at RX gain {gain_db:g} dB. Continue to the next configured RX gain "
            f"while keeping {attenuation_db} dB attenuation."
        )
    if gain_db >= 20:
        if attenuation_db == 50:
            return (
                "TX-ON is still weak after RX gain 20 dB at 50 dB attenuation. Likely next debug targets: "
                "LR1121 not actually transmitting during capture; wrong RF port; firmware TX frequency mismatch; "
                "TX timing missed the capture window; or rx_samples_to_file sample format / antenna / tuning issue."
            )
        return (
            f"TX-ON is still weak after RX gain {gain_db:g} dB. Manual next step: consider testing 50 dB attenuation later "
            f"by removing the 10 dB pad. Do not change attenuation automatically."
        )
    return (
        f"TX-ON is weak at RX gain {gain_db:g} dB and no further configured gains remain. "
        "Extend the gain sweep before considering any attenuation change."
    )


def write_report(
    path: Path,
    *,
    run_dir: Path,
    args: argparse.Namespace,
    gain_db: float,
    noise_file: Path,
    txon_file: Path,
    summary: dict[str, Any],
) -> None:
    report = f"""# Conducted IQ Experiment Report

This report documents a conducted IQ-level capture only.

- Not packet decoding
- No link-layer outcome claim
- No end-to-end link claim
- No live-satellite claim
- Not OTA

## Hardware path

- board: `NUCLEO-L476RG + LR1121`
- RF path: `{rf_path_label(args.attenuation_db)}`

## Session settings

- Run directory: `{run_dir}`
- Attenuation: `{args.attenuation_db} dB`
- USRP channel: `{args.channel}`
- UHD antenna: `{args.antenna}`
- RX gain: `{gain_db} dB`
- Sample rate: `{args.rate} sps`
- Center frequency: `{args.freq} Hz`
- TX control mode: `{args.tx_control}`

## Capture files

- TX-OFF: `{noise_file.name}`
- TX-ON: `{txon_file.name}`
- Metadata: `capture_metadata.json`

## TX-ON/TX-OFF spectrum evidence

- noise floor: `{summary['noise_floor_db']:.3f} dB`
- TX-ON peak: `{summary['txon_peak_db']:.3f} dB`
- TX-ON minus TX-OFF: `{summary['txon_minus_noise_db']:.3f} dB`
- peak frequency: `{summary['peak_frequency_hz']:.3f} Hz`
- peak offset: `{summary['peak_offset_hz']:.3f} Hz`
- max_abs_iq: `{summary['max_abs_iq']:.6f}`
- clipping_warning: `{summary['clipping_warning']}`
- saturation_warning: `{summary['saturation_warning']}`
- TX-ON visible: `{summary['txon_visible']}`
- usable for conducted IQ-level evidence: `{summary['usable_for_conducted_iq_evidence']}`
- CFO / hop-center proxy candidate: `{summary['cfo_hop_center_proxy_candidate']}`
- recommended next step: `{summary['recommended_next_step']}`

## Notes

- `psd_noise.png` and `psd_txon.png` provide TX-ON/TX-OFF spectrum evidence.
- `waterfall_txon.png` provides waterfall evidence.
- This run is limited to conducted IQ-level capture and may support a future CFO / hop-center proxy candidate assessment.
"""
    path.write_text(report, encoding="utf-8")


def write_latest_summary(session_runs: list[tuple[Path, dict[str, Any]]]) -> None:
    if not session_runs:
        return

    best_dir, best_summary = max(
        session_runs,
        key=lambda item: (
            int(bool(item[1].get("usable_for_conducted_iq_evidence"))),
            int(bool(item[1].get("cfo_hop_center_proxy_candidate"))),
            int(bool(item[1].get("txon_visible"))),
            -int(bool(item[1].get("clipping_warning")) or bool(item[1].get("saturation_warning"))),
            float(item[1].get("txon_minus_noise_db", 0.0)),
        ),
    )

    lines = [
        "# Latest Conducted IQ Summary",
        "",
        "This summary covers conducted IQ-level capture only.",
        "",
        f"- best run directory: `{best_dir.name}`",
        f"- TX-ON visible in best run: `{best_summary.get('txon_visible')}`",
        f"- TX-ON minus TX-OFF in best run: `{float(best_summary.get('txon_minus_noise_db', 0.0)):.3f} dB`",
        f"- peak frequency in best run: `{float(best_summary.get('peak_frequency_hz', 0.0)):.3f} Hz`",
        f"- max_abs_iq in best run: `{float(best_summary.get('max_abs_iq', 0.0)):.6f}`",
        f"- clipping_warning in best run: `{best_summary.get('clipping_warning')}`",
        f"- saturation_warning in best run: `{best_summary.get('saturation_warning')}`",
        f"- usable for conducted IQ-level evidence: `{best_summary.get('usable_for_conducted_iq_evidence')}`",
        f"- recommended next step: {best_summary.get('recommended_next_step')}",
        "",
        "## Gain Runs Attempted",
        "",
    ]

    for run_dir, summary in session_runs:
        lines.extend(
            [
                f"### {run_dir.name}",
                f"- TX-ON visible: `{summary.get('txon_visible')}`",
                f"- TX-ON minus TX-OFF: `{float(summary.get('txon_minus_noise_db', 0.0)):.3f} dB`",
                f"- peak frequency: `{float(summary.get('peak_frequency_hz', 0.0)):.3f} Hz`",
                f"- max_abs_iq: `{float(summary.get('max_abs_iq', 0.0)):.6f}`",
                f"- clipping_warning: `{summary.get('clipping_warning')}`",
                f"- saturation_warning: `{summary.get('saturation_warning')}`",
                f"- usable for conducted IQ-level evidence: `{summary.get('usable_for_conducted_iq_evidence')}`",
                f"- CFO / hop-center proxy candidate: `{summary.get('cfo_hop_center_proxy_candidate')}`",
                f"- recommended next step: {summary.get('recommended_next_step')}",
                "",
            ]
        )

    attenuation_db = int(session_runs[0][1].get("attenuation_db", -1))
    if attenuation_db == 50 and not any(bool(summary.get("txon_visible")) for _, summary in session_runs):
        lines.extend(
            [
                "## Diagnostic Note",
                "",
                "- The previous 60 dB session had no clipping or saturation, but no visible TX-ON.",
                "- This 50 dB test is a controlled next step, not a validation claim.",
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


def apply_tx_off_control(args: argparse.Namespace, *, first_gain: bool) -> None:
    if args.tx_control == "command":
        assert args.tx_off_cmd is not None
        run_control_command("Setting LR1121 TX-OFF", args.tx_off_cmd)
        return
    if first_gain:
        return
    countdown(
        f"Disable LR1121 TX now. Capturing TX-OFF in {int(round(args.tx_on_delay))} seconds...",
        args.tx_on_delay,
    )


def apply_tx_on_control(args: argparse.Namespace) -> None:
    if args.tx_control == "command":
        assert args.tx_on_cmd is not None
        run_control_command("Setting LR1121 TX-ON", args.tx_on_cmd)
        return
    countdown(
        f"Enable LR1121 TX now. Capturing TX-ON in {int(round(args.tx_on_delay))} seconds...",
        args.tx_on_delay,
    )


def finalize_tx_after_capture(args: argparse.Namespace) -> None:
    if args.tx_control == "command":
        assert args.tx_off_cmd is not None
        run_control_command("Returning LR1121 to TX-OFF", args.tx_off_cmd)
        return
    print("\nTX-ON capture complete. Disable LR1121 TX now while analysis runs.")


def annotate_summary(
    summary: dict[str, Any],
    *,
    gain_db: float,
    attenuation_db: int,
    tx_control: str,
    has_next_gain: bool,
) -> dict[str, Any]:
    summary["gain_db"] = gain_db
    summary["attenuation_db"] = attenuation_db
    summary["tx_control_mode"] = tx_control
    summary["txon_visible"] = is_txon_visible(summary)
    summary["usable_for_conducted_iq_evidence"] = is_usable(summary)
    summary["cfo_hop_center_proxy_candidate"] = is_cfo_proxy_candidate(summary)
    summary["recommended_next_step"] = recommend_next_step(
        summary,
        gain_db=gain_db,
        attenuation_db=attenuation_db,
        has_next_gain=has_next_gain,
    )
    summary["rf_path"] = rf_path_label(attenuation_db)
    return summary


def run_gain_capture(
    args: argparse.Namespace,
    *,
    stamp: str,
    gain_db: float,
    first_gain: bool,
    has_next_gain: bool,
) -> tuple[Path, dict[str, Any]]:
    run_dir = create_run_dir(stamp, gain_db, args.attenuation_db)
    metadata_path = run_dir / "capture_metadata.json"
    gain_tag = db_token(gain_db)
    attn_tag = db_token(args.attenuation_db)
    noise_file = run_dir / f"noise_rx2a_gain{gain_tag}_{attn_tag}db.npy"
    txon_file = run_dir / f"txon_rx2a_gain{gain_tag}_{attn_tag}db.npy"

    print(f"\nRun directory: {run_dir}")

    apply_tx_off_control(args, first_gain=first_gain)
    noise_cmd = build_capture_cmd(
        freq=args.freq,
        rate=args.rate,
        gain=gain_db,
        duration=args.duration_off,
        out=noise_file,
        metadata=metadata_path,
        antenna=args.antenna,
        channel=args.channel,
        rf_path=rf_path_label(args.attenuation_db),
    )
    run_subprocess(noise_cmd)

    apply_tx_on_control(args)
    txon_cmd = build_capture_cmd(
        freq=args.freq,
        rate=args.rate,
        gain=gain_db,
        duration=args.duration_on,
        out=txon_file,
        metadata=metadata_path,
        antenna=args.antenna,
        channel=args.channel,
        rf_path=rf_path_label(args.attenuation_db),
    )
    run_subprocess(txon_cmd)
    finalize_tx_after_capture(args)

    analyze_cmd = build_analyze_cmd(
        noise_iq=noise_file,
        txon_iq=txon_file,
        rate=args.rate,
        freq=args.freq,
        outdir=run_dir,
        attenuation_db=args.attenuation_db,
        rf_path=rf_path_label(args.attenuation_db),
    )
    run_subprocess(analyze_cmd)

    summary_path = run_dir / "signal_detection_summary.json"
    summary = read_json(summary_path)
    summary = annotate_summary(
        summary,
        gain_db=gain_db,
        attenuation_db=args.attenuation_db,
        tx_control=args.tx_control,
        has_next_gain=has_next_gain,
    )
    with summary_path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")

    write_report(
        run_dir / "EXPERIMENT_REPORT.md",
        run_dir=run_dir,
        args=args,
        gain_db=gain_db,
        noise_file=noise_file,
        txon_file=txon_file,
        summary=summary,
    )
    return run_dir, summary


def should_stop(summary: dict[str, Any]) -> bool:
    if bool(summary.get("clipping_warning")):
        return True
    if bool(summary.get("saturation_warning")):
        return True
    if bool(summary.get("cfo_hop_center_proxy_candidate")):
        return True
    return False


def main() -> None:
    args = parse_args()
    validate_yes_mode(args)
    args.freq = prompt_if_missing(None if args.yes else args.freq, "Enter center frequency in Hz: ") if args.freq is None else float(args.freq)

    gains = parse_gain_sweep(args)
    stamp = session_stamp()

    print_preflight(args)
    if not args.yes:
        confirm(
            "Press Enter only after confirming LR1121 TX is OFF, the firmware/config TX frequency "
            f"matches {args.freq:.0f} Hz, and {args.attenuation_db} dB attenuation is installed."
        )
    else:
        print("\nOne-shot mode enabled. Safety confirmations accepted via command-line flags.")

    session_runs: list[tuple[Path, dict[str, Any]]] = []
    stop_reason = "Configured gain sweep completed."

    for index, gain_db in enumerate(gains):
        has_next_gain = index < len(gains) - 1
        run_dir, summary = run_gain_capture(
            args,
            stamp=stamp,
            gain_db=gain_db,
            first_gain=index == 0,
            has_next_gain=has_next_gain,
        )
        session_runs.append((run_dir, summary))
        write_latest_summary(session_runs)

        if bool(summary.get("clipping_warning")):
            stop_reason = "Stopping gain sweep due to clipping warning."
            break
        if bool(summary.get("saturation_warning")):
            stop_reason = "Stopping gain sweep due to saturation warning."
            break
        if bool(summary.get("cfo_hop_center_proxy_candidate")):
            stop_reason = "Stopping gain sweep after a usable CFO / hop-center proxy candidate was captured."
            break
        if not has_next_gain:
            stop_reason = "Configured gain sweep completed without triggering an early stop condition."
            break
        print(
            f"\nCurrent result at RX gain {gain_db:g} dB is not yet strong enough. "
            f"Continuing to RX gain {gains[index + 1]:g} dB with the same {args.attenuation_db} dB attenuation."
        )

    write_latest_summary(session_runs)

    print(f"\nSession complete. {stop_reason}")
    if session_runs:
        best_dir, best_summary = max(
            session_runs,
            key=lambda item: (
                int(bool(item[1].get("usable_for_conducted_iq_evidence"))),
                int(bool(item[1].get("cfo_hop_center_proxy_candidate"))),
                int(bool(item[1].get("txon_visible"))),
                float(item[1].get("txon_minus_noise_db", 0.0)),
            ),
        )
        print(json.dumps(best_summary, indent=2))
        print(f"\nBest run directory: {best_dir}")
        print(f"Latest summary: {LATEST_SUMMARY}")


if __name__ == "__main__":
    main()
