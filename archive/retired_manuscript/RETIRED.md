# RETIRED MANUSCRIPT

> **RETIRED. NOT SUBMISSION-READY. NUMERICAL RESULTS INVALIDATED.**

This directory holds a frozen snapshot of a manuscript whose central result was
withdrawn. It is retained for provenance only.

## Status

- **Not submission-ready.** Its headline result was invalidated.
- **Numerical results invalidated.** Every performance figure in the text, tables and
  figures derives from experiments listed in
  [`../KNOWN_INVALID_RESULTS.md`](../KNOWN_INVALID_RESULTS.md).
- **Not to be edited into another submission.** Do not branch from it, do not
  reuse its framing, do not treat it as a starting point.
- **Figures and prose may not be copied without re-verification.** Every number in
  every figure traces to an invalidated dataset. Figure *style* may be reused; figure
  *content* may not.

## What was withdrawn

| element | why |
|---|---|
| headline improvement result | depended on a feature knowable only after a future catalogue publication |
| all cell-level statistics | computed on a dataset 96.58 % of whose transmissions placed the satellite below the endpoint horizon |
| screening-sweep opening | same defects, plus a staleness band unreachable under any realistic provisioning policy |
| endpoint-budget conclusions | every input is a residual statistic from the same dataset; the tolerance was representative, never a requirement; no PHY simulation was ever run |
| any claim that the Evidence Gate is validated for deployable Doppler correction | never established at any point, on real data or in software |

## What was not wrong

Recorded for fairness, and still not a result: the *mechanism* description — a physics
baseline, an optional learned residual branch, chronological validation, a frozen gate
bit and fallback — was coherent and survived four adversarial review cycles. What
failed was every attempt to produce a dataset capable of testing it.

## The manuscript file itself was not modified

The snapshot is byte-identical to the freeze. Hashes are in the accompanying
`MANIFEST.sha256` and in the archival tag annotation.

## Where the reusable parts went

- Engineering assets: `salvage/orbit-evidence-toolkit/`
- Defects as executable tests: `salvage/orbit-evidence-toolkit/tests/test_regressions.py`
- Lessons: `docs/FAILURE_TAXONOMY.md`
- If measurements ever become available: `docs/FUTURE_MEASUREMENT_PROTOCOL.md`
