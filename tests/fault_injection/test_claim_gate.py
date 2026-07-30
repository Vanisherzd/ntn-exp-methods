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
_MUTABLE = ("paper/icc_main.tex", "paper/figures/fig_contract.tex", SUMMARY,
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
    assert "artifact numbers bound to the artifact" in r.stdout


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
    p = repo / "paper/figures/fig_contract.tex"
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
    assert "MISSING" in r.stdout


def test_rejects_a_runtime_that_breaks_the_stated_bound(repo):
    """The manuscript claims the sweep runs in under 2 s. That is a claim about the
    artifact, so the artifact must still satisfy it."""
    _drift(repo, "runtime_seconds", 7.5)
    r = _gate(repo)
    assert r.returncode != 0 and "RUNTIME" in r.stdout


def test_refuses_to_run_without_the_artifact(repo):
    """No artifact means no verification. Passing would be worse than failing."""
    (repo / SUMMARY).unlink()
    r = _gate(repo)
    assert r.returncode != 0 and "missing" in r.stdout.lower()
