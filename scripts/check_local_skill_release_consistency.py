#!/usr/bin/env python3
import json
from pathlib import Path

research = Path(__file__).resolve().parent.parent
local = Path('/root/.openclaw/workspace-coder/local-agent-system')
release = Path(__file__).resolve().parent.parent
out = release / 'tests' / 'LOCAL_SKILL_RELEASE_CONSISTENCY_RESULT.md'

checks = []
issues = []

# G1 local system
local_required = [
    local / 'scripts' / 'write_state_store.py',
    local / 'scripts' / 'render_state_views.py',
    local / 'scripts' / 'build_next_task_from_state.py',
    local / 'scripts' / 'retrieve_context.py',
    local / 'scripts' / 'evaluate_risk_policy.py',
    local / 'tests' / 'PHASE2_MAINLINE_CHECK_RESULT.md',
]
for path in local_required:
    ok = path.exists()
    checks.append((f'local:{path.relative_to(local)}', ok))
    if not ok:
        issues.append(f'missing local file: {path.relative_to(local)}')

# G2 skills + dist
skills = ['task-extract', 'project-state', 'context-compact', 'handoff-report']
for skill in skills:
    skill_md = research / 'skills' / skill / 'SKILL.md'
    dist_skill = research / 'dist' / f'{skill}.skill'
    ok = skill_md.exists() and dist_skill.exists()
    checks.append((f'skill:{skill}', ok))
    if not ok:
        issues.append(f'missing skill package pair: {skill}')

# G3 release
release_required = [
    release / 'scripts' / 'write_state_store.py',
    release / 'scripts' / 'render_state_views.py',
    release / 'scripts' / 'build_next_task_from_state.py',
    release / 'scripts' / 'retrieve_context.py',
    release / 'scripts' / 'evaluate_risk_policy.py',
    release / 'scripts' / 'check_phase2_mainline.py',
    release / 'tests' / 'PHASE2_MAINLINE_CHECK_RESULT.md',
    release / 'RELEASE_MANIFEST.md',
]
for path in release_required:
    ok = path.exists()
    checks.append((f'release:{path.relative_to(release)}', ok))
    if not ok:
        issues.append(f'missing release file: {path.relative_to(release)}')

# Cross-consistency snapshots
local_risk = local / 'risk_policy.json'
research_risk = research / 'risk_policy.json'
release_risk = release / 'risk_policy.json'
if local_risk.exists() and research_risk.exists() and release_risk.exists():
    local_version = json.loads(local_risk.read_text(encoding='utf-8')).get('version')
    research_version = json.loads(research_risk.read_text(encoding='utf-8')).get('version')
    release_version = json.loads(release_risk.read_text(encoding='utf-8')).get('version')
    ok = research_version == release_version
    checks.append((f'cross:risk-policy-version research={research_version} release={release_version}', ok))
    if not ok:
        issues.append('research/release risk policy version mismatch')
    checks.append((f'cross:local-risk-policy-present version={local_version}', True))
else:
    issues.append('missing one of local/research/release risk_policy.json')

# Result
lines = ['# LOCAL_SKILL_RELEASE_CONSISTENCY_RESULT', '', '## checks']
for name, ok in checks:
    lines.append(f"- {name}: {'PASS' if ok else 'FAIL'}")
lines.append('')
lines.append('## Overall')
if issues:
    lines.append('- FAIL')
    lines.append('')
    lines.append('## issues')
    lines.extend(f'- {item}' for item in issues)
    code = 1
else:
    lines.append('- PASS')
    code = 0

out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'OK: wrote {out}')
raise SystemExit(code)
