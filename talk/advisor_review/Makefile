# Advisor-review deck. Numbers are regenerated from the frozen artifacts first, every time, so a
# slide cannot quietly disagree with the paper it explains.
#
# This deck is NOT the workshop talk. The reviewer-proof workshop deck is built from talk/ and is
# never touched by these targets.
#
# NO OVERLAYS by design: every frame is final-state, so advisor_deck.pdf IS the handout. There is
# no separate final-state export to drift out of sync, and `check` fails if a future overlay makes
# the physical page count exceed the frame count.
PY  ?= python3
TEX := advisor_deck.tex
PDF := advisor_deck.pdf

.PHONY: all check render clean

all: $(PDF)

$(PDF): $(TEX) numbers.tex
	@latexmk -pdf -halt-on-error -interaction=nonstopmode $(TEX) >/dev/null 2>&1 || \
	  { latexmk -pdf -halt-on-error -interaction=nonstopmode $(TEX); exit 1; }
	@echo "   $(PDF): $$(pdfinfo $(PDF) | awk '/^Pages/{print $$2}') pages"
	@if grep -q Overfull advisor_deck.log; then \
	  echo "   WARNING: overfull boxes remain:"; \
	  grep -oE 'Overfull \\[hv]box \([0-9.]+pt too (high|wide)\) detected at line [0-9]+' \
	    advisor_deck.log | sed 's/^/     /'; \
	fi

numbers.tex: gen_numbers.py \
             ../../evaluation/results/final_summary.json \
             ../../evaluation/real_data/l47_alongtrack.json \
             ../../evaluation/results/l47_power_curve.json
	@$(PY) gen_numbers.py

# Nine gates: number currency, macro coverage, required numbers, no bare literals, semantic lint,
# required qualifiers, stopped-research isolation, frame architecture, no overlays.
check: numbers.tex
	@$(PY) check_numbers.py

# Page images for a visual audit. Layout defects that source review cannot see -- a connector
# crossing a box, a label sitting on a curve -- are only visible here.
render: $(PDF)
	@rm -f pg-*.png
	@pdftoppm -r 150 -png $(PDF) pg
	@echo "   rendered $$(ls -1 pg-*.png | wc -l | tr -d ' ') page images at 150 dpi"

clean:
	@latexmk -C >/dev/null 2>&1 || true
	@rm -f *.nav *.snm *.vrb pg-*.png
