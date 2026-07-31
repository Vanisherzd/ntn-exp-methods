# Final novelty-rebalance cycle — return

Branch `submission/orbit-evidence-workshop` @ `b9db5a8`. `main` untouched. No submission tag.

## Recommendation: IMPROVED SUBMISSION READY

Not because reviewers graded it higher — they did not. Because the baseline is now **known to
contain wrong numbers**: the false-halt rate 19/450 = 0.042 with Wilson [0.027, 0.065], and a
Fig. 2 whose axis ticks disagreed with its own data and caption. Keeping the baseline means
submitting values that this cycle proved stale, and a flagship figure that understates its own
result when read off its own axis.

## Step 0 — reviewer findings against current HEAD

| item | status at entry |
|---|---|
| §I-A ↔ §II-A cross references | VERIFIED_CURRENT — present and consistent; compressed this cycle, mapping retained |
| current LOC count | VERIFIED_CURRENT — 833, gate-bound |
| current L4.6 wording | ALREADY_FIXED — variation-set limitation present |
| current L4.3 wording | ALREADY_FIXED — classified as a support heuristic with its 0.17 null size disclosed |
| current title | ACTION_REQUIRED → retitled to *Relational Validity Checks* |
| current Fig. 2 | ACTION_REQUIRED — replaced with the operating curve, then found misplotted and repaired |
| current `l47_power_curve.json` | ACTION_REQUIRED — `power_curve()` was unreachable after `raise SystemExit(main())`; now wired into `make matrix` |
| current references | ACTION_REQUIRED → two truncated titles restored; Vallado miscitation already replaced |

## What changed

**Novelty presentation (the cycle's stated goal).** Retitled; contribution 1 is now the
relational formulation (4 cross-execution + 1 cross-level, corrected from my own wrong claim
that L4.7 was cross-execution); Fig. 2 is the L4.7 operating curve, not the coverage matrix;
17/17 is two compact rows in Table I labelled "a regression artifact, not the novelty result";
PASS/HALT/INDETERMINATE appears in the abstract, contributions, Fig. 2, §III-A and the
conclusion; prior art credited to hermetic builds (L4.6) and to ICC(1)/permutation inference
(L4.7); core and support rules separated.

**Integrity defects found and fixed — the substantive work of the cycle.**

1. The calibration was **hand-typed literals**, so the gate compared the paper against a
   transcription. A reviewer moved the measured count 19 → 14 and `make gate` still passed on
   0.042. Now read from `l47_calibration.json`, written by `make matrix`.
2. The gate's binding was **required-presence**, defeatable two ways (the count 17 satisfied by
   the seventeen fault classes; a moved rate of 0.038 satisfied by Fig. 2's coordinate
   `(0.038,0.05)`), and could not express a wrong manuscript at all. Replaced with
   `\artv{key}{value}` claim sites and per-claim agreement. 17 numbers bound; 11 attacks fire.
3. §II specified the **anticonservative quantile rule the code discards**, never naming the
   +1/(B+1) correction on which validity turns.
4. **Fig. 2 was plotted at x = 5·ICC while ticked in ICC** — "0.5" at ICC 0.4, "0.8" at ICC 0.6,
   the curve past the end of its axis, `\clip` after `\draw`, and no marker on the headline point.
5. Two **L4.7 guards overstated the design**: the abstention floor counted labelled groups
   including singletons, and a unit in two coarser groups was silently accepted.
6. The **6.4 pt glyph floor was unenforced**; wiring it in caught `\textsc{halt}` at 5.55 pt.
7. The **publication lag was pooled over records** — one object supplies 82.4% of them. At the
   object level the median is 6.36 h, not 1.68 h, which makes the two-clock premise stronger.
8. Two enumerations of the **six state channels listed five**.
9. The **nineteen rules were not enumerable** from the submission after Table I was compressed.

## Verdicts

| | R-N1 | R-N2 | R-N3 | R-N4 |
|---|---|---|---|---|
| scope | novelty, code | statistics | satellite/NTN | reject advocate |
| verdict | WEAK ACCEPT | WEAK ACCEPT | WEAK REJECT | WEAK REJECT |
| novelty | 2 | 3 | 2.5 | 2 |
| internal report? | — | — | **NO** | YES |

Novelty did **not** move: 2 → {2, 3, 2.5, 2}. The retitle and rebalance did not change how
reviewers score originality. R-N3's NO is the first time any reviewer has said the paper does
not read primarily as an internal report.

## Why the loop stops

Eight reviewers over three cycles have asked for the same thing and only that thing: contact
with an artifact the authors did not produce. R-N4 states it needs new experiments; R-N3 says
one such cycle would make it ACCEPT. No reviewer asked for further reframing. Presentation work
cannot supply an external anchor, and new experiments have been out of scope in every cycle.

**The single highest-value next step, from R-N3:** run L4.7 on the already-committed
eleven-object, 63,727-record dataset at both element-set and object level and report the
measured ICC. It uses data in the repository, needs no new collection, and would tell a reader
whether the rule's blind zone below ICC 0.1 is even relevant to the flagship use case.

## Gate

`make gate` and `make gate-twice` both pass from a clean `git archive HEAD`: 62 tests, 6 pages,
0 LaTeX errors, 0 undefined refs/cites, 0 overfull hboxes, 0.0 pt overfull vbox, min author-set
glyph ≥ 6.4 pt, banlist clean, 17 numbers bound, 26 summary fields reproduced including
`matrix_sha256`.
