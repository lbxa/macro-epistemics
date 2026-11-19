# Full five-model sector study handoff

## Authorization and scope

Lucas authorized the full run on November 15, 2026, including API costs as
needed and autonomous execution for roughly six hours. The five models are
DeepSeek V4 Pro 0813, GLM-5.3, Kimi K2.6, GPT-OSS-120B and Inkling 2 Small.
The frozen plan has 120 source-group cases, 600 initial answers, 12,000 main
branches and at most 36,000 main juror calls. The predeclared sensitivity
cohort replays one branch per case with three DeepSeek jurors, adding at most
360 calls. Invalid initial answers make their branches unavailable.

The main jury uses GPT-OSS; source grades remain separate. Four domains are
occupational groupings, not representative industry strata. Finance includes
15 FinQA and 15 numerical TAT-QA contexts. Legal and science use ten cases per
reference label. Education uses 15 original erroneous workings and 15 derived
correct-working controls from distinct problems. Source references remain
fallible. Adapters and controls are versioned adaptations.

## Cloud runner

- Host alias: `gpu-alder`, verified Linux, existing configured SSH access.
- Isolated directory: `/workspace/apart-epistemics-sprint-sector-20261115`.
- Setup log: `setup.log`; toolchains and caches are project-local.
- Secrets: mode-600 `credentials.env` at the cloud project root, injected over
  SSH stdin. Never copy it into an artifact or participant input.
- Model inference: native Cloudflare Workers AI only.
- Tracking: `lbxa-corp/apart-epistemics-sprint`, standard W&B API host unless
  explicitly configured. Prior project recovery found 39 runs, none running.
- Run identity, immutable manifest, source hashes, deadline, live counts and
  spend are written by the runner to `harness/results/sector-full/`.

No existing host workloads are modified. Builds use eight CPU jobs. The cloud
container lacks chown capability; archive extraction must use
`--no-same-owner`, and macOS `._*` sidecars must not enter source archives.

## Recovery and budget

The campaign uses its own $1,500 ceiling, under the new authorization; the
micro-trial's ledger and evidence stay separate. Every paid call reserves first
and reconciles neuron receipts. Unknown charges keep their holds. The SQLite
job journal has unique immutable keys and preserves complete, failed and
interrupted observations. Restart does not resample terminal calls.

Inspect `progress.json`, `study.json`, the safe JSONL exports and W&B before
dispatching. Do not infer an unplayed observation from an absent upload.
Recovery SQLite, spending SQLite, secrets and raw SDK calls are excluded from
report artifacts. Live numeric progress and periodic versioned artifacts are
uploaded during collection. The original plan and architecture documents are
directly authored source files.

## Analysis and report

Use paired source-group bootstrap intervals with the same resampled groups
across models/arms. Report initial accuracy and Brier score, unjustified
concessions, corrections and persistent errors, separate jury acceptance,
confidence shifts, completion and sensitivity-panel disagreement. Preserve
all denominators and undefined strata. The five seeds vary generations, not
source documents. Update the paper brief before strengthening manuscript
claims; retain the prior pilot as a separately labelled case study.

This handoff is updated with the actual run URL, collection progress, costs,
analysis revision, admission and review as they become available.

## Live collection — November 16, 2026

The initial-answer phase started at 05:04 UTC in run
[`da7e42f28ba54247`](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/da7e42f28ba54247).
The cloud collection deadline is 10:00 UTC, leaving report-analysis time within
the authorized overnight window. `initial.log` and `progress.json` are live
on the cloud host; W&B receives numeric progress every 30 seconds and evidence
artifacts approximately every two minutes. The job is detached from the laptop.

Before paid dispatch, the full local gate passed 517 harness tests plus Rust,
Solidity and hook checks (`/tmp/apart-sector-full-verify.log`). The cloud's
focused suite passed all 14 tests, including actual commit/reveal/settlement.
The first startup stopped before model calls because the pinned W&B SDK lacks
`wandb.util.generate_id`; the runner now supplies a standard UUID-based ID.
The same frozen cases and zero-charge ledger were preserved. After that
tracking-only fix, the 14 focused local tests passed again.

## Initial admission and source audit — November 16

The initial artifact is `sector-study-da7e42f28ba54247:v8`, digest
`4bf52b200912400eb98317c85de24c4b`. All 600 calls are retained: 552 strict
outputs and 29 lossless interpretations yield 581 usable answers; 19 remain
unavailable. No initial output was resampled. The phase amendment, parser
hashes and original raw failures remain in the artifact. Before main dispute
dispatch, role caps became 4096 initial / 8192 defence / 2048 ballot tokens.

The [source validation register](original-source-validation.json) matches all
120 cases to pinned original bytes and declared MathDial controls. The
separate [source audit](source-audit.json) retains eight post hoc checks:
two unit-adapter defects, three precision differences and three upstream
reference disagreements. The literal scores remain preserved. Independent
human adjudication is pending. `report/data/sector-initial.json` admits only
the completed initial phase; the report must not infer final branch rates
from an early shuffled snapshot.

A selected GLM multiplication error and unanimous GPT-OSS endorsement
motivated the [post hoc arithmetic-context diagnostic](ARITHMETIC-PROBE.md).
`continue-probe.sh` waits for primary completion, then runs 125 standalone
calculator/judge/defence calls on this cloud host with its own US$10 ceiling and
10:15 UTC deadline. It introduces no new Veracity settlements and never
replaces primary observations. The main branch ID and exact source/defence
hashes are retained. `probe.log` and its separate output directory own the
diagnostic's status; do not pool it into the sector estimates.
The pre-dispatch extension adds five GLM responses to the exact checked
arithmetic, preserving the original frozen conversation. The queue now uses
the primary runner lock, so all main exports finish before it reads them.

The full verification gate passed 522 harness tests plus Rust, Solidity,
formatting and hooks on November 16 (`/tmp/apart-sector-final-verify.log`).
Nineteen focused sector/probe tests passed locally; the cloud passed the
three diagnostic context tests before the queue was started. The report
analysis also retains source-group paired contrasts, per-seed sample SD and
variance, confidence-gap intervals and an exploratory descriptive confidence
AUC. AUC has no estimate when one outcome class is absent; it is not a
prespecified significance test or a direct measurement of internal belief.

## Validity artifact and final admission preparation

The cloud recomputed the numerical objection audit with no model calls in
[`79009dae600f475d`](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/79009dae600f475d).
Artifact `sector-validity-audit-da7e42f28ba54247:v0`, digest
`698f703d0ff227544c8bb9f7d4e833ff`, pins the eight-case source audit,
original-source/normalization checks, the scripted inversion audit and code.
The inverse recovers 287/287 stored numerical references, including 38
initial mismatches. The future proposal policy adds no matches among 37
supported errors; one nonscalar original is unsupported. This does not show
that current models used the inverse. The frozen campaign is unchanged.

The latest full verification passed 532 harness tests plus Rust/Solidity/hooks;
45 report tests pass. The cloud passed all four arithmetic diagnostic context
tests. `sector_archive.py` is installed on the runner; a read-only live audit
validated 7,134 completed main episode views, including aborted panels,
against their frozen votes and contract totals. Run the final archive only
after collection finishes, and retain its separate immutable artifact.

The report now uses Lucas's concurrent title update, **Macro-Epistemics:
Confidence Under Dispute**, and preserves all four main-text case panels from
v35. The additional arithmetic example is branch
`11c495e81bb48bcc53c14f421794`, also in v35: GLM's false product
`1084 * 108.51 = 117628.84` receives three supporting GPT-OSS votes. The exact
product is 117624.84. `report/analysis/arithmetic_probe.py` keeps that source
example separate from the queued 125-call diagnostic and makes no new
settlement claim for the standalone calls.

Final report work: admit an immutable export with all 12,000 main assignments;
regenerate `sector_results.py` assets, then incorporate
`sections/sector-appendix.tex` and its coverage, seed-SD, forecast and domain
charts. Preserve literal and audited variants and the four source-located
panels. Admit final sensitivity and arithmetic results separately, build and
inspect every PDF page, and upload the final safe report/source artifact.
The venue allows eight main-text pages; references and appendices are excluded.

## Complete primary matrix admission — 09:01 UTC

Immutable `sector-study-da7e42f28ba54247:v117`, digest
`efac632306fc5496238031b734369bcd`, contains all 12,000 primary assignments.
The 380 failed branches are exactly 19 unavailable initials times 20; 11,620
branches executed, yielding 11,483 valid defences and 11,469 settled verdicts.
The cloud audit validated every executed evidence view: 10,848 creator
settlements, 621 challenger settlements and 151 aborted panels. Initial bytes
match admitted v8. Local download register:
`harness/results/sector-main-admitted/download-register.json`.

The portable full snapshot, figures, tables and CSVs are regenerated. Main-text
results retain all four concurrent case panels and distinguish low concession
from low repair, source agreement from acceptance, and repeated generations
from independent sources. The working PDF has eight main pages after editorial
trimming. Final sensitivity/probe admission, safe evidence archive, all-page
visual review and immutable report upload remain to be completed.

## Final collection, replay and diagnostic — 09:30 UTC

Primary collection finished at 09:22:39 UTC. Final export:
`sector-study-da7e42f28ba54247:v128`, digest
`7d7230ca4d18fc07c1bb8e0009cdbc1d`. All frozen initial and main branch files
match the previously admitted bytes. Replay: 113 executed of 120 selections,
four aborted DeepSeek panels, 109 paired verdicts, 108 agreements. Seven
selected defences are unavailable. Both panels uphold ten reference mismatches;
DeepSeek upholds one additional legal mismatch. This is not a full crossed
judge experiment or a replacement for external grading.

Evidence audit run `e0de63bb41b8419b` produced
`sector-executed-evidence-da7e42f28ba54247:v0`, digest
`bd0ff1ba88bcafab1b9351c6d5166daf`. Cloud contract validation and local archive
checks cover all 23,466 evidence/frozen-defence files. Archive SHA256:
`119421fddd41645fef274e27f33653dbbdb0bdd2bac5a797c0d69b7fefdc7774`.
Its input hashes match final v128. Recovery databases/ledgers remain protected
on the cloud runner, outside artifacts.

The separate diagnostic run `4ad9a8544dff473f` finished with 124/125 usable
calls and no replacement generations. Artifact
`arithmetic-diagnostic-4ad9a8544dff473f:v0`, digest
`17469e0e688c710966d533d7e2e4bd79`. Both judge families calculate correctly in
15/15 bare calls; claim-only correct rejections are 15/15 DeepSeek, 14/15
GPT-OSS. With the frozen false defence they fall to 3/15 and 0/15; explicit
verified arithmetic restores 15/15 for both. Four valid GLM checked-author
replies correct and withdraw the original; one output is unavailable. There
are no diagnostic game settlements. Do not assign author jury forecasts the
verdicts of different defence contexts.

Primary recorded token-priced charges are US$65.815134873054504403609;
US$17.61312768 remains conservatively reserved for 103 requests without
reconciled usage. Diagnostic charges are US$0.203834639135360716978, with no
unresolved requests. These are ledger accounting values, not a reconciled
Cloudflare invoice; cloud compute is outside the API ledger. No budget top-up,
account configuration change or new provider route was used.

All paid collection is complete. Remaining work is final deterministic
verification, PDF inspection, review record and safe report artifact upload.

## Final report archive — 10:00 UTC

The report is complete as a research draft, with eight main pages, one
reference page and twenty appendix pages. Its 223-word abstract, source-group
intervals, five-seed SDs, domain and benchmark charts, four main-text examples
and separate arithmetic diagnostic are reviewed. All 29 pages were visually
checked; the final clean build has no layout/reference warnings and all fonts
are embedded. Independent source adjudication and author scientific approval
remain open; there is no submission or new public release.

Report run:
[`d6279cd7cd7b4136`](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/d6279cd7cd7b4136),
state `finished`, summary `validated-draft`. Immutable report artifact:
`sector-report-da7e42f28ba54247:v0`, digest
`846fb47c019f51fc8418cd73596e2283`. Its 107 files include source, portable
snapshots, generated assets, verification logs and manifest. All uploaded
manifest digests were checked on the cloud; a fresh canonical-API download
of the PDF exactly matches the reviewed local file. PDF SHA256:
`fc25f5eb4105d2e732c3abdd0d6b35e7a4ca50ef2f17f49a480444e9b8acb688`.
`report-publication.json` pins the publication and manifest; the source-level
`evidence-register.json` pins all input cohorts and checks.

The optional W&B run-media preview lacked Pillow in the locked cloud harness.
The report artifact had already uploaded successfully. The same actual report
run was resumed and finished using retained PNG/PDF artifact files, without
adding dependencies or making model calls. The SDK default selected a different
API host when unset; completion and verification explicitly used
`WANDB_BASE_URL=https://api.wandb.ai`. Future standalone diagnostic/archive
clients now follow the main runner's explicit canonical-host policy, honoring
an environment override. That post-collection guard does not change frozen
runtime source hashes or results. See the
[tracking decision](../../../docs/decisions/standalone-sector-tools-pin-the-canonical-wandb-api.md).

No model collector remains running. The next scientific step is independent
adjudication, followed by a preregistered fresh-source replication of the
defence/evidence comparison with matched controls. More repetitions on the
same disputed references would not resolve their validity.

Final post-collection verification also passes after the host guard:
`/tmp/apart-sector-final-verify-5.log`, 532 harness tests in 425.70 s, plus
Rust/Solidity/hooks/formatting/Clippy/builds. All 45 report tests pass; decision
index and whitespace checks pass. The published PDF and scientific source
files remain byte-identical to the admitted report snapshot. No work remains
running. Preserve the cloud journals and spending holds for inspection; no
additional collection or resampling is scheduled.

## Comprehensive offline report expansion — 2026-11-16

Lucas requested the intermediate, ordinary, null and failed outcomes behind
the summary charts. No collector was restarted and no model call was made.
The source bank was inventoried read-only; pinned raw exports supplied a
whitelisted 47,133-call metadata projection and six systematically selected
visible exchanges. All new readouts are marked exploratory and preserve the
original cohort, grades, missingness and source-group dependence.

The expanded report has eight main pages, one reference page and 55 appendix
pages. Appendix N retains all 80 model/domain/condition grade-transition rows,
120 paired contrasts, 50 confidence bins, matched forecast targets,
stance/support checks, jury confusion and margins, literal quotation checks,
five-seed histograms, categorical confusions, grading sensitivities, resource
receipts, all 120 source rows and a separate pilot section. Ten new CSV
families include the 2,400-row source/model/condition ledger with ordered seed
bits and branch IDs. Six new quantitative figures and six visible panels
supplement the preserved main-text examples.

Immutable report artifact:
`sector-report-da7e42f28ba54247:v1`, digest
`1e687f354c1e79d4f6ab05ad157fce52`. Finished report-only run
[`23ef1e166c254fcc`](https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/23ef1e166c254fcc).
The curated bundle has 175 files and retains source, portable inputs,
generated readouts, PDF, review and verification logs. PDF SHA256 is
`9ab732be30fca65d052e027c1e50b1e07e86c0320ebd8d5e077c5c4cb56b9afc`;
manifest SHA256 is
`ddc8aa91a7c15bb7ab51609cce70f6895c21423834bd1937073dabd91b8415f0`.
The external pointer is `report-publication-expanded.json`; v0 is preserved.

Verification: 53 report tests pass; all 53 checked generated output hashes
repeat exactly; Ruff, whitespace and decision-index checks pass. The full
repository gate exits zero, including 532 harness tests in 424.36 seconds
and Rust/Solidity/hook/build checks (`/tmp/apart-expanded-verify.log`). The
clean PDF build has no layout/reference warnings and embeds all 35 fonts.
Every rendered page was reviewed; the final render is pixel-identical to
the reviewed pages. The review remains a draft, with independent semantic
adjudication and author approval open. No budget, provider route, account
setting, collection policy or protocol was changed.
