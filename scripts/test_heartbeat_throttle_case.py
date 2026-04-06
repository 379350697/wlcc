#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'HEARTBEAT_THROTTLE_CASE_RESULT.md'
issues = []

latest = root / '.agent' / 'heartbeat' / 'latest-heartbeat.json'
history = root / '.agent' / 'heartbeat' / 'heartbeat-history.json'

before = 0
if history.exists():
    before = len(json.loads(history.read_text(encoding='utf-8')))

args = ['python3', str(root / 'scripts' / 'emit_heartbeat.py'), '--stage', 'demo-throttle', '--current-task', 'demo-long-chain-autonomy', '--next-step', 'same-step', '--trigger-reason', 'periodic-step', '--risk-or-blocker', 'none', '--throttle-seconds', '9999']
res1 = subprocess.run(args, capture_output=True, text=True)
res2 = subprocess.run(args, capture_output=True, text=True)
if res1.returncode != 0 or res2.returncode != 0:
    issues.append('heartbeat emit failed')

if history.exists():
    after = len(json.loads(history.read_text(encoding='utf-8')))
    if after - before != 1:
        issues.append('heartbeat throttle did not dedupe duplicate emits')
else:
    issues.append('heartbeat history missing')

if latest.exists():
    data = json.loads(latest.read_text(encoding='utf-8'))
    if data.get('throttled') is not True:
        issues.append('latest heartbeat not marked throttled after duplicate')
else:
    issues.append('latest heartbeat missing')

lines = ['# HEARTBEAT_THROTTLE_CASE_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
