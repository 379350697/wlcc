#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parent.parent


def slugify(text: str):
    text = text.strip().lower()
    text = re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text or 'real-task'


def now_text():
    return datetime.now().strftime('%Y-%m-%d %H:%M Asia/Shanghai')


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Ingest a real user task into runtime canonical state.')
    parser.add_argument('--title', required=True)
    parser.add_argument('--goal', required=True)
    parser.add_argument('--source', default='user-directive')
    parser.add_argument('--priority', default='P1')
    parser.add_argument('--owner-context', default='current-session')
    parser.add_argument('--execution-mode', default='live')
    parser.add_argument('--project-root', default=str(root))
    parser.add_argument('--task-id')
    args = parser.parse_args()

    project_root = Path(args.project_root)
    task_id = args.task_id or f"real-{slugify(args.title)}"
    updated_at = now_text()

    subprocess.run([
        'python3', str(project_root / 'scripts' / 'write_state_store.py'),
        '--project-root', str(project_root),
        '--task-id', task_id,
        '--project', project_root.name,
        '--goal', args.goal,
        '--status', 'doing',
        '--priority', args.priority,
        '--dependencies', '[]',
        '--override', 'none',
        '--latest-result', '真实任务已接入 runtime。',
        '--blocker', '无',
        '--next-step', '进入 lifecycle=ingested，并等待正式推进。',
        '--last-success', '真实任务 ingest 已完成。',
        '--last-failure', '无',
        '--updated-at', updated_at,
    ], check=True)

    state_path = project_root / '.agent' / 'state' / 'tasks' / f'{task_id}.json'
    data = json.loads(state_path.read_text(encoding='utf-8'))
    data.update({
        'kind': 'real',
        'source': args.source,
        'executionMode': args.execution_mode,
        'ownerContext': args.owner_context,
        'supervisionState': 'ingested',
        'eligibleForScheduling': True,
        'isPrimaryTrack': True,
        'lifecycle': 'ingested',
        'title': args.title,
    })
    write_json(state_path, data)

    supervision_path = project_root / '.agent' / 'state' / 'supervision' / f'{task_id}.json'
    write_json(supervision_path, {
        'taskId': task_id,
        'status': 'ingested',
        'lastHeartbeatAt': None,
        'lastResumeAt': None,
        'lastHandoffAt': None,
        'stale': False,
        'updatedAt': updated_at,
    })

    subprocess.run(['python3', str(project_root / 'scripts' / 'render_state_views.py'), '--project-root', str(project_root), '--task-id', task_id], check=True)
    subprocess.run(['python3', str(project_root / 'scripts' / 'build_next_task_from_state.py')], cwd=str(project_root), check=True)
    subprocess.run(['python3', str(project_root / 'scripts' / 'resume_task.py'), '--project-root', str(project_root), '--task-id', task_id], check=True)
    lifecycle_script = project_root / 'scripts' / 'update_task_lifecycle.py'
    if lifecycle_script.exists():
        subprocess.run(['python3', str(lifecycle_script), '--task-id', task_id, '--to', 'active'], check=True)

    out = project_root / 'tests' / 'INGEST_REAL_TASK_RESULT.md'
    lines = ['# INGEST_REAL_TASK_RESULT', '', '## summary']
    lines.append(f'- taskId: {task_id}')
    lines.append(f'- kind: real')
    lines.append(f'- source: {args.source}')
    lines.append(f'- executionMode: {args.execution_mode}')
    lines.append(f'- ownerContext: {args.owner_context}')
    lines.append(f'- lifecycle: ingested')
    lines.append(f'- eligibleForScheduling: true')
    lines.append(f'- isPrimaryTrack: true')
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {out}')


if __name__ == '__main__':
    main()
