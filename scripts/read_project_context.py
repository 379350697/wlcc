#!/usr/bin/env python3
import argparse
from pathlib import Path


def read_if_exists(path: Path):
    if path.exists():
        return path.read_text(encoding='utf-8').strip()
    return None


def main():
    parser = argparse.ArgumentParser(description='Read layered project context with compatibility fallback.')
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--task-id')
    args = parser.parse_args()

    root = Path(args.project_root)

    result = {
        'long_term_rules': read_if_exists(root / 'memory' / 'long-term' / 'RULES.md'),
        'project_readme': read_if_exists(root / 'README.md'),
        'project_status': read_if_exists(root / 'STATUS.md'),
        'project_decisions': read_if_exists(root / 'DECISIONS.md'),
        'project_tasks': read_if_exists(root / 'TASKS.md'),
        'project_incidents': read_if_exists(root / 'INCIDENTS.md'),
        'session_summary': read_if_exists(root / 'memory' / 'session' / 'SESSION_SUMMARY.md'),
    }

    if args.task_id:
        result['task_state'] = read_if_exists(root / '.agent' / 'tasks' / f'{args.task_id}.md')
        result['resume_state'] = read_if_exists(root / '.agent' / 'resume' / f'{args.task_id}-resume.md')
        result['task_changelog'] = read_if_exists(root / '.agent' / 'logs' / 'CHANGELOG.md')

    print('# Layered Read Result')
    for key, value in result.items():
        print(f'\n## {key}')
        if value:
            print(value)
        else:
            print('MISSING')


if __name__ == '__main__':
    main()
