# REPO_PUBLISH_CHECKLIST

## 发布前应确认
- [x] 正式实施文档齐全
- [x] Skill 定义与打包产物齐全
- [x] 状态底座脚本齐全
- [x] 测试与验证材料齐全
- [x] 审计摘要存在
- [x] 部署说明存在
- [x] bootstrap 脚本存在
- [x] 最小健康检查通过
- [x] 交付完整性检查通过

## 发布前建议再看
- `.gitignore` 是否足够
- 是否需要剔除不打算发布的研究源码镜像目录
- 仓库名称与 README 标题是否一致
- Git 远程地址是否已配置为你的目标仓库

## 建议发布范围
优先发布：
- 当前项目根文档
- `skills/`
- `dist/`
- `scripts/`
- `.agent/audit/`
- `.agent/logs/`
- `.agent/tasks/`
- `.agent/resume/`
- `memory/`
- `tests/`

谨慎决定是否保留：
- `claude-code/`
- `open-agent-sdk-typescript/`
- `ai-agent-deep-dive/`
- `claude-code-source-analysis/`

这些更像研究样本，不一定都需要放进最终部署仓库。
