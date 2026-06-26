#!/usr/bin/env python3
"""Extract spectral peaks (hop-center proxy candidates) from a conducted-IQ run.

Peaks are taken from the TX-ON max-hold spectrum after TX-OFF baseline removal and
DC/LO artifact masking. WORDING: these are spectral peaks / hop-center proxy
candidates. This is NOT a decoded LR-FHSS hop sequence and makes no packet/PER/
link/OTA/satellite claim. Conducted IQ-level evidence only.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

GRID_SPACING_HZ = 25391  # LR-FHSS FCC grid


def load_iq(path: Path) -> np.ndarray:
    return np.load(path).astype(np.complex64)


def stft_mag(iq: np.ndarray, rate: float, nperseg: int):
    noverlap = nperseg // 2
    step = max(1, nperseg - noverlap)
    starts = np.arange(0, len(iq) - nperseg + 1, step)
    if len(starts) == 0:
        starts = np.array([0])
        iq = np.pad(iq, (0, nperseg - len(iq)))
    window = np.hanning(nperseg).astype(np.float32)
    rows = []
    for s in starts:
        seg = iq[s : s + nperseg] * window
        rows.append(np.abs(np.fft.fft(seg)) ** 2 / np.sum(window**2))
    sxx = np.array(rows)  # [time, freq]
    freqs = np.fft.fftshift(np.fft.fftfreq(nperseg, d=1.0 / rate))
    sxx = np.fft.fftshift(sxx, axes=1)
    times = np.arange(len(starts)) * (step / rate)
    return times, freqs, sxx


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--txoff-iq", required=True, type=Path)
    p.add_argument("--txon-iq", required=True, type=Path)
    p.add_argument("--rate", required=True, type=float)
    p.add_argument("--freq", required=True, type=float)
    p.add_argument("--outdir", required=True, type=Path)
    p.add_argument("--mask-width-hz", type=float, default=5000.0)
    p.add_argument("--top-n", type=int, default=12)
    p.add_argument("--min-prominence-db", type=float, default=6.0)
    p.add_argument("--nperseg", type=int, default=4096)
    args = p.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    txoff = load_iq(args.txoff_iq)
    txon = load_iq(args.txon_iq)

    times, freqs, son = stft_mag(txon, args.rate, args.nperseg)
    _, foff, soff = stft_mag(txoff, args.rate, args.nperseg)

    on_maxhold = 10 * np.log10(np.max(son, axis=0) + 1e-20)
    off_maxhold = 10 * np.log10(np.max(soff, axis=0) + 1e-20)
    off_median = 10 * np.log10(np.median(soff, axis=0) + 1e-20)
    excess = on_maxhold - off_median

    keep = np.abs(freqs) > args.mask_width_hz
    search = np.where(keep, excess, -np.inf)

    idx, props = find_peaks(search, prominence=args.min_prominence_db)
    if len(idx):
        order = np.argsort(props["prominences"])[::-1][: args.top_n]
        idx = idx[order]

    # off peaks for visible_in_txoff
    off_peak_idx, _ = find_peaks(off_maxhold, prominence=args.min_prominence_db)
    off_peak_offsets = set(np.round(freqs[off_peak_idx] / 1000).astype(int).tolist())

    rows = []
    for pid, i in enumerate(sorted(idx, key=lambda k: -excess[k])):
        off_hz = float(freqs[i])
        in_txoff = int(round(off_hz / 1000)) in off_peak_offsets
        rows.append(
            dict(
                peak_id=pid,
                frequency_hz=round(float(args.freq + off_hz), 3),
                offset_from_center_hz=round(off_hz, 3),
                relative_power_db=round(float(excess[i]), 3),
                txon_power_db=round(float(on_maxhold[i]), 3),
                txoff_power_db=round(float(off_median[i]), 3),
                txon_minus_txoff_db=round(float(excess[i]), 3),
                visible_in_txoff=bool(in_txoff),
                artifact_masked=False,
                note=f"~{round(off_hz / GRID_SPACING_HZ, 1)} grid steps from center; hop-center proxy candidate",
            )
        )

    cols = [
        "peak_id", "frequency_hz", "offset_from_center_hz", "relative_power_db",
        "txon_power_db", "txoff_power_db", "txon_minus_txoff_db", "visible_in_txoff",
        "artifact_masked", "note",
    ]
    with (args.outdir / "hop_center_peak_table.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    summary = {
        "n_peaks": len(rows),
        "center_freq_hz": args.freq,
        "rate_sps": args.rate,
        "mask_width_hz": args.mask_width_hz,
        "grid_spacing_hz": GRID_SPACING_HZ,
        "min_prominence_db": args.min_prominence_db,
        "peaks": rows,
        "validation_scope": "conducted IQ-level capture only",
        "wording_note": "spectral peaks are hop-center proxy candidates, NOT a decoded LR-FHSS hop sequence",
        "non_claims": [
            "Not packet decoding", "No PER / PDR / CRC", "No gateway ACK",
            "No OTA / live-satellite", "Not an RF link validation",
        ],
    }
    (args.outdir / "hop_center_peak_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # ---- annotated max-hold ----
    fmhz = (args.freq + freqs) / 1e6
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(fmhz, on_maxhold, color="C3", lw=1.0, label="TX-ON max-hold")
    ax.plot(fmhz, off_median, color="C0", lw=0.9, alpha=0.7, label="TX-OFF median")
    lo = (args.freq - args.mask_width_hz) / 1e6
    hi = (args.freq + args.mask_width_hz) / 1e6
    ax.axvspan(lo, hi, color="grey", alpha=0.3, label="masked DC/LO artifact")
    for r in rows:
        fx = r["frequency_hz"] / 1e6
        ax.axvline(fx, color="k", ls=":", lw=0.7)
        ax.annotate(str(r["peak_id"]), (fx, on_maxhold[np.argmin(np.abs(fmhz - fx))]),
                    fontsize=10, color="k", ha="center", va="bottom")
    ax.set_xlabel("Frequency [MHz]", fontsize=13)
    ax.set_ylabel("Power [dBFS]", fontsize=13)
    ax.set_title("Conducted IQ-level: TX-ON spectral peaks (hop-center proxy candidates)", fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=11)
    fig.tight_layout()
    fig.savefig(args.outdir / "annotated_maxhold_peaks.png", dpi=130)
    plt.close(fig)

    # ---- annotated waterfall (time-decimated to keep memory/time bounded) ----
    max_rows = 600
    tstep = max(1, son.shape[0] // max_rows)
    son_db = 10 * np.log10(son[::tstep] + 1e-20)
    wtimes = times[::tstep]
    fig, ax = plt.subplots(figsize=(11, 6))
    extent = [fmhz[0], fmhz[-1], wtimes[-1], wtimes[0]]
    ax.imshow(son_db, aspect="auto", extent=extent, cmap="viridis",
              vmin=np.percentile(son_db, 50), vmax=np.percentile(son_db, 99.9))
    for r in rows[: min(6, len(rows))]:
        ax.axvline(r["frequency_hz"] / 1e6, color="w", ls=":", lw=0.6, alpha=0.7)
    ax.set_xlabel("Frequency [MHz]", fontsize=13)
    ax.set_ylabel("Time [s]", fontsize=13)
    ax.set_title("Conducted IQ-level: TX-ON waterfall with spectral-peak markers", fontsize=13)
    ax.tick_params(labelsize=11)
    fig.tight_layout()
    fig.savefig(args.outdir / "annotated_waterfall_txon.png", dpi=130)
    plt.close(fig)

    print(f"n_peaks={len(rows)}")
    for r in rows[:3]:
        print(f"  peak {r['peak_id']}: offset {r['offset_from_center_hz']} Hz, {r['txon_minus_txoff_db']} dB")


if __name__ == "__main__":
    main()
