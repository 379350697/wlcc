"""Sidecar rendering and consistency checks for task views."""

from __future__ import annotations

import json
from pathlib import Path

from runtime.common.io import read_json
from runtime.state.render_views import render_resume_md, render_task_md, render_tasks_summary


def _load_tasks_from_state_dir(state_dir: Path) -> list[dict]:
    tasks = []
    for path in sorted(state_dir.glob("*.json")):
        tasks.append(json.loads(path.read_text(encoding="utf-8")))
    return tasks


def _load_flows_from_state_dir(state_dir: Path) -> list[dict]:
    flows = []
    if not state_dir.exists():
        return flows
    for path in sorted(state_dir.glob("*.json")):
        flows.append(json.loads(path.read_text(encoding="utf-8")))
    return flows


def render_flow_md(flow: dict, tasks: list[dict]) -> str:
    owned = [task for task in tasks if task.get("taskFlowId") == flow.get("taskFlowId")]
    task_ids = ", ".join(task.get("taskId", "") for task in owned) or "[]"
    return "\n".join(
        [
            "# Task Flow",
            "",
            f"- taskFlowId: {flow.get('taskFlowId', '')}",
            f"- ownerSessionId: {flow.get('ownerSessionId', '')}",
            f"- status: {flow.get('status', 'draft')}",
            f"- currentLeafTaskId: {flow.get('currentLeafTaskId', '')}",
            f"- openLeafCount: {flow.get('openLeafCount', 0)}",
            f"- closedLeafCount: {flow.get('closedLeafCount', 0)}",
            f"- replyMode: {flow.get('replyMode', 'restricted')}",
            f"- tasks: {task_ids}",
            "",
        ]
    )


def _write_flow_views(flow_output_dir: Path, flows: list[dict], tasks: list[dict]) -> list[Path]:
    written: list[Path] = []
    flow_output_dir.mkdir(parents=True, exist_ok=True)
    for flow in flows:
        flow_path = flow_output_dir / f"{flow['taskFlowId']}.md"
        flow_path.write_text(render_flow_md(flow, tasks), encoding="utf-8")
        written.append(flow_path)
    return written


def write_state_views(state_dir: Path, task_output_dir: Path, resume_output_dir: Path, tasks_view_path: Path) -> list[Path]:
    tasks = _load_tasks_from_state_dir(state_dir)
    flows_state_dir = state_dir.parent / "flows"
    flows = _load_flows_from_state_dir(flows_state_dir)
    written: list[Path] = []
    task_output_dir.mkdir(parents=True, exist_ok=True)
    resume_output_dir.mkdir(parents=True, exist_ok=True)
    for task in tasks:
        task_path = task_output_dir / f"{task['taskId']}.md"
        resume_path = resume_output_dir / f"{task['taskId']}-resume.md"
        task_path.write_text(render_task_md(task), encoding="utf-8")
        resume_path.write_text(render_resume_md(task), encoding="utf-8")
        written.extend([task_path, resume_path])
    flow_output_dir = task_output_dir.parent / "flows"
    written.extend(_write_flow_views(flow_output_dir, flows, tasks))
    tasks_view_path.write_text(render_tasks_summary(tasks), encoding="utf-8")
    written.append(tasks_view_path)
    return written


def render_state_views_for_root(root: Path, task_id: str | None = None) -> list[Path]:
    tasks_state_dir = root / ".agent" / "state" / "tasks"
    task_files = sorted(tasks_state_dir.glob("*.json"))
    if not task_files:
        raise SystemExit(f"missing state dir content: {tasks_state_dir}")

    tasks_dir = root / ".agent" / "tasks"
    resume_dir = root / ".agent" / "resume"
    tasks_md = root / "TASKS.md"

    if task_id is None:
        return write_state_views(tasks_state_dir, tasks_dir, resume_dir, tasks_md)

    target = tasks_state_dir / f"{task_id}.json"
    task = read_json(target, None)
    if task is None:
        raise SystemExit(f"missing task state: {target}")
    flows_state_dir = root / ".agent" / "state" / "flows"
    flows = _load_flows_from_state_dir(flows_state_dir)
    tasks_dir.mkdir(parents=True, exist_ok=True)
    resume_dir.mkdir(parents=True, exist_ok=True)
    task_md = tasks_dir / f"{task_id}.md"
    resume_md = resume_dir / f"{task_id}-resume.md"
    task_md.write_text(render_task_md(task), encoding="utf-8")
    resume_md.write_text(render_resume_md(task), encoding="utf-8")
    all_tasks = [read_json(path, {}) for path in task_files]
    flow_output_dir = root / ".agent" / "flows"
    written = [task_md, resume_md]
    if flows:
        written.extend(_write_flow_views(flow_output_dir, flows, all_tasks))
    tasks_md.write_text(render_tasks_summary(all_tasks), encoding="utf-8")
    written.append(tasks_md)
    return written


def check_state_view_consistency(root: Path) -> tuple[list[str], Path]:
    state_dir = root / ".agent" / "state" / "tasks"
    issues = []
    all_tasks = []
    for path in sorted(state_dir.glob("*.json")):
        task = read_json(path, {})
        all_tasks.append(task)
        task_id = task["taskId"]
        task_md = root / ".agent" / "tasks" / f"{task_id}.md"
        resume_md = root / ".agent" / "resume" / f"{task_id}-resume.md"

        if not task_md.exists():
            issues.append(f"{task_id}: missing task markdown view")
        else:
            text = task_md.read_text(encoding="utf-8")
            if render_task_md(task).strip() != text.strip():
                issues.append(f"{task_id}: task markdown mismatch")

        if not resume_md.exists():
            issues.append(f"{task_id}: missing resume markdown view")
        else:
            text = resume_md.read_text(encoding="utf-8")
            if render_resume_md(task).strip() != text.strip():
                issues.append(f"{task_id}: resume markdown mismatch")

    flows_state_dir = root / ".agent" / "state" / "flows"
    all_flows = _load_flows_from_state_dir(flows_state_dir)
    for flow in all_flows:
        flow_id = flow["taskFlowId"]
        flow_md = root / ".agent" / "flows" / f"{flow_id}.md"
        if not flow_md.exists():
            issues.append(f"{flow_id}: missing flow markdown view")
        else:
            text = flow_md.read_text(encoding="utf-8")
            if render_flow_md(flow, all_tasks).strip() != text.strip():
                issues.append(f"{flow_id}: flow markdown mismatch")

    tasks_view = root / "TASKS.md"
    if not tasks_view.exists():
        issues.append("TASKS.md: missing tasks summary view")
    else:
        rendered = render_tasks_summary(all_tasks).strip()
        current = tasks_view.read_text(encoding="utf-8").strip()
        if rendered != current:
            issues.append("TASKS.md: summary mismatch")

    out = root / "tests" / "STATE_VIEW_CONSISTENCY_RESULT.md"
    lines = ["# STATE_VIEW_CONSISTENCY", ""]
    if not issues:
        lines.extend(["## summary", f"- task_count: {len(all_tasks)}", f"- tasks_view_checked: {'yes' if tasks_view.exists() else 'no'}", ""])
    lines.append("## issues")
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
    else:
        lines.append("- none")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return issues, out
