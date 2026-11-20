#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/veracity-harness-gate.XXXXXX")"
trap 'rm -rf "$fixture"' EXIT
fixture_repo="$fixture/repo with spaces"
mkdir -p "$fixture_repo/scripts" "$fixture_repo/harness/.venv/bin" "$fixture/bin"
cp "$repo_root/scripts/verify-harness.sh" "$fixture_repo/scripts/"
for command in docker uv; do
  cp "$repo_root/scripts/agent-hooks/fixtures/harness-command.sh" "$fixture/bin/$command"
  chmod +x "$fixture/bin/$command"
done
cp "$repo_root/scripts/agent-hooks/fixtures/harness-command.sh" "$fixture_repo/harness/.venv/bin/python"
chmod +x "$fixture_repo/harness/.venv/bin/python"
export PATH="$fixture/bin:$PATH"
export GATE_CALLS="$fixture/gate-calls"
gate="$fixture_repo/scripts/verify-harness.sh"

bash "$gate"
[ "$(cat "$GATE_CALLS")" = "$(printf '%s\n' docker sync client lint format unit integration)" ]

: > "$GATE_CALLS"
GATE_FAIL=docker bash "$gate" --no-docker > "$fixture/output"
[ "$(cat "$GATE_CALLS")" = "$(printf '%s\n' sync client lint format unit)" ]

for failure in docker sync client lint format unit integration; do
  : > "$GATE_CALLS"
  if GATE_FAIL="$failure" bash "$gate" > "$fixture/output" 2>&1; then
    printf 'Harness verification hid the %s failure\n' "$failure" >&2
    exit 1
  fi
  [ "$(tail -n 1 "$GATE_CALLS")" = "$failure" ]
done

printf 'Harness verification: Docker opt-out, serial acceptance, and failure propagation passed.\n'
