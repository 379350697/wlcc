# STANDARD_RUNTIME_BUNDLE

## 目标
定义面向 OpenClaw 的标准运行版交付边界。

标准运行版不是研发母仓的全量镜像，而是：
- 保留 `entry skill`
- 保留 `runtime core`
- 保留必要 `sidecar services`
- 不强制携带全部 `dev-only assets`

## 术语

### entry skill
- `skills/long-chain-autonomy/`

### runtime core
- `runtime/`
- 在线主链脚本
- `.agent/state/`
- `.agent/loop/`
- `risk_policy.json`

### sidecar services
- `.agent/NEXT_TASK.md`
- `.agent/tasks/*.md`
- `.agent/resume/*.md`
- `.agent/flows/*.md`
- `TASKS.md`
- `.agent/heartbeat/heartbeat-summary.json`
- `.agent/audit/observability-dashboard.json`

### dev-only assets
- `tests/*.md`
- `tests/*.json`
- demo pack
- 历史阶段文档
- 大量 `scripts/test_*.py`

## 必须包含

### skill 入口
- `skills/long-chain-autonomy/`

### runtime core
- `runtime/common/`
- `runtime/actions/`
- `runtime/context/`
- `runtime/evidence/`
- `runtime/events/`
- `runtime/failure/`
- `runtime/flow/`
- `runtime/reply/`
- `runtime/state/`
- `runtime/scheduling/`
- `runtime/resume/`
- `runtime/gates/`
- `runtime/harness/`
- `runtime/supervision/`
- `runtime/sidecar/`

### 必需脚本
- `scripts/ingest_real_task.py`
- `scripts/progress_task_runtime.py`
- `scripts/close_task_runtime.py`
- `scripts/resume_task.py`
- `scripts/resume_real_task.py`
- `scripts/read_project_context.py`
- `scripts/retrieve_context.py`
- `scripts/build_resume_state.py`
- `scripts/decide_next_task_v2.py`
- `scripts/build_next_task_from_state.py`
- `scripts/delivery_gate.py`
- `scripts/progress_reply_gate.py`
- `scripts/check_reply_exit.py`
- `scripts/evaluate_risk_policy.py`
- `scripts/check_risk_level.py`
- `scripts/run_task_supervision.py`
- `scripts/emit_heartbeat.py`
- `scripts/render_state_views.py`
- `scripts/build_heartbeat_summary.py`
- `scripts/build_observability_dashboard.py`
- `scripts/check_state_view_consistency.py`
- `scripts/test_control_plane_smoke.py`
- `scripts/system_healthcheck.py`
- `scripts/check_phase2_mainline.py`
- `scripts/verify_standard_runtime_bundle.py`

### 必需运行态
- `.agent/state/tasks/`
- `.agent/state/flows/`
- `.agent/state/index.json`
- `.agent/state/next-task.json`
- `.agent/state/supervision/`
- `.agent/state/handoffs/`
- `.agent/loop/`
- `.agent/logs/`

## 同步主链产物
这些必须同步生成，不能降为 sidecar：
- `.agent/state/tasks/*.json`
- `.agent/state/flows/*.json`
- `.agent/state/index.json`
- `.agent/state/next-task.json`
- supervision state
- handoff state

## sidecar 产物
这些可以按需刷新，允许短暂落后于 canonical state：
- `.agent/NEXT_TASK.md`
- `.agent/tasks/*.md`
- `.agent/resume/*.md`
- `.agent/flows/*.md`
- `TASKS.md`
- `.agent/heartbeat/heartbeat-summary.json`
- `.agent/audit/observability-dashboard.json`
- `tests/STATE_VIEW_CONSISTENCY_RESULT.md`

## 推荐保留
- `tests/runtime/`
- `pyproject.toml`
- `tests/README.md`

## 可以不随标准运行版强制交付
- 大量历史 `tests/*.md`
- demo 验收材料
- 阶段性总结文档
- 研发期一次性修复脚本

## 标准验收命令
```bash
python3 scripts/verify_standard_runtime_bundle.py
```

## 说明
- `next-task.json` 仍然是同步主链的一部分。
- `reply exit gate` 与 `task flow` 现在是标准运行版的一等组成部分，不能只存在于 prompt 或外部约定里。
- sidecar services 的目标是降低 OpenClaw 主链负担，而不是削弱执行增强能力。
