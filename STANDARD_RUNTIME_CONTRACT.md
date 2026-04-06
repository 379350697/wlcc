# STANDARD_RUNTIME_CONTRACT

## 目标
定义 wlcc 最新标准运行版的最小 contract，避免仓边界变化后，runtime / tests / demo 各自继续依赖旧样本和旧结果文件。

---

## 1. 标准运行版必须包含

### entry skill
- `skills/long-chain-autonomy/`

### runtime core
- `runtime/`
- `scripts/`
- `risk_policy.json`

### canonical state 容器
- `.agent/state/tasks/`
- `.agent/state/supervision/`
- `.agent/state/handoffs/`
- `.agent/state/ownership/`
- `.agent/state/index.json`
- `.agent/state/next-task.json`
- `.agent/state/next-task-input.json`

### sidecar 输出目录
- `.agent/tasks/`
- `.agent/resume/`
- `.agent/logs/`
- `.agent/audit/`
- `.agent/heartbeat/`
- `tests/`

---

## 2. 标准运行版默认不再随仓强制携带的内容
以下内容属于**本地动态运行态**，允许在本地部署目录生成，但不要求作为正式源仓稳定样例提交：

- `.agent/NEXT_TASK.md`
- `.agent/tasks/*.md`
- `.agent/resume/*-resume.md`
- `.agent/logs/*.md`
- `.agent/heartbeat/*.json`
- `.agent/audit/*.md`
- `.agent/audit/*.json`
- `tests/*_RESULT.md`
- `tests/*_OUTPUT.json`
- `tests/*-resume-output.md`

这些文件由脚本运行时生成，**不能再被当成主 contract 本身**。

---

## 3. 标准 fixture contract
标准运行版必须至少能 bootstrap 出一组最小 fixture，供 mainline / bundle / runtime tests 复用：

### real task fixture
- task id: `real-close-runtime-final-target`
- 用途：
  - progress runtime
  - resume real task
  - task supervision
  - retrieval priority
  - render state views

### ingest fixture
- task id: `real-真实任务接管机制层-p0-启动任务`
- 用途：
  - ingest real task
  - render state views smoke

### handoff fixture
- task id: `demo-long-chain-autonomy`
- 用途：
  - handoff / ownership 兼容检查

---

## 4. contract 原则

### 原则 A：tests 不能再硬依赖历史阶段结果文件
例如：
- `RISK_POLICY_MATRIX_RESULT.md`
- `RISK_POLICY_GRANULARITY_RESULT.md`
- 旧 `PHASE2_*` 结果文件

这些如果仍需保留，必须归入历史/legacy 验证，不再作为当前标准运行版主 contract。

### 原则 B：tests 允许依赖标准 fixture，但不能假设本地运行痕迹已提交进仓
也就是说：
- 可以依赖 bootstrap 生成的 canonical fixture
- 不可以依赖“仓里已经预先带好了某次运行后的 sidecar 结果”

### 原则 C：mainline check 只检查当前 contract
mainline check 只应检查：
- 最小 canonical state
- sidecar 可生成
- retrieval 顺序正确
- 关键脚本存在

不要再混入旧阶段 acceptance 结果。
