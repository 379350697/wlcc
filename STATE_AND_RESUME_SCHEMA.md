# STATE_AND_RESUME_SCHEMA

## 1. Task State
文件位置：`.agent/tasks/<task-id>.md`

字段：
- `id`
- `project`
- `goal`
- `status` (`todo | doing | blocked | done`)
- `latestResult`
- `blocker`
- `nextStep`
- `updatedAt`

## 2. Resume State
文件位置：`.agent/resume/<task-id>-resume.md`

字段：
- `taskId`
- `最后目标`
- `最后成功动作`
- `最后失败动作`
- `当前阻塞`
- `建议下一步`
- `updatedAt`

## 3. Next Task Decision
文件位置：`.agent/NEXT_TASK.md`

字段：
- `currentTask`
- `currentStatus`
- `decisionType` (`continue-current | switch-next | blocked | done-no-next`)
- `nextTaskId`
- `reason`
- `nextAction`

## 4. Resume Output Structured Summary
单任务：`tests/<task-id>-resume-output.md`
批量：`tests/BULK_RESUME_OUTPUT.md`

字段：
- `goal`
- `status`
- `blocker`
- `next_step`
- `last_success`
- `last_failure`
- `resume_state`
- `bulk_resume_state`

## 5. Multi-session Resume State
文件位置：`.agent/state/<task-id>-resume-state.json` / `.agent/state/bulk-resume-state.json`

字段：
- `selectedTaskId`
- `selectionReasons`
- `candidateCount`
- `conflictPolicy`
- `loopResume`
- `candidates`

规则：
- 优先级按 `next-task > current-task > doing > override > todo > blocked`
- 恢复必须可引用最近 loop 节点
- 恢复冲突必须输出明确选择原因

## 6. Bulk Update Summary
文件位置：`tests/BULK_UPDATE_SUMMARY.md`

字段：
- `success`
- `failure`

## 7. Validation Rules
- `status` 必须属于 `todo | doing | blocked | done`
- `goal / latest_result / blocker / next_step / last_success / last_failure` 不能为空
- 缺字段或非法状态必须拒绝写入，并记录到 `FAILURE_LOG.md`
