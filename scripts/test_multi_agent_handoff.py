#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
script = root / 'scripts' / 'write_handoff_state.py'
out = root / 'tests' / 'MULTI_AGENT_STATE_RESULT.md'
ownership_path = root / '.agent' / 'state' / 'ownership' / 'task-phase2-demo.json'
handoff_path = root / '.agent' / 'state' / 'handoffs' / 'task-phase2-demo.json'
render_path = root / '.agent' / 'handoffs' / 'task-phase2-demo.md'

res = subprocess.run([
    'python3', str(script),
    '--task-id', 'task-phase2-demo',
    '--owner', 'ceo',
    '--executor', 'coder',
    '--reviewer', 'reviewer',
    '--from-agent', 'coder',
    '--to-agent', 'reviewer',
    '--reason', 'implementation-ready-for-review',
    '--summary', '当前任务已完成实现与基础验证，进入评审阶段。',
    '--next-action', 'review-and-accept',
    '--requires-human',
    '--notes', 'phase-f-handoff',
], capture_output=True, text=True)

issues = []
if res.returncode != 0:
    issues.append('write_handoff_state failed')
if not ownership_path.exists():
    issues.append('missing ownership state')
if not handoff_path.exists():
    issues.append('missing handoff state')
if not render_path.exists():
    issues.append('missing handoff render')

if ownership_path.exists():
    ownership = json.loads(ownership_path.read_text(encoding='utf-8'))
    if ownership.get('owner') != 'ceo':
        issues.append('owner mismatch')
    if ownership.get('executor') != 'coder':
        issues.append('executor mismatch')
    if ownership.get('reviewer') != 'reviewer':
        issues.append('reviewer mismatch')

if handoff_path.exists():
    handoff = json.loads(handoff_path.read_text(encoding='utf-8'))
    if handoff.get('fromAgent') != 'coder':
        issues.append('fromAgent mismatch')
    if handoff.get('toAgent') != 'reviewer':
        issues.append('toAgent mismatch')
    if handoff.get('linkedResumeState') == 'missing':
        issues.append('missing linkedResumeState')
    if handoff.get('linkedNextTask') == 'missing':
        issues.append('missing linkedNextTask')

lines = ['# MULTI_AGENT_STATE_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
