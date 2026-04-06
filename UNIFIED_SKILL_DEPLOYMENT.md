# UNIFIED_SKILL_DEPLOYMENT

## 最终产品形态
本仓库按以下模式部署：

- **总 skill 统一入口**：`skills/long-chain-autonomy/`
- **基建层承载**：`scripts/` + `.agent/`
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
- 总 skill 负责统一入口与路由
- 基建层负责真实运行能力
- 原子模块负责内聚复用与后续演进

## 仓库要求
正式 git 仓应始终保留：
- `skills/long-chain-autonomy/`
- `skills/*` 原子 skill
- `scripts/` 主链脚本
- `.agent/` 必要运行态样例与审计结构
- `dist/` 打包 skill 产物
