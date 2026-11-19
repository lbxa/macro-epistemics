# Replication evidence exports public receipts only

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** harness, research provenance

## Context

The numerical-v2 replication needs verifiable execution evidence alongside its
model results. The engine's durable SQLite stores also contain signed
transactions, reveal material and other recovery data that do not belong in
research artifacts. Its retained HTTP evidence alone omits receipt records.

## Decision

Validate all assigned branches against the frozen parent and read engine
stores through read-only SQLite connections. Reuse the established terminal
vote and conservation checks, then export only contract-view projections,
original and defence hashes, successful receipt metadata and public-log hashes.

## Consequences

The evidence bundle supports retained local-Anvil execution claims without
publishing databases, signing material or private transcripts. Aborted panels
and partial engine failures retain separate counts; a receipt from a partial
failure does not become a settled jury outcome. These are retained execution
records, not proof of public-chain deployment. See the
[admission protocol](../../harness/research/sector-expansion/peer-review/objection-admission.md).

## Operational follow-up — 2026-11-16

Receipt tests now give Rust a private temporary working directory. Three
earlier scripted fixtures had used the shared engine-store directory and
production-derived episode identities. Because the cloud container denied
complete process-descriptor inspection, the stores remain in their original
locations. A read-only symlink view excludes only those three positively
identified fixtures using retained pytest evidence and exact scripted
artifact markers. Unknown duplicates still fail admission. This preserves
all original databases and their evidence while separating test fixtures
from collection. The view's ownership manifest is retained in the
[operational record](../../harness/research/sector-expansion/peer-review/ENGINE-TEST-ISOLATION.md).
