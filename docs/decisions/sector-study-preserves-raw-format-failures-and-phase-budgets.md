# Sector study preserves raw format failures and phase budgets

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas
- **Area:** harness, sector-study protocol, report

## Context

During the authorized full cohort's initial phase, some models returned JSON
numbers where the response schema requested numeric strings, or used `empty`
instead of an empty unit string. These outputs contain interpretable answers;
discarding them would confound response representation with task competence.
The initial 4096-token allowance also produced genuine truncated answers.
Lucas authorized autonomous resolution and continuation of the full study.

## Decision

Normalize only lossless JSON representations: numeric primitives to their
string form, and explicit unit aliases to the corresponding allowed unit.
Reparse all eligible initial raw outputs without additional model calls and
store the result as a separate interpretation job with source-text and parser
hashes. Keep the original terminal validation failures and raw text unchanged.
Do not repair or resample missing, timed-out or truncated outputs.

Before any full-cohort disputes, record phase-specific output allowances:
4096 tokens for original answers, 8192 for defences and 2048 for short juror
ballots. The original-answer budget and prompts do not change. Every role uses
the same allowance across models; reasoning settings remain model-specific.
Record executor/parser source hashes and the amendment in the immutable study
manifest and versioned artifacts. This is a disclosed protocol amendment, not
an unreported change to completed observations or source references.

## Consequences

Reports distinguish raw structured-output failures, normalized usable answers,
and genuine incomplete generations. The current benchmark answer remains the
same number/label; neither confidence nor reference correctness determines
eligibility for normalization. All accepted initial answers keep their exact
original visible-output hash across every challenge. Larger defence budgets
reduce avoidable reasoning truncation but do not equalize effective compute.
Initial versus defence comparisons retain this resource difference explicitly.
The API cap and unresolved monetary holds remain intact.
