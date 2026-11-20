---
name: quality-assurance
description: Review or improve Rust code quality, deterministic tests, linting, formatting, and verification hooks. Apply risk-based testing and maintainable changes without inventing coverage gates.
metadata:
  labels: [quality-assurance, testing, linting, code-quality]
---

# Quality Assurance

Read `AGENTS.md`, `SPEC.md`, and the owning crate's manifest before choosing
checks. The workspace uses Rust 2024, rustfmt, inherited Rust lints, and Clippy
with warnings denied. Preserve the committed `Cargo.lock` and pinned toolchain.

## Verification

Both Stop hooks use `bash scripts/verify-fast.sh` for shell fixtures and the
decision index. Iterate with focused Cargo tests, then use
`bash scripts/verify.sh --no-docker` for workspace formatting, Clippy, tests, and
builds with Foundry and Python regressions. `bash scripts/verify.sh` also runs
Docker acceptance in CI and on demand. Report any unresolved runtime checks.

## Tests That Prove Behavior

Use `#[cfg(test)]` modules for unit tests, crate-local `tests/` for integration
tests, and doctests for public examples. Test public behavior and invariants,
not private implementation details. Keep fixtures deterministic and use local
temporary directories for filesystem tests. Default tests must not require
public RPC, funded wallets, or live model APIs.

As the spec is implemented, prioritize commitment encoding agreement, deadline
boundaries, conservation of funds, transaction recovery, and private observation
isolation. Add Foundry fuzz/invariant tests and local Anvil integration checks
with the owning contract implementation. No numerical coverage threshold is
configured; do not claim an unenforced percentage is a passing or failing gate.

## Code and Review

Prefer typed errors and explicit handling of `Result` and `Option`. Check task
cancellation, resource lifetimes, and error context across async boundaries.
Document public APIs with `///`. Keep domain decisions in their owning modules
and keep external SDK types at integration boundaries. Apply small changes
within the task's scope instead of unrelated cleanup.

Hook changes need observable success/failure tests, valid event output, and
bounded retries. Preserve diagnostic logs under `.harness/verification/` and
report unresolved failures or environmental blockers in the handoff.
