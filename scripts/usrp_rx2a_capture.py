#!/usr/bin/env python3
"""Receive-only conducted IQ capture for LR1121 -> USRP B210 RX2 A / channel 0.

This script is intentionally constrained for the conducted LR1121 capture:
- RX only
- channel 0 only
- antenna RX2 only
- no TX configuration
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_RATE = 1e6
DEFAULT_GAIN = 0.0
DEFAULT_DURATION = 5.0
DEFAULT_ANTENNA = "RX2"
DEFAULT_CHANNEL = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Receive-only IQ capture on USRP B210 RX2 A / UHD channel 0."
    )
    parser.add_argument("--freq", type=float, required=True, help="Center frequency in Hz.")
    parser.add_argument(
        "--rate",
        type=float,
        default=DEFAULT_RATE,
        help=f"Sample rate in samples/s. Default: {DEFAULT_RATE:g}.",
    )
    parser.add_argument(
        "--gain",
        type=float,
        default=DEFAULT_GAIN,
        help=f"RX gain in dB. Default: {DEFAULT_GAIN:g}.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=DEFAULT_DURATION,
        help=f"Capture duration in seconds. Default: {DEFAULT_DURATION:g}.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output IQ path. Use .npy for NumPy or .cfile/.fc32 for raw complex64.",
    )
    parser.add_argument(
        "--metadata",
        type=Path,
        required=True,
        help="Metadata JSON path. Reused path is merged into a single manifest.",
    )
    parser.add_argument(
        "--antenna",
        default=DEFAULT_ANTENNA,
        choices=[DEFAULT_ANTENNA],
        help="Receive antenna. Fixed to RX2 for this validation.",
    )
    parser.add_argument(
        "--channel",
        type=int,
        default=DEFAULT_CHANNEL,
        choices=[DEFAULT_CHANNEL],
        help="UHD RX channel. Fixed to channel 0 for this validation.",
    )
    parser.add_argument(
        "--rf-path",
        default="LR1121 RF port -> 30 dB -> 20 dB -> 10 dB -> SMA coax -> USRP B210 RX2 A",
        help="User-facing RF path label stored in metadata.",
    )
    return parser.parse_args()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_iq(path: Path, iq: np.ndarray) -> None:
    ensure_parent(path)
    if path.suffix.lower() == ".npy":
        np.save(path, iq.astype(np.complex64))
        return
    if path.suffix.lower() in {".cfile", ".fc32"}:
        iq.astype(np.complex64).tofile(path)
        return
    raise ValueError("Unsupported IQ output format. Use .npy, .cfile, or .fc32.")


def expected_iq_bytes(num_samples: int) -> int:
    return int(num_samples) * 2 * np.dtype(np.float32).itemsize


def load_metadata(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "validation_scope": "conducted IQ-level capture only",
            "board": "NUCLEO-L476RG + LR1121",
            "receive_only": True,
            "captures": [],
        }
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def update_metadata(path: Path, capture_info: dict[str, Any]) -> None:
    ensure_parent(path)
    blob = load_metadata(path)
    captures = blob.setdefault("captures", [])
    captures = [item for item in captures if item.get("out") != capture_info["out"]]
    captures.append(capture_info)
    blob["captures"] = captures
    blob["last_updated_unix"] = time.time()
    blob["receive_only"] = True
    blob["board"] = "NUCLEO-L476RG + LR1121"
    blob["rf_path"] = str(capture_info.get("rf_path", ""))
    blob["prohibitions"] = [
        "No USRP TX",
        "No TX/RX shared port",
        "No channel 1",
        "No packet decoding claim",
        "No link-layer outcome claim",
        "No live-satellite claim",
        "No OTA claim",
    ]
    with path.open("w", encoding="utf-8") as fh:
        json.dump(blob, fh, indent=2)
        fh.write("\n")


def locate_rx_samples_to_file() -> Path | None:
    direct = shutil.which("rx_samples_to_file")
    if direct:
        return Path(direct)

    candidates: list[Path] = []
    for root in (Path("/opt/homebrew/Cellar/uhd"), Path("/usr/local/Cellar/uhd")):
        if root.exists():
            candidates.extend(sorted(root.glob("*/lib/uhd/examples/rx_samples_to_file")))
    if candidates:
        return candidates[-1]
    return None


def capture_iq_with_example_binary(args: argparse.Namespace) -> tuple[np.ndarray, dict[str, Any]]:
    rx_binary = locate_rx_samples_to_file()
    if rx_binary is None:
        raise SystemExit(
            "pyuhd import failed and no rx_samples_to_file fallback binary was found. "
            "Install UHD Python bindings or ensure the UHD example binary is installed."
        )

    raw_path = args.out.with_suffix(args.out.suffix + ".tmp.fc32")
    ensure_parent(raw_path)
    cmd = [
        str(rx_binary),
        "--freq",
        str(args.freq),
        "--rate",
        str(args.rate),
        "--gain",
        str(args.gain),
        "--duration",
        str(args.duration),
        "--ant",
        args.antenna,
        "--subdev",
        "A:A",
        "--channels",
        str(args.channel),
        "--type",
        "float",
        "--file",
        str(raw_path),
    ]

    try:
        completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
        expected_samples = max(1, int(round(args.duration * args.rate)))
        file_size_bytes = raw_path.stat().st_size
        floats = np.fromfile(raw_path, dtype=np.float32)
        if len(floats) % 2 != 0:
            raise RuntimeError("Fallback capture file has an odd number of float32 values.")
        iq = floats.reshape(-1, 2)
        parsed = (iq[:, 0] + 1j * iq[:, 1]).astype(np.complex64, copy=False)
        debug_info = {
            "rx_samples_to_file_cmd": cmd,
            "rx_samples_to_file_stdout": completed.stdout,
            "rx_samples_to_file_stderr": completed.stderr,
            "rx_samples_to_file_output_path": str(raw_path),
            "rx_samples_to_file_output_size_bytes": int(file_size_bytes),
            "rx_samples_to_file_expected_samples": int(expected_samples),
            "rx_samples_to_file_expected_bytes": expected_iq_bytes(expected_samples),
            "rx_samples_to_file_actual_samples_parsed": int(len(parsed)),
            "rx_samples_to_file_parser_float32_count": int(len(floats)),
            "rx_samples_to_file_parser_dtype": "float32_interleaved_iq_to_complex64",
            "rx_samples_to_file_sample_format": "float",
            "rx_samples_to_file_channels": str(args.channel),
            "rx_samples_to_file_antenna": args.antenna,
            "rx_samples_to_file_freq_hz": float(args.freq),
            "rx_samples_to_file_gain_db": float(args.gain),
            "rx_samples_to_file_rate_sps": float(args.rate),
            "rx_samples_to_file_duration_s": float(args.duration),
            "rx_samples_to_file_size_matches_expected": int(file_size_bytes) == expected_iq_bytes(expected_samples),
        }
        return parsed, debug_info
    finally:
        if raw_path.exists():
            raw_path.unlink()


def capture_iq(args: argparse.Namespace) -> tuple[np.ndarray, str, dict[str, Any]]:
    try:
        import uhd  # type: ignore
    except ImportError as exc:
        print(
            "pyuhd/uhd Python bindings unavailable; falling back to UHD rx_samples_to_file example.",
            flush=True,
        )
        iq, debug_info = capture_iq_with_example_binary(args)
        return iq, "uhd_rx_samples_to_file_fallback", debug_info

    usrp = uhd.usrp.MultiUSRP()
    channel = args.channel
    antenna = args.antenna

    usrp.set_rx_antenna(antenna, channel)
    usrp.set_rx_rate(args.rate, channel)
    usrp.set_rx_gain(args.gain, channel)
    usrp.set_rx_freq(uhd.libpyuhd.types.tune_request(args.freq), channel)

    stream_args = uhd.usrp.StreamArgs("fc32", "sc16")
    stream_args.channels = [channel]
    rx_streamer = usrp.get_rx_stream(stream_args)

    num_samps = max(1, int(round(args.duration * args.rate)))
    recv_buffer = np.zeros((1, 4096), dtype=np.complex64)
    out = np.empty(num_samps, dtype=np.complex64)
    metadata = uhd.types.RXMetadata()

    cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
    cmd.stream_now = True
    rx_streamer.issue_stream_cmd(cmd)

    filled = 0
    try:
        while filled < num_samps:
            nsamps = rx_streamer.recv(recv_buffer, metadata, timeout=3.0)
            if metadata.error_code != uhd.types.RXMetadataErrorCode.none:
                raise RuntimeError(f"UHD RX error: {metadata.strerror()}")
            if nsamps <= 0:
                continue
            take = min(nsamps, num_samps - filled)
            out[filled : filled + take] = recv_buffer[0, :take]
            filled += take
    finally:
        stop_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont)
        rx_streamer.issue_stream_cmd(stop_cmd)

    debug_info = {
        "rx_streamer_cpu_format": "fc32",
        "rx_streamer_otw_format": "sc16",
        "rx_streamer_expected_samples": int(num_samps),
        "rx_streamer_actual_samples": int(filled),
        "rx_streamer_capture_backend": "pyuhd_multiusrp",
    }
    return out[:filled].astype(np.complex64, copy=False), "pyuhd_multiusrp", debug_info


def main() -> None:
    args = parse_args()
    started = time.time()
    iq, capture_backend, debug_info = capture_iq(args)
    ended = time.time()

    save_iq(args.out, iq)

    capture_info = {
        "out": str(args.out),
        "freq_hz": args.freq,
        "rate_sps": args.rate,
        "gain_db": args.gain,
        "duration_requested_s": args.duration,
        "duration_captured_s": float(len(iq) / args.rate),
        "num_samples": int(len(iq)),
        "dtype": "complex64",
        "channel": args.channel,
        "antenna": args.antenna,
        "usrp_port_mapping": "USRP B210 RX2 A -> UHD channel 0 -> antenna RX2",
        "rf_path": args.rf_path,
        "receive_only": True,
        "tx_configured": False,
        "capture_backend": capture_backend,
        "capture_debug": debug_info,
        "started_unix": started,
        "ended_unix": ended,
        "max_abs_iq": float(np.max(np.abs(iq))) if len(iq) else 0.0,
    }
    update_metadata(args.metadata, capture_info)

    print(json.dumps(capture_info, indent=2))


if __name__ == "__main__":
    main()
