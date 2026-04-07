# OpenClaw Reply-Gated Task Flow Spec

Date: 2026-04-07
Scope: `OpenClaw` conversation entry + `wlcc` execution ownership
Priority: Stop false-progress replies first, then make task flow the session control surface

## 1. Goal

Build the first production-grade bridge between `OpenClaw` chat turns and `wlcc` task execution by implementing:

- `Enhancement A`: a reply exit gate that prevents ordinary replies while the active leaf is still open
- `Enhancement B`: a task-flow control surface that binds the conversation thread to one canonical execution flow

The target outcome is:

`chat may observe execution, but chat may not bypass execution truth`

## 2. Problem Statement

`wlcc` already has meaningful execution primitives:

- canonical task state
- progress / delivery / completion gates
- single-leaf scheduling
- closure artifact requirements
- supervision and next-task recomputation

The structural failure is not missing task logic inside `wlcc`.
The failure is that conversation output is still easier to produce than task closure.

This creates three operator-visible problems:

1. the system can emit a plausible progress reply before a leaf is actually closed
2. the current conversation does not own one durable task-flow record, so execution truth is scattered across task files and summaries
3. blocked or incomplete work can surface as narrative explanation instead of a fail-closed runtime state

The concrete bad pattern is:

`reply success without leaf closure`

## 3. Non-Goals

This spec does not include:

- planner / executor role split across separate runtimes
- multi-flow parallel orchestration
- a new provider loop or agent shell
- rich UI, slash commands, or channel-specific delivery logic
- speculative auto-decomposition beyond the existing leaf-ready runtime

## 4. Governing Principles

### 4.1 Reply must be derived from runtime truth

No user-visible terminal reply may claim meaningful progress unless it is derived from runtime state and closure evidence.

### 4.2 Open leaf means restricted reply surface

If the current leaf is still `ready`, `running`, or `verify`, the system may only emit:

- structured execution status
- structured blocked / waiting-human requests
- closure-complete final result after gate pass

Free-form "still doing", "已推进", or similar narrative progress is not a valid terminal output.

### 4.3 One conversation, one canonical task flow

When a session enters `wlcc` execution mode, the conversation must bind to one `taskFlowId`.
That flow becomes the control-plane owner for:

- current active leaf
- flow status
- flow-level closure summary
- reply eligibility

### 4.4 Closed leaf tasks remain the only unit of completed progress

Parent or flow progress may advance only from `closed` leaves.
Ordinary progress updates remain execution telemetry, not completion truth.

## 5. Enhancement A: Reply Exit Gate

### 5.1 Purpose

Prevent the model from ending a turn with a normal progress reply when the runtime does not yet allow that outcome.

### 5.2 Required behavior

Before any terminal reply is emitted, the system must evaluate a `reply exit gate` against:

- current `taskFlowId`
- active leaf status
- flow status
- closure artifacts
- latest supervision state

### 5.3 Reply decisions

The gate returns one of four decisions:

- `allow-final-reply`
- `allow-blocked-reply`
- `allow-status-reply`
- `reject-open-leaf`

### 5.4 Allow rules

`allow-final-reply` only when:

- the active leaf is `closed` or archived
- completion gate has passed
- required artifacts include `final-result`, `gap-check`, and `status-update`

`allow-blocked-reply` only when:

- the active leaf or flow is `blocked` or `waiting-human`
- a structured blocker exists
- the requested user input is precise enough to unblock the flow

`allow-status-reply` only when:

- the leaf is still open
- the reply is rendered from runtime state rather than free-form narrative
- the reply does not claim closure or completed progress

All other cases return `reject-open-leaf`.

### 5.5 Rejection behavior

When `reject-open-leaf` is returned:

- the system must not emit a normal final reply
- the runtime records a rejection event
- the fallback output is a structured control-plane status packet or no final reply at all, depending on the caller

## 6. Enhancement B: Task Flow Control Surface

### 6.1 Purpose

Turn the conversation into a flow owner rather than a loose narrative wrapper around independent task files.

### 6.2 Canonical flow model

Add a flow-level record:

```json
{
  "taskFlowId": "string",
  "ownerSessionId": "string",
  "entryMode": "wlcc-live",
  "goal": "string",
  "status": "draft|active|blocked|waiting-human|completed|aborted",
  "currentLeafTaskId": "string|null",
  "closedLeafCount": 0,
  "openLeafCount": 0,
  "lastClosureTaskId": "string|null",
  "lastStatusUpdateAt": "string",
  "replyMode": "restricted|final-only|status-only",
  "createdAt": "string",
  "updatedAt": "string"
}
```

### 6.3 Ownership rules

- every executable leaf belongs to exactly one `taskFlowId`
- only one primary active leaf may exist per flow
- flow status is recomputed from owned leaf states
- the reply gate reads flow state first, leaf state second

### 6.4 Flow status rules

- `active`: at least one leaf is `ready`, `running`, or `verify`
- `blocked`: current leaf is blocked and no alternative leaf is eligible
- `waiting-human`: current leaf explicitly requires human input
- `completed`: all owned execution leaves are closed and no runnable leaf remains

### 6.5 Session binding

Entering `wlcc` mode must create or attach to a flow record.

Once attached:

- ingest writes the flow reference onto every leaf
- progress updates refresh flow timestamps and current leaf
- closure updates recompute flow counters and next leaf ownership
- state views render by flow, not only by loose task lists

## 7. Runtime Events

The implementation must emit explicit events for:

- `flow.created`
- `flow.bound`
- `flow.status.changed`
- `reply.exit.checked`
- `reply.exit.rejected`
- `reply.exit.allowed`
- `flow.completed`

These events are consumed by supervision, sidecar summaries, and audit output.

## 8. State Views and Sidecar Outputs

The system should add flow-oriented sidecar views:

- `.agent/state/flows/<taskFlowId>.json`
- `.agent/flows/<taskFlowId>.md`
- `.agent/state/reply-gate/<taskFlowId>.json`

Existing task views remain, but they become leaf-level detail under a flow-level summary.

## 9. Verification Requirements

The implementation is complete only when the following are testable:

1. open leaf blocks ordinary final reply
2. blocked leaf allows only structured unblock reply
3. closed leaf with full closure artifacts allows final reply
4. flow state follows ingest -> progress -> close transitions
5. next-task decisions remain flow-consistent and do not switch around an open primary leaf
6. rendered flow summary matches canonical state

## 10. Implementation Order

The delivery order is:

1. reply exit gate contract and tests
2. task-flow model and persistence
3. ingest / progress / close integration
4. flow-oriented state rendering
5. end-to-end verification

## 11. Success Criteria

This spec succeeds when:

- the user can no longer receive a normal "有进度" style terminal reply while the active leaf is still open
- the conversation has one durable execution owner record
- blocked states are reported as blocked, not narrated as progress
- final replies are emitted only after runtime closure truth exists
