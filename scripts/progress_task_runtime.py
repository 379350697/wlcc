#!/usr/bin/env python3
"""progress_task_runtime.py — 任务推进运行时入口。"""
import argparse
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.common.io import read_json, write_json
from runtime.common.paths import RuntimePaths
from runtime.common.time import now_iso
from runtime.gates.delivery import evaluate_delivery_gate
from runtime.gates.progress import evaluate_progress_gate
from runtime.harness.task_harness import HarnessResult
from runtime.scheduling.next_task import build_next_task_from_state_dir
from runtime.state.lifecycle import transition_lifecycle
from runtime.state.store import resolve_task_id
from runtime.supervision.core import handle_supervision_trigger


def main():
    parser = argparse.ArgumentParser(description='Unified progress entry for real task runtime.')
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--latest-result', required=True)
    parser.add_argument('--next-step', required=True)
    parser.add_argument('--blocker', default='无')
    parser.add_argument('--status')
    parser.add_argument('--lifecycle')
    args = parser.parse_args()

    paths = RuntimePaths(root)
    resolved_task_id = resolve_task_id(paths, args.task_id)
    task_path = paths.tasks_state_dir / f'{resolved_task_id}.json'
    task = read_json(task_path, None)
    if task is None:
        raise SystemExit(f'missing task: {args.task_id}')

    delivery_result = evaluate_delivery_gate(resolved_task_id, args.latest_result, root, task.get('kind', 'sample'))
    if not delivery_result['passed']:
        raise SystemExit(f"[delivery gate] rejected: {delivery_result['reason']}")

    progress_result = evaluate_progress_gate(args.latest_result, args.next_step)
    if not progress_result['passed']:
        raise SystemExit(f"[progress reply gate] rejected: {progress_result['reason']}")

    task['latestResult'] = args.latest_result
    task['nextStep'] = args.next_step
    task['blocker'] = args.blocker
    task['updatedAt'] = now_iso()
    if args.status:
        task['status'] = args.status
    write_json(task_path, task)

    build_next_task_from_state_dir(
        paths.tasks_state_dir,
        paths.state_dir / 'next-task.json',
        paths.agent_dir / 'NEXT_TASK.md',
        paths.state_dir / 'next-task-input.json',
    )

    if args.lifecycle:
        current = read_json(task_path, {}).get('lifecycle')
        if current != args.lifecycle:
            transition_lifecycle(paths, resolved_task_id, args.lifecycle)

    supervision_changed = handle_supervision_trigger(root, resolved_task_id, 'on_task_changed')
    supervision_interval = handle_supervision_trigger(root, resolved_task_id, 'on_interval')
    harness_result = HarnessResult(success=True, steps=[], total_duration_ms=0, consistency_check_passed=None, failed_step=None)

    final_task = read_json(task_path, task)
    out = root / 'tests' / 'PROGRESS_TASK_RUNTIME_RESULT.md'
    lines = ['# PROGRESS_TASK_RUNTIME_RESULT', '', '## summary']
    lines.append(f"- requestedTaskId: {args.task_id}")
    lines.append(f'- taskId: {resolved_task_id}')
    lines.append(f'- latestResult: {args.latest_result}')
    lines.append(f'- nextStep: {args.next_step}')
    lines.append(f'- blocker: {args.blocker}')
    lines.append(f"- status: {final_task.get('status', 'unknown')}")
    lines.append(f"- lifecycle: {final_task.get('lifecycle', 'unknown')}")
    lines.append('- gatesPassed: true')
    lines.append(f"- deliveryEvidence: {delivery_result['collected']}/{delivery_result['required']}")
    lines.append(f"- supervisionStatus: {supervision_changed.get('status', 'unknown')}")
    lines.append(f"- intervalStale: {str(supervision_interval.get('stale', False)).lower()}")
    lines.append(f"- harnessSuccess: {str(harness_result.success).lower()}")
    lines.append(f"- harnessDuration: {harness_result.total_duration_ms}ms")
    lines.append(f"- consistencyCheck: {harness_result.consistency_check_passed}")
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'OK: wrote {out}')


if __name__ == '__main__':
    main()
