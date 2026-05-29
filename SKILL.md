---
name: task-continuity
description: "maintain continuity for long-running office tasks with a clean two-layer workspace: the task root holds current durable memory, canonical materials, reusable knowledge, and latest deliverables, while runs hold temporary workbench files and phase history. use when a user starts, resumes, or changes multi-turn work; when deciding whether to reuse an active run; when promoting stable outputs out of runs; when proactively keeping task.md, request.md, index.json, and run summaries synchronized; or when the user asks to convert the current task or workspace into a reusable skill."
---

# Task Continuity

## Operating Model

Use this skill to keep long-running knowledge work continuous without letting files pile up. A task workspace has two layers:

1. **Task root = current durable truth.** Keep task-level memory, source materials, reusable knowledge, and the latest canonical deliverables here.
2. **Runs = workbench and phase history.** Keep scratch files, drafts, temporary exports, and phase-specific evidence inside the active run.

Do not let durable content stay trapped inside run folders. Do not dump every file into the root. Promote only files that are useful beyond the current run, and keep them in the correct root-level folder.

## Core Rules

1. Treat one task folder as one long-lived unit of work.
2. Read `task.md` first when entering an existing task.
3. Preserve the user's original wording in `request.md`, then append later clarifications or superseding instructions.
4. Keep `request.md` synchronized whenever the user changes requirements, constraints, examples, source materials, acceptance criteria, tone, audience, format, or deliverables.
5. Keep `task.md` current rather than historical. It should summarize current objective, durable context, decisions, canonical files, progress, risks, and next step.
6. Use the active run for the current work phase. A run is a meaningful phase or work session, not a single user message.
7. Reuse the active run for short follow-ups, wording tweaks, small revisions, and clarifications.
8. Before creating or saving any file, decide whether it is run-scoped or durable task-level content.
9. Promote durable files from runs to the task root before ending a turn that creates or materially updates them.
10. Update existing canonical files instead of creating repeated near-duplicates.
11. Keep tool calls, script invocations, raw temporary API results, and scratch transcripts out of persistent files unless the user explicitly asks for an audit record.
12. Keep all task outputs inside the task folder unless the user explicitly requests another location.
13. When converting a task into a Skill, read `references/task-to-skill-conversion.md` before designing or packaging the Skill.

## Default Location

Use a single tasks directory. If the user does not specify a location, default to `./tasks` in the current working directory.

## Task Folder Layout

```text
tasks/
└── <task-short-name>-YYYYMMDD/
    ├── task.md
    ├── request.md
    ├── index.json
    ├── task.log
    ├── error_notes.md
    ├── materials/
    │   └── <durable source files and briefs>
    ├── knowledge/
    │   └── <reusable analyses, style notes, decisions, schemas>
    ├── deliverables/
    │   └── current/
    │       └── <latest canonical outputs>
    ├── archive/
    │   └── <superseded durable files when replacement matters>
    └── runs/
        ├── 001-<run-short-name>-YYYYMMDD/
        │   ├── run_summary.md
        │   └── <scratch, drafts, temporary outputs, phase evidence>
        └── ...
```

The root-level markdown and JSON files are task memory. The root-level folders hold durable files that should survive across runs. The `runs/` folder holds workbench material and historical phase records.

See `references/task-files.md` for detailed file responsibilities.

## Task-To-Skill Conversion Trigger

When the user asks to convert the current task, task folder, or workflow into a reusable Skill, do not simply package the task folder. First read `references/task-to-skill-conversion.md`, then use the `skill-creator` workflow after reviewing the current task context.

Treat this as a deliberate conversion process:

1. Research the current task from root-level durable files first.
2. Identify which workflow, conventions, scripts, references, templates, and examples are reusable.
3. Classify task artifacts as include, adapt, exclude, or ask-for-confirmation.
4. Confirm Skill details with the user, including name, triggers, inputs, outputs, tools/connectors, files to include, and privacy boundaries.
5. Build, validate, and package the Skill as `skill.zip` only after the conversion plan is accepted or the user explicitly authorizes best-effort packaging.

Keep the conversion plan durable in `knowledge/skill_conversion_brief.md` when working inside a writable task folder.

## File Location Decision

Use this decision before writing a file:

| File type | Save location | Rule |
|---|---|---|
| Current task memory | `task.md`, `request.md`, `index.json`, `task.log`, `error_notes.md` | Update in place. Do not duplicate. |
| User-provided source, stable brief, reference data, reusable input | `materials/` | Promote from run or save directly here when it will be reused. |
| Durable analysis, reusable notes, decisions, style guide, schema, checklist | `knowledge/` | Keep concise and current. Replace or update instead of copying. |
| Latest canonical user-facing output | `deliverables/current/` | Use stable names like `proposal.md` or `summary.docx`; archive replaced versions only when needed. |
| Draft, scratch extraction, temporary conversion, phase-specific output | active `runs/<run>/` | Keep here only while it is not durable. |
| Superseded durable file worth retaining | `archive/` | Use timestamped names and link from `task.md` or `index.json` only when relevant. |

## Durable Promotion Rules

Promote a file out of a run when any condition is true:

- It is the latest deliverable the user should use next.
- It is a source material, brief, or reference that later runs must rely on.
- It contains durable conclusions, decisions, preferences, schemas, templates, or reusable analysis.
- The user says to keep it, use it later, make it final/current, or treat it as the version of record.
- A future ChatGPT instance would need the file without opening many run folders.

Do not promote scratch notes, failed attempts, raw temporary exports, or files that only explain how a tool was called.

When promoting:

1. Prefer **move** from run to root to avoid duplicates.
2. Prefer **copy** only when preserving an exact run snapshot is important.
3. If a current canonical file already exists and the new file supersedes it, move the old file to `archive/` or update it in place.
4. Update `index.json` so `canonical_files` points to the promoted file.
5. Update `task.md` so the `Canonical Files` or `Key Materials` section points to the root-level file.
6. Update the active `run_summary.md` with what was promoted, reused, or superseded.
7. Add only a short milestone to `task.log`.

The helper script can perform the file move/copy, archiving, index update, and log update:

```bash
python scripts/task_maintenance.py promote "./tasks/<task-folder>" "./tasks/<task-folder>/runs/<run>/<file>" --kind deliverable --name "proposal.md" --mode move --replace --json
```

## Create A New Task

Prefer the bundled script:

```bash
python scripts/init_task.py "<task title>" --root "./tasks" --run "initial-intake"
```

Optional:

```bash
python scripts/init_task.py "<task title>" --root "./tasks" --run "initial-intake" --request "<original user request>" --json
```

After initialization:

1. Save the user's original request in `request.md` if it was not passed to the script.
2. Fill `task.md` immediately with the current objective, known context, constraints, canonical files if any, and next step.
3. Fill useful `index.json` fields: aliases, tags, deliverable, active run, last run, and canonical files.
4. Use the first run for immediate scratch work.
5. Promote any stable source files or current deliverables to `materials/`, `knowledge/`, or `deliverables/current/` before ending.

## Resume An Existing Task

When resuming, read in this order:

1. `index.json`
2. `task.md`
3. `request.md`
4. the active run's `run_summary.md` or the latest `run_summary.md`
5. `error_notes.md`
6. specific files in `materials/`, `knowledge/`, `deliverables/current/`, or the active run only when needed

Do not re-read every file by default. Start from the current root-level memory and canonical files, then expand only when necessary.

You can locate the current active run without creating a new run:

```bash
python scripts/init_task.py --task-dir "./tasks/<task-folder>" --json
```

If the task was created with an older layout, ensure root folders and index keys exist:

```bash
python scripts/task_maintenance.py ensure "./tasks/<task-folder>" --json
```

## Active Run Reuse

Keep using the active run for:

- wording tweaks
- small structural changes
- quick clarifications
- adding one paragraph, section, table, or small output
- minor formatting cleanup
- short follow-up questions that continue the same immediate work
- repeated edits to the same deliverable in the same phase

Before creating a new file in the active run, check whether an existing file in the active run or `deliverables/current/` has the same purpose. Edit or replace that file instead of creating `new`, `final`, `final2`, or timestamped duplicates.

## Start A New Run

Create a new run only when the work meaningfully changes:

- intake to drafting
- drafting to review
- review to finalization
- finalization to a new deliverable
- source material changes substantially
- the user explicitly asks for a new phase or checkpoint

Good run names:

- `initial-intake`
- `extract-client-feedback`
- `draft-first-version`
- `revise-after-review`
- `prepare-final-summary`

Avoid vague names:

- `continue`
- `update`
- `misc`
- `work`

Create a new run explicitly:

```bash
python scripts/init_task.py --task-dir "./tasks/<task-folder>" --new-run --run "revise-after-review" --json
```

Do not create a new run merely because another user message arrived.

## Required Maintenance Pass Before Ending A Modifying Turn

Before responding after any meaningful work, perform this pass:

1. **Intent sync:** Update `request.md` when the user changed or clarified intent. Preserve earlier wording unless explicitly superseded.
2. **Durable promotion:** Move or copy files that should survive beyond the run into `materials/`, `knowledge/`, or `deliverables/current/`.
3. **Current state sync:** Update `task.md` with current objective, context, decisions, canonical files, progress, risks, and next step.
4. **Index sync:** Update `index.json` fields such as `status`, `last_updated`, `deliverable`, `active_run`, `last_run`, `aliases`, `tags`, and `canonical_files`.
5. **Run sync:** Update the active `run_summary.md` with files created/modified, files promoted to task root, decisions, and next step.
6. **Log only milestones:** Append concise milestones to `task.log`; do not turn it into a transcript.
7. **Error memory:** Add user dislikes, repeated mistakes, and durable risks to `error_notes.md`.
8. **Duplicate check:** If short-term duplicate files were created, remove, archive, or supersede them before finishing.

Use this helper when a duplicate review is useful:

```bash
python scripts/task_maintenance.py dedupe "./tasks/<task-folder>" --write-report --json
```

## Request Synchronization

`request.md` is not write-once. It is the canonical record of the user's evolving intent.

Use this structure:

```markdown
# User Request History

## Initial Request
<original wording>

## Clarifications And Changes
### YYYY-MM-DD HH:MM
<new user instruction or clarification>

### YYYY-MM-DD HH:MM - Supersedes earlier format request
<new instruction>
```

If a new instruction conflicts with an earlier one, mark it as superseding rather than deleting the older wording.

## Task.md Maintenance

`task.md` should be a compact resume file, not a pile of notes. Keep it current and prune stale details.

Maintain these sections:

- `Task Summary`
- `Current Status`
- `Current Objective`
- `Known Context`
- `User Preferences`
- `Constraints`
- `Decisions Already Made`
- `Canonical Files`
- `Progress`
- `Risks / Open Questions`
- `Next Recommended Step`
- `Recent Runs`

When a durable file is promoted, add or update its path in `Canonical Files`.

## Duplicate And Versioning Policy

- Use stable names for current canonical files: `proposal.md`, `client-summary.docx`, `source-notes.md`.
- Avoid names like `final-final`, `new-version`, `copy`, or timestamped names for current files.
- Use timestamped names only in `archive/` or when the user asks for dated snapshots.
- Prefer updating the existing current file when the user requests a minor change.
- Prefer archiving the previous current file when the change is substantial and history matters.
- Keep run folders useful but not bloated: after promotion, leave only scratch material and `run_summary.md` unless a run snapshot is intentionally needed.

## Boundaries

- Do not turn this into heavyweight project management.
- Do not create a new task because the wording changed slightly.
- Do not create a new run for every message.
- Do not leave stable deliverables, reusable materials, or durable decisions buried in runs.
- Do not put raw tool calls, skill invocations, or transient API payloads in persistent files.
- Do not write many long history files when a concise `task.md` update is enough.
