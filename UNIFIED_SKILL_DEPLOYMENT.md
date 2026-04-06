# UNIFIED_SKILL_DEPLOYMENT

## 最终产品形态
本仓库按以下模式部署：

- **entry skill**：`skills/long-chain-autonomy/`
- **runtime core**：`runtime/` + `scripts/` + `.agent/state/`
- **sidecar services**：`.agent/tasks/` + `.agent/resume/` + `.agent/audit/` + heartbeat summaries
- **dev-only assets**：`tests/` 结果、demo、阶段文档
- **原子模块内聚复用**：
  - `skills/task-extract/`
  - `skills/project-state/`
  - `skills/context-compact/`
  - `skills/handoff-report/`

## 入口规则
对外使用时，优先触发：
- `long-chain-autonomy`

对内复用时，可按场景调用原子 skill。

## 部署含义
- 不再要求使用者手动理解多个 skill 的边界
- entry skill 负责统一入口与路由
- runtime core 负责真实运行能力
- sidecar services 负责可读视图和汇总
- 原子模块负责内聚复用与后续演进

## 同步要求
必须同步保留：
- `.agent/state/tasks/*.json`
- `.agent/state/index.json`
- `.agent/state/next-task.json`

可延迟或按需刷新：
- `.agent/NEXT_TASK.md`
- `.agent/tasks/*.md`
- `.agent/resume/*.md`
- `TASKS.md`
- heartbeat summary
- observability dashboard

## 仓库要求
正式 git 仓应始终保留：
- `skills/long-chain-autonomy/`
- `skills/*` 原子 skill
- `runtime/`
- `scripts/` 主链脚本
- `.agent/` 必要运行态样例与审计结构
- `dist/` 打包 skill 产物
