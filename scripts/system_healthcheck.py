#!/usr/bin/env python3
from pathlib import Path
import subprocess

root = Path('/root/.openclaw/projects/shared/research-claude-code')
results = []

# 1. layered read
read_cmd = ['python3', str(root / 'scripts' / 'read_project_context.py'), '--project-root', str(root), '--task-id', 'task-001']
read_res = subprocess.run(read_cmd, capture_output=True, text=True)
results.append(('layered_read', read_res.returncode == 0))

# 2. risk check
risk_cmd = ['python3', str(root / 'scripts' / 'check_risk_level.py'), '--action', 'write-state']
risk_res = subprocess.run(risk_cmd, capture_output=True, text=True)
results.append(('risk_check', risk_res.returncode == 0 and risk_res.stdout.strip() == 'L1'))

# 3. audit summary exists
summary_path = root / '.agent' / 'audit' / 'AUDIT_SUMMARY.md'
results.append(('audit_summary', summary_path.exists()))

out = ['# SYSTEM_HEALTHCHECK', '']
for name, ok in results:
    out.append(f'- {name}: {"PASS" if ok else "FAIL"}')

status = 'PASS' if all(ok for _, ok in results) else 'FAIL'
out.append('')
out.append(f'## Overall\n- {status}')

(root / 'tests' / 'SYSTEM_HEALTHCHECK_RESULT.md').write_text('\n'.join(out) + '\n', encoding='utf-8')
print(status)
