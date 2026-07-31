# Narrative gap — P0 one-sentence test

Four reviewers read the visual candidate once, at reviewing speed, and answered six questions
independently. None saw any earlier review. The measurement is what a reviewer *forms on one pass*,
not what the paper could support under charitable re-reading.

## Convergence

| question | converged? | verdict |
|---|---|---|
| A. what problem | **yes, all** | chronological splitting constrains order within an existing table and leaves availability, membership, hidden state and unit choice unchecked |
| B. main idea | **yes, all** | validity as an executable contract with a three-valued verdict |
| D. why chronology fails | **yes, all** | and all three call it the paper's strongest passage |
| C. what is technically new | **no** | all three marked it **INFERRED** |
| E. why not assembled primitives | **no** | all three marked it **INFERRED**, and all three answered "largely, it is assembled" |
| F. what would be lost | **no** | all four marked it **INFERRED**; the paper never argues its own counterfactual |

So the paper communicates its problem and its gap well, and fails to communicate its contribution.

## The three verbatim diagnoses

> "C — INFER. The contributions list is explicit, but the paper simultaneously disclaims new
> estimators and tests, so I had to work out for myself what the residual novelty is. **That is a
> bad sign at the abstract level: a reviewer should not have to reconstruct the claim.**"

> "C — INFERRED. ... **the paper blurs novelty with engineering.**"

> "E — INFER, and weakly. §II-C is a related-work paragraph, **not an argument that the composition
> exceeds the parts.**"

## The failure mode P15 names, reached independently by all three

> "It reads to me as **'a list of validity rules plus a toolkit'** wrapped around one real
> statistical finding."

> "**The nineteen-rule framing oversells a thin core.** ... The paper would be stronger and more
> honest as *two relational checks plus a satellite-specific rule catalogue* than as a
> nineteen-rule framework."

> "A 'validity as executable CI contract' paper — nineteen rules across four layers, one calibrated
> abstaining gate that is textbook ICC(1) plus a permutation test."

One reviewer added the sharpest structural observation:

> "I could not tell whether **removing the layer structure would change any verdict**. If a reviewer
> cannot answer that after one read, the presentation needs work regardless of the underlying merit."

## What the reviewers *did* credit, unprompted

All three named the same two items as the residual novelty, which means the content is there and
only the framing is failing:

1. the differential-provenance asymmetry — identical manifest hash with differing output refutes
   completeness, and the converse is merely redundant, so the property is falsifiable *without
   enumerating the input space*;
2. the calibrated gate that **abstains** — one reviewer put it precisely: "nobody in the cited
   statistical tradition ships a specificity/power curve and a refusal semantics as a CI verdict."

## One real defect, found by the fourth reviewer

> "the abstract and Fig. 1 promise a three-valued decision (PASS/HALT/INDETERMINATE), but Table II
> reports five values by adding N/A and N/OBS, and the text then calls it a 'five-valued contract.'
> **Either the semantics are three-valued or they are five-valued; as written I could not tell which
> is the claim.**"

Correct, and it is a defect introduced by this campaign rather than a misreading. The distinction
the paper needed to state: a *rule verdict* is three-valued (`PASS`, `HALT`, `INDETERMINATE`) and is
what a rule returns when the obligation applies; *not applicable* and *not observable* are
**audit dispositions** about whether the obligation arises and whether the artifact exposes enough
to run the rule at all. Five outcomes are recorded when auditing someone else's artifact; three are
returned by a rule. Both are true, and the paper asserted them without distinguishing them.

## Diagnosis

The paper leads with the nineteen rules and the four layers. Those are the least novel part, they
dominate the abstract, the contributions, Fig. 1 and Table I, and they cause every reviewer to
summarise the work as a checklist. The two relational checks — which every reviewer independently
identified as the actual contribution — arrive as items *inside* a list of nineteen.

The fix is not more prose defending the composition. It is to lead with the two relational checks,
state the primitives-versus-method distinction outright rather than leaving it to §II-C's
related-work paragraph, and say plainly what would be lost without the work.

## Actions taken in this loop

- The conceptual pivot (row-local versus relational validity) moved into the Introduction as the
  paper's stated foundation, rather than being inferable from contribution 1.
- Three obvious repairs are ruled out explicitly, so the method reads as necessary.
- Primitives and method are separated in a dedicated statement.
- The contributions lead with the two relational checks; the nineteen rules become the
  instantiation rather than the headline.
- The counterfactual is stated, so F does not have to be assembled by the reader.
