#!/usr/bin/env python3
"""Bootstrap the minimal runtime fixtures required by the current standard contract."""
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
from runtime.state.store import write_task_state


PRIMARY_REAL_TASK = 'real-close-runtime-final-target'
HANDOFF_FIXTURE_TASK = 'demo-long-chain-autonomy'


def ensure_task(paths: RuntimePaths, task: TaskState) -> None:
    task_path = paths.tasks_state_dir / f'{task.taskId}.json'
    if not task_path.exists():
        write_task_state(paths, task)


def ensure_supervision(paths: RuntimePaths, task_id: str, status: str = 'active') -> None:
    path = paths.supervision_state_dir / f'{task_id}.json'
    if not path.exists():
        write_json(path, {
            'taskId': task_id,
            'status': status,
            'lastHeartbeatAt': now_iso() if status == 'active' else None,
            'lastResumeAt': now_iso() if status == 'active' else None,
            'lastHandoffAt': None,
            'stale': False,
            'updatedAt': now_iso(),
        })


def ensure_handoff(paths: RuntimePaths, task_id: str) -> None:
    handoff_path = paths.state_dir / 'handoffs' / f'{task_id}.json'
    if not handoff_path.exists():
        write_json(handoff_path, {
            'taskId': task_id,
            'fromAgent': 'coder',
            'toAgent': 'reviewer',
            'reason': 'bootstrap-fixture',
            'linkedResumeState': f'.agent/state/{task_id}-resume-state.json',
            'linkedNextTask': '.agent/state/next-task.json',
            'updatedAt': now_iso(),
        })

    ownership_path = paths.state_dir / 'ownership' / f'{task_id}.json'
    if not ownership_path.exists():
        write_json(ownership_path, {
            'taskId': task_id,
            'owner': 'ceo',
            'executor': 'coder',
            'reviewer': 'reviewer',
            'updatedAt': now_iso(),
        })


def main() -> None:
    paths = RuntimePaths(root)
    updated_at = now_iso()

    ensure_task(paths, TaskState(
        taskId=PRIMARY_REAL_TASK,
        project=root.name,
        title='真实任务最终收口目标',
        goal='作为当前标准运行版 contract 的主 real runtime fixture。',
        status='doing',
        priority='P0',
        dependencies=[],
        override='none',
        latestResult='bootstrap fixture ready',
        blocker='无',
        nextStep='继续推进 runtime bundle 校验。',
        lastSuccess='fixture created',
        lastFailure='无',
        updatedAt=updated_at,
        kind='real',
        source='bootstrap-fixture',
        executionMode='live',
        ownerContext='local-project',
        supervisionState='active',
        eligibleForScheduling=True,
        isPrimaryTrack=True,
        lifecycle='active',
    ))
    ensure_supervision(paths, PRIMARY_REAL_TASK)
    ensure_handoff(paths, PRIMARY_REAL_TASK)
    write_resume_output(root, PRIMARY_REAL_TASK)

    ensure_task(paths, TaskState(
        taskId=HANDOFF_FIXTURE_TASK,
        project=root.name,
        title='handoff compatibility fixture',
        goal='兼容 handoff / ownership demo 链路。',
        status='doing',
        priority='P1',
        dependencies=[],
        override='none',
        latestResult='demo handoff fixture ready',
        blocker='无',
        nextStep='供 handoff smoke 使用。',
        lastSuccess='fixture created',
        lastFailure='无',
        updatedAt=updated_at,
        kind='sample',
        source='bootstrap-fixture',
        executionMode='sample-only',
        ownerContext='local-project',
        supervisionState='legacy',
        eligibleForScheduling=False,
        isPrimaryTrack=False,
        lifecycle='active',
    ))
    ensure_handoff(paths, HANDOFF_FIXTURE_TASK)

    build_next_task_from_state_dir(
        paths.tasks_state_dir,
        paths.state_dir / 'next-task.json',
        paths.agent_dir / 'NEXT_TASK.md',
        paths.state_dir / 'next-task-input.json',
    )
    write_state_views(paths.tasks_state_dir, paths.agent_dir / 'tasks', paths.agent_dir / 'resume', root / 'TASKS.md')

    print('OK: bootstrap runtime fixtures complete')
    print(f'OK: primary fixture -> {PRIMARY_REAL_TASK}')
    print(f'OK: handoff fixture -> {HANDOFF_FIXTURE_TASK}')


if __name__ == '__main__':
    main()
