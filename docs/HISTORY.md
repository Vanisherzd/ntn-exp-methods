# History — lineage, not evidence

Current research: *Orbit-Evidence: Relational Validity Checks for Learning-Assisted Satellite
Communication Experiments* (`paper/icc_main.tex`).

An earlier research line pursued a learning-assisted satellite control problem: a learned
correction to a physical orbital prediction, with deployment gated on validation evidence. That
line was **stopped**. Two independent failures ended it, and both were found by auditing rather
than by a disappointing result: the label source proved missing-not-at-random on the very
covariate under study, and a controlled replacement benchmark failed its own negative control.

Those failures were first handled as individual experiment bugs. Generalising from them to what
they shared — each needed a comparison that a single realised run does not contain — is what
produced *relational validity*, and this paper. That generalisation is the only thing carried
forward.

**No scientific result from the stopped line is evidence for the current paper.** Its performance
figures are withdrawn. The current paper claims no RF, packet, link-layer, Doppler-residual or
learned-accuracy result, and that boundary is enforced mechanically: `paper/scripts/check_banlist.py`
fails the paper build on any banned result or phrase, and `talk/advisor_review/check_numbers.py`
confines stopped-line vocabulary to a single labelled appendix and bans every stopped-line quantity
from the deck outright.

The stopped line's source, experiments, audits and decks are **no longer in this checkout**. They
remain fully recoverable from Git history and from the verified pre-cleanup bundle recorded in
[CLEANUP_RECORD.md](CLEANUP_RECORD.md). One file was retained because active submission metadata
references it: `archive/KNOWN_INVALID_RESULTS.md`, the record of results that must never be reused.
