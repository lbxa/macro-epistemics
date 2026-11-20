---
name: verify
description: Choose fast Stop checks, on-demand Rust and Python verification, or the full CI gate.
---

# Verify

Both Stop hooks run `bash scripts/verify-fast.sh` with a 30-second cap. This gate
runs isolated shell fixtures and validates the generated decision index.

Run `bash scripts/verify.sh --no-docker` from the repository root for the fast
checks, pinned Foundry formatting/unit/fuzz/invariant tests, deployment artifact
consistency, `cargo fmt --all -- --check`, Clippy with warnings denied, Cargo tests
(including doctests), all workspace builds, and Python harness regressions.
CI runs `bash scripts/verify.sh`, which also runs real Docker acceptance
serially. Use it explicitly for Docker and integration changes. Setup installs
the locked dependencies and creates `harness/.venv`.

Iterate with `cargo test -p veracity-game-service <test_name>` or the owning
crate's equivalent. Use the on-demand gate for broader local checks and reserve
full local runs for Docker and integration changes. Cargo reuses build artifacts
and still executes tests.

Runtime verification requires local loopback listeners for isolated Anvil nodes,
but no public networks, model credentials, or funded public wallets. Run setup
first to install pinned Foundry and compiler dependencies. In managed sandboxes,
request local test execution escalation when binding is denied; do not convert
these failures into skipped tests. Report missing runtime evidence explicitly.

A failed first Stop requests one repair continuation. A repeated failure emits a
warning and permits a handoff. Logs live under `.harness/verification/`. Include
unresolved failures in the final response.
Direct `bash scripts/verify.sh` always fails if any check fails.
