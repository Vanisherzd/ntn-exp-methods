#!/usr/bin/env python3
"""Analyze conducted IQ captures for receive-only LR1121 / USRP capture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze conducted IQ captures.")
    parser.add_argument("--noise-iq", type=Path, required=True)
    parser.add_argument("--txon-iq", type=Path, required=True)
    parser.add_argument("--rate", type=float, required=True)
    parser.add_argument("--freq", type=float, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--attenuation-db", type=int, default=60)
    parser.add_argument(
        "--rf-path",
        default="LR1121 RF port -> 30 dB -> 20 dB -> 10 dB -> SMA coax -> USRP B210 RX2 A",
        help="User-facing RF path label stored in the summary JSON.",
    )
    return parser.parse_args()


def load_iq(path: Path) -> np.ndarray:
    if path.suffix.lower() == ".npy":
        arr = np.load(path)
        return np.asarray(arr, dtype=np.complex64)
    if path.suffix.lower() in {".cfile", ".fc32"}:
        return np.fromfile(path, dtype=np.complex64)
    raise ValueError(f"Unsupported IQ format: {path}")


def make_frames(iq: np.ndarray, nperseg: int, noverlap: int) -> np.ndarray:
    step = max(1, nperseg - noverlap)
    if len(iq) < nperseg:
        padded = np.zeros(nperseg, dtype=np.complex64)
        padded[: len(iq)] = iq
        return padded[None, :]
    starts = np.arange(0, len(iq) - nperseg + 1, step)
    return np.stack([iq[s : s + nperseg] for s in starts], axis=0)


def psd_db(iq: np.ndarray, rate: float) -> tuple[np.ndarray, np.ndarray]:
    nperseg = min(8192, max(256, len(iq)))
    noverlap = nperseg // 2
    frames = make_frames(iq, nperseg=nperseg, noverlap=noverlap)
    window = np.hanning(nperseg).astype(np.float32)
    spec = np.fft.fft(frames * window[None, :], axis=1)
    pxx = np.mean(np.abs(spec) ** 2, axis=0) / np.sum(window**2)
    freqs = np.fft.fftfreq(nperseg, d=1.0 / rate)
    freqs = np.fft.fftshift(freqs)
    pxx = np.fft.fftshift(pxx)
    return freqs, 10.0 * np.log10(np.maximum(pxx, 1e-20))


def make_psd_plot(freqs: np.ndarray, db: np.ndarray, center_hz: float, title: str, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    ax.plot((freqs + center_hz) / 1e6, db, lw=1.8, color="#1f4e79")
    ax.set_title(title)
    ax.set_xlabel("Frequency [MHz]")
    ax.set_ylabel("PSD [dB]")
    ax.grid(True, ls=":", alpha=0.35)
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)


def make_maxhold_plot(
    noise_freqs: np.ndarray,
    noise_db: np.ndarray,
    tx_freqs: np.ndarray,
    tx_db: np.ndarray,
    center_hz: float,
    out: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    ax.plot((noise_freqs + center_hz) / 1e6, noise_db, lw=1.6, color="#666666", label="TX-OFF")
    ax.plot((tx_freqs + center_hz) / 1e6, tx_db, lw=1.8, color="#b23a3a", label="TX-ON")
    ax.set_title("TX-ON vs TX-OFF max-hold comparison")
    ax.set_xlabel("Frequency [MHz]")
    ax.set_ylabel("PSD [dB]")
    ax.grid(True, ls=":", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)


def make_waterfall(iq: np.ndarray, rate: float, center_hz: float, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    nperseg = min(2048, max(256, len(iq) // 8 if len(iq) >= 8 else len(iq)))
    noverlap = nperseg // 2
    frames = make_frames(iq, nperseg=nperseg, noverlap=noverlap)
    window = np.hanning(nperseg).astype(np.float32)
    spec = np.fft.fft(frames * window[None, :], axis=1)
    sxx = (np.abs(spec) ** 2 / np.sum(window**2)).T
    freqs = np.fft.fftfreq(nperseg, d=1.0 / rate)
    times = np.arange(frames.shape[0]) * ((nperseg - noverlap) / rate)
    freqs = np.fft.fftshift(freqs)
    sxx = np.fft.fftshift(sxx, axes=0)
    mesh = ax.pcolormesh(
        times,
        (freqs + center_hz) / 1e6,
        10.0 * np.log10(np.maximum(sxx, 1e-20)),
        shading="auto",
        cmap="viridis",
    )
    fig.colorbar(mesh, ax=ax, label="PSD [dB]")
    ax.set_title("TX-ON waterfall / spectrogram")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Frequency [MHz]")
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)


def summarize(
    noise_freqs: np.ndarray,
    noise_db: np.ndarray,
    tx_freqs: np.ndarray,
    tx_db: np.ndarray,
    tx_iq: np.ndarray,
    center_hz: float,
    attenuation_db: int,
) -> dict[str, object]:
    noise_floor_db = float(np.median(noise_db))
    txon_peak_db = float(np.max(tx_db))
    noise_peak_db = float(np.max(noise_db))
    delta_db = tx_db - noise_db
    txon_minus_noise_db = float(np.max(delta_db))
    max_abs_iq = float(np.max(np.abs(tx_iq))) if len(tx_iq) else 0.0
    peak_idx = int(np.argmax(tx_db))
    peak_frequency_hz = float(center_hz + tx_freqs[peak_idx])
    peak_offset_hz = float(tx_freqs[peak_idx])
    noise_peak_idx = int(np.argmax(noise_db))
    noise_peak_frequency_hz = float(center_hz + noise_freqs[noise_peak_idx])
    noise_peak_offset_hz = float(noise_freqs[noise_peak_idx])

    clipping_mag = max_abs_iq > 0.7
    broad_uniform = float(np.mean(delta_db > max(3.0, txon_minus_noise_db - 6.0))) > 0.65
    flat_raise = (
        float(np.percentile(delta_db, 95) - np.percentile(delta_db, 5)) < 4.0
        and float(np.median(delta_db)) > 6.0
    )
    saturation_warning = bool(broad_uniform or flat_raise)
    clipping_warning = bool(clipping_mag)
    likely_artifact_warning = bool(
        abs(peak_offset_hz - noise_peak_offset_hz) <= 1_000.0 and txon_minus_noise_db < 3.0
    )

    if clipping_warning or saturation_warning:
        recommended_next_step = (
            f"Possible clipping/saturation: keep {attenuation_db} dB attenuation, reduce USRP RX gain, "
            "reduce LR1121 TX power, and do not lower attenuation."
        )
    elif txon_minus_noise_db < 6.0:
        recommended_next_step = (
            f"TX-ON is weak: keep {attenuation_db} dB attenuation and continue receiver-chain debug."
        )
    else:
        recommended_next_step = (
            "Conducted IQ difference is visible and unclipped at current settings. "
            "Repeat for stability before any attenuation change."
        )

    return {
        "noise_floor_db": noise_floor_db,
        "noise_peak_db": noise_peak_db,
        "txon_peak_db": txon_peak_db,
        "txon_minus_noise_db": txon_minus_noise_db,
        "peak_frequency_hz": peak_frequency_hz,
        "peak_offset_hz": peak_offset_hz,
        "noise_peak_frequency_hz": noise_peak_frequency_hz,
        "noise_peak_offset_hz": noise_peak_offset_hz,
        "max_abs_iq": max_abs_iq,
        "clipping_warning": clipping_warning,
        "saturation_warning": saturation_warning,
        "broad_uniform_warning": broad_uniform,
        "flat_raise_warning": flat_raise,
        "likely_artifact_warning": likely_artifact_warning,
        "recommended_next_step": recommended_next_step,
    }


def main() -> None:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    noise_iq = load_iq(args.noise_iq)
    txon_iq = load_iq(args.txon_iq)

    noise_freqs, noise_db = psd_db(noise_iq, args.rate)
    tx_freqs, tx_db = psd_db(txon_iq, args.rate)

    make_psd_plot(noise_freqs, noise_db, args.freq, "TX-OFF PSD", args.outdir / "psd_noise.png")
    make_psd_plot(tx_freqs, tx_db, args.freq, "TX-ON PSD", args.outdir / "psd_txon.png")
    make_maxhold_plot(
        noise_freqs,
        noise_db,
        tx_freqs,
        tx_db,
        args.freq,
        args.outdir / "maxhold_txon_vs_noise.png",
    )
    make_waterfall(txon_iq, args.rate, args.freq, args.outdir / "waterfall_txon.png")

    summary = summarize(
        noise_freqs,
        noise_db,
        tx_freqs,
        tx_db,
        txon_iq,
        args.freq,
        args.attenuation_db,
    )
    summary.update(
        {
            "rate_sps": args.rate,
            "freq_hz": args.freq,
            "attenuation_db": args.attenuation_db,
            "noise_iq": str(args.noise_iq),
            "txon_iq": str(args.txon_iq),
            "validation_scope": "conducted IQ-level capture only",
            "board": "NUCLEO-L476RG + LR1121",
            "rf_path": args.rf_path,
            "non_claims": [
                "Not packet decoding",
                "No link-layer outcome claim",
                "No live-satellite claim",
                "Not OTA",
            ],
        }
    )
    with (args.outdir / "signal_detection_summary.json").open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
