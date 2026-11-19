# Numerical objection revision: frozen-answer replication

This prospective extension tests whether the main numerical revision patterns
persist when the false alternative is derived from the model's public answer
rather than the benchmark reference. It does not replace the sector-v1 run.

## Design and scope

Use all 60 numerical source groups in the completed parent cohort: 30 finance
and 30 education, five author models, and defence seeds 101–105. Reuse each
exact frozen initial response and its original conversation. Missing initials
and unsupported non-scalar answers remain assigned and explicitly unavailable.
Do not generate replacement initials or select on observed treatment outcomes.

The existing `numeric_alternative_v2` policy proposes an offset from the public
answer and uses the literal benchmark grade only to veto accidentally correct
alternatives. Its inverse therefore ordinarily reveals the public answer,
not an independently encoded gold reference. The veto remains an oracle
dependency; this is a test of the specific inverse-transform defect, not a
proof that no information can leak. No reference or correctness label is
printed in the participant prompt.

Keep the misleading objection's wording and false rationale fixed, replacing
only the proposed value and scale with the v2 result. Each supported branch
uses the same three GPT-OSS jurors and Rust/HTTP/Anvil settlement as sector-v1,
at fixed 1× synthetic stakes. Jurors assess the frozen original claim.

Use a fresh journal, ledger, W&B run and namespaced immutable job identities.
The run has a US$50 API ceiling and an explicit UTC deadline. The parent run's
files and terminal observations stay read-only. Seed pairing controls the
schedule, not provider nondeterminism or elapsed time between campaigns.

## Analysis

Report assigned, unsupported, valid-defence and settled-panel denominators
separately. Compare v2 against the corresponding legacy misleading branches
within model/source/seed; use source-group resampling for descriptive paired
contrasts. Retain both literal and source-audited sensitivity grades in the
analysis, and do not describe either as independent human adjudication.
The comparison changes generator policy and collection time; it is not a
simultaneously randomized causal estimate.

## Architecture contract

1. The new revision module owns cohort admission, the v2 objection policy
   integration and run configuration; `SectorStudy` retains call, journal,
   budget and dispute lifecycle ownership.
2. The capability is replaying saved answers under one revised objection.
   Rust/HTTP and Solidity retain all voting and financial authority.
3. Change axes are policy version, provider settings and source hashes.
   Source group, original answer and fixed parent identity remain immutable.
4. Invariants are byte-identical parent inputs, no reference-bearing prompts,
   no paid resampling, frozen defences before ballots, and explicit missingness.
5. Existing Cloudflare clients, Pydantic schemas, SQLite journal, spending
   reservations, `LocalEngine` and W&B are the only adapters.
6. Deterministic preparation constructs jobs; orchestration invokes existing
   lifecycle operations. No second harness or settlement implementation exists.
7. Jobs follow the existing terminal complete/failed/interrupted semantics;
   provider, parser, budget and engine failures are retained without retry.
8. Namespaced keys distinguish this intervention; journal intent commits before
   calls, deterministic API keys deduplicate side effects, and original hashes
   are checked before dispatch and resume.
9. The fresh immutable-cap ledger covers all calls and failures. Live progress
   and versioned artifacts exclude secrets, SQLite and spending ledgers.
10. Focused tests check generator input isolation, exclusions, immutable resume
    and one real engine settlement with the explicit objection and namespace.
    The full verification gate precedes paid dispatch.
