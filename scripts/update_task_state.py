#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import time
from pathlib import Path

ALLOWED_STATUS = {"todo", "doing", "blocked", "done"}


def render_task(task_id, project, goal, status, latest_result, blocker, next_step, updated_at):
    return f"""# Task State

- id: {task_id}
- project: {project}
- goal: {goal}
- status: {status}
- latestResult: {latest_result}
- blocker: {blocker}
- nextStep: {next_step}
- updatedAt: {updated_at}
"""


def render_resume(task_id, goal, last_success, last_failure, blocker, next_step, updated_at):
    return f"""# Resume State

- taskId: {task_id}
- 最后目标：{goal}
- 最后成功动作：{last_success}
- 最后失败动作：{last_failure}
- 当前阻塞：{blocker}
- 建议下一步：{next_step}
- updatedAt: {updated_at}
"""


def render_tasks_summary_entry(task_id, goal, status, blocker, next_step, latest_result):
    return f"""### {task_id}
- 目标：{goal}
- 当前状态：{status}
- 阻塞项：{blocker}
- 下一步：{next_step}
- 最近结果：{latest_result}
"""


def append_line(path: Path, line: str, header: str):
    if path.exists():
        old = path.read_text(encoding='utf-8').rstrip() + "\n"
    else:
        old = header
    path.write_text(old + line + "\n", encoding='utf-8')


def append_changelog(changelog_path: Path, line: str):
    append_line(changelog_path, line, "# CHANGELOG\n\n")


def append_failure_log(path: Path, line: str):
    append_line(path, line, "# FAILURE_LOG\n\n")


def safe_write(script_path: Path, target: Path, temp_input: Path, backup_dir: Path):
    cmd = [
        "python3",
        str(script_path),
        str(target),
        "--input",
        str(temp_input),
        "--backup-dir",
        str(backup_dir),
        "--ensure-parent",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def acquire_lock(lock_path: Path, timeout_seconds: float = 10.0, poll_interval: float = 0.1):
    deadline = time.time() + timeout_seconds
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode('utf-8'))
            os.close(fd)
            return
        except FileExistsError:
            if time.time() >= deadline:
                raise RuntimeError(f"lock timeout: {lock_path}")
            time.sleep(poll_interval)


def release_lock(lock_path: Path):
    try:
        if lock_path.exists():
            lock_path.unlink()
    except Exception:
        pass


def update_tasks_summary(tasks_md_path: Path, task_id: str, goal: str, status: str, blocker: str, next_step: str, latest_result: str):
    if tasks_md_path.exists():
        text = tasks_md_path.read_text(encoding='utf-8')
    else:
        text = "# TASKS\n\n## Active\n\n## Done\n"

    entry = render_tasks_summary_entry(task_id, goal, status, blocker, next_step, latest_result).rstrip()
    pattern = re.compile(rf"^### {re.escape(task_id)}\n(?:- .*\n)+", re.MULTILINE)
    text = pattern.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"

    target_section = "## Done" if status == "done" else "## Active"
    if target_section not in text:
        text += f"\n{target_section}\n"

    section_pattern = re.compile(rf"({re.escape(target_section)}\n)(.*?)(?=\n## |\Z)", re.DOTALL)
    match = section_pattern.search(text)
    if match:
        existing = match.group(2).strip()
        new_block = (existing + "\n\n" if existing else "") + entry + "\n"
        text = text[:match.start(2)] + new_block + text[match.end(2):]
    else:
        text += f"\n{target_section}\n\n{entry}\n"

    return text.rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Update task state, resume state, TASKS summary, and changelog in order.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--latest-result", required=True)
    parser.add_argument("--blocker", required=True)
    parser.add_argument("--next-step", required=True)
    parser.add_argument("--last-success", required=True)
    parser.add_argument("--last-failure", required=True)
    parser.add_argument("--updated-at", required=True)
    parser.add_argument("--require-max-risk", default='L1')
    args = parser.parse_args()

    root = Path(args.project_root)
    failure_log = root / '.agent' / 'logs' / 'FAILURE_LOG.md'
    risk_script = root / 'scripts' / 'check_risk_level.py'

    if args.status not in ALLOWED_STATUS:
        append_failure_log(failure_log, f"- {args.updated_at} | task={args.task_id} | invalid_status={args.status}")
        print(f"ERROR: invalid status '{args.status}', allowed={sorted(ALLOWED_STATUS)}")
        raise SystemExit(2)

    risk_check = subprocess.run(
        ['python3', str(risk_script), '--action', 'write-state', '--require-max', args.require_max_risk],
        capture_output=True,
        text=True,
    )
    if risk_check.returncode != 0:
        append_failure_log(failure_log, f"- {args.updated_at} | task={args.task_id} | risk_reject={risk_check.stdout.strip() or risk_check.stderr.strip()}")
        print(risk_check.stdout.strip() or risk_check.stderr.strip())
        raise SystemExit(risk_check.returncode)

    safe_write_script = root / "scripts" / "safe_write.py"
    backups = root / ".agent" / "backups"
    tmp_dir = root / ".agent" / "tmp"
    lock_dir = root / ".agent" / "locks"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    lock_dir.mkdir(parents=True, exist_ok=True)

    lock_path = lock_dir / f"{args.task_id}.lock"
    task_path = root / ".agent" / "tasks" / f"{args.task_id}.md"
    resume_path = root / ".agent" / "resume" / f"{args.task_id}-resume.md"
    tasks_md_path = root / "TASKS.md"
    changelog_path = root / ".agent" / "logs" / "CHANGELOG.md"

    task_tmp = tmp_dir / f"{args.task_id}.task.tmp.md"
    resume_tmp = tmp_dir / f"{args.task_id}.resume.tmp.md"
    tasks_md_tmp = tmp_dir / "TASKS.tmp.md"

    acquire_lock(lock_path)
    try:
        task_tmp.write_text(
            render_task(args.task_id, args.project, args.goal, args.status, args.latest_result, args.blocker, args.next_step, args.updated_at),
            encoding='utf-8'
        )
        resume_tmp.write_text(
            render_resume(args.task_id, args.goal, args.last_success, args.last_failure, args.blocker, args.next_step, args.updated_at),
            encoding='utf-8'
        )
        tasks_md_tmp.write_text(
            update_tasks_summary(tasks_md_path, args.task_id, args.goal, args.status, args.blocker, args.next_step, args.latest_result),
            encoding='utf-8'
        )

        safe_write(safe_write_script, task_path, task_tmp, backups)
        safe_write(safe_write_script, resume_path, resume_tmp, backups)
        safe_write(safe_write_script, tasks_md_path, tasks_md_tmp, backups)
        append_changelog(changelog_path, f"- {args.updated_at} | updated {args.task_id} | status={args.status}")
        print(f"OK: updated {args.task_id}")
    except Exception as e:
        append_failure_log(failure_log, f"- {args.updated_at} | task={args.task_id} | error={str(e)}")
        raise
    finally:
        release_lock(lock_path)


if __name__ == "__main__":
    main()
