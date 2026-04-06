#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'REAL_TASK_AUDIT_SUMMARY_RESULT.md'
issues = []

res = subprocess.run(['python3', str(root / 'scripts' / 'build_real_task_audit_summary.py')], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('build_real_task_audit_summary failed')

md = root / '.agent' / 'audit' / 'AUDIT_SUMMARY.md'
js = root / '.agent' / 'audit' / 'audit-summary.json'
if not md.exists():
    issues.append('missing AUDIT_SUMMARY.md')
else:
    text = md.read_text(encoding='utf-8')
    if 'defaultScope: real-task-first' not in text:
        issues.append('audit summary missing real-task-first scope')
if not js.exists():
    issues.append('missing audit-summary.json')
else:
    data = json.loads(js.read_text(encoding='utf-8'))
    if data.get('defaultScope') != 'real-task-first':
        issues.append('audit-summary.json missing defaultScope')

lines = ['# REAL_TASK_AUDIT_SUMMARY_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
