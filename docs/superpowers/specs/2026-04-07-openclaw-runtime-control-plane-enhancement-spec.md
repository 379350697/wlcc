# OpenClaw Runtime Control Plane Enhancement Spec

Date: 2026-04-07
Scope: `wlcc` as infrastructure serving OpenClaw
Priority: Stability first, stronger long-chain logic second, cost increase tightly bounded

## 1. Goal

Strengthen `wlcc` as OpenClaw's long-chain runtime infrastructure by adding a lightweight control plane on top of the existing runtime core.

This spec does not aim to turn `wlcc` into a Claude Code clone.
It only extracts the parts of Claude Code's rigor that materially improve:

- long-chain stability
- recovery quality
- execution governance
- evidence quality
- failure handling discipline

without introducing a heavy interactive agent shell, duplicate model loop, or expensive runtime layers that OpenClaw already owns.

## 2. Problem Statement

`wlcc` already has strong primitives:

- canonical task state
- next-task scheduling
- retrieval and resume
- risk, delivery, and progress gates
- harness execution
- heartbeat and supervision
- handoff and multi-session continuity

The current gap is not missing capability breadth.
The gap is that execution governance is still distributed across scripts and module-local rules rather than being expressed as one coherent control plane.

This creates five structural weaknesses:

1. Action semantics are implicit.
Different scripts carry different assumptions about read-only behavior, concurrency safety, timeout, evidence expectations, and failure meaning.

2. Runtime events are stateful but not first-class.
Important transitions like ingest, progress, resume, interval checks, rejection, degradation, and handoff happen, but they are not represented through a unified event layer.

3. Failure handling is present but not normalized.
The system can retry, reorder, resume, block, or handoff, but those choices are not yet modeled as one formal degradation pipeline with clear classes and escalation boundaries.

4. Retrieval and resume are layered, but budget discipline is still shallow.
The system knows source priority, but it does not yet strongly control context payload size, evidence packing, or summary pollution.

5. Evidence is collected ad hoc.
Delivery, progress, heartbeat freshness, file changes, and logs all exist, but there is no shared execution-evidence ledger that allows later stages to reason from one normalized record.

## 3. Non-Goals

This spec explicitly does not include:

- a new QueryEngine or tool-use loop that duplicates OpenClaw
- terminal UI, slash command, or provider abstractions
- a replacement permission sandbox for OpenClaw
- speculative multi-agent orchestration expansion beyond current handoff semantics
- expensive always-on tracing or telemetry that meaningfully raises runtime cost

## 4. Design Principles

### 4.1 OpenClaw owns the agent shell

`wlcc` must remain an execution-enhancement infrastructure layer, not become a second agent runtime that competes with OpenClaw.

### 4.2 Control plane, not feature sprawl

New work should unify existing semantics before adding more surface area.

### 4.3 Stronger logic must be provable

Any core change must satisfy at least one of:

- better correctness
- better recovery quality
- better stability under interruption or ambiguity
- lower redundant work
- lower sync-path cost

### 4.4 Cost increase must stay bounded

Added runtime logic must mostly be in-process and metadata-driven.
No enhancement in this spec should require a persistent heavy daemon, remote dependency, or high-frequency expensive summarization.

### 4.5 Canonical state remains the source of truth

New layers may annotate, classify, and summarize.
They must not weaken or bypass canonical state.

## 5. Target Outcome

After implementation, `wlcc` should behave like a more disciplined OpenClaw execution substrate with:

- one normalized action model
- one runtime event model
- one failure-classification and degradation pipeline
- one bounded context packaging model
- one shared execution evidence model

This should make long-chain runs more stable, easier to resume, easier to judge, and less likely to drift into weak progress or ambiguous completion.

## 6. Proposed Enhancements

### 6.1 Enhancement A: Action Registry and Execution Metadata

#### Purpose

Centralize the semantics of runtime actions so scheduling, harnessing, gating, supervision, and evidence collection work from one shared definition table.

#### Why it matters

Today `TaskHarness` already partitions read-only and concurrency-safe work, but action semantics still live partly in script choice, partly in registry metadata, and partly in gate logic.

This should become explicit and reusable.

#### New module

- `runtime/actions/registry.py`

#### New core types

```python
@dataclass
class ActionSpec:
    name: str
    script_name: str
    category: str
    read_only: bool
    concurrent_safe: bool
    timeout_s: int
    max_output_chars: int
    risk_action: str
    target_type: str
    evidence_policy: str
    progress_policy: str
    degradation_class: str
```

#### Responsibilities

- define all runtime actions in one registry
- expose lookup by action name
- expose normalized metadata to harness, gates, and supervision
- remove duplicated assumptions from scripts and tests

#### Required outcomes

- `runtime/harness/task_harness.py` reads `ActionSpec` rather than ad hoc meta shape
- gate logic can reason from action categories, not just script names
- future actions inherit default semantics instead of inventing local ones

#### Expected benefit

- stronger consistency
- fewer hidden behavior differences across scripts
- easier regression testing
- lower chance of unsafe or weakly validated new actions entering the runtime

### 6.2 Enhancement B: Runtime Lifecycle Event Bus

#### Purpose

Turn state transitions into first-class runtime events so governance logic can attach cleanly without increasing script-to-script coupling.

#### Why it matters

You already have meaningful transition points:

- task ingested
- task changed
- interval tick
- interruption detected
- completion reached
- handoff emitted
- delivery rejected
- risk blocked

These should be emitted once and consumed by interested modules.

#### New modules

- `runtime/events/models.py`
- `runtime/events/bus.py`

#### Event examples

```python
RuntimeEvent(
    event_type="task.progress.updated",
    task_id="...",
    stage="progress",
    payload={...},
    emitted_at="..."
)
```

#### Subscribers in phase one

- supervision
- heartbeat emit
- evidence ledger
- audit log writer
- degradation pipeline

#### Design rule

This is a local synchronous event bus, not a distributed message system.
Keep it in-process and cheap.

#### Expected benefit

- cleaner runtime boundaries
- easier auditing
- easier testing of transition semantics
- lower coupling between scripts and side-effects

### 6.3 Enhancement C: Failure Classification and Degradation Pipeline

#### Purpose

Normalize how the runtime reacts when work is weak, blocked, stale, inconsistent, or high-risk.

#### Why it matters

Right now the system has failure-related behaviors, but they are spread across:

- progress gate
- delivery gate
- risk gate
- retry state
- supervision
- resume and handoff flows

The runtime needs a single decision pipeline that answers:

- what kind of failure is this
- can we retry
- should we degrade
- should we prepare resume
- should we block
- should we require human review

#### New modules

- `runtime/failure/models.py`
- `runtime/failure/classifier.py`
- `runtime/failure/pipeline.py`

#### Failure classes

- `content_weak`
- `evidence_insufficient`
- `risk_blocked`
- `state_inconsistent`
- `heartbeat_stale`
- `dependency_unsatisfied`
- `circular_progress`
- `task_scope_conflict`
- `resume_required`
- `manual_intervention_required`

#### Degradation actions

- `retry_same_step`
- `retry_with_reordered_step`
- `degrade_continue`
- `freeze_task`
- `prepare_resume`
- `emit_handoff`
- `escalate_human`

#### Key rule

No failure path should directly decide in isolation once this pipeline exists.
Each gate can produce a structured verdict, but final next action should be normalized through the failure pipeline.

#### Expected benefit

- fewer contradictory reactions across modules
- better long-chain survivability
- more explainable runtime decisions
- cleaner rollback and audit reasoning

### 6.4 Enhancement D: Context Budget and Evidence Budget Control

#### Purpose

Improve retrieval and resume quality by explicitly controlling what is packed into runtime context and how much evidence is carried forward.

#### Why it matters

You already have source priority discipline.
The next level is budget discipline:

- canonical facts should always fit
- task state should be complete
- summaries should be bounded
- logs should be tailed, not dumped
- weak or duplicate context should be trimmed

#### New modules

- `runtime/context/budget.py`
- `runtime/context/package.py`

#### Budget model

One hard char budget plus deterministic section/item caps:

- `context_budget_chars`
- section/item caps for facts, task state, summaries, and recent tails

#### Packaging order

1. project facts
2. canonical task state
3. resume-state essentials
4. next-task essentials
5. summary snippets
6. recent event tails

#### Rules

- facts are never dropped before summaries
- canonical JSON is preferred over markdown renderings
- duplicate sidecar content should be collapsed
- degraded fallback must stay explicit in metadata
- large tails are clipped deterministically

#### Expected benefit

- more stable resume payloads
- lower pollution from sidecar text
- bounded context cost
- better long-chain continuity without expensive summarization

### 6.5 Enhancement E: Execution Evidence Ledger

#### Purpose

Aggregate execution proof into one normalized runtime artifact so progress, delivery, supervision, and final closure reason from the same evidence base.

#### Why it matters

Current evidence exists in multiple forms:

- latest result text
- file existence checks
- file change heuristics
- heartbeat freshness
- harness logs
- event logs
- state updates

These should converge into one ledger per task.

#### New modules

- `runtime/evidence/models.py`
- `runtime/evidence/ledger.py`

#### Evidence types

- `content`
- `file_change`
- `state_change`
- `heartbeat`
- `script_result`
- `risk_verdict`
- `gate_verdict`
- `resume_artifact`
- `handoff_artifact`

#### Artifact location

- `.agent/state/evidence/<task-id>.json`

#### Expected benefit

- stronger completion logic
- less ad hoc proof gathering
- easier audit and debugging
- better support for real-task-first delivery thresholds

## 7. Architecture Impact

### 7.1 New runtime layout

```text
runtime/
├── actions/
├── context/
├── evidence/
├── events/
├── failure/
├── common/
├── gates/
├── harness/
├── resume/
├── scheduling/
├── sidecar/
├── state/
└── supervision/
```

### 7.2 Existing modules that should be upgraded

- `runtime/harness/task_harness.py`
- `runtime/gates/progress.py`
- `runtime/gates/delivery.py`
- `runtime/gates/risk.py`
- `runtime/resume/context.py`
- `runtime/resume/service.py`
- `runtime/supervision/core.py`

### 7.3 Existing modules that should remain structurally stable

- canonical state store
- next-task selection core
- handoff state rendering
- sidecar report generators

The goal is to strengthen orchestration and governance around them, not replace them.

## 8. Runtime Flow After Enhancement

### 8.1 Progress update path

1. script invokes action by normalized action name
2. action registry resolves metadata
3. harness executes under registry metadata
4. event bus emits execution events
5. evidence ledger records proof
6. gates emit structured verdicts
7. failure pipeline normalizes the outcome
8. supervision reacts to normalized outcome
9. sidecar refresh runs only where needed

### 8.2 Resume path

1. context packager loads prioritized sources
2. budget controller trims payload deterministically
3. evidence ledger contributes recent proof snapshot
4. resume payload includes explicit degradation flags
5. failure pipeline decides whether resume is enough or handoff is needed

### 8.3 Completion path

1. delivery gate collects evidence from ledger
2. weak completion becomes `evidence_insufficient`
3. failure pipeline decides retry, degrade, or human escalation
4. only sufficient completion can advance to handoff-prepared

## 9. Acceptance Criteria

### 9.1 Stability criteria

- no loss of canonical state authority
- no new path where sidecar artifacts override canonical JSON
- no direct gate-to-terminal decision path outside the failure pipeline for covered cases
- no reduction in existing runtime test pass rate

### 9.2 Logic criteria

- every runtime action has a normalized `ActionSpec`
- every major transition emits a typed runtime event
- every covered failure resolves through one normalized degradation decision
- every real task has an evidence ledger artifact

### 9.3 Cost criteria

- no new always-on background process
- no remote service dependency
- no mandatory expensive summarization call in the sync path
- sync-path wall time should not regress by more than 10-15% in standard verification runs

### 9.4 Performance criteria

Expected net result should be:

- lower wasted retries
- lower duplicate sidecar reads
- lower ambiguity in completion and resume
- bounded context packaging cost

If a core change adds overhead without materially improving these outcomes, it should be rejected.

## 10. Measurement Plan

### 10.1 New metrics to track

- failure class distribution
- degradation action distribution
- weak completion rejection count
- resume payload size
- evidence item count per task
- harness parallel step efficiency
- stale heartbeat recovery rate

### 10.2 Comparison baseline

Use current:

- `verify_standard_runtime_bundle.py`
- runtime pytest suite
- real task samples
- interruption/resume scenarios
- delivery gate scenarios

### 10.3 Success indicators

- fewer false-positive completions
- fewer ambiguous resume outputs
- fewer circular progress updates
- cleaner supervision decisions
- no meaningful increase in verification runtime beyond bounded threshold

## 11. Rollout Plan

### Phase P0: Control Plane Skeleton

Implement:

- `runtime/actions/registry.py`
- `runtime/events/models.py`
- `runtime/events/bus.py`
- adapter wiring in harness and supervision

Goal:

- central metadata
- event emission without changing core behavior yet

### Phase P1: Failure Pipeline

Implement:

- failure models
- classifier
- degradation pipeline
- gate verdict normalization

Goal:

- unify runtime reactions
- reduce scattered failure semantics

### Phase P2: Context and Evidence Discipline

Implement:

- context budget controller
- context packager
- evidence ledger
- delivery gate integration

Goal:

- stronger resume quality
- stronger delivery proof
- bounded sync-path context cost

### Phase P3: Tightening and Proof

Implement:

- benchmark checks in verification bundle
- scenario-specific assertions for degradation outcomes
- regression tests for cost ceiling and decision consistency

Goal:

- prove the core changes are real optimizations rather than architectural decoration

## 12. Test Strategy

### 12.1 Runtime unit tests

Add focused tests for:

- action registry coverage
- event emission ordering
- failure classification
- degradation routing
- context budget trimming
- evidence ledger aggregation

### 12.2 Integration tests

Add scenarios for:

- weak progress followed by normalized degradation
- stale heartbeat causing resume preparation
- real task completion with insufficient evidence rejected
- resume payload staying bounded under noisy sidecar state
- concurrent harness steps preserving evidence integrity

### 12.3 Verification bundle updates

Extend `scripts/verify_standard_runtime_bundle.py` to include:

- control plane smoke test
- failure pipeline smoke test
- context budget smoke test
- evidence ledger smoke test

## 13. Risks and Countermeasures

### Risk 1: Over-centralization slows iteration

Countermeasure:
Keep the control plane metadata-first and local.
Do not force every edge case into a framework before it proves value.

### Risk 2: Event bus becomes hidden complexity

Countermeasure:
Use synchronous in-process dispatch only.
No async worker system in this phase.

### Risk 3: Failure pipeline becomes overengineered

Countermeasure:
Start with a small failure taxonomy tied directly to current real cases.
Do not add abstract states without tests.

### Risk 4: Context packaging adds unnecessary cost

Countermeasure:
Use deterministic trimming and local packing only.
No model-generated summaries in the sync path.

### Risk 5: Evidence ledger duplicates existing logs

Countermeasure:
Ledger stores normalized pointers and compact facts, not full raw output copies.

## 14. Recommendation

Implement all five enhancements, but in the phased order above.

This is the highest-yield path because it strengthens the exact layer `wlcc` is supposed to own:

- not the agent shell
- not the provider runtime
- not the UI

but the execution control plane that makes OpenClaw long-chain work stable, governable, resumable, and provable.

## 15. Summary

The right Claude Code lessons for `wlcc` are not product-shell features.
They are runtime-discipline patterns.

This spec recommends extracting those patterns into an OpenClaw-serving control plane made of:

- action registry
- lifecycle events
- failure and degradation pipeline
- context budget control
- execution evidence ledger

If implemented well, this should make long-chain execution:

- more stable
- more explainable
- harder to fake-complete
- easier to resume
- stronger under interruption

while keeping cost growth modest and preserving `wlcc`'s role as infrastructure rather than agent shell.
