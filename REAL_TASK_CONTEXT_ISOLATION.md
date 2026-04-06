# REAL_TASK_CONTEXT_ISOLATION

## 目标
让 retrieval / resume / audit / observability 默认优先服务真实任务，不再被 demo / sample / fixture 污染。

## 默认规则
1. 正式主链默认优先 `kind=real`
2. `executionMode=sample-only` 不应进入正式恢复与调度主线
3. audit / observability 展示应优先标出 real task 主线
4. legacy / sample 数据可保留，但不能作为正式主链默认输入

## 应用范围
- retrieval
- resume
- next-task
- supervision
- heartbeat / observability
