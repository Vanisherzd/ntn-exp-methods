#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26", "sgp4>=2.23"]
# ///
"""Phase-3 endpoint-value closure (Paper 1+).

Question: does a statistically detectable ~2 % residual improvement produce any
practically meaningful endpoint-budget reduction at the ACTUAL real-data
residual scale?

Primary case  : IRIDIUM 181 @ 8 h  (robust ~1.9 % improvement, below the margin)
Contrast case : SENTINEL-6B @ 96 h (clearly harmful, +30.6 % degradation)

Uses the real held-out residual predictions from those cells at the
preregistered 1500 Hz screen. Residuals are NOT rescaled and the synthetic
gate-open residual scale is NOT used.

Endpoint proxy chain and constants are taken from the committed Paper 1
artifacts (`experiments/exp7_timing_sensitivity/results.json`), back-derived and
verified to reproduce its `energy_per_success_j` exactly:

  g_t   = g0 + k*sigma_t,           g0 = 30 ms, k = 3
  P_t   = erfc(g_t / (sigma_t*sqrt2))
  P_f   = erfc(F_tol / (sigma_f*sqrt2))
  S     = (1 - P_t)(1 - P_f)
  E_att = I_rx*V*(g_t + t_rx) + P_tx*t_tx
  E_suc = E_att / S
plus the frequency-domain proxies of Paper 1 Sec. III-C:
  guard g = 2*p99(|e|),  outage rho = Pr(|e| > F_tol),
  E_proxy ~ (1 + alpha_g * g/B)(1 + rho)

Software/model-derived endpoint-budget proxy only. No packet-level, error-rate,
receiver-acknowledgement, over-the-air or on-orbit claim.
reference_is_measured_truth = false.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import run_multisat_generalization_matrix as pipeline  # noqa: E402

# --- constants back-derived from experiments/exp7_timing_sensitivity/results.json
G0_S = 0.030
K_SIGMA = 3.0
T_PASS_S = 240.0
T_RX_S = 0.050
I_RX_A = 0.012
V_VOLT = 3.3
P_TX_W = 10.0 ** (14.0 / 10.0) / 1000.0        # 14 dBm
T_TX_S = 0.200
# Paper Table III: TLE age -> sigma_t via ~1.5 km/day of along-track drift
DRIFT_KM_PER_DAY = 1.5
ORBITAL_SPEED_KM_S = 7.67

CASES: tuple[tuple[int, int, str], ...] = (
    (56726, 8, "primary_detectable_gain"),
    (66514, 96, "contrast_clearly_harmful"),
)


def sigma_t_for_band(band_h: float) -> float:
    return (DRIFT_KM_PER_DAY * (band_h / 24.0)) / ORBITAL_SPEED_KM_S


def log10_erfc_upper_bound(z: float) -> float:
    """Rigorous log10 upper bound on erfc(z) for z > 0.

    erfc(z) <= exp(-z^2) / (z*sqrt(pi))  for z > 0, so
    log10 erfc(z) <= (-z^2 - ln(z*sqrt(pi))) / ln(10).
    The matching lower bound differs by log10(1 - 1/(2z^2)), which is < 1e-6 of
    the value for the z encountered here, so the bound is effectively exact.
    """
    if z <= 0:
        return 0.0
    return (-(z * z) - math.log(z * math.sqrt(math.pi))) / math.log(10.0)


def endpoint_proxies(err: np.ndarray, band_h: float, args) -> dict[str, Any]:
    """Endpoint budget proxies for one branch's held-out error sample.

    Sigma naming, kept explicit so no denominator is ambiguous:
      sigma_residual_hz         = std of the held-out inter-TLE residual error
      f_tol_over_sigma_residual = F_tol / sigma_residual   (a count of sigmas)
      erfc_argument             = F_tol / (sigma_residual*sqrt2)
    The erfc argument is NOT a sigma count; it is smaller by a factor sqrt(2).
    Timing dispersion sigma_t_s lives on a separate axis and is never combined
    into a single sigma; P_t and P_f are computed independently and multiplied.
    """
    abs_err = np.abs(err)
    sigma_f = float(np.std(err))
    guard_hz = 2.0 * float(np.percentile(abs_err, 99))
    outage = float(np.mean(abs_err > args.f_tol_hz))

    sigma_t = sigma_t_for_band(band_h)
    g_t = G0_S + K_SIGMA * sigma_t
    p_t = math.erfc(g_t / (sigma_t * math.sqrt(2.0)))
    z_f = args.f_tol_hz / (sigma_f * math.sqrt(2.0)) if sigma_f > 0 else math.inf
    # erfc underflows to 0.0 in double past z ~ 26.6; keep the log-domain value
    # so "zero" is never confused with "unresolved".
    p_f = math.erfc(z_f) if z_f < 26.0 else 0.0
    log10_p_f = log10_erfc_upper_bound(z_f)
    s_joint = (1.0 - p_t) * (1.0 - p_f)
    e_att = I_RX_A * V_VOLT * (g_t + T_RX_S) + P_TX_W * T_TX_S
    e_succ = e_att / s_joint

    return {
        "mae_hz": float(np.mean(abs_err)),
        "p95_hz": float(np.percentile(abs_err, 95)),
        "p99_hz": float(np.percentile(abs_err, 99)),
        "sigma_residual_hz": sigma_f,
        "guard_proxy_hz": guard_hz,
        "guard_fraction_of_hop_bw": guard_hz / args.hop_bandwidth_hz,
        "outage_proxy": outage,
        "energy_overhead_proxy": (
            1.0 + args.alpha_g * guard_hz / args.hop_bandwidth_hz
        ) * (1.0 + outage),
        "sigma_t_s": sigma_t,
        "timing_guard_s": g_t,
        "p_timing_miss": p_t,
        "f_tol_over_sigma_residual": (
            args.f_tol_hz / sigma_f if sigma_f > 0 else math.inf
        ),
        "erfc_argument": z_f,
        "p_freq_miss": p_f,
        "log10_p_freq_miss_upper_bound": log10_p_f,
        "p_freq_miss_double_underflow": bool(z_f >= 26.0),
        "joint_success_proxy": s_joint,
        "energy_per_attempt_j": e_att,
        "energy_per_success_j": e_succ,
    }


def required_sigma_f(target_pf: float, f_tol_hz: float) -> float:
    """sigma_f at which the frequency-miss proxy would reach target_pf."""
    lo, hi = 1e-6, 1e7
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        z = f_tol_hz / (mid * math.sqrt(2.0))
        pf = math.erfc(z) if z < 26.0 else 0.0
        if pf < target_pf:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


def run_case(sat, band: int, role: str, args) -> dict[str, Any]:
    gs = (args.gs_lat, args.gs_lon, args.gs_alt)
    accepted, _, _ = pipeline.build_pairs(
        sat, band, args.reject_hz, gs, args.carrier_hz
    )
    t_tr, t_va = pipeline.split_boundaries(sat)
    train, val, test = pipeline.split_pairs(accepted, t_tr, t_va)
    x_tr, y_tr = pipeline.stack(train)
    x_va, y_va = pipeline.stack(val)
    models = pipeline.fit_correctors(x_tr, y_tr, x_va, y_va)
    val_agg = {
        n: pipeline.aggregate_pair_metrics(val, models[n], args.f_tol_hz)
        for n in pipeline.LEARNED_MODELS + ("zero",)
    }
    selected = min(pipeline.LEARNED_MODELS, key=lambda n: val_agg[n]["mae"])
    gates = pipeline.evaluate_gates(val_agg["zero"], val_agg[selected], args)

    x_te, y_te = pipeline.stack(test)
    err_base = y_te - models["zero"](x_te)      # = y_te, SGP4 makes no correction
    err_learn = y_te - models[selected](x_te)

    base = endpoint_proxies(err_base, band, args)
    learn = endpoint_proxies(err_learn, band, args)

    # Pair-level deltas: the campaign's statistical unit, recorded so the
    # detectability figure is drawn from the same numbers as the sign test and
    # the bootstrap rather than from a re-run.
    pair_base = pipeline.per_pair_mae(test, models["zero"])
    pair_learn = pipeline.per_pair_mae(test, models[selected])
    pair_delta = (pair_learn - pair_base).tolist()
    deltas = {
        f"delta_{k}": learn[k] - base[k]
        for k in ("mae_hz", "p95_hz", "p99_hz", "guard_proxy_hz", "outage_proxy",
                  "energy_overhead_proxy", "energy_per_success_j",
                  "joint_success_proxy", "log10_p_freq_miss_upper_bound")
    }
    rel = {
        f"rel_{k}_pct": (
            100.0 * (learn[k] - base[k]) / base[k] if base[k] not in (0, 0.0) else 0.0
        )
        for k in ("mae_hz", "p95_hz", "p99_hz", "guard_proxy_hz",
                  "energy_overhead_proxy", "energy_per_success_j")
    }
    paired = pipeline.paired_pair_level_test(
        test, models["zero"], models[selected], args.f_tol_hz,
        args.n_boot, args.seed,
    )
    pair_stats = {
        "n_pairs": int(len(pair_delta)),
        "delta_hz": [round(v, 12) for v in pair_delta],
        "win_rate": paired.get("pair_win_rate", 0.0),
        "mean_delta_hz": paired.get("mean_pair_mae_delta_hz", 0.0),
        "ci_low_mhz": round(1e3 * paired.get("boot_ci_low_hz", 0.0), 4),
        "ci_high_mhz": round(1e3 * paired.get("boot_ci_high_hz", 0.0), 4),
        "sign_test_p": paired.get("sign_test_p"),
    }

    return {
        "role": role,
        "satellite": sat.key,
        "satellite_name": sat.name,
        "staleness_h": band,
        "reject_hz": args.reject_hz,
        "selected_model": selected,
        "gate_decision": gates[args.primary_gate],
        "n_test_pairs": len(test),
        "n_test_samples": int(err_base.size),
        "degradation_pct": 100.0
        * (learn["mae_hz"] - base["mae_hz"])
        / base["mae_hz"],
        "improvement_pct": -100.0
        * (learn["mae_hz"] - base["mae_hz"])
        / base["mae_hz"],
        "baseline": base,
        "learned": learn,
        "pair_level_test_deltas": pair_stats,
        **deltas,
        **rel,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tle-dir", type=Path, default=ROOT / "dataraw" / "spacetrack")
    parser.add_argument("--gs-lat", type=float, default=24.0)
    parser.add_argument("--gs-lon", type=float, default=121.0)
    parser.add_argument("--gs-alt", type=float, default=100.0)
    parser.add_argument("--carrier-hz", type=float, default=868e6)
    parser.add_argument("--reject-hz", type=float, default=1500.0)
    parser.add_argument("--gamma", type=float, default=0.95)
    parser.add_argument("--f-tol-hz", type=float, default=500.0)
    parser.add_argument("--alpha-g", type=float, default=1.0)
    parser.add_argument("--hop-bandwidth-hz", type=float, default=137e3)
    parser.add_argument("--primary-gate", default="mae")
    parser.add_argument("--n-boot", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260727)
    parser.add_argument("--out-dir", type=Path, default=HERE / "phase3_endpoint_value")
    args = parser.parse_args(argv)

    sats = {s.norad: s for s in pipeline.discover_satellites(args.tle_dir)}
    cases = [run_case(sats[n], b, role, args) for n, b, role in CASES]

    scale = {
        f"sigma_residual_hz_for_p_freq_miss_{t:g}": required_sigma_f(t, args.f_tol_hz)
        for t in (1e-6, 1e-3, 1e-2)
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "endpoint_value_results.json").write_text(
        json.dumps(
            {
                "metadata": {
                    "campaign": "paper1_plus_phase3_endpoint_value",
                    "question": (
                        "does a statistically detectable ~2% residual improvement "
                        "produce any practically meaningful endpoint-budget "
                        "reduction at the actual real-data residual scale?"
                    ),
                    "residuals_rescaled": False,
                    "synthetic_gate_open_scale_used": False,
                    "proxy_constants_source": (
                        "experiments/exp7_timing_sensitivity/results.json, "
                        "back-derived and verified to reproduce energy_per_success_j"
                    ),
                    "constants": {
                        "g0_s": G0_S, "k_sigma": K_SIGMA, "t_pass_s": T_PASS_S,
                        "t_rx_s": T_RX_S, "i_rx_a": I_RX_A, "v_volt": V_VOLT,
                        "p_tx_w": P_TX_W, "t_tx_s": T_TX_S,
                        "f_tol_hz": args.f_tol_hz,
                        "hop_bandwidth_hz": args.hop_bandwidth_hz,
                        "alpha_g": args.alpha_g,
                    },
                    "scope": (
                        "software/model-derived endpoint-budget proxy; no packet, "
                        "PER, PDR, error-rate, receiver-acknowledgement, "
                        "over-the-air or on-orbit claim"
                    ),
                    "reference_is_measured_truth": False,
                },
                "residual_scale_required_for_frequency_branch_to_matter": scale,
                "cases": cases,
            },
            indent=2,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    for c in cases:
        b, ln = c["baseline"], c["learned"]
        print(f"\n=== {c['satellite_name']} @ {c['staleness_h']}h  ({c['role']}) ===")
        print(f"  gate={c['gate_decision']}  model={c['selected_model']}  "
              f"pairs={c['n_test_pairs']}  degradation={c['degradation_pct']:+.3f}%")
        print(f"  {'metric':28} {'SGP4':>16} {'learned':>16} {'delta':>16}")
        for k, lab in (
            ("mae_hz", "MAE [Hz]"), ("p95_hz", "p95 |e| [Hz]"),
            ("p99_hz", "p99 |e| [Hz]"), ("sigma_residual_hz", "sigma_residual [Hz]"),
            ("guard_proxy_hz", "guard 2*p99 [Hz]"),
            ("outage_proxy", "outage Pr(|e|>Ftol)"),
            ("log10_p_freq_miss_upper_bound", "log10 P_f (upper bd)"),
            ("joint_success_proxy", "S joint success"),
            ("energy_overhead_proxy", "E_proxy overhead"),
            ("energy_per_success_j", "E/success [J]"),
        ):
            print(f"  {lab:28} {b[k]:>16.6g} {ln[k]:>16.6g} {ln[k]-b[k]:>+16.6g}")
        print(f"  F_tol / sigma_residual : SGP4 {b['f_tol_over_sigma_residual']:.1f} "
              f"sigma, learned {ln['f_tol_over_sigma_residual']:.1f} sigma")
        print(f"  erfc argument          : SGP4 {b['erfc_argument']:.1f}, "
              f"learned {ln['erfc_argument']:.1f}  (= sigma count / sqrt2)")
    print("\n=== residual scale required before the frequency branch matters ===")
    for k, v in scale.items():
        print(f"  {k}: sigma_f = {v:.2f} Hz")
    return 0


if __name__ == "__main__":
    sys.exit(main())
