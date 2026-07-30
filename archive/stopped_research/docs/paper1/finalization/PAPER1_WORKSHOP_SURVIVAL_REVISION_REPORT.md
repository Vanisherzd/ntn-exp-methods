# Paper 1 Workshop-Survival Revision Report

## Scope

Performed a conservative workshop-survival pass. No experiments were run, no
hardware was touched, no numerical results were changed, no references were added,
and no Fig. 4 / hardware figure was reintroduced into the main paper.

## Hardware Removal / Downgrade

Removed conducted-IQ from the main-paper claim path:

- abstract no longer mentions conducted-IQ;
- contribution bullets no longer list conducted-IQ as a contribution;
- Fig. 1 footer no longer points to conducted-IQ evidence;
- experimental setup no longer discusses the conducted-IQ run;
- the former Section V `Preliminary Conducted-IQ Evidence` and its conducted-IQ
  table were removed from the main paper;
- conclusion no longer elevates conducted-IQ as evidence for the algorithm.

The only remaining main-paper hardware mention is an artifact/limitation sentence:

> Conducted-IQ measurement-path sanity results are available in the artifact
> package, but they are not used as algorithmic or link-layer validation.

Slides keep the conducted-IQ page only as advisor discussion material, retitled
`Artifact Sanity Only: Conducted-IQ`, with an explicit "not a paper contribution"
boundary.

## New Policy Comparison Table

Added new Table IV:

> Policy comparison across real and controlled regimes.

It compares:

- BLACK KITE real TLE;
- synthetic noise;
- synthetic marginal;
- synthetic systematic.

Columns compare always-learn, never-learn / SGP4, Evidence Gate, and interpretation.
The table makes the selector story explicit: the gate rejects unsafe ML on real
BLACK KITE and weak/no-evidence synthetic regimes, but opens under held-out
systematic synthetic evidence.

The advisor slides now include a matching `Policy Comparison` slide.

## Scale-Ambiguity Fix

Clarified the 2.5 kHz / 90.4% proxy passage so it is explicitly the controlled
synthetic gate-open stress setting, not the BLACK KITE residual scale:

- `2.5 kHz` is now a synthetic baseline frequency error;
- the text explicitly says "not the BLACK KITE residual scale of Table I";
- `90.4%` remains only in the body as a software-only proxy result;
- real BLACK KITE remains the negative result: learned residual is worse than SGP4
  and the gate closes.

## Reproducibility Transparency

Added minimal protocol details already present in existing artifacts:

- real TLE record counts and median inter-TLE gaps remain stated;
- stale/reference pairs use 24 UTC samples over one orbit;
- pair rejection rule is now explicit: reject if any sample has `|r| > 1500 Hz`;
- split rule remains chronological 60/20/20 by reference epoch;
- validation window is causal;
- learned candidates remain ridge, random forest, gradient boosting, and small MLP;
- synthetic stress now states 20,000 samples/regime and 12,000/4,000/4,000 split;
- artifact manifest / compact CSVs are referenced without inventing per-staleness
  counts.

## Build / QA Status

Commands run:

- `tectonic --keep-logs paper/icc_main.tex`
- `tectonic --keep-logs paper/slides_overview.tex`

Results:

- Main paper: 6 pages including references.
- Slides: 14 slides.
- Undefined references/citations: none found in refreshed logs.
- Overfull boxes: none found in refreshed logs.
- Active Fig. 4 / hardware-figure references: none in `paper/icc_main.tex`.
- Conducted-IQ as contribution: none found.
- Ambiguous real-result `90%` claim: none found.
- Ambiguous `2.5 kHz SGP4 residual` claim: none found.

Manual PDF checks:

- rendered paper page containing Table IV; table is present in the evaluation flow;
- rendered the new policy-comparison slide; slide is readable and claim-bounded.

## Risky-Term Scan

Scan terms:

`packet`, `PER`, `PDR`, `CRC`, `gateway ACK`, `OTA`, `live-satellite`,
`link validation`, `RF validation`, `measured Doppler`, `truth`, `end-to-end`,
`90%`, `2.5 kHz`, `conducted-IQ`, `hardware evidence`, `hardware validation`.

Classification:

- OK related work: packet-trace mention in related work.
- OK limitations / non-claims: no packet/link/OTA/live-satellite/measured-Doppler
  statements in abstract, limitations, and slide footers.
- OK synthetic-proxy context: `2.5 kHz` and `90.4%` appear only in the controlled
  synthetic software-only proxy passage.
- OK artifact-only context: conducted-IQ appears only as artifact/limitation in the
  main paper and artifact-only advisor-slide material.
- FIX ambiguous positive claim: none found.

## Remaining Blockers

- Submission readiness still depends on author block / venue anonymity policy and
  final metadata.
- Cross-satellite generalization remains the main scientific limitation and next
  software campaign.

## Readiness

Ready for another strict workshop review as a negative-result / conservative-learning
systems note. Not submission-final until author policy and metadata are resolved.
