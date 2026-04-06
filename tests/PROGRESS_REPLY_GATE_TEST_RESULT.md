# PROGRESS_REPLY_GATE_TEST_RESULT

- 正常通过: PASS (exit=0)
- next_step太短拒绝: PASS (exit=1, reason=next_step 太短（2 字符，最少 10）)
- next_step空话术拒绝: PASS (exit=1)
- 循环推进拒绝: PASS (exit=1, reason=next_step 与 latest_result 完全相同（循环推进）)
- latest_result太短拒绝: PASS (exit=1)
- latest_result空话术拒绝: PASS (exit=1)

## Overall: PASS
