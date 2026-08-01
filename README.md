# Orbit-Evidence

A deployment-causality and falsifiability contract for learning-assisted satellite
communication software, plus the toolkit that implements it and the regression suite that
exercises it.

**Active paper:** *Orbit-Evidence: Relational Validity Checks for Learning-Assisted Satellite
Communication Experiments* — `paper/icc_main.tex`, built to `paper/icc_main.pdf` by `make paper`.
Anything titled "Beyond Chronological Splits" is the superseded title; see
[THE_PAPER.md](THE_PAPER.md) for every other `icc_main` in the tree and why it is not the
submission.

Chronological train/validation/test splitting is necessary for temporal learning
pipelines, but ordering is only one of the properties a deployment claim rests on. A
pipeline can satisfy it exactly and still be uninterpretable, because ordering constrains
neither whether a past-dated quantity was *available* at the decision instant, nor which
rows *exist*, nor what a learner's hidden state has already observed, nor whether the unit
over which intervals are computed is exchangeable. This repository turns those four
assumptions into 19 executable checks over six protected objects, and measures them
against a curated suite of 17 fault classes.

## Quick start

```bash
pip install -e '.[test]'   # numpy + pytest; numpy is the only runtime dependency
make gate         # tests + fault matrix + claim gate + six-page paper build
make gate-twice   # runs the gate twice and asserts the summary artifact reproduces
make paper        # build paper/icc_main.pdf only
```

`numpy` is the only runtime dependency; the paper build needs a TeX Live installation with
`latexmk` and `IEEEtran`. The committed `uv.lock` pins the much larger stack the *archived*
research lines used and is not needed for anything above — do not `uv sync` expecting this
artifact's dependencies.

## Layout

```text
paper/                  active manuscript; icc_main.tex is the sole entry point
  submission/           claims, artifact map, checklist, allowed/prohibited claims
src/orbit_evidence/     the toolkit (pass scheduler, registry, labels, contract)
tests/regression/       two-sided regression tests, one per historical defect
tests/fault_injection/  the matrix acceptance tests
tests/fixtures/         the two pipelines and the frozen fault injectors
evaluation/scripts/     the 19 contract rules, the baseline, the matrix runner
evaluation/results/     final_summary.json -- the single source of every paper number
evaluation/mutations/   the pre-registration, with its withdrawal notice
docs/                   failure taxonomy, future measurement protocol, reproducibility
archive/                stopped research lines, retired manuscript, invalid results
```

## What this repository claims

- Chronological splitting constrains ordering and does not by itself establish
  availability, row membership, hidden-state cleanliness, or unit exchangeability.
- On the curated suite: chronological protocol checks detect **2 of 17** fault classes;
  the contract detects **17 of 17** across three deterministic environments (51 injected
  cells). Clean reference paths are accepted.
- For the statistical-unit rule, specificity is a **measured rate**: 0.031 false halts
  over 450 clean paths against a nominal α = 0.05.
- **16 of 19** rules have a demonstrated broken fixture. L2.2, L2.3 and L4.5 are exercised
  only on the clean path, and the paper says so rather than claiming otherwise.
- `make external-consequence-verify` checks the third-party consequence artifacts against the
  frozen commit, detector hash and recorded data hashes without training anything;
  `make external-consequence-run TELEMANOM=... DATA_ROOT=...` reproduces it and fails closed.
  Its telemetry arrays came from a checksum-verified mirror, not the original endpoint --
  see `evaluation/external_consequence/DATA_PROVENANCE.md`.
- The full sweep takes about 1.5 s on a quiet laptop core and about 3.5 s on a loaded machine; the 3 s / 60 ms figures in `make claims` are this repository's regression thresholds, not portable performance bounds.

## What it does not claim

- **No generalisation to faults the suite does not contain.** The 17/17 figure is
  represented-fault *regression* coverage: the faults and the rules share an author, so
  for most classes it measures detector reachability. An earlier held-out-mutation claim
  was withdrawn after review — see `evaluation/mutations/PREREGISTRATION.md`.
- No completeness over leakage classes. Six protected objects is what we found necessary,
  not what exists.
- No radio-frequency, packet-level, PER/BER/PDR, energy, or live-satellite result. The two
  pipelines are deterministic fixtures for exercising rules, not simulators.
- No claim that any learned communication method works or fails. The object of study is
  the experiment, not the model.

## Stopped research, kept on purpose

This repository previously pursued a residual-Doppler line for LR-FHSS
direct-to-satellite IoT. That line was **stopped** — the label source proved to have
missing-not-at-random censoring on the very covariate under study, and a controlled
replacement benchmark failed its own negative control. Both are archived rather than
deleted:

- `archive/KNOWN_INVALID_RESULTS.md` — results that must never be reused. The paper build
  fails if any of them appears in a manuscript source.
- `archive/retired_manuscript/` — the retired manuscript, preserved.
- `archive/real_tle_causality_audit/` — the causality audit that stopped the line.
- `docs/FAILURE_TAXONOMY.md`, `docs/FUTURE_MEASUREMENT_PROTOCOL.md` — what went wrong and
  what a valid measurement would require.

The threat model and both case studies come from that experience. No performance claim
does.
