COMPANY = Petopia Inc.
ROLE    = Software Support Analyst
TYPE    = technical
DATE    = 2025-06-01

ROOT   := $(shell cd ../.. && pwd)
SLUG   := $(notdir $(CURDIR))
RESUME := Alex Johnson - $(COMPANY) Resume.pdf
LETTER := Alex Johnson - $(COMPANY) Letter.pdf

.PHONY: all resume letter open

all: resume letter

resume:
	cd $(ROOT) && pandoc --pdf-engine=xelatex \
	    --template=template/default_template.tex \
	    -o "jobs/$(SLUG)/$(RESUME)" \
	    "jobs/$(SLUG)/resume.md"
	@echo "Built: $(RESUME)"

letter:
	cd $(ROOT) && pandoc --pdf-engine=xelatex \
	    --template=template/template-letter.tex \
	    -o "jobs/$(SLUG)/$(LETTER)" \
	    "jobs/$(SLUG)/letter.md"
	@echo "Built: $(LETTER)"

open: all
	open "$(RESUME)" "$(LETTER)"
