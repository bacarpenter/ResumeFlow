#!/usr/bin/env python3
"""First-time setup for ResumeFlow.

Prompts for your personal contact details, writes user.yaml (gitignored),
and applies your info to the base resume and letter templates.

Run once when you first clone the repo, and again if you change your contact info.
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).parent

TOKENS = {
    "name": "{{YOUR_NAME}}",
    "email": "{{YOUR_EMAIL}}",
    "phone": "{{YOUR_PHONE}}",
    "linkedin": "{{YOUR_LINKEDIN}}",
    "location": "{{YOUR_LOCATION}}",
}

FILES_TO_PATCH = [
    ROOT / "markdown" / "full_resume.md",
    ROOT / "markdown" / "general_resume.md",
    ROOT / "markdown" / "example_letter.md",
    ROOT / "markdown" / "background.md",
]


def check_deps() -> None:
    missing = []
    if not shutil.which("pandoc"):
        missing.append("pandoc  →  brew install pandoc")
    if not shutil.which("xelatex"):
        missing.append("xelatex  →  brew install --cask mactex  (or install TeX Live)")
    if missing:
        print("Warning: missing system dependencies:")
        for m in missing:
            print(f"  {m}")
        print()


def read_existing_config() -> dict:
    path = ROOT / "user.yaml"
    if not path.exists():
        return {}
    config = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        config[key.strip()] = val.strip().strip('"').strip("'")
    return config


def prompt(label: str, current: str, example: str) -> str:
    if current and not current.startswith("{{"):
        default_hint = f" [{current}]"
    else:
        default_hint = f" (e.g. {example})"
    answer = input(f"{label}{default_hint}: ").strip()
    if not answer and current and not current.startswith("{{"):
        return current
    if not answer:
        print(f"  {label} cannot be empty.")
        return prompt(label, current, example)
    return answer


def write_user_yaml(values: dict) -> None:
    path = ROOT / "user.yaml"
    lines = [
        "# ResumeFlow — Personal Configuration (gitignored, never committed)\n",
        "\n",
    ]
    for key, val in values.items():
        lines.append(f'{key}: "{val}"\n')
    path.write_text("".join(lines))


def patch_files(values: dict) -> list[str]:
    patched = []
    for path in FILES_TO_PATCH:
        if not path.exists():
            continue
        original = path.read_text()
        updated = original
        for key, token in TOKENS.items():
            updated = updated.replace(token, values[key])
        if updated != original:
            path.write_text(updated)
            patched.append(str(path.relative_to(ROOT)))
    return patched


def main() -> None:
    print("ResumeFlow Setup\n")

    check_deps()

    existing = read_existing_config()

    print("Enter your contact details. Press Enter to keep the current value.\n")

    values = {
        "name": prompt("Full name", existing.get("name", ""), "Jane Smith"),
        "email": prompt("Email", existing.get("email", ""), "jane.smith@example.com"),
        "phone": prompt("Phone", existing.get("phone", ""), "(555) 123-4567"),
        "linkedin": prompt(
            "LinkedIn URL", existing.get("linkedin", ""), "linkedin.com/in/jane-smith"
        ),
        "location": prompt(
            "Location (city, province/state)",
            existing.get("location", ""),
            "Ottawa, ON",
        ),
    }

    print()
    write_user_yaml(values)
    print(f"Wrote user.yaml")

    patched = patch_files(values)
    if patched:
        for f in patched:
            print(f"Updated {f}")
    else:
        print("No token placeholders found in markdown files (already set up).")

    print()
    print("Setup complete. Next steps:")
    print("  1. Open Claude Code in this directory")
    print("  2. Run /gather-background to build your career profile")
    print("  3. Run make build to compile your base resume PDF")
    print("  4. Run /tailor-resume when you have a job to apply to")


if __name__ == "__main__":
    main()
