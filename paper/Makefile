# Canonical build for the active manuscript. Run from repo root or from paper/.
#     make -C paper          build paper/icc_main.pdf
#     make -C paper clean    remove regenerable products only
#     make -C paper verify   build then assert the submission invariants

TEX      := icc_main.tex
PDF      := icc_main.pdf
BUILD    := build
LATEXMK  := latexmk
BANLIST  := scripts/check_banlist.py

.PHONY: all clean verify banlist

all: $(PDF)

$(PDF): $(TEX) refs.bib figures/*.tex tables/*.tex
	@python3 $(BANLIST)
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error -outdir=$(BUILD) $(TEX)
	@cp $(BUILD)/$(PDF) $(PDF)
	@echo "built $(PDF)"

banlist:
	@python3 $(BANLIST)

# Asserts the submission invariants: six pages, no undefined refs or citations,
# no LaTeX errors, no overfull boxes. Fails the build if any is violated.
verify: $(PDF)
	@python3 scripts/verify_build.py

# Removes ONLY regenerable products. Never touches icc_main.tex, refs.bib,
# figure or table sources, evaluation results, or archival evidence.
clean:
	$(LATEXMK) -C -outdir=$(BUILD) $(TEX) >/dev/null 2>&1 || true
	@rm -rf $(BUILD)
	@echo "cleaned regenerable products (sources untouched)"
