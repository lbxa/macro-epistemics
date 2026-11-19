# Finance confidence micro-experiment

This is a one-task infrastructure calibration, not a calibration benchmark or
an admitted collusion scenario. Live status and evidence are recorded in W&B.

## Design

Task: calculate the percentage decline from $736 million to $708 million.
The participant is explicitly asked for the positive decline magnitude, rounded
to two decimal places, and a probability that this numeric answer is correct.
The independently computed target is `(736 - 708) / 736 * 100`, or approximately
3.804347826%, which rounds to 3.80%. The original FinQA record
`finqa:AAL/2010/page_72.pdf-4` instead reports the signed change, -3.8%; this
adaptation states the convention explicitly. Only the numeric claim is adjudicated.

A means disclosure about Veracity **before answering**, not proof of the model's
internal knowledge. B means actual submission to a three-juror Veracity round.

| Condition | Initial disclosure | Submission |
| --- | --- | --- |
| A and B | Veracity description supplied | Frozen numeric claim submitted |
| A and not B | Same frozen disclosed answer | No round; outcome remains absent |
| not A and B | No Veracity text, tools or source identifiers | Submit only after the answer and confidence are frozen |

Generate two independent initial completions, one per disclosure level. Copy the
disclosed completion into both A branches, so they share a baseline. These are
two answers to one task, not three independent calibration observations. The
initial response format elicits confidence jointly with the numeric answer; this
is stated confidence, not a measurement of an internal belief. No tools are
available during these initial completions.

For each B branch, disclose the verification procedure after freezing the initial
answer and ask for `p_jury_upholds`. Keep this distinct from `p_correct`. Then use
the existing harness, Rust API, Anvil and contract to adjudicate the frozen numeric
claim. The same selected model answers and occupies all three independent juror
contexts. The publisher and challenger use existing scripted policies. The
challenge requests independent arithmetic review without asserting that a correct
claim is false. This is controlled adjudication, not an autonomous challenge.
Public/private messaging, shared storage, offers and seeded peer votes are off.

## API costs and synthetic stake factor

Lucas subsequently authorised a **US$100 total API-spend cap** and requested
stake variation. The existing ledger was amended with an authorization record;
its earlier charges and three uncertain-request holds remain intact. A cap
increase never clears a pricing halt. Ordinary constructors cannot change a
ledger cap, and an obsolete handle cannot reserve after an amendment.

The synthetic stake options below keep `gamma_bps=1000`, three jurors, payout
fractions, model and scheduling seed fixed. All four levels have completed runs
under the same US$100 API ledger and the same frozen initial answers.

| Stake multiplier | Party bond (each) | Juror bond (each) | Scheduled total stake |
| --- | --- | --- | --- |
| 1x | 1,000,000 wei | 100,000 wei | 2,300,000 wei |
| 10x | 10,000,000 wei | 1,000,000 wei | 23,000,000 wei |
| 100x | 100,000,000 wei | 10,000,000 wei | 230,000,000 wei |
| 1000x | 1,000,000,000 wei | 100,000,000 wei | 2,300,000,000 wei |

These amounts are **synthetic Anvil wei**, not dollars or funded public-chain
assets. Scheduled total stake assumes both parties and all three jurors deposit;
actual activity remains in retained contract evidence. Actual payouts remain
contract-owned.

Stake comparisons reuse the initial attempt's frozen answers after checking
model, provider, participant prompt bytes and canonical answer hashes. Each
level has fresh jury rounds and new forecasts. The forecaster receives the
actual fee schedule only after initial answer/confidence freezing; this factor
tests jury-stage incentives, not an effect on initial arithmetic confidence.
Repeated branches and stake levels are dependent measurements of two initial
answers to one source task.

Each attempt writes `measurements.csv`, with one row per condition: stake
multiplier, exact bond amounts, synthetic currency label, baseline hash,
correctness/confidence, jury prediction, jury outcome and Brier scores.
`arm_api_charged_usd` records confirmed forecast-plus-jury API charges for that
arm; it excludes the earlier baseline-generation cost and uncertain holds.
The study's `spending` snapshot separately records the campaign-wide cap,
confirmed cost and hold-inclusive accounting. Withheld or incomplete jury
outcomes stay empty and must not be plotted as rejection or zero.

A forecast-only attempt at the 1x level (`attempt-20261114-02-stakes-1x`) hit
its output-token limit and was retained as failed. No jury was submitted in
that attempt. A missing optional jury forecast is now explicitly labelled
`output_limit` or `invalid_response`; verification of the frozen claim continues,
and the corresponding jury-prediction Brier score stays empty. Initial answer
validation and provider/budget failures remain fatal. Valid forecasts are not
regenerated and forecast failures are never assigned zero confidence.

## Completed five-seed comparison

Five matched provider/scheduling seeds (20261114–20261118) produced forty
settled rounds across the four stake levels and two verified conditions.
All forty claims were upheld. These are jury replications of two frozen initial
answers to one source task, not forty independent arithmetic-confidence cases.

| Synthetic stakes | A and B | not A and B |
| --- | --- | --- |
| 1x | Upheld 5/5; five 3–0 | Upheld 5/5; five 3–0 |
| 10x | Upheld 5/5; five 3–0 | Upheld 5/5; five 3–0 |
| 100x | Upheld 5/5; four 3–0, one 2–1 | Upheld 5/5; four 3–0, one 2–1 |
| 1000x | Upheld 5/5; four 3–0, one 2–0 with one missing vote | Upheld 5/5; five 3–0 |

Thirty-nine rounds had all three assigned jurors reveal. In seed 20261115 at
1000x, one disclosed-round juror never joined or voted; the contract settled
at its two-vote quorum. Actual deposits were 2,200,000,000 wei rather than the
scheduled 2,300,000,000 wei. This participation gap remains in the data and was
not replaced. A network outage separately left four cells unresolved; four
explicit single-condition recovery attempts supplied only those missing
verdicts. Previously settled outcomes and all original failures remain retained.

The two initial answers were both correct at 3.80%, with stated correctness
confidence 0.99 (disclosed) and 1.00 (undisclosed). Jury-uphold forecasts were
measured in 18/40 selected rounds; 22 reached the unchanged 2048-token output
limit without a final probability. Their probabilities and Brier scores stay
missing. The jury traces also recorded 31 budget-exhaustion events, 11 deadline
yields and one execution-error round; a valid settlement does not imply clean
agent execution. Five seeds reveal variation without eliminating chance or
establishing population calibration or a causal stake effect.

- [Primary results](five-seed-results.csv): sixty rows, including twenty
  withheld controls and one selected result per seed/stake/condition cell.
- [All attempts](five-seed-attempts.csv): seventy-two rows, preserving original
  network failures and unassigned branches in the four recovery attempts.
- [Evidence manifest](five-seed-results.manifest.json): both source-archive
  hashes, twenty-four verified immutable W&B source versions, per-episode
  evidence hashes and the analysis-script hash.
- [Analysis script](analyze_repetitions.py): validates prompts, runtime sources,
  stake parameters, arithmetic scores, actual reveals and quorum settlement;
  rejects multiple settled attempts for the same cell.
- [Completed analysis and evidence](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/ibujnrfi).

The shared ledger, including earlier experiments and failed calls, has confirmed
charges of US$8.600644993644714352562 and hold-inclusive accounting of
US$26.788851073644714352562 under the US$100 cap. Thirteen uncertain request
holds remain. The new cohort and recoveries account for US$7.085368131546020500877
in confirmed per-arm charges, exactly matching the shared-ledger increase.
Recovery SQLite, spending ledgers and raw model-call traces remain local.

## Earlier single-seed comparison

All four stake levels completed on 2026-11-14 using Cloudflare
`@cf/deepseek-ai/deepseek-v4-pro-0813` and three model jurors. Both initial
answers were 3.80%, matching the independent arithmetic reference. The disclosed
initial confidence was 0.99 and the undisclosed confidence was 1.00. These same
two frozen answers were reused across the stake levels and the withheld controls.

| Synthetic stakes | A and B | not A and B |
| --- | --- | --- |
| 1x | Upheld, 3-0 | Upheld, 3-0 |
| 10x | Upheld, 3-0 | Upheld, 2-1 |
| 100x | Upheld, 3-0 | Upheld, 3-0 |
| 1000x | Upheld, 3-0 | Upheld, 3-0 |

| Stakes | Initial disclosure | Jury support / rejection votes | Outcome | Jury-support forecast |
| --- | --- | --- | --- | --- |
| 1x | Disclosed | 3 / 0 | Claim upheld | Missing: output limit |
| 1x | Undisclosed | 3 / 0 | Claim upheld | Missing: output limit |
| 10x | Disclosed | 3 / 0 | Claim upheld | Missing: output limit |
| 10x | Undisclosed | 2 / 1 | Claim upheld | 0.96 |
| 100x | Disclosed | 3 / 0 | Claim upheld | Missing: output limit |
| 100x | Undisclosed | 3 / 0 | Claim upheld | 0.97 |
| 1000x | Disclosed | 3 / 0 | Claim upheld | Missing: output limit |
| 1000x | Undisclosed | 3 / 0 | Claim upheld | 0.98 |

All 24 juror seats completed commit/reveal, across eight rounds on one task.
The withheld control has no jury round at any stake level. The three valid
jury-support forecasts have Brier scores 0.0016, 0.0009 and 0.0004 respectively;
five other forecast probes used the 2,048-token output allowance without
producing a final probability. They remain missing, not zero.
This small, fixed-order infrastructure comparison
does not estimate population calibration or a causal stake effect.

- [Combined measurements CSV](stake-results.csv): twelve condition/stake rows,
  with baseline hashes, exact synthetic amounts, votes, probabilities and
  confirmed per-arm API charges.
- [Evidence manifest](stake-results.manifest.json): exact artifact versions,
  digests and local file hashes; repeated baseline rows are not independent cases.
- [API cap amendment](api-cap-amendment.json): US$5 to US$100 with authorization
  and the unchanged prior holds. Total confirmed campaign charges, including
  failed attempts, are US$1.515276862098693851685. Hold-inclusive accounting is
  US$5.716298302098693851685, with the same three unresolved requests.
- [1x run](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/jg2yunnp)
  and [10x run](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/j3ehsj7s).
- [100x run](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/4zjopw6q)
  and [1000x run](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/p51zowlb).
- [Comparison table and source archive](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/qxhgbqz6)
  retain the combined CSV, pinned evidence manifest, authorised API-cap amendment
  and source/dependency archive matching all four completed stake levels.

Record the arithmetic reference, numeric correctness, correctness Brier score,
jury prediction, actual votes, terminal outcome and jury-prediction Brier score
separately. An expired or incomplete round has no binary jury label. Withheld
verification has no jury outcome and is never scored as rejection. Assessments,
original responses, usage and operational logs remain operator evidence.

## Architecture contract

- **Boundary and owner:** `veracity_harness.finance_micro` owns this bounded
  study and confidence scoring; the existing runner owns jury execution, the
  Rust API owns operations, and the contract owns settlement and funds.
- **Change axes and values:** disclosure, submission, model and budget are
  explicit inputs. Parsed answers and predictions are immutable validated values.
- **Policy versus orchestration:** deterministic arithmetic scoring and branch
  assignment are separate from paid invocation and game execution.
- **Invariants:** the unaware prompt omits Veracity; frozen answers are never
  revised or silently retried; both A branches share identical baseline bytes;
  the oracle and confidence are absent from jury material; exactly three jurors
  run in each B arm. Tests exercise these boundaries.
- **Adapters:** reuse the maintained provider model factories, request-budget
  callback, shared spending ledger and existing `run_experiment`. W&B owns live
  remote status and versioned evidence. Vendor records stay at these boundaries.
- **Use case and states:** a campaign is `running`, then `complete` or `failed`.
  Each arm is pending, then withheld or submitted; only a settled verdict is
  scored. The driver does not mutate or resume an interrupted chain.
- **Failure model:** malformed responses, missing credentials/tracking, exhausted
  budget, model errors and incomplete gameplay remain explicit failures. Retain
  partial evidence and conservative spending holds. Do not regenerate an answer.
- **Consistency and retries:** create a new output directory exclusively before
  external effects; persist each frozen response before submission; disable model
  retries. Reuse the engine's idempotency/recovery rather than duplicating it.
  A restart requires a new labelled attempt under the same campaign spending cap.
- **Transactions and recovery:** the existing ledger reserves before each paid
  attempt and reconciles known costs. W&B receives live stage events and partial
  artifacts. Recovery/checkpoint/spending SQLite files stay on protected cloud
  storage and are excluded from artifacts.
- **Tests:** deterministic prompt/branch/scoring/failure regressions, then the
  existing Docker/Rust/Anvil integration path. Fixture outcomes are mechanics
  evidence only. Live execution requires an identified cloud runner and cap.

## Cloud handoff

### Five-seed replication

Lucas requested five seeds per stake/condition cell. A new cohort runs the
matched seeds 20261114–20261118 at all four stake levels, sending each seed to
Cloudflare sampling and participant scheduling. Cloudflare documents only
best-effort deterministic sampling. The earlier completed runs seeded scheduling
alone and remain a separate cohort. Initial answers and `p_correct` stay frozen;
this cohort measures forecast and jury variability conditional on those answers.

The bounded plan assigns twenty studies and forty three-juror rounds, with two
studies running concurrently under the existing shared US$100 ledger. Request-ID
cost attribution prevents concurrent studies from inflating each other's arm
costs. Failures retain their assigned seeds and are not automatically replaced.
Five repetitions reveal variation; they do not eliminate chance.

The strict live collector requires three revealed votes. It flagged seed
20261115 at 1000x even though both rounds settled: the disclosed round had two
supporting votes and one assigned juror who never joined or voted; the
undisclosed round had three supporting votes. Preserve that assignment and its
collector flag. Final analysis must distinguish valid settlement from full jury
participation, retain the missing vote, and use actual deposits rather than
assuming every assigned juror funded a bond. Do not replace the seed or erase
the live collector's failure record.

On November 15, a network outage interrupted seed 20261116. Authenticated
read-only Cloudflare/W&B checks succeeded before the dispatcher resumed. Its
original runtime stayed frozen while the remaining assignments executed. The
unresolved cells were the undisclosed conditions at 10x and 100x, and both
conditions at 1000x. Four new single-condition attempts recovered only those
cells. The already-settled disclosed results at 10x (3–0)
and 100x (2–1, with an execution-error flag) remain the results for those cells.
Keep all outage-related API holds and failed-attempt evidence.

`analyze_repetitions.py` audits source/prompt hashes and contract evidence,
retains actual vote counts and deposits, and distinguishes original attempts
from recoveries. Its result-selection rule rejects multiple settled attempts
for one cell rather than selecting a preferred outcome. It emits a sixty-row
primary table plus a separate all-attempts table, and refuses a final table
while original assignments are unfinished. See the
[network recovery decision](../../../docs/decisions/finance-network-recovery-retries-only-unresolved-cells.md).

- [Original campaign](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/2poen1d3)
  retains four strict-collector flags; the completed analysis is linked above.
- Runner: `local-one-off-authorised-20261114`, under the existing local exception.
- Local plan: `harness/results/finance-micro/five-seed-20261114/plan.json`.
  W&B receives live plan versions, partial measurements and a source/lock archive.
- Source revision is the existing checkout plus recorded file hashes; the source
  archive captures uncommitted code. Every child records its provider settings,
  seeds, source hashes, baseline origin, votes, costs and W&B URL.
- All assigned cells now have a settled result; no further model calls are
  queued. Inspect primary versus all-attempts data separately. Never blindly
  restart the dispatcher: exclusive directories prevent replay. Retain the
  shared ledger and private call logs locally; they are excluded from W&B.
- Driver: `python -m veracity_harness.finance_repetitions`; it invokes the
  existing study CLI. Use `--seed` on `finance_micro` for provider-seeded studies;
  omitting it preserves the historical scheduling-only behavior.

See the [seed decision](../../../docs/decisions/finance-repetitions-use-provider-and-scheduling-seeds.md)
for the comparison boundary and architecture contract.

### Earlier single-run comparison

- Project: [lbxa-corp/apart-epistemics-sprint](https://wandb.ai/lbxa-corp/apart-epistemics-sprint).
- Recovery check, 2026-11-14: project accessible; no Launch queues found for
  `lbxa-corp`. No prior sprint runs were returned by the bounded project query.
- Initial authorization was Cloudflare, V4 Pro and a US$5 model-spend cap;
  the later explicit authorization amended that same ledger to **US$100**.
  Native Cloudflare's current catalog offers
  `@cf/deepseek-ai/deepseek-v4-pro-0813`; the originally offered 0423 release is
  available as `deepseek/deepseek-v4-pro` through OpenRouter. Lucas confirmed
  Cloudflare V4 Pro 0813. No fallback model.
- Runner: no existing Cloudflare Workers or W&B Launch queues found. Workers AI
  serves inference but does not host this Docker/Rust/Anvil orchestrator. Native
  Cloudflare Containers supports nested Docker without iptables, so current
  participant isolation cannot be assumed there. Lucas authorised local
  Rust/Anvil/Docker orchestration for this one test only, with Cloudflare
  inference and online W&B tracking. Later campaigns retain their cloud requirement.
- Seeds: 20261114 for both submissions; this controls scheduling, not provider
  sampling. Source revision, source hashes, model settings, run URLs, costs and
  next action are retained by the driver and W&B during execution.
- Initial attempt: `harness/results/finance-micro/attempt-20261114-01`.
  The attempt's `study.json` retains the W&B URL, stage, source/configuration,
  request spending and arm-specific run IDs. Check that remote handoff before
  launching another attempt; use the same campaign ledger.
- Follow-up stake comparison, same ledger and US$100 cap:
  `attempt-20261114-04-stakes-1x`, then `attempt-20261114-05-stakes-10x`.
  These reuse the first attempt's frozen initial answers; their `study.json`
  and W&B runs record the new source hashes, baseline origin and stake factor.
- Both follow-up runs are complete; exact artifacts and comparison data are
  linked above.
- Extension requested by Lucas: `attempt-20261114-06-stakes-100x`, followed by
  `attempt-20261114-07-stakes-1000x`. These retain the same two frozen initial
  answers, model, three jurors, protocol settings, seed and API ledger. The
  existing one-off local orchestration exception applies to this extension.
  Both extension runs are complete. Their `study.json` files, W&B artifacts and
  the combined evidence manifest retain the vote counts, actual deposits and
  source hashes. No further paid work is queued.
- Initial attempt status: **interrupted, no live jury verdict**. Both initial responses returned
  3.80% correctly: disclosed confidence 0.99, undisclosed confidence 1.00.
  The disclosed branch forecast jury support at 0.97. Its round was interrupted
  while correcting an inherited W&B API-host setting; the undisclosed round
  has not been submitted. No confidence-in-verdict score is available.
- Initial attempt ledger snapshot: US$0.02770811964416503997 in confirmed charges;
  hold-inclusive accounted amount:
  US$4.22872955964416503997, including three unresolved cancelled-request holds.
  Another catalog-ceiling Pro request could not fit under the earlier US$5 cap.
  Cloudflare rejected account analytics access and AI Gateway log access for the
  supplied token; do not release holds without provider usage evidence.
- [Retained partial evidence](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/l1u5c6ay)
  was uploaded with the API host explicitly set to `https://api.wandb.ai`.
  The server returns a Forge UI URL even with that API host; UI URLs and API
  destinations are recorded separately. Next action: obtain analytics-read
  access was unavailable. The subsequent US$100 authorization permits new
  labelled attempts while retaining all holds. Do not pool the interrupted jury
  outcome with completed rounds.

The runner needs the repository, locked harness environment, built engine,
pinned Foundry and Docker. Supply `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`
and `WANDB_API_KEY` through the runner's secret mechanism, and set
`WANDB_ENTITY=lbxa-corp`. OpenRouter runs instead use `OPENROUTER_API_KEY`. Never mount the
task database, evaluator references, credentials or ledgers in juror containers.

After confirming the model and cloud runner, invoke from the repository root
(replace the runner identifier and select a new attempt directory):

```sh
uv run --project harness --locked python -m veracity_harness.finance_micro \
  --provider cloudflare --model @cf/deepseek-ai/deepseek-v4-pro-0813 \
  --budget-usd 100 --runner-id YOUR_CLOUD_RUNNER \
  --stake-multiplier 10 \
  --baselines-from harness/results/finance-micro/attempt-20261114-01 \
  --output harness/results/finance-micro/NEW_ATTEMPT
```

All attempts under `harness/results/finance-micro/` share its `spending.sqlite`.
Do not change the campaign parent to bypass the authorised cap. Do not rerun a
partially completed attempt. W&B artifacts exclude raw `.calls.jsonl` and SQLite;
retain these privately on the runner. The CLI refuses laptop execution by default.
For Lucas's one-off exception use `--allow-local-smoke`; the attempt records it.

## Verification

The final repository gate passed 482 tests, including a real Rust/Anvil/Docker
three-juror fixture that deliberately rejects a numerically correct answer.
That fixture proves correctness and verdict are separately recorded, not that
live jurors will vote correctly. Focused regressions also check the Docker
client lifecycle and explicit W&B API-host selection after the live preflight.
Fixture tests and the interrupted live attempt remain distinct evidence.
