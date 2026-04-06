#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
build = root / 'scripts' / 'build_observability_dashboard.py'
json_path = root / '.agent' / 'audit' / 'observability-dashboard.json'
md_path = root / '.agent' / 'audit' / 'OBSERVABILITY_DASHBOARD.md'
out = root / 'tests' / 'OBSERVABILITY_DASHBOARD_TEST_RESULT.md'

res = subprocess.run(['python3', str(build)], capture_output=True, text=True)
issues = []
if res.returncode != 0:
    issues.append('build_observability_dashboard failed')
if not json_path.exists():
    issues.append('missing observability-dashboard.json')
if not md_path.exists():
    issues.append('missing OBSERVABILITY_DASHBOARD.md')

if json_path.exists():
    data = json.loads(json_path.read_text(encoding='utf-8'))
    for key in ['loopHistory', 'checkHistory', 'failureClusters', 'retryReorderRollbackHistory', 'systemHealthSummary']:
        if key not in data:
            issues.append(f'missing {key}')
    if 'heartbeatSummary' not in data.get('systemHealthSummary', {}):
        issues.append('missing heartbeatSummary')
    if 'systemHealthcheck' not in data.get('systemHealthSummary', {}):
        issues.append('missing systemHealthcheck')

lines = ['# OBSERVABILITY_DASHBOARD_TEST_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
