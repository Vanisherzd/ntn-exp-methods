# Orbit-Evidence -- canonical entry point. Everything runs from the repository root.
#
#     make gate         full submission gate: tests, matrix, claims, paper (the CI target)
#     make gate-twice    run the gate twice and assert the summary artifact is identical
#     make test          regression + fault-injection tests
#     make matrix        re-run the fault-injection matrix and the summary artifact
#     make paper         build paper/icc_main.pdf
#     make verify        assert the six-page submission invariants
#     make realdata      re-run the real-catalogue L4.7 application (needs dataraw/, local)
#     make external      re-run the third-party artifact study (needs a network clone)
#     make clean         remove regenerable products only (never sources or evidence)
#
# WHAT `make gate` DOES AND DOES NOT REGENERATE. It regenerates the fault matrix, the L4.7
# calibration and the operating curve on every run. It does NOT regenerate the two external
# evidence artifacts, because neither input ships with the repository: the real-data application
# needs dataraw/ (Space-Track records, untracked local data) and the third-party study needs a
# network clone at a frozen commit. Their artifacts are committed and the gate READS them, and it
# refuses to build if the contract's sha256 differs from the pre-registration hash, if the frozen
# third-party commit is not the registered one, or if the two studies disagree about which
# contract version they ran against. That is weaker than regeneration and is stated as such --
# claiming otherwise is the exact defect that let a stale calibration through once already.
#
# `clean` never removes: paper/icc_main.tex, paper/refs.bib, figure or table sources,
# anything under evaluation/results/, or anything under archive/.

PY      := python3
SUMMARY := evaluation/results/final_summary.json

.PHONY: all gate gate-twice test matrix summary claims paper verify clean realdata external \
        external-consequence-verify external-consequence-run

all: paper

# ---------------------------------------------------------------- gate
# Order matters: evidence FIRST, then the tests and claims that read it, then the document.
# `test` runs check_banlist against the committed tree, and `claims` reads the summary, so both
# consume matrix output. With `test` first they read whatever the previous run left behind: a
# runtime measured on a loaded machine kept failing the gate here, and re-running could not clear
# it because the stale artifact was re-read before `matrix` ever regenerated it.
gate: matrix test claims verify
	@echo ""
	@echo "SUBMISSION GATE: PASS"

# S4D: the gate must be repeatable. Results and claims must reproduce exactly;
# wall-clock timings are not expected to and are excluded from the comparison.
gate-twice:
	@$(MAKE) --no-print-directory gate
	@cp $(SUMMARY) /tmp/orbit_evidence_summary_run1.json
	@$(MAKE) --no-print-directory clean >/dev/null
	@$(MAKE) --no-print-directory gate
	@$(PY) scripts/compare_summaries.py /tmp/orbit_evidence_summary_run1.json $(SUMMARY)
	@echo "SUBMISSION GATE: PASS TWICE, summary artifact reproduced"

# ---------------------------------------------------------------- parts
test:
	@echo "== tests"
	@$(PY) -m pytest tests/regression tests/fault_injection -q

matrix:
	@echo "== fault-injection matrix"
	@$(PY) evaluation/scripts/run_matrix.py >/dev/null
	@echo "== L4.7 calibration and operating curve (Fig. 2)"
	@$(PY) evaluation/scripts/calibrate_l47.py >/dev/null
	@$(MAKE) --no-print-directory summary

summary:
	@$(PY) evaluation/scripts/make_final_summary.py >/dev/null
	@echo "   wrote $(SUMMARY)"

# Banned invalid results, withdrawn claims, and every headline number in the
# manuscript checked against the summary artifact.
claims:
	@echo "== claim and banlist gate"
	@$(PY) paper/scripts/check_banlist.py

paper:
	@$(MAKE) --no-print-directory -C paper

verify:
	@echo "== paper build and submission invariants"
	@$(MAKE) --no-print-directory -C paper verify

# Re-derivable only where the inputs are present. Both print what they need rather than
# failing obscurely, and both refuse to run against a different contract than the registered one.
realdata:
	@echo "== real-catalogue L4.7 application (needs dataraw/)"
	@test -d dataraw/spacetrack || { echo "   dataraw/spacetrack absent -- untracked local data, skipping"; exit 0; }
	@$(PY) evaluation/scripts/real_l47_application.py
	@$(PY) evaluation/scripts/object_level_timing.py
	@$(MAKE) --no-print-directory summary

external:
	@echo "== third-party artifact study (needs a clone at the frozen commit)"
	@test -n "$(TELEMANOM)" || { echo "   set TELEMANOM=/path/to/clone; see evaluation/external/SELECTION.md"; exit 1; }
	@$(PY) evaluation/scripts/external_artifact_study.py --repo "$(TELEMANOM)"
	@$(MAKE) --no-print-directory summary

# The consequence experiment could be neither checked nor re-run by an artifact evaluator: its
# scripts had no target, its inputs do not ship, and re-running it trains five paired seeds twice.
# Two entry points now exist. VERIFY checks the committed artifacts against the frozen commit, the
# frozen detector and the recorded data hashes, and trains nothing. RUN reproduces the experiment
# and fails closed if any of those is absent -- it never substitutes synthetic data.
external-consequence-verify:
	@echo "== external consequence: verify committed artifacts (no training)"
	@$(PY) evaluation/scripts/external_consequence_verify.py

external-consequence-run:
	@echo "== external consequence: full paired run (trains 5 seeds x 2 arms)"
	@test -n "$(TELEMANOM)" || { echo "   set TELEMANOM=/path/to/clone at 2e6c5b6c; see evaluation/external/SELECTION.md"; exit 1; }
	@test -n "$(DATA_ROOT)" || { echo "   set DATA_ROOT=/path/to/telemanom/data/data (must contain train/A-1.npy and test/A-1.npy)"; exit 1; }
	@test -f "$(DATA_ROOT)/train/A-1.npy" || { echo "   $(DATA_ROOT)/train/A-1.npy absent -- refusing to run"; exit 1; }
	@test -f "$(DATA_ROOT)/test/A-1.npy" || { echo "   $(DATA_ROOT)/test/A-1.npy absent -- refusing to run"; exit 1; }
	@$(PY) evaluation/scripts/external_consequence.py --repo "$(TELEMANOM)" --data "$(DATA_ROOT)"
	@$(MAKE) --no-print-directory external-consequence-verify

clean:
	@$(MAKE) --no-print-directory -C paper clean
	@find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache
	@echo "cleaned regenerable products (sources and evidence untouched)"
