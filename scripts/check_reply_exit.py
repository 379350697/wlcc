#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.common.io import read_json, write_json
from runtime.common.paths import RuntimePaths
from runtime.events.bus import publish_runtime_event
from runtime.flow.store import load_task_flow
from runtime.reply.exit_gate import evaluate_reply_exit_gate
from runtime.state.store import load_task_state


def main():
    parser = argparse.ArgumentParser(description="Check whether a reply may exit the runtime.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--reply-kind", required=True, choices=["final", "blocked", "status"])
    parser.add_argument("--structured", action="store_true")
    parser.add_argument("--requested-input")
    args = parser.parse_args()

    project_root = Path(args.project_root)
    paths = RuntimePaths(project_root)
    task = load_task_state(paths, args.task_id)
    flow = None
    task_flow_id = str(task.get("taskFlowId", "") or "")
    if task_flow_id:
        try:
            flow = load_task_flow(paths, task_flow_id)
        except SystemExit:
            flow = None

    verdict = evaluate_reply_exit_gate(
        task=task,
        flow=flow,
        payload={
            "replyKind": args.reply_kind,
            "structured": args.structured,
            "requestedInput": args.requested_input,
        },
    )

    publish_runtime_event(
        "reply.exit.checked",
        str(task.get("taskId", args.task_id)),
        "reply",
        {
            "decision": verdict["decision"],
            "allowed": verdict["allowed"],
            "replyKind": args.reply_kind,
        },
    )
    publish_runtime_event(
        "reply.exit.allowed" if verdict["allowed"] else "reply.exit.rejected",
        str(task.get("taskId", args.task_id)),
        "reply",
        {
            "decision": verdict["decision"],
            "reason": verdict["reason"],
            "replyKind": args.reply_kind,
        },
    )

    output_id = task_flow_id or str(task.get("taskId", args.task_id))
    output_path = paths.state_dir / "reply-gate" / f"{output_id}.json"
    write_json(output_path, verdict)
    print(json.dumps(verdict, ensure_ascii=False))

    if not verdict["allowed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
