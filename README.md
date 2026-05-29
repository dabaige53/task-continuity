# Task Continuity Skill

A lightweight skill for keeping long-running office work organized across conversations.

The optimized model is:

- task root = current durable truth
- runs = temporary workbench and phase history

This prevents two common failure modes:

1. every file gets dumped into `runs/` forever
2. repeated short follow-ups create duplicate files and duplicate runs

## Package Contents

```text
task-continuity/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── init_task.py
│   └── task_maintenance.py
└── references/
    ├── task-files.md
    └── task-to-skill-conversion.md
```

## Workspace Layout

```text
tasks/
└── <task-short-name>-YYYYMMDD/
    ├── task.md
    ├── request.md
    ├── index.json
    ├── task.log
    ├── error_notes.md
    ├── materials/
    ├── knowledge/
    ├── deliverables/
    │   └── current/
    ├── archive/
    └── runs/
        ├── 001-<run-short-name>-YYYYMMDD/
        │   ├── run_summary.md
        │   └── workbench files
        └── ...
```

## File Responsibilities

- `task.md`: main resume file and current task state.
- `request.md`: original request plus later clarifications and superseding instructions.
- `index.json`: machine-readable task lookup, active run, and canonical file index.
- `task.log`: short milestone log.
- `error_notes.md`: durable preferences, repeated mistakes to avoid, and risks.
- `materials/`: durable user inputs, briefs, and source references.
- `knowledge/`: reusable analyses, decisions, style notes, schemas, and checklists.
- `deliverables/current/`: latest canonical outputs.
- `archive/`: superseded durable files worth keeping.
- `runs/.../`: scratch work, drafts, temporary outputs, and phase history.

## Scripts

Both scripts use only the Python standard library.

### Create a new task

```bash
python scripts/init_task.py "client proposal revision" --root ./tasks --run initial-intake --request "revise the client proposal" --json
```

### Resume an existing task and return the active run

```bash
python scripts/init_task.py --task-dir ./tasks/client-proposal-revision-20260417 --json
```

### Create a new run explicitly

```bash
python scripts/init_task.py --task-dir ./tasks/client-proposal-revision-20260417 --new-run --run revise-after-review --json
```

### Ensure an older task has the optimized structure

```bash
python scripts/task_maintenance.py ensure ./tasks/client-proposal-revision-20260417 --json
```

### Promote a durable file from a run to the task root

```bash
python scripts/task_maintenance.py promote ./tasks/client-proposal-revision-20260417 ./tasks/client-proposal-revision-20260417/runs/001-initial-intake-20260417/proposal.md --kind deliverable --name proposal.md --mode move --replace --json
```

Kinds:

- `material` goes to `materials/`
- `knowledge` goes to `knowledge/`
- `deliverable` goes to `deliverables/current/`

### Find duplicate files

```bash
python scripts/task_maintenance.py dedupe ./tasks/client-proposal-revision-20260417 --write-report --json
```

The report is written to `knowledge/maintenance_report.md` when `--write-report` is used.

## Usage Guidance

1. Start or resume the task.
2. Reuse the active run for small follow-ups.
3. Save scratch and drafts in the active run.
4. Promote durable materials, reusable knowledge, and latest deliverables to the task root.
5. Update `task.md`, `request.md`, `index.json`, and `run_summary.md` before finishing a modifying turn.
6. Avoid duplicate current files; update or replace stable filenames instead.
7. When converting a task into a reusable Skill, read `references/task-to-skill-conversion.md`, audit durable task artifacts, prepare a conversion plan, confirm scope and file handling with the user, then use `skill-creator` to build and package `skill.zip`.
