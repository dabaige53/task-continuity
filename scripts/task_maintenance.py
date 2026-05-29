#!/usr/bin/env python3
"""Maintain a task-continuity workspace.

Commands:
  ensure <task_dir>
  promote <task_dir> <source_file> --kind material|knowledge|deliverable
  dedupe <task_dir>

The script uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

CANONICAL_KEYS = {
    'material': 'materials',
    'knowledge': 'knowledge',
    'deliverable': 'deliverables',
}

DESTINATIONS = {
    'material': Path('materials'),
    'knowledge': Path('knowledge'),
    'deliverable': Path('deliverables/current'),
}

IGNORE_DIRS = {'.git', '__pycache__'}


def now() -> datetime:
    return datetime.now()


def timestamp(dt: Optional[datetime] = None) -> str:
    return (dt or now()).strftime('%Y-%m-%d %H:%M')


def stamp(dt: Optional[datetime] = None) -> str:
    return (dt or now()).strftime('%Y%m%d%H%M%S')


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


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
    with log_path.open('a', encoding='utf-8') as handle:
        handle.write(f'[{timestamp()}] {message}\n')


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def relative_to_task(task_dir: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(task_dir.resolve()).as_posix()
    except ValueError:
        return str(path)


def ensure_structure(task_dir: Path) -> Dict[str, Any]:
    if not task_dir.exists() or not task_dir.is_dir():
        raise ValueError(f'Task directory not found: {task_dir}')

    created_dirs: List[str] = []
    for relative in ('materials', 'knowledge', 'deliverables/current', 'archive', 'runs'):
        path = task_dir / relative
        if not path.exists():
            created_dirs.append(relative)
        path.mkdir(parents=True, exist_ok=True)

    index_path = task_dir / 'index.json'
    index_data = load_json(index_path)
    index_changed = False
    if index_data:
        if 'durable_dirs' not in index_data:
            index_data['durable_dirs'] = {
                'materials': 'materials',
                'knowledge': 'knowledge',
                'deliverables': 'deliverables/current',
                'archive': 'archive',
            }
            index_changed = True
        if 'canonical_files' not in index_data or not isinstance(index_data.get('canonical_files'), dict):
            index_data['canonical_files'] = {
                'materials': [],
                'knowledge': [],
                'deliverables': [],
            }
            index_changed = True
        else:
            for key in ('materials', 'knowledge', 'deliverables'):
                if key not in index_data['canonical_files']:
                    index_data['canonical_files'][key] = []
                    index_changed = True
        if 'active_run_policy' not in index_data:
            index_data['active_run_policy'] = 'reuse active run until the work meaningfully shifts to a new phase'
            index_changed = True
        if index_changed:
            index_data['last_updated'] = timestamp()
            save_json(index_path, index_data)

    return {
        'mode': 'ensure',
        'task_dir': str(task_dir),
        'created_dirs': created_dirs,
        'index_updated': index_changed,
    }


def resolve_source(task_dir: Path, source: str) -> Path:
    source_path = Path(source).expanduser()
    candidates = []
    if source_path.is_absolute():
        candidates.append(source_path)
    else:
        candidates.append(Path.cwd() / source_path)
        candidates.append(task_dir / source_path)
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()
    raise ValueError(f'Source file not found: {source}')


def unique_archive_path(archive_dir: Path, original: Path) -> Path:
    archive_dir.mkdir(parents=True, exist_ok=True)
    name = f'{original.stem}-{stamp()}{original.suffix}'
    candidate = archive_dir / name
    counter = 2
    while candidate.exists():
        name = f'{original.stem}-{stamp()}-{counter:02d}{original.suffix}'
        candidate = archive_dir / name
        counter += 1
    return candidate


def update_canonical_index(task_dir: Path, kind: str, dest: Path, source: Optional[Path], action: str) -> None:
    index_path = task_dir / 'index.json'
    index_data = load_json(index_path)
    if not index_data:
        return

    canonical = index_data.setdefault('canonical_files', {})
    for key in ('materials', 'knowledge', 'deliverables'):
        canonical.setdefault(key, [])

    bucket = CANONICAL_KEYS[kind]
    rel_dest = relative_to_task(task_dir, dest)
    rel_source = relative_to_task(task_dir, source) if source else ''
    entries = [entry for entry in canonical[bucket] if entry.get('path') != rel_dest]
    entries.append({
        'path': rel_dest,
        'kind': kind,
        'source': rel_source,
        'updated_at': timestamp(),
        'action': action,
    })
    canonical[bucket] = entries
    index_data['canonical_files'] = canonical
    index_data['last_updated'] = timestamp()
    save_json(index_path, index_data)


def append_run_promotion_note(task_dir: Path, source: Path, dest: Path, action: str) -> None:
    parts = source.resolve().parts
    try:
        run_index = parts.index('runs')
    except ValueError:
        return
    if len(parts) <= run_index + 1:
        return
    run_dir = Path(*parts[:run_index + 2])
    if not run_dir.exists():
        return
    run_summary = run_dir / 'run_summary.md'
    rel_source = relative_to_task(task_dir, source)
    rel_dest = relative_to_task(task_dir, dest)
    note = f'\n### {timestamp()}\n- {action}: `{rel_source}` -> `{rel_dest}`\n'
    if run_summary.exists():
        with run_summary.open('a', encoding='utf-8') as handle:
            handle.write(note)


def promote(args: argparse.Namespace) -> Dict[str, Any]:
    task_dir = Path(args.task_dir).expanduser().resolve()
    ensure_structure(task_dir)
    source = resolve_source(task_dir, args.source_file)
    if args.kind not in DESTINATIONS:
        raise ValueError(f'Unsupported kind: {args.kind}')

    dest_dir = task_dir / DESTINATIONS[args.kind]
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_name = args.name or source.name
    dest = dest_dir / dest_name
    action = args.mode
    archived_path = None
    duplicate_removed = False

    if source.resolve() == dest.resolve():
        update_canonical_index(task_dir, args.kind, dest, source, 'already_current')
        append_log(task_dir, f'Canonical file confirmed: {relative_to_task(task_dir, dest)}')
        return {
            'mode': 'promote',
            'action': 'already_current',
            'task_dir': str(task_dir),
            'destination': str(dest),
        }

    if dest.exists():
        if sha256(dest) == sha256(source):
            if args.mode == 'move':
                source.unlink()
                duplicate_removed = True
            action = 'deduplicated'
        elif args.replace:
            archived_path = unique_archive_path(task_dir / 'archive', dest)
            shutil.move(str(dest), str(archived_path))
        else:
            raise ValueError(
                f'Destination exists with different content: {dest}. Use --replace to archive it first.'
            )

    if action != 'deduplicated':
        if args.mode == 'copy':
            shutil.copy2(str(source), str(dest))
        elif args.mode == 'move':
            shutil.move(str(source), str(dest))
        else:
            raise ValueError(f'Unsupported mode: {args.mode}')

    update_canonical_index(task_dir, args.kind, dest, source, action)
    append_run_promotion_note(task_dir, source, dest, action)
    append_log(task_dir, f'Promoted {args.kind}: {relative_to_task(task_dir, dest)}')

    return {
        'mode': 'promote',
        'action': action,
        'kind': args.kind,
        'task_dir': str(task_dir),
        'source': str(source),
        'destination': str(dest),
        'archived_previous': str(archived_path) if archived_path else None,
        'duplicate_removed': duplicate_removed,
    }


def iter_files(task_dir: Path) -> Iterable[Path]:
    for root, dirs, files in os.walk(task_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        root_path = Path(root)
        for file_name in files:
            path = root_path / file_name
            if path.name == '.DS_Store':
                continue
            yield path


def duplicate_report(task_dir: Path) -> Dict[str, Any]:
    ensure_structure(task_dir)
    by_hash: Dict[str, List[str]] = {}
    for path in iter_files(task_dir):
        try:
            digest = sha256(path)
        except OSError:
            continue
        by_hash.setdefault(digest, []).append(relative_to_task(task_dir, path))

    duplicates = []
    for digest, paths in sorted(by_hash.items()):
        if len(paths) > 1:
            duplicates.append({'sha256': digest, 'paths': sorted(paths)})

    return {
        'mode': 'dedupe',
        'task_dir': str(task_dir),
        'duplicate_groups': duplicates,
        'duplicate_group_count': len(duplicates),
    }


def write_duplicate_report(task_dir: Path, report: Dict[str, Any]) -> Path:
    lines = ['# Maintenance Report', '', f'Generated: {timestamp()}', '']
    groups = report.get('duplicate_groups', [])
    if not groups:
        lines.append('No duplicate file hashes found.')
    else:
        lines.append('## Duplicate File Groups')
        lines.append('')
        for index, group in enumerate(groups, start=1):
            lines.append(f'### Group {index}')
            lines.append(f'- sha256: `{group["sha256"]}`')
            for path in group['paths']:
                lines.append(f'- `{path}`')
            lines.append('')
    report_path = task_dir / 'knowledge' / 'maintenance_report.md'
    write_text(report_path, '\n'.join(lines).rstrip() + '\n')
    append_log(task_dir, f'Maintenance duplicate report written: {relative_to_task(task_dir, report_path)}')
    return report_path


def dedupe(args: argparse.Namespace) -> Dict[str, Any]:
    task_dir = Path(args.task_dir).expanduser().resolve()
    report = duplicate_report(task_dir)
    if args.write_report:
        report_path = write_duplicate_report(task_dir, report)
        report['report_path'] = str(report_path)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Maintain a task-continuity workspace.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    ensure_parser = subparsers.add_parser('ensure', help='Ensure optimized task structure exists.')
    ensure_parser.add_argument('task_dir')
    ensure_parser.add_argument('--json', action='store_true')

    promote_parser = subparsers.add_parser('promote', help='Promote a durable file from a run to task root.')
    promote_parser.add_argument('task_dir')
    promote_parser.add_argument('source_file')
    promote_parser.add_argument('--kind', required=True, choices=['material', 'knowledge', 'deliverable'])
    promote_parser.add_argument('--name', help='Destination filename. Defaults to the source filename.')
    promote_parser.add_argument('--mode', choices=['move', 'copy'], default='move')
    promote_parser.add_argument('--replace', action='store_true', help='Archive existing destination with different content.')
    promote_parser.add_argument('--json', action='store_true')

    dedupe_parser = subparsers.add_parser('dedupe', help='Report duplicate file hashes in the task folder.')
    dedupe_parser.add_argument('task_dir')
    dedupe_parser.add_argument('--write-report', action='store_true')
    dedupe_parser.add_argument('--json', action='store_true')

    return parser


def print_result(result: Dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print('Done.')
    for key, value in result.items():
        print(f'{key}: {value}')


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == 'ensure':
            result = ensure_structure(Path(args.task_dir).expanduser().resolve())
        elif args.command == 'promote':
            result = promote(args)
        elif args.command == 'dedupe':
            result = dedupe(args)
        else:
            raise ValueError(f'Unsupported command: {args.command}')
        print_result(result, getattr(args, 'json', False))
        return 0
    except Exception as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
