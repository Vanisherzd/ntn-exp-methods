"""Event-driven visible-pass discovery and fixed within-pass sampling.

Extracted from a stopped research line. The scientific results of that line are
invalid (see ../../../archive/KNOWN_INVALID_RESULTS.md); this scheduling machinery
is not, and is the single most reusable piece.

Design rule it encodes: transmissions are GENERATED from passes predicted by the
state the endpoint actually holds. They are never sampled on a UTC grid and filtered
by elevation afterwards -- doing so left 96.58 % of one dataset below the horizon,
with the residual 5.6x smaller than on visible geometry.

No orbital, carrier or ground-station constant is baked in; every one is a parameter.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np

WGS84_A_M = 6378137.0
WGS84_E2 = 0.006694379990141317
OMEGA_EARTH = 7.292115e-5
C_LIGHT = 299792458.0


@dataclass(frozen=True)
class Station:
    """Fixed ground station. Elevation uses the GEODETIC normal, not the geocentric
    radius -- the two differ by f*sin(2*lat), which is 0.143 deg at 24 deg N and put
    0.27 % of one historical dataset below its own declared mask."""
    lat_deg: float
    lon_deg: float
    alt_m: float

    def ecef_position_m(self) -> np.ndarray:
        lat, lon = math.radians(self.lat_deg), math.radians(self.lon_deg)
        n = WGS84_A_M / math.sqrt(1.0 - WGS84_E2 * math.sin(lat) ** 2)
        return np.array([(n + self.alt_m) * math.cos(lat) * math.cos(lon),
                         (n + self.alt_m) * math.cos(lat) * math.sin(lon),
                         (n * (1.0 - WGS84_E2) + self.alt_m) * math.sin(lat)])

    def ecef_geodetic_normal(self) -> np.ndarray:
        lat, lon = math.radians(self.lat_deg), math.radians(self.lon_deg)
        return np.array([math.cos(lat) * math.cos(lon),
                         math.cos(lat) * math.sin(lon), math.sin(lat)])


@dataclass(frozen=True)
class PassFinderConfig:
    """Every setting is declared, including the numerical ones.

    `mask_deg` and `min_pass_s` define the visibility CRITERION -- what counts as a
    usable pass. `coarse_step_s`, `bisect_tol_s` and `bisect_max_iter` are SOLVER
    settings of the interval finder: they determine how accurately the criterion's
    boundaries are located, and they belong in the provenance manifest for that
    reason. They do not define the criterion, but they are not free of it either --
    the schedule is a numerical solution, and claiming otherwise would be the same
    kind of undeclared dependence the contract exists to catch.

    Two consequences are enforced below rather than assumed:

    - A pass shorter than the coarse step can fall entirely between two grid points
      and be missed, so `coarse_step_s <= min_pass_s` is required. The historical
      implementation justified a 60 s step with a false claim ('a 10 deg pass lasts
      >= 4 min') while the true minimum above-mask pass measured 15 s -- so the
      criterion, not folklore, has to bound the solver.
    - `bisect_tol_s` bounds boundary ERROR, not boundary VALUE: refinement returns
      the above-threshold side of the bracket, so the reported extent is contained
      within the true pass to within the tolerance rather than straddling it.

    `test_scheduler_convergence_over_declared_step_range` exercises the declared
    range and asserts stability of the recovered extent.
    """
    mask_deg: float
    coarse_step_s: float = 60.0
    bisect_tol_s: float = 1.0
    bisect_max_iter: int = 30
    min_pass_s: float = 60.0

    def __post_init__(self) -> None:
        if self.coarse_step_s > self.min_pass_s:
            raise ValueError(
                f"coarse_step_s={self.coarse_step_s} exceeds min_pass_s="
                f"{self.min_pass_s}: a shortest-admissible pass could fall between "
                "two grid points and never be found")
        if self.bisect_tol_s <= 0 or self.bisect_max_iter < 1:
            raise ValueError("bisect_tol_s must be > 0 and bisect_max_iter >= 1")


def gmst_rad(jd: np.ndarray, fr: np.ndarray) -> np.ndarray:
    d = (jd + fr) - 2451545.0
    return np.radians((280.46061837 + 360.98564736629 * d) % 360.0)


def jd_split(unix_s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    jt = np.asarray(unix_s, dtype=float) / 86400.0 + 2440587.5
    jd = np.floor(jt - 0.5) + 0.5
    return jd, jt - jd


def station_teme_km(st: Station, jd: np.ndarray, fr: np.ndarray
                    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(position_km, velocity_km_s, geodetic_up_unit) in TEME, vectorized over time."""
    r_ecef = st.ecef_position_m()
    up_ecef = st.ecef_geodetic_normal()
    th = gmst_rad(jd, fr)
    ct, st_ = np.cos(th), np.sin(th)

    def rot(v):
        return np.stack([ct * v[0] - st_ * v[1], st_ * v[0] + ct * v[1],
                         np.full_like(ct, v[2])], axis=1)

    r = rot(r_ecef) * 1e-3
    up = rot(up_ecef)
    v = np.stack([-OMEGA_EARTH * r[:, 1], OMEGA_EARTH * r[:, 0],
                  np.zeros_like(ct)], axis=1)
    return r, v, up


def look_angles(propagate: Callable[[np.ndarray, np.ndarray], tuple],
                st: Station, unix_s: np.ndarray, carrier_hz: float
                ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(elevation_deg, range_km, doppler_hz, ok).

    `propagate(jd, fr) -> (err, r_km, v_km_s)` is any propagator with the sgp4
    array signature. Nothing here reads a reference or truth trajectory.
    """
    jd, fr = jd_split(np.atleast_1d(unix_s))
    err, r, v = propagate(jd, fr)
    r, v = np.asarray(r, dtype=float), np.asarray(v, dtype=float)
    gr, gv, up = station_teme_km(st, jd, fr)
    dr = r - gr
    rm = np.linalg.norm(dr, axis=1)
    ok = (np.asarray(err) == 0) & (rm > 1.0) & np.isfinite(rm)
    rh = dr / np.where(ok, rm, 1.0)[:, None]
    el = np.degrees(np.arcsin(np.clip(np.einsum("ij,ij->i", rh, up), -1.0, 1.0)))
    rr = np.einsum("ij,ij->i", v - gv, rh)
    return el, rm, -carrier_hz * rr * 1e3 / C_LIGHT, ok


def find_passes(propagate, st: Station, t0: float, t1: float,
                cfg: PassFinderConfig) -> list[tuple[float, float]]:
    """Predicted-visible intervals in [t0, t1], from the held state only.

    Coarse vectorized scan locates sign changes of (elevation - mask); each crossing
    is bisected. Both crossings are refined to the ABOVE-threshold side of the final
    bracket, so a sample placed at a normalized offset inside the interval can never
    fall below the mask through bisection error.

    The historical implementation passed the exit bracket reversed, so the loop guard
    was immediately true and the exit was never refined -- returning the coarse
    midpoint and placing the last sample up to one coarse step past the true exit.
    """
    n = max(int(math.ceil((t1 - t0) / cfg.coarse_step_s)) + 1, 2)
    grid = t0 + np.arange(n) * cfg.coarse_step_s
    grid = grid[grid <= t1]
    if grid.size < 2:
        return []
    el, _, _, ok = look_angles(propagate, st, grid, 1.0)
    f = np.where(ok, el - cfg.mask_deg, -1e3)

    def bisect(t_below: np.ndarray, t_above: np.ndarray) -> np.ndarray:
        """Order-agnostic in time. Returns the above-threshold side."""
        lo, hi = np.asarray(t_below, dtype=float).copy(), np.asarray(t_above, dtype=float).copy()
        for _ in range(cfg.bisect_max_iter):
            if np.all(np.abs(hi - lo) <= cfg.bisect_tol_s):
                break
            m = 0.5 * (lo + hi)
            el_m, _, _, ok_m = look_angles(propagate, st, m, 1.0)
            above = ok_m & (el_m - cfg.mask_deg >= 0.0)
            hi = np.where(above, m, hi)
            lo = np.where(above, lo, m)
        return hi

    ui = np.flatnonzero((f[:-1] < 0.0) & (f[1:] >= 0.0))
    di = np.flatnonzero((f[:-1] >= 0.0) & (f[1:] < 0.0))
    pairs = [(int(i), int(di[di > i][0])) for i in ui if np.any(di > i)]
    if not pairs:
        return []
    entry = bisect(grid[[p[0] for p in pairs]], grid[[p[0] + 1 for p in pairs]])
    exit_ = bisect(grid[[p[1] + 1 for p in pairs]], grid[[p[1] for p in pairs]])
    return [(float(a), float(b)) for a, b in zip(entry, exit_)
            if b - a >= cfg.min_pass_s]


def sample_passes(intervals: Sequence[tuple[float, float]],
                  offsets: Sequence[float]) -> list[tuple[int, int, float]]:
    """(pass_index, offset_index, t) at fixed normalized offsets.

    WARNING, measured: within a single pass, elevation and range trace one smooth
    unimodal curve, so offsets CANNOT be decorrelated by choosing their positions.
    Two independent attempts measured 0.9986-0.9997 correlation between offset pairs.
    Treat within-pass samples as REPEATED MEASURES and take the pass as the
    independent unit; geometric diversity comes from across-pass variation.
    """
    out: list[tuple[int, int, float]] = []
    for p, (a, b) in enumerate(intervals):
        span = b - a
        for k, frac in enumerate(offsets):
            out.append((p, k, a + frac * span))
    return out


def pass_id(object_key: str, scenario: str, episode: int, pass_index: int) -> str:
    return f"{object_key}|{scenario}|{episode}|{pass_index}"


def tx_id(pass_identifier: str, offset_index: int) -> str:
    return f"{pass_identifier}|{offset_index}"
