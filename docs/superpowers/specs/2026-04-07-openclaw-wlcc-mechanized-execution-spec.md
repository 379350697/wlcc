# OpenClaw + wlcc Mechanized Execution Spec

Date: 2026-04-07
Scope: `OpenClaw` planning + `wlcc` execution/closure infrastructure
Priority: Mechanism-first correctness, then autonomy depth

## 1. Goal

Build a mechanism-level execution model where:

- `OpenClaw` decomposes complex goals into structured tasks
- `wlcc` executes one leaf task at a time
- task progress, task closure, and task switching are decided by state, events, gates, and evidence
- soft prompting remains useful, but no critical path depends on model memory or context luck

The target outcome is not "a smarter prompt."
The target outcome is a stable system where task decomposition and task execution are both durable, auditable, and fail-closed.

## 2. Problem Statement

Current `wlcc` already has meaningful runtime primitives:

- canonical task state
- lifecycle state
- progress / delivery / completion gates
- next-task scheduling
- supervision and heartbeat
- evidence ledger
- handoff and resume flows

Current `OpenClaw` already has some planning and task-splitting ability through the model.

The remaining gap is structural:

1. `OpenClaw` can think in tasks, but does not yet emit a task bundle that `wlcc` can reliably execute.
2. `wlcc` can execute tasks, but does not yet require every incoming task to be a bounded, closure-ready leaf.
3. task switching still risks being inferred from text or weak progress rather than from closure truth.
4. key rules still risk living in prompts or operator memory rather than in mechanism-level enforcement.

This creates the failure mode the system must eliminate:

`continuous motion, zero closed leaf tasks`

## 3. Governing Principles

### 3.1 Mechanism first

Every critical capability must be enforced by mechanism:

- task decomposition handoff
- task contract validation
- lifecycle transitions
- progress admission
- closure judgment
- task switching
- resume / handoff continuity

### 3.2 Soft constraints may enhance, not guarantee

Prompting, style rules, and memory may improve quality, but they cannot be the final source of truth for:

- what the current task is
- whether the task is complete
- whether the system may switch tasks
- whether progress is valid

### 3.3 OpenClaw owns planning, wlcc owns execution

`OpenClaw` is the planner and decomposer.
`wlcc` is the leaf-task executor and closure judge.

Neither side should impersonate the other:

- `OpenClaw` must not directly mark a leaf as complete
- `wlcc` must not expand scope into a new task on its own

### 3.4 Closed leaf tasks are the only valid unit of progress

Parent task and epic progress may only advance from `closed` leaf tasks.
Natural-language summaries, partial edits, or repeated status updates are not valid substitutes.

## 4. System Roles

### 4.1 OpenClaw

Responsibilities:

- normalize user goals
- split work into `epic -> task -> leaf`
- decide ordering and dependency shape
- produce structured task bundles
- re-evaluate parent progress after leaf closure

### 4.2 wlcc

Responsibilities:

- validate leaf task contracts
- ingest only `ready` leaf tasks into the execution chain
- enforce single-leaf execution
- enforce progress / delivery / closure gates
- supervise weak progress and stale execution
- archive only after closure passes

## 5. Canonical Task Model

The system uses three task levels:

- `epic`
- `task`
- `leaf`

Only `leaf` tasks may enter the active execution chain.

Each `leaf` must carry a minimum contract:

```json
{
  "taskId": "string",
  "parentTaskId": "string",
  "taskLevel": "leaf",
  "goal": "string",
  "allowedPaths": ["..."],
  "doneWhen": ["..."],
  "requiredEvidence": ["..."],
  "requiredTests": ["..."],
  "priority": "P0|P1|P2|P3",
  "riskLevel": "low|medium|high",
  "estimatedTurns": 1,
  "estimatedMinutes": 1,
  "splitConfidence": 0.0,
  "status": "draft|ready|running|verify|closed|blocked|waiting-human"
}
```

Additional guidance:

- `goal` must describe one bounded outcome
- `allowedPaths` must define the writable execution boundary
- `doneWhen` must be explicit and testable
- `requiredEvidence` and `requiredTests` must make closure provable
- `estimatedTurns` and `estimatedMinutes` are used to reject oversized leaves

## 6. Lifecycle and Control Ownership

The canonical state machine is:

`draft -> ready -> running -> verify -> closed`

Exceptional states:

- `blocked`
- `waiting-human`

Ownership by state:

- `draft`: `OpenClaw`
- `ready`: handoff boundary from `OpenClaw` to `wlcc`
- `running`: `wlcc`
- `verify`: `wlcc`
- `closed`: hand back to `OpenClaw`
- `blocked` / `waiting-human`: neither side may bypass the gate

Rules:

1. `draft` leaves are visible but not schedulable.
2. only `ready` leaves may be ingested into `wlcc`.
3. only one `running` or `verify` leaf may exist on the primary track at a time.
4. sibling or parent switching is forbidden until the current leaf is `closed` or explicitly blocked.
5. parent task progress is recomputed from child leaf states, not from summaries.

## 7. Decomposition Flow

`OpenClaw` must not free-form split work directly into executable tasks.
It must follow this sequence:

1. Goal normalize
2. Phase split
3. Leaf candidate expand
4. Leaf judge
5. Draft-to-ready promotion

### 7.1 Leaf judge

Every candidate leaf must be judged on:

- single-goal fit
- bounded scope
- verifiability
- closure readiness
- execution budget fit

Candidate leaves must be rejected if they include patterns like:

- "顺便"
- "同时处理多个模块"
- "补齐剩余问题"
- "推进到下一阶段"
- "完成相关工作"

These indicate a parent task or vague bundle, not a leaf.

### 7.2 Mixed admission mode

The system should use mixed admission:

- auto-promote simple, bounded leaves from `draft` to `ready`
- keep ambiguous or high-risk leaves in `draft` pending confirmation or further split

Auto-promotion is only allowed when:

- scope is single-directory or equivalently bounded
- closure standard is explicit
- required tests are known or explicitly unnecessary
- no multi-leaf dependency is hidden inside the candidate

## 8. Execution Signals

`OpenClaw` must consume real execution signals rather than infer state from ordinary chat text.

All executors should map into one normalized runtime event model, including:

- task created
- task promoted to ready
- task started
- task progress updated
- artifact emitted
- test recorded
- gap check emitted
- status update emitted
- closure requested
- closure passed
- closure rejected
- handoff prepared
- human input required
- run stopped

Canonical state changes must be event-driven.

## 9. Closure Contract

Every real leaf task must pass a hard closure gate before it may become `closed`.

Default closure requirements for real work:

- `final-result`
- `gap-check`
- `status-update`

These are the default "three-piece" closure artifacts.
They may be extended by task-specific evidence or tests, but they may not be silently dropped.

Closure rules:

1. no three-piece evidence, no closure
2. no closure, no archive
3. no archive, no next leaf switch on the same execution track

## 10. Progress Discipline

Valid progress is not "any update."
Valid progress must be:

- admitted by progress and delivery gates
- written transactionally
- supported by changed files, tests, or evidence
- supervised for weak-progress patterns

Weak progress must cause escalation rather than silent continuation.

## 11. Non-Goals

This spec does not propose:

- replacing `OpenClaw` with a second shell
- copying Claude Code or Codex UX wholesale
- relying on always-on heavy telemetry
- broad multi-agent orchestration beyond task-tree and handoff discipline
- using prompts as the main enforcement layer

## 12. Acceptance Criteria

The design is successful when all of the following are true:

1. `OpenClaw` can emit a structured task bundle with `draft` and `ready` leaves.
2. `wlcc` can ingest only `ready` leaves and reject malformed ones.
3. `wlcc` can execute one leaf at a time and refuse sibling switching before closure.
4. closure requires three-piece artifacts plus task-specific requirements.
5. parent progress changes only after child leaf closure.
6. loss of prompt context does not cause incorrect closure or task switching.

## 13. One-Line Summary

`OpenClaw` must mechanize decomposition into closure-ready leaves, and `wlcc` must mechanize execution into provably closed leaves, with soft constraints enhancing quality but never carrying correctness alone.
