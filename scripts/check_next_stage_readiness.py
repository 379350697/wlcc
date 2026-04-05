#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parent.parent
checks = {
    'delivery_completeness': root / 'tests' / 'DELIVERY_COMPLETENESS_RESULT.md',
    'system_healthcheck': root / 'tests' / 'SYSTEM_HEALTHCHECK_RESULT.md',
    'audit_summary': root / '.agent' / 'audit' / 'AUDIT_SUMMARY.md',
    'risk_gate_test': root / 'tests' / 'RISK_GATE_RESULT.md',
    'test_results': root / 'TEST_RESULTS.md',
    'final_delivery_summary': root / 'FINAL_DELIVERY_SUMMARY.md',
}

lines = ['# NEXT_STAGE_READINESS', '']
all_ok = True
for name, path in checks.items():
    ok = path.exists()
    lines.append(f'- {name}: {"PASS" if ok else "MISSING"}')
    all_ok = all_ok and ok

lines.append('')
lines.append('## Overall')
lines.append(f'- {"READY" if all_ok else "NOT_READY"}')

out = root / 'tests' / 'NEXT_STAGE_READINESS_RESULT.md'
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('READY' if all_ok else 'NOT_READY')
