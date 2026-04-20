---
name: task-continuity
description: maintain continuity for long-running white-collar tasks by creating or resuming lightweight task folders, preserving the user's original request, keeping task.md as the single task context file, storing working files in the active run folder instead of dumping them in the task root, and reusing the active run for small follow-ups instead of opening a new run every turn. use when a user wants to continue a previous task, start work that should span multiple turns, or decide whether a similar existing task should be resumed instead of creating a new one.
---

# Task Continuity

## Overview

Use this skill to keep long-running white-collar work continuous across conversations without turning the workspace into a mess. Each task lives in one lightweight folder. `task.md` is the single context file that another ChatGPT instance should read first to understand the task.

This skill is for office work such as proposals, reports, summaries, meeting follow-ups, document revision, stakeholder communication, and other multi-turn knowledge work. Do not use it for one-off questions that do not need persistence.

## Core Rules

1. Treat one task folder as one long-lived unit of work.
2. Keep `task.md` as the main context file. When entering a task, read `task.md` first.
3. Preserve the user's original wording in `request.md`.
4. Keep the task root minimal. The root is for task-level memory files only.
5. Put working files, drafts, outputs, and revisions in the **active run folder** by default, not in the task root.
6. A run is a meaningful work phase or work session, **not** a single user turn. Small follow-ups stay in the current active run.
7. **Do not write tool calls or skill script invocations to any file.** They are ephemeral actions, not persistent outputs.
8. Keep all outputs inside the task folder. Do not scatter files elsewhere unless the user explicitly requests it.
9. Prefer lightweight structure and short updates over heavy project-management ceremony.

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
        │   └── <working files and outputs>
        └── ...
```

**task root** holds task-level memory files only: `task.md`, `request.md`, `index.json`, `task.log`, and `error_notes.md`.

**runs/** holds the actual working files for each phase: drafts, revisions, exported outputs, notes created during that run, and the `run_summary.md` record.

See `references/task-files.md` for the purpose of each file and the expected sections.

## What Goes Where

| Content | Location |
|---|---|
| `task.md`, `request.md`, `index.json`, `task.log`, `error_notes.md` | task root |
| Drafts, deliverables, revised files, analysis notes, generated outputs | active run folder |
| Execution record for one run | `runs/<run-folder>/run_summary.md` |
| Tool call results | not written to disk |
| Skill script invocations | not written to disk |

Do **not** dump every file into the task root. Keep the root clean.

## Decide Whether To Resume Or Create

When a new user message arrives and it looks like ongoing work:

1. Look inside the tasks directory.
2. Read `index.json` for likely candidate folders first.
3. Read `task.md` only for the closest candidates.
4. Resume an existing task when the message clearly matches the same goal and same deliverable, or when the user explicitly signals continuation.
5. Create a new task when the deliverable changes materially, the objective shifts to a different outcome, or no existing task is a strong match.

Use these signals for matching:
- explicit continuation language like "继续上次", "接着做", "上次那个"
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
3. Make sure `index.json` reflects useful aliases, tags, status, deliverable, `active_run`, and `last_run`.
4. Use the first run folder for the current working session.
5. Write working files for that session into the first run folder, not the task root.

## Resume An Existing Task

When resuming, read in this order:
1. `index.json`
2. `task.md`
3. `request.md`
4. the active run's `run_summary.md` or the latest `run_summary.md`
5. `error_notes.md`
6. specific files inside the active run or latest relevant run only if more detail is needed

Do not re-read every file by default. Start from the lightweight files above and expand only when necessary.

## Use The Active Run

Every task should have one **active run** recorded in `index.json`.

A run stays active across small follow-ups such as:
- wording tweaks
- small structural changes
- quick clarifications
- adding one paragraph or one section
- minor formatting cleanup
- short follow-up questions that continue the same immediate work

When the task already has an active run, keep using that run instead of creating a new one.

You can locate the current active run with:

```bash
python scripts/init_task.py --task-dir "./tasks/<task-folder>" --json
```

This returns the active run path without creating a new run.

## Start A New Run

Create a new run only when the work meaningfully changes, for example:
- the sub-goal changes materially
- the deliverable enters a new stage such as intake → drafting, drafting → revision, revision → finalization
- the main file set changes substantially
- you want a clean checkpoint for a new phase
- the user explicitly asks to start a new phase

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

Create a new run explicitly:

```bash
python scripts/init_task.py --task-dir "./tasks/<task-folder>" --new-run --run "rewrite-structure"
```

Do **not** create a new run for every message.

## Update Rules While Working

While a run is active:
1. Keep updating working files inside the active run folder.
2. Update the same `run_summary.md` as the work evolves.
3. Update `task.md` whenever the task-level understanding changes.
4. Update `index.json` with current status, tags, aliases, deliverable, `last_updated`, `active_run`, and `last_run` when needed.
5. Append key milestones to `task.log`.
6. Add repeatable mistakes, risks, or user dislikes to `error_notes.md`.
7. Append new user clarifications to `request.md` if the task scope changes.

When a run is effectively done and a new phase begins, then create a new run.

## File Writing Guidance

Keep files short, current, and useful.

- `task.md`: dynamic task memory and current status
- `request.md`: original request and later clarifications in the user's own words when possible
- `index.json`: lightweight machine-readable lookup file with `active_run` and `last_run`
- `task.log`: timestamped milestones only
- `error_notes.md`: things not to repeat
- `run_summary.md`: what this run tried to achieve, which files were changed, what changed, and the next step

## Boundaries

- Do not turn this into a heavyweight project-management system.
- Do not create extra top-level files unless they materially help the task.
- Do not split context across many files when `task.md` can hold it.
- Do not create a new task merely because the conversation wording changed slightly.
- Do not create a new run merely because one more instruction arrived.
- Do not log tool calls, skill invocations, or intermediate API results to any file.
- Do not place all output files in the task root; keep run-scoped files in the active run folder.
