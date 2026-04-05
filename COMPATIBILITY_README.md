# COMPATIBILITY_README

## 目标
说明新旧结构如何兼容读取，避免一次性硬切换。

## 当前兼容原则
1. 旧文件不删除
2. 新结构优先用于新增写入
3. 新结构缺失时，降级读取旧结构
4. 摘要类文件不覆盖事实类文件

## 读取顺序
### 项目级
1. `README.md`
2. `STATUS.md`
3. `DECISIONS.md`
4. `TASKS.md`
5. `INCIDENTS.md`

### 任务级
1. `.agent/tasks/<task>.md`
2. `.agent/resume/<task>-resume.md`
3. `TASKS.md` 总览
4. `CHANGELOG.md`

### 摘要级
1. `tests/*.md`
2. `SKILL_VALIDATION_ROUND1.md`
3. 其他 compact / handoff 产物

## 降级规则
- 缺少 task state 时，用 TASKS 总览 + CHANGELOG 补
- 缺少 resume 时，用 task state + TASKS 总览补
- 缺少项目事实文件时，明确标记未发现，不用聊天猜补

## 当前判断
本项目当前已具备新旧并行读取的最小条件，但还没有完全自动化的兼容读取实现。
