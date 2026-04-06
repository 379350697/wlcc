#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description='Resume a real task through runtime protocol.')
    parser.add_argument('--task-id', required=True)
    args = parser.parse_args()

    task_path = root / '.agent' / 'state' / 'tasks' / f'{args.task_id}.json'
    if not task_path.exists():
        raise SystemExit(f'missing task: {args.task_id}')

    task = load_json(task_path)
    if task.get('kind') != 'real':
        raise SystemExit('resume_real_task only supports kind=real')

    subprocess.run(['python3', str(root / 'scripts' / 'resume_task.py'), '--project-root', str(root), '--task-id', args.task_id], check=True)
    subprocess.run(['python3', str(root / 'scripts' / 'update_task_lifecycle.py'), '--task-id', args.task_id, '--to', 'active'], check=True)
    subprocess.run(['python3', str(root / 'scripts' / 'run_task_supervision.py'), '--task-id', args.task_id, '--trigger', 'on_interruption_detected'], check=True)

    supervision_path = root / '.agent' / 'state' / 'supervision' / f'{args.task_id}.json'
    supervision = load_json(supervision_path) if supervision_path.exists() else {}

    out = root / 'tests' / 'RESUME_REAL_TASK_RESULT.md'
    lines = ['# RESUME_REAL_TASK_RESULT', '', '## summary']
    lines.append(f'- taskId: {args.task_id}')
    lines.append(f"- lifecycle: {load_json(task_path).get('lifecycle', 'unknown')}")
    lines.append(f"- supervisionStatus: {supervision.get('status', 'unknown')}")
    lines.append(f"- lastResumeAt: {supervision.get('lastResumeAt', 'unknown')}")
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {out}')


if __name__ == '__main__':
    main()
