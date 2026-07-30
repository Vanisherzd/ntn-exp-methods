#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "matplotlib>=3.8"]
# ///
"""Paper 1 result figures, built from the committed multi-satellite campaign.

Reads only campaign artifacts under
experiments/exp14_multisat_generalization_matrix/ -- no simulation is re-run, so
the figures cannot silently diverge from the recorded results.

Outputs:
  paper/figures_final/fig_decision_map.pdf   -- validation vs held-out decision
  paper/figures_final/fig_evidence_axes.pdf  -- three-axis evidence

Scope: software-only, model-derived inter-TLE residuals; references are later
element solutions propagated by SGP4, not measured RF truth.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / "experiments" / "exp14_multisat_generalization_matrix"

INK = "#222222"          # text and structural lines
GREY = "#9AA3AB"         # the 54 neutral points
ACCENT = "#B35A00"       # the single accent
MARGIN_PCT = 5.0         # gamma = 0.95 -> +5 % validation improvement
SCREENS = ["none", "150", "500", "1500", "3000"]

plt.rcParams.update({
    "font.size": 9,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.linewidth": 0.8,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def _load():
    p2 = json.loads((EXP / "phase2_reject_sensitivity"
                     / "reject_sensitivity_results.json").read_text())
    p3 = json.loads((EXP / "phase3_endpoint_value"
                     / "endpoint_value_results.json").read_text())
    sens_path = EXP / "canonicalization_sensitivity.json"
    sens = json.loads(sens_path.read_text()) if sens_path.is_file() else {}
    return p2, p3, sens


def _primary_cells(p2):
    """The 54 target-specific cells at the pre-specified 1500 Hz screen."""
    return [r for r in p2["rows"]
            if r["status"] == "evaluated" and r["threshold_hz"] == "1500"]


def _threshold_series(p2, name: str, band: int) -> list[float]:
    idx = {r["threshold_hz"]: r for r in p2["rows"]
           if r["status"] == "evaluated"
           and r["satellite_name"] == name and r["staleness_h"] == band}
    return [idx[t]["test_improvement_pct"] if t in idx else np.nan for t in SCREENS]


# ---------------------------------------------------------------------------
# Figure 2 -- what validation told the gate, and what happened next
# ---------------------------------------------------------------------------
def fig_decision_map(p2, sens) -> None:
    """(a) every configuration at true coordinates; (b) the deployment region."""
    cells = _primary_cells(p2)
    xs = np.array([c["val_improvement_pct"] for c in cells])
    ys = np.array([c["test_improvement_pct"] for c in cells])
    n_open = sum(1 for c in cells if c["gate_decision"] == "open")

    zx = (-15.5, 8.5)
    zy = (-23.0, 7.0)

    fig, (axg, axz) = plt.subplots(
        1, 2, figsize=(7.16, 1.72),
        gridspec_kw={"width_ratios": [0.32, 0.68], "wspace": 0.26})

    # ---- (a) global view, true coordinates, nothing clipped --------------
    axg.axvline(MARGIN_PCT, color=ACCENT, lw=1.0, ls="--", zorder=3)
    axg.axhline(0.0, color=INK, lw=0.7, ls=":", zorder=3)
    axg.scatter(xs, ys, s=11, facecolor=GREY, edgecolor=INK, linewidth=0.3,
                alpha=0.85, zorder=4)
    axg.add_patch(plt.Rectangle((zx[0], zy[0]), zx[1] - zx[0], zy[1] - zy[0],
                                fill=False, edgecolor=INK, lw=0.7, zorder=5))
    axg.set_xlim(-135, 22)
    axg.set_ylim(-135, 22)
    axg.set_xticks([-120, -60, 0])
    axg.set_yticks([-120, -60, 0])
    axg.set_xticklabels(["$-$120", "$-$60", "0"])
    axg.set_yticklabels(["$-$120", "$-$60", "0"])
    axg.tick_params(labelsize=7.5)
    axg.set_xlabel("validation impr. [%]", fontsize=8)
    axg.set_ylabel("held-out impr. [%]", fontsize=8)
    axg.set_title("(a) all 54 configurations", fontsize=8.5)
    for side in ("top", "right"):
        axg.spines[side].set_visible(False)

    # ---- (b) deployment-region zoom --------------------------------------
    axz.axvline(MARGIN_PCT, color=ACCENT, lw=1.4, ls="--", zorder=3)
    axz.axhline(0.0, color=INK, lw=0.8, ls=":", zorder=3)
    keep = (xs >= zx[0]) & (xs <= zx[1]) & (ys >= zy[0]) & (ys <= zy[1])
    axz.scatter(xs[keep], ys[keep], s=26, facecolor=GREY, edgecolor=INK,
                linewidth=0.4, alpha=0.75, zorder=4)

    def mark(name, band, label, off):
        c = next(c for c in cells
                 if c["satellite_name"] == name and c["staleness_h"] == band)
        x, y = c["val_improvement_pct"], c["test_improvement_pct"]
        axz.scatter([x], [y], s=54, facecolor="none", edgecolor=ACCENT,
                    linewidth=1.5, zorder=6)
        axz.annotate(label, xy=(x, y), xytext=off, textcoords="offset points",
                     fontsize=7.5, color=ACCENT, ha="center", zorder=7,
                     arrowprops=dict(arrowstyle="-", lw=0.6, color=ACCENT))

    mark("IRIDIUM 181", 8, "IRID-181 @8 h", (-46, 13))
    mark("BLACK KITE-2", 24, "BK-2 @24 h", (-42, 0))

    abl = sens.get("deletion_ablation") if sens else None
    if abl:
        axz.scatter([abl["val_improvement_pct"]], [abl["test_improvement_pct"]],
                    s=60, facecolor="none", edgecolor=INK, linewidth=1.2,
                    marker="D", zorder=6)
        axz.annotate("deletion ablation",
                     xy=(abl["val_improvement_pct"], abl["test_improvement_pct"]),
                     xytext=(-4, -26), textcoords="offset points", fontsize=7.5,
                     color=INK, ha="center", zorder=7,
                     arrowprops=dict(arrowstyle="-", lw=0.6, color=INK))

    axz.annotate(f"{n_open} / {len(cells)} admitted", xy=(0.60, 0.045),
                 xycoords="axes fraction", ha="center", fontsize=8.5,
                 color=ACCENT)

    axz.set_xlim(*zx)
    axz.set_ylim(*zy)
    axz.set_xticks([-15, -10, -5, 0, MARGIN_PCT])
    axz.set_xticklabels(["$-$15", "$-$10", "$-$5", "0", "+5"])
    axz.set_yticks([-20, -15, -10, -5, 0])
    axz.set_yticklabels(["$-$20", "$-$15", "$-$10", "$-$5", "0"])
    axz.tick_params(labelsize=8)
    axz.set_xlabel("validation improvement [%]", fontsize=8.5)
    axz.set_ylabel("held-out improvement [%]", fontsize=8.5)
    axz.set_title("(b) deployment region", fontsize=8.5)
    for side in ("top", "right"):
        axz.spines[side].set_visible(False)

    fig.tight_layout()
    for ext, kw in (("pdf", {}), ("png", {"dpi": 220})):
        fig.savefig(HERE / f"fig_decision_map.{ext}", bbox_inches="tight", **kw)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3 -- detectability, robustness, endpoint relevance
# ---------------------------------------------------------------------------
def fig_evidence_axes(p2, p3) -> None:
    case = next(c for c in p3["cases"] if c["role"] == "primary_detectable_gain")
    pair = case["pair_level_test_deltas"]
    base = case["baseline"]

    hero = _threshold_series(p2, "IRIDIUM 181", 8)
    exception = _threshold_series(p2, "IRIDIUM 177", 168)

    fig = plt.figure(figsize=(7.16, 2.40))
    gs = fig.add_gridspec(2, 2, width_ratios=[0.33, 0.67],
                          height_ratios=[0.90, 1.0], hspace=0.95, wspace=0.28)

    # --- (a) effect size ---------------------------------------------------
    ax = fig.add_subplot(gs[0, 0])
    # Same quantity the endpoint panel labels; use the full-precision field so
    # both panels are driven by one artifact value.
    est = case["delta_mae_hz"] * 1e3
    lo, hi = pair["ci_low_mhz"], pair["ci_high_mhz"]
    ax.axvline(0.0, color=INK, lw=1.0, ls=":", zorder=2)
    ax.plot([lo, hi], [0, 0], color=ACCENT, lw=2.2, solid_capstyle="butt",
            zorder=3)
    ax.plot([lo, hi], [0, 0], "|", color=ACCENT, ms=10, mew=1.7, zorder=4)
    ax.plot([est], [0], "o", color=ACCENT, ms=7.5, zorder=5)
    ax.set_ylim(-1.0, 1.0)
    ax.set_yticks([])
    ax.set_xlim(-4.9, 1.1)
    ax.set_xticks([-4, -2, 0])
    ax.tick_params(labelsize=8)
    ax.set_xlabel(r"$\Delta$MAE $=$ learned $-$ SGP4 [mHz]", fontsize=8.5)
    ax.set_title("(a) effect size, IRID-181 @8 h", fontsize=8.5)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)

    # --- (b) screening robustness -----------------------------------------
    ax = fig.add_subplot(gs[0, 1])
    xs = np.arange(len(SCREENS))
    ax.axhline(0.0, color=INK, lw=0.9, zorder=2)
    ax.axvline(SCREENS.index("1500"), color=INK, lw=0.8, ls=":", zorder=2)
    ax.plot(xs, hero, "o-", color=INK, ms=5, lw=1.7, zorder=3,
            label="IRID-181 @8 h")
    ax.plot(xs, exception, "s--", color=ACCENT, ms=5, lw=1.7, zorder=3,
            label="IRID-177 @168 h")
    ax.plot([1], [exception[1]], "o", ms=13, mfc="none", mec=ACCENT, mew=1.6,
            zorder=4)
    ax.set_xticks(xs)
    ax.set_xticklabels(SCREENS, fontsize=8)
    ax.set_ylim(-5.4, 9.4)
    ax.tick_params(labelsize=8)
    ax.set_xlabel(r"residual screen $\tau_s$ [Hz]", fontsize=8.5)
    ax.set_ylabel("held-out impr. [%]", fontsize=8.5)
    ax.legend(fontsize=7.5, frameon=False, loc="upper right",
              handlelength=1.8, borderpad=0.1, labelspacing=0.25)
    ax.set_title("(b) screening robustness", fontsize=8.5)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    # --- (c) endpoint relevance, wide, in stacked levels -------------------
    ax = fig.add_subplot(gs[1, :])
    gain = abs(case["delta_mae_hz"])
    sigma = base["sigma_residual_hz"]
    ftol = 500.0
    g_disp, s_disp = round(gain * 1e3, 2) / 1e3, round(sigma, 3)
    r1, r2 = round(s_disp / g_disp), round(ftol / s_disp)

    Y_OVERALL, Y_PAIR, Y_AXIS = 1.62, 0.86, 0.0
    ax.hlines(Y_AXIS, 1.6e-3, 1.2e3, color=INK, lw=1.0, zorder=1)

    def span(x0, x1, y, txt, cap=0.13):
        """Capped distance bar: a scale comparison, not a process arrow."""
        ax.hlines(y, x0, x1, color=INK, lw=0.8, zorder=2)
        ax.vlines([x0, x1], y - cap, y + cap, color=INK, lw=0.8, zorder=2)
        ax.annotate(txt, xy=(float(np.sqrt(x0 * x1)), y + 0.14), ha="center",
                    fontsize=8.5, color=INK)

    span(gain, ftol, Y_OVERALL, r"$\approx1.5\times10^{5}$ overall")
    span(gain, sigma, Y_PAIR, rf"$\times{r1}$")
    span(sigma, ftol, Y_PAIR, rf"$\times{r2}$")
    # level 3: the three points and what each one is
    for value, colour, label in (
            (gain, ACCENT, f"$|\\Delta$MAE$| = {gain*1e3:.2f}$ mHz\nabsolute gain"),
            (sigma, INK, f"$\\sigma_{{\\mathrm{{res}}}} = {sigma:.3f}$ Hz\nresidual spread"),
            (ftol, INK, "$F_{\\mathrm{tol}} = 500$ Hz\nrepresentative tolerance")):
        ax.plot([value], [Y_AXIS], "o", color=colour, ms=8, zorder=3)
        ax.plot([value, value], [Y_AXIS + 0.10, Y_PAIR - 0.06], color=INK,
                lw=0.5, ls=":", zorder=1)
        ax.annotate(label, xy=(value, Y_AXIS), xytext=(0, -10),
                    textcoords="offset points", ha="center", va="top",
                    fontsize=8, color=colour, linespacing=1.3)

    ax.set_xscale("log")
    ax.set_xlim(1.0e-3, 2.0e3)
    ax.set_ylim(-3.30, 2.55)
    ax.set_yticks([])
    ax.set_xticks([1e-3, 1e-2, 1e-1, 1e0, 1e1, 1e2, 1e3])
    ax.tick_params(labelsize=8, pad=3)
    ax.set_xlabel("frequency [Hz], logarithmic", fontsize=8.5, labelpad=2)
    ax.set_title("(c) endpoint relevance", fontsize=8.5, pad=6)
    for side in ("left", "right", "top"):
        ax.spines[side].set_visible(False)

    for ext, kw in (("pdf", {}), ("png", {"dpi": 220})):
        fig.savefig(HERE / f"fig_evidence_axes.{ext}", bbox_inches="tight", **kw)
    plt.close(fig)


def main() -> int:
    p2, p3, sens = _load()
    fig_decision_map(p2, sens)
    fig_evidence_axes(p2, p3)
    print("wrote fig_decision_map and fig_evidence_axes (pdf+png)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
