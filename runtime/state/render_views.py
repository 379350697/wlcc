"""Pure Markdown rendering helpers for task state views."""

from __future__ import annotations


def render_task_md(task: dict) -> str:
    return f"""# Task State

- id: {task['taskId']}
- project: {task['project']}
- goal: {task['goal']}
- status: {task['status']}
- priority: {task['priority']}
- dependencies: {', '.join(task['dependencies']) if task['dependencies'] else '[]'}
- override: {task['override']}
- latestResult: {task['latestResult']}
- blocker: {task['blocker']}
- nextStep: {task['nextStep']}
- updatedAt: {task['updatedAt']}
"""


def render_resume_md(task: dict) -> str:
    return f"""# Resume State

- taskId: {task['taskId']}
- 最后目标：{task['goal']}
- 最后成功动作：{task['lastSuccess']}
- 最后失败动作：{task['lastFailure']}
- 当前阻塞：{task['blocker']}
- 建议下一步：{task['nextStep']}
- updatedAt: {task['updatedAt']}
"""


def render_tasks_summary(tasks: list[dict]) -> str:
    active = [t for t in tasks if t["status"] != "done"]
    done = [t for t in tasks if t["status"] == "done"]
    lines = ["# TASKS", "", "## Active"]
    for task in active:
        lines.extend(
            [
                f"### {task['taskId']}",
                f"- 目标：{task['goal']}",
                f"- 当前状态：{task['status']}",
                f"- 优先级：{task['priority']}",
                f"- 阻塞项：{task['blocker']}",
                f"- 下一步：{task['nextStep']}",
                f"- 最近结果：{task['latestResult']}",
                "",
            ]
        )
    lines.append("## Done")
    for task in done:
        lines.extend(
            [
                f"### {task['taskId']}",
                f"- 目标：{task['goal']}",
                f"- 当前状态：{task['status']}",
                f"- 优先级：{task['priority']}",
                f"- 阻塞项：{task['blocker']}",
                f"- 下一步：{task['nextStep']}",
                f"- 最近结果：{task['latestResult']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
