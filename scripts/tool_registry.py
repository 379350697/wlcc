#!/usr/bin/env python3
"""Compatibility wrapper for runtime harness registry."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from runtime.harness.registry import DEFAULTS, REGISTRY, get_meta, is_registered, list_concurrent_safe, list_state_modifiers

__all__ = [
    'DEFAULTS',
    'REGISTRY',
    'get_meta',
    'is_registered',
    'list_concurrent_safe',
    'list_state_modifiers',
]


if __name__ == '__main__':
    import json

    if len(sys.argv) > 1:
        for name in sys.argv[1:]:
            meta = get_meta(name)
            registered = is_registered(name)
            print(f"{'[REG]' if registered else '[DEFAULT]'} {name}:")
            print(json.dumps(meta, ensure_ascii=False, indent=2))
    else:
        total = len(REGISTRY)
        concurrent = len(list_concurrent_safe())
        modifiers = len(list_state_modifiers())
        print(f'Tool Registry: {total} scripts registered')
        print(f'  concurrent_safe: {concurrent}')
        print(f'  state_modifiers: {modifiers}')
        print(f'  fail-closed defaults: {DEFAULTS}')
