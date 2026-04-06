# TASKS

## Active
### demo-schema-check
- 目标：demo-schema-check
- 当前状态：todo
- 优先级：P0
- 阻塞项：无
- 下一步：check
- 最近结果：init

### real-lifecycle-check
- 目标：lifecycle check
- 当前状态：doing
- 优先级：P0
- 阻塞项：无
- 下一步：move active
- 最近结果：created

### real-lifecycle-runtime-integration
- 目标：验证 ingest 与 lifecycle 迁移逻辑已接通。
- 当前状态：doing
- 优先级：P0
- 阻塞项：无
- 下一步：进入 lifecycle=ingested，并等待正式推进。
- 最近结果：真实任务已接入 runtime。

### real-schema-check
- 目标：real-schema-check
- 当前状态：todo
- 优先级：P1
- 阻塞项：无
- 下一步：check
- 最近结果：init

### real-task-runtime-mainline
- 目标：按 REAL_TASK_RUNTIME_FINAL_PLAN/REAL_TASK_RUNTIME_FINAL_TASKS 从 P0 开始补齐真实任务接管机制层，并按既定顺序从 1 做到 9。
- 当前状态：doing
- 优先级：P0
- 阻塞项：无
- 下一步：继续推进 supervisor logs。
- 最近结果：Task 5.1 heartbeat 已接入正式 runtime。

### real-真实任务接管机制层-p0-启动任务
- 目标：验证真实任务可一跳接入 runtime，并自动生成 state/view/next-task/resume。
- 当前状态：doing
- 优先级：P0
- 阻塞项：无
- 下一步：进入 lifecycle=ingested，并等待正式推进。
- 最近结果：真实任务已接入 runtime。

### task-001
- 目标：继续推进整体项目收口与下一阶段增强。
- 当前状态：doing
- 优先级：P1
- 阻塞项：缺少 release 侧 canonical state 运行态产物。
- 下一步：补齐 state/view/next-task 并重跑 release 检查。
- 最近结果：发布版已同步 Phase 2 主链脚本、文档与验证材料。

### task-bulk-a
- 目标：验证批量更新能力 A。
- 当前状态：doing
- 优先级：P2
- 阻塞项：无
- 下一步：检查 task/resume/TASKS 是否同步。
- 最近结果：批量更新测试 A 已执行。

### task-bulk-b
- 目标：验证批量更新能力 B。
- 当前状态：blocked
- 优先级：P2
- 阻塞项：等待批量结果核验。
- 下一步：检查 task/resume/TASKS 是否同步。
- 最近结果：批量更新测试 B 已执行。

### task-phase2-demo
- 目标：验证 canonical state 写入。
- 当前状态：doing
- 优先级：P1
- 阻塞项：无
- 下一步：继续补渲染层。
- 最近结果：state store 已写入。

### task-phase2-e2e-bulk-a
- 目标：验证批量链路 A。
- 当前状态：doing
- 优先级：P2
- 阻塞项：无
- 下一步：检查批量 state/view/next-task。
- 最近结果：批量 E2E 更新 A 已执行。

### task-phase2-e2e-bulk-b
- 目标：验证批量链路 B。
- 当前状态：blocked
- 优先级：P2
- 阻塞项：等待批量验证。
- 下一步：检查批量 state/view/next-task。
- 最近结果：批量 E2E 更新 B 已执行。

### task-phase2-e2e-single
- 目标：验证单任务端到端链路。
- 当前状态：doing
- 优先级：P2
- 阻塞项：无
- 下一步：检查 state/view/next-task/retrieval。
- 最近结果：单任务 E2E 更新已触发。

### task-phase2-link-demo
- 目标：验证 update_task_state 接 canonical state。
- 当前状态：doing
- 优先级：P2
- 阻塞项：无
- 下一步：继续扩大接入范围。
- 最近结果：已同步写入 markdown 与 state store。

### task-phase2-render-link
- 目标：验证 update_task_state 自动触发 state views 渲染。
- 当前状态：doing
- 优先级：P2
- 阻塞项：无
- 下一步：继续扩大 audit 视图接入。
- 最近结果：已自动刷新 task/resume/TASKS 视图。

### task-phase2-v2-link
- 目标：验证 update_task_state 自动刷新 next-task v2。
- 当前状态：doing
- 优先级：P2
- 阻塞项：无
- 下一步：继续扩大 canonical state 覆盖。
- 最近结果：已接入 state store + next-task v2。

## Done
### real-close-runtime-final-target
- 目标：验证 close_task_runtime 收口链。
- 当前状态：done
- 优先级：P1
- 阻塞项：无
- 下一步：archive
- 最近结果：真实任务机制层 closure 已完成。
