# PHASE_2_MAINLINE_INTEGRATION

## 已接回主链路的能力

### 1. canonical state 写入已接入 `update_task_state.py`
证据：
- `scripts/update_task_state.py`
- `scripts/write_state_store.py`
- `tests/UPDATE_STATE_STORE_LINK_RESULT.md`
- `.agent/state/tasks/task-phase2-link-demo.json`

结论：
- 状态更新后，除 markdown 外，已同步写入 canonical state。

### 2. next-task v2 已接入状态更新链路
证据：
- `scripts/build_next_task_from_state.py`
- `scripts/decide_next_task_v2.py`
- `tests/UPDATE_NEXT_TASK_V2_LINK_RESULT.md`
- `.agent/state/next-task.json`
- `.agent/NEXT_TASK.md`
- `tests/NEXT_TASK_CONSISTENCY_RESULT.md`

结论：
- 状态更新后，已自动触发 next-task v2 重算并回写结构化状态与 markdown 视图。
- 当前 next-task 一致性结果已带结构化 summary，可被统一主检查消费。

### 3. TASKS / task / resume 视图已开始由 canonical state 渲染
证据：
- `scripts/render_state_views.py`
- `tests/STATE_TASKS_RENDER_RESULT.md`
- `tests/STATE_RESUME_RENDER_RESULT.md`
- `tests/UPDATE_RENDER_STATE_VIEWS_LINK_RESULT.md`
- `tests/STATE_VIEW_CONSISTENCY_RESULT.md`
- `TASKS.md`
- `.agent/tasks/task-phase2-render-link.md`
- `.agent/resume/task-phase2-render-link-resume.md`

结论：
- task / resume / TASKS 视图已开始由 state store 生成，并已接回 `update_task_state.py` 自动刷新链路。
- state/view 一致性检查已带结构化 summary，可被统一主检查消费。

### 4. retrieval protocol 已接回多个读取主入口
证据：
- `scripts/retrieve_context.py`
- `scripts/read_project_context.py`
- `scripts/resume_task.py`
- `scripts/resume_many_tasks.py`
- `scripts/system_healthcheck.py`
- `tests/RETRIEVAL_PRIORITY_CHECK_RESULT.md`

结论：
- retrieval 已不只是旁路脚本，而是已经进入 read / resume / healthcheck 多个主入口。
- retrieval priority 检查已输出结构化 summary，并已接回统一主检查。

### 5. risk policy layer 已接回旧 risk gate，并已配置化 / 细粒度化
证据：
- `risk_policy.json`
- `scripts/evaluate_risk_policy.py`
- `scripts/check_risk_level.py`
- `scripts/check_risk_policy_consistency.py`
- `tests/RISK_POLICY_MATRIX_RESULT.md`
- `tests/RISK_POLICY_GRANULARITY_RESULT.md`
- `tests/RISK_POLICY_CONSISTENCY_RESULT.md`

结论：
- 旧 risk gate 主判断逻辑已改为调用 policy evaluator。
- risk policy 已从脚本硬编码进入配置化与细粒度化阶段。
- risk 一致性检查已输出结构化 summary，并已接回统一主检查。

## 当前尚未完全接回的能力
### memory retrieval
- 已接入多个主入口
- 但尚未替换所有历史读取入口

### canonical state
- 已大幅推进 state-first
- 但 markdown-first 旧解析入口仍未完全清理

## 统一检查
- `tests/PHASE2_MAINLINE_CHECK_RESULT.md` = PASS
- 当前主检查已同时覆盖：
  - next-task 一致性
  - state/view 一致性
  - retrieval 优先级行为
  - risk policy 一致性
  - risk matrix / granularity 关键场景

## 当前结论
Phase 2 已经不只是设计和旁路脚本验证，已有多条能力正式进入主链路。
而且统一主检查已开始从“文件存在性”升级为“结构化语义断言 + 关键 case 覆盖”的验收入口。
