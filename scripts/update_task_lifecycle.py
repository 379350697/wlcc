#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from runtime.common.paths import RuntimePaths
from runtime.state.lifecycle import transition_lifecycle


def main():
    parser = argparse.ArgumentParser(description='Update task lifecycle with transition validation.')
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--to', required=True)
    args = parser.parse_args()

    paths = RuntimePaths(root)
    task, supervision, current = transition_lifecycle(paths, args.task_id, args.to)

    out = paths.root / 'tests' / 'TASK_LIFECYCLE_RESULT.md'
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = ['# TASK_LIFECYCLE_RESULT', '', '## summary']
    lines.append(f'- taskId: {args.task_id}')
    lines.append(f'- from: {current}')
    lines.append(f'- to: {args.to}')
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"OK: wrote {paths.tasks_state_dir / f'{args.task_id}.json'}")
    print(f'OK: wrote {out}')


if __name__ == '__main__':
    main()
