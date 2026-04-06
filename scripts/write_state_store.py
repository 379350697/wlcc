#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from runtime.common.models import TaskState
from runtime.common.paths import RuntimePaths
from runtime.state.store import write_task_state


def main():
    parser = argparse.ArgumentParser(description='Write canonical task state store.')
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--project', required=True)
    parser.add_argument('--goal', required=True)
    parser.add_argument('--status', required=True)
    parser.add_argument('--priority', default='P2')
    parser.add_argument('--dependencies', default='[]')
    parser.add_argument('--override', default='none')
    parser.add_argument('--latest-result', required=True)
    parser.add_argument('--blocker', required=True)
    parser.add_argument('--next-step', required=True)
    parser.add_argument('--last-success', required=True)
    parser.add_argument('--last-failure', required=True)
    parser.add_argument('--updated-at', required=True)
    parser.add_argument('--kind', default='sample')
    parser.add_argument('--source', default='legacy')
    parser.add_argument('--execution-mode', default='sample-only')
    parser.add_argument('--owner-context', default='unknown')
    parser.add_argument('--supervision-state', default='legacy')
    parser.add_argument('--eligible-for-scheduling', choices=['true', 'false'], default='false')
    parser.add_argument('--is-primary-track', choices=['true', 'false'], default='false')
    parser.add_argument('--lifecycle', default='legacy')
    parser.add_argument('--title', default='')
    args = parser.parse_args()

    task = TaskState(
        taskId=args.task_id,
        project=args.project,
        goal=args.goal,
        status=args.status,
        priority=args.priority,
        dependencies=json.loads(args.dependencies),
        override=args.override,
        latestResult=args.latest_result,
        blocker=args.blocker,
        nextStep=args.next_step,
        lastSuccess=args.last_success,
        lastFailure=args.last_failure,
        updatedAt=args.updated_at,
        kind=args.kind,
        source=args.source,
        executionMode=args.execution_mode,
        ownerContext=args.owner_context,
        supervisionState=args.supervision_state,
        eligibleForScheduling=args.eligible_for_scheduling == 'true',
        isPrimaryTrack=args.is_primary_track == 'true',
        lifecycle=args.lifecycle,
        title=args.title,
    )
    paths = RuntimePaths(Path(args.project_root))
    task_path, index_path = write_task_state(paths, task)
    print(f'OK: wrote {task_path}')
    print(f'OK: wrote {index_path}')


if __name__ == '__main__':
    main()
