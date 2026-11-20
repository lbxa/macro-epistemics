# Separate fast Stop hooks from runtime verification

- **Date:** 2026-11-20
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** Developer tooling and harness

## Context

Both Stop hooks ran the full verification gate at every handoff. The Docker
acceptance stage could overlap two tests, and each participant receives its own
bridge network. Docker Desktop CPU and network pressure interrupted local work
on the sibling project, which used the same gate design.

## Decision

Use `scripts/verify-fast.sh` for Stop with a 30-second cap. Run Foundry,
Rust/Anvil, and Python regressions with `scripts/verify.sh --no-docker` on demand.
Keep the complete gate in CI and explicit `scripts/verify.sh` runs, with one
Docker acceptance case at a time and private participant networks.

## Consequences

Routine handoffs finish after shell fixtures and decision-index checks. Runtime
regressions surface in CI or deliberate verification. Serial acceptance trades
suite time for lower peak daemon load. CI allows 45 minutes for a cold build and
serial acceptance. This supersedes the pytest worker
scheduling in [the earlier lifecycle decision](./parallel-sandbox-lifecycle-and-stepped-mechanics-tests.md).
That decision still governs stepped clocks and bounded sandbox lifecycle.
See the [verification guide](../verification.md) for the entry points.
