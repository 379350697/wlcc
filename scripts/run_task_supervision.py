#!/usr/bin/env python3
import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parent.parent


def now_text():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def append_log(path: Path, line: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(line + '\n')


def task_paths(task_id: str):
    return {
        'task': root / '.agent' / 'state' / 'tasks' / f'{task_id}.json',
        'supervision': root / '.agent' / 'state' / 'supervision' / f'{task_id}.json',
        'handoff': root / '.agent' / 'state' / 'handoffs' / f'{task_id}.json',
    }


def emit_heartbeat(task, trigger_reason, next_step=None, requires_human=False, blocker=None):
    cmd = [
        'python3', str(root / 'scripts' / 'emit_heartbeat.py'),
        '--stage', f"lifecycle-{task.get('lifecycle', 'unknown')}",
        '--current-task', task['taskId'],
        '--next-step', next_step or task.get('nextStep', 'none'),
        '--trigger-reason', trigger_reason,
        '--risk-or-blocker', blocker or task.get('blocker', 'none'),
        '--throttle-seconds', '0',
    ]
    if requires_human:
        cmd.append('--requires-human')
    subprocess.run(cmd, check=True)
    subprocess.run(['python3', str(root / 'scripts' / 'build_heartbeat_summary.py')], check=True)


def run_resume(task_id):
    subprocess.run(['python3', str(root / 'scripts' / 'resume_task.py'), '--project-root', str(root), '--task-id', task_id], check=True)


def run_handoff(task):
    subprocess.run([
        'python3', str(root / 'scripts' / 'write_handoff_state.py'),
        '--task-id', task['taskId'],
        '--owner', task.get('ownerContext', 'unknown'),
        '--executor', 'coder',
        '--reviewer', 'reviewer',
        '--from-agent', 'coder',
        '--to-agent', 'reviewer',
        '--reason', 'supervision-handoff',
        '--summary', f"任务 {task['taskId']} 进入 handoff 监督阶段。",
        '--next-action', 'review-runtime-state',
        '--requires-human',
    ], check=True)


def main():
    parser = argparse.ArgumentParser(description='Run unified task supervision triggers.')
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--trigger', required=True, choices=['on_task_ingested', 'on_task_changed', 'on_interruption_detected', 'on_interval', 'on_completion'])
    args = parser.parse_args()

    paths = task_paths(args.task_id)
    task = load_json(paths['task'], None)
    if not task:
        raise SystemExit(f'missing task: {args.task_id}')
    supervision = load_json(paths['supervision'], {'taskId': args.task_id})
    supervision['taskKind'] = task.get('kind', 'unknown')
    supervision['scope'] = 'real-task-first' if task.get('kind') == 'real' else 'sample-scope'

    supervisor_log = root / '.agent' / 'logs' / 'SUPERVISOR_ACTIONS_LOG.md'
    stalled_log = root / '.agent' / 'logs' / 'STALLED_TASK_LOG.md'
    missed_log = root / '.agent' / 'logs' / 'MISSED_HEARTBEAT_LOG.md'

    if args.trigger == 'on_task_ingested':
        supervision['status'] = 'active'
        supervision['lastHeartbeatAt'] = now_text()
        supervision['stale'] = False
        emit_heartbeat(task, 'periodic-step', next_step=task.get('nextStep', 'continue-runtime'))
        append_log(supervisor_log, f"- {now_text()} | task={args.task_id} | trigger=on_task_ingested | status=active")
    elif args.trigger == 'on_task_changed':
        supervision['status'] = task.get('supervisionState', 'active')
        supervision['lastHeartbeatAt'] = now_text()
        emit_heartbeat(task, 'periodic-step')
        append_log(supervisor_log, f"- {now_text()} | task={args.task_id} | trigger=on_task_changed | status={supervision['status']}")
    elif args.trigger == 'on_interruption_detected':
        supervision['lastResumeAt'] = now_text()
        supervision['status'] = 'resume-prepared'
        run_resume(args.task_id)
        append_log(supervisor_log, f"- {now_text()} | task={args.task_id} | trigger=on_interruption_detected | action=resume")
    elif args.trigger == 'on_interval':
        supervision['lastHeartbeatAt'] = now_text()
        supervision['stale'] = task.get('lifecycle') in {'blocked', 'waiting-human'}
        emit_heartbeat(task, 'periodic-step', requires_human=supervision['stale'])
        append_log(supervisor_log, f"- {now_text()} | task={args.task_id} | trigger=on_interval | stale={str(supervision['stale']).lower()}")
        if supervision['stale']:
            append_log(stalled_log, f"- {now_text()} | task={args.task_id} | lifecycle={task.get('lifecycle', 'unknown')} | stale=true")
            append_log(missed_log, f"- {now_text()} | task={args.task_id} | reason=blocked-or-waiting-human")
    elif args.trigger == 'on_completion':
        supervision['status'] = 'handoff-prepared'
        supervision['lastHandoffAt'] = now_text()
        run_handoff(task)
        emit_heartbeat(task, 'stage-complete-stop', next_step='close-task-runtime', requires_human=True, blocker='completion-ready')
        append_log(supervisor_log, f"- {now_text()} | task={args.task_id} | trigger=on_completion | action=handoff")

    supervision['updatedAt'] = now_text()
    save_json(paths['supervision'], supervision)

    out = root / 'tests' / 'TASK_SUPERVISION_RESULT.md'
    lines = ['# TASK_SUPERVISION_RESULT', '', '## summary']
    lines.append(f'- taskId: {args.task_id}')
    lines.append(f'- trigger: {args.trigger}')
    lines.append(f"- status: {supervision.get('status', 'unknown')}")
    lines.append(f"- stale: {str(supervision.get('stale', False)).lower()}")
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {out}')


if __name__ == '__main__':
    main()
