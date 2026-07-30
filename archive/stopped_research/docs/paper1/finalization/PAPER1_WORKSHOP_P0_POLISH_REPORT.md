# Paper 1 Workshop P0 Polish Report

## Scope

Performed a P0 workshop-submission polish pass only. No experiments were run, no
hardware was touched, no numerical results were changed, no references were added,
and conducted-IQ was not reintroduced into the main paper.

## Inter-TLE Residual Wording

The real-data residual is now framed consistently as model-derived inter-TLE
residual evidence:

- abstract: `learned inter-TLE residual`;
- introduction: `model-derived inter-TLE residual`;
- real-data contribution: `learned inter-TLE residual never beats SGP4`;
- Sec. II-B: added the compact clarification that the residual is not
  over-the-air Doppler error, but the residual observable to a TLE-only terminal
  by comparing stale and later TLE propagations;
- Table I caption and Fig. 2 caption: changed to inter-TLE wording.

General "Doppler residual" remains only in broad keyword / concept contexts.

## Real Residual Scale Framing

Sec. IV-B now owns the small BLACK KITE residual scale as the main finding:

- the 168 h BK1 inter-TLE baseline MAE is explicitly described as small against
  `F_tol = 500 Hz`;
- the text states this leaves little useful signal for always-on residual ML;
- the negative result is framed as a warning against deploying residual ML by
  default, not a failed improvement result.

The paper does not imply BLACK KITE inter-TLE residuals threaten real hop
reception.

## 90.4% Demotion

Sec. IV-E no longer repeats the full stair-step proxy sequence in prose. It now
states that Fig. 3(c,d) is an illustrative stress-proxy using a deliberately larger
baseline frequency-error scale than Table I, and should not be read as a BLACK KITE
deployment outcome.

The 90% value remains only in the figure itself, bounded by the figure caption and
nearby prose as controlled gate-open synthetic proxy evidence.

## Table IV Cleanup

Table IV remains compact and now uses clearer policy wording:

- BLACK KITE: `learned worse` / `SGP4` / `closed` / `unsafe ML rejected`;
- synthetic systematic: `helps` / `misses opportunity` / `open` /
  `opens only with held-out evidence`.

No new numerical results were added.

## Protocol Transparency

The paper keeps compact protocol details without inventing unavailable
per-staleness n:

- 24 UTC samples per pair over one orbit;
- pair rejection rule: reject if any sample has `|r| > 1500 Hz`;
- chronological 60/20/20 train/validation/test split;
- causal validation window;
- synthetic stress split: 20,000 samples per regime with 12,000/4,000/4,000
  train/validation/test split;
- artifact manifest indexes compact CSV summaries, linked reports, and regeneration
  commands.

Per-staleness n was not added because a clean manifest-level per-staleness count
table was not immediately available.

## Conducted-IQ Removal Status

Main paper:

- no conducted-IQ in abstract;
- no conducted-IQ in contributions;
- no conducted-IQ in system figure footer;
- no conducted-IQ section or table;
- no conducted-IQ in conclusion or limitations.

Slides:

- conducted-IQ remains only as an advisor discussion slide marked artifact-only and
  not a paper contribution.

## Build / QA Status

Commands run:

- `tectonic --keep-logs paper/icc_main.tex`
- `tectonic --keep-logs paper/slides_overview.tex`
- `tectonic paper/icc_main.tex`
- `tectonic paper/slides_overview.tex`

Results:

- Main paper: 6 pages including references.
- Slides: 14 slides.
- Undefined references/citations: none found in refreshed logs.
- Overfull boxes: none found in refreshed logs.
- Remaining warnings: existing underfull boxes, existing `algorithm.sty` UTF-8
  warning, and slide embedded-PDF version warnings.

Manual PDF checks:

- rendered page with Table IV and real residual scale framing;
- rendered Fig. 3 page and confirmed the 90% proxy remains visually bounded by
  synthetic/proxy caption and prose.

## Risky-Term Scan

Scan terms:

`conducted-IQ`, `hardware evidence`, `hardware validation`, `90%`, `2.5 kHz`,
`Doppler residual`, `measured Doppler`, `RF truth`, `packet`, `PER`, `PDR`, `CRC`,
`gateway ACK`, `OTA`, `live-satellite`, `link validation`.

Classification:

- OK limitation / future work: packet/PER/PDR/CRC/OTA/live-satellite/link-layer
  terms appear in non-claim boundaries, related work, or future work.
- OK synthetic-proxy context: 90% remains only in Fig. 3 visual content and is
  bounded by synthetic/proxy caption and prose; 2.5 kHz no longer appears in main
  manuscript prose.
- OK artifact-only context: conducted-IQ appears only in the advisor slide, not the
  main paper.
- OK general concept: `Doppler residual` remains in keywords/general context only.
- FIX ambiguous positive claim: none found.

## Remaining Blockers

- Author block / venue anonymity policy.
- Final metadata.
- Cross-satellite generalization remains the main scientific limitation and next
  software campaign.

## Readiness

Ready for another strict workshop review as a negative-result /
conservative-learning systems note. Not final submission-ready until author policy
and metadata are resolved.
