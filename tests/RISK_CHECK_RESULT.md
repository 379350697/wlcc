# Risk Check Result

## 场景
- 当前项目最小权限分级检查

## 检查项
- `write-state` -> 预期 `L1`
- `delete-state` -> 预期 `L3`
- `unknown-action` -> 预期拒绝 / UNKNOWN

## 目标
证明当前权限分级不只存在文档，还能通过最小检查脚本给出结果。
