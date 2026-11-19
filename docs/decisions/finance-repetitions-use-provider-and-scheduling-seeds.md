# Finance repetitions use provider and scheduling seeds

- **Date:** 2026-11-14
- **Status:** Accepted
- **Deciders:** Lucas
- **Area:** harness, finance micro-experiment

## Context

Lucas requested five seeds for each synthetic stake level and disclosure
condition, under the existing US$100 API cap. The previous four completed
comparisons seeded participant scheduling but did not send a provider sampling
seed. They cannot count as seeded repetitions. The Cloudflare
[Pro 0813 schema](https://developers.cloudflare.com/workers-ai/models/deepseek-v4-pro-0813/)
accepts a sampling seed with best-effort determinism, not a replay guarantee.

## Decision

Run five fresh matched seeds (20261114 through 20261118) at each of 1x, 10x,
100x and 1000x, applying each seed to scheduling and Cloudflare generation.
Keep the two previously frozen initial answers and their confidence values;
these repetitions measure forecast and jury variation conditional on those
answers. Retain the earlier unseeded comparison as a separate cohort.

## Consequences

There are twenty assigned studies and forty submitted rounds, with three jurors
per round. Report outcomes per round and seed; juror votes are not independent
replicates. Five repetitions expose variation without eliminating chance or
establishing population calibration. The same synthetic stakes, API ledger and
local-orchestration exception apply. Two studies can run concurrently under the
existing shared provider rate limiter; record concurrency as part of the cohort.

### Architecture contract

- **Boundary and ownership:** `finance_micro` owns one frozen-answer study;
  `finance_repetitions` owns the bounded assignment plan, subprocess lifecycle
  and evidence aggregation. The existing runner, provider factory, spending
  ledger and contract retain their responsibilities. No second agent harness.
- **Capability, concepts and change axes:** replicate a study across explicit
  seed/stake assignments. Seeds and stake factors are the planned axes; answers,
  model, prompts and jury size remain fixed. Configuration values are validated
  by existing immutable models.
- **Invariants and policy:** one fresh attempt per assignment; no automatic
  replacement of failures; exactly five assigned seeds per cell; missing or
  incomplete verdicts stay missing. Aggregate only observed contract evidence.
- **Ports and adapters:** the existing Cloudflare factory sends sampling seeds;
  other providers reject this option until supported. Child processes invoke
  the existing study CLI. W&B retains live status, source hashes and artifacts.
- **States and use case:** assignments move from pending to running to complete
  or failed. Terminal assignments are never relaunched by this dispatcher.
  Exclusive campaign-directory creation prevents accidental replay.
- **Failure model:** retain failed/partial children and unknown API holds. A
  failed assignment does not become an upheld or rejected result. No new model
  retry policy or settlement logic is introduced.
- **Consistency and transactions:** persist and remotely publish intent before
  paid calls. The shared ledger reserves each request transactionally. Child
  output directories are exclusive; interrupted campaigns require inspection,
  not blind reruns. W&B artifact versions preserve successive checkpoints.
- **Test strategy:** prove seed propagation to provider payloads and both jury
  configurations, and prove vote aggregation rejects mismatched or incomplete
  evidence. Run focused Python checks and the repository verification gate.

## Alternatives considered

Reusing the original runs would mix provider-seeded and unseeded generations.
Regenerating initial answers would change the existing stake comparison into a
different study. Neither is included in this cohort.
