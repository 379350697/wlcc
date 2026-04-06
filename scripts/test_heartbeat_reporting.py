#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
script = root / 'scripts' / 'emit_heartbeat.py'
res = subprocess.run([
    'python3', str(script),
    '--stage', 'demo-extreme',
    '--current-task', 'demo-long-chain-autonomy',
    '--next-step', 'wait-for-human-review',
    '--trigger-reason', 'stop-condition',
    '--requires-human',
    '--risk-or-blocker', 'stage-complete-stop',
    '--completed-items', 'demo-task-state', 'demo-resume', 'demo-handoff',
    '--throttle-seconds', '0',
], capture_output=True, text=True)

heartbeat_json = root / '.agent' / 'heartbeat' / 'latest-heartbeat.json'
heartbeat_md = root / 'tests' / 'HEARTBEAT_RESULT.md'
issues = []
if res.returncode != 0:
    issues.append('emit_heartbeat failed')
if not heartbeat_json.exists():
    issues.append('missing latest-heartbeat.json')
if not heartbeat_md.exists():
    issues.append('missing HEARTBEAT_RESULT.md')
if heartbeat_json.exists():
    data = json.loads(heartbeat_json.read_text(encoding='utf-8'))
    if data.get('triggerReason') != 'stop-condition':
        issues.append('unexpected triggerReason')
    if data.get('requiresHuman') is not True:
        issues.append('requiresHuman should be true')

lines = ['# HEARTBEAT_TEST_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out = root / 'tests' / 'HEARTBEAT_TEST_RESULT.md'
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
