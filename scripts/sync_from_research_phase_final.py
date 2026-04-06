#!/usr/bin/env python3
from pathlib import Path
import shutil

research = Path('/root/.openclaw/projects/shared/research-claude-code')
release = Path('/root/.openclaw/projects/shared/wlcc-release')
files = [
    'FINAL_PRODUCTIZATION_SUMMARY.md',
    'tests/FINAL_VALIDATION_MATRIX.md',
    'tests/LONG_CHAIN_AUTONOMY_H_FINAL_RESULT.md',
    'tests/LONG_CHAIN_AUTONOMY_G_FINAL_RESULT.md',
    'tests/LONG_CHAIN_AUTONOMY_F_FINAL_RESULT.md',
    'tests/LONG_CHAIN_AUTONOMY_E_LINE_FINAL_RESULT.md',
    'tests/LONG_CHAIN_AUTONOMY_E_FINAL_RESULT.md',
    'tests/LONG_CHAIN_AUTONOMY_D_FINAL_RESULT.md',
    'tests/LONG_CHAIN_AUTONOMY_C3_FINAL_RESULT.md',
    'tests/LONG_CHAIN_AUTONOMY_B3_FINAL_RESULT.md',
    'tests/LOCAL_SKILL_RELEASE_CONSISTENCY_RESULT.md',
    'tests/MULTI_AGENT_INHERITANCE_RESULT.md',
    'tests/MULTI_AGENT_STATE_RESULT.md',
    'tests/RESUME_CONFLICT_RESOLUTION_RESULT.md',
    'tests/RESUME_LOOP_LINK_RESULT.md',
    'tests/OBSERVABILITY_DASHBOARD_TEST_RESULT.md',
    'tests/HEARTBEAT_SUMMARY_TEST_RESULT.md',
    'tests/HEARTBEAT_SUMMARY_RESULT.md',
    'tests/RETRY_REORDER_TEST_RESULT.md',
    'LONG_CHAIN_AUTONOMY_FINAL_PRODUCT_TASKS.md',
    'MULTI_AGENT_HANDOFF_SCHEMA.md',
    'STATE_AND_RESUME_SCHEMA.md',
    'HEARTBEAT_SCHEMA.md',
    'RETRY_REORDER_SCHEMA.md',
    'scripts/check_local_skill_release_consistency.py',
    'scripts/build_heartbeat_summary.py',
    'scripts/test_heartbeat_summary.py',
    'scripts/build_observability_dashboard.py',
    'scripts/test_observability_dashboard.py',
    'scripts/build_resume_state.py',
    'scripts/test_resume_conflict_resolution.py',
    'scripts/test_resume_loop_link.py',
    'scripts/write_handoff_state.py',
    'scripts/test_multi_agent_handoff.py',
    'scripts/test_multi_agent_inheritance.py',
    'scripts/evaluate_retry_reorder.py',
    'scripts/test_retry_reorder.py',
    'scripts/emit_heartbeat.py',
    'scripts/resume_task.py',
    'scripts/resume_many_tasks.py'
]

for rel in files:
    src = research / rel
    dst = release / rel
    if not src.exists():
        print(f'SKIP missing {rel}')
        continue
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f'copied {rel}')
