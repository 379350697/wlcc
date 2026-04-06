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


def main():
    parser = argparse.ArgumentParser(description='Close a real task runtime with final handoff and archive.')
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--final-result', required=True)
    args = parser.parse_args()

    task_path = root / '.agent' / 'state' / 'tasks' / f'{args.task_id}.json'
    if not task_path.exists():
        raise SystemExit(f'missing task: {args.task_id}')
    task = load_json(task_path)
    if task.get('kind') != 'real':
        raise SystemExit('close_task_runtime only supports kind=real')

    task['latestResult'] = args.final_result
    task['status'] = 'done'
    task['blocker'] = '无'
    task['nextStep'] = 'archive'
    task['updatedAt'] = now_text()
    task_path.write_text(json.dumps(task, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    subprocess.run(['python3', str(root / 'scripts' / 'render_state_views.py'), '--project-root', str(root), '--task-id', args.task_id], check=True)
    subprocess.run(['python3', str(root / 'scripts' / 'write_handoff_state.py'), '--task-id', args.task_id, '--owner', task.get('ownerContext', 'unknown'), '--executor', 'coder', '--reviewer', 'reviewer', '--from-agent', 'coder', '--to-agent', 'reviewer', '--reason', 'final-handoff', '--summary', args.final_result, '--next-action', 'archive-runtime-task', '--requires-human'], check=True)
    subprocess.run(['python3', str(root / 'scripts' / 'run_task_supervision.py'), '--task-id', args.task_id, '--trigger', 'on_completion'], check=True)
    subprocess.run(['python3', str(root / 'scripts' / 'update_task_lifecycle.py'), '--task-id', args.task_id, '--to', 'done'], check=True)
    subprocess.run(['python3', str(root / 'scripts' / 'update_task_lifecycle.py'), '--task-id', args.task_id, '--to', 'archived'], check=True)

    closure_note = root / '.agent' / 'logs' / 'CLOSURE_NOTE.md'
    with closure_note.open('a', encoding='utf-8') as f:
        f.write(f"- {now_text()} | task={args.task_id} | finalResult={args.final_result}\n")

    out = root / 'tests' / 'CLOSE_TASK_RUNTIME_RESULT.md'
    lines = ['# CLOSE_TASK_RUNTIME_RESULT', '', '## summary']
    lines.append(f'- taskId: {args.task_id}')
    lines.append(f'- finalResult: {args.final_result}')
    lines.append('- archived: true')
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {out}')


if __name__ == '__main__':
    main()
