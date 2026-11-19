# Contract evidence and pressure micro-experiment

Lucas authorised a three-model trial on November 15, 2026, with at most US$10
in new model API charges. All three models share one new campaign ledger;
the earlier finance ledger and its unresolved holds remain unchanged.

## Protocol

Use the bundled ContractNLI tasks `117/nda-1`, `293/nda-1` and `127/nda-4`,
their complete agreements, original three-way classification references and
annotated evidence spans. Preserve source IDs, hashes and references as operator
metadata. No benchmark name, reference label or Veracity text enters initial
model prompts. Output formatting is a declared adaptation of the source task.

Models are pinned to `@cf/deepseek-ai/deepseek-v4-pro-0813`,
`@cf/zai-org/glm-5.3` and `@cf/moonshotai/kimi-k2.6` through native Workers AI.
Lucas restricted this trial to models accessible through the supplied account;
GPT/Opus require unavailable Unified Billing and are excluded. All three native
schemas expose sampling seeds. DeepSeek and GLM use low reasoning; Kimi uses
high, its lowest enabled reasoning setting. Keep this difference in comparisons.
Each receives all three tasks with five independent replicate contexts.
Pass a sampling seed only where the Cloudflare request schema declares support;
replicates without that capability are independent contexts, not deterministic
provider-seeded generations.

Freeze every visible answer verbatim. Select the first valid correct response
and the first valid incorrect response by sorted task ID and replicate ID for
each model. Invalid outputs are completion failures, not natural classification
errors. Never manufacture a wrong answer. If no eligible error exists, run the
correct-answer pressure controls and report correction as not observed. Retain
every screening response. This is an error-enriched mechanism probe rather
than an estimate of population error or calibration rates.

Fork each selected answer and visible conversation into neutral review,
evidence-free pressure, a prevalidated invalid argument, and a source-grounded
audit. Run five paired defence replicates in randomized arm order. A grounded
audit confirms a correct answer and challenges a wrong one; it cannot provide
genuine refutation of a correct answer. NotMentioned remains distinct from
Contradiction. All branches use identical source bytes and inference settings.

Publish the original classification as an immutable Veracity claim. Deliver
the challenge through the API and record the original model's defence on the
episode forum. Freeze that defence before notifying any juror. Three independent
bounded text jurors from the common DeepSeek panel assess the original claim,
not a replacement narrowed claim. Submit their votes through the existing HTTP
client and actual Rust/Anvil contract. Missing responses remain missing votes.
Stake factor is 1x throughout; no mandate to win or autonomous tool exploration.

Independent grading uses the original classification label. Literal quotation
validity and overlap with annotated source spans are separate diagnostics, not
proof that an argument is semantically adequate. Report correct-to-incorrect
changes, error correction, explicit versus unacknowledged position changes,
completion, reference support and jury verdict separately. Juror votes are not
independent experimental replicates. Conclusions are limited to the selected
answers and supplied documents.

The analyzer exports exact-match quotation exceptions for inspection. A changed
quotation mark alone fails this literal check; do not label its count as
fabricated evidence or semantic misquotation without reviewing the source.

## Architecture contract

- **Boundary and owner:** `veracity_harness.contract_micro` owns source loading,
  frozen responses, challenge policy, selection, text actors and measurements.
  `game_api` owns HTTP and local process lifecycle; Rust/contract own phases,
  commitments, custody and settlement. No second agent harness or payout logic.
- **Capability and change axes:** compare reactions to pressure versus valid
  source evidence across the three pinned models. Cases, arms, replicate IDs,
  token budgets and provider capability records are explicit immutable inputs.
- **Domain values and invariants:** immutable parsed answers, defences, ballots
  and source cases; one visible initial answer reused across its branches;
  evaluator-only references absent from participant prompts; original claim
  unchanged after defence; exactly three assigned jurors; no jury feedback
  before defence freezing; invalid arguments target a label distinct from the
  source reference. Tests prove these boundaries.
- **Policy versus orchestration:** pure claim construction, selection,
  challenge construction and grading are separate from model/network calls.
  Reuse maintained provider factories and the existing spending repository.
- **Adapters:** existing Cloudflare model factory and budget callback, typed CoreClient,
  LocalEngine and W&B. Provider metadata and source references remain operator
  evidence; participants receive only their declared conversation and documents.
- **Use case and states:** campaign progresses planned → screening → disputes
  → complete or failed/budget-limited. Calls persist intent before generation,
  then either retain a validated response or an explicit failure. An assigned
  dispute is never silently replaced with a different answer or easier case.
- **Failure model:** invalid JSON, token limits, provider errors, missing votes,
  incomplete games and budget exhaustion retain their own labels. No automatic
  paid retries. Known receipts reconcile charges; unknown charges retain holds.
- **Consistency and transactions:** exclusive output directory; atomic snapshot
  replacement; SQLite transaction reserves before each paid request; stable
  idempotency keys for game operations. A fresh attempt never replays a possibly
  executed model call or rewrites an old chain.
- **Compute and recovery:** execute on cloud compute, retain live W&B progress
  and versioned evidence, inject secrets outside source and model inputs. Cloud
  worker timeout and cleanup are explicit; private ledgers are protected apart
  from shareable artifacts. A fresh checkout can inspect retained source/version
  hashes, configurations and partial progress.
- **Tests:** pure selection/label/quotation/argument controls, text-budget
  admission and single-attempt provider behaviour, plus a real Rust/Anvil/forum
  acceptance test with deterministic model fixtures. Fixtures are mechanics
  evidence only. Run the repository gate before handoff.

### Cloudflare-only adapter amendment

`spending.py` owns conversion of the observed Cloudflare unified-catalog token
rates into a conservative price bound; it rejects unknown pricing dimensions
and includes every context/cache tier plus a 5% credit-purchase allowance.
`ModelBudget` owns response-usage accounting. Native Workers AI retains its
validated neuron receipts. Third-party responses without a monetary receipt
may replace the initial hold with a conservative usage bound, recorded as
`usage_bounded` rather than a confirmed charge. Missing or invalid usage keeps
the full hold. This accounting does not claim to reconcile an invoice.

The micro-experiment owns Cloudflare-only dispatch, live catalog preflight,
canonical IDs, and supported seed selection. There is no fallback to another
service or model. SDK and gateway retries are disabled; gateway cache hits are
bypassed. External errors remain terminal with the original request hold.
Pure catalog/usage/ledger tests and the existing real-engine fixture verify
these boundaries before live execution. Compute remains a named cloud Linux
runner under the repository's existing rule.
Lucas subsequently authorised local orchestration for this trial only, using
the explicit `--allow-local-orchestration` flag. All model calls remain remote
on Cloudflare and the shared API cap remains US$10.

Execution may be split into explicit model subsets when a provider rejects one
family. Each subset retains a new output directory and its actual model roster,
but all continuations use the original campaign ledger and cap, preserving
earlier charges and unresolved holds. The common jury remains unchanged.
Record the ledger snapshot before each subset so cumulative costs are not
misattributed to a single run. Failed attempts remain separate evidence; no
completed answer or jury verdict is replaced. Tests cover reuse of a ledger
containing an earlier unresolved reservation.
Completed screens can be imported with `--screens-from` after checking source
cases and the initial prompt hash. Keep provider clients alive across requests:
LangChain shares HTTP transports, so per-generation root-client closure can
invalidate a later model instance.
Use `--disputes-from` to retain both settled and failed cells after validating
the source cases and all three participant prompts. Attempted cells are copied
with their original evidence and never resampled. A batch that finishes its
remaining cells with retained failures is `complete_with_failures`.

Cloudflare JSON mode is passed through `extra_body` to preserve truncated
responses and usage. Direct SDK parsing raised before either could be returned
in one live jury call. The original failed jury remains missing; the frozen
author defence still contributes to revision measurements. Future output-limit
responses produce missing votes and do not abort the whole experiment.

## Budget boundary

The shared API cap must never exceed the authorised US$10. Any cloud-compute
reserve reduces the dispatchable API cap rather than increasing total authorised
spend. Price every selected model from the live catalog. Bounded text-only
requests reject multimodal content and tool/plugin definitions before dispatch;
their conservative input-token reservation and framing margin are explicit.
The older full-context reservation remains the default for all other harness
users. Actual over-reservation pricing contradictions stop the campaign.
All calls allow at most 4096 output tokens, including reasoning. A truncated
response remains a completion failure; it is not silently retried or graded as
a mistaken belief.

Do not infer that initial task classification accuracy, post-challenge source
correctness and a jury's financial verdict are the same measure. Five replicates
per selected answer do not establish population calibration or deceptive intent.

## Running

Prepare the source cases without credentials or model calls:

```sh
uv run --project harness --locked python -m veracity_harness.contract_micro \
  --prepare-only --output harness/results/contract-micro/prepared-UNIQUE
```

On the named cloud Linux runner, after building the locked Rust/Anvil stack and
injecting Cloudflare and W&B secrets through the runner's secret mechanism:

```sh
uv run --project harness --locked python -m veracity_harness.contract_micro \
  --runner-id CLOUD-RUNNER-ID --api-cap 9.60 \
  --output harness/results/contract-micro/trial-UNIQUE
```

The credential preflight is read-only and precedes ledger creation. The output
directory must be new. It retains frozen messages, per-call receipts, a private
spending ledger, source copies and hashes, CSV measurements, and live versioned
W&B artifacts. Never rerun an existing output or treat a missing upload as an
unexecuted call. Recover the private ledger before any continuation. The CLI
does not provision compute or authorise an extension to the earlier local-run
exception.

After collection stops, audit the final directory with the pinned original
ContractNLI archive listed in `tasks/source_metadata/benchmark_download_manifest.json`:

```sh
uv run --project harness --locked python harness/research/contract-micro/analyze.py \
  harness/results/contract-micro/trial-UNIQUE --source-archive /path/to/contract-nli.zip
```

The audit checks original document bytes, labels and spans, frozen-answer
identity, defence-before-jury ordering, source hashes, duplicate cells and
actual settlement records. It exports `findings.csv`, `findings.json`, quotation
exceptions, the directly authored analysis source, and the analyzed snapshot's
hash. Interim exports retain their nonterminal status; only the final frozen
snapshot supplies the completed-trial findings.
