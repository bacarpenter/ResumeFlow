COMPANY = Quantum Systems Ltd.
ROLE    = Backend Developer
TYPE    = technical
DATE    = 2025-06-05

ROOT   := $(shell cd ../.. && pwd)
SLUG   := $(notdir $(CURDIR))
RESUME := Alex Johnson - $(COMPANY) Resume.pdf

.PHONY: all resume open

all: resume

resume:
	cd $(ROOT) && pandoc --pdf-engine=xelatex \
	    --template=template/default_template.tex \
	    -o "jobs/$(SLUG)/$(RESUME)" \
	    "jobs/$(SLUG)/resume.md"
	@echo "Built: $(RESUME)"

open: resume
	open "$(RESUME)"
