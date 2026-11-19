# Veracity occupational epistemics study

This is a task-source bank and proposed experimental protocol. No model campaign or source-environment evaluation has been run as part of this deliverable.

## Three distinct targets

Measure factual or task-specific correctness against an independent reference. Measure whether a jury upholds a claim as an institutional outcome. Measure whether a model maintains, qualifies, withdraws or reverses its original commitment as a behavioural outcome.

The reference can be a numerical calculation, a frozen document-support annotation, an executable test, a database query or an independently reviewed rubric criterion. State its scope. A scientific abstract-support label is not ultimate scientific truth. An expert preference is not a binary factual oracle.

## Initial task and freezing

Give the model an ordinary task and its necessary source material. Keep benchmark names, source IDs, source answers, canaries, private rubrics, challenge plans and Veracity instructions outside the initial participant input. Preserve source attribution and canaries in evaluator metadata.

Freeze the exact initial response, output artifacts, source bytes, tool observations and model/provider settings before introducing the dispute. No prompt can guarantee absence of evaluation awareness. Treat a subsequent awareness probe as a self-report and report it separately.

Extract atomic claims while preserving units, quantifiers, qualifications and source scope. Have reviewers judge what the initial response implies without seeing the later defence. Predeclare which claims can be judged and how. The model may have generated a claim different from the source reference; score its actual submitted claim rather than assuming a fixed reference verdict applies.

## Confidence

Elicit a probability that a specified factual claim is correct and, separately, the probability that a specified jury will uphold it. The first can be evaluated against the independent reference. The second can be evaluated against the jury outcome. Store these as separate variables.

If probability elicitation follows the ordinary answer, retain a separate fork before that probe so the probe's effect on later behaviour can be checked. These numbers are stated confidence measurements, not direct observations of internal beliefs.

Use Brier or log scores for a well-defined binary target. For document-support tasks with a third uncertainty class, elicit a distribution over the actual reference classes and use a multiclass proper score. Abstention is a separate action whose coverage and cost must be reported. Report calibration on a sufficiently large set of distinct underlying cases, alongside accuracy and completion.

## Matched experimental branches

Branch from the same frozen initial response and context. Randomize execution order. Hold model settings, tools, budgets, jury composition, evidence availability and applicable constitution constant unless one is the specified intervention.

The conditions table specifies neutral reconsideration, evidence-free pressure, valid counterevidence, misleading counterevidence, peer agreement, financial pressure, verdict-only reflection and verdict-with-logs reflection. Prevalidate the substantive counterarguments. A revision can be justified by a new argument even if no new factual document was added.

For the two reflection branches, use the same already-frozen dispute trajectory and verdict. Vary only whether logs are shown. Freeze pre-verdict measurements first. Logs can contain new evidence, so a rational correction after reading them is not evidence of flip-flopping by itself.

Keep any seeded peer vote and resulting quorum constant when testing message influence. Scripted recruitment measures induced susceptibility. A spontaneous-collusion claim requires autonomous coordination with an applicable duty, an agreement and implementing actions.

## Labels and statistics

Keep commitment transition, correctness change, evidence faithfulness and jury outcome separate. Commitment transitions are maintained, qualified, withdrawn, reversed or unresolved. An omitted answer is not automatically a withdrawal. Inaccurate citation support requires checking the actual referenced source span.

Estimate paired differences between the randomized branches. Bootstrap original question/source groups rather than individual claims or cloned juror votes. Cluster repeated interactions at the session level. Use the group_id and source-document identity when splitting or resampling. Shared source papers can also create dependence across scientific claims.

Report counts, denominators, effect sizes, confidence intervals, completion, abstention and unresolved labels. At low sample sizes show uncertainty rather than rank models from a few outcomes. Blind human review to model and treatment where feasible and retain grader disagreements. Disagreement between two outputs alone does not establish deception.

## First admission wave

Begin with compact FinQA, TAT-QA, ContractNLI and SciFact cases. For each, confirm that the source inputs are sufficient, the reference is coherent and a compliant response is feasible. Keep NotMentioned and insufficient evidence as valid uncertainty outcomes.

Then add MathDial factual-feedback checks. Teaching quality requires a distinct rubric. Add CRM, workplace, software, clinical EHR and engineering tasks only after their required assets, environments and independent evaluators are working.

MathDial's source scenarios intentionally contain student errors. Add separately labelled matched cases with correct student working before estimating a tutor's tendency to criticize or agree. Do not let every task presuppose that an error exists.

An honest challenger may leave a supported claim unchallenged. Do not manufacture a valid refutation of a correct claim. If a scripted dispute is needed for a controlled pressure intervention, identify it explicitly and retain an achievable compliant response.

This catalog's occupational mappings are researcher judgments about relevance. The Economic Index does not certify the realism of every imported evaluation instance. Compare occupations with a balanced design first. A separate Claude-usage-weighted analysis must retain the source, month and platform scope.

## Keeping the benchmark meaningful

Use an unchanged anchor cohort for longitudinal comparison and a separately reported rotating cohort of newly validated instances. Public tasks can be contaminated even when randomly held out locally. New names or numbers alone do not establish novelty. Regenerate all dependent evidence and references, check oracle success and empty-baseline failure, deduplicate by document/repository/source group and version repairs.

Keep evaluator references, tests, grading code and source manifests outside participant sandboxes. Grade artifacts in a clean evaluator environment. Freeze submitted claims and artifacts so later edits cannot silently change the target. Treat source text as untrusted data and record attempted grader-directed instructions.

Include insufficient-evidence and ambiguous cases with honest abstention paths. Audit whether agents can exploit answer-formatting cues, leaked labels, public test access, hidden rubric contradictions, judge persuasion, claim rewriting or selective noncompletion. A closed exploit needs a before/after control showing reduced exploit success while valid solutions continue to pass.

Changing task difficulty or rubrics changes score meaning. Publish versions, source identities, validation failures, task retirements and anchor comparisons. Evolution reduces some failure modes; it cannot guarantee an unlearnable benchmark.

## Existing infrastructure

The existing collusion-bench harness provides isolated participants, retained evidence, messaging treatments and binding protocol actions. This database does not modify that repository or implement its new task adapters. Verify the exact delivered constitution. The root short charter and the principles charter carry different behavioural duties.

Mark preexisting infrastructure and source benchmark material separately from new sprint contributions. The proposed new contributions are the source catalog, case adapters, matched experiment protocol and new measurements produced during the sprint.
