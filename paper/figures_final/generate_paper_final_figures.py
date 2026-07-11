#!/usr/bin/env python3
"""
Paper 1 final figures — regenerated from COMMITTED results.json only.
=====================================================================
Reads experiments/exp7_timing_sensitivity/results.json and
experiments/exp8_control_ablation/results.json (committed artifacts) and renders
paper-styled and talk-styled figures. No simulation is re-run; every number is
taken verbatim from the committed JSON, so figures cannot silently diverge from
the recorded results.

Outputs (paper, IEEE column width):
  paper/figures_final/fig_timing_sensitivity.pdf
  paper/figures_final/fig_control_ablation.pdf
Outputs (talk, 16:9 friendly, large fonts, deck color scheme):
  paper/slide_figures/fig_timing_sensitivity_talk.pdf
  paper/slide_figures/fig_control_ablation_talk.pdf

Scope: software-only guard-coverage / hop-bin-tolerance proxies — NOT measured
LR-FHSS packet outcomes. PGRL bars = gate-open synthetic regime.
"""
from __future__ import annotations

import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
SLIDE_DIR = os.path.join(REPO, "paper", "slide_figures")

# Deck color scheme (slides_overview.tex)
C_PHYS  = "#1F4E79"   # physics / SGP4 — dark blue
C_ML    = "#C46A1A"   # ML / PGRL candidate — muted orange
C_GATE  = "#2E7D32"   # gate / fallback — dark green
C_BAD   = "#B23A3A"   # failure / unsafe — dark red
C_GRAY  = "#666666"   # limitations / scope — gray

with open(os.path.join(REPO, "experiments/exp7_timing_sensitivity/results.json")) as f:
    EXP7 = json.load(f)
with open(os.path.join(REPO, "experiments/exp8_control_ablation/results.json")) as f:
    EXP8 = json.load(f)

ABLATION_ORDER = ["no_control", "timing_only", "frequency_only",
                  "timing_frequency", "timing_freq_pgrl"]
ABLATION_LABEL = {
    "no_control": "none",
    "timing_only": "timing\nonly",
    "frequency_only": "freq.\nonly",
    "timing_frequency": "timing\n+freq.",
    "timing_freq_pgrl": "timing+freq.\n+PGRL*",
}
ABLATION_COLOR = {
    "no_control": C_GRAY,
    "timing_only": C_PHYS,
    "frequency_only": C_PHYS,
    "timing_frequency": C_PHYS,
    "timing_freq_pgrl": C_ML,
}


def timing_figure(path: str, talk: bool = False):
    """(a) miss + guard overhead vs sigma_t; (b) energy/success vs sigma_t with
    named configs and TLE-age markers."""
    fs = 13 if talk else 8
    figsize = (10.0, 4.2) if talk else (7.1, 2.55)
    plt.rcParams.update({"font.size": fs})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    sweep = EXP7["residual_offset_sweep"]
    sg   = np.array([r["sigma_t_s"] for r in sweep])
    miss = np.array([r["miss_rate"] for r in sweep]) * 100
    ovh  = np.array([r["guard_overhead"] for r in sweep]) * 100
    eps  = np.array([r["energy_per_success_j"] for r in sweep]) * 1e3

    ax1.semilogx(sg, miss, "-", color=C_BAD, lw=2, label="TX-window miss rate")
    ax1.semilogx(sg, ovh, "--", color=C_PHYS, lw=2, label="guard overhead")
    ax1.set_xlabel(r"residual timing offset $\sigma_t$ [s]")
    ax1.set_ylabel("[% ]")
    ax1.legend(fontsize=fs - 1, loc="upper left", frameon=False)
    ax1.grid(True, alpha=0.3)
    ax1.set_title("(a) coverage vs. timing offset", fontsize=fs)

    ax2.loglog(sg, eps, "-", color=C_GATE, lw=2)
    marker_cfg = {
        "sgp4_only": (C_PHYS, "s", "SGP4 open-loop"),
        "pgrl_uncert": (C_ML, "^", "PGRL (gate-open synth.)"),
    }
    for name, (c, m, lab) in marker_cfg.items():
        cfg = EXP7["named_configs"][name]
        ax2.plot(cfg["sigma_t_s"], cfg["energy_per_success_j"] * 1e3,
                 m, color=c, ms=8 if talk else 6, label=lab, zorder=5)
    # TLE-age markers on the SGP4 open-loop staleness curve
    for row in EXP7["tle_age_sweep"]:
        if row["tle_age_h"] in (24, 168):
            s = row["sgp4"]["sigma_t_s"]
            e = row["sgp4"]["energy_per_success_j"] * 1e3
            # keep labels inside axes (168 h sits at the top-right corner)
            dx, dy = (0.30, 0.45) if row["tle_age_h"] == 168 else (0.24, 2.4)
            ax2.annotate(f'TLE {row["tle_age_h"]} h', xy=(s, e),
                         xytext=(s * dx, e * dy), fontsize=fs - 1.5,
                         color=C_GRAY,
                         arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=0.8))
            ax2.plot(s, e, "o", color=C_GRAY, ms=5)
    ax2.set_xlabel(r"residual timing offset $\sigma_t$ [s]")
    ax2.set_ylabel("energy / successful burst [mJ]")
    ax2.legend(fontsize=fs - 1, loc="lower right", frameon=False)
    ax2.grid(True, alpha=0.3, which="both")
    ax2.set_title("(b) energy vs. timing offset", fontsize=fs)

    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


ABLATION_LABEL_TALK = {
    "no_control": "none",
    "timing_only": "timing",
    "frequency_only": "freq.",
    "timing_frequency": "t+f",
    "timing_freq_pgrl": "t+f+PGRL*",
}


def ablation_figure(path: str, talk: bool = False):
    """(a) joint success rate (log); (b) energy per successful burst (log)."""
    fs = 13 if talk else 8
    figsize = (10.0, 4.2) if talk else (7.1, 2.55)
    plt.rcParams.update({"font.size": fs})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    res = EXP8["results"]
    x = np.arange(len(ABLATION_ORDER))
    labels = [(ABLATION_LABEL_TALK if talk else ABLATION_LABEL)[n]
              for n in ABLATION_ORDER]
    colors = [ABLATION_COLOR[n] for n in ABLATION_ORDER]
    succ = [res[n]["success_rate"] * 100 for n in ABLATION_ORDER]
    eps  = [res[n]["energy_per_success_j"] * 1e3 for n in ABLATION_ORDER]

    ax1.bar(x, succ, color=colors)
    ax1.set_yscale("log")
    ax1.set_ylim(top=max(succ) * 4)   # headroom for value labels
    ax1.set_xticks(x); ax1.set_xticklabels(labels, fontsize=fs - 1.5)
    ax1.set_ylabel("joint success rate [%] (log)")
    for xi, v in zip(x, succ):
        ax1.text(xi, v * 1.25, f"{v:.2g}%", ha="center", fontsize=fs - 2)
    ax1.grid(True, axis="y", alpha=0.3, which="both")
    ax1.set_title("(a) success / hit rate", fontsize=fs)

    ax2.bar(x, eps, color=colors)
    ax2.set_yscale("log")
    ax2.set_ylim(top=max(eps) * 4)    # headroom for value labels
    ax2.set_xticks(x); ax2.set_xticklabels(labels, fontsize=fs - 1.5)
    ax2.set_ylabel("energy / successful burst [mJ] (log)")
    for xi, v in zip(x, eps):
        ax2.text(xi, v * 1.25, f"{v:,.0f}" if v >= 100 else f"{v:.1f}",
                 ha="center", fontsize=fs - 2)
    ax2.grid(True, axis="y", alpha=0.3, which="both")
    ax2.set_title("(b) energy per successful burst", fontsize=fs)

    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


# ── Composite paper figures ───────────────────────────────────────────────────
# Evidence-gate data copied VERBATIM from committed docs/review/*.csv (same
# numbers as paper/figures/generate_evidence_gate_figures.py).
BK_STALE      = [8, 24, 48, 72, 96, 168]
BK_BASE       = [0.2430, 0.8161, 1.9433, 4.8947, 10.1153, 26.9243]
BK_ML         = [0.3501, 0.9109, 2.8608, 5.9092, 11.7663, 45.2629]
BK_DPCT       = [44.1, 11.6, 47.2, 20.7, 16.3, 68.1]
BKX_STALE     = [8, 24, 48]
BKX_BASE      = [0.1877, 0.4969, 2.4092]
BKX_ML        = [0.3261, 1.8639, 2.8458]
BKX_DPCT      = [73.7, 275.1, 18.1]
GAMMA         = [0.90, 0.95, 0.99, 1.00]
GATE_FRESH    = [0, 0, 0, 0]
GATE_MODERATE = [0, 0, 1, 1]
GATE_EXTREME  = [1, 1, 1, 1]
DEP_FRESH     = [9.558] * 4
DEP_MODERATE  = [63.174, 63.174, 60.176, 60.176]
DEP_EXTREME   = [99.748] * 4
BASE_EXTREME  = 1859.296


def gate_evidence_figure(path: str):
    """Composite Fig. 2: (a,b) real BLACK KITE negative result; (c,d) synthetic
    gate sanity check. Numbers verbatim from committed CSVs."""
    fs = 8
    plt.rcParams.update({"font.size": fs})
    fig, axes = plt.subplots(2, 2, figsize=(7.1, 3.85))

    # (a) real: held-out MAE vs staleness
    ax = axes[0, 0]
    real_handles = [
        ax.plot(BK_STALE, BK_BASE, "o-", color=C_PHYS, lw=1.5, ms=4,
                label="baseline (BK1)")[0],
        ax.plot(BK_STALE, BK_ML, "s--", color=C_BAD, lw=1.5, ms=4,
                label="learned (BK1)")[0],
        ax.plot(BKX_STALE, BKX_BASE, "^:", color=C_PHYS, lw=1.0, ms=4, alpha=0.65,
                label=r"baseline (BK1$\to$BK2)")[0],
        ax.plot(BKX_STALE, BKX_ML, "v:", color=C_BAD, lw=1.0, ms=4, alpha=0.65,
                label=r"learned (BK1$\to$BK2)")[0],
    ]
    ax.set_yscale("log")
    ax.set_xscale("log"); ax.set_xticks(BK_STALE)
    ax.set_xticklabels([str(s) for s in BK_STALE], fontsize=fs - 1)
    ax.set_xlabel("stale-TLE age [h]")
    ax.set_ylabel("held-out MAE [Hz] (log)")
    ax.grid(True, which="major", ls=":", alpha=0.35)
    ax.set_title("(a) Real-data held-out MAE", fontsize=fs)
    ax.text(0.97, 0.05, "real BLACK KITE", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=fs - 2, color=C_GRAY,
            style="italic",
            bbox=dict(fc="white", ec="none", alpha=0.65, pad=1.0))

    # (b) real: degradation, all positive → gate closes
    ax = axes[0, 1]
    ax.axhline(0, color="0.5", lw=0.8)
    ax.plot(BK_STALE, BK_DPCT, "s-", color=C_BAD, lw=1.5, ms=4)
    ax.plot(BKX_STALE, BKX_DPCT, "v:", color=C_BAD, lw=1.2, ms=4, alpha=0.65)
    ax.set_xscale("log"); ax.set_xticks(BK_STALE)
    ax.set_xticklabels([str(s) for s in BK_STALE], fontsize=fs - 1)
    ax.set_xlabel("stale-TLE age [h]")
    ax.set_ylabel("degradation [%]")
    ax.grid(True, ls=":", alpha=0.35)
    ax.set_title("(b) Real-data degradation", fontsize=fs)
    ax.text(0.97, 0.05, "real BLACK KITE", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=fs - 2, color=C_GRAY,
            style="italic",
            bbox=dict(fc="white", ec="none", alpha=0.65, pad=1.0))

    # (c) synthetic: gate decision vs gamma
    ax = axes[1, 0]
    synth_handles = [
        ax.step(GAMMA, GATE_EXTREME, where="mid", marker="o", ms=4, lw=1.6,
                color=C_GATE, label="systematic")[0],
        ax.step(GAMMA, GATE_MODERATE, where="mid", marker="s", ms=4, lw=1.6,
                color=C_ML, label="moderate")[0],
        ax.step(GAMMA, GATE_FRESH, where="mid", marker="^", ms=4, lw=1.6,
                color=C_PHYS, label="noise-dom. (real-like)")[0],
    ]
    ax.set_yticks([0, 1]); ax.set_yticklabels(["closed", "open"], fontsize=fs - 1)
    ax.set_ylim(-0.3, 1.3)
    ax.set_xticks([0.90, 0.95, 1.00])
    ax.set_xlabel(r"gate threshold $\gamma$")
    ax.set_ylabel("gate decision")
    ax.grid(True, ls=":", alpha=0.35)
    ax.set_title("(c) Synthetic gate decision", fontsize=fs)
    ax.text(0.05, 0.43, "synthetic sanity check", transform=ax.transAxes,
            ha="left", va="center", fontsize=fs - 2, color=C_GRAY,
            style="italic",
            bbox=dict(fc="white", ec="none", alpha=0.65, pad=1.0))

    # (d) synthetic: deployed MAE vs gamma
    ax = axes[1, 1]
    ax.plot(GAMMA, DEP_EXTREME, "o-", color=C_GATE, lw=1.5, ms=4, label="systematic")
    ax.plot(GAMMA, DEP_MODERATE, "s-", color=C_ML, lw=1.5, ms=4, label="moderate")
    ax.plot(GAMMA, DEP_FRESH, "^-", color=C_PHYS, lw=1.5, ms=4, label="noise-dom.")
    ax.axhline(BASE_EXTREME, color=C_GATE, ls="--", lw=0.9, alpha=0.6)
    ax.text(0.03, 0.78, "systematic baseline\n(gate closed)",
            transform=ax.transAxes, fontsize=fs - 2, color=C_GATE,
            bbox=dict(fc="white", ec="none", alpha=0.65, pad=1.0))
    ax.set_yscale("log")
    ax.set_xticks([0.90, 0.95, 1.00])
    ax.set_xlabel(r"gate threshold $\gamma$")
    ax.set_ylabel("deployed MAE [Hz] (log)")
    ax.grid(True, which="major", ls=":", alpha=0.35)
    ax.set_title("(d) Synthetic deployed MAE", fontsize=fs)
    ax.text(0.56, 0.62, "synthetic sanity check", transform=ax.transAxes,
            ha="left", va="center", fontsize=fs - 2, color=C_GRAY,
            style="italic",
            bbox=dict(fc="white", ec="none", alpha=0.65, pad=1.0))

    fig.tight_layout(rect=(0.0, 0.08, 1.0, 0.92), h_pad=1.0, w_pad=1.1)
    fig.legend(handles=real_handles, loc="upper center", bbox_to_anchor=(0.5, 1.0),
               ncol=4, fontsize=fs - 2.2, frameon=False, handlelength=1.4,
               columnspacing=0.9)
    fig.legend(handles=synth_handles, loc="lower center", bbox_to_anchor=(0.5, 0.0),
               ncol=3, fontsize=fs - 2.2, frameon=False, handlelength=1.4,
               columnspacing=1.0)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def endpoint_proxies_figure(path: str):
    """Composite Fig. 3: (a,b) exp7 timing sensitivity; (c,d) exp8 ablation."""
    fs = 8
    plt.rcParams.update({"font.size": fs, "axes.titlesize": fs - 0.5,
                         "xtick.labelsize": fs - 0.5, "ytick.labelsize": fs - 0.5})
    fig, axes = plt.subplots(2, 2, figsize=(7.1, 3.85))

    sweep = EXP7["residual_offset_sweep"]
    sg   = np.array([r["sigma_t_s"] for r in sweep])
    miss = np.array([r["miss_rate"] for r in sweep]) * 100
    ovh  = np.array([r["guard_overhead"] for r in sweep]) * 100
    eps  = np.array([r["energy_per_success_j"] for r in sweep]) * 1e3

    ax = axes[0, 0]
    proxy_handles = [
        ax.semilogx(sg, miss, "-", color=C_BAD, lw=1.8,
                    label="TX-window miss")[0],
        ax.semilogx(sg, ovh, "--", color=C_PHYS, lw=1.8,
                    label="guard overhead")[0],
    ]
    ax.set_xlabel(r"residual timing offset $\sigma_t$ [s]")
    ax.set_ylabel("[%]")
    ax.grid(True, ls=":", alpha=0.35)
    ax.set_title("(a) coverage vs. timing offset", fontsize=fs)

    ax = axes[0, 1]
    ax.loglog(sg, eps, "-", color=C_GATE, lw=1.8)
    for name, (c, m, lab) in {
        "sgp4_only": (C_PHYS, "s", "SGP4 open-loop"),
        "pgrl_uncert": (C_ML, "^", "learned (gate-open synth.)"),
    }.items():
        cfg = EXP7["named_configs"][name]
        proxy_handles.append(ax.plot(
            cfg["sigma_t_s"], cfg["energy_per_success_j"] * 1e3, m,
            color=c, ms=6, label=lab, zorder=5)[0])
    for row in EXP7["tle_age_sweep"]:
        if row["tle_age_h"] in (24, 168):
            s = row["sgp4"]["sigma_t_s"]
            e = row["sgp4"]["energy_per_success_j"] * 1e3
            offset = (-10, -11) if row["tle_age_h"] == 168 else (5, 7)
            ha = "right" if row["tle_age_h"] == 168 else "left"
            ax.annotate(f'TLE {row["tle_age_h"]} h', xy=(s, e),
                        xytext=offset, textcoords="offset points",
                        ha=ha, fontsize=fs - 2, color=C_GRAY)
            ax.plot(s, e, "o", color=C_GRAY, ms=4)
    ax.set_xlabel(r"residual timing offset $\sigma_t$ [s]")
    ax.set_ylabel("energy / success [mJ] (log)")
    ax.grid(True, which="major", ls=":", alpha=0.35)
    ax.set_title("(b) energy vs. timing offset", fontsize=fs)

    res = EXP8["results"]
    x = np.arange(len(ABLATION_ORDER))
    labels = [ABLATION_LABEL_TALK[n] for n in ABLATION_ORDER]
    colors = [ABLATION_COLOR[n] for n in ABLATION_ORDER]
    succ = [res[n]["success_rate"] * 100 for n in ABLATION_ORDER]
    epsb = [res[n]["energy_per_success_j"] * 1e3 for n in ABLATION_ORDER]

    ax = axes[1, 0]
    ax.bar(x, succ, color=colors)
    ax.set_yscale("log"); ax.set_ylim(top=max(succ) * 8)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=fs - 1)
    ax.set_ylabel("joint success [%] (log)")
    for xi, v in zip(x, succ):
        ax.text(xi, v * 1.2, f"{v:.2g}%", ha="center", fontsize=fs - 2)
    ax.grid(True, axis="y", which="major", ls=":", alpha=0.35)
    ax.set_title("(c) ablation: success proxy", fontsize=fs)

    ax = axes[1, 1]
    ax.bar(x, epsb, color=colors)
    ax.set_yscale("log"); ax.set_ylim(top=max(epsb) * 8)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=fs - 1)
    ax.set_ylabel("energy / success [mJ] (log)")
    for xi, v in zip(x, epsb):
        ax.text(xi, v * 1.2, f"{v:,.0f}" if v >= 100 else f"{v:.1f}",
                ha="center", fontsize=fs - 2)
    ax.grid(True, axis="y", which="major", ls=":", alpha=0.35)
    ax.set_title("(d) ablation: energy proxy", fontsize=fs)

    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.92), h_pad=1.0, w_pad=1.1)
    fig.legend(handles=proxy_handles, loc="upper center", bbox_to_anchor=(0.5, 1.0),
               ncol=4, fontsize=fs - 2.2, frameon=False, handlelength=1.4,
               columnspacing=0.9)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def hw_evidence_figure(path: str):
    """Fig. 4 (sanity-evidence box): (a) conducted setup schematic; (b) compact
    evidence summary; (c) small subordinate max-hold spectrum inset (committed
    PNG pixels verbatim, in-image title strip cropped; no re-analysis). Numbers
    from committed campaign reports."""
    from PIL import Image
    import matplotlib.patches as mpatches

    src = os.path.join(REPO, "hardware_conducted_iq", "figures",
                       "fig_hw_maxhold_txon_vs_txoff.png")
    img = Image.open(src)
    w, h = img.size
    img_c = img.crop((0, int(h * 0.095), w, h))  # strip in-image title only

    fs = 9
    plt.rcParams.update({"font.size": fs})
    fig = plt.figure(figsize=(3.5, 2.9))
    gs = fig.add_gridspec(2, 2, height_ratios=[0.42, 0.58],
                          width_ratios=[0.55, 0.45], hspace=0.42, wspace=0.06)

    # (a) conducted setup schematic (full width)
    axa = fig.add_subplot(gs[0, :])
    axa.set_xlim(0, 10); axa.set_ylim(0, 3.1); axa.axis("off")

    def box(x, y, wd, ht, txt, fc="#FFFFFF"):
        axa.add_patch(mpatches.FancyBboxPatch(
            (x, y), wd, ht, boxstyle="round,pad=0.06",
            fc=fc, ec="#444444", lw=0.8))
        axa.text(x + wd / 2, y + ht / 2, txt, ha="center", va="center",
                 fontsize=fs - 2.5)

    box(0.15, 0.95, 3.0, 1.6,
        "NUCLEO-L476RG\n+ LR1121\n923.2 MHz / $-$17 dBm", fc="#EDF3F8")
    box(4.0, 1.15, 2.0, 1.2, "50 dB att.\n+ coax")
    box(6.9, 0.95, 2.95, 1.6, "USRP B210\nRX2 A", fc="#F2F2F2")
    axa.annotate("", xy=(4.0, 1.75), xytext=(3.15, 1.75),
                 arrowprops=dict(arrowstyle="->", color="#444444", lw=0.9))
    axa.annotate("", xy=(6.9, 1.75), xytext=(6.0, 1.75),
                 arrowprops=dict(arrowstyle="->", color="#444444", lw=0.9))
    axa.text(5.0, 0.25, "conducted only --- no antenna, no OTA path",
             ha="center", fontsize=fs - 2.7, color=C_GRAY, style="italic")
    axa.set_title("(a) conducted measurement path", fontsize=fs - 1)

    # (b) evidence summary (left)
    axb = fig.add_subplot(gs[1, 0])
    axb.axis("off")
    lines = [
        "923.2 MHz / $-$17 dBm deterministic FW",
        "TX-ON$-$TX-OFF: $41.25\\pm0.36$ dB",
        "\u2003(four 4 MS/s runs)",
        "2 MS/s sanity: 43.76 dB",
        "no clipping / saturation",
        "no packet decode / PER / PDR / OTA",
    ]
    y = 0.95
    for ln in lines:
        bullet = "" if ln.startswith("\u2003") else "$\\bullet$ "
        axb.text(0.0, y, bullet + ln, fontsize=fs - 2.6, va="top",
                 color="#222222")
        y -= 0.145
    axb.set_title("(b) evidence summary", fontsize=fs - 1, loc="left")

    # (c) small subordinate spectrum inset (right)
    axc = fig.add_subplot(gs[1, 1])
    axc.imshow(img_c)
    axc.axis("off")
    axc.set_title("(c) max-hold", fontsize=fs - 2)

    fig.savefig(path, bbox_inches="tight", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    # Composite paper figures (final manuscript)
    gate_evidence_figure(os.path.join(HERE, "fig_gate_evidence.pdf"))
    endpoint_proxies_figure(os.path.join(HERE, "fig_endpoint_proxies.pdf"))
    hw_evidence_figure(os.path.join(HERE, "fig_hw_evidence.pdf"))
    # Talk variants (deck; unchanged paths)
    os.makedirs(SLIDE_DIR, exist_ok=True)
    timing_figure(os.path.join(SLIDE_DIR, "fig_timing_sensitivity_talk.pdf"), talk=True)
    ablation_figure(os.path.join(SLIDE_DIR, "fig_control_ablation_talk.pdf"), talk=True)
    print("Wrote composite paper figures + talk variants (committed data only).")
