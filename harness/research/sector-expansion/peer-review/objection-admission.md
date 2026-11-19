# Executed-evidence admission for the numerical-v2 replication

This postprocessing does not change the running experiment. Run it only after
the fresh replication reports complete collection, against the admitted v128
parent and the cloud host's retained `.harness/runs` engine stores.

The admission checks all 1,500 assignments: 1,430 supported branches, 65 missing
initials and five unsupported-policy branches. Completed branches must have
matching frozen originals, objections, defences, votes and terminal contract
views. Partial failures remain explicit and cannot supply settled outcomes.

The exporter reads engine SQLite files through read-only connections and
projects receipt metadata and public-log hashes. It never packages SQLite,
raw signed transactions, reveal material, private conversations, environment
files, provider SDK responses or returned reasoning. The full retained engine
views are checked before projecting away claim and objection bodies; the
archived hashes bind the projection to those checked inputs.

## Architecture contract

1. This module owns post-run admission and safe evidence packaging. Existing
   `sector_archive.validate_episode` owns vote and conservation checks.
2. The capability is checking retained execution evidence, not executing games,
   reconstructing financial authority, generating answers or changing labels.
3. Parent identity, protocol and assignment counts are fixed. Artifact versions
   and receipt availability can change; those remain explicit inputs.
4. Exact source hashes, terminal statuses and one-to-one episode identities are
   admission invariants. Missing, tampered or duplicate evidence aborts admission.
5. Generated API models validate engine views. SQLite and W&B use existing
   standard adapters; no provider client or model inference is invoked.
6. Admission validates sources, enumerates assignments, cross-checks frozen
   records and receipts, then writes a deterministic archive and register.
7. Failed observations remain failed. An invalid archive is rejected rather
   than repaired or treated as successful execution.
8. Processing is read-only and repeatable; stable ordering and gzip metadata
   give reproducible archives. Upload creates a new versioned evidence artifact.
9. Safe allowlisted projections omit recovery secrets and raw transaction data.
   Actual configured credential strings are checked before packaging.
10. Tests cover source and assignment tampering, archive privacy, and extraction
    from a real isolated Rust/Anvil settlement without model APIs.

Upload is a separate explicit CLI action. It requires an exact version of the
finished replication's study artifact and preserves the original artifacts.
