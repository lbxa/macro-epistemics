# Peer-review extensions

## Frozen parent and authorization

Lucas requested implementing the peer-review feedback with delegated work.
Retain parent run `da7e42f28ba54247`, artifact
`lbxa-corp/apart-epistemics-sprint/sector-study-da7e42f28ba54247:v128`,
digest `7d7230ca4d18fc07c1bb8e0009cdbc1d`. All parent observations remain
read-only. The new protocols are numerical replications, not new industries
or replacements for the completed five-model cohort.

## Runner and bounded dispatch

- Cloud host: `gpu-alder`.
- Workspace: `/workspace/apart-epistemics-sprint-sector-20261115`.
- Tracking: `https://wandb.ai/lbxa-corp/apart-epistemics-sprint`, standard API.
- Inference: existing native Cloudflare models only.
- Objection-v2 ceiling: $50; output `harness/results/peer-review-objections`.
- Judge-context ceiling: $20; output `harness/results/peer-review-judges`.
- Dispatch deadline: `2026-11-17T07:45:00+00:00`.
- Source archive SHA256:
  `445bf75480e3ef399c79ee32bcd8ff802fad648a57e154fcfc15878742c2a4ae`.

Preparation verifies exact v128 file hashes. The numerical rerun retains
300 original assignments: 286 supported scalar originals, 13 unavailable
initials and one unsupported non-scalar original. Five seeds give 1,500
assigned branches, including 70 explicitly unavailable branches. At most
1,430 defences and 4,290 ballots may be called; each supported panel executes
the existing Rust/HTTP/Anvil settlement protocol.

The standalone judge comparison contains eight source groups, four errors
and four correct controls. Two judge families, three contexts, five seeds and
three calls per cell give 720 assigned calls. One error is the historical
trigger; analysis also excludes that source. Checked evidence is operator-
verified source arithmetic, not independent human adjudication. Categorical
extensions wait for qualified review. Proof cards and selection are frozen
before any new judge outputs.

## Recovery and admission

Before dispatch, read-only recovery found the parent finished, no active W&B
runs, and no active campaign collector on the cloud host. The new journals
and ledgers are separate from historical spending, including unresolved holds.
Each run freezes its source hashes, settings, prices and immutable identities.
Resume preserves terminal failures; no replacement calls are authorized by
an absent upload. Source, price or configuration drift aborts before new calls.

Live progress is in each output's `progress.json` and W&B. Detached logs are
`.harness/peer-review-objections.log` and `.harness/peer-review-judges.log`.
Run IDs, URLs, final artifact versions and measured costs will be recorded
after dispatch. Do not upload credentials, SQLite journals or spending ledgers.
Validate final artifacts and engine receipts before admitting new paper claims.

### Dispatch record

Both jobs started after repository verification passed (516 harness tests
plus 36 integration tests, alongside Rust, Solidity and hook checks). The
final focused suite passed 13 tests locally and 13 on the cloud runner,
including a real settlement. Eight packet/analysis tests also passed locally.

- Objection run: `6cffaa22ee0c470a`,
  <https://wandb.ai/lbxa-corp/apart-epistemics-sprint/runs/6cffaa22ee0c470a>.
- Judge run: `37ae1979dd144603`,
  <https://wandb.ai/lbxa-corp/apart-epistemics-sprint/runs/37ae1979dd144603>.
- Detached launcher PIDs: 739687 and 739688 respectively.
- Reviewed source hashes: `sector_revision.py`
  `92a5f4fb6551ae5918094c04529e42a0dc1922bbbbb100930ab86f47df1fc474`;
  `sector_judge_extension.py`
  `35f0228f1a3595c3db283a9ed5bdb4a9bc49ae95279c8033ad0447461511bca2`.

Initial live inspection confirms paid execution, not just queued jobs.
Ledger holds for active calls are not final charges. No new observation has
yet been admitted into the paper by this dispatch entry.

## Human review

The prepared adjudication packet has zero completed human reviews. Release
only its stage-1 sources and forms first; withhold stage-2 model responses
until both source reviews are frozen and hashed. Model votes cannot close
this requirement. See `ADJUDICATION.md`.

## Completed admission

Both model runs are finished. Numerical collection has 1,430 completed
executions and 70 structural unavailabilities, with 5,630 model requests.
There are 1,400 valid defences and settlements plus 30 aborted panels.
The judge comparison has 720 requests, 681 valid judgments and 39 failed
DeepSeek calls (37 output limits, two timeouts). None of the 37 truncated
visible outputs contains a complete ballot under the original schema.

Immutable artifacts and digests:

- `sector-study-6cffaa22ee0c470a:v20`:
  `179811a3578576b63d2d3c313f08a5e9`.
- `numeric-judge-extension-37ae1979dd144603:v0`:
  `f039f58c821a1c3241a168e5405c0444`.
- `sector-objection-executed-evidence-6cffaa22ee0c470a:v0`:
  `682131423c15be7a17d4cf6108c90376`, producer `2dad059d286a4612`.

The standard API downloaded all three fixed versions. Their file hashes
match `admission.json`, SHA256
`844a2fd0078b2823a1a8196a5c9d07fae1cc63445d76073c90eab88a30f07a56`.
Executed evidence validates 14,118 confirmed receipts and 21,177 public logs.
The 4,863,175-byte safe projection has SHA256
`60c52b2bdfcb98ebd11f1e405cce170ebba1d411b01ae9cca3befd5f8af30b52`.
All original databases remain intact. The read-only admission view excludes
exactly three proven scripted test stores; see `ENGINE-TEST-ISOLATION.md`.

Recorded API charges total $9.229405510906219481326. Accounted spending,
including conservative holds on 23 unresolved requests, is
$12.634819910906219481326. Holds remain in their original cloud ledgers;
no analytics access, top-up, retry or budget increase was required. These
figures exclude cloud-compute costs.

The results are in `report/data/peer-review-results.json`, with source-level
contrasts and deterministic missing-outcome bounds. The complete GPT-OSS
extension does not reproduce a large defence penalty on the three new errors.
DeepSeek's paired defence comparison covers only two eligible sources;
its all-assigned missing-outcome bounds span −28.9 to +31.1 pp. Independent
human adjudication remains the main scientific gate. Do not launch another
campaign merely because completed calls failed to support a broad effect.

## Report archive

The revised working paper is in report run `be3b408f03d8402e`, artifact
`sector-peer-review-report-da7e42f28ba54247:v0`, digest
`c7fe3d37428f6455487b558d1bec6912`. It contains the PDF, manifest and a
13,341,482-byte reproducibility ZIP (213 payload files plus manifest).
Fresh standard-API downloads match all three hashes in `publication.json`.
No submission or change to sharing settings was performed. Next action:
arrange qualified source-first human review; consider a separately specified
larger-output-budget sensitivity for DeepSeek's truncated comparisons.
