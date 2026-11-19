# Three-model micro-experiment handoff

As of November 15, 2026, the native Cloudflare trial has completed with Lucas's
explicit local-orchestration exception and one shared US$10 API cap. Earlier
finance charges and holds belong to the earlier campaign.

## Current execution

The active roster is DeepSeek V4 Pro 0813, GLM-5.3 and Kimi K2.6 on native
Workers AI. GPT/Opus were excluded after Lucas restricted execution to models
accessible with the supplied token and existing billing; we cannot administer
or fund the account.

- Opus preflight attempt: `uxjsd0bk`, HTTP 402 with no answer.
- Initial DeepSeek attempt: `ynlsa1xj`, one valid answer retained, then a shared
  HTTP-client lifetime failure. Closing per-call SDK clients was corrected.
- Native attempt: [`bt478zw1`](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/bt478zw1),
  27 settled disputes followed by a jury SDK length-limit exception. The active
  defence was already frozen and remains measured; that jury has no verdict.
- Completed continuation: [`g9t35ump`](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/g9t35ump),
  local output `harness/results/contract-micro/trial-20261115-native-continuation`.
  It copied all 28 attempted cells and generated only unattempted cells.
  Collection ended at 2026-11-16 00:56:33 UTC: 45 screens, 100 assigned
  branches, 99 complete defences and 95 settled verdicts. Length-limited
  responses remain incomplete; they were not resampled.

All attempts share `harness/results/contract-micro/trial-20261115-local/spending.sqlite`.
The valid first DeepSeek answer is imported verbatim. All three unresolved
request reservations remain; do not reset the ledger or replace observations.
Final costs, completion and findings are in `study.json` and the frozen W&B
artifact below. No further model calls are scheduled.

## Intended execution

The original plan named DeepSeek, GPT and Opus. The active native roster above
supersedes it. Each model receives three ContractNLI cases and five
screening replicates. Branch each selected natural correct/incorrect answer
into four challenge conditions with five defence replicates per condition.
The original model defends its own frozen answer. Three common DeepSeek jurors
vote on the original classification; original source references grade the
classification separately. See the protocol and prompts in this directory.

The base Git revision is `c7cfbd779718116ad679a22719bb68ec31ae5825` with
uncommitted experiment changes. A live run must retain its exact source copies,
source hashes, configuration, model versions, seeds, receipts and ledger;
the base revision alone cannot reproduce the uncommitted adapter.

## Cloudflare access and compute

Lucas explicitly instructed that this trial use only Cloudflare. OpenRouter
credentials are irrelevant and must not be requested or used for this trial.
The earlier provider selection is superseded by the Cloudflare-only decision.

Read-only checks on November 15 returned HTTP 200 for the native Workers AI
DeepSeek catalog and Cloudflare's unified GPT/Opus catalog and schemas. The
unified endpoint is `/accounts/{id}/ai/catalog/models`, distinct from native
`/ai/models/search`. GPT and Opus expose no seed field through these schemas.
The account token's catalog access did not establish prepaid credit balance:
the first Opus inference returned HTTP 402. Native inference works for the
active roster. Do not retry the unfunded unified route.

The token still cannot list Containers or AI Gateway administration (HTTP 403).
Workers listing returned HTTP 200 with zero existing services. Gateway admin
access is distinct from invoking catalog models: the documented default gateway
can be created automatically on the first authenticated request. No experiment
compute resource has been created. Lucas subsequently authorised local
orchestration for this trial, with all model inference remaining on Cloudflare.
The existing Wrangler OAuth login was also refreshed non-interactively and
checked read-only. It does not list the supplied experiment account and cannot
access that account's Containers or gateways (HTTP 403). Do not deploy this
experiment into a different account as an implicit substitute.

W&B project scope is `lbxa-corp/apart-epistemics-sprint`, using the standard
`https://api.wandb.ai` API host unless explicitly configured otherwise. The live
run IDs are listed above. Preparation run
[`5md16bxb`](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/5md16bxb)
retains `lbxa-corp/apart-epistemics-sprint/contract-micro-preparation:v0`, digest
`09cbf23fc3e2273e5dbebf3bcbba2a5d`. It contains no model-behaviour evidence.
The displayed Forge URL is returned by tracking; it does not change the API
host used for credentials.

## Verification

The previous `bash scripts/verify.sh` passed on November 15, 2026: hooks, decision index,
Solidity checks, Rust formatting/Clippy/tests/build and all 498 harness tests.
The nine micro-experiment tests include real Rust/Anvil/forum settlement with
deterministic actor fixtures and a rejected-credential admission check. These
tests do not supply empirical epistemic findings for any of the three models.
The Cloudflare-only revision also passed `bash scripts/verify.sh` on November 15:
all 500 harness tests, including the new catalog/usage-accounting checks, plus
the Rust/Solidity/hook checks. No model API calls were made by verification.
The verified preparation is retained as
`lbxa-corp/apart-epistemics-sprint/contract-micro-preparation:v1`, digest
`28863453009c3f66b3ee28fd2e89889c`, including the full verification log.
The Cloudflare-only preparation supersedes that provider configuration in
`lbxa-corp/apart-epistemics-sprint/contract-micro-preparation:v2`, digest
`092c41b3891f01ab720a3b599fb1797a`. It retains the updated source, catalog/schema
evidence and 500-test verification log, with zero paid model calls.
The later native revision passed 502 tests before the jury-truncation fix.
The fix and lossless completed-cell recovery pass 47 focused tests, including a
mocked HTTP length-limit response with preserved neuron receipts. The latest
full gate passed all 503 harness tests plus Rust, Solidity and hook checks;
its log is `/tmp/apart-contract-recovery-verify.log`.

## Frozen evidence and next action

Review [FINDINGS.md](FINDINGS.md) and the generated comparison. The immutable
evidence artifact is
`lbxa-corp/apart-epistemics-sprint/contract-micro-g9t35ump:v734`, digest
`fc3d2a8f00f10f0ffb65e3fcc795a92b`. All 1,237 downloaded files matched the
local evidence. [evidence-register.json](evidence-register.json) records their
SHA256 hashes, the analysis revision and cutoff. The shared ledger matches
the final snapshot: US$1.329688393676757813655 charged, US$1.1526144 reserved,
US$2.482302793676757813655 accounted against the US$10 cap. Preserve this
ledger and all failed attempts; the finance cap is separate.

The independent audit also matched all three cases against the original test
split in the pinned ContractNLI archive, SHA256
`e03fc77bbf8b53e2976a250e81d8a294bc3d5e5fb014521e477dee9340d6287b`.
The local archive is `/tmp/apart-contract-original.zip`; its immutable download
URL is in `tasks/source_metadata/benchmark_download_manifest.json`. After the
runner exited, `analyze.py --source-archive` passed the final audit and replaced
the interim findings. The protocol documents reproduction.
The active output retains the passing 503-test log and test sources under
`verification/`; raw call logs and the spending ledger remain private.

The analyzed `study.json` SHA256, analysis source SHA256 and source-audit result
are retained with the final comparison. The existing strict quote
check flags single versus double quotation marks; inspect exceptions before
calling them evidence errors.

Kimi had no natural error in screening, so its correction result is not
observed. Five branches lacked a verdict, and one lacked a complete defence.
Counts concern selected saved answers; fixture tests establish mechanics only.
Numerical confidence and the effect of Veracity relative to review outside the
protocol remain untested. Further experiments require an explicit design and
must preserve existing spend and authorisation boundaries.

## Post-pilot access diagnostic — November 15, 2026

Lucas subsequently asked which additional models the supplied Cloudflare key
could actually invoke. The [access diagnostic](../sector-expansion/README.md#authenticated-inference-check--november-15-2026)
confirmed GPT-OSS-120B, Inkling 2 Small and DeepSeek V4.1 Flash. It appended
$0.0001157998476028442367 in confirmed charges and two retained reservations to
the same ledger, for $0.0062085998476028442367 additional accounted cost. The
cap remains $10. The pilot's frozen artifact, collection cutoff, costs and
three-model scientific cohort are unchanged; the current live ledger therefore
contains later access checks in addition to the pilot's original entries.
