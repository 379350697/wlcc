# OpenClaw Reply-Gated Task Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reply exit gate and a canonical task-flow control surface so `OpenClaw` can no longer report false progress ahead of `wlcc` closure truth.

**Architecture:** Add a small reply-governance layer in front of terminal replies and a flow store that binds one conversation session to one canonical execution flow. Reuse existing task lifecycle, completion gate, scheduler, and sidecar rendering so the new logic constrains output and ownership without replacing the current runtime core.

**Tech Stack:** Python 3, pytest, existing `runtime/` package, JSON state under `.agent/state/`, markdown sidecar views under `.agent/`

---

## File Structure

### New files

- `runtime/flow/__init__.py`
- `runtime/flow/models.py`
- `runtime/flow/store.py`
- `runtime/reply/__init__.py`
- `runtime/reply/exit_gate.py`
- `runtime/reply/presenter.py`
- `scripts/check_reply_exit.py`
- `scripts/bind_task_flow.py`
- `tests/runtime/test_reply_exit_gate.py`
- `tests/runtime/test_task_flow_store.py`
- `tests/runtime/test_task_flow_binding.py`
- `tests/runtime/test_reply_gated_flow_e2e.py`

### Existing files to modify

- `runtime/common/models.py`
- `runtime/state/store.py`
- `runtime/progress_runtime.py`
- `runtime/close_runtime.py`
- `runtime/scheduling/next_task.py`
- `runtime/supervision/core.py`
- `runtime/sidecar/tasks_view.py`
- `runtime/events/models.py`
- `runtime/events/bus.py`
- `scripts/ingest_decomposed_leaf.py`
- `scripts/progress_task_runtime.py`
- `scripts/close_task_runtime.py`
- `scripts/render_state_views.py`

## Task 1: Add the Reply Exit Gate Contract

**Files:**
- Create: `runtime/reply/__init__.py`
- Create: `runtime/reply/exit_gate.py`
- Create: `tests/runtime/test_reply_exit_gate.py`
- Modify: `runtime/close_runtime.py`
- Modify: `runtime/progress_runtime.py`

- [ ] **Step 1: Write the failing reply gate tests**

Cover:
- open leaf returns `reject-open-leaf`
- blocked leaf with blocker returns `allow-blocked-reply`
- closed leaf with required artifacts returns `allow-final-reply`
- open leaf may return `allow-status-reply` only for structured status payloads

- [ ] **Step 2: Run the failing tests**

Run: `python3 -m pytest tests/runtime/test_reply_exit_gate.py -q`
Expected: FAIL because `runtime.reply.exit_gate` does not exist yet

- [ ] **Step 3: Implement reply gate decisions**

In `runtime/reply/exit_gate.py`, define:
- a normalized reply verdict model
- gate evaluation from flow state + task state + closure artifacts
- fail-closed default when active leaf truth is missing

- [ ] **Step 4: Reuse the completion gate for final replies**

Modify `runtime/close_runtime.py` so final-reply eligibility is derived from the same artifact truth used for closure, not a looser text-based condition.

- [ ] **Step 5: Keep progress updates non-terminal**

Modify `runtime/progress_runtime.py` so progress remains telemetry and does not implicitly authorize final reply emission.

- [ ] **Step 6: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_reply_exit_gate.py tests/runtime/test_completion_gate.py tests/runtime/test_progress_transaction.py -q`
Expected: PASS

## Task 2: Add the Canonical Task-Flow Model and Store

**Files:**
- Create: `runtime/flow/__init__.py`
- Create: `runtime/flow/models.py`
- Create: `runtime/flow/store.py`
- Create: `tests/runtime/test_task_flow_store.py`
- Modify: `runtime/common/models.py`
- Modify: `runtime/state/store.py`

- [ ] **Step 1: Write the failing flow-store tests**

Cover:
- create flow record
- bind a leaf to a flow
- recompute counters from leaf states
- derive flow status from owned leaves
- persist `ownerSessionId`, `currentLeafTaskId`, and `replyMode`

- [ ] **Step 2: Run the failing tests**

Run: `python3 -m pytest tests/runtime/test_task_flow_store.py -q`
Expected: FAIL because `runtime.flow.store` does not exist yet

- [ ] **Step 3: Implement flow models**

In `runtime/flow/models.py`, define:
- `TaskFlowRecord`
- normalization helpers
- flow status derivation helpers

- [ ] **Step 4: Implement flow persistence**

In `runtime/flow/store.py`, add:
- create / load / write helpers
- task-to-flow binding helpers
- flow recomputation helpers from canonical task files

- [ ] **Step 5: Extend canonical models**

Modify `runtime/common/models.py` and `runtime/state/store.py` so leaf tasks round-trip:
- `taskFlowId`
- `ownerSessionId` when present
- flow-aware scheduling metadata

- [ ] **Step 6: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_task_flow_store.py tests/runtime/test_state_store.py tests/runtime/test_task_contract.py -q`
Expected: PASS

## Task 3: Bind Ingest, Progress, and Close to the Task Flow

**Files:**
- Create: `scripts/bind_task_flow.py`
- Create: `tests/runtime/test_task_flow_binding.py`
- Modify: `scripts/ingest_decomposed_leaf.py`
- Modify: `runtime/progress_runtime.py`
- Modify: `runtime/close_runtime.py`
- Modify: `runtime/scheduling/next_task.py`

- [ ] **Step 1: Write the failing flow-binding tests**

Cover:
- ingest creates or attaches to a flow
- progress refreshes `currentLeafTaskId` and `updatedAt`
- close recomputes `closedLeafCount`, `openLeafCount`, and `lastClosureTaskId`
- scheduler keeps focus inside the same flow while a primary leaf remains open

- [ ] **Step 2: Run the failing tests**

Run: `python3 -m pytest tests/runtime/test_task_flow_binding.py tests/runtime/test_next_task.py -q`
Expected: FAIL because flow binding is not yet integrated

- [ ] **Step 3: Bind new leaves at ingest time**

Modify `scripts/ingest_decomposed_leaf.py` so every schedulable leaf is written with a `taskFlowId` and the target flow record is created or updated in the same operation.

- [ ] **Step 4: Update progress to refresh flow ownership**

Modify `runtime/progress_runtime.py` so successful progress updates:
- refresh flow timestamps
- keep the current open leaf pinned
- emit a flow-status change event when needed

- [ ] **Step 5: Update close to release or complete the flow**

Modify `runtime/close_runtime.py` so closing a leaf:
- recomputes the flow record
- advances the next leaf inside the same flow
- marks the flow `completed` only when no runnable leaf remains

- [ ] **Step 6: Tighten scheduler semantics**

Modify `runtime/scheduling/next_task.py` so open-leaf continuation and next-leaf switching are both flow-aware and remain fail-closed when task-flow metadata is inconsistent.

- [ ] **Step 7: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_task_flow_binding.py tests/runtime/test_next_task.py tests/runtime/test_mechanized_execution_e2e.py -q`
Expected: PASS

## Task 4: Render Flow-Owned Status and Wire the Reply Checks

**Files:**
- Create: `runtime/reply/presenter.py`
- Create: `scripts/check_reply_exit.py`
- Modify: `runtime/sidecar/tasks_view.py`
- Modify: `scripts/progress_task_runtime.py`
- Modify: `scripts/close_task_runtime.py`
- Modify: `scripts/render_state_views.py`
- Modify: `runtime/supervision/core.py`

- [ ] **Step 1: Write the failing presenter / integration tests**

Cover:
- flow summary markdown renders current flow status
- reply-check script prints structured verdict JSON
- blocked flows render unblock requests instead of normal progress narrative

- [ ] **Step 2: Run the failing tests**

Run: `python3 -m pytest tests/runtime/test_reply_gated_flow_e2e.py -q`
Expected: FAIL because the presenter and reply-check path do not exist yet

- [ ] **Step 3: Implement structured reply presentation**

In `runtime/reply/presenter.py`, render:
- final reply payloads from closure truth
- blocked reply payloads from blocker truth
- status reply payloads from flow summary

- [ ] **Step 4: Add a CLI reply check**

In `scripts/check_reply_exit.py`, expose the gate as a deterministic CLI wrapper for future OpenClaw integration and local debugging.

- [ ] **Step 5: Render flow-level sidecars**

Modify `runtime/sidecar/tasks_view.py` and `scripts/render_state_views.py` so `.agent/flows/` and related flow summaries are generated alongside task-level views.

- [ ] **Step 6: Emit governance events**

Modify `runtime/supervision/core.py` and the CLI wrappers so `reply.exit.checked`, `reply.exit.allowed`, `reply.exit.rejected`, and `flow.status.changed` are emitted through the existing event bus.

- [ ] **Step 7: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_reply_gated_flow_e2e.py tests/runtime/test_supervision_core.py tests/runtime/test_events.py -q`
Expected: PASS

## Task 5: End-to-End Verification and Standard Runtime Documentation

**Files:**
- Modify: `tests/runtime/test_reply_gated_flow_e2e.py`
- Modify: `tests/runtime/test_mechanized_execution_e2e.py`
- Modify: `STANDARD_RUNTIME_BUNDLE.md`
- Modify: `scripts/verify_standard_runtime_bundle.py`

- [ ] **Step 1: Extend the end-to-end runtime test**

Cover the full sequence:
- ingest leaf into a flow
- attempt early final reply and verify rejection
- record progress in verify phase
- close leaf with artifacts
- verify final reply is now allowed
- verify next leaf selection stays in-flow

- [ ] **Step 2: Run the end-to-end failing tests**

Run: `python3 -m pytest tests/runtime/test_reply_gated_flow_e2e.py tests/runtime/test_mechanized_execution_e2e.py -q`
Expected: FAIL until all flow and reply logic is wired

- [ ] **Step 3: Update bundle verification**

Modify `scripts/verify_standard_runtime_bundle.py` and `STANDARD_RUNTIME_BUNDLE.md` so the standard bundle now asserts:
- reply exit gate present
- flow store present
- flow-level sidecars present
- reply-gated closure path verified

- [ ] **Step 4: Run full focused verification**

Run: `python3 -m pytest tests/runtime/test_reply_exit_gate.py tests/runtime/test_task_flow_store.py tests/runtime/test_task_flow_binding.py tests/runtime/test_reply_gated_flow_e2e.py tests/runtime/test_mechanized_execution_e2e.py tests/runtime/test_next_task.py tests/runtime/test_completion_gate.py -q`
Expected: PASS

- [ ] **Step 5: Run bundle verification**

Run: `python3 scripts/verify_standard_runtime_bundle.py`
Expected: PASS and include the reply-gated task-flow checks
