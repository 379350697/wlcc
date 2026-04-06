#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parent.parent
required = [
    'ARCHITECTURE_PLAN.md',
    'MIGRATION_PLAN.md',
    'ROLLBACK_PLAN.md',
    'TEST_RESULTS.md',
    'FINAL_DELIVERY_SUMMARY.md',
    'skills/task-extract/SKILL.md',
    'skills/project-state/SKILL.md',
    'skills/context-compact/SKILL.md',
    'skills/handoff-report/SKILL.md',
    'scripts/safe_write.py',
    'scripts/update_task_state.py',
    'scripts/read_project_context.py',
    'scripts/check_risk_level.py',
    'scripts/build_audit_summary.py',
    '.agent/audit/AUDIT_SUMMARY.md',
    '.agent/logs/CHANGELOG.md',
    '.agent/logs/FAILURE_LOG.md',
]

lines = ['# DELIVERY_COMPLETENESS', '']
all_ok = True
for rel in required:
    path = root / rel
    ok = path.exists()
    lines.append(f'- {rel}: {"PASS" if ok else "MISSING"}')
    all_ok = all_ok and ok

lines.append('')
lines.append('## Overall')
lines.append(f'- {"PASS" if all_ok else "FAIL"}')

out = root / 'tests' / 'DELIVERY_COMPLETENESS_RESULT.md'
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('PASS' if all_ok else 'FAIL')
