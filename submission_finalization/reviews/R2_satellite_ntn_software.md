# R2 — SATELLITE / NTN SOFTWARE

**VERDICT: WEAK REJECT**

**One-sentence contribution (reviewer's words):** A 19-rule executable contract that treats
experimental validity as a per-commit gate rather than a protocol description, arguing that
chronological splitting constrains only row ordering and is blind to whether a past-dated
quantity was obtainable, whether a row exists, and what a learner's non-column state has seen.

## Findings

| # | severity | finding | status |
|---|---|---|---|
| F1 | **BLOCKER** | the 2/18 baseline was never executed; named artifact absent; Fig. 2's left column hand-drawn under a "3/3 environments" legend | **FIXED** `7035eb7` |
| F2 | MAJOR | row membership depends on `coarse_step_s`, an undeclared solver knob, inside the module offered as the fix for row-membership defects; `min_pass_s >= coarse_step_s` unenforced | OPEN |
| F3 | MAJOR | §V-A never states the label is model-derived rather than truth; calls fitted mean elements "observations" | OPEN |
| F4 | MAJOR | manoeuvres absent from paper, contract and toolkit — a second censoring mechanism that also breaks the reference premise | OPEN |
| F5 | MAJOR | `build_label` implements the outcome-dependent status its own docstring forbids | OPEN (also R1-10) |
| F6 | MAJOR | "every detector two-sided" false; L4.5 has no failing side and is only a key-presence check | OPEN (also R1-3) |
| F7 | MAJOR | HO4 does not exercise L2.4's extrapolation margin | OPEN (also R1-5) |
| F8 | MAJOR | L4.3's "mechanical check" depends on a caller-supplied `aggregated` boolean — self-report | OPEN |
| F9 | MINOR | LOC inflated by tracked duplicate; four dangling `salvage/` references remain | **PARTLY FIXED** `7035eb7` (duplicate removed; dangling refs OPEN) |
| F10 | MAJOR | "chronologically consistent" never given a reference frame; Fig. 3 caption not harmonised with Fig. 1's | OPEN |
| F11 | MINOR | L2.3's 3× late/early ratio cannot separate integrating state from ordinary orbital error growth; magic defaults undeclared | OPEN |
| F12 | MINOR | six small precision defects in the contract implementation | OPEN |
| F13 | MINOR | `refs.bib` entry-type hygiene; only one comms reference | OPEN |

**Top rejection argument:** same as R1 — a never-executed baseline in a paper about
falsifiability — compounded by the contract not having been applied to the artifact that
embodies it (F2, F5).

**R2's Q1–Q4 verdicts, which drive the framing decision:**
- Only **2 of 6** protected objects are satellite-specific: row membership as *generated*
  from predicted visibility, and the pass as the irreducible statistical unit. Both live in
  code comments rather than the paper.
- The two-clock problem **as stated** is a generic data-feed property. What is characteristic
  and unstated: one clock governs both feature availability *and* target existence, and the
  publication clock is itself partially unrecoverable.
- Too generic for a comms workshop **as written**; zero link-layer content. Becomes legitimate
  if the two load-bearing objects are promoted and the along-track-error-to-acquisition-window
  mechanism is stated qualitatively.
- Abstract sentence 1 makes an uncited empirical claim about NTN practice that may be false;
  an NTN reviewer may not recognise the premise as describing their field.

**Verified sound by R2:** framing discipline exemplary; every traceable headline number
reproduces exactly; pre-registration genuinely adversarial toward itself; L4.6's asymmetry
argument nice; geodetic normal correct (0.1427° at 24 N); threshold refinement correct, so
the "no sample below the mask" guarantee holds under a scalar mask; Fig. 1's L1.3 dotted fix
is correct and must survive to camera-ready.
