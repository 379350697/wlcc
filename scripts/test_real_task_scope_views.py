#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'REAL_TASK_SCOPE_VIEWS_RESULT.md'
issues = []

# refresh handoff/supervision for real mainline task
subprocess.run([
    'python3', str(root / 'scripts' / 'write_handoff_state.py'),
    '--task-id', 'real-task-runtime-mainline',
    '--owner', 'ceo',
    '--executor', 'coder',
    '--reviewer', 'reviewer',
    '--from-agent', 'coder',
    '--to-agent', 'reviewer',
    '--reason', 'scope-view-check',
    '--summary', '验证 handoff / ownership / supervision 是否显式区分 real task。',
    '--next-action', 'review-scope-view',
    '--requires-human',
], capture_output=True, text=True)
subprocess.run([
    'python3', str(root / 'scripts' / 'run_task_supervision.py'),
    '--task-id', 'real-task-runtime-mainline',
    '--trigger', 'on_task_changed',
], capture_output=True, text=True)
subprocess.run(['python3', str(root / 'scripts' / 'build_observability_dashboard.py')], capture_output=True, text=True)

ownership = root / '.agent' / 'state' / 'ownership' / 'real-task-runtime-mainline.json'
handoff = root / '.agent' / 'state' / 'handoffs' / 'real-task-runtime-mainline.json'
supervision = root / '.agent' / 'state' / 'supervision' / 'real-task-runtime-mainline.json'
dashboard = root / '.agent' / 'audit' / 'OBSERVABILITY_DASHBOARD.md'

if ownership.exists():
    data = json.loads(ownership.read_text(encoding='utf-8'))
    if data.get('taskKind') != 'real':
        issues.append('ownership missing taskKind=real')
else:
    issues.append('missing ownership state')

if handoff.exists():
    data = json.loads(handoff.read_text(encoding='utf-8'))
    if data.get('taskKind') != 'real':
        issues.append('handoff missing taskKind=real')
else:
    issues.append('missing handoff state')

if supervision.exists():
    data = json.loads(supervision.read_text(encoding='utf-8'))
    if data.get('taskKind') != 'real':
        issues.append('supervision missing taskKind=real')
    if data.get('scope') != 'real-task-first':
        issues.append('supervision missing real-task-first scope')
else:
    issues.append('missing supervision state')

if dashboard.exists():
    text = dashboard.read_text(encoding='utf-8')
    if 'defaultScope: real-task-first' not in text:
        issues.append('dashboard missing real-task-first scope')
else:
    issues.append('missing observability dashboard')

lines = ['# REAL_TASK_SCOPE_VIEWS_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
