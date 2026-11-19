# Analysis of the peer-review extensions

The extension analyses remain separate from the original sector statistics.
They compare repeated calls on frozen source groups; they do not turn the
additional calls into independent tasks or independently adjudicated truth.

## Architecture contract

1. `report/analysis/peer_review_results.py` owns offline extraction, matching
   and new publication assets. The harness owns inference and retained job
   records; the original report statistics stay immutable.
2. The capability is a paired generator-policy replication and a selected
   numerical judge-context diagnostic, each with explicit missingness.
3. Change axes are export schemas, policy version and available observations.
   Source identities, frozen original hashes and the prior cohort are stable.
4. Invariants are unique immutable matching keys, unchanged originals, no
   failed call converted to an incorrect judgment, and distinct reference,
   author-support and jury endpoints.
5. JSON files are the input boundary. The analysis reuses
   `sector_results.audited_numeric_grade`, `sampling_stratum` and
   `cluster_summary` rather than inventing a new grading or bootstrap policy.
   Those dependencies are loaded only for offline analysis, keeping the pure
   matching/admission tests independent of the plotting environment.
6. Extraction validates identities and creates matched records; endpoint
   policy determines eligibility; summarization and rendering consume those
   records. No provider client, retry or new harness is introduced.
7. Assigned, unavailable, failed, valid-defence and settled observations remain
   distinguishable. Unmatched or failed paired outcomes are excluded only from
   the corresponding contrast and are counted in its missingness.
8. Read-only source hashes identify each imported record set. Unique
   `(case, model, seed)` and `(source, judge, condition, seed, juror)` keys reject
   duplicates. Rerunning analysis makes no paid side effects.
9. Computed result files retain source hashes, completion status, exclusion
   counts and methods. New assets use the `peer-review-` prefix and do not
   overwrite frozen sector statistics.
10. Focused tests cover missing paired outcomes, original-hash mismatch,
    duplicate identities and the distinction between true controls and false
    claims. Existing source-group bootstrap tests cover the reused estimator.

Before extraction, the operator selects and downloads immutable W&B artifact
versions through the authenticated API. `admission.json` records the exact
three artifact identities, digests and per-file SHA256 values: raw replication,
raw judge calls and validated executed evidence. The analysis verifies every
consumed file against that register, then binds the executed-evidence
register's input hashes back to the same raw replication. The register is an
operator admission decision, not an untrusted model output. Its SHA256 is
retained in the computed results and the publication review record.

After that admission, run with the report environment:

```sh
MPLCONFIGDIR="$PWD/.harness/report-matplotlib" \
  .harness/report-venv/bin/python report/analysis/peer_review_results.py \
  --revision REVISION_EXPORT_DIRECTORY --judge JUDGE_EXPORT_DIRECTORY \
  --admission harness/research/sector-expansion/peer-review/admission.json \
  --revision-register EXECUTION_ARTIFACT_DIRECTORY/evidence-register.json \
  --output report/data/peer-review-results.json --assets report/epistemics
```

## Generator-policy replication

Enumerate all 1,500 assigned numerical branches (60 source groups, five models,
five seeds). Pair each with its legacy misleading-objection branch. Report
completion and settlement over all assignments; report behavior only when both
members have the required valid outcome. Compute literal and automated
source-audit sensitivities separately. Original reference status defines the
loss or repair stratum; jury acceptance always concerns the original claim.
Support/qualify/retract statements are separate from reference transitions.

For each endpoint, average paired seed differences within a source group and
resample complete source groups within the original numerical sampling strata
2,000 times. Finance retains its two benchmark strata; education retains the
original erroneous-working and correct-working-control strata. The analysis
reuses the existing `sampling_stratum` policy. Also retain paired eligible counts and pooled numerators so
missingness cannot be hidden by a rate. The legacy and revised runs occur at
different times; their contrast is descriptive, not a simultaneous randomized
effect of leakage repair.

## Judge-context diagnostic

Report true controls and proof-checked false claims separately. Compare
defended and checked-evidence contexts with the same source/judge/seed/juror
claim-only calls. Average matched call differences within each source, keeping
its five seeds and three repeated calls together. Reuse 2,000 source-group
resamples stratified by benchmark and correctness class. Provide results with
and without the historical arithmetic trigger source.
The true-control rows repeat unchanged in the exclusion sensitivity, because
the excluded historical trigger belongs only to the false-claim cohort.

For every context contrast, additionally bound the source-mean difference
over all assigned calls. Hold each observed binary correctness outcome fixed
and allow each missing outcome to range independently over zero and one.
The minimum per-call difference uses a missing new outcome of zero and a
missing baseline outcome of one; the maximum reverses those choices. Average
within each source and then equally across the assigned sources. These sharp
missing-outcome bounds are deterministic limits for this assigned cohort,
not 95% confidence intervals or observed votes. They remain distinct from the
bootstrap interval conditional on complete matched calls and require no
assumption that provider failures are random. With no missing calls they
collapse to the observed source-mean difference. They do not resolve
uncertainty about unobserved source groups or establish population prevalence.

The selected eight-source cohort tests whether a failure recurs on additional
numerical tasks. Four proof-checked errors and four controls cannot estimate
the prevalence of the effect in the 120-source cohort, other domains or a
population of tasks. Intervals are pointwise exploratory summaries; boundary
intervals and small strata do not imply certainty about unseen sources.
