# PHASE_2_PROGRESS

## 当前状态
Phase 2 已不再只是“设计 + 最小实现 + 验证并行推进”，而是已经进入**主链路迁移中段**。
当前进展重点已经转向：
- canonical state 继续扶正
- retrieval protocol 继续接管
- risk policy 配置化 / 细粒度化
- mainline check 从存在性检查升级为一致性检查

## 主线 1：next-task 决策器升级
### 已完成
- `NEXT_TASK_PHASE2_SCHEMA.md`
- `NEXT_TASK_PRIORITY_RULES.md`
- `scripts/decide_next_task_v2.py`
- `scripts/build_next_task_from_state.py`
- 旧 `scripts/decide_next_task.py` 已降级为 wrapper
- `update_task_state.py` 已自动触发 next-task v2
- `.agent/state/next-task.json` + `.agent/NEXT_TASK.md` 已联动
- `resume_task.py` / `resume_many_tasks.py` 已直接读 `next-task.json`
- `scripts/check_next_task_consistency.py` 已完成并输出结构化 summary

### 当前结果
- override / dependency / priority 三类决议均已通过样例验证
- next-task v2 已接回主链路核心部分
- `NEXT_TASK_CONSISTENCY_RESULT.md` 已不只输出 issues，还会输出 `currentTask / nextTaskId / decisionType / selectedPriority`

## 主线 2：canonical state
### 已完成
- `CANONICAL_STATE_PLAN.md`
- `STATE_STORE_SCHEMA.md`
- `scripts/write_state_store.py`
- `scripts/render_state_views.py`
- `.agent/state/tasks/*.json`
- `.agent/state/index.json`
- `.agent/state/next-task.json`
- `update_task_state.py` / `bulk_update_tasks.py` 已写 state store
- `render_state_views.py` 已生成 task / resume / TASKS / NEXT_TASK 视图
- `read_project_context.py` 已改为 state-first fallback
- `resume_task.py` / `resume_many_tasks.py` 已改为 state-first
- `scripts/check_state_view_consistency.py` 已完成并输出结构化 summary

### 当前结果
- 结构化状态源已开始接管 task / resume / TASKS / NEXT_TASK
- markdown 已进一步降级为 view / fallback
- `STATE_VIEW_CONSISTENCY_RESULT.md` 已输出 `task_count / tasks_view_checked`

## 主线 3：memory retrieval
### 已完成
- `MEMORY_RETRIEVAL_ORDER.md`
- `scripts/retrieve_context.py`
- `scripts/test_retrieve_context_split.py`
- `tests/RETRIEVE_CONTEXT_DEGRADED_OUTPUT.json`
- `tests/RETRIEVE_CONTEXT_NORMAL_OUTPUT.json`
- `read_project_context.py` 已优先走 retrieval
- `resume_task.py` / `resume_many_tasks.py` 已接 retrieval
- `system_healthcheck.py` 已接 retrieval
- `scripts/check_retrieval_priority.py` 已完成并输出结构化 summary
- retrieval priority check 已接回统一主检查

### 当前结果
- retrieval 顺序已固定为 fact > task state > summary > chat
- degraded / normal 两种 fallback 场景已验证
- `RETRIEVAL_PRIORITY_CHECK_RESULT.md` 已输出：
  - `canonical_task_before_markdown`
  - `canonical_next_before_markdown`
  - `degraded_fallback`

## 主线 4：risk policy layer
### 已完成
- `RISK_POLICY_SCHEMA.md`
- `risk_policy.json`
- `scripts/evaluate_risk_policy.py`
- `scripts/test_risk_policy_matrix.py`
- `scripts/test_risk_policy_granularity.py`
- `scripts/check_risk_policy_consistency.py`
- `tests/RISK_POLICY_MATRIX_RESULT.md`
- `tests/RISK_POLICY_GRANULARITY_RESULT.md`
- `tests/RISK_POLICY_INTEGRATION_RESULT.md`
- `tests/RISK_POLICY_CONSISTENCY_RESULT.md`

### 当前结果
- allow / require-confirmation / reject 三类策略决议已跑通
- evaluator 已从脚本硬编码切到 `risk_policy.json` 配置驱动
- 已支持 `action / scope / target / context` 细粒度判定
- `RISK_POLICY_CONSISTENCY_RESULT.md` 已输出 `policy_version / matrix_artifact / granularity_artifact / integration_artifact / risk_log_artifact`

## 主链路接回进展
### 已接回
- `update_task_state.py` -> `write_state_store.py`
- `update_task_state.py` -> `build_next_task_from_state.py`
- `render_state_views.py` -> `TASKS.md`
- `read_project_context.py` -> `retrieve_context.py`
- `check_risk_level.py` -> `evaluate_risk_policy.py`
- retrieval priority check -> `check_phase2_mainline.py`
- risk policy consistency check -> `check_phase2_mainline.py`

### 统一检查结果
- `tests/PHASE2_MAINLINE_CHECK_RESULT.md` = PASS
- 当前主检查已开始同时校验：
  - state/view 一致性
  - next-task 一致性
  - retrieval 行为摘要
  - risk policy 行为摘要
  - risk matrix / granularity 关键 case 覆盖

### 端到端验证结果
- `tests/PHASE2_SINGLE_TASK_E2E_RESULT.md` = PASS
- `tests/PHASE2_BULK_E2E_RESULT.md` = PASS
- `tests/PHASE2_RESUME_E2E_RESULT.md` = PASS

结论：
- E2 三条主链路端到端验证已全部打通：
  - 单任务更新链路
  - 批量更新链路
  - 恢复链路

## 下一步建议
1. 继续清理剩余 markdown-first 入口，逼近 canonical state 唯一事实源
2. 继续扩大 retrieval 对历史读取脚本的接管范围
3. 按 `PHASE_2_RELEASE_SYNC_PLAN.md` 开始执行 F1：发布版同步清单与落地路径
4. 再做一次发布版侧验证与收口
