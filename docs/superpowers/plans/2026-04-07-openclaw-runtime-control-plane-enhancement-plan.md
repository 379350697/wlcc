# OpenClaw Runtime Control Plane Enhancement Implementation Plan

> **For agentic workers:** Implement this plan task-by-task and keep the work split into small, reviewable steps. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a lightweight runtime control plane to `wlcc` that improves long-chain stability, failure handling, context discipline, and execution evidence without turning the project into a second agent shell.

**Architecture:** Build the enhancement around five small runtime additions: action registry, lifecycle events, failure pipeline, context budget control, and execution evidence ledger. Integrate them into existing `runtime/` modules incrementally so each stage is testable and can prove logic or stability gains before becoming part of the standard verification path.

**Tech Stack:** Python 3, pytest, existing `runtime/` package, existing `scripts/` wrappers, JSON state artifacts under `.agent/state/`

---

## File Structure

### New files

- `runtime/actions/__init__.py`
- `runtime/actions/registry.py`
- `runtime/events/__init__.py`
- `runtime/events/models.py`
- `runtime/events/bus.py`
- `runtime/failure/__init__.py`
- `runtime/failure/models.py`
- `runtime/failure/classifier.py`
- `runtime/failure/pipeline.py`
- `runtime/context/__init__.py`
- `runtime/context/budget.py`
- `runtime/context/package.py`
- `runtime/evidence/__init__.py`
- `runtime/evidence/models.py`
- `runtime/evidence/ledger.py`
- `tests/runtime/test_action_registry.py`
- `tests/runtime/test_events.py`
- `tests/runtime/test_failure_pipeline.py`
- `tests/runtime/test_context_budget.py`
- `tests/runtime/test_evidence_ledger.py`
- `scripts/test_control_plane_smoke.py`

### Existing files to modify

- `runtime/harness/registry.py`
- `runtime/harness/task_harness.py`
- `runtime/gates/progress.py`
- `runtime/gates/delivery.py`
- `runtime/gates/risk.py`
- `runtime/resume/context.py`
- `runtime/resume/service.py`
- `runtime/supervision/core.py`
- `runtime/common/models.py`
- `scripts/verify_standard_runtime_bundle.py`
- `STANDARD_RUNTIME_BUNDLE.md`

### Existing tests to extend when useful

- `tests/runtime/test_harness.py`
- `tests/runtime/test_gates.py`
- `tests/runtime/test_resume_service.py`
- `tests/runtime/test_supervision_core.py`

## Task 1: Normalize Runtime Actions Into an Action Registry

**Files:**
- Create: `runtime/actions/__init__.py`
- Create: `runtime/actions/registry.py`
- Modify: `runtime/harness/registry.py`
- Modify: `runtime/harness/task_harness.py`
- Modify: `tests/runtime/test_harness.py`
- Test: `tests/runtime/test_action_registry.py`

- [x] **Step 1: Write the failing registry coverage test**

Create `tests/runtime/test_action_registry.py` with checks for:
- action lookup by name
- fail-closed unknown action defaults
- structured fields like `category`, `risk_action`, and `evidence_policy`

- [x] **Step 2: Run the new test to confirm it fails**

Run: `python3 -m pytest tests/runtime/test_action_registry.py -q`
Expected: FAIL because `runtime.actions.registry` does not exist yet

- [x] **Step 3: Implement `ActionSpec` and registry lookup**

In `runtime/actions/registry.py`, define:
- `ActionSpec`
- registry defaults
- normalized lookup helpers
- listing helpers for concurrent-safe and state-modifying actions

Keep the data sourced from the existing `runtime/harness/registry.py` semantics so behavior does not change yet.

- [x] **Step 4: Add a compatibility bridge in `runtime/harness/registry.py`**

Refactor `runtime/harness/registry.py` into a thin compatibility wrapper that delegates to `runtime.actions.registry`.

- [x] **Step 5: Update `TaskHarness` to read normalized action metadata**

Modify `runtime/harness/task_harness.py` so `TrackedStep.meta` and partition logic use normalized `ActionSpec`-derived data rather than raw registry dict assumptions.

- [x] **Step 6: Extend harness tests to assert no behavior regression**

Update `tests/runtime/test_harness.py` so it validates:
- suffix/path normalization still works
- concurrent grouping still behaves the same
- `TrackedStep` metadata stays fail-closed for unknown actions

- [x] **Step 7: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_action_registry.py tests/runtime/test_harness.py -q`
Expected: PASS

- [x] **Step 8: Commit**

```bash
git add runtime/actions runtime/harness/registry.py runtime/harness/task_harness.py tests/runtime/test_action_registry.py tests/runtime/test_harness.py
git commit -m "feat: normalize runtime actions with shared registry"
```

## Task 2: Add a Lightweight Runtime Lifecycle Event Bus

**Files:**
- Create: `runtime/events/__init__.py`
- Create: `runtime/events/models.py`
- Create: `runtime/events/bus.py`
- Modify: `runtime/supervision/core.py`
- Modify: `runtime/harness/task_harness.py`
- Test: `tests/runtime/test_events.py`
- Test: `tests/runtime/test_supervision_core.py`

- [x] **Step 1: Write the failing event bus test**

Create `tests/runtime/test_events.py` to cover:
- synchronous publish/subscribe
- event ordering
- event payload preservation
- no-op behavior when there are no subscribers

- [x] **Step 2: Run the test to confirm it fails**

Run: `python3 -m pytest tests/runtime/test_events.py -q`
Expected: FAIL because `runtime.events` does not exist yet

- [x] **Step 3: Implement event model and in-process bus**

In `runtime/events/models.py` and `runtime/events/bus.py`, add:
- `RuntimeEvent`
- simple local bus
- subscriber registration
- publish helper

Keep dispatch synchronous and cheap.

- [x] **Step 4: Emit runtime events from `TaskHarness`**

Modify `runtime/harness/task_harness.py` to emit events for:
- step queued
- step started
- step completed
- step failed
- consistency check result

- [x] **Step 5: Emit transition events from supervision**

Modify `runtime/supervision/core.py` to emit events for:
- task ingested
- task changed
- interruption detected
- interval tick
- completion handoff

- [x] **Step 6: Extend supervision tests**

Update `tests/runtime/test_supervision_core.py` so at least one supervision path asserts that an event is emitted with the right `event_type` and `task_id`.

- [x] **Step 7: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_events.py tests/runtime/test_supervision_core.py tests/runtime/test_harness.py -q`
Expected: PASS

- [x] **Step 8: Commit**

```bash
git add runtime/events runtime/harness/task_harness.py runtime/supervision/core.py tests/runtime/test_events.py tests/runtime/test_supervision_core.py tests/runtime/test_harness.py
git commit -m "feat: add runtime lifecycle event bus"
```

## Task 3: Introduce Failure Classification and Degradation Decisions

**Files:**
- Create: `runtime/failure/__init__.py`
- Create: `runtime/failure/models.py`
- Create: `runtime/failure/classifier.py`
- Create: `runtime/failure/pipeline.py`
- Modify: `runtime/gates/progress.py`
- Modify: `runtime/gates/delivery.py`
- Modify: `runtime/gates/risk.py`
- Modify: `runtime/supervision/core.py`
- Test: `tests/runtime/test_failure_pipeline.py`
- Modify: `tests/runtime/test_gates.py`

- [x] **Step 1: Write the failing failure-pipeline tests**

Create `tests/runtime/test_failure_pipeline.py` for:
- progress weakness maps to `content_weak`
- low evidence maps to `evidence_insufficient`
- risk rejection maps to `risk_blocked`
- stale heartbeat maps to `heartbeat_stale`
- failure classes resolve to one normalized degradation action

- [x] **Step 2: Run the new tests to confirm they fail**

Run: `python3 -m pytest tests/runtime/test_failure_pipeline.py -q`
Expected: FAIL because `runtime.failure` does not exist yet

- [x] **Step 3: Implement failure models and classifier**

In `runtime/failure/models.py` and `runtime/failure/classifier.py`, define:
- failure classes
- normalized verdict shape
- mapping helpers from gate outputs to failure types

- [x] **Step 4: Implement degradation decision pipeline**

In `runtime/failure/pipeline.py`, define deterministic routing from failure class to:
- retry
- reorder
- degrade_continue
- freeze_task
- prepare_resume
- handoff
- escalate_human

Do not mutate task state in this file yet; only return structured decisions.

- [x] **Step 5: Upgrade gate outputs to structured verdicts**

Modify:
- `runtime/gates/progress.py`
- `runtime/gates/delivery.py`
- `runtime/gates/risk.py`

so they still preserve current `passed/reason` compatibility but also expose enough data for failure classification.

- [x] **Step 6: Route supervision through the failure pipeline**

Modify `runtime/supervision/core.py` so covered rejection cases are classified and normalized through the pipeline before supervision decides the next runtime reaction.

- [x] **Step 7: Extend gate tests**

Update `tests/runtime/test_gates.py` to assert structured verdict content exists without breaking current gate semantics.

- [x] **Step 8: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_failure_pipeline.py tests/runtime/test_gates.py tests/runtime/test_supervision_core.py -q`
Expected: PASS

- [x] **Step 9: Commit**

```bash
git add runtime/failure runtime/gates/progress.py runtime/gates/delivery.py runtime/gates/risk.py runtime/supervision/core.py tests/runtime/test_failure_pipeline.py tests/runtime/test_gates.py tests/runtime/test_supervision_core.py
git commit -m "feat: normalize runtime failures and degradation decisions"
```

## Task 4: Add Context Budget and Resume Packaging Discipline

**Files:**
- Create: `runtime/context/__init__.py`
- Create: `runtime/context/budget.py`
- Create: `runtime/context/package.py`
- Modify: `runtime/resume/context.py`
- Modify: `runtime/resume/service.py`
- Test: `tests/runtime/test_context_budget.py`
- Modify: `tests/runtime/test_resume_service.py`

- [x] **Step 1: Write the failing context budget tests**

Create `tests/runtime/test_context_budget.py` for:
- source priority stays facts > task_state > summary > chat
- canonical JSON is retained ahead of markdown sidecars
- large summary/log payloads are clipped deterministically
- degraded fallback is still surfaced in metadata

- [x] **Step 2: Run the new tests to confirm they fail**

Run: `python3 -m pytest tests/runtime/test_context_budget.py -q`
Expected: FAIL because `runtime.context` does not exist yet

- [x] **Step 3: Implement budget helpers**

In `runtime/context/budget.py`, add helpers for:
- char budget clipping
- tail clipping
- deduplication by source role
- deterministic trimming order

- [x] **Step 4: Implement a context packager**

In `runtime/context/package.py`, add the packaging function that:
- consumes prioritized source buckets
- applies budget control
- returns a normalized payload plus packaging metadata

- [x] **Step 5: Upgrade resume context collection**

Modify `runtime/resume/context.py` so it still gathers the same sources but routes output through the new packager.

- [x] **Step 6: Upgrade resume service to use packaged context**

Modify `runtime/resume/service.py` so `resume_task_payload()` and related flows include bounded context payloads without changing the existing top-level contract shape more than necessary.

- [x] **Step 7: Extend resume tests**

Update `tests/runtime/test_resume_service.py` to assert:
- packaged context remains prioritized
- payload remains bounded under noisy summaries
- real task metadata survives trimming

- [x] **Step 8: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_context_budget.py tests/runtime/test_resume_service.py -q`
Expected: PASS

- [x] **Step 9: Commit**

```bash
git add runtime/context runtime/resume/context.py runtime/resume/service.py tests/runtime/test_context_budget.py tests/runtime/test_resume_service.py
git commit -m "feat: add bounded context packaging for resume flows"
```

## Task 5: Build an Execution Evidence Ledger and Use It in Delivery Logic

**Files:**
- Create: `runtime/evidence/__init__.py`
- Create: `runtime/evidence/models.py`
- Create: `runtime/evidence/ledger.py`
- Modify: `runtime/gates/delivery.py`
- Modify: `runtime/supervision/core.py`
- Modify: `runtime/common/models.py`
- Test: `tests/runtime/test_evidence_ledger.py`
- Modify: `tests/runtime/test_gates.py`
- Modify: `tests/runtime/test_supervision_core.py`

- [x] **Step 1: Write the failing evidence-ledger tests**

Create `tests/runtime/test_evidence_ledger.py` for:
- append normalized evidence items
- persist under `.agent/state/evidence/<task-id>.json`
- preserve compact evidence facts instead of raw output dumps
- support multiple evidence types for one task

- [x] **Step 2: Run the new tests to confirm they fail**

Run: `python3 -m pytest tests/runtime/test_evidence_ledger.py -q`
Expected: FAIL because `runtime.evidence` does not exist yet

- [x] **Step 3: Implement evidence models and ledger storage**

In `runtime/evidence/models.py` and `runtime/evidence/ledger.py`, add:
- evidence item structure
- append/read helpers
- compact serialization
- ledger file path resolution

- [x] **Step 4: Record evidence from supervision and harness outcomes**

Modify `runtime/supervision/core.py` to append evidence for:
- heartbeat emits
- supervision verdicts
- handoff preparation

If needed, add a small helper in `runtime/common/models.py` for shared evidence typing.

- [x] **Step 5: Update delivery gate to read from the ledger**

Modify `runtime/gates/delivery.py` so it still supports current heuristics, but prefers normalized ledger evidence when available.

- [x] **Step 6: Extend gate and supervision tests**

Update:
- `tests/runtime/test_gates.py`
- `tests/runtime/test_supervision_core.py`

to assert that delivery can pass or fail based on ledger-backed evidence rather than only ad hoc file probing.

- [x] **Step 7: Run focused tests**

Run: `python3 -m pytest tests/runtime/test_evidence_ledger.py tests/runtime/test_gates.py tests/runtime/test_supervision_core.py -q`
Expected: PASS

- [x] **Step 8: Commit**

```bash
git add runtime/evidence runtime/gates/delivery.py runtime/supervision/core.py runtime/common/models.py tests/runtime/test_evidence_ledger.py tests/runtime/test_gates.py tests/runtime/test_supervision_core.py
git commit -m "feat: add execution evidence ledger for delivery decisions"
```

## Task 6: Wire the Control Plane Into the Standard Verification Path

**Files:**
- Create: `scripts/test_control_plane_smoke.py`
- Modify: `scripts/verify_standard_runtime_bundle.py`
- Modify: `STANDARD_RUNTIME_BUNDLE.md`
- Modify: `tests/runtime/test_harness.py`
- Modify: `tests/runtime/test_gates.py`
- Modify: `tests/runtime/test_resume_service.py`
- Modify: `tests/runtime/test_supervision_core.py`

- [x] **Step 1: Write the failing control-plane smoke test**

Create `scripts/test_control_plane_smoke.py` to verify, in one small scenario:
- action lookup works
- an event is emitted
- a failure verdict is classified
- context packaging stays bounded
- evidence ledger is written

- [x] **Step 2: Run the smoke test to confirm it fails**

Run: `python3 scripts/test_control_plane_smoke.py`
Expected: FAIL until the new modules are fully wired

- [x] **Step 3: Add the smoke test to the standard verification bundle**

Modify `scripts/verify_standard_runtime_bundle.py` to include the new smoke test before the broader bundle checks.

- [x] **Step 4: Document the new runtime guarantees**

Update `STANDARD_RUNTIME_BUNDLE.md` with:
- new control plane modules
- bounded cost expectations
- new verification coverage
- explicit note that this remains OpenClaw-serving infrastructure, not a second agent shell

- [x] **Step 5: Run the full runtime tests**

Run: `python3 -m pytest tests/runtime -q`
Expected: PASS

- [x] **Step 6: Run the full standard verification bundle**

Run: `python3 scripts/verify_standard_runtime_bundle.py`
Expected: PASS and write `tests/STANDARD_RUNTIME_BUNDLE_VERIFICATION.md`

- [x] **Step 7: Review runtime cost impact**

Compare before and after wall time for:
- `python3 -m pytest tests/runtime -q`
- `python3 scripts/verify_standard_runtime_bundle.py`

Expected:
- no permanent background process added
- no remote calls added
- verification wall time regression stays modest

- [x] **Step 8: Commit**

```bash
git add scripts/test_control_plane_smoke.py scripts/verify_standard_runtime_bundle.py STANDARD_RUNTIME_BUNDLE.md tests/runtime
git commit -m "test: verify runtime control plane in standard bundle"
```

## Task 7: Final Integration Check and Release Readiness Review

**Files:**
- Modify: `docs/superpowers/specs/2026-04-07-openclaw-runtime-control-plane-enhancement-spec.md`
- Modify: `docs/superpowers/plans/2026-04-07-openclaw-runtime-control-plane-enhancement-plan.md`
- Test: `tests/STANDARD_RUNTIME_BUNDLE_VERIFICATION.md`

- [x] **Step 1: Re-read the spec and confirm each enhancement is implemented**

Check the spec against code and mark any deferred pieces directly in the spec if needed.

- [x] **Step 2: Re-read this plan and mark any plan drift**

Update only if implementation revealed a necessary simplification or file-path change.

- [x] **Step 3: Run the final verification commands**

Run:
- `python3 -m pytest tests/runtime -q`
- `python3 scripts/verify_standard_runtime_bundle.py`

Expected: PASS

- [x] **Step 4: Summarize measurable improvements**

Record:
- which paths now use shared action metadata
- which transitions emit events
- which failures route through the pipeline
- whether context payloads are now bounded
- whether delivery can reason from ledger evidence

- [x] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-04-07-openclaw-runtime-control-plane-enhancement-spec.md docs/superpowers/plans/2026-04-07-openclaw-runtime-control-plane-enhancement-plan.md tests/STANDARD_RUNTIME_BUNDLE_VERIFICATION.md
git commit -m "docs: finalize control plane enhancement rollout notes"
```

## Notes for Execution

- Keep all new behavior fail-closed and compatibility-aware.
- Prefer additive contracts before replacing old return shapes.
- Do not move sidecar responsibilities back onto the sync path.
- If any task cannot prove logic gain or bounded cost, stop and trim the implementation.
- If a task balloons, split it before coding rather than widening the PR.
