#!/usr/bin/env python3
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'tests' / 'DEMO_COMPLETENESS_PACK_RESULT.md'
scripts = [
    'test_demo_extreme_cases.py',
    'test_invalid_and_override_cases.py',
    'test_handoff_resume_crosscheck.py',
    'test_heartbeat_throttle_case.py',
    'test_state_corruption_cases.py',
    'test_conflict_and_batch_cases.py',
    'test_empty_dirty_observability_cases.py',
    'test_deadloop_and_rollback_cases.py',
    'test_missing_dirty_field_cases.py',
    'test_resume_state_conflict_cases.py',
    'test_ownership_and_dirty_event_cases.py',
]
issues = []
lines = ['# DEMO_COMPLETENESS_PACK_RESULT', '']
for name in scripts:
    res = subprocess.run(['python3', str(root / 'scripts' / name)], capture_output=True, text=True)
    ok = res.returncode == 0
    lines.append(f'- {name}: {'PASS' if ok else 'FAIL'}')
    if not ok:
        issues.append(name)
lines.append('')
lines.append('## Overall')
if issues:
    lines.append('- FAIL: ' + ', '.join(issues))
    code = 1
else:
    lines.append('- PASS')
    code = 0
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
