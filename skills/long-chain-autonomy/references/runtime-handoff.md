# Runtime Handoff

## Ownership
- `.agent/state/ownership/<task-id>.json`
- owner / executor / reviewer

## Handoff
- `.agent/state/handoffs/<task-id>.json`
- `.agent/handoffs/<task-id>.md`

## Inheritance
- `.agent/state/multi-agent-policy.json`
- shared canonical state
- shared next-task semantics
- shared stop / heartbeat / risk semantics
- handoff-state-first resume

## Scripts
- `scripts/write_handoff_state.py`
- `scripts/build_resume_state.py`
