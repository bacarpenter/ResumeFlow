# Build the base resume
build:
	@mkdir -p output
	pandoc --pdf-engine=xelatex \
	    --template=template/default_template.tex \
	    -o output/resume.pdf \
	    markdown/full_resume.md

# Build a specific job: make job JOB=001_marler_search_group
job:
	@[ -n "$(JOB)" ] || (echo "Usage: make job JOB=<job-dir>  (e.g. make job JOB=001_marler_search_group)"; exit 1)
	$(MAKE) -C jobs/$(JOB)

# List all job directories
list:
	@ls -1 jobs/

dashboard:
	python3 dashboard.py && open site/dashboard.html

.PHONY: build job list dashboard
