#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"
initial_pid="${1:?Supply the original initial-phase process ID}"
for attempt in $(seq 1 180); do
  stage="$(harness/.venv/bin/python -c 'import json; print(json.load(open("harness/results/sector-full/progress.json"))["status"])')"
  if [ "$stage" = initial_phase_complete ]; then
    pid_state="$(ps -p "$initial_pid" -o stat= 2>/dev/null || true)"
    if [ -n "$pid_state" ] && [[ "$pid_state" != Z* ]]; then
      sleep 5
      continue
    fi
    exec bash harness/research/sector-expansion/run-cloud.sh all
  fi
  if [ "$stage" != initial_answers ]; then
    printf 'Initial collection ended with stage %s; inspect before dispatch.\n' "$stage" >&2
    exit 1
  fi
  sleep 5
done
printf 'Initial phase did not finish within the continuation window.\n' >&2
exit 1
