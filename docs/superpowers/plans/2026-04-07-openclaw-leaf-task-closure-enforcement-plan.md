# OpenClaw Leaf Task Closure Enforcement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `wlcc` enforce fast, fail-closed closure of one leaf task at a time so long-chain runs cannot drift into "continuous motion, zero completed tasks."

**Architecture:** Add a small task-contract layer on top of the existing runtime state, then route ingest, progress, close, scheduling, and supervision through that contract. The runtime stays a control plane, not a second agent shell: one active leaf task, structured evidence-backed progress, strict completion gates, and anti-stall escalation.

**Tech Stack:** Python 3, pytest, existing `runtime/` package, existing `scripts/` wrappers, JSON state under `.agent/state/`

---

## File Structure

### New files

- `runtime/contracts/__init__.py`
- `runtime/contracts/task_contract.py`
- `runtime/gates/completion.py`
- `tests/runtime/test_task_contract.py`
- `tests/runtime/test_completion_gate.py`
- `tests/runtime/test_execution_lock.py`
- `tests/runtime/test_stall_guard.py`

### Existing files to modify

- `runtime/common/models.py`
- `runtime/state/store.py`
- `runtime/scheduling/next_task.py`
- `runtime/supervision/core.py`
- `scripts/ingest_real_task.py`
- `scripts/progress_task_runtime.py`
- `scripts/close_task_runtime.py`
- `scripts/test_ingest_real_task.py`
- `scripts/test_progress_task_runtime.py`
- `scripts/test_close_task_runtime.py`
- `tests/runtime/test_next_task.py`
- `tests/runtime/test_supervision_core.py`

### Responsibilities

- `runtime/contracts/task_contract.py`
  Define the normalized contract for a task: leaf-vs-parent role, allowed scope, completion requirements, turn/time budgets, and execution phase.
- `runtime/gates/completion.py`
  Centralize completion validation so `close_task_runtime.py` fails closed instead of trusting free-form text.
- `runtime/common/models.py`
  Extend `TaskState` with contract fields without breaking current callers.
- `scripts/ingest_real_task.py`
  Require or derive a default leaf-task contract at ingest time.
- `scripts/progress_task_runtime.py`
  Accept structured progress payload, reject evidence-free progress, and persist turn/phase updates.
- `runtime/scheduling/next_task.py`
  Enforce the single-leaf execution lock so no sibling task is scheduled while the current leaf is still open.
- `runtime/supervision/core.py`
  Detect weak progress from missing evidence/test/phase deltas and escalate to resume/handoff instead of silently spinning.

## Task 1: Add Task Contract Schema and Persistence

**Files:**
- Create: `runtime/contracts/__init__.py`
- Create: `runtime/contracts/task_contract.py`
- Modify: `runtime/common/models.py`
- Modify: `runtime/state/store.py`
- Modify: `scripts/ingest_real_task.py`
- Test: `tests/runtime/test_task_contract.py`
- Test: `scripts/test_ingest_real_task.py`

- [ ] **Step 1: Write the failing contract tests**

Create `tests/runtime/test_task_contract.py` covering:
- contract defaults for a leaf real task
- fail-closed validation for unknown phase
- fail-closed validation when `allowedPaths` is empty on a leaf task
- serialization round-trip from `TaskState`

```python
def test_leaf_contract_requires_allowed_paths():
    from runtime.contracts.task_contract import TaskContract

    contract = TaskContract(taskLevel="leaf", allowedPaths=[], doneWhen=["state updated"])

    verdict = contract.validate()

    assert verdict.passed is False
    assert "allowedPaths" in verdict.reason
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python3 -m pytest tests/runtime/test_task_contract.py -q`
Expected: FAIL because `runtime.contracts.task_contract` does not exist yet

- [ ] **Step 3: Implement the contract model**

In `runtime/contracts/task_contract.py`, define:
- `TaskContract`
- `ContractValidationResult`
- `normalize_contract(...)`
- `validate_contract_dict(...)`

Required fields for leaf tasks:
- `taskLevel`
- `phase`
- `doneWhen`
- `requiredEvidence`
- `requiredTests`
- `allowedPaths`
- `maxTurns`
- `maxMinutes`

Keep defaults intentionally small and strict:
- `taskLevel="leaf"`
- `phase="analyze"`
- `requiredEvidence=["state-update"]`
- `requiredTests=[]`
- `maxTurns=8`
- `maxMinutes=20`

- [ ] **Step 4: Extend `TaskState` and persistence**

Modify `runtime/common/models.py` and `runtime/state/store.py` so task JSON can carry:

```python
taskLevel: str = "leaf"
parentTaskId: str = ""
phase: str = "analyze"
doneWhen: list[str] = field(default_factory=list)
requiredEvidence: list[str] = field(default_factory=list)
requiredTests: list[str] = field(default_factory=list)
allowedPaths: list[str] = field(default_factory=list)
forbiddenPaths: list[str] = field(default_factory=list)
maxTurns: int = 8
maxMinutes: int = 20
turnCount: int = 0
```

Preserve backward compatibility by filling missing fields during load/normalize rather than crashing on legacy task files.

- [ ] **Step 5: Make ingest create a real contract**

Modify `scripts/ingest_real_task.py` so real tasks either:
- accept explicit contract-like CLI inputs, or
- derive a strict default contract from the project root and title

Minimum initial behavior:
- real tasks ingest as `taskLevel="leaf"`
- `phase="analyze"`
- `allowedPaths=["."]`
- `doneWhen=["required evidence recorded", "required tests passed", "state archived"]`

- [ ] **Step 6: Extend ingest script test**

Update `scripts/test_ingest_real_task.py` to assert that ingested tasks contain the new contract fields and default values.

- [ ] **Step 7: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_task_contract.py tests/runtime/test_state_store.py -q`
Run: `python3 scripts/test_ingest_real_task.py`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add runtime/contracts runtime/common/models.py runtime/state/store.py scripts/ingest_real_task.py tests/runtime/test_task_contract.py scripts/test_ingest_real_task.py
git commit -m "feat: persist strict task contracts for real tasks"
```

## Task 2: Enforce Structured Progress and Fail-Closed Completion

**Files:**
- Create: `runtime/gates/completion.py`
- Modify: `scripts/progress_task_runtime.py`
- Modify: `scripts/close_task_runtime.py`
- Modify: `scripts/test_progress_task_runtime.py`
- Modify: `scripts/test_close_task_runtime.py`
- Test: `tests/runtime/test_completion_gate.py`

- [ ] **Step 1: Write the failing completion-gate tests**

Create `tests/runtime/test_completion_gate.py` for:
- missing required evidence blocks completion
- missing required tests blocks completion
- phase not equal to `verify` blocks completion
- changed file outside `allowedPaths` blocks completion
- valid payload passes

```python
def test_completion_gate_rejects_missing_tests():
    from runtime.gates.completion import evaluate_completion_gate

    task = {
        "phase": "verify",
        "requiredEvidence": ["state-update"],
        "requiredTests": ["python3 -m pytest tests/runtime/test_task_contract.py -q"],
        "allowedPaths": ["runtime/"],
    }
    payload = {
        "evidenceIds": ["state-update"],
        "testsRun": [],
        "changedFiles": ["runtime/common/models.py"],
    }

    result = evaluate_completion_gate(task, payload)

    assert result["passed"] is False
    assert "required tests" in result["reason"]
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python3 -m pytest tests/runtime/test_completion_gate.py -q`
Expected: FAIL because `runtime.gates.completion` does not exist yet

- [ ] **Step 3: Implement the completion gate**

In `runtime/gates/completion.py`, implement:
- `evaluate_completion_gate(task: dict, payload: dict) -> dict`
- checks for `phase == "verify"`
- required evidence coverage
- required tests coverage
- allowed-path enforcement
- fail-closed reason list

Return a shape similar to existing gates:

```python
{
    "passed": False,
    "reason": "missing required tests",
    "violations": [...],
}
```

- [ ] **Step 4: Make progress runtime require structured evidence**

Modify `scripts/progress_task_runtime.py` to accept new CLI fields:
- `--changed-file` repeated
- `--test-run` repeated
- `--evidence-id` repeated
- `--phase`
- `--turn-delta`

Rules:
- reject progress if none of `changed-file`, `test-run`, or `evidence-id` is provided
- increment `turnCount`
- reject progress when `turnCount > maxTurns`
- persist `phase`

- [ ] **Step 5: Make close runtime fail closed**

Modify `scripts/close_task_runtime.py` so close only succeeds when:
- task is `taskLevel == "leaf"`
- `phase == "verify"`
- completion gate passes

Do not archive on failure. Emit a clear error with missing requirements.

- [ ] **Step 6: Update script-level regression tests**

Update `scripts/test_progress_task_runtime.py` to pass at least one `--evidence-id` and one `--changed-file`, and add a negative case for evidence-free progress.

Update `scripts/test_close_task_runtime.py` into two cases:
- one expected failure when contract requirements are incomplete
- one expected success after valid progress data has been written

- [ ] **Step 7: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_completion_gate.py -q`
Run: `python3 scripts/test_progress_task_runtime.py`
Run: `python3 scripts/test_close_task_runtime.py`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add runtime/gates/completion.py scripts/progress_task_runtime.py scripts/close_task_runtime.py tests/runtime/test_completion_gate.py scripts/test_progress_task_runtime.py scripts/test_close_task_runtime.py
git commit -m "feat: enforce structured progress and fail-closed completion"
```

## Task 3: Add Single-Leaf Execution Lock to Scheduling

**Files:**
- Modify: `runtime/scheduling/next_task.py`
- Modify: `tests/runtime/test_next_task.py`
- Test: `tests/runtime/test_execution_lock.py`

- [ ] **Step 1: Write the failing scheduler-lock tests**

Create `tests/runtime/test_execution_lock.py` covering:
- current active leaf task wins over sibling todo tasks
- parent tasks are never scheduled ahead of an open leaf task
- blocked current leaf returns a blocked/continue decision instead of switching siblings

```python
def test_choose_next_task_stays_on_open_leaf():
    from runtime.scheduling.next_task import choose_next_task

    tasks = [
        {"taskId": "0.1", "status": "doing", "taskLevel": "leaf", "phase": "implement", "priority": "P0", "dependencies": [], "override": "none", "kind": "real", "executionMode": "live", "eligibleForScheduling": True, "isPrimaryTrack": True, "updatedAt": "2026-04-07T10:00:00"},
        {"taskId": "0.2", "status": "todo", "taskLevel": "leaf", "phase": "analyze", "priority": "P0", "dependencies": [], "override": "none", "kind": "real", "executionMode": "live", "eligibleForScheduling": True, "isPrimaryTrack": True, "updatedAt": "2026-04-07T10:01:00"},
    ]

    result = choose_next_task(tasks)

    assert result["nextTaskId"] == "0.1"
    assert result["decisionType"] == "continue-current-leaf"
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python3 -m pytest tests/runtime/test_execution_lock.py -q`
Expected: FAIL because the scheduler does not yet know about `taskLevel` or leaf-lock semantics

- [ ] **Step 3: Implement the leaf lock**

Modify `runtime/scheduling/next_task.py` to:
- normalize `taskLevel` and `phase`
- prefer active leaf tasks before any other candidate
- return a distinct decision for open leaf tasks, such as `continue-current-leaf`
- refuse to switch to a sibling when a current leaf is still `doing` or `blocked`

Keep existing priority sorting as fallback once there is no open leaf task.

- [ ] **Step 4: Extend scheduler tests**

Update `tests/runtime/test_next_task.py` so existing fixtures include `taskLevel` and verify backward-compatible behavior for legacy tasks.

- [ ] **Step 5: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_next_task.py tests/runtime/test_execution_lock.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add runtime/scheduling/next_task.py tests/runtime/test_next_task.py tests/runtime/test_execution_lock.py
git commit -m "feat: enforce single-leaf execution lock in scheduler"
```

## Task 4: Detect Weak Progress and Escalate Instead of Spinning

**Files:**
- Modify: `runtime/supervision/core.py`
- Modify: `tests/runtime/test_supervision_core.py`
- Test: `tests/runtime/test_stall_guard.py`

- [ ] **Step 1: Write the failing stall-guard tests**

Create `tests/runtime/test_stall_guard.py` to cover:
- no new evidence for the threshold window marks `weak_progress`
- no new test runs for the threshold window contributes to weak progress
- phase unchanged plus no evidence triggers resume/handoff preparation
- fresh evidence resets the weak-progress counter

```python
def test_supervision_marks_weak_progress_when_no_evidence_delta(tmp_path):
    from runtime.supervision.core import judge_progress

    task = {"taskId": "real-0-1", "latestResult": "still working", "phase": "implement"}

    verdict = judge_progress(task, tmp_path)

    assert verdict["allowed"] is False
    assert verdict["reason"] in {"weak-progress", "empty-latest-result", "stale-heartbeat"}
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python3 -m pytest tests/runtime/test_stall_guard.py -q`
Expected: FAIL because supervision does not yet inspect evidence/test/phase deltas

- [ ] **Step 3: Teach supervision to inspect real deltas**

Modify `runtime/supervision/core.py` so `judge_progress(...)` also checks:
- whether new evidence ledger entries appeared since last supervision update
- whether `turnCount` increased without evidence/test/phase change
- whether `phase` has remained unchanged across repeated ticks

Map those conditions to a normalized rejection reason:
- `weak-progress`

- [ ] **Step 4: Escalate weak progress fail-closed**

When `handle_supervision_trigger(..., "on_task_changed")` or interval supervision sees `weak-progress`:
- route through the existing failure pipeline
- mark supervision state as blocked or resume-prepared
- record evidence
- emit an event
- do not silently keep the task in a healthy active state

- [ ] **Step 5: Extend supervision tests**

Update `tests/runtime/test_supervision_core.py` to assert emitted event payload includes the failure class and that weak-progress changes the supervision status.

- [ ] **Step 6: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_supervision_core.py tests/runtime/test_stall_guard.py -q`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add runtime/supervision/core.py tests/runtime/test_supervision_core.py tests/runtime/test_stall_guard.py
git commit -m "feat: stop weak-progress task spinning in supervision"
```

## Task 5: Verify End-to-End Leaf Closure Behavior

**Files:**
- Modify: `scripts/test_ingest_real_task.py`
- Modify: `scripts/test_progress_task_runtime.py`
- Modify: `scripts/test_close_task_runtime.py`
- Modify: `scripts/verify_standard_runtime_bundle.py`

- [ ] **Step 1: Add a full happy-path script sequence**

Extend the existing script tests so one end-to-end path proves:
- ingest creates a contract
- progress writes evidence/test/phase updates
- scheduler stays on the same leaf
- close succeeds only after verification data is present

- [ ] **Step 2: Add one explicit failure path**

Add a script-level scenario where the user tries to close a task from `implement` phase or without enough evidence, and assert that:
- the command exits non-zero
- the task remains unarchived
- the reason is visible in stdout/stderr or result markdown

- [ ] **Step 3: Update the standard bundle verification**

Modify `scripts/verify_standard_runtime_bundle.py` so the standard verification path runs the strengthened ingest/progress/close tests.

- [ ] **Step 4: Run final verification**

Run: `python3 -m pytest tests/runtime/test_task_contract.py tests/runtime/test_completion_gate.py tests/runtime/test_execution_lock.py tests/runtime/test_stall_guard.py tests/runtime/test_next_task.py tests/runtime/test_supervision_core.py -q`

Run:

```bash
python3 scripts/test_ingest_real_task.py
python3 scripts/test_progress_task_runtime.py
python3 scripts/test_close_task_runtime.py
python3 scripts/verify_standard_runtime_bundle.py
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/test_ingest_real_task.py scripts/test_progress_task_runtime.py scripts/test_close_task_runtime.py scripts/verify_standard_runtime_bundle.py
git commit -m "test: verify leaf-task closure enforcement end to end"
```

## Notes for the Implementer

- Do not import Claude Code's full query loop. This plan intentionally keeps `wlcc` as a control plane.
- Treat "three-piece evidence" as a useful default, not a universal truth. The contract is the source of truth.
- Fail closed when task requirements are ambiguous. If a leaf task does not have a usable contract, reject progress/close and force repair rather than guessing.
- Preserve backward compatibility for legacy task JSON wherever practical, but do not allow legacy ambiguity to bypass new gates for newly ingested real tasks.
