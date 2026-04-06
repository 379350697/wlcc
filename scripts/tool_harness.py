#!/usr/bin/env python3
"""Compatibility wrapper for runtime TaskHarness."""
import argparse
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.harness.task_harness import HarnessResult, TaskHarness, TrackedStep

__all__ = ['HarnessResult', 'TaskHarness', 'TrackedStep']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool Harness CLI — 用于调试和测试。')
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--project-root', default='.')
    parser.add_argument('--steps', required=True, help='JSON 格式的步骤列表，如 [["render_state_views","--task-id","T001"],["build_next_task_from_state"]]')
    parser.add_argument('--no-consistency-check', action='store_true')
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    harness = TaskHarness(task_id=args.task_id, project_root=project_root, enable_consistency_check=not args.no_consistency_check)
    steps = json.loads(args.steps)
    for step in steps:
        script = step[0]
        step_args = step[1:] if len(step) > 1 else []
        harness.add(script, step_args)
    result = harness.execute_all()
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    raise SystemExit(0 if result.success else 1)
