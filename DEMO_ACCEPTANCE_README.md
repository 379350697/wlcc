# DEMO_ACCEPTANCE_README

## 目标
说明本地 `long-chain-autonomy` 完整 demo 的能力范围、验证范围和当前完成度。

## 当前结论
本地 demo 已达到完整级别：
- 已覆盖主链能力
- 已覆盖恢复/交接/观测/失败治理
- 已覆盖多类异常、冲突、损坏、脏输入、回退样本
- 已形成完整 demo 测试包

## 已覆盖主链
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

## 已覆盖异常/边界
- invalid status reject
- canonical missing fallback
- broken next-task json
- broken heartbeat history
- duplicate heartbeat throttle
- force-run override
- dependency unsatisfied
- batch conflict selection
- force-run vs force-hold collision
- empty event log
- dirty event log line
- dead-loop sample
- rollback sample
- task state missing field
- handoff dirty field
- ownership malformed field
- resume state conflict

## 关键结果文件
- `tests/DEMO_COMPLETENESS_SUMMARY.md`
- `tests/DEMO_COMPLETENESS_PACK_RESULT.md`
- `tests/DEMO_EXTREME_CASES_RESULT.md`
- `tests/INVALID_AND_OVERRIDE_CASES_RESULT.md`
- `tests/DEADLOOP_AND_ROLLBACK_CASES_RESULT.md`
- `tests/RESUME_STATE_CONFLICT_CASES_RESULT.md`
- `tests/OWNERSHIP_AND_DIRTY_EVENT_CASES_RESULT.md`

## 当前判断
这套 demo 已经可以作为：
- 本地完整能力演示
- 交付验收演示
- 回归检查基础包
