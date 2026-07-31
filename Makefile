# Orbit-Evidence -- canonical entry point. Everything runs from the repository root.
#
#     make gate         full submission gate: tests, matrix, claims, paper (the CI target)
#     make gate-twice    run the gate twice and assert the summary artifact is identical
#     make test          regression + fault-injection tests
#     make matrix        re-run the fault-injection matrix and the summary artifact
#     make paper         build paper/icc_main.pdf
#     make verify        assert the six-page submission invariants
#     make clean         remove regenerable products only (never sources or evidence)
#
# `clean` never removes: paper/icc_main.tex, paper/refs.bib, figure or table sources,
# anything under evaluation/results/, or anything under archive/.

PY      := python3
SUMMARY := evaluation/results/final_summary.json

.PHONY: all gate gate-twice test matrix summary claims paper verify clean

all: paper

# ---------------------------------------------------------------- gate
# Order matters: evidence first, then the claims that quote it, then the document.
gate: test matrix claims verify
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

clean:
	@$(MAKE) --no-print-directory -C paper clean
	@find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache
	@echo "cleaned regenerable products (sources and evidence untouched)"
