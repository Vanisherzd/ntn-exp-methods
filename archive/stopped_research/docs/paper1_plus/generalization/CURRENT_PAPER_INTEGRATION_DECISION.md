# Current-Paper Integration Decision — Paper 1+ Generalization Campaign

Date: 2026-07-27
Decision authority: this document records a recommendation. **No paper or slide
file was edited in this campaign**, per the campaign brief.
Scope: every number quoted below is a model-derived inter-TLE residual with
`reference_is_measured_truth = false`; no measured RF truth is involved.

## Summary of the four questions

| | Question | Decision |
|---|---|---|
| **A** | Should current Paper 1 be changed? | **No — not by this campaign's results.** One *separate* wording defect was found that is worth a future pass (§3). |
| **B** | Should this remain Paper 1+? | **Yes, entirely.** |
| **C** | Should slides get a backup mention? | **No.** Backup slide 15 already covers it correctly. |
| **D** | Does any result contradict current Paper 1? | **No result contradicts it.** One *protocol description* in the paper is broader than what the cross-satellite artifact supports (§3). |

---

## A. Should current Paper 1 be changed?

**No.** The campaign produced no new residual, no new number, and no new
evidence: `status: insufficient_data`, `satellites_found: 0`. There is nothing
to integrate.

Even the two supporting observations that *are* new — that screened-out BK1
pairs sit 1.4×–20× above threshold, and that a per-cell gated matrix runner now
exists — are not paper material:

- The reject-magnitude table is a strengthening of an existing limitation, not a
  new claim. Paper 1 already states the finding is conditional on accepted
  non-outlier pairs. Adding magnitudes would consume page budget the paper does
  not have (it is at exactly 6 pages with zero slack) to make a concession the
  paper already makes.
- A runner with no data behind it is not a result.

Default preference in the brief — *do not change current Paper 1 unless the
result is directly relevant and compact* — is satisfied by leaving it frozen.

## B. Should this remain Paper 1+?

**Yes, all of it.** Nothing here reaches the bar for the workshop note:

| Artifact | Home |
|---|---|
| exp14 matrix runner and its schema | Paper 1+ |
| Multi-satellite generalization matrix | Paper 1+, blocked on ≥ 3 satellites |
| Reject-sensitivity sweep | Paper 1+, blocked on raw data |
| Tail-aware gate on real data | Paper 1+, blocked on per-sample export |
| Unified-protocol re-run of both experiments | Paper 1+ (and a prerequisite for any matrix claim) |
| Reject-magnitude table | Paper 1+ / advisor Q&A talking point |

## C. Should slides get a backup mention?

**No new slide, no edit.** Backup slide 15 ("Software Extension Diagnostics")
already states:

> The multi-satellite pipeline is prepared as future work; no new generalization
> claim.

That is exactly the campaign's outcome. Adding a slide saying the same thing
with a runner name would grow the deck for no informational gain. The deck is at
16 slides (12 main + 4 backup), which is the agreed ceiling.

The reject-magnitude numbers are worth carrying **verbally** into advisor Q&A —
see §5 — but they do not need a slide.

## D. Does any result contradict current Paper 1?

**No result contradicts Paper 1.** Every committed number this campaign
re-read matches Table I exactly. The gate closes in all nine reported rows, and
that closure is invariant to selection rule and γ.

However, the audit surfaced **one protocol-description defect** that is genuinely
worth fixing in a future paper pass. Recording it here so it is not lost.

### The defect

Paper 1 Sec. IV-A now states, correctly for the six BK1 target-specific rows:

> Training fits the candidates; the model family and the gate decision are fixed
> on the chronological validation segment; the held-out test segment reports the
> consequence of that pre-decided policy and never decides the gate.

For the three BK1→BK2 rows in the same table this does not hold as written.
`tools/bk_tle_residual_experiment.py` splits BK1 entirely to train and BK2
entirely to test; there is **no target-side validation window**, and the
reported model is chosen by `min(ridge_mae, mlp_mae)` evaluated on the BK2
**test** set. The MLP's internal early-stopping split is carved from BK1 train
data, i.e. source-side only.

Two further descriptive mismatches in the same direction:

| Paper text | BK1 target-specific | BK1→BK2 transfer |
|---|---|---|
| "a pair is rejected if any sample has \|r\| > 1500 Hz" (Sec. III-D, unscoped) | 1500 Hz ✅ | **150 Hz** ✗ |
| feature vector incl. "stale orbital elements" (Sec. II-B) | 10 features ✅ | **7 features**, no orbital elements ✗ |
| "conditional on accepted non-outlier pairs under this \|r\| > 1500 Hz screening" (Sec. III-D) | ✅ | ✗ (150 Hz) |

Table I's caption already scopes the 1500 Hz screen to "BK1 target rows", so the
caption is correct; the unscoped sentences in Sec. II-B and Sec. III-D are the
imprecise ones.

### Why this is not urgent, and not a retraction

For all three cross rows **every** candidate is worse than the zero baseline on
test:

| Staleness | zero | ridge | MLP | min(candidates) | worse than zero? |
|---:|---:|---:|---:|---:|:--:|
| 8 h | 0.1877 | 0.3738 | 0.3261 | 0.3261 | yes |
| 24 h | 0.4969 | 2.5413 | 1.8639 | 1.8639 | yes |
| 48 h | 2.4092 | 2.8458 | 2.9593 | 2.8458 | yes |

Selecting on test therefore cannot flip any gate decision, cannot inflate any
reported improvement, and gives the learner the *most favourable* number
available — so the reported degradations are, if anything, conservative. The
reported values (0.3261, 1.8639, 2.8458) are exactly what Table I prints.

This is a defect in how the protocol is described, not in the result.

### Recommended fix, for a future paper pass (not now)

Cheapest correct wording, roughly one line, inside the Table I caption where the
per-row scoping already lives:

> The cross-transfer rows use the earlier transfer protocol (source-only
> training, 150 Hz screen, 7 features) and report the best candidate on the
> target segment; every candidate is worse than the baseline there, so the
> closed decision is selection-invariant.

Alternative, if page budget forbids even that: drop the three BK1→BK2 rows from
Table I and describe them in one sentence as a limited transfer check. The paper
already de-weights them ("limited BK1→BK2 transfer checks"), and the slides
already label them "a limited transfer check; per-split counts were not
preserved."

**Priority: P1, not P0.** No claim is wrong, no number is wrong, and no decision
changes. Do this at the next natural paper pass, not as an emergency edit — and
only alongside a page-budget trim, since the paper has zero slack.

---

## 5. Advisor Q&A talking points from this campaign

**"Did you test whether it generalizes to other satellites?"**
No — and the honest reason is that only two satellites, both BLACK KITE family
with ~6 h cadence and no orbit-regime diversity, have ever entered the pipeline.
The runner and schema for a proper matrix now exist; it needs a third satellite
outside the family before any generalization word is used.

**"Your cross-satellite rows show 275 %. Isn't that your strongest number?"**
It is the largest number, not the strongest evidence. Three rows, one ordered
pair, and the degradation is not even monotone across staleness (worse at 8 and
24 h, better at 48 h than target-specific). Paper and slides both de-weight it
deliberately.

**"What did the 1500 Hz screen throw away?"**
0/6/5/11/13/19 pairs across 8→168 h, with magnitudes 1.4×–20× above threshold —
2072 Hz up to 30574 Hz. That population is manoeuvre / bad-OD, not borderline
drift. What is still unknown is the residual energy those pairs carried and
whether they were learnable; `reject_sensitivity_summary.csv` is built to answer
exactly that once the raw archive is back. Do not defend the screen as neutral.

**"Why is target-specific failing more interesting than transfer failing?"**
Because target-specific removes the domain-shift explanation entirely. The model
trains and validates on the satellite it deploys to, and still loses to SGP4 —
including the constant-median-bias baseline, which has essentially no variance
cost. That points at residual scale and near-zero mean, not at distribution
mismatch.

**"Is the gate actually doing anything?"**
On this data it prevents false opens on nine rows where nothing should deploy.
It has never been tested for missed opens on real data, because no real row
contains a learnable residual. The synthetic branch is the only demonstration
that it can open.
