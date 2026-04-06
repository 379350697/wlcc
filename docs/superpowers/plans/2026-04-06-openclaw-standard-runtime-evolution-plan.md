# OpenClaw Standard Runtime Evolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将当前“总 Skill + scripts 基建层”的实现演进为“统一入口 + runtime 内核 + sidecar 外环”的标准运行版，在不削弱 OpenClaw 执行增强能力的前提下，显著降低主链同步 IO、重复 subprocess 和全量重建开销。

**Architecture:** 保留 `skills/long-chain-autonomy/` 和 `scripts/*.py` 作为稳定入口，将核心能力下沉到 `runtime/` 包，在线主链仅保留任务推进、上下文检索、next-task、gate、harness、canonical state、resume/supervision 最小刷新。Markdown 视图、dashboard、summary、一致性全量扫描迁移到 sidecar 服务并按需触发。

**Tech Stack:** Python 3, stdlib (`argparse`, `json`, `pathlib`, `dataclasses`), `pytest`, existing Markdown/JSON state files, current Skill-based OpenClaw integration

---

## Implementation Status Snapshot

- `Task 1` Bootstrap runtime package: completed
- `Task 2` Extract common helpers: completed
- `Task 3` Move canonical state and lifecycle: completed
- `Task 4` Split next-task core from sidecar packaging: completed
- `Task 5` Extract context and resume-state builders: completed
- `Task 6` Build runtime resume service: completed
- `Task 7` Move delivery/progress/risk checks: completed
- `Task 8` Runtime-ize harness: completed
- `Task 9` Split supervision core and sidecar actions: completed
- `Task 10` Move Markdown task/resume views into sidecar services: completed
- `Task 11` Move heartbeat summary and observability off the main path: completed
- `Task 12` Rewrite critical CLIs as runtime wrappers: completed
- `Task 13` Add pytest-based runtime regression coverage: completed
- `Task 14` Update deployment docs for standard runtime bundle: completed
- `Task 15` Final verification for evolved standard runtime: completed

Current verification entrypoint:

```bash
python3 scripts/verify_standard_runtime_bundle.py
```

Artifacts added during implementation:
- `runtime/`
- `tests/runtime/`
- `STANDARD_RUNTIME_BUNDLE.md`
- `tests/STANDARD_RUNTIME_BUNDLE_VERIFICATION.md`

---

## File Structure Map

### New runtime package

- Create: `runtime/__init__.py`
- Create: `runtime/common/__init__.py`
- Create: `runtime/common/paths.py`
- Create: `runtime/common/io.py`
- Create: `runtime/common/time.py`
- Create: `runtime/common/logging.py`
- Create: `runtime/common/models.py`
- Create: `runtime/state/__init__.py`
- Create: `runtime/state/store.py`
- Create: `runtime/state/lifecycle.py`
- Create: `runtime/state/render_views.py`
- Create: `runtime/scheduling/__init__.py`
- Create: `runtime/scheduling/next_task.py`
- Create: `runtime/resume/__init__.py`
- Create: `runtime/resume/context.py`
- Create: `runtime/resume/resume_state.py`
- Create: `runtime/resume/resume_service.py`
- Create: `runtime/gates/__init__.py`
- Create: `runtime/gates/delivery.py`
- Create: `runtime/gates/progress.py`
- Create: `runtime/gates/risk.py`
- Create: `runtime/harness/__init__.py`
- Create: `runtime/harness/registry.py`
- Create: `runtime/harness/task_harness.py`
- Create: `runtime/supervision/__init__.py`
- Create: `runtime/supervision/core.py`
- Create: `runtime/supervision/heartbeat.py`
- Create: `runtime/sidecar/__init__.py`
- Create: `runtime/sidecar/heartbeat_summary.py`
- Create: `runtime/sidecar/observability.py`
- Create: `runtime/sidecar/tasks_view.py`

### CLI wrappers to thin out

- Modify: `scripts/tool_registry.py`
- Modify: `scripts/tool_harness.py`
- Modify: `scripts/write_state_store.py`
- Modify: `scripts/update_task_lifecycle.py`
- Modify: `scripts/render_state_views.py`
- Modify: `scripts/decide_next_task_v2.py`
- Modify: `scripts/build_next_task_from_state.py`
- Modify: `scripts/read_project_context.py`
- Modify: `scripts/retrieve_context.py`
- Modify: `scripts/build_resume_state.py`
- Modify: `scripts/resume_task.py`
- Modify: `scripts/resume_real_task.py`
- Modify: `scripts/delivery_gate.py`
- Modify: `scripts/progress_reply_gate.py`
- Modify: `scripts/evaluate_risk_policy.py`
- Modify: `scripts/check_risk_level.py`
- Modify: `scripts/run_task_supervision.py`
- Modify: `scripts/emit_heartbeat.py`
- Modify: `scripts/build_heartbeat_summary.py`
- Modify: `scripts/build_observability_dashboard.py`
- Modify: `scripts/ingest_real_task.py`
- Modify: `scripts/progress_task_runtime.py`
- Modify: `scripts/close_task_runtime.py`
- Modify: `scripts/check_state_view_consistency.py`

### Test and tooling

- Create: `pyproject.toml`
- Create: `tests/runtime/test_common_io.py`
- Create: `tests/runtime/test_state_store.py`
- Create: `tests/runtime/test_next_task.py`
- Create: `tests/runtime/test_resume_service.py`
- Create: `tests/runtime/test_gates.py`
- Create: `tests/runtime/test_harness.py`
- Create: `tests/runtime/test_supervision_core.py`
- Create: `tests/runtime/test_sidecar_split.py`
- Modify: `tests/README.md`

### Docs and deployment

- Modify: `README.md`
- Modify: `README_DEPLOY.md`
- Modify: `UNIFIED_SKILL_DEPLOYMENT.md`
- Modify: `QUICK_DEPLOY_AND_USE.md`
- Create: `STANDARD_RUNTIME_BUNDLE.md`

## Runtime design rules

- Canonical state remains the source of truth under `.agent/state/`.
- `next-task.json` stays synchronous and mandatory.
- `NEXT_TASK.md`, `.agent/tasks/*.md`, `.agent/resume/*.md`, dashboard, heartbeat summary become sidecar outputs.
- Core services expose Python APIs first; CLI files only parse args and print results.
- Online path must avoid internal `subprocess.run` except for true external process boundaries.
- Sidecar work must be callable inline for tests and optionally deferred by policy.

## Task 1: Bootstrap the runtime package and shared path model

**Files:**
- Create: `runtime/__init__.py`
- Create: `runtime/common/__init__.py`
- Create: `runtime/common/paths.py`
- Create: `runtime/common/models.py`
- Modify: `scripts/tool_registry.py`
- Test: `tests/runtime/test_common_io.py`

- [ ] **Step 1: Create the runtime package directories and empty `__init__.py` files**

Run: `mkdir -p runtime/common runtime/state runtime/scheduling runtime/resume runtime/gates runtime/harness runtime/supervision runtime/sidecar tests/runtime`
Expected: directories exist with no errors

- [ ] **Step 2: Implement a shared path container in `runtime/common/paths.py`**

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class RuntimePaths:
    root: Path

    @property
    def state_dir(self) -> Path:
        return self.root / ".agent" / "state"

    @property
    def tasks_state_dir(self) -> Path:
        return self.state_dir / "tasks"
```

- [ ] **Step 3: Define core dataclasses in `runtime/common/models.py`**

```python
from dataclasses import dataclass, field

@dataclass
class TaskState:
    taskId: str
    project: str
    goal: str
    status: str
    priority: str = "P2"
    dependencies: list[str] = field(default_factory=list)
```

- [ ] **Step 4: Add a tiny test that imports the new package and asserts path resolution**

```python
from pathlib import Path
from runtime.common.paths import RuntimePaths

def test_runtime_paths_resolve_state_dirs(tmp_path: Path):
    paths = RuntimePaths(tmp_path)
    assert paths.tasks_state_dir == tmp_path / ".agent" / "state" / "tasks"
```

- [ ] **Step 5: Run the new test**

Run: `python3 -m pytest tests/runtime/test_common_io.py -q`
Expected: `1 passed`

- [ ] **Step 6: Update `scripts/tool_registry.py` imports only if needed to avoid path hacks spreading**

Run: `python3 scripts/tool_registry.py`
Expected: registry summary prints normally

- [ ] **Step 7: Commit the bootstrap**

```bash
git add runtime tests/runtime scripts/tool_registry.py
git commit -m "refactor: bootstrap runtime package"
```

## Task 2: Extract common IO, time, logging, and schema helpers

**Files:**
- Create: `runtime/common/io.py`
- Create: `runtime/common/time.py`
- Create: `runtime/common/logging.py`
- Modify: `scripts/progress_task_runtime.py`
- Modify: `scripts/run_task_supervision.py`
- Modify: `scripts/emit_heartbeat.py`
- Modify: `scripts/build_heartbeat_summary.py`
- Test: `tests/runtime/test_common_io.py`

- [ ] **Step 1: Implement shared JSON helpers**

```python
def read_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
```

- [ ] **Step 2: Implement shared time helpers**

```python
def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")
```

- [ ] **Step 3: Implement append-log helper**

```python
def append_line(path: Path, line: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
```

- [ ] **Step 4: Replace duplicate helper implementations in target scripts with imports**

Run: `rg -n "def (load_json|write_json|save_json|now_text|now_iso|append_log)\\(" scripts`
Expected: duplicate helper count decreases materially after edits

- [ ] **Step 5: Add unit tests for JSON round-trip and append-log**

Run: `python3 -m pytest tests/runtime/test_common_io.py -q`
Expected: all tests pass

- [ ] **Step 6: Smoke test three refactored scripts**

Run: `python3 scripts/emit_heartbeat.py --stage demo --current-task demo-task --next-step continue --trigger-reason manual --throttle-seconds 0`
Expected: heartbeat files and test markdown are written successfully

- [ ] **Step 7: Commit**

```bash
git add runtime/common scripts/progress_task_runtime.py scripts/run_task_supervision.py scripts/emit_heartbeat.py scripts/build_heartbeat_summary.py tests/runtime/test_common_io.py
git commit -m "refactor: extract common runtime helpers"
```

## Task 3: Move canonical task state and lifecycle logic into runtime/state

**Files:**
- Create: `runtime/state/store.py`
- Create: `runtime/state/lifecycle.py`
- Modify: `scripts/write_state_store.py`
- Modify: `scripts/update_task_lifecycle.py`
- Modify: `scripts/ingest_real_task.py`
- Modify: `scripts/close_task_runtime.py`
- Test: `tests/runtime/test_state_store.py`

- [ ] **Step 1: Extract `write_state_store` logic into `runtime/state/store.py`**

```python
def write_task_state(paths: RuntimePaths, task: TaskState) -> Path:
    task_path = paths.tasks_state_dir / f"{task.taskId}.json"
    write_json(task_path, asdict(task))
    return task_path
```

- [ ] **Step 2: Extract index maintenance into a dedicated function**

```python
def update_index(paths: RuntimePaths, task_id: str, updated_at: str) -> Path:
    ...
```

- [ ] **Step 3: Extract lifecycle transition table and transition function into `runtime/state/lifecycle.py`**

```python
def transition_lifecycle(task: dict, target: str) -> dict:
    ...
```

- [ ] **Step 4: Convert `scripts/write_state_store.py` and `scripts/update_task_lifecycle.py` into thin wrappers**

Run: `python3 scripts/write_state_store.py --help && python3 scripts/update_task_lifecycle.py --help`
Expected: both CLIs still show usage

- [ ] **Step 5: Add state-store tests for write and lifecycle transition behavior**

Run: `python3 -m pytest tests/runtime/test_state_store.py -q`
Expected: tests pass

- [ ] **Step 6: Run compatibility smoke tests against existing scripts**

Run: `python3 scripts/test_task_lifecycle.py`
Expected: existing lifecycle test still passes

- [ ] **Step 7: Commit**

```bash
git add runtime/state scripts/write_state_store.py scripts/update_task_lifecycle.py scripts/ingest_real_task.py scripts/close_task_runtime.py tests/runtime/test_state_store.py
git commit -m "refactor: move state and lifecycle logic into runtime"
```

## Task 4: Extract synchronous next-task core and split sidecar packaging

**Files:**
- Create: `runtime/scheduling/next_task.py`
- Modify: `scripts/decide_next_task_v2.py`
- Modify: `scripts/build_next_task_from_state.py`
- Modify: `scripts/progress_task_runtime.py`
- Test: `tests/runtime/test_next_task.py`

- [ ] **Step 1: Move normalize/choose logic from CLI into `runtime/scheduling/next_task.py`**

```python
def choose_next_task(tasks: list[dict]) -> dict:
    ...
```

- [ ] **Step 2: Add a `write_next_task_state` helper that writes only `.agent/state/next-task.json`**

```python
def write_next_task_state(paths: RuntimePaths, result: dict) -> Path:
    ...
```

- [ ] **Step 3: Turn `scripts/decide_next_task_v2.py` into wrapper around runtime API**

Run: `python3 scripts/decide_next_task_v2.py --input .agent/state/next-task-input.json --output /tmp/next-task.json`
Expected: output JSON is written

- [ ] **Step 4: Reduce `scripts/build_next_task_from_state.py` responsibility to sidecar packaging only**

```python
def build_next_task_view(result: dict) -> str:
    ...
```

- [ ] **Step 5: Update `scripts/progress_task_runtime.py` to compute and write `next-task.json` inline through API instead of shelling out**

Run: `python3 scripts/test_progress_task_runtime.py`
Expected: test still passes

- [ ] **Step 6: Add tests covering force-run, force-hold, dependency ordering, and sync write**

Run: `python3 -m pytest tests/runtime/test_next_task.py -q`
Expected: all tests pass

- [ ] **Step 7: Commit**

```bash
git add runtime/scheduling scripts/decide_next_task_v2.py scripts/build_next_task_from_state.py scripts/progress_task_runtime.py tests/runtime/test_next_task.py
git commit -m "refactor: split next-task core from sidecar packaging"
```

## Task 5: Extract project-context, retrieval, and resume-state builders

**Files:**
- Create: `runtime/resume/context.py`
- Create: `runtime/resume/resume_state.py`
- Modify: `scripts/read_project_context.py`
- Modify: `scripts/retrieve_context.py`
- Modify: `scripts/build_resume_state.py`
- Test: `tests/runtime/test_resume_service.py`

- [ ] **Step 1: Extract project context source ordering into `runtime/resume/context.py`**

```python
def collect_context_sources(paths: RuntimePaths, task_id: str | None) -> list[dict]:
    ...
```

- [ ] **Step 2: Extract resume target selection into `runtime/resume/resume_state.py`**

```python
def choose_resume_target(task_ids, next_task_state, last_run):
    ...
```

- [ ] **Step 3: Convert context-related scripts into thin wrappers**

Run: `python3 scripts/retrieve_context.py --project-root . --task-id real-task-runtime-mainline`
Expected: JSON output still renders

- [ ] **Step 4: Add tests for source priority and resume target selection**

Run: `python3 -m pytest tests/runtime/test_resume_service.py -q`
Expected: tests pass

- [ ] **Step 5: Verify compatibility with existing retrieval priority test**

Run: `python3 scripts/check_retrieval_priority.py`
Expected: retrieval priority result is generated without regression

- [ ] **Step 6: Commit**

```bash
git add runtime/resume scripts/read_project_context.py scripts/retrieve_context.py scripts/build_resume_state.py tests/runtime/test_resume_service.py
git commit -m "refactor: extract context and resume-state services"
```

## Task 6: Build a real resume service and remove internal subprocess chaining

**Files:**
- Create: `runtime/resume/resume_service.py`
- Modify: `scripts/resume_task.py`
- Modify: `scripts/resume_real_task.py`
- Modify: `scripts/run_task_supervision.py`
- Test: `tests/runtime/test_resume_service.py`

- [ ] **Step 1: Implement a `resume_task_payload` service**

```python
def resume_task_payload(paths: RuntimePaths, task_id: str) -> dict:
    return {
        "task": ...,
        "resumeState": ...,
        "nextTask": ...,
        "sources": ...,
    }
```

- [ ] **Step 2: Implement a `resume_real_task` service that performs lifecycle and supervision refresh through API calls**

```python
def resume_real_task(paths: RuntimePaths, task_id: str) -> dict:
    ...
```

- [ ] **Step 3: Replace subprocess chaining in `scripts/resume_real_task.py` with direct service calls**

Run: `python3 scripts/resume_real_task.py --task-id real-task-runtime-mainline`
Expected: script completes without spawning internal CLI chain

- [ ] **Step 4: Update `run_task_supervision.py` interruption flow to call resume service directly**

Run: `python3 scripts/test_resume_real_task.py`
Expected: compatibility test passes

- [ ] **Step 5: Add unit tests for resume payload composition**

Run: `python3 -m pytest tests/runtime/test_resume_service.py -q`
Expected: tests pass

- [ ] **Step 6: Commit**

```bash
git add runtime/resume/resume_service.py scripts/resume_task.py scripts/resume_real_task.py scripts/run_task_supervision.py tests/runtime/test_resume_service.py
git commit -m "refactor: add runtime resume service"
```

## Task 7: Move delivery, progress, and risk checks into runtime/gates

**Files:**
- Create: `runtime/gates/delivery.py`
- Create: `runtime/gates/progress.py`
- Create: `runtime/gates/risk.py`
- Modify: `scripts/delivery_gate.py`
- Modify: `scripts/progress_reply_gate.py`
- Modify: `scripts/evaluate_risk_policy.py`
- Modify: `scripts/check_risk_level.py`
- Modify: `scripts/update_task_lifecycle.py`
- Modify: `scripts/progress_task_runtime.py`
- Test: `tests/runtime/test_gates.py`

- [ ] **Step 1: Extract delivery evidence collection into a runtime module**

```python
def evaluate_delivery_gate(paths: RuntimePaths, task_id: str, latest_result: str, task_kind: str) -> dict:
    ...
```

- [ ] **Step 2: Normalize heartbeat timestamp handling during extraction**

```python
timestamp_str = hb.get("emittedAt") or hb.get("timestamp") or ""
```

- [ ] **Step 3: Extract progress reply gate into runtime API**

```python
def evaluate_progress_gate(latest_result: str, next_step: str) -> dict:
    ...
```

- [ ] **Step 4: Extract risk policy evaluation helpers into runtime API**

Run: `python3 scripts/test_delivery_gate.py && python3 scripts/test_progress_reply_gate.py`
Expected: both gate tests pass

- [ ] **Step 5: Update online callers to use API instead of spawning gate CLIs**

Run: `python3 scripts/test_progress_task_runtime.py`
Expected: test passes and no internal gate subprocess remains in core path

- [ ] **Step 6: Add gate unit tests for heartbeat field compatibility and file-change evidence**

Run: `python3 -m pytest tests/runtime/test_gates.py -q`
Expected: tests pass

- [ ] **Step 7: Commit**

```bash
git add runtime/gates scripts/delivery_gate.py scripts/progress_reply_gate.py scripts/evaluate_risk_policy.py scripts/check_risk_level.py scripts/update_task_lifecycle.py scripts/progress_task_runtime.py tests/runtime/test_gates.py
git commit -m "refactor: extract runtime gate services"
```

## Task 8: Runtime-ize the harness and remove CLI-to-CLI orchestration from the main path

**Files:**
- Create: `runtime/harness/registry.py`
- Create: `runtime/harness/task_harness.py`
- Modify: `scripts/tool_registry.py`
- Modify: `scripts/tool_harness.py`
- Modify: `scripts/progress_task_runtime.py`
- Test: `tests/runtime/test_harness.py`

- [ ] **Step 1: Move registry data and query helpers into `runtime/harness/registry.py`**

```python
REGISTRY: dict[str, dict] = {...}

def get_meta(script_name: str) -> dict:
    ...
```

- [ ] **Step 2: Move `TrackedStep`, `HarnessResult`, and `TaskHarness` into `runtime/harness/task_harness.py`**

- [ ] **Step 3: Replace `sys.path.insert` imports in current harness scripts with normal package imports**

Run: `python3 scripts/test_tool_harness.py`
Expected: harness tests remain green

- [ ] **Step 4: In `progress_task_runtime.py`, stop adding sidecar work to the synchronous harness queue**

```python
harness.add("update_task_lifecycle", ...)
harness.add("run_task_supervision_core", ...)
```

- [ ] **Step 5: Add tests that assert concurrent groups contain only read-only core-safe steps**

Run: `python3 -m pytest tests/runtime/test_harness.py -q`
Expected: tests pass

- [ ] **Step 6: Commit**

```bash
git add runtime/harness scripts/tool_registry.py scripts/tool_harness.py scripts/progress_task_runtime.py tests/runtime/test_harness.py
git commit -m "refactor: move harness into runtime package"
```

## Task 9: Split supervision into online core and sidecar actions

**Files:**
- Create: `runtime/supervision/core.py`
- Create: `runtime/supervision/heartbeat.py`
- Modify: `scripts/run_task_supervision.py`
- Modify: `scripts/emit_heartbeat.py`
- Modify: `scripts/progress_task_runtime.py`
- Test: `tests/runtime/test_supervision_core.py`

- [ ] **Step 1: Extract judge and supervision state transition logic into `runtime/supervision/core.py`**

```python
def judge_progress(task: dict, paths: RuntimePaths) -> dict:
    ...

def handle_supervision_trigger(task: dict, supervision: dict, trigger: str, paths: RuntimePaths) -> dict:
    ...
```

- [ ] **Step 2: Extract heartbeat emission primitive into `runtime/supervision/heartbeat.py`**

```python
def emit_heartbeat_record(paths: RuntimePaths, payload: dict) -> dict:
    ...
```

- [ ] **Step 3: Keep only minimal heartbeat write in the online trigger path**

Run: `python3 scripts/test_task_supervision.py`
Expected: supervision behavior stays compatible

- [ ] **Step 4: Remove synchronous calls to `build_heartbeat_summary.py` from supervision core**

- [ ] **Step 5: Add unit tests for judge rejection, stale behavior, and trigger transitions**

Run: `python3 -m pytest tests/runtime/test_supervision_core.py -q`
Expected: tests pass

- [ ] **Step 6: Commit**

```bash
git add runtime/supervision scripts/run_task_supervision.py scripts/emit_heartbeat.py scripts/progress_task_runtime.py tests/runtime/test_supervision_core.py
git commit -m "refactor: split supervision core from sidecar work"
```

## Task 10: Move Markdown task/resume views into sidecar-only services

**Files:**
- Create: `runtime/state/render_views.py`
- Create: `runtime/sidecar/tasks_view.py`
- Modify: `scripts/render_state_views.py`
- Modify: `scripts/check_state_view_consistency.py`
- Modify: `scripts/build_next_task_from_state.py`
- Test: `tests/runtime/test_sidecar_split.py`

- [ ] **Step 1: Extract pure rendering functions from `scripts/render_state_views.py` into runtime modules**

```python
def render_task_md(task: dict) -> str: ...
def render_resume_md(task: dict) -> str: ...
def render_tasks_summary(tasks: list[dict]) -> str: ...
```

- [ ] **Step 2: Create a sidecar coordinator that renders views on demand**

```python
def render_task_sidecars(paths: RuntimePaths, task_id: str | None = None) -> list[Path]:
    ...
```

- [ ] **Step 3: Convert `scripts/render_state_views.py` into a thin sidecar wrapper**

Run: `python3 scripts/render_state_views.py --project-root . --task-id real-task-runtime-mainline`
Expected: markdown files are written

- [ ] **Step 4: Reframe `check_state_view_consistency.py` as a sidecar verifier instead of mandatory core invariant**

- [ ] **Step 5: Add tests proving core next-task and state writes succeed without rendering Markdown**

Run: `python3 -m pytest tests/runtime/test_sidecar_split.py -q`
Expected: tests pass

- [ ] **Step 6: Commit**

```bash
git add runtime/state/render_views.py runtime/sidecar/tasks_view.py scripts/render_state_views.py scripts/check_state_view_consistency.py scripts/build_next_task_from_state.py tests/runtime/test_sidecar_split.py
git commit -m "refactor: move markdown views into sidecar services"
```

## Task 11: Move heartbeat summary and observability dashboard fully out of the online path

**Files:**
- Create: `runtime/sidecar/heartbeat_summary.py`
- Create: `runtime/sidecar/observability.py`
- Modify: `scripts/build_heartbeat_summary.py`
- Modify: `scripts/build_observability_dashboard.py`
- Modify: `scripts/run_task_supervision.py`
- Modify: `scripts/progress_task_runtime.py`
- Test: `tests/runtime/test_sidecar_split.py`

- [ ] **Step 1: Extract heartbeat summary builder into sidecar module**

```python
def build_heartbeat_summary(paths: RuntimePaths) -> dict:
    ...
```

- [ ] **Step 2: Extract observability dashboard builder into sidecar module**

```python
def build_observability_dashboard(paths: RuntimePaths) -> dict:
    ...
```

- [ ] **Step 3: Remove direct summary/dashboard generation from online progress and supervision scripts**

Run: `rg -n "build_heartbeat_summary|build_observability_dashboard" scripts/progress_task_runtime.py scripts/run_task_supervision.py`
Expected: no synchronous main-path calls remain

- [ ] **Step 4: Keep CLI wrappers for manual or deferred invocation**

Run: `python3 scripts/build_heartbeat_summary.py && python3 scripts/build_observability_dashboard.py`
Expected: both scripts still produce outputs when called directly

- [ ] **Step 5: Extend sidecar tests to prove main path works without summaries**

Run: `python3 -m pytest tests/runtime/test_sidecar_split.py -q`
Expected: tests pass

- [ ] **Step 6: Commit**

```bash
git add runtime/sidecar scripts/build_heartbeat_summary.py scripts/build_observability_dashboard.py scripts/run_task_supervision.py scripts/progress_task_runtime.py tests/runtime/test_sidecar_split.py
git commit -m "refactor: move heartbeat and observability summaries off the main path"
```

## Task 12: Rewrite the three critical CLIs as true thin wrappers over runtime APIs

**Files:**
- Modify: `scripts/ingest_real_task.py`
- Modify: `scripts/progress_task_runtime.py`
- Modify: `scripts/close_task_runtime.py`
- Modify: `scripts/resume_real_task.py`
- Test: `tests/runtime/test_state_store.py`
- Test: `tests/runtime/test_resume_service.py`

- [ ] **Step 1: Make `scripts/ingest_real_task.py` call runtime state, next-task, and supervision APIs directly**

- [ ] **Step 2: Make `scripts/progress_task_runtime.py` orchestrate only inline core services and enqueue no sidecars**

- [ ] **Step 3: Make `scripts/close_task_runtime.py` share the same runtime services**

- [ ] **Step 4: Re-run existing integration scripts after the wrapper conversion**

Run: `python3 scripts/test_ingest_real_task.py && python3 scripts/test_progress_task_runtime.py && python3 scripts/test_close_task_runtime.py`
Expected: all integration scripts pass

- [ ] **Step 5: Commit**

```bash
git add scripts/ingest_real_task.py scripts/progress_task_runtime.py scripts/close_task_runtime.py scripts/resume_real_task.py
git commit -m "refactor: convert critical CLIs into runtime wrappers"
```

## Task 13: Add pytest-based runtime regression coverage and keep legacy script tests as compatibility smoke tests

**Files:**
- Create: `pyproject.toml`
- Create: `tests/runtime/test_common_io.py`
- Create: `tests/runtime/test_state_store.py`
- Create: `tests/runtime/test_next_task.py`
- Create: `tests/runtime/test_resume_service.py`
- Create: `tests/runtime/test_gates.py`
- Create: `tests/runtime/test_harness.py`
- Create: `tests/runtime/test_supervision_core.py`
- Create: `tests/runtime/test_sidecar_split.py`
- Modify: `tests/README.md`

- [ ] **Step 1: Add minimal `pyproject.toml` with pytest config**

```toml
[tool.pytest.ini_options]
testpaths = ["tests/runtime"]
pythonpath = ["."]
```

- [ ] **Step 2: Ensure each runtime module has at least one direct unit test**

- [ ] **Step 3: Keep selected `scripts/test_*.py` files as compatibility smoke tests, not the primary confidence layer**

- [ ] **Step 4: Document the new test pyramid in `tests/README.md`**

- [ ] **Step 5: Run the runtime test suite**

Run: `python3 -m pytest tests/runtime -q`
Expected: all runtime tests pass

- [ ] **Step 6: Run the key legacy smoke tests**

Run: `python3 scripts/test_tool_harness.py && python3 scripts/test_task_supervision.py && python3 scripts/test_progress_task_runtime.py`
Expected: compatibility scripts still pass

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml tests/runtime tests/README.md
git commit -m "test: add runtime regression suite"
```

## Task 14: Update deployment docs for the new standard runtime bundle

**Files:**
- Modify: `README.md`
- Modify: `README_DEPLOY.md`
- Modify: `UNIFIED_SKILL_DEPLOYMENT.md`
- Modify: `QUICK_DEPLOY_AND_USE.md`
- Create: `STANDARD_RUNTIME_BUNDLE.md`

- [ ] **Step 1: Document the new architecture vocabulary**

Add these terms:
- `entry skill`
- `runtime core`
- `sidecar services`
- `dev-only assets`

- [ ] **Step 2: Update deployment docs to describe which outputs are synchronous vs sidecar**

- [ ] **Step 3: Add a dedicated `STANDARD_RUNTIME_BUNDLE.md` listing what ships in the standard bundle**

- [ ] **Step 4: Verify docs mention that `next-task.json` remains synchronous and mandatory**

Run: `rg -n "next-task.json|sidecar|runtime core|standard bundle" README.md README_DEPLOY.md UNIFIED_SKILL_DEPLOYMENT.md QUICK_DEPLOY_AND_USE.md STANDARD_RUNTIME_BUNDLE.md`
Expected: all concepts appear in docs

- [ ] **Step 5: Commit**

```bash
git add README.md README_DEPLOY.md UNIFIED_SKILL_DEPLOYMENT.md QUICK_DEPLOY_AND_USE.md STANDARD_RUNTIME_BUNDLE.md
git commit -m "docs: describe standard runtime bundle architecture"
```

## Task 15: Final verification for the evolved standard runtime

**Files:**
- Modify: `README_DEPLOY.md`
- Test: `tests/runtime/test_common_io.py`
- Test: `tests/runtime/test_state_store.py`
- Test: `tests/runtime/test_next_task.py`
- Test: `tests/runtime/test_resume_service.py`
- Test: `tests/runtime/test_gates.py`
- Test: `tests/runtime/test_harness.py`
- Test: `tests/runtime/test_supervision_core.py`
- Test: `tests/runtime/test_sidecar_split.py`

- [ ] **Step 1: Run the runtime unit suite**

Run: `python3 -m pytest tests/runtime -q`
Expected: all tests pass

- [ ] **Step 2: Run critical compatibility smoke tests**

Run: `python3 scripts/test_ingest_real_task.py && python3 scripts/test_progress_task_runtime.py && python3 scripts/test_task_supervision.py && python3 scripts/test_resume_real_task.py`
Expected: all pass

- [ ] **Step 3: Run health checks that remain relevant to the standard bundle**

Run: `python3 scripts/system_healthcheck.py && python3 scripts/check_phase2_mainline.py`
Expected: both commands succeed

- [ ] **Step 4: Confirm the online path no longer shells out to sidecar scripts**

Run: `rg -n "subprocess\\.run\\(" scripts/ingest_real_task.py scripts/progress_task_runtime.py scripts/run_task_supervision.py`
Expected: only true external boundaries remain; core-to-core orchestration is removed

- [ ] **Step 5: Confirm the standard bundle still produces mandatory canonical outputs**

Run: `test -f .agent/state/next-task.json && test -d .agent/state/tasks && echo OK`
Expected: `OK`

- [ ] **Step 6: Commit the final verification pass**

```bash
git add .
git commit -m "chore: verify evolved standard runtime bundle"
```

## Notes for implementers

- Do not remove the existing CLI filenames during this plan. Preserve entry compatibility.
- Do not move `.agent/state/next-task.json` off the synchronous path.
- Do not make `retrieve_context`, `resume`, `gates`, or `harness` sidecar-only.
- It is acceptable for `NEXT_TASK.md`, `TASKS.md`, `.agent/tasks/*.md`, `.agent/resume/*.md`, heartbeat summaries, and dashboards to lag behind canonical state briefly.
- If a compatibility script fails after a runtime extraction, patch the wrapper or tests immediately before moving on.
- If any step introduces unexpected changes in checked-in `.agent/` runtime samples unrelated to the task, stop and inspect before proceeding.
