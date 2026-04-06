#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.resume.service import resume_real_task_flow


def main():
    parser = argparse.ArgumentParser(description='Resume a real task through runtime protocol.')
    parser.add_argument('--task-id', required=True)
    args = parser.parse_args()

    result = resume_real_task_flow(root, args.task_id)
    task = result['task']
    supervision = result['supervision']

    out = root / 'tests' / 'RESUME_REAL_TASK_RESULT.md'
    lines = ['# RESUME_REAL_TASK_RESULT', '', '## summary']
    lines.append(f'- taskId: {args.task_id}')
    lines.append(f"- lifecycle: {task.get('lifecycle', 'unknown')}")
    lines.append(f"- supervisionStatus: {supervision.get('status', 'unknown')}")
    lines.append(f"- lastResumeAt: {supervision.get('lastResumeAt', 'unknown')}")
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {out}')


if __name__ == '__main__':
    main()
