#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p \
  "$ROOT/.agent/tasks" \
  "$ROOT/.agent/resume" \
  "$ROOT/.agent/logs" \
  "$ROOT/.agent/audit" \
  "$ROOT/.agent/backups" \
  "$ROOT/.agent/tmp" \
  "$ROOT/.agent/locks" \
  "$ROOT/memory/long-term" \
  "$ROOT/memory/session" \
  "$ROOT/tests" \
  "$ROOT/dist"

echo "OK: bootstrap complete -> $ROOT"
