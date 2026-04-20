#!/usr/bin/env python3
"""Initialize a task folder, return the active run, or create a new run.

Examples:
  python scripts/init_task.py "客户方案修订"
  python scripts/init_task.py "客户方案修订" --root ./tasks --run "initial-intake"
  python scripts/init_task.py --task-dir ./tasks/客户方案修订-20260417
  python scripts/init_task.py --task-dir ./tasks/客户方案修订-20260417 --new-run --run "提炼客户反馈"
  python scripts/init_task.py "客户方案修订" --request "整理客户反馈并重写方案结构" --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

INVALID_FILENAME_CHARS = '<>:"/\\|?*'
CONTROL_CHARS_RE = re.compile(r'[\x00-\x1f]')
MULTI_SPACE_RE = re.compile(r'\s+')
MULTI_HYPHEN_RE = re.compile(r'-{2,}')
RUN_PREFIX_RE = re.compile(r'^(\d{3})-')
RUN_FOLDER_RE = re.compile(r'^(\d{3})-(.+)-(\d{8})$')
WINDOWS_RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
}


def now() -> datetime:
    return datetime.now()


def timestamp(dt: Optional[datetime] = None) -> str:
    return (dt or now()).strftime('%Y-%m-%d %H:%M')


def datestamp(dt: Optional[datetime] = None) -> str:
    return (dt or now()).strftime('%Y%m%d')


def sanitize_component(text: str, fallback: str) -> str:
    """Create a filesystem-safe name while preserving Unicode when possible."""
    value = unicodedata.normalize('NFKC', (text or '').strip())
    value = CONTROL_CHARS_RE.sub('', value)
    value = ''.join(' ' if ch in INVALID_FILENAME_CHARS else ch for ch in value)
    value = value.replace('/', ' ').replace('\\', ' ')
    value = MULTI_SPACE_RE.sub('-', value)
    value = MULTI_HYPHEN_RE.sub('-', value)
    value = value.strip(' .-_')
    if not value:
        value = fallback
    if value.upper() in WINDOWS_RESERVED_NAMES:
        value = f'{value}-item'
    value = value[:80].strip(' .-_') or fallback
    return value.lower()


def unique_dir(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 2
    while True:
        candidate = path.with_name(f'{path.name}-{counter:02d}')
        if not candidate.exists():
            return candidate
        counter += 1


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding='utf-8')


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(read_text(path))
    except Exception:
        return {}


def save_json(path: Path, payload: Dict[str, Any]) -> None:
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + '\n')


def append_log(task_dir: Path, message: str) -> None:
    log_path = task_dir / 'task.log'
    line = f'[{timestamp()}] {message}\n'
    with log_path.open('a', encoding='utf-8') as handle:
        handle.write(line)


def request_initial_text(user_request: str) -> str:
    content = user_request.strip() if user_request else '[Fill in the original user request here.]'
    return (
        '# User Request History\n\n'
        '## Initial Request\n'
        f'{content}\n\n'
        '## Clarifications\n'
        '- (Add follow-up clarifications here.)\n'
    )


def append_request_clarification(task_dir: Path, user_request: str) -> None:
    request_path = task_dir / 'request.md'
    if not request_path.exists():
        write_text(request_path, request_initial_text(user_request))
        return

    existing = read_text(request_path).rstrip() + '\n\n'
    addition = f'### {timestamp()}\n{user_request.strip()}\n'
    write_text(request_path, existing + addition)


def task_md_template(title: str, created_at: str, first_run_name: str) -> str:
    return f'''# {title}

## Task Summary
- Briefly describe the task in one sentence.

## Current Status
- in_progress

## Original Intent
- Summarize what the user is truly trying to achieve.

## Current Objective
- State the most important current goal.

## Known Context
- Record the most important context that future sessions must know.
- Keep this section updated. This is the main context entry point for the task.

## User Preferences
- Capture task-specific user preferences, tone, format, or workflow expectations.

## Constraints
- Record hard boundaries, must-follow rules, deadlines, or exclusions.

## Decisions Already Made
- List decisions that should not be re-litigated unless the user changes direction.

## Progress
### Done
- 

### In Progress
- 

### Pending
- 

## Key Materials
- Add important source files, outputs, or references here.

## Risks / Open Questions
- Track uncertainty, blockers, or assumptions that might change the work.

## Next Recommended Step
- Describe the best next step.

## Recent Runs
| Run | Date | Focus | Outcome |
|-----|------|-------|---------|
| 001 | {created_at[:10]} | {first_run_name} | initialized |
'''


def error_notes_template() -> str:
    return '''# Error Notes

## User Preferences
- 

## Repeated Mistakes To Avoid
- 

## Known Risks
- 
'''


def run_summary_template(run_number: int, run_name: str, created_at: str) -> str:
    return f'''# Run {run_number:03d} — {run_name}

## Date
{created_at}

## Goal
- Describe the purpose of this run.

## Why This Run
- Explain why this run exists and what changed.

## Inputs Reviewed
- 

## Outputs
- 

## Decisions
- 

## Next Step
- 
'''


def default_index(title: str, short_name: str, created_at: str, run_folder_name: str) -> Dict[str, Any]:
    return {
        'title': title,
        'short_name': short_name,
        'status': 'in_progress',
        'created_at': created_at,
        'last_updated': created_at,
        'active_run': run_folder_name,
        'last_run': run_folder_name,
        'aliases': [],
        'tags': [],
        'deliverable': '',
    }


def next_run_number(runs_dir: Path) -> int:
    max_number = 0
    if not runs_dir.exists():
        return 1
    for child in runs_dir.iterdir():
        if not child.is_dir():
            continue
        match = RUN_PREFIX_RE.match(child.name)
        if match:
            max_number = max(max_number, int(match.group(1)))
    return max_number + 1


def parse_run_folder_name(folder_name: str) -> Tuple[int, str]:
    match = RUN_FOLDER_RE.match(folder_name)
    if match:
        return int(match.group(1)), match.group(2)
    prefix = RUN_PREFIX_RE.match(folder_name)
    if prefix:
        return int(prefix.group(1)), folder_name
    return 0, folder_name


def ensure_run_summary(run_dir: Path) -> Path:
    run_summary_path = run_dir / 'run_summary.md'
    if run_summary_path.exists():
        return run_summary_path
    run_number, run_name = parse_run_folder_name(run_dir.name)
    write_text(run_summary_path, run_summary_template(run_number or 1, run_name, timestamp()))
    return run_summary_path


def update_index(task_dir: Path, updates: Dict[str, Any], touch_time: bool = True) -> None:
    index_path = task_dir / 'index.json'
    index_data = load_json(index_path)
    if not index_data:
        return
    index_data.update(updates)
    if touch_time:
        index_data['last_updated'] = timestamp()
    save_json(index_path, index_data)


def resolve_active_run(task_dir: Path) -> Tuple[str, Path]:
    runs_dir = task_dir / 'runs'
    if not runs_dir.exists() or not runs_dir.is_dir():
        raise ValueError(f'Runs directory not found: {runs_dir}')

    index_data = load_json(task_dir / 'index.json')
    for key in ('active_run', 'last_run'):
        run_name = str(index_data.get(key, '')).strip()
        if run_name:
            run_dir = runs_dir / run_name
            if run_dir.exists() and run_dir.is_dir():
                if key != 'active_run':
                    update_index(task_dir, {'active_run': run_name})
                return run_name, run_dir

    candidates = []
    for child in runs_dir.iterdir():
        if child.is_dir() and RUN_PREFIX_RE.match(child.name):
            candidates.append(child)
    if not candidates:
        raise ValueError('No run folders found. Use --new-run to create one.')

    candidates.sort(key=lambda item: item.name)
    active_dir = candidates[-1]
    update_index(task_dir, {'active_run': active_dir.name, 'last_run': active_dir.name})
    return active_dir.name, active_dir


def create_run(task_dir: Path, run_name: str) -> Dict[str, str]:
    created_at = timestamp()
    date_part = datestamp()
    runs_dir = task_dir / 'runs'
    runs_dir.mkdir(parents=True, exist_ok=True)

    run_number = next_run_number(runs_dir)
    run_short_name = sanitize_component(run_name, 'work-session')
    run_folder_name = f'{run_number:03d}-{run_short_name}-{date_part}'
    run_dir = runs_dir / run_folder_name
    run_dir.mkdir(parents=False, exist_ok=False)

    run_summary_path = run_dir / 'run_summary.md'
    write_text(run_summary_path, run_summary_template(run_number, run_short_name, created_at))

    update_index(task_dir, {'active_run': run_folder_name, 'last_run': run_folder_name})
    append_log(task_dir, f'Run created: {run_folder_name}')

    return {
        'run_dir': str(run_dir),
        'run_summary': str(run_summary_path),
        'run_name': run_short_name,
        'run_folder_name': run_folder_name,
        'created_at': created_at,
        'run_number': f'{run_number:03d}',
    }


def create_task(args: argparse.Namespace) -> Dict[str, str]:
    if not args.title:
        raise ValueError('A task title is required when creating a new task.')

    created_at = timestamp()
    date_part = datestamp()
    root_dir = Path(args.root).expanduser().resolve()
    root_dir.mkdir(parents=True, exist_ok=True)

    task_short_name = sanitize_component(args.title, 'untitled')
    requested_task_dir = root_dir / f'{task_short_name}-{date_part}'
    task_dir = unique_dir(requested_task_dir)
    task_dir.mkdir(parents=False, exist_ok=False)

    runs_dir = task_dir / 'runs'
    runs_dir.mkdir(exist_ok=True)

    first_run_name = sanitize_component(args.run or 'initial-intake', 'initial-intake')
    first_run_number = 1
    first_run_folder_name = f'{first_run_number:03d}-{first_run_name}-{date_part}'
    first_run_dir = runs_dir / first_run_folder_name
    first_run_dir.mkdir(exist_ok=False)

    task_md_path = task_dir / 'task.md'
    request_path = task_dir / 'request.md'
    index_path = task_dir / 'index.json'
    log_path = task_dir / 'task.log'
    error_notes_path = task_dir / 'error_notes.md'
    run_summary_path = first_run_dir / 'run_summary.md'

    write_text(task_md_path, task_md_template(args.title, created_at, first_run_name))
    write_text(request_path, request_initial_text(read_request_value(args) or ''))
    save_json(index_path, default_index(args.title, task_short_name, created_at, first_run_folder_name))
    write_text(log_path, f'[{created_at}] Task created: {task_dir.name}\n')
    write_text(error_notes_path, error_notes_template())
    write_text(run_summary_path, run_summary_template(first_run_number, first_run_name, created_at))

    return {
        'mode': 'new_task',
        'root_dir': str(root_dir),
        'task_dir': str(task_dir),
        'task_folder_name': task_dir.name,
        'task_md': str(task_md_path),
        'request_md': str(request_path),
        'index_json': str(index_path),
        'task_log': str(log_path),
        'error_notes': str(error_notes_path),
        'run_dir': str(first_run_dir),
        'run_summary': str(run_summary_path),
        'run_name': first_run_name,
        'run_folder_name': first_run_folder_name,
        'created_at': created_at,
    }


def read_request_value(args: argparse.Namespace) -> str:
    if args.request_file:
        request_path = Path(args.request_file).expanduser().resolve()
        return read_text(request_path)
    return args.request or ''


def resume_task(args: argparse.Namespace) -> Dict[str, str]:
    task_dir = Path(args.task_dir).expanduser().resolve()
    if not task_dir.exists() or not task_dir.is_dir():
        raise ValueError(f'Task directory not found: {task_dir}')

    if args.run:
        raise ValueError('Use --new-run with --run to create a new run. Without --new-run the script returns the active run.')

    run_folder_name, run_dir = resolve_active_run(task_dir)
    run_summary_path = ensure_run_summary(run_dir)

    result = {
        'mode': 'active_run',
        'task_dir': str(task_dir),
        'run_dir': str(run_dir),
        'run_summary': str(run_summary_path),
        'run_folder_name': run_folder_name,
    }

    request_value = read_request_value(args).strip()
    if request_value:
        append_request_clarification(task_dir, request_value)
        update_index(task_dir, {'active_run': run_folder_name}, touch_time=True)
        append_log(task_dir, f'Clarification appended while using active run: {run_folder_name}')
        result['request_updated'] = str(task_dir / 'request.md')

    return result


def add_run(args: argparse.Namespace) -> Dict[str, str]:
    task_dir = Path(args.task_dir).expanduser().resolve()
    if not task_dir.exists() or not task_dir.is_dir():
        raise ValueError(f'Task directory not found: {task_dir}')

    result = {'mode': 'new_run', 'task_dir': str(task_dir)}
    result.update(create_run(task_dir, args.run or 'work-session'))

    request_value = read_request_value(args).strip()
    if request_value:
        append_request_clarification(task_dir, request_value)
        result['request_updated'] = str(task_dir / 'request.md')

    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Initialize a task folder, return the active run, or create a new run.'
    )
    parser.add_argument('title', nargs='?', help='Task title when creating a new task.')
    parser.add_argument('--root', default='tasks', help='Task root directory. Defaults to ./tasks')
    parser.add_argument('--run', help='Run name. Used for a new task or with --new-run.')
    parser.add_argument('--task-dir', help='Existing task directory. Returns the active run unless --new-run is provided.')
    parser.add_argument('--new-run', action='store_true', help='Create a new run inside an existing task.')
    parser.add_argument('--request', help='Original request text or a new clarification to append.')
    parser.add_argument('--request-file', help='Read request text from a UTF-8 text file.')
    parser.add_argument('--json', action='store_true', help='Print machine-readable JSON output.')
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.request and args.request_file:
            raise ValueError('Use either --request or --request-file, not both.')

        if args.task_dir and args.new_run:
            result = add_run(args)
        elif args.task_dir:
            result = resume_task(args)
        else:
            result = create_task(args)

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print('Done.')
            for key, value in result.items():
                print(f'{key}: {value}')
        return 0
    except Exception as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
