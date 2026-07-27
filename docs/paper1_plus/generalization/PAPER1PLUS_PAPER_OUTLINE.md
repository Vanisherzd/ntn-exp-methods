# Paper 1+ Outline (Phase 9, provisional)

Date: 2026-07-27
Status: **skeleton only. The story is deliberately not chosen.** The framing
depends on which Phase 8 case occurs, and no data exists yet. Titles below are
placeholders per case, not decisions.

Frozen dependency: Paper 1 at `b529c5e`, not edited.

---

## Fixed regardless of outcome

These parts are the same in all four cases, because they describe the method,
not the finding.

### Abstract skeleton

> Endpoint terminals for LR-FHSS direct-to-satellite IoT pre-compensate Doppler
> from a stale TLE. Whether a learned inter-TLE residual correction should ever
> be deployed is a per-satellite decision, and prior work — including our own —
> evaluated it on a single object under a protocol that differed between the
> target-specific and transfer cases. We build a unified, pair-level,
> validation-gated protocol and apply it to **N** LEO satellites across **M**
> orbital regimes, producing an ordered train-source × deploy-target
> generalization matrix. ⟨case-specific finding⟩. All results are model-derived
> inter-TLE residuals (`reference_is_measured_truth = false`); no packet,
> error-rate, receiver-acknowledgement, over-the-air, or on-orbit result is
> claimed.

### Sec. II — Unified protocol *(the methodological contribution, case-independent)*

1. Two split semantics: A→A and A→B, both validating on the **target**.
2. Test never selects and never decides G.
3. The accepted TLE pair as the experimental unit; why 24 in-pass samples are
   not 24 observations.
4. One shared configuration: pairing, features, bands, screen, station, carrier,
   candidates.
5. Why the old BK1→BK2 numbers are superseded and not reused — this is stated
   plainly, as a methodological correction, not buried.

### Sec. III — Dataset

Satellite table from `data_manifest.json`: name, NORAD, family, records, epoch
span, cadence, altitude, inclination, eccentricity, B\*, usable staleness bands.
Diversity argument along the six axes of `DATASET_DESIGN.md`.

### Sec. VI — Reject sensitivity *(case-independent, must not be optional)*

The threshold sweep and the pre-committed decision table. This section exists
whatever the outcome, because the objection exists whatever the outcome.

### Sec. VIII — Limitations

Model-derived reference only; no measured RF truth; finite satellite set; one
carrier; one ground station; lightweight model family; a validation-window
property rather than a distribution-shift bound.

---

## Case-dependent framing

| Case | Placeholder title | Core claim | Primary figure |
|---|---|---|---|
| **A** — broadly unlearnable | "No Free Residual: Evidence-Gated Refusal Across LEO Regimes" | public-TLE residual learning showed no chronological utility in any tested satellite; the gate is a constant, correct refusal | F1 |
| **B** — regime-dependent | "When Residual Learning Earns Deployment: Regime-Dependent Inter-TLE Learnability" | learnability tracks an orbital axis; the gate becomes a real per-satellite selector | F1 + F5 |
| **C** — local yes, transfer no | "Learn Locally, Never Transfer: Satellite-Specific Inter-TLE Residual Structure" | residual structure is satellite-specific; local chronological validation is a necessary deployment condition | F1 + F2 |
| **D** — transfer works somewhere | "Transferable Residuals: Which LEO Regimes Share Inter-TLE Structure" | identify the source/target characteristics that support transfer; first missed-open evidence for the gate | F1 + F3 |

Case B is the most interesting and Case A the most continuous with Paper 1.
**Neither is favoured.** The claim thresholds in `GENERALIZATION_CLAIM_MATRIX.md`
§3 decide which case applies, and they were fixed before data.

---

## Section skeleton

```
I    Introduction — generalization as the problem, not a BLACK KITE extension
II   Unified protocol                       (case-independent)
III  Dataset and diversity                  (case-independent)
IV   Target-specific learnability           (Phase 4)
V    Cross-satellite generalization matrix  (Phase 5, headline)
VI   Reject sensitivity                     (Phase 6, case-independent)
VII  Gate objectives and tail awareness     (Phase 7)
VIII Discussion, limitations, conclusion
```

Sec. IV and V carry the case-specific story. Sec. VI and VII are defensive and
are written the same way in every case.

---

## Relationship to the frozen Paper 1

- Paper 1 is cited as prior work, not superseded wholesale: its contribution is
  the Evidence Gate formulation and the single-satellite negative result.
- The protocol correction is stated in Sec. II as a methodological improvement
  over our own earlier setup. It is not hidden and not apologised for.
- If Case D occurs, or if Phase 6 shows the screen manufactured the finding, the
  paper says so, and whether Paper 1 needs a correction note becomes a separate
  editorial decision — **not** something this paper resolves silently.
- The frozen manuscript and slides are never edited to agree with a later
  result.

## Venue

Same class of venue as Paper 1 (ICC/GLOBECOM workshop) if the outcome is Case A
or C; a short journal note if Case B or D, since those need the full matrix plus
the regime analysis and will not fit six pages.

## Prerequisite

None of this can be written until Phase 1 acquisition succeeds. Until then this
file stays a skeleton and the campaign stays in dry run.
