#!/usr/bin/env python3
import shutil

checks = {
    'python3': shutil.which('python3') is not None,
    'bash': shutil.which('bash') is not None,
}

all_ok = all(checks.values())
print('PASS' if all_ok else 'FAIL')
for name, ok in checks.items():
    print(f'{name}={"OK" if ok else "MISSING"}')
raise SystemExit(0 if all_ok else 1)
