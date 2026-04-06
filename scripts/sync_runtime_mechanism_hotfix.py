#!/usr/bin/env python3
from pathlib import Path
import shutil

local = Path('/root/.openclaw/workspace-coder/local-agent-system')
release = Path('/root/.openclaw/projects/shared/wlcc-release')
files = [
    'scripts/write_state_store.py',
    'scripts/decide_next_task_v2.py',
    'scripts/retrieve_context.py',
    'scripts/resume_task.py',
    'scripts/build_observability_dashboard.py',
    'scripts/write_handoff_state.py',
    'scripts/progress_task_runtime.py',
    'scripts/run_task_supervision.py',
]
for rel in files:
    src = local / rel
    dst = release / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f'copied {rel}')
