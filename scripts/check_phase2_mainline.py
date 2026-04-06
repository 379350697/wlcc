#!/usr/bin/env python3
from pathlib import Path
import subprocess


root = Path(__file__).resolve().parent.parent

render_views = root / 'scripts' / 'render_state_views.py'
if render_views.exists():
    subprocess.run(['python3', str(render_views), '--project-root', str(root)], capture_output=True, text=True)

consistency = root / 'scripts' / 'check_state_view_consistency.py'
if consistency.exists():
    subprocess.run(['python3', str(consistency)], capture_output=True, text=True)

checks = {
    'canonical_state_task': root / '.agent' / 'state' / 'tasks' / 'task-001.json',
    'state_index': root / '.agent' / 'state' / 'index.json',
    'next_task_v2_state': root / '.agent' / 'state' / 'next-task.json',
    'next_task_view': root / '.agent' / 'NEXT_TASK.md',
    'next_task_consistency': root / 'tests' / 'NEXT_TASK_CONSISTENCY_RESULT.md',
    'task_view': root / '.agent' / 'tasks' / 'task-001.md',
    'resume_view': root / '.agent' / 'resume' / 'task-001-resume.md',
    'tasks_view': root / 'TASKS.md',
    'state_view_consistency': root / 'tests' / 'STATE_VIEW_CONSISTENCY_RESULT.md',
    'risk_policy_script': root / 'scripts' / 'evaluate_risk_policy.py',
    'risk_gate_script': root / 'scripts' / 'check_risk_level.py',
    'risk_policy_consistency': root / 'tests' / 'RISK_POLICY_CONSISTENCY_RESULT.md',
    'retrieve_context_script': root / 'scripts' / 'retrieve_context.py',
    'read_context_entry': root / 'scripts' / 'read_project_context.py',
    'retrieval_priority_check': root / 'tests' / 'RETRIEVAL_PRIORITY_CHECK_RESULT.md',
}

content_assertions = {
    'next_task_consistency': [
        '## summary',
        '- decisionType: continue-current',
        '## issues',
        '- none',
    ],
    'state_view_consistency': [
        '## summary',
        '- tasks_view_checked: yes',
        '## issues',
        '- none',
    ],
    'risk_policy_consistency': [
        '## summary',
        '- policy_version: phase2-v2',
        '- matrix_artifact: yes',
        '- granularity_artifact: yes',
        '## issues',
        '- none',
    ],
    'retrieval_priority_check': [
        '## summary',
        '- canonical_task_before_markdown: yes',
        '- canonical_next_before_markdown: yes',
        '- degraded_fallback: false',
        '## issues',
        '- none',
    ],
}

extra_result_checks = {
    'risk_policy_matrix': {
        'path': root / 'tests' / 'RISK_POLICY_MATRIX_RESULT.md',
        'contains': [
            '## Overall\n- PASS',
            '## write-state-project',
            '- result: PASS',
            '## delete-state-approved-confirmed',
        ],
    },
    'risk_policy_granularity': {
        'path': root / 'tests' / 'RISK_POLICY_GRANULARITY_RESULT.md',
        'contains': [
            '## Overall\n- PASS',
            '## canonical-state-write-needs-confirmation',
            'decision: require-confirmation',
            '## release-script-modify-approved',
            '## destructive-delete-state-unapproved',
        ],
    },
}

lines = ['# PHASE2_MAINLINE_CHECK', '']
missing = []
failed = []

for name, path in checks.items():
    if not path.exists():
        lines.append(f'- {name}: MISSING')
        missing.append(name)
        continue

    expected_tokens = content_assertions.get(name)
    if expected_tokens:
        text = path.read_text(encoding='utf-8')
        missing_tokens = [token for token in expected_tokens if token not in text]
        if missing_tokens:
            lines.append(f'- {name}: FAIL')
            failed.append(f"{name}: missing tokens -> {' | '.join(missing_tokens)}")
            continue

    lines.append(f'- {name}: PASS')

for name, spec in extra_result_checks.items():
    path = spec['path']
    if not path.exists():
        lines.append(f'- {name}: MISSING')
        missing.append(name)
        continue

    text = path.read_text(encoding='utf-8')
    missing_tokens = [token for token in spec['contains'] if token not in text]
    if missing_tokens:
        lines.append(f'- {name}: FAIL')
        failed.append(f"{name}: missing tokens -> {' | '.join(missing_tokens)}")
        continue

    lines.append(f'- {name}: PASS')

lines.append('')
lines.append('## Overall')
if missing or failed:
    parts = []
    if missing:
        parts.append('missing=' + ', '.join(missing))
    if failed:
        parts.append('failed=' + ', '.join(failed))
    lines.append('- FAIL: ' + ' | '.join(parts))
    code = 1
else:
    lines.append('- PASS')
    code = 0

out = root / 'tests' / 'PHASE2_MAINLINE_CHECK_RESULT.md'
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
