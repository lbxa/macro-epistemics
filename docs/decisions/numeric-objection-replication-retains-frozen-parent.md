# Numerical objection replication retains its frozen parent

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** harness, research

## Context

Peer-review feedback requests integrating the repaired numerical objection
generator and rerunning the affected condition. The completed sector study
must remain reproducible; silently changing its generator would mix different
interventions and invalidate its provenance.

## Decision

Run the numerical-v2 objection as a separate replication using the exact
admitted v128 originals, new namespaced job identities, a fresh ledger and
the same Rust/HTTP/Anvil dispute lifecycle. Keep missing and unsupported
assignments visible, and preserve all terminal observations without replacement.

## Consequences

The v2 generator proposes from the public answer and retains a reference-based
veto. This closes the measured legacy inverse-transform defect on supported
inputs; it does not establish universal freedom from information leakage.
Legacy and replication branches can be paired by source/model/seed, but their
collection times differ. The replication's US$50 ceiling is separate from
historical spending. Provider sampling settings remain frozen; current catalog
prices are recorded on resume while the existing ledger enforces the ceiling.
See the [prospective protocol](../../harness/research/sector-expansion/peer-review/objection-protocol.md).
