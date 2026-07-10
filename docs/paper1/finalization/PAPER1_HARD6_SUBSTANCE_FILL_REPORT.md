# Paper 1 — Hard-6 Substance-Fill Report

_Build: `tectonic paper/icc_main.tex` — SUCCESS; 0 overfull boxes, 0 undefined
refs/citations. No experiments run; no numbers changed; no hardware touched._

## Page count

**6 pages including references — hard-6 holds.** Page 6 is now intentional and
well-filled: left column = end of Sec. V + Fig. 4 sanity box + Conclusion and
Limitations; right column = complete references ending [13] near the bottom. No
large unexplained empty area remains; the small residual slack is the real
author-block buffer.

## What was added (substance, no filler)

### 1. Coverage-proxy derivation (Sec. III-B, new Eqs. (10)–(13))

Added a compact derivation chain **stated exactly as implemented** in
`experiments/paper1_proxy_model.py` / exp7 / exp8 (verified against source
before writing):

- adaptive guard: g_t = g_0 + kσ_t, k = 3 (`adaptive_guard_time`);
- miss proxies: P_t = Pr[|δ_t|>g_t] = erfc(g_t/(σ_t√2)),
  P_f = erfc(F_tol/(σ_f√2)) (`missed_opportunity_probability`,
  `freq_miss_probability`);
- joint success: S = (1−P_t)(1−P_f) (exp8 `evaluate_config`);
- energy: E_att = I_rx·V·(g_t+t_rx) + P_tx·t_tx, E_succ = E_att/S
  (`total_opportunity_energy`, exp7/exp8 division).

Includes the reviewer-facing explanation of Fig. 3's shape (adaptive guard pins
P_t at the 3σ floor erfc(3/√2)≈0.3% while E_att grows linearly with σ_t) and the
explicit note that Fig. 3(a,b) uses S = 1−P_t (timing-only) while Fig. 3(c,d)
uses Eq. (12) — matching the scripts' actual behaviour, not an invented
simplification.

### 2. Table II — "Proxy model and evaluation parameters"

New compact single-column table (10 rows): T_pass = 240 s; g_0 = 30 ms with
g_t = g_0+3σ_t; TX burst 14 dBm/200 ms; RX listen 50 ms, 12 mA @ 3.3 V;
F_tol = 500 Hz; P_t/P_f (Eq. 11); S and E_att/S (Eqs. 12–13); guard overhead
g_t/T_pass; TLE-age mapping ~1.5 km/day ÷ 7.67 km/s; γ = 0.95 with chronological
V. Referenced from Sec. IV-E (whose now-redundant inline parameter list was
replaced by the table reference — net prose shrink offsetting table cost).

### 3. Conclusion design rule (slightly extended)

Now names the three endpoint margins (TX timing guard, hop-bin margin, energy
policy) and ties them to Eqs. (10)–(13). No new claim.

## How Fig. 4 was reframed

Now a **compact measurement-path sanity-evidence box**, three sub-panels:

- (a) conducted setup schematic (NUCLEO-L476RG + LR1121 923.2 MHz/−17 dBm →
  50 dB att. + coax → USRP B210 RX2 A; "conducted only — no antenna, no OTA
  path");
- (b) evidence summary bullets: deterministic FW; TX-ON−TX-OFF 41.25 ± 0.36 dB
  (four 4 MS/s runs); 2 MS/s sanity 43.76 dB; no clipping/saturation; no packet
  decode / PER / PDR / OTA;
- (c) **small subordinate** max-hold spectrum inset (committed PNG pixels
  verbatim; no re-analysis).

Caption = the requested "Conducted measurement-path sanity check… It is not
packet, link-layer, or OTA validation." Fig. 3 remains the visually dominant
result; Fig. 4 reads as supporting sanity evidence.

## No-overclaim scan

**PASS** — 3 residual hits, all negations or future work ("explicitly below any
packet-level or over-the-air claim"; "not packet, link-layer, or OTA
validation"; "Packet-level conducted PER/PDR … are future work").

## Evidence integrity

- No numerical results changed; every equation added matches the released
  implementation line-for-line (formulas re-read from
  `paper1_proxy_model.py` / `run_control_ablation.py` before writing).
- BK negative result, gate definition, proxy results, conducted-IQ boundary all
  intact.

## Remaining blockers

1. **Author block placeholder** (pre-existing SUBMISSION BLOCKER) — page-6
   buffer reserved; re-check count after filling.
2. Optional: [7] ACM ToSN metadata human check (see `PAPER1_REFERENCE_AUDIT.md`).
3. Commits D–G still pending (`PAPER1_FINAL_COMMIT_PLAN.md`).
