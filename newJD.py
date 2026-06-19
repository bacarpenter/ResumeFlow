#!/usr/bin/env python3
"""Bootstrap a new job application directory.

Usage:
    python newJD.py --company "ACME Corp" --role "Software Engineer" --type technical

Prints the created job directory path to stdout.
Requires user.yaml to exist — run `python3 setup.py` first.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent


def load_user_config() -> dict:
    path = ROOT / "user.yaml"
    if not path.exists():
        sys.exit("Error: user.yaml not found. Run `python3 setup.py` first.")
    config = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        config[key.strip()] = val.strip().strip('"').strip("'")
    return config


def get_next_id() -> int:
    id_file = ROOT / "next_id.txt"
    if id_file.exists():
        next_id = int(id_file.read_text().strip())
    else:
        existing = sorted((ROOT / "jobs").glob("???_*"))
        next_id = len(existing) + 1
    id_file.write_text(f"{next_id + 1}\n")
    return next_id


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def make_makefile(company: str, role: str, type_: str, name: str) -> str:
    today = date.today().strftime("%Y-%m-%d")
    return f"""\
COMPANY = {company}
ROLE    = {role}
TYPE    = {type_}
DATE    = {today}

ROOT   := $(shell cd ../.. && pwd)
SLUG   := $(notdir $(CURDIR))
RESUME := {name} - $(COMPANY) Resume.pdf
LETTER := {name} - $(COMPANY) Letter.pdf

.PHONY: all resume letter open

all: resume letter

resume:
\tcd $(ROOT) && pandoc --pdf-engine=xelatex \\
\t    --template=template/default_template.tex \\
\t    -o "jobs/$(SLUG)/$(RESUME)" \\
\t    "jobs/$(SLUG)/resume.md"
\t@echo "Built: $(RESUME)"

letter:
\tcd $(ROOT) && pandoc --pdf-engine=xelatex \\
\t    --template=template/template-letter.tex \\
\t    -o "jobs/$(SLUG)/$(LETTER)" \\
\t    "jobs/$(SLUG)/letter.md"
\t@echo "Built: $(LETTER)"

open: all
\topen "$(RESUME)" "$(LETTER)"
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--role", required=True, help="Job title")
    parser.add_argument(
        "--type",
        dest="type_",
        choices=["technical", "general"],
        default="technical",
        help="Resume type (default: technical)",
    )
    args = parser.parse_args()

    next_id = get_next_id()
    slug = f"{next_id:03d}_{slugify(args.company)}"
    job_dir = ROOT / "jobs" / slug
    job_dir.mkdir(parents=True, exist_ok=True)

    base_resume = "full_resume.md" if args.type_ == "technical" else "general_resume.md"
    (job_dir / "resume.md").write_text((ROOT / "markdown" / base_resume).read_text())

    letter_src = (ROOT / "markdown" / "example_letter.md").read_text()
    (job_dir / "letter.md").write_text(letter_src)

    cfg = load_user_config()
    name = cfg.get("name", "Your Name")
    (job_dir / "Makefile").write_text(make_makefile(args.company, args.role, args.type_, name))

    print(job_dir)


if __name__ == "__main__":
    main()
