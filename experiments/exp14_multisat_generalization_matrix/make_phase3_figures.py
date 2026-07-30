#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "matplotlib>=3.8"]
# ///
"""Phase-3 figures: endpoint-value closure and gamma deployment frontier.

Software-only, model-derived inter-TLE residuals; no measured RF truth and no
packet/PER/PDR claim.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path(__file__).resolve().parent / "phase3_endpoint_value"
C_PHYS, C_ML, C_GRAY = "#1F4E79", "#C46A1A", "#666666"
C_BAD, C_OK = "#B23A3A", "#2F6F3E"
NOTE = ("Software/model-derived endpoint-budget proxy "
        "(reference_is_measured_truth = false); not a packet or link result.")


def fig_endpoint(payload) -> None:
    cases = payload["cases"]
    scale = payload["residual_scale_required_for_frequency_branch_to_matter"]
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 3.9))

    ax = axes[0]
    labels = [f"{c['satellite_name']}\n@{c['staleness_h']} h" for c in cases]
    x = np.arange(len(cases))
    base = [c["baseline"]["mae_hz"] for c in cases]
    learn = [c["learned"]["mae_hz"] for c in cases]
    ax.bar(x - 0.19, base, 0.38, color=C_PHYS, label="SGP4")
    ax.bar(x + 0.19, learn, 0.38, color=C_ML, label="learned")
    for xi, c in zip(x, cases):
        ax.text(xi, max(base[xi], learn[xi]) * 1.04,
                f"{c['degradation_pct']:+.2f}%", ha="center", fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("held-out MAE [Hz]", fontsize=8)
    ax.set_title("(a) residual MAE: the detectable difference", fontsize=8.5)
    ax.legend(fontsize=6.5, frameon=False)
    ax.grid(True, axis="y", ls=":", alpha=0.35)

    ax = axes[1]
    keys = [("guard_proxy_hz", "guard 2·p99 [Hz]"),
            ("outage_proxy", "outage Pr(|e|>F_tol)"),
            ("energy_per_success_j", "energy / success [J]")]
    width = 0.38
    for ci, c in enumerate(cases):
        rels = []
        for k, _ in keys:
            b, ln = c["baseline"][k], c["learned"][k]
            rels.append(100.0 * (ln - b) / b if b else 0.0)
        ax.bar(np.arange(len(keys)) + (ci - 0.5) * width, rels, width,
               color=[C_ML, C_PHYS][ci], label=f"{c['satellite_name']}")
    ax.axhline(0.0, color=C_BAD, lw=1.2)
    ax.set_xticks(np.arange(len(keys)))
    ax.set_xticklabels([lab for _, lab in keys], fontsize=7)
    ax.set_ylabel("endpoint proxy change [%]", fontsize=8)
    ax.set_ylim(-1.2, 1.2)
    ax.set_title("(b) endpoint budget: no measurable change", fontsize=8.5)
    ax.text(0.5, 0.5, "all changes < 0.001 %\n(energy / success delta\n"
            "unresolvable at double precision)",
            transform=ax.transAxes, ha="center", va="center",
            fontsize=8, color=C_GRAY)
    ax.legend(fontsize=6.5, frameon=False)
    ax.grid(True, axis="y", ls=":", alpha=0.35)

    ax = axes[2]
    actual = [c["baseline"]["sigma_residual_hz"] for c in cases]
    need = [scale["sigma_residual_hz_for_p_freq_miss_1e-06"],
            scale["sigma_residual_hz_for_p_freq_miss_0.001"],
            scale["sigma_residual_hz_for_p_freq_miss_0.01"]]
    names = ([f"{c['satellite_name']} actual" for c in cases]
             + ["σ_residual for P_f=1e-6", "σ_residual for P_f=1e-3",
                "σ_residual for P_f=1e-2"])
    vals = actual + need
    cols = [C_ML, C_PHYS, C_OK, C_OK, C_OK]
    ax.barh(np.arange(len(vals)), vals, color=cols)
    ax.set_yticks(np.arange(len(vals)))
    ax.set_yticklabels(names, fontsize=7)
    ax.set_xscale("log")
    ax.set_xlabel("σ_residual [Hz] (log)", fontsize=8)
    ax.set_title("(c) how far the residual is from mattering", fontsize=8.5)
    ax.grid(True, axis="x", ls=":", alpha=0.35)
    for i, v in enumerate(vals):
        ax.text(v * 1.15, i, f"{v:.2f}", va="center", fontsize=6.5)

    fig.suptitle("Phase-3 endpoint-value closure: a statistically detectable "
                 "~2 % residual gain produces no endpoint-budget reduction",
                 fontsize=10)
    fig.text(0.5, -0.02, NOTE, ha="center", fontsize=6, color=C_GRAY)
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_real_gain_vs_endpoint_value.{ext}",
                    bbox_inches="tight", dpi=200 if ext == "png" else None)
    plt.close(fig)


def fig_gamma(frontier) -> None:
    g = [f["gamma"] for f in frontier]
    x = np.arange(len(g))
    imp = [f["n_improve"] for f in frontier]
    wor = [f["n_worsen"] for f in frontier]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.8))

    ax = axes[0]
    ax.bar(x, imp, 0.62, color=C_OK, label="opened & improves held-out")
    ax.bar(x, wor, 0.62, bottom=imp, color=C_BAD, label="opened & worsens held-out")
    for xi, (a, b) in enumerate(zip(imp, wor)):
        if a + b:
            ax.text(xi, a + b + 0.4, f"{a + b}", ha="center", fontsize=7.5)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{v:.3f}".rstrip("0").rstrip(".") for v in g], fontsize=8)
    ax.set_xlabel("γ (deployment margin)", fontsize=8)
    ax.set_ylabel("cells opening / 54", fontsize=8)
    ax.axvline(g.index(0.95), color=C_PHYS, lw=1.4, ls=":")
    ax.text(g.index(0.95), max(np.array(imp) + np.array(wor)) * 0.85,
            " preregistered\n γ = 0.95", fontsize=7, color=C_PHYS)
    ax.set_title("(a) cells deploying, and whether they help\n"
                 "(left = looser gate)", fontsize=8.5)
    ax.legend(fontsize=6.5, frameon=False)
    ax.grid(True, axis="y", ls=":", alpha=0.35)

    ax = axes[1]
    prec = [100.0 * f["n_improve"] / (f["n_open"] or 1) for f in frontier]
    ax.plot(x, prec, "o-", color=C_PHYS, lw=1.8, ms=5)
    for xi, f in enumerate(frontier):
        if f["n_open"]:
            ax.annotate(f"n={f['n_open']}", (xi, prec[xi]), textcoords="offset points",
                        xytext=(0, 7), ha="center", fontsize=6.5, color=C_GRAY)
    ax.axhline(50.0, color=C_BAD, lw=1.1, ls="--")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{v:.3f}".rstrip("0").rstrip(".") for v in g], fontsize=8)
    ax.set_xlabel("γ (deployment margin)", fontsize=8)
    ax.set_ylabel("% of opened cells that improve held-out", fontsize=8)
    ax.set_ylim(0, 105)
    ax.set_title("(b) a larger required margin does not raise precision",
                 fontsize=8.5)
    ax.grid(True, ls=":", alpha=0.35)

    fig.suptitle("Phase-3 γ deployment frontier, preregistered 1500 Hz dataset "
                 "(54 target-specific cells). γ is NOT re-chosen.", fontsize=10)
    fig.text(0.5, -0.02, NOTE, ha="center", fontsize=6, color=C_GRAY)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_gamma_deployment_frontier.{ext}",
                    bbox_inches="tight", dpi=200 if ext == "png" else None)
    plt.close(fig)


def main() -> int:
    payload = json.loads((OUT / "endpoint_value_results.json").read_text())
    frontier = json.loads((OUT / "gamma_frontier.json").read_text())
    fig_endpoint(payload)
    fig_gamma(frontier)
    print("wrote 4 figure files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
