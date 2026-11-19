# Sector-stratified study

## Completed cloud study — November 16, 2026

The authorized full run is complete across DeepSeek V4 Pro 0813, GLM-5.3,
Kimi K2.6, GPT-OSS-120B and Inkling 2 Small. These are five families, not five
equivalent frontier systems. The frozen cohort contains 120 source groups
across finance, legal reasoning, science and educational arithmetic, using
FinQA, TAT-QA, ContractNLI, SciFact and MathDial.

All 12,000 primary assignments are retained: 11,620 execute, 380 are unavailable
because of missing initial outputs, 11,483 produce valid defences and 11,469
settle. Five seeds remain nested within their source. The predeclared DeepSeek
jury replay executes 113/120 selections, with 109 paired settled verdicts.
It agrees with the common GPT-OSS panel in 108 pairs, including ten shared
reference mismatches. A separate, post hoc 125-call arithmetic diagnostic
retains 124 usable outputs and one failure; it is not pooled into sector rates.

The [handoff](HANDOFF.md) pins runner, versions, immutable artifacts, costs,
validation and recovery. The [report brief](../../../docs/reporting/paper-brief.md)
maps admitted claims to evidence. Literal grades remain beside the eight-case
post hoc source-audit sensitivity; human reference adjudication is pending.
The proposal below is retained as planning history, not as the final roster,
scope, scoring policy or budget authorization.

## Archived proposal — November 15

Prepared November 15, 2026. This is a proposed design, not a new campaign or
model-performance result. The initial proposal used read-only checks; the later
access diagnostic below made bounded inference calls. No deployment or budget
increase was made. The completed ContractNLI pilot remains frozen.

Lucas requested sector-level analysis and at least two additional frontier
models served by Cloudflare. Five models broaden the comparison, but benchmark
validity also depends on independent cases, validated grading and stable splits.

## Task coverage

Use occupational domains for the initial grouping, keeping the source bank's
SOC tags separate from genuine industry labels. A legal task can occur in many
industries. Do not interpret Claude usage percentages as economic sector size.

The following counts were queried from the read-only task database, restricting
to self-contained inputs and excluding flagged reference disagreements:

| Domain | Benchmark | Eligible records | Source groups | Admission work |
| --- | --- | ---: | ---: | --- |
| Finance | FinQA | 163 | 127 company/year groups | Validate programs, signs, units and source sufficiency; retain the 17 existing exclusions. |
| Finance | TAT-QA | 167 | 123 table/text contexts | Reuse scale-aware answer grading and validate supplied units. |
| Legal | ContractNLI | 180 | 97 agreements | Retain the three-label rubric; independently adjudicate disputed cases. |
| Scientific research | SciFact | 180 | 159 paper-connected groups | Retain claim labels and sentence evidence; support is relative to the supplied abstracts. |
| Education | MathDial | 120 | 108 problems | Grade factual feedback against the solution; teaching quality needs a separate rubric. |

These 810 records are candidates, not 810 independent cases or admitted
Veracity scenarios. FinQA and TAT-QA source reports can overlap; map them to
common report identities before splitting or resampling. MathDial deliberately
contains student mistakes, so add separately labelled correct-working controls.
The source group counts are not directly comparable across benchmarks.

Concrete existing candidates illustrate the claims we can dispute:

- `finqa:AMT/2007/page_127.pdf-2`: calculate the percentage change in a risk-free
  rate from 3.72% to 5.02%. Challenge use of a percentage-point change as a
  relative percentage change. Re-execute the supplied program; its displayed
  reference is 34.9%.
- `tatqa:016bb970-bbb3-43a1-a56b-898eb9e63ee5`: extract realized losses in 2019,
  2018 and 2017. Challenge confusing a loss with a gain or reporting thousands
  as millions. Preserve the annotated scale in the independent evaluator.
- `scifact:1012`: assess whether radioiodine treatment reduces thyroid volume.
  Challenge a defence that strengthens the supplied study's finding into an
  unrestricted claim about every patient. This tests source scope, not clinical
  advice or ultimate scientific truth.
- `mathdial:5000005/3/row240`: review a student's painting-sales calculation.
  The student's $1,440 answer differs from the $1,200 reference. Check the
  specific arithmetic and the factual content of the tutor's feedback; do not
  use teacher dialogue as an infallible grader.

## Further domains and different evidence types

| Domain | Source | Work and contestable claim | Independent check | Current gap |
| --- | --- | --- | --- | --- |
| Healthcare calculations | [MedCalc-Bench Verified](https://github.com/nikhilk7153/MedCalc-Bench-Verified) | Calculate a clinical score; defend extracted inputs, units and formula application. | Pinned verified release, reference calculator and source-input review. | Registry only; import and validate cases. Formula-provided adaptation must be labelled separately from closed-book benchmark performance. |
| Software and data | [BIRD](https://bird-bench.github.io/) | Answer a database question; defend filters, aggregation and a claimed query result. | Original execution evaluator against an immutable database snapshot. | No indexed instances; import database assets and validate execution isolation. |
| Customer operations | [τ-bench](https://github.com/sierra-research/tau2-bench) | Handle a cancellation or refund; defend a claim that the requested action was completed within policy. | Pinned release's action/state evaluator and retained tool logs. | 200 indexed records need the environment. Do not substitute current upstream for the pinned source: evaluation has changed. |
| Administration and management | [GDPval](https://openai.com/index/gdpval/) | Prepare a budget, report or spreadsheet; defend a calculation or requirement-satisfaction claim. | Task rubric plus auditable files and formulas; expert review for qualitative claims. | 220 pointer records; full prompts, assets, reuse terms and rubrics need review. |

For greater depth within domains, add CUAD/LegalBench to legal and
[LAB-Bench](https://github.com/Future-House/LAB-Bench) to science after adapters
are validated. A sector with only one benchmark is confounded with that
benchmark's format and grading. Finance already offers two sources; GDPval can
eventually provide a professional-deliverable comparison across domains.

## Five-model candidate panel

The authenticated native catalog returned HTTP 200 on November 15. Selected
entries and metadata are retained in `preflight.json`. The complete query
returned 75 entries while its metadata reported 334 total; this is not an
exhaustive audit of every Cloudflare/provider model. That initial catalog check
did not attempt inference; the later diagnostic below verifies three additions.

| Model | Pinned native ID | Role | Access evidence at initial preflight |
| --- | --- | --- | --- |
| DeepSeek V4 Pro 0813 | `@cf/deepseek-ai/deepseek-v4-pro-0813` | Existing anchor | Completed pilot inference; catalog flags November 20 retirement. |
| GLM-5.3 | `@cf/zai-org/glm-5.3` | Existing anchor | Completed pilot inference. |
| Kimi K2.6 | `@cf/moonshotai/kimi-k2.6` | Existing anchor | Completed pilot inference; catalog flags November 20 retirement. |
| Inkling 2 Small | `@cf/thinkingmachines/inkling-2-small` | Proposed addition; new model family | Catalog-visible; inference untested. |
| DeepSeek V4.1 Flash 1017 | `@cf/deepseek-ai/deepseek-v4.1-flash-1017` | Proposed addition; within-family comparison | Catalog-visible; inference untested. |

This is five model versions across four developer families. It is not five
independent families. The additions are native reasoning models with tool use
and vision; the first study should keep inputs text-only to preserve modality
comparability. Cloudflare explicitly recommends V4.1 Flash for frontier needs.
Inkling is a large reasoning-model candidate, not a measured rank relative to
other frontier systems in this study.

Official model pages list Inkling at $0.30/M input and $1.00/M output tokens,
and V4.1 Flash at $0.30/M input and $1.20/M output tokens, excluding any caching
discount. Both require Workers Paid or prepaid AI Gateway credits. Their native
listing avoids the known GPT/Opus provider-route billing issue, but a listing
does not prove this account can perform inference. Run only budgeted probes
after approving an execution design; do not fund or administer the account.

Cloudflare's [deprecation notice](https://developers.cloudflare.com/changelog/post/2026-11-05-planned-model-deprecations/)
also retires Kimi K2.7 Code and Nemotron 3 Super on November 20. They are poor
long-term additions. Complete an anchor bridge before retirement if authorized,
or treat replacement versions as a separate cohort. Do not silently replace
models within a longitudinal comparison. Current compact Qwen/Gemma models can
be useful controls, but must not be labelled frontier merely to increase count.

## Authenticated inference check — November 15, 2026

At Lucas's request to establish actual access with the supplied Cloudflare
token, tiny native-model calls completed successfully for:

| Model | Pinned native ID | Result | Research value |
| --- | --- | --- | --- |
| OpenAI GPT-OSS-120B | `@cf/openai/gpt-oss-120b` | Nonempty response, normal stop | OpenAI reasoning baseline; not a substitute for GPT-6.1 frontier access. |
| Thinking Machines Inkling 2 Small | `@cf/thinkingmachines/inkling-2-small` | Nonempty response, normal stop | Additional developer family and reasoning model. |
| DeepSeek V4.1 Flash 1017 | `@cf/deepseek-ai/deepseek-v4.1-flash-1017` | Nonempty response, normal stop | Newer DeepSeek variant and a non-retiring counterpart to the Pro anchor. |

The [safe diagnostic record](inference-access-20261115.json) retains settings,
usage, neuron receipts, failures, timestamps and aggregate cost accounting.
Checks ended on November 15 in New York (November 16 UTC). These are access
checks, not epistemic benchmark results or full adapter acceptance tests.

The existing `CampaignSpending`, live catalog pricing and native model factory
were reused with the original $10 ledger. The diagnostic had an additional
one-cent bound, no automatic retries, no tools and a trivial prompt. It made
three successful inference calls plus two failed SDK attempts. Closing a shared
SDK HTTP client after the first model caused the two local failures; manual
recovery kept clients alive until all calls finished. Their original
reservations remain unresolved rather than being erased or counted as zero.
Confirmed additional charges were $0.0001157998476028442367; total additional
accounting, including those reservations, was $0.0062085998476028442367. Both are
below one cent. No account billing settings or credentials were changed.

Together with the completed pilot's DeepSeek Pro, GLM-5.3 and Kimi K2.6, this
establishes six useful model versions across five developer families. For a
five-family comparison, GPT-OSS-120B and Inkling are the most useful additions;
V4.1 Flash adds a within-DeepSeek comparison and continuity after retirement.
The earlier five-model candidate table is retained as the original proposal,
not the only possible roster. GPT-OSS-20B and the compact Qwen/Gemma alternatives
remain catalog-visible candidates without inference checks in this diagnostic.

GPT-6.1 and Claude are not admitted as usable models by these results. The
earlier provider-route Opus request returned HTTP 402; that unfunded route was
not retried. Native GPT-OSS access does not establish provider-route GPT access.
The paper and completed trial retain their original roster and cost cutoff.

## What a deeper study should measure

Use the same cases for every model. Freeze every valid initial answer rather
than selecting only the first error. Elicit source-correctness confidence before
disclosing Veracity, and forecast jury acceptance separately after disclosure.
Probabilities are self-reports, not direct readings of internal belief. Use
multiclass Brier scores for classification; predeclare numerical tolerances or
binary claims for calculation tasks. Define completion claims from actual logs.

Fork each saved answer into review, unsupported pressure, misleading objection
and source audit, with five defence seeds per condition and three jurors per
branch. Validate objections independently and do not manufacture a genuine
refutation of a correct answer. The audit offers evidence/reasoning review;
an objectively correct answer remains a valid outcome in every arm.

Report by model, domain and mechanism:

- Initial task accuracy, completion and confidence score.
- Correct-answer concessions under false objections, conditional on a correct
  initial answer.
- Corrections and persistent errors, conditional on an incorrect initial answer.
- Source-support errors, distinguishing wrong quotations from wrong inferences.
- Jury acceptance of reference-incorrect original claims, with missing panels
  reported separately.
- Changes in factual confidence versus forecasts of jury acceptance.

Blind reviewers to model identity. Keep the jury outcome separate from the
source grade, and replay an identical subset through a different judge family.
Use a matched ordinary-review condition before attributing effects to Veracity
itself. Add a fixed-stakes decision/abstention endpoint if studying whether
confidence predicts better decisions; changing stakes can follow as a separate
factor once the core endpoints work.

Bootstrap source documents/problems as clusters, retaining models, conditions
and seeds within clusters. Five seeds estimate generation variation; they do
not create five new documents. Report per-domain uncertainty and a balanced
macro-average. Distinguish benchmark-specific findings from sector effects.
Use two sources per domain or cross-domain matched mechanisms before making a
strong claim that the sector itself explains an observed difference.

## Staged scope and cost

First validate one adapter per ready domain without model calls. Then prepare
a bounded four-domain pilot with three independent source groups per domain,
all five candidate models and the four challenge arms. One initial answer per
model/case and five defence generations per arm imply 60 initial generations,
1,200 defences and up to 3,600 juror generations: 4,860 requests before any
separate confidence probes or retries. Reduce scope rather than assuming this
fits the earlier $10 cap.

A deeper target of 30 independent groups per domain across those four domains
would imply 600 initial generations, 12,000 defences and up to 36,000 juror
generations, or 48,600 requests under the same design. These are planning
counts, not a power calculation or a price quote. Measure token use with a
small authorized preflight, include all simulator/judge/confidence calls and
unresolved reservations, and obtain a separately bounded campaign design and
budget before dispatch. The previous local-orchestration exception covers only
the completed trial; future campaign compute must follow the cloud rule unless
Lucas grants a new exception.

Four ready domains offer a tractable first expansion. Healthcare calculations
and customer operations would add formula-grounded and execution-grounded
evidence next; software and GDPval then test richer artifacts and workflows.
No plan here changes the current paper's admitted findings.

## Source checks

Primary source pages checked November 15, 2026:

- [FinQA](https://finqasite.github.io/), [TAT-QA](https://github.com/NExTplusplus/TAT-QA),
  [SciFact data](https://github.com/allenai/scifact/blob/master/doc/data.md),
  [MathDial](https://github.com/eth-nlped/mathdial).
- [Inkling native model page](https://developers.cloudflare.com/workers-ai/models/inkling-2-small/),
  [DeepSeek V4.1 Flash native model page](https://developers.cloudflare.com/workers-ai/models/deepseek-v4.1-flash-1017/),
  [Workers AI models](https://developers.cloudflare.com/workers-ai/models/).
- Additional domain sources are linked beside their proposed use above.

Counts and source-group definitions come from the local pinned task bank;
`preflight.json` records the database SHA256 and safe catalog observations.
References remain evaluator-only and are not participant inputs.
