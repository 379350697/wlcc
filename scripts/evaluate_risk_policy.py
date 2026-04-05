#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / 'risk_policy.json'


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding='utf-8'))


def value_matches(expected, actual) -> bool:
    if expected in (None, '*'):
        return True
    if isinstance(expected, list):
        return actual in expected
    return expected == actual


def match_rule(rule: dict, action: str, scope: str, target_type: str | None, target_path: str | None, context: dict) -> bool:
    action_ok = value_matches(rule.get('action', '*'), action)
    scope_ok = value_matches(rule.get('scope', '*'), scope)
    target_type_ok = value_matches(rule.get('targetType', '*'), target_type)

    path_prefix = rule.get('pathPrefix')
    if path_prefix in (None, '*'):
        path_ok = True
    else:
        path_ok = bool(target_path and str(target_path).startswith(path_prefix))

    context_match = True
    for key, expected in rule.get('matchContext', {}).items():
        if context.get(key) != expected:
            context_match = False
            break

    return action_ok and scope_ok and target_type_ok and path_ok and context_match


def condition_met(rule: dict, context: dict) -> bool:
    allow_if = rule.get('allowIf')
    if not allow_if:
        return False
    for key, expected in allow_if.items():
        if context.get(key) != expected:
            return False
    return True


def evaluate(action: str, scope: str, context: dict, target: dict | None = None):
    policy = load_policy()
    target = target or {}
    target_type = target.get('type')
    target_path = target.get('path')
    for rule in policy.get('rules', []):
        if not match_rule(rule, action, scope, target_type, target_path, context):
            continue
        result = {
            'riskLevel': rule['riskLevel'],
            'decision': rule['decision'],
            'reason': rule['reason'],
            'matchedRule': {
                'action': rule.get('action'),
                'scope': rule.get('scope'),
                'targetType': rule.get('targetType', '*'),
                'pathPrefix': rule.get('pathPrefix', '*'),
                'matchContext': rule.get('matchContext', {}),
            },
        }
        if condition_met(rule, context):
            result['decision'] = rule.get('allowDecision', result['decision'])
            result['reason'] = rule.get('allowReason', result['reason'])
            result['matchedRule']['conditionOverride'] = True
        else:
            result['matchedRule']['conditionOverride'] = False
        return result

    default_rule = policy['defaultRule']
    return {
        'riskLevel': default_rule['riskLevel'],
        'decision': default_rule['decision'],
        'reason': default_rule['reason'],
        'matchedRule': {
            'action': 'default',
            'scope': 'default',
            'conditionOverride': False,
        },
    }


def main():
    parser = argparse.ArgumentParser(description='Evaluate policy-based risk decision.')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding='utf-8'))
    result = evaluate(payload['action'], payload['scope'], payload.get('context', {}), payload.get('target'))
    result['action'] = payload['action']
    result['scope'] = payload['scope']
    result['policyVersion'] = load_policy().get('version', 'unknown')
    if 'target' in payload:
        result['target'] = payload['target']
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('OK')


if __name__ == '__main__':
    main()
