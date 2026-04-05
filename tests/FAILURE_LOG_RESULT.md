# Failure Log Result

## 场景
- 非法状态输入触发失败日志

## 目标
- 非法状态不仅被拒绝
- 还要把失败写入 `FAILURE_LOG.md`

## 判断
若失败日志出现对应 task 与 invalid_status 记录，则视为通过。
