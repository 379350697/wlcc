# TEST_FIXTURE_CONTRACT

## 目标
统一 wlcc 当前主检查链和 runtime tests 所依赖的 fixture/task contract。

---

## fixture 分类

### F1. primary real runtime fixture
- task id: `real-close-runtime-final-target`
- kind: `real`
- status: `doing`
- priority: `P0`
- lifecycle: `active`
- eligibleForScheduling: `true`
- isPrimaryTrack: `true`

#### 覆盖场景
- `progress_task_runtime.py`
- `resume_real_task.py`
- `run_task_supervision.py`
- `check_retrieval_priority.py`
- `render_state_views.py`
- `check_phase2_mainline.py`

---

### F2. ingest smoke fixture
- task id: `real-真实任务接管机制层-p0-启动任务`
- kind: `real`
- 来源：通过 `ingest_real_task.py` 生成

#### 覆盖场景
- ingest runtime smoke
- render views smoke
- supervision bootstrap smoke

---

### F3. handoff compatibility fixture
- task id: `demo-long-chain-autonomy`
- 用途：兼容 handoff / ownership / demo 路径

> 说明：这是兼容 fixture，不是当前主 runtime fixture。

---

## fixture 生成规则

### 规则 1
fixture 不要求稳定提交进正式源仓。

### 规则 2
标准运行版验证前，允许由 bootstrap / test setup 自动生成最小 fixture。

### 规则 3
如果 fixture 缺失：
- 当前主检查链应优先尝试 bootstrap 最小 fixture
- 而不是继续写死依赖旧 task id 或旧 result 文件

---

## 禁止事项

以下都不再允许：
- 写死 `task-001` 作为唯一主样本
- 写死 `local-task-001`
- 写死 `real-task-runtime-mainline`
- 直接把某次本地运行生成的 `tests/*_RESULT.md` 当作 fixture

---

## 当前建议
默认主链和标准运行包统一优先使用：
- `real-close-runtime-final-target`

如果将来要换新的主 fixture，必须先改本文件，再改脚本，不允许脚本各自私改。
