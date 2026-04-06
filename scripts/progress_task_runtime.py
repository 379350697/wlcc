#!/usr/bin/env python3
import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parent.parent


def now_text():
    return datetime.now().strftime('%Y-%m-%d %H:%M Asia/Shanghai')


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Unified progress entry for real task runtime.')
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--latest-result', required=True)
    parser.add_argument('--next-step', required=True)
    parser.add_argument('--blocker', default='无')
    parser.add_argument('--status')
    parser.add_argument('--lifecycle')
    args = parser.parse_args()

    task_path = root / '.agent' / 'state' / 'tasks' / f'{args.task_id}.json'
    if not task_path.exists():
        raise SystemExit(f'missing task: {args.task_id}')

    task = load_json(task_path)
    task['latestResult'] = args.latest_result
    task['nextStep'] = args.next_step
    task['blocker'] = args.blocker
    task['updatedAt'] = now_text()
    if args.status:
        task['status'] = args.status
    write_json(task_path, task)

    subprocess.run(['python3', str(root / 'scripts' / 'render_state_views.py'), '--project-root', str(root), '--task-id', args.task_id], check=True)
    subprocess.run(['python3', str(root / 'scripts' / 'build_next_task_from_state.py')], cwd=str(root), check=True)

    if args.lifecycle:
        current = load_json(task_path).get('lifecycle')
        if current != args.lifecycle:
            subprocess.run(['python3', str(root / 'scripts' / 'update_task_lifecycle.py'), '--task-id', args.task_id, '--to', args.lifecycle], check=True)

    subprocess.run(['python3', str(root / 'scripts' / 'run_task_supervision.py'), '--task-id', args.task_id, '--trigger', 'on_task_changed'], check=True)
    subprocess.run(['python3', str(root / 'scripts' / 'run_task_supervision.py'), '--task-id', args.task_id, '--trigger', 'on_interval'], check=True)

    out = root / 'tests' / 'PROGRESS_TASK_RUNTIME_RESULT.md'
    lines = ['# PROGRESS_TASK_RUNTIME_RESULT', '', '## summary']
    lines.append(f'- taskId: {args.task_id}')
    lines.append(f'- latestResult: {args.latest_result}')
    lines.append(f'- nextStep: {args.next_step}')
    lines.append(f'- blocker: {args.blocker}')
    lines.append(f"- status: {task.get('status', 'unknown')}")
    lines.append(f"- lifecycle: {load_json(task_path).get('lifecycle', 'unknown')}")
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {out}')


if __name__ == '__main__':
    main()
