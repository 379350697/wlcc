#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
emit = root / 'scripts' / 'emit_heartbeat.py'
summary = root / 'scripts' / 'build_heartbeat_summary.py'
history = root / '.agent' / 'heartbeat' / 'heartbeat-history.json'
latest = root / '.agent' / 'heartbeat' / 'latest-heartbeat.json'
summary_json = root / '.agent' / 'heartbeat' / 'heartbeat-summary.json'
summary_md = root / 'tests' / 'HEARTBEAT_SUMMARY_RESULT.md'
out = root / 'tests' / 'HEARTBEAT_SUMMARY_TEST_RESULT.md'

if history.exists():
    history.unlink()
if latest.exists():
    latest.unlink()
if summary_json.exists():
    summary_json.unlink()

cases = [
    ['--stage', 'phase-e', '--current-task', 'task-phase2-demo', '--next-step', 'continue-loop', '--trigger-reason', 'periodic-step', '--risk-or-blocker', 'none', '--throttle-seconds', '0'],
    ['--stage', 'phase-e', '--current-task', 'task-phase2-demo', '--next-step', 'wait-human', '--trigger-reason', 'degraded-continue', '--risk-or-blocker', 'retrieval_priority', '--requires-human', '--throttle-seconds', '0'],
    ['--stage', 'phase-e', '--current-task', 'task-bulk-a', '--next-step', 'report-stage-complete', '--trigger-reason', 'stage-complete-stop', '--risk-or-blocker', 'current stage boundary reached', '--requires-human', '--throttle-seconds', '0'],
]
issues = []
for args in cases:
    res = subprocess.run(['python3', str(emit), *args], capture_output=True, text=True)
    if res.returncode != 0:
        issues.append('emit failed')

res = subprocess.run(['python3', str(summary)], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('summary build failed')

if not summary_json.exists():
    issues.append('missing heartbeat-summary.json')
else:
    data = json.loads(summary_json.read_text(encoding='utf-8'))
    if data.get('historyCount') != 3:
        issues.append('historyCount mismatch')
    if not data.get('dailySummary'):
        issues.append('missing dailySummary')
    if not data.get('stageSummary'):
        issues.append('missing stageSummary')
    if len(data.get('anomalyHeartbeats', [])) < 2:
        issues.append('missing anomalyHeartbeats aggregation')
    latest_data = data.get('latest', {})
    if latest_data.get('triggerReason') != 'stage-complete-stop':
        issues.append('unexpected latest triggerReason')

if not summary_md.exists():
    issues.append('missing HEARTBEAT_SUMMARY_RESULT.md')

lines = ['# HEARTBEAT_SUMMARY_TEST_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
