#!/usr/bin/env python3
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'REAL_TASK_VIEWS_CLOSURE_RESULT.md'
issues = []

for script in [
    'test_real_task_scope_views.py',
    'test_real_task_audit_summary.py',
    'test_real_task_context_isolation.py',
]:
    res = subprocess.run(['python3', str(root / 'scripts' / script)], capture_output=True, text=True)
    if res.returncode != 0:
        issues.append(f'{script} failed')

lines = ['# REAL_TASK_VIEWS_CLOSURE_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
