#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.common.io import read_json, write_json
from runtime.common.models import TaskState
from runtime.common.paths import RuntimePaths
from runtime.common.time import now_iso
from runtime.contracts.task_contract import validate_contract_dict
from runtime.decomposition.judge import judge_leaf_bundle
from runtime.decomposition.models import LeafBundle
from runtime.resume.service import write_resume_output
from runtime.scheduling.next_task import build_next_task_from_state_dir, write_state_views
from runtime.state.lifecycle import transition_lifecycle
from runtime.state.store import write_task_state


def main():
    parser = argparse.ArgumentParser(description="Ingest a decomposed ready leaf into wlcc canonical state.")
    parser.add_argument("--payload-file", required=True)
    parser.add_argument("--project-root", default=str(root))
    args = parser.parse_args()

    project_root = Path(args.project_root)
    payload = read_json(Path(args.payload_file), None)
    if not isinstance(payload, dict):
        raise SystemExit("invalid payload file")

    leaf = LeafBundle.from_dict(payload)
    if leaf.status != "ready":
        raise SystemExit("only ready leaf bundles may be ingested")
    if not leaf.parentTaskId:
        raise SystemExit("parentTaskId is required for decomposed leaf ingest")

    contract_verdict = validate_contract_dict(leaf.to_task_contract())
    if not contract_verdict.passed:
        raise SystemExit(f"incomplete ready leaf contract: {contract_verdict.reason}")

    judge_verdict = judge_leaf_bundle(leaf)
    if not judge_verdict.passed:
        raise SystemExit(f"ready leaf failed ingest judge: {judge_verdict.reason}")

    paths = RuntimePaths(project_root)
    updated_at = now_iso()
    task = TaskState(
        taskId=leaf.taskId,
        project=project_root.name,
        goal=leaf.goal,
        status="ready",
        priority=leaf.priority,
        dependencies=[],
        override="none",
        latestResult="decomposed leaf ingested into wlcc.",
        blocker="无",
        nextStep="ready leaf 已接入 runtime，等待正式执行。",
        lastSuccess="decomposed leaf ingest completed.",
        lastFailure="无",
        updatedAt=updated_at,
        kind="real",
        source="openclaw-decomposition",
        executionMode="live",
        ownerContext="openclaw",
        supervisionState="ingested",
        eligibleForScheduling=True,
        isPrimaryTrack=True,
        lifecycle="ingested",
        title=leaf.goal,
        taskLevel="leaf",
        parentTaskId=leaf.parentTaskId,
        phase="analyze",
        doneWhen=leaf.doneWhen,
        requiredEvidence=leaf.requiredEvidence,
        requiredTests=leaf.requiredTests,
        allowedPaths=leaf.allowedPaths,
        forbiddenPaths=[],
        maxTurns=8,
        maxMinutes=20,
        turnCount=0,
        riskLevel=leaf.riskLevel,
        estimatedTurns=leaf.estimatedTurns,
        estimatedMinutes=leaf.estimatedMinutes,
        splitConfidence=leaf.splitConfidence,
    )
    task_path, index_path = write_task_state(paths, task)

    supervision_path = paths.supervision_state_dir / f"{leaf.taskId}.json"
    write_json(
        supervision_path,
        {
            "taskId": leaf.taskId,
            "status": "ingested",
            "lastHeartbeatAt": None,
            "lastResumeAt": None,
            "lastHandoffAt": None,
            "stale": False,
            "updatedAt": updated_at,
        },
    )

    build_next_task_from_state_dir(
        paths.tasks_state_dir,
        paths.state_dir / "next-task.json",
        paths.agent_dir / "NEXT_TASK.md",
        paths.state_dir / "next-task-input.json",
    )
    write_state_views(paths.tasks_state_dir, paths.agent_dir / "tasks", paths.agent_dir / "resume", project_root / "TASKS.md")
    write_resume_output(project_root, leaf.taskId)
    transition_lifecycle(paths, leaf.taskId, "ready")

    out = project_root / "tests" / "INGEST_DECOMPOSED_LEAF_RESULT.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "\n".join(
            [
                "# INGEST_DECOMPOSED_LEAF_RESULT",
                "",
                "## summary",
                f"- taskId: {leaf.taskId}",
                f"- taskStatePath: {task_path}",
                f"- indexPath: {index_path}",
                f"- parentTaskId: {leaf.parentTaskId}",
                "- status: ready",
                "- lifecycle: ready",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"OK: taskId {leaf.taskId}")
    print(f"OK: wrote {task_path}")
    print(f"OK: wrote {index_path}")
    print(f"OK: wrote {out}")


if __name__ == "__main__":
    main()
