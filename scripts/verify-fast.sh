#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# Fixture stubs can override these guards. An accidental real tool call fails
# immediately, even on a developer machine with the full toolchain installed.
guard="$(mktemp -d "${TMPDIR:-/tmp}/veracity-fast-tools.XXXXXX")"
trap 'rm -rf "$guard"' EXIT
cp "$repo_root/scripts/agent-hooks/fixtures/forbidden-heavy-command.sh" "$guard/forbidden-heavy-command"
chmod +x "$guard/forbidden-heavy-command"
for command in cargo rustup forge anvil uv pytest docker docker-compose bun npm pip; do
  ln -s forbidden-heavy-command "$guard/$command"
done
export PATH="$guard:$PATH"
export FORBIDDEN_COMMANDS="$guard/attempts"

for test_script in "$repo_root"/scripts/agent-hooks/*.test.sh "$repo_root"/.claude/hooks/*.test.sh; do
  [ -f "$test_script" ] || continue
  bash "$test_script"
done

python3 "$repo_root/scripts/decision-index.py" --check
if [ -s "$FORBIDDEN_COMMANDS" ]; then
  printf 'Heavyweight commands were attempted during fast verification:\n' >&2
  cat "$FORBIDDEN_COMMANDS" >&2
  exit 1
fi
