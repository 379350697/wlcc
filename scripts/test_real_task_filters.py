#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'REAL_TASK_FILTERS_RESULT.md'
issues = []

# retrieval should expose taskKind=real for real task
res = subprocess.run(['python3', str(root / 'scripts' / 'retrieve_context.py'), '--project-root', str(root), '--task-id', 'real-task-runtime-mainline'], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('retrieve_context failed for real task filter case')
else:
    data = json.loads((root / 'tests' / 'RETRIEVE_CONTEXT_OUTPUT.json').read_text(encoding='utf-8'))
    if data.get('meta', {}).get('taskKind') != 'real':
        issues.append('retrieve_context did not expose taskKind=real')

# observability should still build with filtered real-task loop history
res = subprocess.run(['python3', str(root / 'scripts' / 'build_observability_dashboard.py')], capture_output=True, text=True)
if res.returncode != 0:
    issues.append('build_observability_dashboard failed for real filter case')
else:
    text = (root / '.agent' / 'audit' / 'OBSERVABILITY_DASHBOARD.md').read_text(encoding='utf-8')
    if '## loop_history' not in text:
        issues.append('missing loop_history section after rebuild')

lines = ['# REAL_TASK_FILTERS_RESULT', '', '## issues']
if issues:
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- none')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
