# RISK_POLICY_MATRIX_RESULT

## write-state-project
- stdout: L1
- exit_code: 0
- expected_stdout: L1
- expected_exit_code: 0
- result: PASS

## modify-script-unapproved
- stdout: L2
- exit_code: 4
- expected_stdout: L2
- expected_exit_code: 4
- result: PASS

## modify-script-approved
- stdout: L2
- exit_code: 0
- expected_stdout: L2
- expected_exit_code: 0
- result: PASS

## delete-state-unapproved
- stdout: L3
- exit_code: 3
- expected_stdout: L3
- expected_exit_code: 3
- result: PASS

## delete-state-approved-confirmed
- stdout: L3
- exit_code: 0
- expected_stdout: L3
- expected_exit_code: 0
- result: PASS

## Overall
- PASS
