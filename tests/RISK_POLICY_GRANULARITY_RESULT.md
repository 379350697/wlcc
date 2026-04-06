# RISK_POLICY_GRANULARITY_RESULT

## canonical-state-write-needs-confirmation
- riskLevel: L2
- decision: require-confirmation
- matchedRule: {"action": "write-state", "scope": "*", "targetType": "state", "pathPrefix": "*", "matchContext": {"touchesCanonicalState": true}, "conditionOverride": false}
- result: PASS

## release-script-modify-approved
- riskLevel: L3
- decision: allow
- matchedRule: {"action": "modify-script", "scope": "release", "targetType": "scripts", "pathPrefix": "*", "matchContext": {"touchesReleaseRepo": true}, "conditionOverride": true}
- result: PASS

## destructive-delete-state-unapproved
- riskLevel: L3
- decision: reject
- matchedRule: {"action": "delete-state", "scope": "*", "targetType": "state", "pathPrefix": "*", "matchContext": {"isDestructive": true}, "conditionOverride": false}
- result: PASS

## Overall
- PASS
