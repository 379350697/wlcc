# 真实任务接管机制层任务拆解（最终版）

## 总原则

继续沿用当前 release 版本方式部署：
- 总 skill 作为入口层
- 基建层脚本 / state / checks 作为运行底座
- release 仓库作为交付方式

本轮不推翻现有方式，只补齐：
- 真实任务接入
- 生命周期
- 监督触发
- 任务隔离
- orchestrator

---

# Phase 0：真实任务正式接入 runtime

## Task 0.1：实现 `ingest_real_task.py`
### 目标
把真实用户任务自动接入 canonical runtime。
### 输入
- 用户任务文本
- 标题
- 来源
- 优先级
- ownerContext
- executionMode
### 输出
- canonical task
- lifecycle 初始状态
- task/resume/TASKS 视图
- next-task
- supervision 初始状态
### 验收标准
- 不再依赖人工先造 task-id 才能推进
- 新任务可自动进入正式执行链
### 当前状态
- [x] 已完成本地完整版收口（RT-01）
- [x] 已同步到正式仓并进入 release 验证链

## Task 0.2：补 canonical task 元字段
### 必加字段
- `kind`
- `source`
- `executionMode`
- `ownerContext`
- `supervisionState`
- `eligibleForScheduling`
- `isPrimaryTrack`
### 验收标准
- real / demo / fixture / sample 可明确区分
- next-task 默认不被样本污染
### 当前状态
- [x] 已完成本地完整版收口（RT-02）
- [x] 已同步到正式仓并进入 release 验证链

---

# Phase 1：生命周期状态机

## Task 1.1：新增 `TASK_LIFECYCLE.md`
### 目标
定义真实任务完整生命周期。
### 建议状态
- `new`
- `ingested`
- `active`
- `blocked`
- `waiting-human`
- `handoff`
- `done`
- `archived`
### 验收标准
- 每个状态有进入条件、退出条件、必做动作
### 当前状态
- [x] 已完成本地完整版收口（RT-03）
- [x] 已同步到正式仓并进入 release 验证链

## Task 1.2：实现状态迁移逻辑
### 目标
把 lifecycle 从文档变成可执行规则。
### 验收标准
- 状态迁移有校验
- 非法迁移会拒绝或告警
### 当前状态
- [x] 已完成本地完整版收口（RT-03）
- [x] 已同步到正式仓并进入 release 验证链

---

# Phase 2：监督触发器机制

## Task 2.1：实现 `run_task_supervision.py`
### 目标
把 heartbeat / stale scan / resume prep / handoff prep 接成统一监督器。
### 触发点
- on_task_ingested
- on_task_changed
- on_interruption_detected
- on_interval
- on_completion
### 验收标准
- 不再靠人工记得触发关键监督动作
### 当前状态
- [x] 已完成本地完整版收口（RT-04）
- [x] 已同步到正式仓并进入 release 验证链

## Task 2.2：定义 trigger 规范
### 目标
为每类 trigger 定义输入、动作链、输出、失败策略。
### 验收标准
- trigger 行为固定
- 可测试
### 当前状态
- [x] 已完成本地完整版收口（RT-04）
- [x] 已同步到正式仓并进入 release 验证链

---

# Phase 3：统一 orchestrator

## Task 3.1：实现 `progress_task_runtime.py`
### 目标
统一真实任务推进入口。
### 验收标准
- 推进任务不再默认散改 state
- next-task / checks / supervision 能统一串起
### 当前状态
- [x] 已完成本地完整版收口（RT-05）
- [x] 已同步到正式仓并进入 release 验证链

## Task 3.2：实现 `resume_real_task.py`
### 目标
支持真实任务在换会话 / 换 agent / 中断后机制化恢复。
### 验收标准
- 不依赖某条原始聊天上下文仍可恢复推进
### 当前状态
- [x] 已完成本地完整版收口（RT-05）
- [x] 已同步到正式仓并进入 release 验证链

## Task 3.3：实现 `close_task_runtime.py`
### 目标
统一 closure / final handoff / archive。
### 验收标准
- done 任务可规范收口
- 自动写 final status / closure note

---

# Phase 4：正式任务与样本任务隔离

## Task 4.1：next-task 调度过滤默认限定 real task
### 目标
正式调度链默认只选 `kind=real` 或显式允许集合。
### 验收标准
- demo / fixture 不会自动进入正式执行链
### 当前状态
- [x] 已完成本地完整版收口（RT-06）
- [x] 已同步到正式仓并进入 release 验证链

## Task 4.2：retrieval / audit / resume 同步使用任务类型过滤
### 目标
避免样本污染恢复、审计、交付视图。
### 验收标准
- 正式任务与样本链路隔离清晰
### 当前状态
- [x] 已完成本地完整版收口（RT-07 / RT-08）
- [x] 已同步到正式仓并进入 release 验证链

---

# Phase 5：监督与交付增强

## Task 5.1：heartbeat 进入正式 runtime
### 目标
实现真实任务阶段汇报，不再只是日志。
### 验收标准
- 每完成 N 步 / 阶段结束 / stop condition 触发时可汇报
### 当前状态
- [x] 已完成本地完整版收口（RT-09）
- [x] 已同步到正式仓并进入 release 验证链

## Task 5.2：补 supervisor logs
### 目标
增加：
- supervisor actions log
- stalled task log
- missed heartbeat log
### 验收标准
- 监督动作可追溯
### 当前状态
- [x] 已完成本地完整版收口（RT-10）
- [x] 已同步到正式仓并进入 release 验证链

## Task 5.3：补 final handoff / closure / archive
### 验收标准
- 完成后自动生成 final handoff 与 closure note
### 当前状态
- [x] 已完成本地完整版收口（RT-11）
- [x] 已同步到正式仓并进入 release 验证链

---

# 不该做的事

1. 不要推翻当前 release 交付方式
2. 不要在机制层没补完前追求无限后台自治
3. 不要先做重型 UI / bridge / remote transport
4. 不要先做复杂多 agent 编排
5. 不要继续让真实任务依赖 demo 链路手工接入

---

# 推荐执行顺序

1. Task 0.1
2. Task 0.2
3. Task 1.1
4. Task 1.2
5. Task 2.1
6. Task 2.2
7. Task 3.1
8. Task 3.2
9. Task 4.1
10. Task 4.2
11. Task 5.1
12. Task 3.3 / 5.2 / 5.3

---

# 一句话要求

**继续沿用总 skill + 基建层 + release 方式，但把真实任务正式接进 runtime 状态机，让系统不再靠上下文运气推进。**

## 当前总状态
- [x] Task 0.1
- [x] Task 0.2
- [x] Task 1.1
- [x] Task 1.2
- [x] Task 2.1
- [x] Task 2.2
- [x] Task 3.1
- [x] Task 3.2
- [x] Task 4.1
- [x] Task 4.2
- [x] Task 5.1
- [x] Task 5.2
- [x] Task 5.3
- [x] 已完成正式仓同步与 release 收口（RT-12）
