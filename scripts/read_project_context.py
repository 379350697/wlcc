#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.resume.service import collect_context_payload


def read_if_exists(path: Path):
    if path.exists():
        return path.read_text(encoding='utf-8').strip()
    return None


def state_first_fallback(root: Path, task_id: str | None):
    result = {
        'long_term_rules': read_if_exists(root / 'memory' / 'long-term' / 'RULES.md'),
        'project_readme': read_if_exists(root / 'README.md'),
        'project_status': read_if_exists(root / 'STATUS.md'),
        'project_decisions': read_if_exists(root / 'DECISIONS.md'),
        'project_tasks_view': read_if_exists(root / 'TASKS.md'),
        'project_incidents': read_if_exists(root / 'INCIDENTS.md'),
        'session_summary': read_if_exists(root / 'memory' / 'session' / 'SESSION_SUMMARY.md'),
        'state_index': read_if_exists(root / '.agent' / 'state' / 'index.json'),
        'next_task_state': read_if_exists(root / '.agent' / 'state' / 'next-task.json'),
        'next_task_view': read_if_exists(root / '.agent' / 'NEXT_TASK.md'),
    }

    if task_id:
        result['task_state_json'] = read_if_exists(root / '.agent' / 'state' / 'tasks' / f'{task_id}.json')
        result['task_view'] = read_if_exists(root / '.agent' / 'tasks' / f'{task_id}.md')
        result['resume_view'] = read_if_exists(root / '.agent' / 'resume' / f'{task_id}-resume.md')
        result['task_changelog'] = read_if_exists(root / '.agent' / 'logs' / 'CHANGELOG.md')

    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Read layered project context with compatibility fallback.')
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--task-id')
    args = parser.parse_args()

    root = Path(args.project_root)
    if args.task_id:
        print(json.dumps(collect_context_payload(root, args.task_id), ensure_ascii=False, indent=2))
        return

    state_first_fallback(root, args.task_id)


if __name__ == '__main__':
    main()
