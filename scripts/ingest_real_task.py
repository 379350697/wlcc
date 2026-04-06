#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.common.io import write_json
from runtime.common.models import TaskState
from runtime.common.paths import RuntimePaths
from runtime.common.time import now_iso
from runtime.resume.service import write_resume_output
from runtime.scheduling.next_task import build_next_task_from_state_dir, write_state_views
from runtime.state.lifecycle import transition_lifecycle
from runtime.state.store import write_task_state


def slugify(text: str):
    text = text.strip().lower()
    text = re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text or 'real-task'


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
    paths = RuntimePaths(project_root)
    task_id = args.task_id or f"real-{slugify(args.title)}"
    updated_at = now_iso()

    task = TaskState(
        taskId=task_id,
        project=project_root.name,
        goal=args.goal,
        status='doing',
        priority=args.priority,
        dependencies=[],
        override='none',
        latestResult='真实任务已接入 runtime。',
        blocker='无',
        nextStep='进入 lifecycle=ingested，并等待正式推进。',
        lastSuccess='真实任务 ingest 已完成。',
        lastFailure='无',
        updatedAt=updated_at,
        kind='real',
        source=args.source,
        executionMode=args.execution_mode,
        ownerContext=args.owner_context,
        supervisionState='ingested',
        eligibleForScheduling=True,
        isPrimaryTrack=True,
        lifecycle='ingested',
        title=args.title,
    )
    task_path, index_path = write_task_state(paths, task)

    supervision_path = paths.supervision_state_dir / f'{task_id}.json'
    write_json(supervision_path, {
        'taskId': task_id,
        'status': 'ingested',
        'lastHeartbeatAt': None,
        'lastResumeAt': None,
        'lastHandoffAt': None,
        'stale': False,
        'updatedAt': updated_at,
    })

    build_next_task_from_state_dir(
        paths.tasks_state_dir,
        paths.state_dir / 'next-task.json',
        paths.agent_dir / 'NEXT_TASK.md',
        paths.state_dir / 'next-task-input.json',
    )
    write_state_views(paths.tasks_state_dir, paths.agent_dir / 'tasks', paths.agent_dir / 'resume', project_root / 'TASKS.md')
    write_resume_output(project_root, task_id)
    transition_lifecycle(paths, task_id, 'active')

    out = project_root / 'tests' / 'INGEST_REAL_TASK_RESULT.md'
    lines = ['# INGEST_REAL_TASK_RESULT', '', '## summary']
    lines.append(f'- taskId: {task_id}')
    lines.append(f'- taskStatePath: {task_path}')
    lines.append(f'- indexPath: {index_path}')
    lines.append('- kind: real')
    lines.append(f'- source: {args.source}')
    lines.append(f'- executionMode: {args.execution_mode}')
    lines.append(f'- ownerContext: {args.owner_context}')
    lines.append('- lifecycle: ingested')
    lines.append('- eligibleForScheduling: true')
    lines.append('- isPrimaryTrack: true')
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: taskId {task_id}')
    print(f'OK: wrote {task_path}')
    print(f'OK: wrote {index_path}')
    print(f'OK: wrote {out}')


if __name__ == '__main__':
    main()
