#!/usr/bin/env python3
from pathlib import Path
import shutil

local = Path('/root/.openclaw/workspace-coder/local-agent-system/.agent')
release = Path('/root/.openclaw/projects/shared/wlcc-release/.agent')
items = [
    'state/tasks/real-task-runtime-mainline.json',
    'state/supervision/real-task-runtime-mainline.json',
    'state/handoffs/real-task-runtime-mainline.json',
    'state/ownership/real-task-runtime-mainline.json',
    'heartbeat/latest-heartbeat.json',
    'heartbeat/heartbeat-history.json',
    'heartbeat/heartbeat-summary.json',
    'audit/OBSERVABILITY_DASHBOARD.md',
    'audit/observability-dashboard.json',
    'audit/AUDIT_SUMMARY.md',
    'audit/audit-summary.json',
    'logs/SUPERVISOR_ACTIONS_LOG.md',
    'logs/STALLED_TASK_LOG.md',
    'logs/MISSED_HEARTBEAT_LOG.md',
    'logs/CLOSURE_NOTE.md'
]
for rel in items:
    src = local / rel
    dst = release / rel
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f'copied {rel}')
