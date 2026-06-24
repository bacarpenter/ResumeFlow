# Gather User Background

You are onboarding a new user. Your goal is to learn enough about them to write a structured background profile that the `/tailor-resume` skill will read before every tailoring session, and optionally to draft their base resume files.

Work **conversationally** — ask one topic at a time. Do not dump all questions at once.

## Before starting

Check whether `user.yaml` exists and whether it still contains `{{YOUR_NAME}}` (unreplaced tokens). If so, tell the user:

> "Please run `python3 setup.py` first to fill in your contact details (name, email, phone, LinkedIn). Then come back and run `/gather-background`."

Then exit.

Otherwise, read `user.yaml` and note the user's name for reference throughout.

## Step 1 — Do you have an existing resume?

Ask:

> "Do you have a resume you'd like to paste in? I can extract your background from it. If you're starting from scratch, just say 'no'."

### If they paste a resume

Parse it for:
- Education: school, degree, graduation date, GPA/honors
- Work experience: each role with company, title, dates, responsibilities
- Projects: each with name, tech stack, what it does
- Skills: languages, tools, frameworks

Summarize what you found:

> "Here's what I extracted: [summary by section]. Does this look right? Anything missing, wrong, or that you'd rather not include?"

Then ask:

> "Are there any projects, roles, or skills you'd like to add that aren't on this resume?"

### If starting from scratch

Ask these sequentially — wait for each answer before asking the next:

1. **Education:** "What's your highest level of education? School name, degree, graduation date, and GPA or honors if you'd like them included."

2. **Work experience:** "Tell me about your work experience, starting with the most recent. For each role: company, job title, dates, and the 2–3 most important things you did there." Prompt "Anything else to add?" after each role, then "Any more roles?" until they say no.

3. **Projects:** "Any personal or academic projects you're proud of? For each: what it is, the tech stack, and what you'd want to highlight to a hiring manager." Same prompting pattern.

4. **Skills:** "What languages, frameworks, and tools are you comfortable with? List them however you like — I'll organize them."

5. **Job search focus:** "What kinds of roles are you targeting? And where — in-office, remote, specific cities or regions?"

## Step 2 — Writing preferences

Ask:

> "Any preferences for how your resume should sound? For example: more technical, more leadership-focused, concise, formal? And anything you'd like to avoid or de-emphasize?"

## Step 3 — Write `markdown/background.md`

Generate a structured background document and write it to `markdown/background.md`. Use this structure:

```markdown
# [Name] — Background & Profile

## Contact
See user.yaml for contact details.

## Summary
[2–3 sentence positioning statement: who they are, what they do, what they're targeting]

## Work Experience

**[Company] — [Job Title]** | [Location] | [Dates]
- [Key responsibility or accomplishment]
- [Key responsibility or accomplishment]
[For each role, add a FRAMING NOTE if relevant — e.g. "Best for: showing X, Y."]

## Education
**[Degree]** | [School] | [Graduation]
- [GPA / honors if included]
- [Other academic achievements]

## Projects

**[Project Name]** ([Tech stack])
[What it does and what to highlight when the JD is a match]

## Skills
[Organized by category: Languages, Backend & Infra, Tools, etc.]

## What I Care About
[Their values — use these in cover letters when the JD gives a genuine hook]

## Writing Voice
[Their stated preferences — tone, emphasis, things to avoid]
```

After writing, confirm:

> "I've written your background profile to `markdown/background.md`. The `/tailor-resume` skill reads this before every session — keep it up to date as your experience grows."

## Step 4 — Optionally draft base resumes

Ask:

> "Would you like me to draft your base resume files now?
> - `markdown/technical_resume.md` — technical version (projects, engineering skills prominent)
> - `markdown/general_resume.md` — general version (operations, service, communication)
>
> You can (and should!) always edit these manually. Generate them?"

If yes:

- Read `markdown/technical_resume.md` to understand the exact Pandoc markdown format (YAML front matter + heading hierarchy). Match it exactly.
- Write `markdown/technical_resume.md` with the user's real content.
- Write `markdown/general_resume.md` as a leaner version: drop the Projects section, lead with Experience, use softer skills in the Skills section.
- Use `{{YOUR_NAME}}`, `{{YOUR_EMAIL}}`, `{{YOUR_PHONE}}`, `{{YOUR_LINKEDIN}}`, `{{YOUR_LOCATION}}` tokens for all contact fields — this ensures they survive re-runs of `setup.py`.
- Run `make build` to verify the resume compiles to PDF.

If the build fails, diagnose and fix the Pandoc/LaTeX error before reporting success.

## Step 5 — Next steps

Tell the user:

- What files were written
- "Run `make build` to compile your base resume to `output/resume.pdf`"
- "Run `/tailor-resume` when you have a job to apply to — paste the company name, role, and full job description"
- "You can edit `markdown/background.md` any time to update your profile (new job, new project, change of direction)"
- "You can edit the resume files as well to update formatting, etc"
