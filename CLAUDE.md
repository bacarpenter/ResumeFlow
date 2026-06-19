# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

ResumeFlow is an AI-assisted job application toolkit. Users write their resume in Markdown, then use Claude Code skills to tailor it to specific job descriptions and compile it to PDF using Pandoc + XeLaTeX. A CSV tracker and HTML dashboard track application status over time.

## First-time setup

```bash
python3 setup.py          # enter your name, email, phone, LinkedIn
/gather-background        # in Claude Code — interview to build your career profile
make build                # compile base resume to output/resume.pdf
```

`setup.py` writes `user.yaml` (gitignored) and applies your contact info to the base markdown files. `/gather-background` writes `markdown/background.md` with your full career context.

## Build commands

```bash
# Compile the base resume (for preview / testing)
make build

# Build a specific job application
make job JOB=001_petopia_inc

# Build resume only for a job
make resume -C jobs/001_petopia_inc/

# Build cover letter only (after you've written the body)
make letter -C jobs/001_petopia_inc/

# Generate the application tracker dashboard
make dashboard
open site/dashboard.html
```

## Claude Code skills

### `/gather-background`

Onboarding skill for new users. Run after `setup.py`. It asks you to paste an existing resume or answer questions, then writes `markdown/background.md` — a structured profile that `/tailor-resume` reads before every session. Optionally drafts `markdown/full_resume.md` and `markdown/general_resume.md`.

### `/tailor-resume`

Core skill. Provide company name, job title, and full JD on three lines. The skill:
1. Reads `markdown/background.md` to understand who you are
2. Picks the right base resume (technical vs. general)
3. Runs `python3 newJD.py` to scaffold `jobs/NNN_company/`
4. Edits `resume.md` to surface ATS keywords from the JD
5. Primes `letter.md` with the company/date headers — you write the body
6. Compiles the resume PDF and logs the application to `tracker.csv`

## Cover letters

`letter.md` is scaffolded automatically by `/tailor-resume` (contact block and YAML front matter pre-filled). Write the body yourself — 3-4 paragraphs. When ready:

```bash
make letter -C jobs/NNN_company/
```

The template expects a handwritten signature at `template/signature.png`. Add your own or remove the `signature:` fields from the YAML front matter to omit it.

## Markdown resume format

Resumes use a YAML front matter block followed by standard Markdown:

```markdown
---
mainfont: Times New Roman
top-margin: 0.5in
---
# Your Name

**Phone:** ... | **Email:** ... | **LinkedIn:** ...

## Section Heading

### **Title** | *Company* | *Date Range*

- bullet
```

Heading levels: `#` (name, once), `##` (section with rule), `###` (entry header).

`markdown/full_resume.md` is the technical base resume (projects section included).  
`markdown/general_resume.md` is the general base (no projects, softer skills).  
`markdown/background.md` is the biographical context file for Claude — not compiled to PDF.

## `newJD.py`

Scaffolds a new job application directory. Called automatically by `/tailor-resume`, but can also be used directly:

```bash
python3 newJD.py --company "Acme Corp" --role "Software Engineer" --type technical
```

Requires `user.yaml` to exist. Reads your name from it for PDF filenames.

## `dashboard.py`

Reads `tracker.csv` and writes `site/dashboard.html` (gitignored). Run via `make dashboard`.

## Template variables (YAML front matter)

The LaTeX template (`template/default_template.tex`) supports these Pandoc variables:

| Variable | Effect |
|---|---|
| `mainfont` | System font name (e.g. `Times New Roman`). Falls back to Gentium Plus if omitted. |
| `fontsize` | Font size (e.g. `11pt`) |
| `margin` | All margins (e.g. `0.75in`) |
| `top-margin` / `bottom-margin` / `left-margin` / `right-margin` | Individual margins |
| `title-color` | Color name for `##` section headings |

## Architecture

The PDF build pipeline is a direct `pandoc --pdf-engine=xelatex` call with a LaTeX template. No Python wrapping — the root `Makefile` and per-job `Makefile`s invoke pandoc directly.

`template/default_template.tex` is a standard Pandoc LaTeX template (`$variable$` / `$if(var)$` syntax). It produces dark-blue `##` section headings with a rule, dotted lines under `###` entries, compact list spacing, and clickable hyperlinks.

`template/template-letter.tex` is the cover letter template, using the `letter` documentclass.

The `jobs/` directory holds one subdirectory per application. Each contains `resume.md` (tailored), `letter.md` (manual), `jd.txt` (raw JD), and a `Makefile`. Demo entries (`001_petopia_inc`, etc.) show the complete structure.
