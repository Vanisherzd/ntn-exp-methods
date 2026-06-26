#!/usr/bin/env python3
"""Artifact-masked conducted-IQ analysis.

Separates a DC/LO center-spike artifact (present in the TX-OFF capture) from the
LR1121 TX emission, and reports the TX-ON vs TX-OFF difference after masking.

Conducted IQ-level evidence ONLY. This does not constitute packet decoding,
PER/PDR/CRC, gateway ACK, OTA, or live-satellite / RF-link validation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

CLIP_THRESH = 0.7  # matches scripts/analyze_conducted_iq.py
SAT_THRESH = 0.9
VISIBLE_DELTA_DB = 6.0


def load_iq(path: Path) -> np.ndarray:
    arr = np.load(path)
    return arr.astype(np.complex64)


def psd_dbfs(iq: np.ndarray, rate: float) -> tuple[np.ndarray, np.ndarray]:
    nperseg = min(8192, max(256, len(iq)))
    noverlap = nperseg // 2
    step = max(1, nperseg - noverlap)
    starts = np.arange(0, len(iq) - nperseg + 1, step)
    if len(starts) == 0:
        starts = np.array([0])
        iq = np.pad(iq, (0, nperseg - len(iq)))
    window = np.hanning(nperseg).astype(np.float32)
    acc = np.zeros(nperseg, dtype=np.float64)
    for s in starts:
        seg = iq[s : s + nperseg] * window
        acc += np.abs(np.fft.fft(seg)) ** 2
    pxx = acc / (len(starts) * np.sum(window**2))
    freqs = np.fft.fftshift(np.fft.fftfreq(nperseg, d=1.0 / rate))
    pxx = np.fft.fftshift(pxx)
    db = 10.0 * np.log10(pxx + 1e-20)
    return freqs, db


def build_mask(freqs: np.ndarray, mask_width_hz: float, extra_offsets: list[float]) -> np.ndarray:
    """True where bin is KEPT (not artifact)."""
    keep = np.abs(freqs) > mask_width_hz
    for off in extra_offsets:
        keep &= np.abs(freqs - off) > mask_width_hz
    return keep


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--txoff-iq", required=True, type=Path)
    p.add_argument("--txon-iq", required=True, type=Path)
    p.add_argument("--rate", required=True, type=float)
    p.add_argument("--freq", required=True, type=float)
    p.add_argument("--outdir", required=True, type=Path)
    p.add_argument("--artifact-mask-width-hz", type=float, default=5000.0)
    p.add_argument("--known-artifact-bins", default="", help="comma list of Hz offsets to also mask")
    args = p.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    extra = [float(x) for x in args.known_artifact_bins.split(",") if x.strip()]

    txoff = load_iq(args.txoff_iq)
    txon = load_iq(args.txon_iq)
    max_abs_iq = float(np.max(np.abs(txon))) if len(txon) else 0.0
    clipping = max_abs_iq > CLIP_THRESH
    saturation = max_abs_iq > SAT_THRESH

    foff, off_db = psd_dbfs(txoff, args.rate)
    fon, on_db = psd_dbfs(txon, args.rate)
    # same nperseg -> same freq axis
    freqs = fon

    # TX-OFF artifact peak within mask window around center
    near = np.abs(freqs) <= args.artifact_mask_width_hz
    artifact_idx = np.argmax(np.where(near, off_db, -np.inf))
    txoff_artifact_peak_hz = float(args.freq + freqs[artifact_idx])

    keep = build_mask(freqs, args.artifact_mask_width_hz, extra)

    excess = on_db - off_db
    masked_excess = np.where(keep, excess, -np.inf)
    peak_idx = int(np.argmax(masked_excess))
    peak_offset = float(freqs[peak_idx])
    peak_freq = float(args.freq + peak_offset)
    txon_minus_txoff_db = float(excess[peak_idx])

    visible = bool(txon_minus_txoff_db >= VISIBLE_DELTA_DB and not clipping and not saturation)

    # ---- plot 1: artifact-masked max-hold TX-ON vs TX-OFF ----
    fmhz = (args.freq + freqs) / 1e6
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(fmhz, on_db, label="TX-ON", color="C3", lw=1.2)
    ax.plot(fmhz, off_db, label="TX-OFF", color="C0", lw=1.0, alpha=0.8)
    lo = (args.freq - args.artifact_mask_width_hz) / 1e6
    hi = (args.freq + args.artifact_mask_width_hz) / 1e6
    ax.axvspan(lo, hi, color="grey", alpha=0.3, label="masked DC/LO artifact (±%.0f kHz)" % (args.artifact_mask_width_hz / 1e3))
    ax.axvline(peak_freq / 1e6, color="k", ls="--", lw=1, label="masked peak %.4f MHz" % (peak_freq / 1e6))
    ax.set_xlabel("Frequency [MHz]", fontsize=13)
    ax.set_ylabel("Power [dBFS]", fontsize=13)
    ax.set_title("Conducted IQ-level: artifact-masked TX-ON vs TX-OFF (50 dB, RX2 A)", fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=11)
    fig.tight_layout()
    fig.savefig(args.outdir / "artifact_masked_maxhold_txon_vs_noise.png", dpi=130)
    plt.close(fig)

    # ---- plot 2: TX-ON minus TX-OFF difference spectrum ----
    fig, ax = plt.subplots(figsize=(11, 6))
    diff_plot = np.where(keep, excess, np.nan)
    ax.plot(fmhz, diff_plot, color="C2", lw=1.2, label="TX-ON − TX-OFF (masked)")
    ax.axvspan(lo, hi, color="grey", alpha=0.3, label="masked DC/LO artifact")
    ax.axhline(VISIBLE_DELTA_DB, color="r", ls=":", lw=1, label="%.0f dB visibility threshold" % VISIBLE_DELTA_DB)
    ax.axvline(peak_freq / 1e6, color="k", ls="--", lw=1, label="peak +%.1f kHz, %.2f dB" % (peak_offset / 1e3, txon_minus_txoff_db))
    ax.set_xlabel("Frequency [MHz]", fontsize=13)
    ax.set_ylabel("TX-ON − TX-OFF [dB]", fontsize=13)
    ax.set_title("Conducted IQ-level: TX-ON minus TX-OFF difference spectrum", fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=11)
    fig.tight_layout()
    fig.savefig(args.outdir / "txon_minus_txoff_psd.png", dpi=130)
    plt.close(fig)

    summary = {
        "txoff_artifact_peak_hz": txoff_artifact_peak_hz,
        "artifact_mask_width_hz": args.artifact_mask_width_hz,
        "known_artifact_bins_hz": extra,
        "peak_frequency_hz_after_mask": peak_freq,
        "peak_offset_hz_after_mask": peak_offset,
        "txon_minus_txoff_db_after_mask": txon_minus_txoff_db,
        "visible_txon_after_mask": visible,
        "max_abs_iq": max_abs_iq,
        "clipping_warning": clipping,
        "saturation_warning": saturation,
        "center_freq_hz": args.freq,
        "rate_sps": args.rate,
        "validation_scope": "conducted IQ-level capture only",
        "non_claims": [
            "Not packet decoding",
            "No PER / PDR / CRC",
            "No gateway ACK",
            "No OTA / live-satellite",
            "Not an RF link validation",
        ],
    }
    out_json = args.outdir / "artifact_masked_signal_detection_summary.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
