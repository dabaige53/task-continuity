# Task To Skill Conversion Guide

Use this reference when the user asks to convert the current task, task folder, or ongoing workflow into a reusable Skill. Example trigger phrases include:

- "把这个 task 转成一个 skill"
- "将此任务沉淀成技能"
- "make this task a skill"
- "turn this workspace into a reusable skill"
- "把这套流程封装成 skills"

## Purpose

Help the user transform a concrete long-running task into a reusable Skill by using:

1. the current task context and task memory files,
2. durable task materials, knowledge, deliverables, and selected run evidence,
3. the `skill-creator` Skill's requirements and packaging workflow, and
4. multiple rounds of investigation and confirmation before building.

Do not convert a task into a Skill in one blind pass. A good Skill is a reusable workflow, not a dump of the task folder.

## Required First Action

When this conversion intent appears, first review the task context and prepare a conversion plan. Then inspect the task in this order:

1. `index.json`
2. `task.md`
3. `request.md`
4. `error_notes.md`
5. `materials/`
6. `knowledge/`
7. `deliverables/current/`
8. active or latest `runs/*/run_summary.md`
9. specific run files only when the durable task files do not explain the reusable workflow

Do not scan every run by default. Runs are workbench history and may contain duplicate, temporary, failed, or superseded files.

If the workspace is in an older layout, first run or recommend the structure maintenance step:

```bash
python scripts/task_maintenance.py ensure "./tasks/<task-folder>" --json
```

After the initial task-context review, use the `skill-creator` workflow. If that Skill is available, invoke or consult it before designing or packaging the new Skill.

## Required Multi-Pass Workflow

Treat conversion as a multi-pass discovery and confirmation process. For non-trivial tasks, complete these passes unless the user explicitly authorizes a rough best-effort package:

1. **Context research pass:** identify the reusable workflow, durable knowledge, repeated operations, input/output expectations, and success criteria.
2. **Conversion plan pass:** propose what should become `SKILL.md` instructions, `references/`, `scripts/`, `assets/`, examples, or exclusions.
3. **Skill detail confirmation pass:** confirm the Skill name, triggering description, expected inputs, expected outputs, supported tools/connectors, file inclusion choices, and privacy boundaries.
4. **Implementation pass:** build or update the Skill only after the user accepts the conversion plan or provides enough direction to proceed.

Ask focused confirmation questions after showing what has already been inferred from the task. Do not ask the user to repeat information already present in task files.

## Durable Conversion Brief

Create or update `knowledge/skill_conversion_brief.md` when the task folder is writable. Keep it concise and current. Include:

- reusable problem statement
- repeated workflow steps
- expected user inputs
- expected outputs and acceptance criteria
- tools, connectors, or scripts used
- decisions and conventions worth preserving
- known failure modes from `error_notes.md`
- files proposed for inclusion, adaptation, exclusion, or external reference
- open questions for the user

Treat this brief as the current source of truth for the conversion plan. Update it after each material user confirmation.

## File Selection Rules

Classify every relevant task artifact before adding it to a Skill.

| Classification | Put in Skill? | Typical destination | Rule |
|---|---:|---|---|
| reusable workflow instructions | yes | `SKILL.md` | Distill into concise imperative steps. Do not paste raw task history. |
| detailed reusable guidance | yes | `references/*.md` | Move long checklists, schemas, examples, and policies out of `SKILL.md`. |
| deterministic repeated operation | yes, if tested | `scripts/` | Include scripts only when repeatability or correctness benefits from code. Test representative scripts before packaging. |
| output templates, boilerplates, icons, static examples | yes, if reusable and small | `assets/` | Keep total package size below 25 MB. Do not include fonts unless allowed and necessary. |
| current deliverable with user/client-specific content | usually no | transform into anonymized example or template | Preserve structure, not confidential content. |
| source materials from the specific task | usually no | summarize or convert to synthetic example | Include only if explicitly reusable, non-sensitive, and approved by the user. |
| `task.md`, `request.md`, `index.json` | no direct copy | use as source material | Extract reusable intent, constraints, and process. |
| `task.log`, raw tool output, scratch files, failed drafts | no | exclude | These are task history, not Skill resources. |
| old run duplicates or superseded files | no | exclude | Use only to understand mistakes or evolution when needed. |

Prefer **adaptation** over copying. Rewrite task-specific material into neutral, reusable instructions and examples.

## Skill Design Questions To Confirm

Confirm these items in one or more short rounds:

1. **Scope:** What should the Skill do every time, and what should remain outside the Skill?
2. **Triggering:** What user phrases or situations should activate it?
3. **Inputs:** What files, text, links, connectors, or parameters will future users provide?
4. **Outputs:** What artifact or answer should the Skill produce, and in what format?
5. **Reusable resources:** Which files should be included, transformed, or excluded?
6. **Scripts:** Which operations need deterministic scripts rather than instructions?
7. **Privacy:** Which task materials contain sensitive or one-off content that must not be bundled?
8. **Success criteria:** How should the user judge that the Skill worked correctly?

When possible, provide a proposed answer for each item and ask the user to approve or edit it.

## Conversion Plan Format

Before building, present a plan like this:

```markdown
# Proposed Task-To-Skill Conversion

## Inferred Skill Purpose
<one paragraph>

## Proposed Skill Name
<lowercase-hyphen-name>

## Trigger Description Draft
<frontmatter description draft>

## Expected Inputs
- ...

## Expected Outputs
- ...

## Workflow To Encode
1. ...
2. ...

## Files To Include
| Source file | Skill destination | Treatment | Reason |
|---|---|---|---|
| `knowledge/example.md` | `references/example.md` | adapt | reusable checklist |

## Files To Exclude
| Source file | Reason |
|---|---|
| `runs/.../scratch.md` | temporary run artifact |

## Open Confirmations
1. ...
```

Do not create `skill.zip` until the user has accepted the plan, unless they explicitly authorize best-effort packaging without confirmation.

## Implementation Handoff To Skill-Creator

After the user confirms the plan:

1. Use the `skill-creator` Skill's process for creating or updating the Skill.
2. Initialize a new Skill directory when creating from scratch.
3. Keep `SKILL.md` concise and move detailed material to one-level reference files.
4. Include only reusable scripts, references, and assets approved by the conversion plan.
5. Test included scripts with representative inputs.
6. Validate and package the complete Skill as `skill.zip`.
7. Return the packaged `skill.zip` to the user.

For updates to an existing Skill, preserve its structure, apply the agreed changes, validate, and repackage the full updated Skill as `skill.zip`.

## Task Continuity Maintenance During Conversion

Because the conversion is itself part of the task:

- Append the user's conversion request and later clarifications to `request.md`.
- Keep `knowledge/skill_conversion_brief.md` as the durable planning artifact.
- Update `task.md` with the current conversion status, decisions, canonical conversion brief, and next step.
- Update `index.json` so `canonical_files` includes the conversion brief and any current Skill package if produced.
- Use the active run for temporary extraction, experiments, and packaging work.
- Promote the final `skill.zip` or Skill source folder only if it is intended to be a durable deliverable for the task.

## Privacy And Safety Defaults

- Do not bundle confidential, client-specific, personal, or one-off task content unless the user explicitly approves it.
- Prefer anonymized examples and templates over real task artifacts.
- Do not include raw conversation transcripts, raw tool logs, credentials, connector exports, or hidden/private reasoning.
- When unsure whether a file is reusable or sensitive, list it under `Open Confirmations` instead of bundling it.
