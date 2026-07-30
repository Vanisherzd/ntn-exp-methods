# Paper 1 — Positioning & Contribution-Sharpening Report

_Combined with the gate/carrier consistency pass (see
`PAPER1_GATE_AND_CARRIER_FIX_REPORT.md`). Build: 6 pages incl. references,
0 overfull, 0 undefined refs._

## Related-work categories compared (full map: `PAPER1_RELATED_WORK_POSITIONING.md`)

1. LR-FHSS overview/performance — [2],[4]
2. LR-FHSS D2S link/capacity/energy + Doppler limits — [1],[5]
3. LR-FHSS transceiver design / implementation — [6] (+ optional OJVT 2025, already in refs.bib)
4. LR-FHSS real packet traces — [7]
5. LR-FHSS ToA/current-consumption measurement — optional (arXiv 2408.09954 / IEEE IoT-J, verified)
6. D2D-aided LR-FHSS outage/capacity — optional (IEEE IoT-J 11:11101–11116, 2024, verified)
7. NTN sync / timing advance / random access — [8]=TR 38.821 (+ optional TVT TA paper, needs human check)
8. ML orbit correction / dSGP4 / GP / survey — [9]–[12]
9. D2S uplink policy — [13]

## Citations added/changed

- **Added to manuscript: none** (hard-6 budget); four verified optional
  references documented for future versions.
- Taxonomy reordering shifted citation numbers: [8]=3GPP, [9]=Hoots, [10]=Peng,
  [11]=Acciarini, [12]=Caldas (audit doc maps by BibTeX key).
- refs.bib unchanged this pass (earlier fixes [1],[8-institution] retained).

## Final novelty sentence (in manuscript, before contributions)

> "Unlike receiver-side LR-FHSS studies and orbit-accuracy learning, we study
> the *pre-transmission endpoint decision*: is a learned Doppler residual
> trustworthy enough to size timing/frequency/energy margins, or should the
> terminal retain the SGP4 physics default?"

## Final related-work paragraph (taxonomy form)

Four explicit layers — (i) link/capacity/energy, (ii) receiver-side
transceiver/packet-trace, (iii) NTN synchronisation (TA/ToA/CFO at
receiver/RA layer), (iv) orbit-learning + uplink policy — each with a one-line
contrast, closing with the gap sentence: none decides, at the endpoint and
before transmission, whether a learned residual should be trusted under stale
orbital information, nor how timing/frequency uncertainty should size the
LR-FHSS guard, hop-bin margin, and energy policy.

## Final contribution bullets

1. **Evidence-gated endpoint control under stale orbital information:**
   deploy/no-deploy trust test (Eqs. 6–7) at the Doppler-precompensation point
   with causal chronological windows; no distribution-shift guarantee claimed.
2. **Real-data negative control plus controlled gate-open condition:** on
   BLACK KITE (8–168 h, strict splits) the learned residual never beats SGP4 →
   gate closes; synthetic systematic regime opens the same rule
   (Tables I–II, Fig. 2); no real-data improvement from learning claimed.
3. **Endpoint-budget proxies plus bounded conducted-IQ evidence:**
   coverage-proxy chain (Eqs. 10–13) linking timing/frequency uncertainty to
   guard, hop-bin margin, and energy per successful burst at MCU-class
   footprint (Fig. 3), plus a repeatable conducted measurement-path sanity
   check; no packet, link-layer, or OTA validation claimed.

## Abstract / conclusion consistency

Abstract adds the deploy/no-deploy value sentence; conclusion adds "safe
fallback" + "trust/deploy decision for learning, not a guaranteed-improvement
claim." Endpoint decision, evidence-gated trust, stale orbital information,
timing/frequency/energy margins, and the bounded conducted-IQ wording all
aligned across abstract–intro–conclusion.

## Page count & scan

- **6 pages including references** (refs end near bottom of p. 6); 0 overfull,
  0 undefined. Offsetting trims listed in the gate/carrier report.
- **No-overclaim scan: PASS** (2 hits, negation/future-work only).

## Remaining blockers

1. Author-block placeholder (pre-existing SUBMISSION BLOCKER).
2. Optional [7] ACM ToSN metadata + optional NTN TVT reference — human check.
3. Commits D–G pending (`PAPER1_FINAL_COMMIT_PLAN.md`).
