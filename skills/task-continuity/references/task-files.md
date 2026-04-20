# Task File Conventions

## Purpose Of Each File

### `task.md`
The single context file for the task. Another ChatGPT instance should read this file first.

Recommended sections:
- `Task Summary`
- `Current Status`
- `Original Intent`
- `Current Objective`
- `Known Context`
- `User Preferences`
- `Constraints`
- `Decisions Already Made`
- `Progress`
- `Key Materials`
- `Risks / Open Questions`
- `Next Recommended Step`
- `Recent Runs`

### `request.md`
Store the user's original request and later clarifications.
Keep the user's original wording whenever possible.

Recommended sections:
- `Initial Request`
- `Clarifications`

### `index.json`
Lightweight lookup file for matching and recovery.
It should also track the current `active_run` so small follow-ups can continue inside the same run.

Suggested keys:
```json
{
  "title": "客户方案修订",
  "short_name": "客户方案修订",
  "status": "in_progress",
  "created_at": "2026-04-17 09:30",
  "last_updated": "2026-04-17 10:10",
  "active_run": "001-initial-intake-20260417",
  "last_run": "001-initial-intake-20260417",
  "aliases": ["客户方案", "proposal update"],
  "tags": ["proposal", "client", "revision"],
  "deliverable": "修订后的客户提案"
}
```

### `task.log`
Timestamped milestones only.
Do not use it as a long diary.

### `error_notes.md`
Store durable mistakes to avoid, user dislikes, or repeated risks.

Recommended sections:
- `User Preferences`
- `Repeated Mistakes To Avoid`
- `Known Risks`

### `runs/.../run_summary.md`
Store the purpose and outcome of one run.
Update the same file while the run stays active.

Recommended sections:
- `Goal`
- `Why This Run`
- `Inputs Reviewed`
- `Outputs`
- `Decisions`
- `Next Step`

### Working Files Inside `runs/.../`
Place drafts, revised documents, analysis notes, exported files, and other run-scoped outputs inside the active run folder.
Do not dump them all into the task root.

## Naming Rules

### Task Folder
Use:

```text
<task-short-name>-YYYYMMDD
```

Examples:
- `client-proposal-revision-20260417`
- `weekly-sales-summary-20260417`
- `客户方案修订-20260417`

### Run Folder
Use:

```text
NNN-<run-short-name>-YYYYMMDD
```

Examples:
- `001-initial-intake-20260417`
- `002-extract-client-feedback-20260417`
- `003-重写结构-20260418`

## Recovery Order

When resuming an existing task, read in this order:
1. `index.json`
2. `task.md`
3. `request.md`
4. the active run's `run_summary.md` or the latest `run_summary.md`
5. `error_notes.md`
6. specific outputs only if needed

## Run Reuse Principles

A run is not one user message.
Reuse the current active run for:
- small edits
- follow-up wording changes
- one more clarification
- minor formatting cleanup
- short additions to the same working file

Create a new run only when the work meaningfully shifts to a new phase, new sub-goal, or new checkpoint.

## Updating Principles

- Keep `task.md` current.
- Keep `request.md` close to the user's wording.
- Keep `index.json` lightweight and machine-friendly.
- Keep `task.log` short.
- Keep `run_summary.md` focused on one meaningful run.
- Keep run-scoped outputs inside the active run folder.
