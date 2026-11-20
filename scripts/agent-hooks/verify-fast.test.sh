#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/veracity-fast-gate.XXXXXX")"
trap 'rm -rf "$fixture"' EXIT
fixture_repo="$fixture/repo with spaces"
mkdir -p "$fixture_repo/scripts/agent-hooks/fixtures" "$fixture_repo/docs/decisions"
cp "$repo_root/scripts/verify-fast.sh" "$repo_root/scripts/decision-index.py" "$fixture_repo/scripts/"
cp "$repo_root/scripts/agent-hooks/fixtures/verify.sh" "$fixture_repo/scripts/agent-hooks/example.test.sh"
cp "$repo_root/scripts/agent-hooks/fixtures/forbidden-heavy-command.sh" "$fixture_repo/scripts/agent-hooks/fixtures/"
python3 "$fixture_repo/scripts/decision-index.py" >/dev/null

bash "$fixture_repo/scripts/verify-fast.sh" > "$fixture/output"
grep -Fq 'Fixture verification output' "$fixture/output"

printf 'docker info || true\n' > "$fixture_repo/scripts/agent-hooks/forbidden.test.sh"
if bash "$fixture_repo/scripts/verify-fast.sh" > "$fixture/output" 2>&1; then
  printf 'Fast verification accepted a heavyweight tool attempt\n' >&2
  exit 1
fi
grep -Fq 'Heavyweight command entered fast verification: docker' "$fixture/output"
grep -Fq 'Heavyweight commands were attempted during fast verification' "$fixture/output"
printf 'Fast verification: shell fixtures, index checks, and heavyweight tool guard passed.\n'
