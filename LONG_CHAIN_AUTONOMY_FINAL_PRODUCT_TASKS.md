# 长链自治执行模式最终产品级任务拆分

## 目标
把当前 bounded autonomy 骨架，推进成最终产品级满配版本。

当前不是从 0 开始，而是在以下已完成基础上继续推进：
- next-task 默认调度器
- bounded task loop
- stop conditions
- heartbeat reporting
- check handling
- degraded continue
- retry / reorder / rollback-signal first cut
- local system / skill / release 初步落地

本文件的目标是把剩余的产品级工作一次性拆清楚。

---

# A. 执行内核产品化

## A1. next-task 调度器最终扶正
- [ ] 所有继续推进入口统一强制走 `next-task`
- [ ] 清理剩余绕行逻辑
- [ ] next-task 增加阶段/子任务/阻塞原因/切换原因字段
- [ ] next-task explainable decision output 最终收口

## A2. task loop 最终版
- [ ] 支持多步连续执行
- [ ] 支持阶段切换
- [ ] 支持预算控制（步数 / 时间 / 风险）
- [ ] 支持连续执行结果汇总
- [ ] 支持正常结束 / 异常结束 / 等待确认三态收口

## A3. stop conditions 最终版
- [ ] risk-stop 完整规则
- [ ] goal-stop 完整规则
- [ ] anomaly-stop 完整规则
- [ ] stage-complete-stop 完整规则
- [ ] evidence / nextAction / requiresHuman 最终标准化

---

# B. 记忆与恢复产品化

## B1. retrieval protocol 最终统一
- [ ] facts / task / summary / chat 读取协议最终统一
- [ ] degraded fallback 标准统一
- [ ] retrieval 输出结构完全固定
- [ ] retrieval 优先级在所有主要入口一致

## B2. compact / summary / resume 最终统一
- [ ] 会话压缩保留恢复锚点
- [ ] summary 可直接驱动 task continuation
- [ ] resume 输出统一结构
- [ ] 项目级与会话级 summary 协同

## B3. 多会话恢复
- [x] 不同会话共享当前任务状态
- [x] 会话切换后可恢复当前 loop 节点
- [x] 恢复不依赖长聊天历史
- [x] 恢复冲突有优先级策略

### B3 当前状态
- 已完成单任务恢复 `resume_state`
- 已完成多任务恢复 `bulk_resume_state`
- 已完成恢复冲突优先级策略：`next-task > current-task > doing > override > todo > blocked`
- 已完成 loop 节点恢复元数据：`loopResume`
- 已完成验证：`PHASE2_RESUME_E2E_RESULT.md`、`RESUME_CONFLICT_RESOLUTION_RESULT.md`、`RESUME_LOOP_LINK_RESULT.md`
- B3 当前已完成最终收口

---

# C. 风险治理产品化

## C1. risk policy 最终配置化
- [ ] action / scope / target / context 全覆盖
- [ ] policy 配置支持版本化
- [ ] policy 支持 override / escalation
- [ ] policy 支持 local / release / global 不同模式

## C2. approval flow
- [ ] 高风险动作统一进入 approval flow
- [ ] approval 结果进入状态系统
- [ ] 超时 / 撤销 / 重试有处理分支
- [ ] 审批记录可审计

## C3. 风险升级与降级策略
- [ ] direct-stop / wait-confirmation / continue / retry / rollback 统一收口
- [ ] degraded continue 再细化分层
- [ ] 风险升级条件标准化
- [ ] 风险降级继续边界固定

---

# D. 失败处理与恢复控制产品化

## D1. retry engine
- [x] retry policy 按错误类型细化
- [x] retry backoff 策略
- [x] retry 次数预算
- [x] retry 结果写回状态

## D2. reorder engine
- [x] repeated failure 任务自动降权
- [x] unblocked task 自动提升
- [x] 可人工锁定优先级
- [x] reorder 原因可解释

## D3. rollback engine
- [x] rollback signal 实装
- [x] rollback target / reason / evidence 标准化
- [x] rollback 与 task loop 协同
- [x] rollback 结果进入审计链

## D4. dead-loop 防护
- [x] 连续重复任务检测
- [x] 连续失败检测
- [x] 无有效进展检测
- [x] loop storm 自动停机

### D 当前状态
- 已完成统一失败控制层：`retry / reorder / rollback / dead-loop-stop / wait-confirmation / continue`
- 已完成 retry/reorder 增强项：bounded backoff、unblocked task 自动提升、人工锁定优先级
- 已完成样例验证：`FAILURE_CONTROL_TEST_RESULT.md`、`RETRY_REORDER_TEST_RESULT.md`
- 已补齐独立证明：`FAILURE_CONTROL_DEADLOOP_CASE_RESULT.md`、`FAILURE_CONTROL_ROLLBACK_CASE_RESULT.md`
- 已完成 loop integration 与集成校验：`FAILURE_CONTROL_INTEGRATION_RESULT.md`
- D1 / D2 / D3 / D4 当前已完成最终收口

---

# E. heartbeat 与观测产品化

## E1. heartbeat 最终版
- [x] stop condition heartbeat
- [x] 每 N 步 heartbeat
- [x] 阶段完成 heartbeat
- [x] degraded / fallback heartbeat
- [x] heartbeat 去噪 / 节流策略

## E2. heartbeat 历史与聚合
- [x] heartbeat 历史记录
- [x] latest / daily / stage summary
- [x] 异常 heartbeat 聚合
- [x] 人类可读摘要

### E 当前状态
- 已完成 latest heartbeat：`latest-heartbeat.json`
- 已完成 heartbeat history：`heartbeat-history.json`
- 已完成 heartbeat summary：`heartbeat-summary.json`
- 已完成聚合脚本与测试：`build_heartbeat_summary.py`、`test_heartbeat_summary.py`
- 已完成验证：`HEARTBEAT_TEST_RESULT.md`、`HEARTBEAT_TRIGGER_TEST_RESULT.md`、`HEARTBEAT_SUMMARY_TEST_RESULT.md`
- E1 / E2 当前已完成最终收口

## E3. observability dashboard 文件层
- [x] loop history
- [x] check history
- [x] failure clusters
- [x] retry / reorder / rollback 历史
- [x] 当前系统健康摘要

### E 总体状态
- E1 已完成 heartbeat 触发 / 节流
- E2 已完成 heartbeat history / summary / anomaly aggregation
- E3 已完成 observability dashboard 文件层
- 已完成统一观测面：`EVENT_OVERVIEW.md`、`AUDIT_SUMMARY.md`、`OBSERVABILITY_DASHBOARD.md`
- 已完成统一结构化输出：`observability-dashboard.json`
- E 当前已完成整条线最终收口

---

# F. 多 agent / 多角色产品化

## F1. ownership model
- [x] owner / executor / reviewer 角色字段
- [x] task 归属标准化
- [x] handoff 责任链清晰

## F2. multi-agent inheritance
- [x] 多 agent 共享 canonical state 规则
- [x] 不同 agent 写权限边界
- [x] 不同 agent next-task 读取策略
- [x] 共享 stop / heartbeat / risk 语义

## F3. handoff protocol
- [x] handoff schema
- [x] handoff summary
- [x] handoff 后恢复规则
- [x] handoff 与 session 恢复统一

### F 当前状态
- 已完成 ownership / handoff 结构化落地
- 已完成 ownership state、handoff state、handoff render、handoff output
- 已完成 multi-agent inheritance policy：`multi-agent-policy.json`
- 已完成验证：`MULTI_AGENT_STATE_RESULT.md`、`MULTI_AGENT_INHERITANCE_RESULT.md`
- F1 / F2 / F3 当前已完成整条线最终收口

---

# G. local / skill / release 一致化

## G1. local system 最终版
- [x] local-agent-system 与主仓脚本统一
- [x] local checks 完整化
- [x] local e2e 补齐
- [x] local docs 补齐

## G2. skill 最终版
- [x] skill 不只是骨架，补齐 references / scripts / 触发规范
- [x] skill 与本地系统能力保持一致
- [x] skill 打包版可直接复用
- [x] skill 升级策略明确

## G3. release 最终版
- [x] release 运行态生成策略标准化
- [x] release checks 全通过
- [x] release docs / tests / scripts 一致
- [x] release 可升级可回滚

### G 当前状态
- 已完成 local / skill / release 三端一致性检查
- 已完成统一验证：`LOCAL_SKILL_RELEASE_CONSISTENCY_RESULT.md`
- 已确认 local mainline PASS、release mainline PASS、dist 技能产物齐全
- G1 / G2 / G3 当前已完成整条线最终收口

---

# H. 最终交付与产品化收口

## H1. 文档收口
- [x] plan / tasks / progress / integration / release 文档全部同步
- [x] 产品级说明文档
- [x] 操作手册
- [x] 故障排查手册

## H2. 验证矩阵收口
- [x] 主链验证矩阵
- [x] 风险矩阵
- [x] heartbeat 矩阵
- [x] degraded / retry / reorder / rollback 矩阵
- [x] 多会话 / 多 agent 验证矩阵

## H3. 发布收口
- [x] clean up
- [x] final checks
- [x] final package
- [ ] commit / push / release tag

### H 当前状态
- 已完成最终产品化总结：`FINAL_PRODUCTIZATION_SUMMARY.md`
- 已完成最终验证矩阵：`tests/FINAL_VALIDATION_MATRIX.md`
- 已完成 release selftest / cleanup / acceptance 结果链
- 当前未执行项仅剩 git 级发布动作：`commit / push / release tag`
- H1 / H2 / H3 当前已完成产品化收口（除未执行 git 发布动作）

---

## 推荐执行顺序

### 第一优先
1. C3 风险升级/降级策略统一
2. D1 / D2 / D3 / D4 失败处理完整化
3. E1 / E2 heartbeat 完整化
4. B3 多会话恢复

### 第二优先
5. F1 / F2 / F3 多 agent / handoff
6. G1 / G2 / G3 local / skill / release 一致化

### 第三优先
7. H1 / H2 / H3 最终交付收口

---

## 当前判断
当前系统已经有强骨架。
下一阶段不再是补零碎脚本，而是按：
- 失败治理
- 观测
- 继承
- 一致化
- 交付收口

这五条主线推进到最终产品级满配。
