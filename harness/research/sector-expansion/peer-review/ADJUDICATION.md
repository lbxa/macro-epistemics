# Independent reference adjudication

This packet is **prepared, not adjudicated**. No human reviewer has supplied
a decision. The eight existing numerical checks are an automated post hoc
sensitivity analysis and remain separate from this review.

## Scope and observation unit

Review all 120 source groups, including 30 legal agreements, 30 scientific
claims, 30 finance problems and 30 educational arithmetic problems. This avoids
estimating reference quality from only the eight selected numerical disputes
or the two selected legal/scientific vignettes. The packet also retains all
581 usable original answers for a second review stage. Nineteen unavailable
original answers remain missing; they are not assigned an incorrect grade.

The source group is the independent sampling unit. The five model answers to
one source are dependent evaluations of the same task. Defence seeds and jury
votes do not add independent source groups.

## Reviewer distribution and blinding

Give each of two independently working reviewers this document and only the
`adjudication/reviewer/stage-1/` directory at first. Give them separate copies
of its source-review form. Keep the complete `stage-2/` directory withheld
until both reviewers' source-only forms have been frozen and hashed. Then
release `stage-2/`, with separate copies of its response-review form. Keep
`adjudication/operator-only/` and the historical paper, scores,
model identities, source-audit decisions and jury verdicts withheld until
their first-stage forms are frozen. Do not send reviewers the repository or
join key as the review interface. Blind IDs have no substantive meaning.

The exported metadata omits the benchmark name, old reference, model name,
confidence, condition, seed and verdict. The source prose or writing style
may nevertheless reveal origin or authorship; this is metadata blinding,
not a guarantee that a reviewer cannot infer it. No source text is rewritten
to conceal such clues. `content_sha256` identifies the exact task/document
pair. The operator key retains upstream provenance for later verification.

## Stage 1: solve from the supplied sources

Use `sources.json` and complete `source-reviews.csv` before opening model
responses. Enter reviewer identity, relevant expertise and completion time.
Legal and scientific judgments require appropriately qualified reviewers;
record a lack of expertise and reassign the task rather than guessing.

For each task, supply an answer, exact supporting or contradicting spans,
a derivation where relevant and a short rationale. Mark ambiguity and missing
context explicitly. Multiple defensible answers can remain admissible.

- For numerical questions, state the quantity and unit before calculating.
  Record scale conversions, denominator, sign and rounding. Set acceptable
  precision from the wording and reported source precision before inspecting
  model answers. A percentage change and a percentage-point change are
  different quantities. Do not use the number of decimals in a historical
  reference as the sole justification for a tolerance.
- For legal entailment, use Entailment when the supplied contract supports
  the proposition, Contradiction when it supports its negation, and
  NotMentioned when neither is established. Explain the interpretation of
  scope, conditions, exceptions and unstated requirements. This is a textual
  inference assessment, not a legal opinion about enforceability.
- For scientific claims, use Supported, Contradicted or InsufficientEvidence
  relative to the supplied abstracts. Separate an unsupported component of
  a compound claim from actual contradicting evidence. Distinguish study
  population, intervention, outcome and uncertainty. Do not treat absent
  annotation as proof that a scientific proposition is false.
- For educational problems, solve the stated arithmetic and separately
  identify any error in the student's working. The numerical answer rubric
  does not establish teaching quality.

The `ambiguity` and `insufficient_context` fields take `yes`, `no` or
`uncertain`. Leave no substantive field blank when submitting a completed
review; use `not_applicable` with a reason where appropriate.

## Stage 2: assess the frozen model response

After the operator freezes both source-only reviews, use `responses.json`
and the task lookup in `sources.json`. Complete `response-reviews.csv`.
The packet contains the answer, scale, explanation and cited strings exactly
as parsed from each retained visible output. The 29 lossless parser
interpretations preserve the underlying output; their join records remain
operator-only. No new answer is generated.

Use `correct`, `incorrect`, `ambiguous` or `ungradable` for the answer and
explanation assessments. For citations, use `fully_supporting`,
`partly_supporting`, `unsupported`, `missing` or `not_applicable`. A correct
short answer can have a flawed explanation. A quotation's literal occurrence
does not establish that it supports the claim. Give evidence and rationale
for each material discrepancy. Reviewers should assess responses
independently and should not see each other's forms at this stage.

This packet covers original answers. Assessing whether every challenge and
defence is justified requires an additional, separately blinded trajectory
review. The 11,483 valid defences are not silently treated as reviewed here.

## Reconciliation and analysis

Freeze and hash each reviewer's forms before discussion. Compare the two
source answers, numerical admissibility criteria, ambiguity decisions and
response assessments. Retain every original decision. A third qualified
adjudicator should resolve disagreements using the supplied material and
record the competing rationales, resolution and expertise; unresolved items
remain ambiguous or ungradable. Do not force a majority label onto an
inherently ambiguous task.

Report source-level agreement and disagreement counts by domain before
reconciliation, plus agreement on the answer, explanation and citations at
the response level. Any inter-rater coefficient must state its categories,
eligible denominator and missingness; raw agreement and category marginals
remain necessary. Recompute results with independently admissible labels,
and report sensitivity to unresolved tasks. Preserve literal benchmark grades
and the earlier automated sensitivity beside the adjudicated grades.

This process provides independent human evidence only after qualified people
complete it. Additional model votes or this packet generator cannot substitute
for that evidence.

## Reproduction and inventory

From the repository root, run:

```sh
python3 harness/research/sector-expansion/peer-review/build_adjudication_packet.py
```

The exporter pins artifact v128 and portable snapshot SHA256
`c44d7a3f3963941a0eb661c4a01832005c1742713aaade8b2aeba347d56883f6`
before trusting that snapshot's declared case, initial and interpretation file
hashes. Editing both the raw files and the supplied snapshot cannot create
a newly admissible cohort. It uses the existing
JSON and CSV standard-library serializers, makes no model or network calls
and does not change scores. Exports are blank templates. The exporter refuses
to overwrite a nonempty output directory, protecting completed review forms.

The manifest gives input/output hashes, counts and the explicit pending status.
The operator join key retains source URLs, upstream example hashes, literal
references, the eight previous automated checks and model/job mappings.
It also flags the selected legal and scientific disagreements and a newly
identified MathDial ambiguity (`5000751/1/row495`): the requested number of
sprouting plants may differ from the number surviving immediate consumption.
That note is an adjudication priority, not a resolved label correction, and
is withheld from the source-first reviewer packet.
Files contain public benchmark passages and visible model outputs, not secrets,
private chats or spending ledgers. Distribution remains subject to each source's
reuse terms; provenance URLs are not a blanket redistribution license.

### Architecture contract

The exporter owns offline extraction and metadata separation. The frozen
campaign owns tasks and outputs; qualified humans own adjudication. Inputs
are admitted files and the existing audit registry. Outputs are reviewer
material, blank forms and an operator key. Hash mismatch, wrong cohort size
or wrong usable-output count aborts before export. The exporter adds no
provider integration, retry policy, grading policy or experiment lifecycle.
Stable review IDs and deterministic order make repeated exports comparable;
completed forms must never be overwritten by rerunning the exporter.

## Changelog

### 2026-11-18

- Keep generated source passages, responses and the operator join key out of
  Git. Use the frozen packet or regenerate it locally so the operator can
  distribute each stage at the appropriate time.

### 2026-11-16

- Prepare a complete-cohort, source-first review packet so selected disputes
  do not masquerade as a representative estimate of reference quality.
- Keep the operator join key separate from reviewer material, and keep all
  human decision fields empty until reviewers supply their own judgments.
