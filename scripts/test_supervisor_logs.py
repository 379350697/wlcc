#!/usr/bin/env python3
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'SUPERVISOR_LOGS_RESULT.md'
issues = []

# force blocked state so interval can produce stale-related logs
subprocess.run(['python3', str(root / 'scripts' / 'update_task_lifecycle.py'), '--task-id', 'real-task-runtime-mainline', '--to', 'blocked'], capture_output=True, text=True)
for trigger in ['on_task_changed', 'on_interval', 'on_completion']:
    res = subprocess.run(['python3', str(root / 'scripts' / 'run_task_supervision.py'), '--task-id', 'real-task-runtime-mainline', '--trigger', trigger], capture_output=True, text=True)
    if res.returncode != 0:
        issues.append(f'{trigger} failed')

for rel in [
    '.agent/logs/SUPERVISOR_ACTIONS_LOG.md',
    '.agent/logs/STALLED_TASK_LOG.md',
    '.agent/logs/MISSED_HEARTBEAT_LOG.md',
]:
    path = root / rel
    if not path.exists():
        issues.append(f'missing log: {rel}')

lines = ['# SUPERVISOR_LOGS_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
