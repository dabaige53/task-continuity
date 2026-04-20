---
name: task-continuity
description: maintain continuity for long-running white-collar tasks by creating or resuming lightweight task folders, preserving the user's original request, keeping task.md as the single task context file, keeping request.md continuously synchronized with the latest user intent, storing working files in the active run folder instead of dumping them in the task root, and reusing the active run for small follow-ups instead of opening a new run every turn. use when a user wants to continue a previous task, start work that should span multiple turns, or decide whether a similar existing task should be resumed instead of creating a new one.
---

# Task Continuity

## Overview

Use this skill to keep long-running white-collar work continuous across conversations without turning the workspace into a mess. Each task lives in one lightweight folder. `task.md` is the single context file that another ChatGPT instance should read first to understand the task.

This skill is for office work such as proposals, reports, summaries, meeting follow-ups, document revision, stakeholder communication, and other multi-turn knowledge work. Do not use it for one-off questions that do not need persistence.

## Core Rules

1. Treat one task folder as one long-lived unit of work.
2. Keep `task.md` as the main context file. When entering a task, read `task.md` first.
3. Preserve the user's original wording in `request.md`.
4. Keep `request.md` continuously synchronized with the latest user intent. When the user adds, changes, removes, or clarifies requirements, constraints, preferences, acceptance criteria, source materials, or deliverables, append that change to `request.md` in the same working pass.
5. Treat `request.md` as the canonical record of user intent over time: keep the original request at the top, then append dated or clearly separated clarifications underneath it. Do not silently replace prior intent unless the user explicitly supersedes it.
6. Keep the task root minimal. The root is for task-level memory files only.
7. Put working files, drafts, outputs, and revisions in the **active run folder** by default, not in the task root.
8. A run is a meaningful work phase or work session, **not** a single user turn. Small follow-ups stay in the current active run.
9. **Do not write tool calls or skill script invocations to any file.** They are ephemeral actions, not persistent outputs.
10. Keep all outputs inside the task folder. Do not scatter files elsewhere unless the user explicitly requests it.
11. Prefer lightweight structure and short updates over heavy project-management ceremony.

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

## Synchronization Rules

Before finishing any turn that changes the task, make sure the lightweight memory files are still aligned.

Update `request.md` when:
- the user adds a new requirement or example
- the user changes the desired deliverable
- the user adds or removes constraints
- the user changes tone, audience, format, or priority
- the user supplies new source files, links, or reference materials
- the user corrects a previous assumption

Update `task.md` when:
- the task-level objective, plan, status, or next step changes
- you learn something that another ChatGPT instance would need to resume correctly
- the active risks, blockers, or assumptions change

Update `run_summary.md` when:
- working files were created or modified
- the current run's immediate goal changed
- you want the next turn to understand what happened in this run without opening many files

If `request.md` and `task.md` conflict, reconcile them immediately before continuing. `request.md` is the source of truth for what the user wants; `task.md` explains how the task is currently being handled.

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
2. If the current turn already includes clarifications beyond the original request, append them to `request.md` immediately instead of waiting for a later turn.
3. Fill `task.md` immediately with the current objective, known context, constraints, and next step.
4. Make sure `index.json` reflects useful aliases, tags, status, deliverable, `active_run`, and `last_run`.
5. Use the first run folder for the current working session.
6. Write working files for that session into the first run folder, not the task root.

## Resume An Existing Task

When resuming, read in this order:
1. `index.json`
2. `task.md`
3. `request.md`
4. the active run's `run_summary.md` or the latest `run_summary.md`
5. `error_notes.md`
6. specific files inside the active run or latest relevant run only if more detail is needed

Do not re-read every file by default. Start from the lightweight files above and expand only when necessary.

After reading, check whether `request.md` still reflects the latest user intent from the conversation. If it is stale or incomplete, update it before producing new work.

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
3. Update `request.md` on any turn that materially changes user intent, even if the overall task scope does not change.
4. Update `task.md` whenever the task-level understanding changes.
5. Update `index.json` with current status, tags, aliases, deliverable, `last_updated`, `active_run`, and `last_run` when needed.
6. Append key milestones to `task.log`.
7. Add repeatable mistakes, risks, or user dislikes to `error_notes.md`.
8. Before ending the turn, quickly check that `request.md`, `task.md`, and `run_summary.md` are mutually consistent at their own levels.

When a run is effectively done and a new phase begins, then create a new run.

## File Writing Guidance

Keep files short, current, and useful.

- `task.md`: dynamic task memory and current status
- `request.md`: original request plus subsequent clarifications, corrections, and superseding instructions in the user's own words when possible
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
- Do not treat `request.md` as a write-once file. It must stay current enough that another ChatGPT instance can reconstruct the latest user intent without re-reading the full conversation.
