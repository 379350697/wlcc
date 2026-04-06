# PHASE_2_RELEASE_SYNC_PLAN

## 结论
`wlcc-release` 当前还停留在更早一版交付状态，尚未同步本轮 Phase 2 主链路迁移成果。
如果直接把它当发布版使用，会缺失 canonical state / retrieval / risk policy / mainline consistency 这一整批能力。

---

## 一、已确认的发布版目录
- `/root/.openclaw/projects/shared/wlcc-release`

---

## 二、与研究主线相比的关键缺口
以下对比基于：
- 源目录：`/root/.openclaw/projects/shared/research-claude-code`
- 发布目录：`/root/.openclaw/projects/shared/wlcc-release`

### 1. 发布版中缺失的关键新增文件
#### next-task / canonical state
- `scripts/build_next_task_from_state.py`
- `scripts/decide_next_task.py`
- `scripts/decide_next_task_v2.py`
- `scripts/check_next_task_consistency.py`
- `scripts/write_state_store.py`
- `scripts/render_state_views.py`
- `scripts/check_state_view_consistency.py`

#### retrieval
- `scripts/retrieve_context.py`
- `scripts/check_retrieval_priority.py`
- `scripts/resume_many_tasks.py`

#### risk policy
- `risk_policy.json`
- `scripts/evaluate_risk_policy.py`
- `scripts/check_risk_policy_consistency.py`

#### mainline / e2e
- `scripts/check_phase2_mainline.py`
- `scripts/test_phase2_single_task_e2e.py`
- `scripts/test_phase2_bulk_e2e.py`
- `scripts/test_phase2_resume_e2e.py`

#### Phase 2 文档
- `PHASE_2_PROGRESS.md`
- `PHASE_2_MAINLINE_INTEGRATION.md`
- `PHASE_2_REMAINING_GAPS_AND_COMPLETION_PLAN.md`
- `PHASE_2_COMPLETE_TASK_BREAKDOWN.md`

### 2. 发布版中已存在但内容已落后/不同的文件
- `scripts/read_project_context.py`
- `scripts/resume_task.py`
- `scripts/system_healthcheck.py`
- `scripts/check_risk_level.py`
- `README_DEPLOY.md`
- `FINAL_DELIVERY_SUMMARY.md`

---

## 三、F1 同步包建议

### 包 1：主链脚本同步包
目标：先让发布版具备当前 Phase 2 的实际运行能力。

建议同步：
- next-task v2 / canonical state 脚本
- retrieval 脚本
- risk policy 脚本
- mainline / e2e 检查脚本
- 已落后的入口脚本更新版

### 包 2：Phase 2 文档同步包
目标：让发布版文档与当前真实状态一致。

建议同步：
- `PHASE_2_PROGRESS.md`
- `PHASE_2_MAINLINE_INTEGRATION.md`
- `PHASE_2_REMAINING_GAPS_AND_COMPLETION_PLAN.md`
- `PHASE_2_COMPLETE_TASK_BREAKDOWN.md`
- 更新 `README_DEPLOY.md`
- 更新 `FINAL_DELIVERY_SUMMARY.md`

### 包 3：验证材料同步包
目标：让发布版在同步后有可直接复验的证据链。

建议同步：
- `tests/RISK_POLICY_MATRIX_RESULT.md`
- `tests/RISK_POLICY_GRANULARITY_RESULT.md`
- `tests/RISK_POLICY_CONSISTENCY_RESULT.md`
- `tests/PHASE2_MAINLINE_CHECK_RESULT.md`
- `tests/PHASE2_SINGLE_TASK_E2E_RESULT.md`
- `tests/PHASE2_BULK_E2E_RESULT.md`
- `tests/PHASE2_RESUME_E2E_RESULT.md`

---

## 四、推荐同步顺序
1. 先同步脚本与配置
2. 再同步 Phase 2 文档
3. 再同步验证材料
4. 最后在 `wlcc-release` 内重新跑 healthcheck / delivery / readiness / mainline checks

---

## 五、当前判断
当前已经具备进入 F1 的条件。
但在真正同步前，最好先做一个最小同步清单，避免把 research 目录里无关测试噪音整体搬过去。
