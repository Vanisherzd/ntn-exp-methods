# Generalization Stress-Test Report — Paper 1+

Date: 2026-07-27
Status: **dry run / insufficient data.** No new residual was computed.
Scope: software-only. Every value discussed is a model-derived inter-TLE
residual observed in available TLE artifacts. `reference_is_measured_truth =
false` — there is **no measured RF truth** anywhere in this campaign, and no
packet, error-rate, receiver-acknowledgement, over-the-air, or on-orbit result.

## 0. What was actually run

| Step | Outcome |
|---|---|
| Inventory of TLE artifacts in the workspace | 0 usable historical archives (see `TLE_DATA_INVENTORY.md`) |
| exp14 matrix runner against `dataraw/spacetrack` | `status: insufficient_data`, `satellites_found: 0`, empty CSVs, no figure |
| Runner code-path validation | exercised end-to-end on **synthetic** TLE histories written to a scratchpad only; those outputs are a code-path check, are not committed, and are not a result |
| Audit of the two committed real experiments | protocol discrepancies found (§5) |

No experiment was re-run on real data, because no real data is present.

## 1. Does residual learning generalize across satellites?

**Unknown, and not answerable from the available artifacts.**

Only two satellites have ever entered this pipeline, both BLACK KITE family with
near-identical refresh cadence (6.3 h and 6.4 h median) and no orbit-regime
diversity. The campaign's own threshold for a generalization statement is three
satellites; two similar objects test *transfer between two similar objects*, not
generalization.

The one directional observation available, in the transfer artifact, is that a
corrector fitted on BK1 and applied to BK2 is worse than SGP4 at 8, 24 and 48 h.
That is an observation about one ordered pair of BLACK KITE objects, in one
2-month common window, under one protocol. It is **not** evidence about
generalization in general.

## 2. Does target-specific training help?

**Not in the available BLACK KITE artifacts — and this is the more informative
of the two negatives.**

BK1 target-specific, trained and validated on the deploy target itself, still
fails at every reported staleness (reported point estimates, held-out test MAE):

| Staleness | zero / SGP4 | selected learned | degradation |
|---:|---:|---:|---:|
| 8 h | 0.2430 | 0.3501 | +44.1 % |
| 24 h | 0.8161 | 0.9109 | +11.6 % |
| 48 h | 1.9433 | 2.8608 | +47.2 % |
| 72 h | 4.8947 | 5.9092 | +20.7 % |
| 96 h | 10.1153 | 11.7663 | +16.3 % |
| 168 h | 26.9243 | 45.2629 | +68.1 % |

Even the constant validation-median bias — the lowest-variance correction that
exists — loses to zero at every age (exp11). So the failure is not "the model
never saw this satellite". Removing the domain-shift explanation entirely still
leaves the learner behind SGP4.

## 3. Does cross-satellite transfer fail?

**It failed in the one ordered pair observed, and it failed harder than
target-specific training** — the direction one would expect, but from a single
pair and a non-comparable protocol.

| Staleness | BK1→BK2 baseline | BK1→BK2 learned | degradation | BK1→BK1 degradation |
|---:|---:|---:|---:|---:|
| 8 h | 0.1877 | 0.3261 | +73.7 % | +44.1 % |
| 24 h | 0.4969 | 1.8639 | +275.1 % | +11.6 % |
| 48 h | 2.4092 | 2.8458 | +18.1 % | +47.2 % |

Transfer is worse than target-specific at 8 h and 24 h but *better* at 48 h, so
even the ordering is not monotone across staleness. Two of three rows worsen and
one improves; with three rows, one ordered pair and no per-split counts, this
cannot support a "cross-satellite transfer fails" law. The safe statement is
that the transfer checks observed in the available artifacts close the gate.

## 4. Does the Evidence Gate close unsafe transfers?

**Yes, in every reported row — and that is the one robust conclusion here.**

The gate closes on all six target-specific rows and all three transfer rows.
Because the learned candidate is worse than the zero baseline on every row, the
closure is invariant to which candidate is selected and to the γ value across
the tested range. In deployment terms the gate returns SGP4 / never-learn in
every observed case, which is the correct action given the measured degradations
above.

The important qualifier: the gate closing correctly on nine rows where *nothing*
should have deployed demonstrates the gate does not produce **false opens** on
this data. It says nothing about **missed opens**, because no row in the
available artifacts contains a genuinely learnable residual. The synthetic
gate-open branch remains the only demonstration that the rule can open at all.

## 5. Are the failures caused by residual scale, domain shift, or reject filtering?

Three candidate causes, with what the artifacts do and do not support:

**(a) Small residual scale — best supported.** BK1 held-out residuals are near
zero-mean (|mean| ≤ 0.081 Hz at every age) with the scale carried entirely by
spread (std 0.419 → 45.383 Hz over 8 → 168 h). BK2 residuals are smaller still
at short staleness (MAE < 0.25 Hz at 8 h). A near-zero-mean target with no
stable structure is exactly the regime in which a regressor fits validation
noise. This explanation also accounts for why the constant-bias baseline fails:
there is no consistent offset to remove.

**(b) Domain shift — supported for the cross rows only.** The transfer report
records BK1 residuals ~4× larger than BK2 at 8 h and BK1 outliers up to 6930 Hz
attributed to post-launch orbit-determination instability. A model fitted on
BK1's larger-residual distribution imports that scale onto BK2 and inflates
error. This explains why transfer degrades more than target-specific at short
staleness — but it cannot explain (2), where there is no shift at all.

**(c) Reject/outlier filtering — plausible, unquantified, and the weakest link.**
The screen removes 0/6/5/11/13/19 BK1 pairs at 8/24/48/72/96/168 h, with removed
magnitudes 1.4×–20× above the 1500 Hz threshold (2072 → 30574 Hz). Two readings
coexist and the artifacts cannot separate them:

- *Benign:* the removed population is far above threshold, not a borderline
  tail, so it is manoeuvre / bad-OD rather than ordinary drift — screening it is
  the standard treatment and the retained population is the nominal one.
- *Circular:* manoeuvres and bad fits are precisely the systematic, plausibly
  predictable events. Removing them and then reporting the remainder as
  unlearnable risks assuming the conclusion.

Neither the residual energy carried by removed pairs nor their learnability was
ever evaluated. `reject_sensitivity_summary.csv` in exp14 exists to settle this
once raw data returns. **This is the single most important open question in the
whole negative result.**

A fourth factor is a measurement artifact rather than a cause: the two
experiments used different reject thresholds (1500 Hz vs 150 Hz), different
feature counts (10 vs 7), different pairing rules, and different selection
procedures (§5 of `TLE_DATA_INVENTORY.md`). Target-specific and cross-satellite
rows are therefore not strictly comparable to each other, which independently
weakens any transfer-versus-target-specific conclusion drawn from Table I.

## 6. Claims that are safe

1. In the inter-TLE residual artifacts available for two BLACK KITE satellites,
   the reported point estimates of every lightweight learned corrector are worse
   than the zero-residual SGP4 baseline at every reported staleness.
2. The Evidence Gate closes in every reported row, so the deployed policy in all
   observed cases is SGP4 / never-learn.
3. Closure is invariant to candidate selection on these rows, because every
   candidate is worse than the baseline.
4. The observed BLACK KITE inter-TLE residual is near zero-mean with scale
   growing with staleness, which is consistent with — and sufficient to explain
   — the absence of a learnable correction in this data.
5. Screened-out pairs are far above the threshold rather than marginal, so the
   screen is not removing borderline drift.
6. A generalization matrix runner, gated per cell under the corrected
   train/validation/test protocol, now exists and is ready for restored data.

Every one of these is scoped to *model-derived inter-TLE residuals observed in
available TLE artifacts*, with no measured RF truth.

## 7. Claims that are NOT safe

1. ✗ "Inter-TLE residual learning does not generalize across satellites."
   Two same-family satellites, one ordered pair, one 2-month common window.
2. ✗ "Cross-satellite transfer fails." Three rows, non-monotone across
   staleness, protocol not comparable to the target-specific rows.
3. ✗ "The residual is unlearnable." Not universal — different features, longer
   arcs, manoeuvre-aware modelling, or other orbit regimes remain untested. The
   gate exists precisely to admit such a case if it appears.
4. ✗ "The Evidence Gate prevents unsafe cross-satellite deployment." It closed
   on the transfers observed; there is no evidence about transfers it has not
   seen, and no missed-open evidence at all.
5. ✗ Any tail-aware, p95/p99, guard-cost, or outage gate conclusion on real
   data. Per-sample learned predictions were never archived.
6. ✗ Any claim that the reject rule is neutral. Unquantified.
7. ✗ Any packet, error-rate, receiver-acknowledgement, over-the-air, on-orbit,
   or measured-Doppler statement. None exists in this campaign.
8. ✗ Anything derived from the synthetic scratchpad run used to validate the
   runner's code paths. It is a code-path check on fabricated orbits, is not
   committed, and carries no physical meaning.

## 8. What would change the answers

| Question | Blocking requirement |
|---|---|
| Does it generalize? | ≥ 3 satellites spanning distinct orbit/drag regimes and operator cadences |
| Is the reject rule circular? | `reject_sensitivity_summary.csv` over a threshold sweep, plus learnability of the screened population |
| Is "worse in every row" statistically real? | pair-level prediction export → pair-clustered paired test |
| Do tail-aware gates also close? | archived per-sample validation and test predictions |
| Are the two result blocks comparable? | one unified protocol re-run of both experiments |

All five need the local raw TLE archive restored first.
