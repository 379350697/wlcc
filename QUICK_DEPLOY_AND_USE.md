# QUICK_DEPLOY_AND_USE

## 目标
说明如何把本仓库按 **总 skill 统一包装 + 基建层承载 + 原子模块内聚复用** 的模式快速部署并开始使用。

---

## 一、最终部署形态

部署后的仓库应保留以下三层：

### 1. 总 skill 入口
- `skills/long-chain-autonomy/`

这是对外统一入口。
默认优先使用它，而不是让使用者自己在多个 skill 之间手动切换。

### 2. 基建层
- `scripts/`
- `.agent/state/`
- `.agent/loop/`
- `.agent/heartbeat/`
- `.agent/audit/`
- `risk_policy.json`

这是实际运行时能力承载层。
负责：
- canonical state
- next-task
- retrieval
- risk / escalation
- failure control
- heartbeat / observability
- resume / handoff

### 3. 原子模块
- `skills/task-extract/`
- `skills/project-state/`
- `skills/context-compact/`
- `skills/handoff-report/`

这些模块继续保留，用于：
- 内部复用
- 场景化单独调用
- 后续演进拆分

---

## 二、快速部署清单

### 必须保留的目录/文件
- `skills/long-chain-autonomy/`
- `skills/*` 原子 skill
- `dist/`
- `scripts/`
- `.agent/`
- `risk_policy.json`
- `README.md`
- `STATUS.md`
- `TASKS.md`
- `DECISIONS.md`
- `INCIDENTS.md`

### 部署前确认
优先确认以下文件存在：
- `scripts/check_phase2_mainline.py`
- `scripts/retrieve_context.py`
- `scripts/resume_task.py`
- `scripts/resume_many_tasks.py`
- `scripts/emit_heartbeat.py`
- `scripts/build_observability_dashboard.py`
- `scripts/write_handoff_state.py`
- `.agent/state/next-task.json`
- `.agent/state/index.json`
- `tests/PHASE2_MAINLINE_CHECK_RESULT.md`

---

## 三、推荐启动顺序

### Step 1：确认主链健康
先跑：
```bash
python3 scripts/check_phase2_mainline.py
```

目标：确认 canonical state / next-task / retrieval / risk policy 主链正常。

### Step 2：确认 release 自检
再跑：
```bash
python3 scripts/system_healthcheck.py
```

目标：确认 retrieval / risk / audit summary 基本健康。

### Step 3：确认统一 skill 入口已存在
检查：
- `skills/long-chain-autonomy/SKILL.md`
- `UNIFIED_SKILL_DEPLOYMENT.md`

### Step 4：开始使用总 skill
后续使用时，默认把：
- `long-chain-autonomy`
作为主入口 skill。

---

## 四、使用模式

### 模式 1：task mode
适用：
- 新需求落任务
- 更新当前任务
- 从聊天提取成可执行项

优先复用：
- `task-extract`
- runtime state write / render 链

### 模式 2：state mode
适用：
- 看当前项目状态
- 读阶段、风险、阻塞、下一步

优先复用：
- `project-state`
- canonical state / fact files

### 模式 3：resume mode
适用：
- 中断后恢复
- 多会话接续
- handoff 后继续执行

优先复用：
- `context-compact`
- `scripts/build_resume_state.py`
- `scripts/resume_task.py`
- `scripts/resume_many_tasks.py`

### 模式 4：handoff mode
适用：
- CEO / coder 不同口径交接
- reviewer 接手
- 多角色责任链流转

优先复用：
- `handoff-report`
- `scripts/write_handoff_state.py`

### 模式 5：runtime mode
适用：
- 看 next-task
- 看 risk / failure
- 看 heartbeat / observability
- 跑一致性检查

优先复用：
- `scripts/check_phase2_mainline.py`
- `scripts/check_risk_level.py`
- `scripts/emit_heartbeat.py`
- `scripts/build_heartbeat_summary.py`
- `scripts/build_observability_dashboard.py`

---

## 五、运行时优先级

在总 skill 模式下，读取顺序固定为：
1. `.agent/state/tasks/*.json`
2. `.agent/state/*resume-state.json`
3. `.agent/state/handoffs/*.json`
4. `.agent/state/next-task.json`
5. `.agent/tasks/*.md` / `.agent/resume/*.md` / `.agent/NEXT_TASK.md`
6. `README.md` / `STATUS.md` / `DECISIONS.md` / `TASKS.md` / `INCIDENTS.md`
7. summaries
8. chat

不要反过来先靠长聊天历史恢复。

---

## 六、部署原则

### 对外原则
- 总是优先暴露 `long-chain-autonomy`
- 不要求终端使用者理解多个 skill 的边界

### 对内原则
- 不删除原子 skill
- 不让总 skill 替代基建层
- 不绕过 canonical state
- 不绕过 risk / failure / heartbeat 语义

### 发布原则
- 正式 git 仓以 `wlcc-release` 为准
- 后续版本迭代优先同步到 `wlcc-release`
- release tag 在 `wlcc-release` 执行

---

## 七、当前推荐用法

如果现在要开始实际使用：
1. 先把 `long-chain-autonomy` 当主入口
2. 默认让它调用 runtime state / next-task / resume / handoff / observability
3. 遇到特别单一场景，再下沉到原子 skill

这就是当前版本最推荐的产品使用方式。
