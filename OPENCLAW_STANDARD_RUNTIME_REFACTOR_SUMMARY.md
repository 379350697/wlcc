# OPENCLAW_STANDARD_RUNTIME_REFACTOR_SUMMARY

## 一、这份说明的目的

这份文档专门说明本轮面向 OpenClaw 的标准运行版重构做了什么、为什么这么做、哪些能力被保留、哪些能力被移到 sidecar，以及现在应该如何验证和理解这套结构。

这不是一份抽象规划，而是对本次已经落地改动的说明。

---

## 二、本轮改动的背景

本仓库原本已经具备：
- 总 Skill 统一入口
- canonical state
- next-task
- resume / retrieval
- risk / delivery / progress gate
- harness
- heartbeat / observability
- handoff / supervision

问题不在于方向错误，而在于实现形态更接近“脚本集合”：
- 主链上有较多 CLI 到 CLI 的互调
- 公共 helper 分散
- 在线执行增强逻辑和人类可读 sidecar 混在一起
- 后续继续服务 OpenClaw 演进时，模块边界不够清晰

因此本轮改动的目标不是重写业务逻辑，而是把这套基建从“脚本式基建”推进成“runtime 产品骨架”。

---

## 三、本轮重构目标

目标是形成下面这四层结构：

### 1. entry skill
- `skills/long-chain-autonomy/`

### 2. runtime core
- `runtime/`
- 在线主链脚本
- `.agent/state/`

### 3. sidecar services
- Markdown 视图
- heartbeat summary
- observability dashboard
- 一致性校验结果

### 4. dev-only assets
- `tests/*.md`
- `tests/*.json`
- demo / acceptance / phase 文档

核心原则是：
- 不削弱 OpenClaw 的执行增强层
- 不把 `next-task`、`resume`、`retrieve_context`、`gates`、`harness` 旁路掉
- 只把重视图、重汇总、重校验从同步主链拆出去

---

## 四、本轮做了哪些核心改动

### 1. 新增 `runtime/` 内核

已新增：
- `runtime/common/`
- `runtime/state/`
- `runtime/scheduling/`
- `runtime/resume/`
- `runtime/gates/`
- `runtime/harness/`
- `runtime/supervision/`
- `runtime/sidecar/`

这些模块分别承接：
- 公共 IO / 时间 / 路径 / schema
- canonical state 与 lifecycle
- `next-task` 核心调度
- context / resume state / resume service
- delivery / progress / risk gate
- harness 编排
- supervision 与 heartbeat emit
- sidecar 视图、summary、dashboard

### 2. 主链脚本变成薄 wrapper

以下主链脚本已经主要通过 runtime API 工作：
- `scripts/ingest_real_task.py`
- `scripts/progress_task_runtime.py`
- `scripts/close_task_runtime.py`
- `scripts/resume_task.py`
- `scripts/resume_real_task.py`
- `scripts/run_task_supervision.py`
- `scripts/tool_harness.py`
- `scripts/tool_registry.py`

### 3. sidecar 从主链里拆出

以下能力被明确收敛到 sidecar：
- `NEXT_TASK.md`
- `.agent/tasks/*.md`
- `.agent/resume/*.md`
- `TASKS.md`
- heartbeat summary
- observability dashboard
- state view consistency

这些能力依然保留，但不再作为主链必须先完成的同步前提。

### 4. 新增统一验收入口

新增：
- `scripts/verify_standard_runtime_bundle.py`

作用：
- 把标准运行版最关键的 runtime 测试和兼容性 smoke test 收成固定命令
- 避免每次靠人工抄一串命令验收

---

## 五、哪些能力被保留在线

本轮没有弱化下面这些 OpenClaw 执行增强能力：

- canonical task state
- `.agent/state/next-task.json`
- retrieval / resume
- progress gate
- delivery gate
- risk gate
- harness
- ingest / progress / close
- supervision judge
- handoff state

换句话说，保住的是：
- 执行力
- 记忆补强
- 任务接续
- 风险约束
- 可恢复性

---

## 六、哪些能力被移到 sidecar

本轮被移出同步主链的主要是：

- `NEXT_TASK.md`
- task / resume Markdown 视图
- `TASKS.md`
- heartbeat summary
- observability dashboard
- view consistency check

这不代表这些能力不重要，而是它们更适合作为：
- 人读视图
- 运维视图
- 审计与汇总产物

而不是每一步都阻塞 OpenClaw 主链执行的同步步骤。

---

## 七、这次对性能和主链负担的影响

### 改善点
- 主链内部大量能力改成 Python 进程内调用
- 减少了不必要的 CLI 到 CLI 编排
- supervision 不再同步生成 heartbeat summary
- sidecar 产物可以按需补齐

### 保留点
- 仍保留必要的同步 canonical state
- 仍保留同步 `next-task.json`
- 仍保留同步 gate / harness / resume / supervision 逻辑

因此本轮不是“把能力裁掉换轻量”，而是：
- 保留执行增强语义
- 降低同步负担

---

## 八、兼容性处理

本轮额外补了几处关键兼容点：

- heartbeat 时间字段同时支持 `emittedAt` 和 `timestamp`
- heartbeat 文件同时兼容单对象和历史数组格式
- `build_resume_state` 对显式传入但缺 state 文件的候选仍保留排序
- 标准运行版验收会先刷新必要 sidecar，避免读旧产物误报

---

## 九、验证方式

### runtime 回归
```bash
python3 -m pytest tests/runtime -q
```

### 标准运行版验收
```bash
python3 scripts/verify_standard_runtime_bundle.py
```

本轮已经补上的关键验证包括：
- runtime 单测
- progress / ingest / close
- resume real task
- task supervision
- heartbeat summary
- observability dashboard
- state view consistency
- phase2 mainline
- system healthcheck

---

## 十、当前交付结果

到本次改动结束时，仓库已经具备：

- 清晰的 runtime core
- 明确的 sidecar 边界
- 标准运行版 bundle 说明
- 固定的一键验收入口
- 面向 OpenClaw 的持续演进结构

这意味着当前仓库已经不只是“有很多机制脚本”，而是已经形成：

- 可执行
- 可恢复
- 可验证
- 可演进
- 可部署说明

的标准运行版骨架。

---

## 十一、和旧结构相比，最本质的变化

旧结构更像：
- 总 Skill
- 一组能力脚本
- 通过脚本互调拼出运行时

新结构更像：
- entry skill
- runtime core
- sidecar services
- dev-only assets

这也是本轮最核心的产出：

不是只把文件搬了位置，
而是把这套服务 OpenClaw 的基建，正式做成了“有运行内核、有边界、有验收口径”的基础设施形态。
