# wlcc

一个面向 OpenClaw 的**长链自治（Long Chain Autonomy）产品化仓库**。

这不是单一 Skill 的提示词集合，也不是一堆零散脚本的研究目录。
当前仓库已经整理成以下正式形态：

- **entry skill 统一入口**
- **runtime core 承载真实能力**
- **sidecar services 承担视图与汇总**
- **原子模块内聚复用**
- **dev-only assets 保留研发与验证材料**
- **可直接进入部署、演示、回归验证流程**

---

## 一、这是什么

`wlcc` 是一套面向 OpenClaw 的长链任务执行与恢复方案，目标是把“任务推进、状态恢复、风险治理、失败处理、heartbeat 观测、handoff 交接”收敛成一套可部署、可验证、可继续演进的产品形态。

它解决的不是单次问答，而是：
- 任务如何稳定落盘
- 中断后如何恢复
- 风险如何治理
- 失败如何处理
- 长链执行如何观测
- 多角色/多会话如何交接

---

## 二、当前产品结构

### 1. entry skill
- `skills/long-chain-autonomy/`

这是当前推荐的**主入口**。
使用时，优先把它当成统一产品入口，而不是手动在多个 Skill 之间来回切换。

### 2. runtime core
- `runtime/`
- `scripts/`
- `.agent/state/`
- `.agent/loop/`
- `risk_policy.json`

这部分是真正干活的在线内核，负责：
- canonical state
- next-task v2
- retrieval / resume
- risk policy / escalation
- failure control
- supervision / heartbeat emit
- handoff / inheritance

### 3. sidecar services
- `.agent/tasks/`
- `.agent/resume/`
- `.agent/heartbeat/heartbeat-summary.json`
- `.agent/audit/`
- `TASKS.md`

这部分负责：
- `NEXT_TASK.md`
- task / resume Markdown 视图
- heartbeat summary
- observability dashboard
- 一致性校验与可读报表

### 4. dev-only assets
- `tests/*.md`
- `tests/*.json`
- 历史 phase 文档
- demo / acceptance 材料
- 大量 `scripts/test_*.py`

### 5. 原子模块
- `skills/task-extract/`
- `skills/project-state/`
- `skills/context-compact/`
- `skills/handoff-report/`

这些模块继续保留，用于：
- 内部复用
- 场景化单独调用
- 后续演进与拆分

---

## 三、当前已具备的核心能力

### 状态与调度
- canonical state
- next-task v2
- 结构化 task / resume / next-task 视图
- mainline consistency check

### 检索与恢复
- retrieval-first
- 单任务恢复
- 批量恢复
- 多会话恢复
- loop 节点恢复引用
- 冲突优先级策略

### 风险与失败治理
- risk policy
- risk escalation
- degraded continue
- retry / reorder / rollback / dead-loop 防护
- 统一 failure control

### heartbeat 与观测
- latest heartbeat
- heartbeat history / summary
- anomaly aggregation
- observability dashboard
- system health summary

### 多角色 / 多 agent
- owner / executor / reviewer
- handoff state
- handoff render / output
- inheritance policy
- shared stop / heartbeat / risk semantics

### 一致化与发布
- local / skill / release 一致性检查
- release 自检
- final acceptance
- git 发布与 tag

---

## 四、快速开始

### 1. 基础自检
先执行：

```bash
bash scripts/bootstrap_project.sh
python3 scripts/system_healthcheck.py
python3 scripts/check_phase2_mainline.py
python3 scripts/verify_standard_runtime_bundle.py
```

### 2. 查看统一部署说明
优先阅读：
- `UNIFIED_SKILL_DEPLOYMENT.md`
- `QUICK_DEPLOY_AND_USE.md`
- `STANDARD_RUNTIME_BUNDLE.md`
- `OPENCLAW_STANDARD_RUNTIME_REFACTOR_SUMMARY.md`

### 3. 作为统一产品入口使用
默认把：
- `skills/long-chain-autonomy/`

作为主入口 Skill。

### 4. 如需验收 Demo
优先阅读：
- `DEMO_ACCEPTANCE_README.md`
- `LOCAL_DEMO_RUNBOOK.md`

并查看：
- `tests/DEMO_COMPLETENESS_SUMMARY.md`
- `tests/DEMO_COMPLETENESS_PACK_RESULT.md`

---

## 五、推荐阅读顺序

如果你是第一次接手这个仓库，建议按这个顺序看：

1. `README.md`
2. `UNIFIED_SKILL_DEPLOYMENT.md`
3. `QUICK_DEPLOY_AND_USE.md`
4. `OPENCLAW_STANDARD_RUNTIME_REFACTOR_SUMMARY.md`
5. `FINAL_PRODUCTIZATION_SUMMARY.md`
6. `FINAL_DELIVERY_SUMMARY.md`
7. `tests/FINAL_VALIDATION_MATRIX.md`
8. `DEMO_ACCEPTANCE_README.md`
9. `TASKS.md`
10. `.agent/audit/AUDIT_SUMMARY.md`

---

## 六、当前仓库定位

当前仓库已经不再只是“研究原型”，而是已经具备：

- 可执行
- 可恢复
- 可审计
- 可观测
- 可交接
- 可发布复验

的产品化闭环。

其中同步主链必须保留：
- `.agent/state/tasks/*.json`
- `.agent/state/index.json`
- `.agent/state/next-task.json`

可以延迟生成的 sidecar 产物包括：
- `.agent/NEXT_TASK.md`
- `.agent/tasks/*.md`
- `.agent/resume/*.md`
- `TASKS.md`
- heartbeat summary
- observability dashboard

这意味着它可以被用作：
- 正式交付仓
- 本地部署源
- Demo 演示仓
- 回归验证基础仓

---

## 七、Demo 与验收

当前仓库已经带有一版**完整级别 demo 测试包**，覆盖：

### 主链
- task state
- next-task
- retrieval
- resume
- heartbeat
- observability
- handoff
- ownership / inheritance
- retry / reorder
- failure control

### 异常 / 边界
- invalid status reject
- canonical missing fallback
- broken next-task json
- broken heartbeat history
- duplicate heartbeat throttle
- force-run override
- dependency unsatisfied
- batch conflict selection
- force-run vs force-hold collision
- empty / dirty event log
- dead-loop sample
- rollback sample
- missing / dirty field injection
- resume state conflict

关键结果文件：
- `tests/DEMO_COMPLETENESS_SUMMARY.md`
- `tests/DEMO_COMPLETENESS_PACK_RESULT.md`

---

## 八、仓库说明

### 正式仓
当前正式 git 仓以 `wlcc-release` 为准。
后续发布、tag、正式同步，默认都在这个仓库内进行。

### 研究/上游目录
研究和中间演进目录可以继续保留，但不再作为主交付入口。

---

## 九、当前建议

如果你现在就要开始使用，建议直接这样做：

1. 先跑主链自检
2. 以 `long-chain-autonomy` 作为统一入口
3. 需要时下沉到原子 Skill
4. 用 demo 包做回归或演示验证

这就是当前版本最推荐的产品使用方式。
