# Paper 1 — Related-Work Positioning & Literature Classification

_Basis: refs.bib + `PAPER1_REFERENCE_AUDIT.md` + fresh external checks (arXiv /
IEEE Xplore) for candidate additions. Purpose: make the novelty unmistakable —
endpoint-side timing/frequency uncertainty control with an evidence-gated
learned residual under stale orbital information; NOT a receiver/link/capacity,
orbit-accuracy, or packet-validation paper._

## Category map (what each layer studies vs. what Paper 1 does)

| Category | Representative works | Layer | Evidence they provide | How Paper 1 differs | Cite in final ms? |
|---|---|---|---|---|---|
| LR-FHSS overview / performance | Boquet et al. [Commun. Mag. 59(3), 2021]; Semtech AN1200.64 | PHY/system characterisation | analytic + vendor performance of the modulation | we take LR-FHSS as given; our object is the *pre-TX control decision* | ✅ cited ([2],[4]) |
| LR-FHSS D2S link/capacity/energy | Ullah et al. [WCL 11(3), 2022]; Ullah et al. Doppler-limits [OJ-COMS 5, 2024] | network/link aggregate | capacity, delivery, Doppler-limit analyses | they quantify aggregate reliability/cost; no per-terminal trust decision, no stale-TLE gating | ✅ cited ([1],[5]) |
| LR-FHSS transceiver design | Jung et al. [Commun. Lett. 27(12), 2023] | receiver PHY | detector/transceiver sims under Doppler | receiver-side, post-transmission; we act before transmission | ✅ cited ([6]) |
| LR-FHSS transceiver implementation/verification | Jung et al. [OJVT 2025, DOI 10.1109/OJVT.2025.3585160] (in refs.bib, uncited) | receiver implementation | implemented/verified transceiver | same contrast as [6]; adds implementation depth | ⚪ optional (page budget; [6] already covers the layer) |
| LR-FHSS real packet traces | Bukhari & Zhang [arXiv 2312.13981; ToSN version exists] | receiver empirical | real-trace decoding study | decoding of existing transmissions; we make no decode claim | ✅ cited ([7]) |
| LR-FHSS ToA / current-consumption measurement | Ullah et al., "Experiment-based Models for Air Time and Current Consumption of LoRaWAN LR-FHSS" — [arXiv 2408.09954](https://arxiv.org/abs/2408.09954), published IEEE IoT-J ([Xplore 11184757](https://ieeexplore.ieee.org/document/11184757/)) | device energy measurement | measured ToA/current models | measures transmission cost; does not decide *whether/when to trust a learned residual*; complements our energy proxy | ⚪ **optional** — would strengthen Eq. (13) grounding; withheld for hard-6 |
| D2D-aided LR-FHSS D2S outage/capacity | Maleki et al., "Outage Probability Analysis of LR-FHSS and D2D-Aided LR-FHSS…," IEEE IoT-J 11:11101–11116, 2024 ([Xplore 10304196](https://ieeexplore.ieee.org/document/10304196/); [arXiv 2212.04331](https://arxiv.org/abs/2212.04331)) | network outage analysis | closed-form outage under shadowed-Rice | network-level capacity aid; orthogonal to endpoint trust/margin sizing | ⚪ optional (layer already represented by [5]) |
| NTN sync / timing advance / RA | 3GPP TR 38.821 V16.0.0 [official]; candidate paper: "Location-Based Timing Advance Estimation for 5G Integrated LEO Satellite Communications" ([arXiv 2105.03858](https://arxiv.org/pdf/2105.03858), IEEE TVT — **metadata needs human check**) | receiver/RA-layer estimation | TA/ToA/CFO estimation procedures | they estimate sync quantities at RA/receiver; we *gate a learned corrector* and size margins pre-TX | ✅ [8]=TR 38.821 cited; TVT paper ⚪ optional pending verification |
| ML orbit correction | Peng & Bai GP [Acta Astr. 161, 2019]; dSGP4 [Acta Astr. 226]; survey [Acta Astr. 220, 2024]; SGP4 [SPACETRACK No. 3] | trajectory accuracy | corrected orbit/Doppler accuracy | they improve the estimate; we decide whether an improvement claim is *trustworthy enough to deploy* | ✅ cited ([9]–[12]) |
| D2S uplink policy | Álvarez et al. [IEEE Access 10, 2022] | scheduling given trusted prediction | when/how to transmit from geometry/link scores | assumes prediction trustworthy; we supply the missing trust decision | ✅ cited ([13]) |

## The gap (as now written in the manuscript)

> None decides, at the endpoint and **before** transmission, whether a learned
> residual should be trusted under stale orbital information, nor how
> timing/frequency uncertainty should size the LR-FHSS guard, hop-bin margin,
> and energy policy.

## Citations added/changed in the manuscript

**None added** (hard-6 budget). Taxonomy paragraph now uses the existing
13 references, reorganised into four explicit layers. Citation **numbering
shifted** (taxonomy order): [8]=3GPP TR 38.821, [9]=Hoots, [10]=Peng,
[11]=Acciarini, [12]=Caldas — `PAPER1_REFERENCE_AUDIT.md` rows map by key, not
number.

## Optional references (verified, ready if a future venue allows more room)

1. `ullah2024toa` — arXiv 2408.09954 / IEEE IoT-J (ToA + current consumption) — strengthens energy-proxy grounding.
2. `maleki2024d2d` — IEEE IoT-J 11:11101–11116, 2024, D2D-aided outage — strengthens layer (i).
3. `jung2025lrfhss` — already in refs.bib (OJVT 2025) — strengthens layer (ii).
4. NTN TA estimation (arXiv 2105.03858 / IEEE TVT) — strengthens layer (iii); **metadata needs human check before use**.
