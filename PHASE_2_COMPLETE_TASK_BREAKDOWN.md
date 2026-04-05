# PHASE_2_COMPLETE_TASK_BREAKDOWN

## 目标
把当前系统补成“完整上线版”。
要求：本拆分覆盖剩余全部工作；只要此清单全部完成，即视为完整上线版完成。

---

# A. next-task v2 全量替代

## A1. 默认主决议器切换
- [x] 让 `build_next_task_from_state.py` 成为默认 next-task 生成入口
- [x] 让旧 `decide_next_task.py` 降级为 fallback
- [ ] 清理仍直接依赖旧决议格式的脚本

## A2. 批量/恢复链路统一接入 v2
- [x] `bulk_update_tasks.py` 改为刷新 `next-task.json` + `NEXT_TASK.md`
- [x] `resume_task.py` 直接读取 `next-task.json`
- [x] `resume_many_tasks.py` 直接读取 `next-task.json`
- [ ] readiness / audit / delivery 相关检查统一使用 v2 输出

## A3. next-task v2 一致性测试
- [ ] 增加 state -> next-task 决议一致性测试
- [ ] 增加 bulk / resume / update 三条链路的一致性测试
- [ ] 增加 override / dependency / priority 混合场景测试

---

# B. canonical state 成为唯一事实源

## B1. 写入链路收口
- [ ] `update_task_state.py` 全量以 state store 为主
- [ ] `bulk_update_tasks.py` 同步写 state store
- [ ] 其他状态变更脚本统一经过 state writer

## B2. 视图渲染覆盖完整
- [ ] `render_state_views.py` 稳定生成 task 视图
- [ ] `render_state_views.py` 稳定生成 resume 视图
- [ ] `render_state_views.py` 稳定生成 `TASKS.md`
- [ ] `render_state_views.py` 稳定生成 `NEXT_TASK.md`

## B3. markdown-first 解析下线
- [x] 清理主链路中直接解析 `.agent/tasks/*.md` 的逻辑（`read_project_context.py` / `resume_task.py` / `resume_many_tasks.py` 已 state-first）
- [x] 清理主链路中直接解析 `.agent/resume/*.md` 的逻辑（恢复链已改为 json first，markdown 仅 fallback）
- [ ] 只保留 markdown 作为视图层/fallback

## B4. canonical state 一致性测试
- [x] state -> task md 一致性测试
- [x] state -> resume md 一致性测试
- [x] state -> TASKS.md 一致性测试
- [x] state -> NEXT_TASK.md 一致性测试

---

# C. retrieval protocol 全局接管

## C1. 统一读取入口替换
- [x] `resume_task.py` 接入 `retrieve_context.py`
- [x] `resume_many_tasks.py` 接入 `retrieve_context.py`
- [x] `system_healthcheck.py` 接入 retrieval protocol
- [ ] `check_delivery_completeness.py` 接入 retrieval protocol（仅需要处）
- [ ] `check_next_stage_readiness.py` 接入 retrieval protocol（仅需要处）

## C2. retrieval 优先级验证
- [ ] facts 覆盖 summary 测试
- [ ] canonical state 优先于 markdown state 测试
- [ ] markdown state 回退测试
- [ ] summary / chat 最后补位测试

## C3. retrieval 输出标准化
- [ ] 统一 meta 字段
- [ ] 统一 usedSources 输出格式
- [ ] 统一 degradedFallback 标记规范

---

# D. risk policy 完整化

## D1. policy 配置化
- [x] 抽出独立 policy 配置文件
- [x] action / scope / target / context 规则外置
- [x] 支持默认规则 + 覆盖规则

## D2. policy 粒度增强
- [x] 支持 target path/type 判断
- [x] 支持 release/project/workspace/external scope 区分
- [x] 支持 destructive / canonical-state / release-repo 语义判断

## D3. 主链路替换与测试
- [x] 让 `check_risk_level.py` 完整依赖 policy config
- [x] 补齐 allow / require-confirmation / reject 矩阵测试
- [x] 把风险结果接入审计链路

---

# E. 系统一致性检查补齐

## E1. 存在性检查升级为一致性检查
- [x] `check_phase2_mainline.py` 增加 state/view 一致性断言
- [x] 增加 next-task state/view 一致性断言
- [x] 增加 retrieval 行为一致性断言
- [x] 增加 risk policy 行为一致性断言

## E2. 端到端验证
- [x] 单任务更新 -> state -> views -> next-task -> retrieval 全链路验证
- [x] 批量更新 -> state -> views -> next-task 全链路验证
- [x] 恢复 -> retrieval -> next-task -> summary 输出全链路验证

---

# F. 发布版最终收口

## F1. Phase 2 成果同步到 `wlcc-release`
- [ ] 同步 next-task v2
- [ ] 同步 canonical state
- [ ] 同步 retrieval protocol
- [ ] 同步 risk policy
- [ ] 同步一致性检查脚本

## F2. 发布版验证
- [ ] release manifest 通过
- [ ] audit summary 通过
- [ ] healthcheck 通过
- [ ] delivery completeness 通过
- [ ] readiness 通过
- [ ] Phase 2 mainline checks 通过

## F3. 发布版清理与发布
- [ ] 清理临时文件/测试噪音
- [ ] 更新最终文档与交付说明
- [ ] commit
- [ ] push

---

## 完成定义（Definition of Done）
只有当 A~F 所有任务都打勾，并且：
- 主链路检查 PASS
- 一致性检查 PASS
- 发布版检查 PASS
- 发布版重新推送完成

才视为：
**完整上线版完成。**
