# Talk build. Numbers are regenerated from the evidence artifact first, every time, so a slide
# cannot quietly disagree with the paper it presents.
PY  ?= python3
TEX := orbit_evidence_talk.tex
PDF := orbit_evidence_talk.pdf

.PHONY: all clean check

all: $(PDF)

$(PDF): $(TEX) numbers.tex figures/*.tex
	@latexmk -pdf -halt-on-error -interaction=nonstopmode $(TEX) >/dev/null 2>&1 || \
	  { latexmk -pdf -halt-on-error -interaction=nonstopmode $(TEX); exit 1; }
	@echo "   $(PDF): $$(pdfinfo $(PDF) | awk '/^Pages/{print $$2}') pages"

numbers.tex: gen_numbers.py ../evaluation/results/final_summary.json
	@$(PY) gen_numbers.py

# Refuse a deck whose numbers have drifted from the artifact.
check: numbers.tex
	@$(PY) check_numbers.py

clean:
	@latexmk -C >/dev/null 2>&1 || true
	@rm -f *.nav *.snm *.vrb
