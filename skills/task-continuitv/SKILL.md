---
name: task-continuity
description: maintain continuity for long-running white-collar tasks by creating or resuming lightweight task folders, preserving the user's original request, keeping task.md as the single task context file, and organizing each execution in purpose-named run folders. use when a user wants to continue a previous task, start work that should span multiple turns, or decide whether a similar existing task should be resumed instead of creating a new one.
---

# Task Continuity

## Overview

Use this skill to keep long-running white-collar work continuous across conversations without turning the workspace into a mess. Each task lives in one lightweight folder. `task.md` is the single context file that another ChatGPT instance should read first to understand the task.

This skill is for office work such as proposals, reports, summaries, meeting follow-ups, document revision, stakeholder communication, and other multi-turn knowledge work. Do not use it for one-off questions that do not need persistence.

## Core Rules

1. Treat one task folder as one long-lived unit of work.
2. Keep `task.md` as the main context file. When entering a task, read `task.md` first.
3. Preserve the user's original wording in `request.md`.
4. Put every run inside `runs/` and give each run a purpose-driven name.
5. Keep all outputs inside the task folder. Do not scatter files elsewhere unless the user explicitly requests it.
6. Prefer lightweight structure and short updates over heavy project-management ceremony.

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
    └── runs/
        ├── 001-<run-short-name>-YYYYMMDD/
        │   ├── run_summary.md
        │   └── <outputs>
        └── ...
```

See `references/task-files.md` for the purpose of each file and the expected sections.

## Decide Whether To Resume Or Create

When a new user message arrives and it looks like ongoing work:

1. Look inside the tasks directory.
2. Read `index.json` for likely candidate folders first.
3. Read `task.md` only for the closest candidates.
4. Resume an existing task when the message clearly matches the same goal and same deliverable, or when the user explicitly signals continuation.
5. Create a new task when the deliverable changes materially, the objective shifts to a different outcome, or no existing task is a strong match.

Use these signals for matching:
- explicit continuation language like “继续上次”, “接着做”, “上次那个”
- same deliverable
- same goal
- same key materials or input sources
- overlapping aliases or tags in `index.json`

If two tasks are close, choose the one with the strongest deliverable match and briefly state the assumption while proceeding.

## Create A New Task

Prefer the bundled script:

```bash
python scripts/init_task.py "<task title>" --root "./tasks" --run "initial-intake"
```

Optional:

```bash
python scripts/init_task.py "<task title>" --root "./tasks" --run "initial-intake" --request "<original user request>"
```

After initialization:
1. Save the user's original request in `request.md` if it was not passed to the script.
2. Fill `task.md` immediately with the current objective, known context, constraints, and next step.
3. Make sure `index.json` reflects useful aliases, tags, status, deliverable, and `last_run`.
4. Use the first run folder for the current working session.

## Resume An Existing Task

When resuming, read in this order:
1. `index.json`
2. `task.md`
3. `request.md`
4. the latest `runs/.../run_summary.md`
5. `error_notes.md`
6. specific output files only if more detail is needed

Do not re-read every file by default. Start from the lightweight files above and expand only when necessary.

## Start A New Run

Every new execution should get its own run folder. Use a purpose-driven name, not a generic label.

Good run names:
- `initial-intake`
- `extract-client-feedback`
- `rewrite-structure`
- `draft-first-version`
- `prepare-final-summary`

Avoid vague names:
- `continue`
- `update`
- `misc`
- `work`

You can create a new run inside an existing task with the same script:

```bash
python scripts/init_task.py --task-dir "./tasks/<task-folder>" --run "rewrite-structure"
```

## Update Rules After Each Run

Before ending a run:
1. update `run_summary.md` with the goal, inputs reviewed, outputs, decisions, and next step
2. update `task.md` so it remains the best single-file summary of the task
3. update `index.json` with current status, tags, aliases, deliverable, `last_updated`, and `last_run` when needed
4. append key milestones to `task.log`
5. add repeatable mistakes, risks, or user dislikes to `error_notes.md`
6. append new user clarifications to `request.md` if the task scope changes

## File Writing Guidance

Keep files short, current, and useful.

- `task.md`: dynamic task memory and current status
- `request.md`: original request and later clarifications in the user's own words when possible
- `index.json`: lightweight machine-readable lookup file
- `task.log`: timestamped milestones only
- `error_notes.md`: things not to repeat
- `run_summary.md`: what this run tried to achieve and what changed

## Boundaries

- Do not turn this into a heavyweight project-management system.
- Do not create extra top-level files unless they materially help the task.
- Do not split context across many files when `task.md` can hold it.
- Do not create a new task merely because the conversation wording changed slightly.
