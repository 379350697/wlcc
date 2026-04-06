#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'TASK_SUPERVISION_TEST_RESULT.md'
issues = []
task_id = 'real-task-runtime-mainline' if (root / '.agent' / 'state' / 'tasks' / 'real-task-runtime-mainline.json').exists() else 'real-close-runtime-final-target'

# use current real task
for trigger in ['on_task_ingested', 'on_task_changed', 'on_interruption_detected', 'on_interval', 'on_completion']:
    res = subprocess.run([
        'python3', str(root / 'scripts' / 'run_task_supervision.py'),
        '--task-id', task_id,
        '--trigger', trigger,
    ], capture_output=True, text=True)
    if res.returncode != 0:
        issues.append(f'{trigger} failed')

supervision_path = root / '.agent' / 'state' / 'supervision' / f'{task_id}.json'
if not supervision_path.exists():
    issues.append('missing supervision state')
else:
    data = json.loads(supervision_path.read_text(encoding='utf-8'))
    if not data.get('lastHeartbeatAt'):
        issues.append('missing lastHeartbeatAt')
    if not data.get('lastResumeAt'):
        issues.append('missing lastResumeAt')
    if not data.get('lastHandoffAt'):
        issues.append('missing lastHandoffAt')

handoff_path = root / '.agent' / 'state' / 'handoffs' / f'{task_id}.json'
if not handoff_path.exists():
    issues.append('missing handoff after completion trigger')

heartbeat_summary = root / '.agent' / 'heartbeat' / 'heartbeat-summary.json'
if not heartbeat_summary.exists():
    issues.append('missing heartbeat summary after supervision')

lines = ['# TASK_SUPERVISION_TEST_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
