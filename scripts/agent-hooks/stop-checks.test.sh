#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/veracity-stop-test.XXXXXX")"
trap 'rm -rf "$fixture"' EXIT
mkdir -p "$fixture/scripts/agent-hooks" "$fixture/.codex/hooks" "$fixture/docs/decisions"
cp "$repo_root/scripts/agent-hooks/stop-checks.sh" "$fixture/scripts/agent-hooks/"
cp "$repo_root/scripts/agent-hooks/fixtures/verify.sh" "$fixture/scripts/verify-fast.sh"
cp "$repo_root/scripts/decision-index.py" "$fixture/scripts/"
cp "$repo_root/.codex/hooks/stop_checks.sh" "$fixture/.codex/hooks/"
hook="$fixture/scripts/agent-hooks/stop-checks.sh"

for config in "$repo_root/.codex/hooks.json" "$repo_root/.claude/settings.json"; do
  jq -e '[.hooks.Stop[].hooks[]] | length == 1 and all(.[]; .type == "command" and (.timeout | type == "number" and . > 0 and . <= 30))' "$config" >/dev/null
done
jq -e '.hooks.Stop[0].hooks[0].command == "/bin/bash \"$(git rev-parse --show-toplevel)/.codex/hooks/stop_checks.sh\""' "$repo_root/.codex/hooks.json" >/dev/null
jq -e '.hooks.Stop[0].hooks[0].command == "/bin/bash \"$CLAUDE_PROJECT_DIR\"/scripts/agent-hooks/stop-checks.sh"' "$repo_root/.claude/settings.json" >/dev/null

printf '{}' | bash "$fixture/.codex/hooks/stop_checks.sh" >"$fixture/output" 2>"$fixture/errors"
jq -se 'length == 1 and (.[0] | type == "object" and .decision != "block")' "$fixture/output" >/dev/null
[ -f "$fixture/docs/decisions/INDEX.md" ]

printf '{"stop_hook_active":false}' | VERIFY_EXIT=1 bash "$hook" >"$fixture/output" 2>"$fixture/errors"
jq -se 'length == 1 and (.[0] | .decision == "block" and (.reason | contains("verify-fast.sh")))' "$fixture/output" >/dev/null

printf '{"stop_hook_active":true}' | VERIFY_EXIT=1 bash "$hook" >"$fixture/output" 2>"$fixture/errors"
jq -se 'length == 1 and (.[0] | .decision != "block" and (.systemMessage | contains("still failing")))' "$fixture/output" >/dev/null
find "$fixture/.harness/verification" -type f -name 'run.*' | while IFS= read -r log; do
  grep -q 'Fixture verification output' "$log"
done
[ "$(find "$fixture/.harness/verification" -type f -name 'run.*' | wc -l | tr -d ' ')" = "3" ]

printf '# Undated choice\n' >"$fixture/docs/decisions/undated.md"
printf '{}' | bash "$hook" >"$fixture/output"
jq -se 'length == 1 and .[0].decision == "block"' "$fixture/output" >/dev/null
grep -Fq 'docs/decisions/undated.md' "$fixture"/.harness/verification/run.*
printf 'Stop hooks: fast routing, timeouts, index rebuild, and bounded failure reporting passed.\n'
