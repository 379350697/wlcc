# Invalid Status Result

## 场景
- 非法状态值写入

## 预期
- update_task_state.py 拒绝写入非法状态
- 不污染 task / resume / TASKS / CHANGELOG

## 判断
若脚本返回错误并且未生成对应状态文件，则视为通过。
