#!/usr/bin/env python3
from pathlib import Path
import shutil

research = Path('/root/.openclaw/projects/shared/research-claude-code/.agent')
release = Path('/root/.openclaw/projects/shared/wlcc-release/.agent')
items = [
    'loop-config.json',
    'NEXT_TASK.md',
    'STATE_UPDATE_FLOW.md',
    'state/index.json',
    'state/next-task-input.json',
    'state/next-task.json',
    'state/bulk-resume-state.json',
    'state/multi-agent-policy.json',
    'state/task-phase2-demo-resume-state.json',
    'state/tasks/task-bulk-a.json',
    'state/tasks/task-bulk-b.json',
    'state/tasks/task-phase2-demo.json',
    'state/tasks/task-phase2-e2e-bulk-a.json',
    'state/tasks/task-phase2-e2e-bulk-b.json',
    'state/tasks/task-phase2-e2e-single.json',
    'state/tasks/task-phase2-link-demo.json',
    'state/tasks/task-phase2-render-link.json',
    'state/tasks/task-phase2-v2-link.json',
    'state/handoffs/task-phase2-demo.json',
    'state/ownership/task-phase2-demo.json',
    'tasks/task-bulk-a.md',
    'tasks/task-bulk-b.md',
    'tasks/task-phase2-demo.md',
    'tasks/task-phase2-e2e-bulk-a.md',
    'tasks/task-phase2-e2e-bulk-b.md',
    'tasks/task-phase2-e2e-single.md',
    'tasks/task-phase2-link-demo.md',
    'tasks/task-phase2-render-link.md',
    'tasks/task-phase2-v2-link.md',
    'resume/task-bulk-a-resume.md',
    'resume/task-bulk-b-resume.md',
    'resume/task-phase2-demo-resume.md',
    'resume/task-phase2-e2e-bulk-a-resume.md',
    'resume/task-phase2-e2e-bulk-b-resume.md',
    'resume/task-phase2-e2e-single-resume.md',
    'resume/task-phase2-link-demo-resume.md',
    'resume/task-phase2-render-link-resume.md',
    'resume/task-phase2-v2-link-resume.md',
    'loop/check-summary.json',
    'loop/last-run.json',
    'loop/retry-policy.json',
    'loop/retry-state.json',
    'loop/failure-control.json',
    'loop/risk-escalation.json',
    'loop/stop-condition.json',
    'heartbeat/latest-heartbeat.json',
    'heartbeat/heartbeat-history.json',
    'heartbeat/heartbeat-summary.json',
    'handoffs/task-phase2-demo.md',
    'audit/EVENT_OVERVIEW.md',
    'audit/AUDIT_SUMMARY.md',
    'audit/OBSERVABILITY_DASHBOARD.md',
    'audit/observability-dashboard.json',
    'logs/EVENT_LOG.md',
    'logs/CHANGELOG.md',
    'logs/FAILURE_LOG.md',
    'logs/HEALTHCHECK_LOG.md'
]

for rel in items:
    src = research / rel
    dst = release / rel
    if not src.exists():
        print(f'SKIP missing {rel}')
        continue
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f'copied {rel}')
