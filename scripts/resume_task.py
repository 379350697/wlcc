#!/usr/bin/env python3
import argparse
from pathlib import Path


def read_if_exists(path: Path):
    if path.exists():
        return path.read_text(encoding='utf-8').strip()
    return 'MISSING'


def main():
    parser = argparse.ArgumentParser(description='Resume a task from task state + resume state + TASKS summary.')
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--task-id', required=True)
    args = parser.parse_args()

    root = Path(args.project_root)
    task = read_if_exists(root / '.agent' / 'tasks' / f'{args.task_id}.md')
    resume = read_if_exists(root / '.agent' / 'resume' / f'{args.task_id}-resume.md')
    tasks = read_if_exists(root / 'TASKS.md')

    out = [
        '# RESUME_OUTPUT',
        '',
        '## task_state',
        task,
        '',
        '## resume_state',
        resume,
        '',
        '## tasks_summary',
        tasks,
    ]
    result_path = root / 'tests' / f'{args.task_id}-resume-output.md'
    result_path.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'OK: wrote {result_path}')


if __name__ == '__main__':
    main()
