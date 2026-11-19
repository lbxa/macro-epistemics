# Executed sector study: architecture contract

November 15, 2026. Lucas authorized the five-model, four-domain full study,
additional API spending as needed, cloud execution and iterative report updates
over approximately six hours. GPT-OSS-120B and Inkling join the three pilot
models. The pilot remains a separate frozen cohort.

1. **Boundary and ownership.** The existing harness owns task admission,
   participant inputs, confidence, branching, provider calls and analysis.
   `sector_cases.py` owns reference grading and deterministic sampling;
   `sector_study.py` owns the resumable run. Rust/HTTP and Solidity own actual
   registration, commitments, reveals, votes and financial settlement.
2. **Capability.** Run all five models on the same 120 source-group cases
   (30 per occupational domain), then four challenges and five defence seeds
   for every valid saved answer. GPT-OSS provides three blinded juror calls.
   This common judge is a design choice, not independent ground truth.
3. **Change axes and concepts.** Cases, benchmark grades, frozen answers,
   challenge arms, defence seeds, ballots, settlements, model versions and
   source groups are explicit. Providers, task formats and grading can change;
   actor roles, original-claim identity and contract authority cannot.
4. **Invariants.** Never expose references or operator secrets to participants.
   Freeze the answer before challenges; freeze defence before jurors. Never
   replace a completed or failed observation. Grade the actual submitted
   answer, preserve units, and keep missingness distinct from an incorrect
   answer. Tests cover leakage, grading, split uniqueness and frozen hashes.
5. **Ports and adapters.** Reuse `create_cloudflare_model`, `ModelBudget`,
   `CampaignSpending`, `CoreClient`, `LocalEngine`, and W&B. Pydantic validates
   model output. SQLite is the atomic run journal, not an alternate game
   engine. No new provider SDK or second harness is introduced.
6. **Use cases and policy.** Freeze a manifest; screen once per case/model;
   fork all valid answers; generate defence and blinded ballots; execute votes
   through HTTP; retain evidence; publish numeric progress and safe artifacts.
   Sampling and grading are deterministic functions separate from orchestration.
7. **Failure state machine.** Jobs transition `pending -> running -> complete`
   or `failed`; recovery marks interrupted running work `interrupted`. Complete,
   failed and interrupted jobs are terminal observations. A failed initial
   answer leaves downstream branches structurally unavailable. Provider
   timeouts, output limits and malformed JSON retain their observations and
   spending holds. No automatic paid retries.
8. **Idempotency and transactions.** The immutable key is
   `(case, model, phase, condition, seed, juror)`. Journal intent commits before
   external calls, output before downstream dispatch. A unique SQLite key
   prevents duplicate jobs. API actions use deterministic idempotency keys;
   settlements are recovered from core evidence, never recalculated in Python.
9. **Consistency and observability.** One shared immutable-cap ledger covers
   the campaign, including failures. Secrets enter the cloud host through a
   protected file and never enter prompts/artifacts. W&B receives live counts,
   safe diagnostics and periodic versioned evidence. The runner has a durable
   source snapshot, configuration and handoff for remote inspection. Use an
   isolated cloud directory and CPU build budget on the existing remote host.
10. **Test strategy.** Witness failures for new policies, then test grading,
    challenge generation, leakage, duplicate jobs, restart behavior and
    uncertainty. Exercise a real Rust/Anvil dispute without model APIs before
    paid dispatch. Run the repository verification gate and inspect report
    figures, tables and rendered pages. Fixture results are not model evidence.

The 30 source groups per domain support exploratory case-level comparisons,
not representative economic-sector estimates. Finance uses two source
benchmarks. MathDial grades numerical correction separately from teaching
quality; supplied references remain fallible. Source-group clustered intervals
retain all model/arm/seed observations within a sampled group. The five defence
seeds do not multiply the number of source groups.

GPT-OSS is chosen as the common jury because native compact/open models have
different throughput limits from paid frontier models. The three-call panel is
homogeneous and may share errors. A cross-family judge sensitivity subset is
recorded separately if time permits; it cannot silently change the main panel.

## Selected arithmetic diagnostic

The [post hoc protocol](ARITHMETIC-PROBE.md) uses the existing native provider
factory, `SectorStudy.invoke`, journal and spending reservations for standalone
calculator/judge calls after the primary run. Its module owns only frozen
context construction and the small diagnostic schedule. It introduces no
second game engine and claims no new executed settlement. Source/defence
hashes, correct Decimal decomposition, conditions and failed observations are
retained in a separate W&B run and artifact. The main sector roster, prompts,
records and analysis denominators remain unchanged.
The pre-dispatch extension adds five original-author checked-proof responses,
using the exact frozen initial text and normal defence schema. The source hash
must match before any call. It also makes no new settlement claim.

## Final evidence admission

The harness owns a read-only archival audit after collection. Generated API
models validate retained episode, settlement and balance bodies; identifiers,
votes and totals must match the frozen branch record. Completed records with
missing evidence fail admission, while structurally unavailable branches and
partial failures remain explicit. Archive only retained episode JSON after
rejecting private transcripts and checking actual credential values. Exclude
SQLite, ledgers, credentials and raw SDK logs. A separate versioned W&B
artifact owns the file hashes and archive; Python verifies consistency without
recomputing or overriding contract verdicts or payment rules. An actual Anvil
fixture tests admission and rejection of a tampered vote count.

## Numerical objection leakage audit

`sector_objections.py` owns an offline inverse of the frozen numerical
objection transform and a future candidate policy. Proposals in that policy
depend on the public original answer, while the existing grader only rejects
an accidentally reference-correct candidate. The current campaign continues
with its frozen generator; the new policy is not integrated or silently
applied to old records. Tests prove the old inverse, check unchanged proposals
across different compatible references, and reject accidentally correct
alternatives. Audit results are scripted policies, not model behavior.
