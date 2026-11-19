# Numerical judge-context replication

Declared before new calls, November 16, 2026. This post hoc extension tests
whether the selected arithmetic diagnostic repeats across further frozen
source groups. It does not estimate prevalence in the benchmark population.

## Selection and comparisons

Use the completed parent matrix, not the partial working export. Select
numerical audit-arm defences at seed 101 whose original remains supported by
the author. Exclude the eight source-audit tasks and the ambiguous dandelion
task `mathdial:5000751/1/row495`, which requires semantic adjudication.
Retain all remaining reference-mismatch source groups, selecting one frozen
author branch per source by SHA256 of the protocol name and branch ID.
Select the same number of reference-matching control source groups within
each benchmark, ranked by SHA256 of protocol name and source-group ID.
Controls require the original value and scale to equal the literal reference;
matching within a numerical tolerance alone does not qualify. Selection never
reads the jury outcome. Four mismatch sources and four controls result.

For each source, cross two judge families (GPT-OSS-120B and DeepSeek V4 Pro
0813), three contexts, five seed blocks (101–105) and three isolated calls:
720 assigned calls. Contexts show (1) task, original claim and frozen audit
objection; (2) the same with the frozen author defence; (3) the same with the
defence and a source-located checked calculation. This is a standalone judge
experiment, with no new Veracity settlements. Confidence forecasts remain
hidden from judges. The common outcome is support of the original claim.

`judge-proofs.json` contains source substrings and arithmetic steps checked
with exact rational arithmetic; any declared rounding is explicit. These
are operator source/calculation checks, not independent human adjudication.
The GS buffer case requires interpreting “what percent ... consisted of a
buffer” as the buffer's share of the total requirement. Report its scope
separately from simple arithmetic mistakes. Categorical cases await human
adjudication; no categorical “verified evidence” is manufactured.

Report source-level support and correct-rejection rates separately for
mismatches and matching controls. Pair comparisons within source, judge,
seed and juror. Resample whole source groups within benchmark/outcome strata;
do not treat the 15 calls per cell as 15 independent tasks. Retain failures
and denominators. Report the GPN historical trigger separately and repeat
the mismatch comparison after excluding it. Four errors are a small selected
cohort, so exploratory intervals cannot establish benchmark-wide incidence.

## Execution and architecture contract

1. The new module owns source selection, exact-proof validation, context
   construction and the finite diagnostic schedule; it does not own grades,
   game settlements or provider billing rules.
2. The use case is a fresh, versioned judge comparison of frozen outputs.
   Source groups, contexts, seed blocks, judge families and original support
   are explicit domain concepts and likely change axes.
3. `SectorStudy.invoke`, `StudyJournal`, the existing provider factory and
   `CampaignSpending` own calls, idempotency, validation and spending. W&B owns
   remote tracking. No second provider client or generic persistence layer
   is introduced.
4. Exact source bytes, proof cards, prompts and code hashes are immutable.
   Final observations are never replaced; missing calls are not false votes.
   Tests cover source-dependent selection, jury blindness, proof arithmetic,
   source quotation validation and context isolation.
5. Job keys contain protocol, source branch, judge, context, seed and juror.
   Journal intent precedes each external call. Recovery preserves terminal
   failed/interrupted observations and never automatically resamples them.
6. Model APIs may timeout, return invalid JSON or omit usage. Existing bounded
   call handling retains output failures and spending holds. The new ledger
   has a US$20 ceiling; no top-ups or billing changes are authorized here.
7. Execute only on the configured Linux cloud host with a four-hour dispatch
   deadline. Keep live W&B counts, safe exports and final versioned artifacts;
   do not publish journals, spending ledgers or credentials.
8. Startup validates parent completion, source hashes, proof coverage and live
   tracking before paid calls. Resume rejects changed sources or configuration.
   Operator-reviewed proof cards are required before first dispatch.

No calls have been run merely by creating this protocol. Completion and
results belong to the separate run manifest and evidence register.
