# State Update Flow

## 目标
规范 `TASKS.md`、`.agent/tasks/*.md`、`.agent/resume/*.md` 的最小更新流程，避免状态漂移和半写入。

## 更新顺序
1. 先更新任务主状态
2. 再更新 Resume State
3. 最后写入 CHANGELOG

## Task State 最小字段
- id
- project
- goal
- status
- latestResult
- blocker
- nextStep
- updatedAt

## Resume State 最小字段
- taskId
- 最后目标
- 最后成功动作
- 最后失败动作
- 当前阻塞
- 建议下一步
- updatedAt

## 状态流转规则
- todo -> doing：开始执行
- doing -> blocked：出现明确阻塞
- blocked -> doing：阻塞已解除
- doing -> done：验收标准满足且有证据

## 更新原则
- 不跳过关键中间状态
- done 必须有完成证据
- blocker 解除后要同步更新 nextStep
- Resume State 必须与 Task State 保持一致

## 写入原则
- 一律使用安全写入
- 先生成新内容到临时输入文件
- 再通过 `scripts/safe_write.py` 原子替换目标文件
- 成功后再更新 CHANGELOG
