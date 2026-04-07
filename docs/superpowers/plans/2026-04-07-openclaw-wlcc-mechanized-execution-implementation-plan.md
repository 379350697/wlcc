# OpenClaw + wlcc Mechanized Execution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `OpenClaw` decompose work into structured `wlcc`-ready leaves and make `wlcc` execute and close those leaves through mechanism-level contracts, gates, events, and evidence.

**Architecture:** Add a decomposition layer that produces `draft` and `ready` leaves, extend the runtime contract and lifecycle to understand those states, harden closure with three-piece artifact gates, and bind scheduling/progress/supervision to closed-leaf truth rather than summary text. Keep `OpenClaw` as planner and `wlcc` as execution control plane.

**Tech Stack:** Python 3, pytest, existing `runtime/` package, existing `scripts/` wrappers, JSON state under `.agent/state/`, markdown specs/plans under `docs/superpowers/`

---

## File Structure

### New files

- `runtime/decomposition/__init__.py`
- `runtime/decomposition/models.py`
- `runtime/decomposition/judge.py`
- `runtime/decomposition/promotion.py`
- `runtime/gates/closure_artifacts.py`
- `scripts/ingest_decomposed_leaf.py`
- `tests/runtime/test_decomposition_models.py`
- `tests/runtime/test_leaf_judge.py`
- `tests/runtime/test_leaf_promotion.py`
- `tests/runtime/test_closure_artifacts.py`
- `tests/runtime/test_mechanized_execution_e2e.py`

### Existing files to modify

- `runtime/contracts/task_contract.py`
- `runtime/common/models.py`
- `runtime/state/store.py`
- `runtime/state/lifecycle.py`
- `runtime/scheduling/next_task.py`
- `runtime/supervision/core.py`
- `runtime/evidence/ledger.py`
- `runtime/gates/completion.py`
- `scripts/ingest_real_task.py`
- `scripts/progress_task_runtime.py`
- `scripts/close_task_runtime.py`
- `scripts/verify_standard_runtime_bundle.py`
- `tests/runtime/test_task_contract.py`
- `tests/runtime/test_completion_gate.py`
- `tests/runtime/test_execution_lock.py`
- `tests/runtime/test_stall_guard.py`
- `tests/runtime/test_next_task.py`

## Task 1: Extend the Leaf Task Contract for Mechanized Execution

**Files:**
- Modify: `runtime/contracts/task_contract.py`
- Modify: `runtime/common/models.py`
- Modify: `runtime/state/store.py`
- Modify: `tests/runtime/test_task_contract.py`
- Test: `tests/runtime/test_decomposition_models.py`

- [ ] **Step 1: Write failing contract tests for mechanized leaf fields**

Add tests for:
- `status=draft|ready|running|verify|closed|blocked|waiting-human`
- `estimatedTurns`
- `estimatedMinutes`
- `riskLevel`
- `splitConfidence`
- parent-child persistence for leaf tasks

- [ ] **Step 2: Run the failing tests**

Run: `python3 -m pytest tests/runtime/test_task_contract.py tests/runtime/test_decomposition_models.py -q`
Expected: FAIL because the contract does not yet understand the new fields or states

- [ ] **Step 3: Extend the normalized task contract**

In `runtime/contracts/task_contract.py`, add normalized support for:
- execution status fields
- execution budget fields
- split-confidence metadata
- parent-task linkage used by decomposition output

Fail closed on unknown lifecycle-ready execution states.

- [ ] **Step 4: Persist the extended contract in task state**

Modify `runtime/common/models.py` and `runtime/state/store.py` so the new fields round-trip cleanly for real leaf tasks and remain backward compatible for legacy tasks.

- [ ] **Step 5: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_task_contract.py tests/runtime/test_decomposition_models.py tests/runtime/test_state_store.py -q`
Expected: PASS

## Task 2: Add Draft-to-Ready Decomposition Models and Leaf Judge

**Files:**
- Create: `runtime/decomposition/__init__.py`
- Create: `runtime/decomposition/models.py`
- Create: `runtime/decomposition/judge.py`
- Create: `runtime/decomposition/promotion.py`
- Test: `tests/runtime/test_decomposition_models.py`
- Test: `tests/runtime/test_leaf_judge.py`
- Test: `tests/runtime/test_leaf_promotion.py`

- [ ] **Step 1: Write failing tests for decomposition bundle models**

Cover:
- `epic/task/leaf` bundle normalization
- `draft` leaves are non-schedulable
- simple bounded leaves can be promoted to `ready`
- ambiguous leaves stay in `draft`

- [ ] **Step 2: Run the failing tests**

Run: `python3 -m pytest tests/runtime/test_leaf_judge.py tests/runtime/test_leaf_promotion.py -q`
Expected: FAIL because the decomposition layer does not exist

- [ ] **Step 3: Implement decomposition models**

In `runtime/decomposition/models.py`, define:
- `EpicBundle`
- `TaskBundle`
- `LeafBundle`
- helpers to map a decomposed leaf into `wlcc` task contract shape

- [ ] **Step 4: Implement leaf judge**

In `runtime/decomposition/judge.py`, add fail-closed checks for:
- single-goal fit
- bounded scope
- closure readiness
- verifiability
- execution budget fit

Reject phrases that indicate bundled work or vague scope.

- [ ] **Step 5: Implement draft-to-ready promotion**

In `runtime/decomposition/promotion.py`, add auto-promotion rules for:
- bounded `allowedPaths`
- explicit closure standard
- known evidence and tests
- no hidden sibling work

- [ ] **Step 6: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_decomposition_models.py tests/runtime/test_leaf_judge.py tests/runtime/test_leaf_promotion.py -q`
Expected: PASS

## Task 3: Make Lifecycle and Scheduling Understand Draft/Ready/Closed Truth

**Files:**
- Modify: `runtime/state/lifecycle.py`
- Modify: `runtime/scheduling/next_task.py`
- Modify: `tests/runtime/test_execution_lock.py`
- Modify: `tests/runtime/test_next_task.py`

- [ ] **Step 1: Write failing tests for ready-only scheduling**

Cover:
- `draft` leaves are visible but never selected
- `ready` leaves may be scheduled
- `running` or `verify` leaf blocks sibling switching
- only `closed` leaf releases the track

- [ ] **Step 2: Run the failing scheduling tests**

Run: `python3 -m pytest tests/runtime/test_execution_lock.py tests/runtime/test_next_task.py -q`
Expected: FAIL because scheduling does not yet distinguish these semantics

- [ ] **Step 3: Extend lifecycle transitions**

In `runtime/state/lifecycle.py`, add or map execution states so the runtime can distinguish:
- planning-only draft state
- execution-ready state
- verification state
- closed state that authorizes parent recomputation

- [ ] **Step 4: Tighten scheduler selection**

In `runtime/scheduling/next_task.py`, enforce:
- `draft` is non-runnable
- only `ready` may be selected as next leaf
- active `running` / `verify` leaf blocks siblings
- `closed` is the only success path that opens the next leaf

- [ ] **Step 5: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_execution_lock.py tests/runtime/test_next_task.py -q`
Expected: PASS

## Task 4: Harden Closure With Three-Piece Artifact Gates

**Files:**
- Create: `runtime/gates/closure_artifacts.py`
- Modify: `runtime/gates/completion.py`
- Modify: `scripts/close_task_runtime.py`
- Modify: `tests/runtime/test_completion_gate.py`
- Test: `tests/runtime/test_closure_artifacts.py`

- [ ] **Step 1: Write failing tests for the three-piece closure requirement**

Cover:
- missing `final-result` fails closure
- missing `gap-check` fails closure
- missing `status-update` fails closure
- all three plus task-specific requirements pass

- [ ] **Step 2: Run the failing closure tests**

Run: `python3 -m pytest tests/runtime/test_completion_gate.py tests/runtime/test_closure_artifacts.py -q`
Expected: FAIL because closure artifacts are not yet a hard mechanism

- [ ] **Step 3: Implement closure artifact checks**

In `runtime/gates/closure_artifacts.py`, normalize artifact presence checks from evidence or explicit artifact records.

- [ ] **Step 4: Extend completion gate**

In `runtime/gates/completion.py`, require:
- verify phase
- three-piece closure artifacts
- task-specific required evidence
- task-specific required tests
- allowed-path compliance

- [ ] **Step 5: Make close fail closed**

Modify `scripts/close_task_runtime.py` so close only succeeds after the closure artifact gate passes.
Do not archive on failure.

- [ ] **Step 6: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_completion_gate.py tests/runtime/test_closure_artifacts.py -q`
Expected: PASS

## Task 5: Make Progress Transactional and Reject Weak Non-Closure Motion

**Files:**
- Modify: `scripts/progress_task_runtime.py`
- Modify: `runtime/supervision/core.py`
- Modify: `runtime/evidence/ledger.py`
- Modify: `tests/runtime/test_stall_guard.py`

- [ ] **Step 1: Write failing tests for transactional progress**

Cover:
- rejected progress does not write task state
- rejected progress does not advance turn count
- rejected progress does not mutate schedulable status
- repeated weak progress escalates to `blocked` or `waiting-human`

- [ ] **Step 2: Run the failing tests**

Run: `python3 -m pytest tests/runtime/test_stall_guard.py tests/runtime/test_supervision_core.py -q`
Expected: FAIL because progress still writes state before all governance checks settle

- [ ] **Step 3: Refactor progress into candidate -> validate -> commit**

Modify `scripts/progress_task_runtime.py` so it:
- builds a candidate update in memory
- runs progress, delivery, and supervision-relevant checks
- commits only if all gates pass

- [ ] **Step 4: Record closure-relevant evidence in the ledger**

Modify `runtime/evidence/ledger.py` integration points so progress, artifacts, and tests are stored in a shape closure and supervision can reuse directly.

- [ ] **Step 5: Escalate repeated weak progress**

Modify `runtime/supervision/core.py` so repeated weak-progress transitions stop further healthy continuation and force explicit recovery.

- [ ] **Step 6: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_stall_guard.py tests/runtime/test_supervision_core.py tests/runtime/test_evidence_ledger.py -q`
Expected: PASS

## Task 6: Add a Decomposed-Leaf Ingest Path

**Files:**
- Create: `scripts/ingest_decomposed_leaf.py`
- Modify: `scripts/ingest_real_task.py`
- Modify: `tests/runtime/test_task_contract.py`
- Test: `tests/runtime/test_leaf_promotion.py`

- [ ] **Step 1: Write failing tests for decomposed-leaf ingest**

Cover:
- `draft` leaf cannot be ingested into active execution
- `ready` leaf can be ingested with parent linkage preserved
- malformed decomposition bundle is rejected

- [ ] **Step 2: Run the failing tests**

Run: `python3 -m pytest tests/runtime/test_task_contract.py tests/runtime/test_leaf_promotion.py -q`
Expected: FAIL because no decomposed-leaf ingest entry exists

- [ ] **Step 3: Implement decomposed-leaf ingest**

In `scripts/ingest_decomposed_leaf.py`, accept a structured leaf bundle and write a `wlcc`-ready task only when:
- state is `ready`
- contract is complete
- parent linkage is present

- [ ] **Step 4: Keep legacy ingest compatible**

Modify `scripts/ingest_real_task.py` minimally so direct real-task ingest still works, but internally aligns with the stricter ready-leaf contract when appropriate.

- [ ] **Step 5: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_task_contract.py tests/runtime/test_leaf_promotion.py -q`
Expected: PASS

## Task 7: Verify End-to-End Mechanized Execution

**Files:**
- Modify: `scripts/verify_standard_runtime_bundle.py`
- Test: `tests/runtime/test_mechanized_execution_e2e.py`

- [ ] **Step 1: Write the end-to-end failing test**

Cover this path:
- decomposed leaf starts as `draft`
- passes judge and promotion into `ready`
- ingests into `wlcc`
- runs one leaf only
- cannot close without three-piece artifacts
- closes after all closure requirements are present
- only then releases the next leaf

- [ ] **Step 2: Run the failing test**

Run: `python3 -m pytest tests/runtime/test_mechanized_execution_e2e.py -q`
Expected: FAIL because the full mechanism path is incomplete

- [ ] **Step 3: Update bundle verification**

Modify `scripts/verify_standard_runtime_bundle.py` so the standard verification path includes the new mechanized execution scenario.

- [ ] **Step 4: Run final verification**

Run: `python3 -m pytest tests/runtime/test_task_contract.py tests/runtime/test_decomposition_models.py tests/runtime/test_leaf_judge.py tests/runtime/test_leaf_promotion.py tests/runtime/test_completion_gate.py tests/runtime/test_closure_artifacts.py tests/runtime/test_execution_lock.py tests/runtime/test_stall_guard.py tests/runtime/test_mechanized_execution_e2e.py -q`

Run:

```bash
python3 scripts/verify_standard_runtime_bundle.py
```

Expected: PASS

## Notes for the Implementer

- Do not weaken current canonical state guarantees.
- Do not rely on prompt text as the source of closure truth.
- Preserve backward compatibility for legacy tasks where practical, but do not let legacy ambiguity bypass new real-leaf rules.
- Keep `OpenClaw` as planner and `wlcc` as execution control plane; do not let either side absorb the other's role.
- Treat three-piece closure as the default mechanism for real work, with task-specific extensions allowed.
