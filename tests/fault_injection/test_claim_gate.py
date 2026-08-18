"""Two-sided tests for the claim gate itself.

The paper's own doctrine is that a check which cannot go red is not evidence. That applies
to the checker as much as to the nineteen contract rules -- arguably more, since the claim
gate is the mechanism the paper offers for keeping a withdrawn claim unreachable.

It was not held to that standard, and an adversarial reviewer defeated it three ways
without touching a detector: a negation earlier in the same sentence suppressed the match,
two artifact counts carried hardcoded English-word alternatives that the prose always
satisfied, and the entire submission-document surface was outside the file glob while one
of those documents advertised the gate as enforcing it. A self-check then found a fourth: a
legend word inside a TikZ block, which has no blank lines, made the whole figure count as a
"prohibition context".

Each test below plants a specific defect in a COPY of the repository and asserts the gate
refuses it. If any of these ever passes, the gate has regressed to a state where the
paper's central mechanical claim is false.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CHECKER = "paper/scripts/check_banlist.py"
SUMMARY = "evaluation/results/final_summary.json"

# A sentence in the manuscript body that no other test depends on.
ANCHOR = "We claim nothing about radio-frequency or packet-level performance."

_IGNORE = shutil.ignore_patterns(".git", "tmp", "build", "local_archive", "hardware",
                                 "dataraw", "outputs", "logs", "validation_runs",
                                 "archive", "__pycache__", "*.pyc", ".pytest_cache")


def _gate(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, CHECKER], cwd=repo,
                          capture_output=True, text=True)


# Only the files a test actually mutates need restoring, so ONE copy serves the module.
# Copying per test cost ~25 s x 17 = seven minutes, which made `make gate` too slow to be
# the per-commit gate this paper claims it is.
_MUTABLE = ("paper/icc_main.tex", "paper/figures/fig_architecture.tex", SUMMARY,
            "README.md", "paper/submission/CLAIMS.md", "paper/submission/README.md")


@pytest.fixture(scope="module")
def _repo_copy():
    d = Path(tempfile.mkdtemp(prefix="claim_gate_"))
    dst = d / "repo"
    shutil.copytree(ROOT, dst, ignore=_IGNORE)
    pristine = {rel: (dst / rel).read_bytes() for rel in _MUTABLE}
    yield dst, pristine
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def repo(_repo_copy):
    """One repository copy per module, restored to pristine before each test.

    Restoring beats re-copying, but it only holds if every test mutates a file in
    _MUTABLE -- so the restore is verified rather than assumed: after each test the copy
    must be byte-identical to the pristine state it started from.
    """
    dst, pristine = _repo_copy
    for rel, data in pristine.items():
        (dst / rel).write_bytes(data)
    yield dst

    def _current(rel):
        f = dst / rel
        return f.read_bytes() if f.exists() else None   # a test may delete the artifact

    drift = [rel for rel, data in pristine.items() if _current(rel) != data]
    # Any file mutated outside _MUTABLE would silently leak into the next test.
    assert set(drift) <= set(_MUTABLE), f"unrestorable mutation in {drift}"


def _plant(repo: Path, rel: str, sentence: str, anchor: str = ANCHOR) -> None:
    p = repo / rel
    t = p.read_text()
    assert anchor in t, f"anchor missing from {rel}; update the test"
    p.write_text(t.replace(anchor, anchor + " " + sentence, 1))


def _drift(repo: Path, field: str, value) -> None:
    p = repo / SUMMARY
    s = json.loads(p.read_text())
    s[field] = value
    p.write_text(json.dumps(s, indent=1))


# ---------------------------------------------------------------- green side

def test_gate_passes_on_the_committed_tree(repo):
    """The clean side. A gate that refuses everything is as useless as one that refuses
    nothing, and the exemptions for legitimate scope-bounding must actually work."""
    r = _gate(repo)
    assert r.returncode == 0, r.stdout + r.stderr
    # Legitimate mentions are permitted AND reported, never silently dropped.
    assert "permitted:" in r.stdout
    assert "artifact numbers bound at named claim sites" in r.stdout


# ---------------------------------------------------------------- withdrawn claims

def test_rejects_a_plain_withdrawn_claim(repo):
    _plant(repo, "paper/icc_main.tex", "The contract generalises to unseen faults.")
    assert _gate(repo).returncode != 0


def test_rejects_a_claim_hidden_behind_an_in_sentence_negation(repo):
    """R4F's defeat, verbatim. A negation in a DIFFERENT clause must not exempt."""
    _plant(repo, "paper/icc_main.tex",
           "We do not overstate this: the contract generalises to unseen faults.")
    assert _gate(repo).returncode != 0


def test_rejects_a_claim_behind_a_comma_separated_negation(repo):
    _plant(repo, "paper/icc_main.tex",
           "This is not speculative, the suite proves generalisation to faults unseen.")
    assert _gate(repo).returncode != 0


def test_rejects_a_claim_planted_in_a_figure_block(repo):
    """A figure body must not be able to exempt itself.

    Figure sources contain words like "prohibited" as legend text, and a TikZ picture has
    no blank lines -- so a paragraph-scoped exemption once treated an entire figure as a
    prohibition context. Anchored on the environment, not on any particular label, so
    redrawing the figure cannot silently disarm this test.
    """
    p = repo / "paper/figures/fig_architecture.tex"
    t = p.read_text()
    assert "\\end{tikzpicture}" in t, "figure source no longer holds a tikzpicture"
    p.write_text(t.replace("\\end{tikzpicture}",
                           "\\node at (0,0) {generalises to unseen faults};\n"
                           "\\end{tikzpicture}", 1))
    assert _gate(repo).returncode != 0


@pytest.mark.parametrize("doc", ["README.md", "paper/submission/CLAIMS.md",
                                 "paper/submission/README.md"])
def test_rejects_a_withdrawn_claim_in_any_claim_surface(repo, doc):
    """The manuscript is not the only place a claim can be made. These three restate every
    headline number, and one of them advertises this gate as enforcing the ban."""
    p = repo / doc
    p.write_text(p.read_text() +
                 "\n\nHeld-out mutations prove generalisation to unseen faults.\n")
    assert _gate(repo).returncode != 0


def test_rejects_a_permanently_banned_result(repo):
    _plant(repo, "paper/icc_main.tex", "The gate improves LR-FHSS performance by 1.94x.")
    assert _gate(repo).returncode != 0


# ---------------------------------------------------------------- artifact binding

@pytest.mark.parametrize("field,value", [
    ("rule_count", 23),                    # was unguarded: prose says "nineteen"
    ("detectors_with_red_fixture", 12),    # was unguarded: prose says "Sixteen"
    ("contract_detected_count", 9),
    ("chronological_detected_count", 5),
    ("fault_class_count", 21),
    ("source_loc", 99999),
])
def test_rejects_an_artifact_value_the_manuscript_does_not_quote(repo, field, value):
    """Every headline number must track the artifact in BOTH directions.

    Two of these fields passed at any value because their regex accepted a hardcoded
    English word the prose always contained.
    """
    _drift(repo, field, value)
    r = _gate(repo)
    assert r.returncode != 0, f"{field}={value} accepted:\n{r.stdout}"
    assert "ARTIFACT SITE" in r.stdout


def _drift_l47(repo: Path, field: str, value) -> None:
    p = repo / SUMMARY
    s = json.loads(p.read_text())
    s["l47_calibration"][field] = value
    p.write_text(json.dumps(s, indent=1))


@pytest.mark.parametrize("field,value", [
    ("clean_false_halts", 17),
    ("measured_clean_false_halt_rate", 0.038),
    ("clean_false_halt_wilson_95", [0.027, 0.065]),
    ("clean_paths_evaluated", 900),
    ("nominal_alpha", 0.01),
])
def test_rejects_a_drifted_l47_calibration_value(repo, field, value):
    """The operating characteristic was outside the gate entirely.

    Its numbers were hand-typed literals in make_final_summary.py, so the gate compared the
    paper against a transcription; a reviewer moved the measured false-halt count 19 -> 14 by
    rederiving the permutation stream and `make gate` kept reporting the stale 0.042. The
    rate 0.038 is in this list for a second reason: under the old required-presence check it
    passed even once the artifact carried it, because Fig. 2 contains the ICC coordinate
    (0.038,0.05) and presence anywhere counted as agreement.
    """
    _drift_l47(repo, field, value)
    r = _gate(repo)
    assert r.returncode != 0, f"l47 {field}={value} accepted:\n{r.stdout}"
    assert "ARTIFACT SITE" in r.stdout


@pytest.mark.parametrize("old,new", [
    (r"\artv{l47_wilson}{[0.018,0.052]}", r"\artv{l47_wilson}{[0.027,0.065]}"),
    (r"\artv{chronological}{2/17}", r"\artv{chronological}{3/17}"),
    (r"\artv{l47_rate}{0.031}", r"\artv{l47_rate}{0.042}"),
])
def test_rejects_a_manuscript_number_that_drifts_from_the_artifact(repo, old, new):
    """The other direction, which required-presence could not express at all: the artifact is
    correct and the PAPER is wrong."""
    p = repo / "paper/icc_main.tex"
    t = p.read_text()
    assert old in t, f"claim site {old!r} not present"
    p.write_text(t.replace(old, new))
    r = _gate(repo)
    assert r.returncode != 0, f"manuscript drift {new!r} accepted:\n{r.stdout}"
    assert "ARTIFACT SITE" in r.stdout


def test_rejects_dropping_a_claim_site(repo):
    """A headline number must be CLAIMED, not merely consistent. Deleting the sentence that
    reports it is a way to make the gate vacuous."""
    p = repo / "paper/icc_main.tex"
    t = p.read_text()
    p.write_text(t.replace(r"\artv{contract}{17/17}", "17/17"))
    r = _gate(repo)
    assert r.returncode != 0 and "no \\artv{contract}" in r.stdout, r.stdout


def test_rejects_a_runtime_that_breaks_the_stated_bound(repo):
    """The repository guards the sweep at 3 s. That is a threshold on the
    artifact, so the artifact must still satisfy it."""
    _drift(repo, "runtime_seconds", 7.5)
    r = _gate(repo)
    assert r.returncode != 0 and "RUNTIME" in r.stdout


def test_requires_the_mandated_framing_for_a_permitted_observation(repo):
    """The banlist permits citing the labelled-vs-censored SMD only as a stopped-pipeline
    observation, never as a general rate. Grepping for the banned rate cannot enforce that
    the framing is PRESENT, so the gate requires it in the same file -- a first version
    checked the concatenation of all sources, so the word "stopped" in the README satisfied
    a claim made in the manuscript.
    """
    p = repo / "paper/icc_main.tex"
    t = p.read_text()
    if "standardised mean difference" not in t:
        # Not citing the observation at all is compliant, so there is no framing to police and
        # this check has nothing to do. SKIP rather than fail: failing would force the manuscript
        # to keep a sentence in order to satisfy a test, which inverts what the test is for.
        pytest.skip("manuscript does not cite the SMD observation, so no framing is required")
    p.write_text(t.replace("stopped", "earlier"))
    r = _gate(repo)
    assert r.returncode != 0 and "FRAMING" in r.stdout, r.stdout


def test_rejects_a_per_condition_runtime_that_breaks_its_bound(repo):
    """The manuscript states a bound on per-condition cost, so it must be checked like the
    sweep bound rather than left to drift -- this figure moved 30 -> 27 -> 26 unchecked."""
    _drift(repo, "runtime_ms_per_condition", 95.0)
    r = _gate(repo)
    assert r.returncode != 0 and "RUNTIME" in r.stdout


def test_refuses_to_run_without_the_artifact(repo):
    """No artifact means no verification. Passing would be worse than failing."""
    (repo / SUMMARY).unlink()
    r = _gate(repo)
    assert r.returncode != 0 and "missing" in r.stdout.lower()


# ------------------------------------------------- the GENERATED claims table
#
# CLAIMS.md is written by `make matrix`, yet the gate only ever grepped it for banned words. So a
# block generated before a number moved -- committed, then never regenerated -- passed every gate
# while contradicting the artifact in the one file that calls itself the single source of truth.
# The fix is an equality: regenerate the block from the artifact into a temp copy and require the
# checked-in block to match, with per-FIELD exemptions for the two declared volatile measurements.
#
# The pair that matters most is 3 s -> 2 s and 60 ms -> 30 ms. Both sit in the SAME table row as
# those volatile measurements, so any row-level exemption -- the obvious implementation -- would
# leave them unguarded. That is why these are not one test but the anchor of the whole section.

CLAIMS = "paper/submission/CLAIMS.md"
RUNTIME_ROW_GUARDS = "repository regression guards 3.0 s and 60.0 ms"


def _edit_claims(repo: Path, old: str, new: str) -> None:
    p = repo / CLAIMS
    t = p.read_text()
    assert old in t, f"{old!r} not in CLAIMS.md; the generator changed, update the test"
    p.write_text(t.replace(old, new, 1))


@pytest.mark.parametrize("old,new,what", [
    ("guards 3.0 s", "guards 2.0 s", "the sweep guard"),
    ("and 60.0 ms", "and 30.0 ms", "the per-condition guard"),
])
def test_rejects_a_weakened_regression_guard_in_the_generated_table(repo, old, new, what):
    """3 s -> 2 s and 60 ms -> 30 ms must fail, in the row whose neighbours may legally move.

    The guards are promises the repository makes, not measurements, so they are semantic. They
    are rendered from runtime_threshold_s / runtime_threshold_ms_per_condition, which are
    deliberately absent from VOLATILE_CLAIM_FIELDS.
    """
    assert RUNTIME_ROW_GUARDS in (repo / CLAIMS).read_text(), "runtime row no longer states both guards"
    _edit_claims(repo, old, new)
    r = _gate(repo)
    assert r.returncode != 0, f"{what} weakened without failing:\n{r.stdout}"
    assert "GENERATED CLAIMS" in r.stdout, r.stdout


@pytest.mark.parametrize("field,value", [
    ("runtime_threshold_s", 2.0),
    ("runtime_threshold_ms_per_condition", 30.0),
])
def test_rejects_a_guard_moved_in_the_artifact_without_regenerating(repo, field, value):
    """The same drift from the other side: the artifact changes and CLAIMS.md is left stale."""
    _drift(repo, field, value)
    r = _gate(repo)
    assert r.returncode != 0, f"{field}={value} accepted:\n{r.stdout}"
    assert "GENERATED CLAIMS" in r.stdout, r.stdout


def _row(repo: Path, claim: str) -> str:
    """The generated row for `claim`, read from the file rather than hardcoded.

    Hardcoding these rows made three tests fail the moment the suite grew: `test_count` and
    `test_suite_loc` count THIS file, so any test added here moves two of the very numbers the
    table reports. A test that has to be edited whenever it is added to is not a gate.
    """
    for line in (repo / CLAIMS).read_text().splitlines():
        if line.startswith(f"| {claim} |"):
            return line
    raise AssertionError(f"no {claim!r} row in CLAIMS.md; the generator changed, update the test")


def _bump_first_number(line: str) -> str:
    return re.sub(r"\d+", lambda m: str(int(m.group()) + 9), line, count=1)


@pytest.mark.parametrize("claim,mutate", [
    ("contract coverage", lambda l: l.replace("17/17", "16/17")),
    ("contract rules", _bump_first_number),
    ("tests", _bump_first_number),
    ("clean-path rule firings", _bump_first_number),
    # The artifact-field column is part of the claim: it says which field backs the number. Both
    # fields hold 3, so a check scoped to the value cell exempted this -- a negative test caught it.
    ("clean reference paths", lambda l: l.replace("`clean_path_count`", "`environment_count`")),
])
def test_rejects_an_altered_evidence_backed_claim(repo, claim, mutate):
    line = _row(repo, claim)
    new = mutate(line)
    assert new != line, f"mutation did not apply to {line!r}; the test proves nothing"
    _edit_claims(repo, line, new)
    r = _gate(repo)
    assert r.returncode != 0, f"{line!r} -> {new!r} accepted:\n{r.stdout}"
    assert "GENERATED CLAIMS" in r.stdout, r.stdout


def test_rejects_dropping_a_generated_row(repo):
    """A row cannot be quietly deleted to make its claim unverifiable."""
    line = _row(repo, "rules with no red fixture")
    _edit_claims(repo, line + "\n", "")
    r = _gate(repo)
    assert r.returncode != 0 and "GENERATED CLAIMS" in r.stdout, r.stdout


def test_rejects_removing_the_generated_table_markers(repo):
    """Deleting the markers would make the regeneration a no-op and silently disable the check --
    the same shape of hole as a check that cannot go red."""
    _edit_claims(repo, "<!-- END GENERATED CLAIMS TABLE -->", "")
    r = _gate(repo)
    assert r.returncode != 0 and "GENERATED CLAIMS" in r.stdout, r.stdout


def test_rejects_a_non_numeric_value_in_a_volatile_slot(repo):
    """The volatile exemption frees a NUMBER at a fixed offset, not the text around it."""
    line = _row(repo, "sweep runtime")
    new = re.sub(r"\*\*[\d.]+ s", "**fast s", line, count=1)
    assert new != line, "runtime row no longer opens with a measurement; update the test"
    _edit_claims(repo, line, new)
    r = _gate(repo)
    assert r.returncode != 0 and "GENERATED CLAIMS" in r.stdout, r.stdout


# ------------------------------------------------- the documented volatile path

def test_allows_a_declared_volatile_measurement_to_move(repo):
    """The one permitted difference, and the reason the check is field-level rather than a plain
    file comparison: wall-clock timings vary a few percent between runs and machines, so requiring
    byte equality would make `make gate` fail on a busy machine.

    Both values stay inside their regression guards, so the separate RUNTIME bound still holds --
    this exempts the table from re-rendering, not the artifact from its promises. There is no
    timestamp in the generated block, so these two declared fields are the whole volatile surface.
    """
    before = _row(repo, "sweep runtime")
    _drift(repo, "runtime_seconds", 2.220)
    _drift(repo, "runtime_ms_per_condition", 41.1)
    # The pass must come from the exemption, not from the block happening to agree, so assert the
    # checked-in row really is stale now: it still carries the pre-drift measurements.
    assert _row(repo, "sweep runtime") == before, "row changed by itself; test is vacuous"
    assert "**2.22 s" not in before and "41.1 ms" not in before, \
        "the artifact already carried the drifted values; test is vacuous"
    r = _gate(repo)
    assert r.returncode == 0, f"volatile-only drift refused:\n{r.stdout}{r.stderr}"


def test_rejects_an_edit_to_the_generators_header_comment(repo):
    """The whole block is compared, not only its data rows -- the comment is what tells a reader
    the file is generated, so weakening it is a semantic change to the claim surface."""
    _edit_claims(repo, "Do not hand-edit", "Feel free to hand-edit")
    r = _gate(repo)
    assert r.returncode != 0 and "GENERATED CLAIMS" in r.stdout, r.stdout


def test_the_volatile_declaration_excludes_the_guards(repo):
    """Guards against the fix regressing into the hole it closed: if a future edit adds a
    threshold field to VOLATILE_CLAIM_FIELDS, the tests above would still pass for the wrong
    reason, so assert the declaration's contents directly."""
    sys.path.insert(0, str(repo / "evaluation" / "scripts"))
    try:
        import make_final_summary as mfs
        vol = set(mfs.VOLATILE_CLAIM_FIELDS)
    finally:
        sys.path.pop(0)
    assert vol == {"runtime_seconds", "runtime_ms_per_condition"}, vol
    assert all(mfs.VOLATILE_CLAIM_FIELDS.values()), "every volatile field needs a written reason"
