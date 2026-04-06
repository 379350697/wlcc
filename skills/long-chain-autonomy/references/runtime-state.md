# Runtime State

## Core state sources
- `.agent/state/tasks/*.json`
- `.agent/state/*resume-state.json`
- `.agent/state/handoffs/*.json`
- `.agent/state/next-task.json`

## Rendered views
- `.agent/tasks/*.md`
- `.agent/resume/*.md`
- `.agent/NEXT_TASK.md`
- `TASKS.md`

## Read priority
1. canonical state json
2. resume state / handoff state
3. rendered markdown views
4. project fact files
5. summaries
6. chat

## Runtime scripts
- `scripts/write_state_store.py`
- `scripts/render_state_views.py`
- `scripts/build_next_task_from_state.py`
- `scripts/retrieve_context.py`
- `scripts/resume_task.py`
- `scripts/resume_many_tasks.py`
