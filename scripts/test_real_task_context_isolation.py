#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'REAL_TASK_CONTEXT_ISOLATION_RESULT.md'
issues = []

# resume output should expose real task kind
res = subprocess.run(['python3', str(root / 'scripts' / 'resume_task.py'), '--project-root', str(root), '--task-id', 'real-task-runtime-mainline'], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('resume_task failed for real task isolation case')
else:
    text = (root / 'tests' / 'real-task-runtime-mainline-resume-output.md').read_text(encoding='utf-8')
    if '## runtime_meta' not in text or '"taskKind": "real"' not in text:
        issues.append('resume output missing real task runtime_meta')

# observability dashboard should declare real-task-first scope
res = subprocess.run(['python3', str(root / 'scripts' / 'build_observability_dashboard.py')], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('build_observability_dashboard failed for isolation case')
else:
    text = (root / '.agent' / 'audit' / 'OBSERVABILITY_DASHBOARD.md').read_text(encoding='utf-8')
    if 'defaultScope: real-task-first' not in text:
        issues.append('observability dashboard missing real-task-first scope declaration')

lines = ['# REAL_TASK_CONTEXT_ISOLATION_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
