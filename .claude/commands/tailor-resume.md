# Tailor Resume for a Job Description

You are helping the user tailor their resume for a specific job. Follow these steps precisely.

## Most important!!

You are helping a user tailor their resume for a specific job. You may not, under any circumstances make up, invent, or fabricate experiences or projects that are not present in `markdown/background.md`. Doing so will result in a poor resume at best, and leaving your user caught in a lie at worst.

## Before you begin

Read `markdown/background.md` to understand who the user is — their experience, skills, projects, values, and writing preferences. All biographical details come from that file. Do not use any hardcoded information.

## Input

The user will provide (in `$ARGUMENTS`):
- The **company name** on the first line
- The **job title** on the second line
- The **full job description** on the remaining lines

If the user did not provide all three parts, ask for them before proceeding.

Parse:
- `COMPANY` = first line of `$ARGUMENTS`, stripped
- `ROLE` = second line of `$ARGUMENTS`, stripped
- `JD` = everything from line 3 onward

## Step 1 — Read both base resumes

Read both files:
- `markdown/technical_resume.md` — technical resume (CS projects, engineering-heavy skills)
- `markdown/general_resume.md` — general resume (operations, customer service, no projects section)

## Step 2 — Choose the right base resume

Analyze the JD and classify the role:

**Use `technical_resume.md` (technical) if the JD:**
- Mentions software engineering, development, programming languages, or specific tech stacks
- Is for a role in engineering, data science, DevOps, IT, or similar technical domains
- Lists technical skills as requirements (Python, AWS, SQL, APIs, etc.)

**Use `general_resume.md` (general) if the JD:**
- Is primarily about customer service, operations, administration, sales, retail, banking, or management
- Does not require a technical background or lists tech only incidentally (e.g. "proficient in Microsoft Office")
- Would be better served by foregrounding the user's communication, leadership, and service experience

State which base you chose and one sentence explaining why. Set `TYPE` to `technical` or `general`.

## Step 3 — Scaffold the job directory

```bash
python3 newJD.py --company "<COMPANY>" --role "<ROLE>" --type <TYPE>
```

Capture the printed directory path (e.g. `jobs/003_acme_corp`). This is `JOB_DIR`.

The script creates:
- `JOB_DIR/resume.md` — copy of the correct base resume
- `JOB_DIR/letter.md` — cover letter template (contact block pre-filled; body is yours to write)
- `JOB_DIR/Makefile` — builds the resume and letter PDFs

## Step 4 — Analyze the JD for ATS keywords

Identify:
1. **Hard skills / technologies** explicitly mentioned
2. **Soft skills / action verbs** that appear repeatedly
3. **Domain terms** relevant to the role

Only surface keywords that are genuinely present (or latently demonstrable) in the user's actual experience on the chosen base resume.

## Step 5 — Plan targeted edits

For each keyword you can honestly incorporate, decide:
- Which bullet(s) to reword to surface that keyword naturally
- Which existing skill to rename/reorder to match JD terminology
- Whether to reorder sections (e.g. move Skills above Experience for a heavily skill-screened role)

**Hard rules — never break these:**
- Do not add technologies, roles, or accomplishments the user did not actually have
- Do not change dates, company names, or job titles
- Do not exaggerate metrics

## Step 6 — Edit `resume.md` in place

Edit `JOB_DIR/resume.md` directly (the file already exists from Step 3).

Preserve the exact YAML front matter. Apply the targeted edits from Step 5: reorder skills, reword bullets to surface ATS keywords. Keep all formatting conventions from the base resume.

After editing, briefly list the specific changes made and which keyword each targets. One line per change.

## Step 6b — Cover letter

The cover letter template is at `JOB_DIR/letter.md`. The YAML front matter (your contact info, date placeholder, company address) is already set up.

Update only these YAML fields:
- `date`: today's date spelled out (e.g. `5 June 2026`)
- `address`: company name + city (pull from JD if available)

Do NOT write the letter body. Leave the placeholder comment in place. Tell the user:

> "`letter.md` is ready for you to write. Open `JOB_DIR/letter.md` and fill in the body (3-4 paragraphs). When ready, run `make letter` inside the job directory to compile the PDF."

For reference, `markdown/background.md` contains the user's values and suggested cover letter tone — pass those along as a reminder if the JD is a strong fit for the user's stated goals.

## Step 7 — Compile the resume PDF

```bash
make resume -C <JOB_DIR>/
```

Report success or any compilation errors. (Do not compile the letter — the user hasn't written it yet.)

## Step 8 — Update the application tracker

The tracker lives at `tracker.csv`. If it doesn't exist, create it with this header:
```
Date,Job ID,Company,Role,Resume Type,PDF,ATS Keywords,Status
```

Read `user.yaml` to get the user's name for the PDF filename.

Append one row with:
- **Date**: today's date in `YYYY-MM-DD` format
- **Job ID**: the slug directory name from Step 3 (e.g. `011_acme_corp`)
- **Company**: the company name
- **Role**: the job title
- **Resume Type**: `technical` or `general`
- **PDF**: `JOB_DIR/[Name] - COMPANY Resume.pdf`
- **ATS Keywords**: a quoted comma-separated list of the top 5–8 ATS keywords targeted
- **Status**: `Applied` (always the default for new entries)

## Step 9 — Open the resume PDF

```bash
open "JOB_DIR/[Name] - COMPANY Resume.pdf"
```

## Step 10 — Final report

Tell the user:
1. Which base resume was used and why
2. The job directory path
3. The list of resume changes made (from Step 6)
4. A reminder that `letter.md` is ready to write, and the `make letter` command to compile it when done
5. Confirmation that the resume PDF compiled and opened
6. Confirmation that the tracker was updated
