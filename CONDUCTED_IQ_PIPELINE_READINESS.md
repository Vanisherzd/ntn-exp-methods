# Conducted IQ Pipeline Readiness Review (Agent 5)

Date: 2026-06-26
Reviewer scope: static review + `py_compile` + `--help` only. No RF capture, no USRP TX,
no serial port access performed. `scripts/lr1121_serial_logger.py` reviewed statically;
its `--help` was confirmed hardware-safe (argparse exits inside `parse_args()` before any
`serial.Serial()` open).

Goal config reference: 923200000 Hz, lowest TX power, conducted-only, attenuation >= 50 dB.

## Verdict summary

| Script | py_compile | --help (HW-safe) | Over-claim risk | Verdict |
| --- | --- | --- | --- | --- |
| scripts/usrp_rx2a_capture.py | OK | OK | none (RX-only, no detection logic) | READY |
| scripts/analyze_conducted_iq.py | OK | OK | MEDIUM (max-bin delta statistic) | READY w/ caveat |
| scripts/run_conducted_iq_session.py | OK | OK | LOW (inherits analyzer statistic) | READY |
| scripts/run_conducted_iq_debug_scan.py | OK | OK | LOW (inherits analyzer statistic) | READY |
| scripts/lr1121_serial_logger.py | OK | OK | none (read-only, never writes port) | READY |

All five are READY to run only after deterministic board TX is confirmed by the operator.
None of them falsely assume TX is present (see "TX-presence handling" below).

## 1. TX-presence handling (no false assumption of TX)

- `run_conducted_iq_session.py` and `run_conducted_iq_debug_scan.py` both capture a TX-OFF
  ("noise") segment first, then a TX-ON segment, and compute the difference. If the board
  is silent, the result is correctly reported as weak / not-visible and the recommended
  next step lists debug targets ("LR1121 not actually transmitting during capture", "wrong
  RF port", "firmware TX frequency mismatch", "TX timing missed the capture window", etc.).
- TX enable/disable is operator-driven (`manual-countdown`) or via explicit external command
  (`--tx-control command` + `--tx-on-cmd`/`--tx-off-cmd`). The scripts never assert that TX
  is on; they only prompt/countdown and then measure.
- `--yes` one-shot mode is gated behind four explicit operator confirmations
  (`--confirm-board-freq`, `--confirm-hardware-ready`, `--confirm-lowest-tx-power`,
  `--confirm-conducted-only`) and a board-freq/`--freq` match check (<=0.5 Hz). This is a
  correct "confirm deterministic board TX first" gate.
- `usrp_rx2a_capture.py` is hard-constrained to RX-only: channel 0 only, antenna RX2 only,
  `tx_configured: False` recorded in metadata, prohibitions list includes "No USRP TX".

## 2. LR1131 -> LR1121 wording

- `grep "LR1131" scripts/*.py` => NO matches. All source files are clean and use "LR1121".
- LR1131 appears ONLY inside stale compiled bytecode:
  `scripts/__pycache__/analyze_conducted_iq.cpython-314.pyc` and
  `scripts/__pycache__/usrp_rx2a_capture.cpython-314.pyc`. These were compiled from an
  earlier version of the source that has since been corrected. They are NOT source and are
  not generated into any report.
- `__pycache__/` is gitignored (`.gitignore` line 8) and `git check-ignore` confirms the
  stale `.pyc` is ignored, so the obsolete LR1131 strings cannot be committed.
- LR1121 occurrence counts in current source: session=23, debug_scan=15, capture=5,
  analyze=4, serial_logger=1.

Conclusion: NO LR1131->LR1121 fix required. No source edits were applied.
(Optional hygiene: `rm -rf scripts/__pycache__` to drop the stale bytecode; not required
for correctness and not done here to avoid unsolicited changes.)

## 3. Over-claim risk assessment

Good guardrails already present (no link-level over-claim):
- No script emits a literal `signal_detected: true`. The summary file is named
  `signal_detection_summary.json` but its content is hedged booleans only.
- Every report/metadata block carries explicit non-claims: "Not packet decoding", "No
  link-layer outcome claim", "No live-satellite claim", "Not OTA", "conducted IQ-level
  capture only".
- `usable_for_conducted_iq_evidence` and `cfo_hop_center_proxy_candidate` are additionally
  gated on `not clipping_warning and not saturation_warning`; the CFO candidate requires a
  stronger >=10 dB delta. Clipping/saturation trigger early stop.

MEDIUM risk (statistical), `analyze_conducted_iq.py` `summarize()`:
- `txon_minus_noise_db = float(np.max(tx_db - noise_db))` is the MAX over all FFT bins of
  the per-bin TX-ON-minus-TX-OFF difference. The max of many noisy bins is positively
  biased: for two independent noise captures (TX truly silent), a single bin can exceed the
  fixed `VISIBLE_DELTA_DB = 6.0` threshold by chance, which would set `txon_visible = True`
  and propagate to `usable_for_conducted_iq_evidence`. This is the one place the pipeline
  could mislabel noise-vs-noise fluctuation as "TX-ON visible".
- Existing partial guard `likely_artifact_warning` only fires when the TX peak offset is
  within 1 kHz of the noise peak offset AND delta < 3 dB, so it does not cover the
  >=6 dB-by-chance case.

Recommended (do not rewrite wholesale):
1. Make visibility noise-statistics-aware: compare the TX-ON peak against the TX-OFF
   distribution at/near the same bin (e.g. peak excess over noise mean + k*std), instead of
   a single global max-bin delta vs a flat 6 dB.
2. Require the TX-ON peak offset to be reproducible / near the expected hop-center before
   declaring `txon_visible`, rather than wherever the global max lands.
3. Optionally raise the bare `txon_visible` bar or treat 6-10 dB as "inconclusive" so that
   only the >=10 dB CFO-candidate path counts as positive evidence.

These are recommendations only; no detection-logic edits were applied.

## 4. Raw IQ gitignore confirmation

`git check-ignore -q` confirmed IGNORED:
- `hardware_conducted_iq/**/*.npy`  (e.g. noise/txon `.npy`)  -> IGNORED
- `hardware_conducted_iq/**/*.fc32`                            -> IGNORED
- `hardware_conducted_iq/**/*.cfile`                           -> IGNORED
- `*.fc32` / `*.cfile` global rules also present (lines 58-59).
- `scripts/__pycache__/*.pyc`                                  -> IGNORED (via `__pycache__/`)

Raw IQ artifacts cannot be accidentally committed. Confirmed, not re-architected.

## 5. py_compile results

All five compiled cleanly with `.venv/bin/python -m py_compile`:
- run_conducted_iq_session.py  -> OK
- run_conducted_iq_debug_scan.py -> OK
- usrp_rx2a_capture.py          -> OK
- analyze_conducted_iq.py       -> OK
- lr1121_serial_logger.py       -> OK

## 6. --help check results (hardware-safe)

For all five, argparse handles `--help` and raises SystemExit inside `parse_args()` before
any device/port/USRP access. Verified in source first for the serial logger (`parse_args()`
is the first call in `main()`, before `serial.Serial(...)`). All returned exit 0:
- run_conducted_iq_session.py --help  -> HELP OK
- run_conducted_iq_debug_scan.py --help -> HELP OK
- usrp_rx2a_capture.py --help          -> HELP OK
- analyze_conducted_iq.py --help       -> HELP OK
- lr1121_serial_logger.py --help       -> HELP OK (no port opened)

## 7. Changes made by this review

None. No source files edited (LR1131 was not present in source). No LR1131->LR1121 patch
was needed.

`git diff --stat`:
```
 .gitignore | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)
```
NOTE: this `.gitignore` modification pre-existed this review (present in `git status` at
session start) and was NOT made by Agent 5. Agent 5 made zero file modifications to the
repository (only this readiness report was written).
