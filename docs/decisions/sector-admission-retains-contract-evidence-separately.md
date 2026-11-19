# Sector admission retains contract evidence separately

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** harness, report

## Context

The live study artifact contains frozen answers, ballots and contract outcome
fields, while full episode views remain on the cloud runner. The report needs
durable, versioned evidence of execution without uploading recovery SQLite,
spending ledgers, credentials or private SDK reasoning.

## Decision

After primary completion, validate retained episode/settlement/balance views
against each completed branch and archive their JSON plus frozen defences in
a separate artifact. Reject private transcripts, credential values, changed
defences and mismatched votes or totals. Keep structurally unavailable branches
and partial failures distinguishable. This implements the authorized study's
evidence and recovery requirements; no public sharing is enabled.

## Consequences

The [archival audit](../../harness/src/veracity_harness/sector_archive.py)
uses generated API models and records per-file SHA256 hashes. It verifies
consistency with the contract's recorded verdict and accounting, rather than
reimplementing financial policy. These are Anvil episodes on cloud compute,
not public-chain settlements. Protected journals remain on the cloud host;
the report artifact contains no recovery databases or secrets.
