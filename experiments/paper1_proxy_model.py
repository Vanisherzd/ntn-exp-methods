"""
Paper 1 — shared software-only proxy model
==========================================
Common constants and proxy functions for the Paper-1 gap-closure analyses
(timing-offset sensitivity, control ablation, PGRL footprint).

SCOPE GUARDRAIL
---------------
Everything here is software-only and model-derived. No hardware, RF, UART,
packet decode, PER/PDR/CRC, gateway ACK, OTA, or live-satellite measurement is
involved. The TX-window "hit/miss" is an analytic guard-coverage proxy, NOT a
measured LR-FHSS packet outcome. The PGRL-vs-SGP4 separation reflects the
calibrated synthetic residual values used in exp2/exp3; the paper's headline
real-data finding (BLACK KITE) is that learning does NOT beat SGP4 at the tested
staleness and the evidence gate closes. These proxies characterise the control
mechanism *when the gate opens*, not a real-data PGRL-wins claim.

All constants are pulled from the existing committed experiments so the new
analyses stay numerically consistent with exp2 / exp3 / icc_main.tex.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

# Make `controller` importable when run from repo root.
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from controller.guard_band_policy import (
    adaptive_guard_time,
    guard_overhead_fraction,
    missed_opportunity_probability,
)
from controller.energy_model import total_opportunity_energy
from controller.doppler_precomp import C_LIGHT

# ── Physical / link constants (consistent with icc_main.tex §Evaluation) ───────
F_CARRIER_HZ   = 868e6     # representative Doppler-scaling carrier (paper §V)
V_ORBITAL_KMS  = 7.67      # ~ISS orbital speed [km/s]
V_ORBITAL_MS   = V_ORBITAL_KMS * 1000.0

# LR-FHSS bin-tolerance proxy (paper §IV: F_tol = 500 Hz, sub-kHz tolerance).
F_TOL_HZ       = 500.0

# ── Pass / energy scenario (consistent with exp2_guard_band_energy/config.yaml)─
PASS_DURATION_S = 240.0    # 400 km pass opportunity
BASE_GUARD_S    = 0.030    # ITU-minimum fixed guard [s]
K_SIGMA         = 3.0      # 3-sigma coverage factor
RX_CURRENT_MA   = 12.0
TX_CURRENT_MA   = 28.0     # (informational; tx_energy uses radiated power)
VOLTAGE_V       = 3.3
TX_POWER_DBM    = 14.0
TX_BURST_S      = 0.200    # representative LR-FHSS uplink burst on-air time [s]
RX_LISTEN_S     = 0.050    # representative beacon/downlink listen window [s]

# ── Residual-uncertainty configs (from exp2/exp3 calibration) ──────────────────
# Timing 1-sigma [s] per control config.
SIGMA_T_S = {
    "no_control":   2.000,   # no timing prediction; raw open-loop slot error
    "sgp4_only":    1.500,   # SGP4 mean prediction (exp2 sgp4_only)
    "pgrl_mean":    0.200,   # PGRL mean-only (exp2 pgrl_mean_only)
    "pgrl_uncert":  0.016,   # PGRL calibrated 3-sigma (exp2 pgrl_uncertainty)
}
# Residual Doppler 1-sigma [Hz] per compensation config (exp3 baselines).
SIGMA_F_HZ = {
    "no_comp":   20000.0,    # full one-way Doppler order @868 MHz (paper §III)
    "sgp4_comp":  2500.0,    # SGP4-based pre-comp residual (exp3)
    "pgrl_comp":   300.0,    # PGRL-based pre-comp residual (exp3, calibrated)
    "oracle":       10.0,    # perfect-knowledge floor (exp3)
}

# ── TLE-staleness → open-loop SGP4 along-track timing error ─────────────────────
# Documented rule-of-thumb: SGP4 along-track position error of a typical LEO grows
# ~1.5 km/day with TLE age (literature range 1-3 km/day). Timing error = along-track
# error / orbital speed. This is the open-loop (uncompensated) SGP4 staleness curve.
ALONG_TRACK_KM_PER_DAY = 1.5

# Real BLACK KITE held-out baseline Doppler MAE [Hz @ 868 MHz] vs TLE staleness
# (icc_main.tex Table tab:bk, BK1 target). Used as the empirically-grounded shape
# of SGP4 frequency-residual growth with staleness — NOT a Gaussian drift.
BK_STALENESS_H        = [8, 24, 48, 72, 96, 168]
BK_BASELINE_DOPPLER_HZ = [0.2430, 0.8161, 1.9433, 4.8947, 10.1153, 26.9243]


def sgp4_timing_sigma_from_age(tle_age_h: float) -> float:
    """Open-loop SGP4 along-track timing 1-sigma [s] at a given TLE age [h]."""
    days = tle_age_h / 24.0
    along_track_km = ALONG_TRACK_KM_PER_DAY * days
    return along_track_km / V_ORBITAL_KMS


def doppler_to_radial_velocity(doppler_hz: float) -> float:
    """Δv_r [m/s] from a Doppler residual [Hz]: Δv = Δf · c / f_c."""
    return doppler_hz * C_LIGHT / F_CARRIER_HZ


@dataclass
class WindowOutcome:
    """Analytic guard-coverage outcome for one TX-window config."""
    sigma_t_s: float
    guard_s: float
    miss_rate: float          # P(|timing offset| > guard)  — proxy
    hit_rate: float           # 1 - miss_rate
    guard_overhead: float     # guard / pass_duration
    energy_per_burst_j: float       # energy charged per attempted burst
    energy_per_success_j: float     # energy per *successful* burst


def evaluate_window(
    sigma_t_s: float,
    *,
    adaptive: bool = True,
    fixed_guard_s: float | None = None,
) -> WindowOutcome:
    """Analytic TX-window guard-coverage + energy proxy for a timing sigma.

    adaptive=True : guard = base + k·sigma_t  (uncertainty-aware policy)
    adaptive=False: guard = fixed_guard_s     (deterministic policy)
    """
    if adaptive:
        guard = adaptive_guard_time(BASE_GUARD_S, sigma_t_s, k=K_SIGMA)
    else:
        guard = fixed_guard_s if fixed_guard_s is not None else BASE_GUARD_S

    miss = missed_opportunity_probability(sigma_t_s, guard)
    hit = 1.0 - miss
    overhead = guard_overhead_fraction(guard, PASS_DURATION_S)

    e = total_opportunity_energy(
        guard_s=guard,
        rx_on_s=RX_LISTEN_S,
        tx_s=TX_BURST_S,
        rx_current_ma=RX_CURRENT_MA,
        tx_power_dbm=TX_POWER_DBM,
        voltage_v=VOLTAGE_V,
    )
    e_per_burst = e["total_j"]
    e_per_success = e_per_burst / hit if hit > 1e-9 else float("inf")
    return WindowOutcome(
        sigma_t_s=sigma_t_s,
        guard_s=guard,
        miss_rate=miss,
        hit_rate=hit,
        guard_overhead=overhead,
        energy_per_burst_j=e_per_burst,
        energy_per_success_j=e_per_success,
    )


def freq_miss_probability(sigma_f_hz: float, f_tol_hz: float = F_TOL_HZ) -> float:
    """P(|residual Doppler| > F_tol) for a zero-mean Gaussian residual — the
    frequency-miss (hop-bin miss) proxy of icc_main.tex §IV."""
    if sigma_f_hz <= 0:
        return 0.0
    return float(math.erfc(f_tol_hz / (sigma_f_hz * math.sqrt(2.0))))
