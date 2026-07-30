# Slides Build Report (Paper 1 finalization)

## Command

```bash
tectonic paper/slides_overview.tex
```

## Result

- **Status:** SUCCESS
- **Output:** `paper/slides_overview.pdf` (~206 KB)
- **Slide count:** **12** (16:9 beamer)
- **Unresolved refs/assets:** none — all `\includegraphics` resolve
  (`slide_figures/`, `figures/`, `figures_final/`, `assets_external/tabler/`)

## Final deck story (aligned with paper)

1. Title — new paper title; "Physics first. Evidence decides ML."; software-only scope line
2. Doppler pre-compensation risk — now explicitly *joint timing + frequency* risk
3. Dangerous intuition (training→deployment shift)
4. Physics-first framework (architecture)
5. Evidence-gate decision rule
6. Real BLACK KITE negative result (gate closes)
7. Negative evidence becomes fallback
8. Synthetic sanity check (gate opens only under systematic residual)
9. **NEW** Timing sensitivity (exp7 talk figure, software-only proxy scopefooter)
10. **NEW** Timing/frequency/PGRL ablation (exp8 talk figure; "PGRL bar = gate-open *synthetic* regime" in scopefooter)
11. **NEW** Conducted IQ-level evidence 923.2 MHz — replaced stale "Validation
    Roadmap" (which still said conducted IQ was "next"); setup + result cards
    (41.25 ± 0.36 dB, 43.76 dB control, artifact-masked 41.1 dB, before/after
    ~0.5 dB→41.1 dB, no clip/sat) + committed TX-ON/TX-OFF figure + visible claim
    boundary footer
12. Contributions — card 4 now "Conducted IQ-level evidence … no link-layer overclaim"

## Visual rules check

- Color scheme kept: PhysicsBlue #1F4E79 / MLOrange #C46A1A / GateGreen #2E7D32 /
  UnsafeRed #B23A3A / ScopeGray #666666; new talk figures use the same palette.
- "conducted IQ-level evidence" wording used; "RF validation" nowhere claimed.
- Claim boundary visible on the hardware slide (gray scopefooter).
- Fixed during finalization: clipped takeaways on slides 9–10 (figure height
  0.66→0.56 textheight), colliding ablation x-labels (short talk labels), value
  labels grazing the axis top (log-axis headroom).

## Remaining manual fixes (optional)

- Slide 9 annotation "TLE 168 h" sits close to the curve — legible, could nudge.
- Title slide overview graphic still shows the tagline pipeline only; could add a
  timing/frequency cue (cosmetic).
- No speaker notes; add if the venue wants them.
