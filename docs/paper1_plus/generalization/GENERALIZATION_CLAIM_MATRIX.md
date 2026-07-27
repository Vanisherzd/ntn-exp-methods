# Generalization Claim Matrix (Phase 8, pre-registered)

Date: 2026-07-27
Status: **pre-registration.** Written before any result exists, so that no
outcome is easier to claim than another. Nothing here is a finding.

Scope: software-only, model-derived inter-TLE residuals,
`reference_is_measured_truth = false`.

---

## 1. Outcome cases and the claims each licenses

The frozen Paper 1 conclusion is **not** privileged. All four cases are written
to the same standard.

### Case A — most/all satellites unlearnable

*Signature:* diagonal degradation positive across satellites and staleness;
pair win rate well below 50 %; sign test significant against the learner; gates
closed almost everywhere.

| Safe to claim | Not safe |
|---|---|
| Across the tested LEO regimes, public-TLE inter-TLE residual learning showed no chronological utility over SGP4 in any tested satellite | "Residual learning is impossible" |
| The Evidence Gate returned the safe action in every tested cell | Any statement about untested regimes, feature sets, or longer arcs |
| Generalizes the frozen Paper 1 from 1 object to N objects and M regimes | That the result holds for manoeuvre-inclusive populations, unless Phase 6 says so |

*This is the strongest possible version of the current story, and the only case
in which Paper 1+ is a straightforward extension.*

### Case B — regime-dependent learnability

*Signature:* diagonal gates open for some satellites, closed for others, with
the split tracking an orbital axis (altitude, B\*, cadence, manoeuvre behaviour).

| Safe to claim | Not safe |
|---|---|
| Inter-TLE residual learnability is regime-dependent among the tested objects | That the identified axis is *causal* rather than correlated, without an ablation |
| The Evidence Gate acts as a genuine selector, not a constant refusal | Extrapolation to regimes with no satellite in the set |
| The gate's value shifts from "refusal" to "per-satellite admission control" | A general rule from a handful of objects per regime |

*This is the most scientifically interesting case and would reframe the gate as
the contribution rather than the negative result.*

### Case C — target-specific works, transfer fails

*Signature:* diagonal gates open, off-diagonal gates closed; off-diagonal
degradation systematically worse than diagonal.

| Safe to claim | Not safe |
|---|---|
| Inter-TLE residual structure is satellite-specific among tested objects and unsafe to transfer without local validation | "Transfer is impossible between LEO satellites" |
| Local chronological validation is a **necessary** deployment condition | That similarity metrics predict transferability, without testing them |
| Directly supports the endpoint argument: a terminal must validate on its own satellite | Any claim about untested source/target ordering |

*This case would make the endpoint framing stronger than the frozen paper's,
because refusal becomes conditional rather than absolute.*

### Case D — transfer succeeds somewhere

*Signature:* one or more off-diagonal gates open with a real test-set
improvement and a pair win rate above 50 % with a significant sign test.

| Safe to claim | Not safe |
|---|---|
| Transferable residual structure exists between the specific named source/target regimes | "Residual learning generalizes" as a general statement |
| Identify which orbital/drag characteristics the transferable pairs share | Causal attribution from a single successful direction |
| The gate correctly admitted a genuinely useful branch — the first missed-open evidence | Deployment recommendation without tail-aware confirmation (Phase 7) |

*This case partially contradicts the frozen Paper 1's framing. It would be
reported plainly, with the frozen paper left intact and a separate decision made
about whether Paper 1 needs a correction note.*

---

## 2. Claims that stay unsafe in every case

1. Any measured-Doppler, packet, error-rate, receiver-acknowledgement,
   over-the-air, or on-orbit statement.
2. Universal unlearnability. The tested set is always finite.
3. Any conclusion drawn from cells with `status: insufficient_pairs` — that is a
   sample-size limitation, not evidence.
4. Any conclusion that ignores Phase 6. If screening changes the sign of the
   result, every learnability claim inherits that conditionality.
5. Any comparison against the **old** BK1→BK2 numbers. Different protocol,
   superseded, not comparable.
6. Any tail-aware claim from an `unavailable` or degenerate (baseline-is-zero)
   gate.
7. Attribution of an outcome to an orbital axis without varying that axis while
   holding others roughly fixed.

---

## 3. Evidence thresholds agreed in advance

| Statement | Minimum evidence |
|---|---|
| "satellite X is learnable" | diagonal gate open on validation **and** test degradation < 0 **and** pair win rate > 50 % **and** sign-test p < 0.05 |
| "satellite X is not learnable" | diagonal gate closed at every staleness **and** test degradation > 0 at every staleness |
| "transfer A→B is unsafe" | off-diagonal gate closed **and** test degradation > 0, with B's own diagonal evaluable for comparison |
| "learnability is regime-dependent" | ≥ 2 satellites open and ≥ 2 closed, with ≥ 3 satellites per side of the proposed axis |
| "the screen manufactured the result" | degradation crosses zero or a gate opens at a looser threshold (Phase 6 §4) |
| any multi-satellite wording at all | ≥ 6 satellites over ≥ 3 regimes ingested and evaluable |

A cell that fails its threshold is reported as inconclusive. Inconclusive is an
acceptable outcome and must not be rounded toward either story.

---

## 4. Current state

No case is selected. No data. The campaign is in dry run, and this document
remains a pre-registration until `data_manifest.json` contains ≥ 6 satellites
over ≥ 3 regimes.
