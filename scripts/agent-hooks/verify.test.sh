#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/veracity-verify-test.XXXXXX")"
trap 'rm -rf "$fixture"' EXIT
mkdir -p "$fixture/repo with spaces/scripts/agent-hooks/fixtures" "$fixture/repo with spaces/docs/decisions" "$fixture/bin"
cp "$repo_root/scripts/verify.sh" "$repo_root/scripts/verify-fast.sh" "$repo_root/scripts/decision-index.py" "$fixture/repo with spaces/scripts/"
cp "$repo_root/scripts/agent-hooks/fixtures/forbidden-heavy-command.sh" "$fixture/repo with spaces/scripts/agent-hooks/fixtures/"
python3 "$fixture/repo with spaces/scripts/decision-index.py" >/dev/null
cp "$repo_root/scripts/agent-hooks/fixtures/verify.sh" "$fixture/repo with spaces/scripts/verify-harness.sh"
cp "$repo_root/scripts/agent-hooks/fixtures/cargo.sh" "$fixture/bin/cargo"
chmod +x "$fixture/bin/cargo"
export PATH="$fixture/bin:$PATH"
export CARGO_CALLS="$fixture/cargo-calls"
bash "$fixture/repo with spaces/scripts/verify.sh"
diff -u "$repo_root/scripts/agent-hooks/fixtures/cargo-calls.txt" "$CARGO_CALLS"

: > "$CARGO_CALLS"
VERIFY_EXPECT_ARGS=--no-docker bash "$fixture/repo with spaces/scripts/verify.sh" --no-docker
diff -u "$repo_root/scripts/agent-hooks/fixtures/cargo-calls.txt" "$CARGO_CALLS"

for failure in fmt clippy test build; do
  : > "$CARGO_CALLS"
  if CARGO_FAIL="$failure" bash "$fixture/repo with spaces/scripts/verify.sh" >"$fixture/output" 2>&1; then
    printf 'Verification hid a cargo %s failure\n' "$failure" >&2
    exit 1
  fi
  [ "$(tail -n 1 "$CARGO_CALLS" | cut -d ' ' -f 1)" = "$failure" ]
done

mkdir -p "$fixture/repo with spaces/contracts"
cp "$repo_root/contracts/foundry.toml" "$fixture/repo with spaces/contracts/foundry.toml"
cp "$repo_root/.foundry-version" "$fixture/repo with spaces/.foundry-version"
cp "$repo_root/scripts/agent-hooks/fixtures/forge.sh" "$fixture/bin/forge"
chmod +x "$fixture/bin/forge"
export FORGE_CALLS="$fixture/forge-calls"
for failure in fmt test; do
  : > "$CARGO_CALLS"
  if FORGE_FAIL="$failure" bash "$fixture/repo with spaces/scripts/verify.sh" >"$fixture/output" 2>&1; then
    printf 'Verification hid a forge %s failure\n' "$failure" >&2
    exit 1
  fi
  [ ! -s "$CARGO_CALLS" ]
done

if VERIFY_EXIT=1 bash "$fixture/repo with spaces/scripts/verify.sh" >"$fixture/output" 2>&1; then
  printf 'Verification hid a harness test failure\n' >&2
  exit 1
fi
[ "$(tail -n 1 "$CARGO_CALLS" | cut -d ' ' -f 1)" = build ]

rm "$fixture/repo with spaces/docs/decisions/INDEX.md"
: > "$CARGO_CALLS"
if bash "$fixture/repo with spaces/scripts/verify.sh" >"$fixture/output" 2>&1; then
  printf 'Verification hid a stale decision index\n' >&2
  exit 1
fi
[ ! -s "$CARGO_CALLS" ]
grep -Fq 'INDEX.md is out of date' "$fixture/output"
python3 "$fixture/repo with spaces/scripts/decision-index.py" >/dev/null

mkdir -p "$fixture/repo with spaces/.claude/hooks"
cp "$repo_root/scripts/agent-hooks/fixtures/verify.sh" "$fixture/repo with spaces/.claude/hooks/failing.test.sh"
: > "$CARGO_CALLS"
if VERIFY_EXIT=1 bash "$fixture/repo with spaces/scripts/verify.sh" >"$fixture/output" 2>&1; then
  printf 'Verification hid a hook test failure\n' >&2
  exit 1
fi
[ ! -s "$CARGO_CALLS" ]
grep -Fq 'Fixture verification output' "$fixture/output"
printf 'Verification: fast gate, Foundry, Cargo, and harness failure propagation passed.\n'
