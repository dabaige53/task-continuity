# Task File Conventions

## Workspace Principle

A task folder has two layers:

1. The task root stores current durable truth.
2. `runs/` stores workbench files and phase history.

Durable files should not remain hidden inside a run after they become useful beyond that run.

## Root Memory Files

### `task.md`

The single context file for resuming the task. Read this first.

Recommended sections:

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

Keep `task.md` current. It is not a full diary. Move historical detail into run summaries only when needed.

### `request.md`

The canonical record of user intent over time.

Recommended sections:

- `Initial Request`
- `Clarifications And Changes`

Preserve the original request. Append later instructions with timestamps. If a new instruction supersedes an earlier one, label it clearly instead of deleting the earlier wording.

### `index.json`

Lightweight lookup and recovery metadata. It should help another session decide whether to resume this task and where the current truth lives.

Suggested keys:

```json
{
  "title": "client proposal revision",
  "short_name": "client-proposal-revision",
  "status": "in_progress",
  "created_at": "2026-04-17 09:30",
  "last_updated": "2026-04-17 10:10",
  "active_run": "001-initial-intake-20260417",
  "last_run": "001-initial-intake-20260417",
  "aliases": ["proposal update"],
  "tags": ["proposal", "client", "revision"],
  "deliverable": "revised client proposal",
  "canonical_files": {
    "materials": [],
    "knowledge": [],
    "deliverables": []
  }
}
```

### `task.log`

Timestamped milestones only. Do not use it as a transcript.

### `error_notes.md`

Durable preferences, repeated mistakes to avoid, and known risks.

Recommended sections:

- `User Preferences`
- `Repeated Mistakes To Avoid`
- `Known Risks`

## Root Durable Folders

### `materials/`

Use for durable inputs and source references that future runs may need:

- user-provided source files
- briefs
- data extracts that are the source of truth
- reference documents
- reusable input notes

### `knowledge/`

Use for reusable task knowledge:

- durable analyses
- decision notes
- style guides
- schemas
- checklists
- assumptions that should survive across phases

### `deliverables/current/`

Use for latest canonical outputs the user should use next:

- current report
- latest proposal
- final summary
- cleaned dataset
- exported document

Use stable filenames for current files. Replace or update them rather than creating repeated versions.

### `archive/`

Use for superseded durable files that are worth retaining. Timestamp archived files.

Do not archive every minor version. Archive only when history matters or a replacement is substantial.

## Run Files

### `runs/.../run_summary.md`

The concise record of one work phase. Update the same summary while the run remains active.

Recommended sections:

- `Goal`
- `Why This Run`
- `Inputs Reviewed`
- `Files Created Or Modified`
- `Promoted To Task Root`
- `Superseded Or Reused`
- `Decisions`
- `Next Step`

### Working Files Inside `runs/.../`

Use the active run for:

- scratch notes
- draft fragments
- temporary conversions
- intermediate analysis
- phase-specific evidence
- non-canonical outputs

Promote any durable file before ending a modifying turn.

## Naming Rules

### Task Folder

Use:

```text
<task-short-name>-YYYYMMDD
```

Examples:

- `client-proposal-revision-20260417`
- `weekly-sales-summary-20260417`
- `customer-feedback-analysis-20260417`

### Run Folder

Use:

```text
NNN-<run-short-name>-YYYYMMDD
```

Examples:

- `001-initial-intake-20260417`
- `002-extract-client-feedback-20260417`
- `003-revise-after-review-20260418`

### Current Durable Files

Use stable names:

- `proposal.md`
- `executive-summary.docx`
- `source-notes.md`
- `analysis-assumptions.md`

Avoid:

- `final-final.md`
- `proposal-new.md`
- `proposal-copy.md`
- `proposal-20260417.md` in `deliverables/current/`

Timestamped names belong in `archive/`, not in current folders.

## Recovery Order

When resuming an existing task, read in this order:

1. `index.json`
2. `task.md`
3. `request.md`
4. active run `run_summary.md` or latest `run_summary.md`
5. `error_notes.md`
6. only the specific durable or run files needed for the current step

## Run Reuse Principles

Reuse the current active run for:

- small edits
- follow-up wording changes
- minor formatting cleanup
- short additions to the same deliverable
- clarifications that do not change the phase

Create a new run only when the phase, sub-goal, or checkpoint changes materially.

## Promotion Checklist

Before ending a modifying turn, ask:

1. Did the user provide a source file or stable brief that should move to `materials/`?
2. Did this run create durable analysis or reusable decisions that should move to `knowledge/`?
3. Did this run produce the latest user-facing output that should move to `deliverables/current/`?
4. Did an old current file need to be archived or replaced?
5. Did `task.md`, `request.md`, `index.json`, and `run_summary.md` get updated to point to the current files?
6. Are there short-term duplicates that should be removed, archived, or replaced?
