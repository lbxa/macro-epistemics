# Sector results retain literal and source-audited grades

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** harness, benchmark, report

## Context

The authorized five-model study exposed shared initial-answer disagreements.
Checking the pinned original records identified two adapter unit defects,
three precision disagreements and three source-reference disagreements. A
literal reference grade can therefore misidentify accurate arithmetic as a
model error. Replacing those scores silently would conceal a post hoc choice.

## Decision

Retain the frozen runtime grades and publish a separate versioned arithmetic
and source-audit sensitivity. Keep every original response and challenge.
Continue the fully crossed assignment because initial correctness never
determines branch admission. Record audit criteria, source quotations and
analysis hashes; independent human adjudication remains pending.

This implements Lucas's authorization to resolve study issues autonomously.
It does not imply his scientific approval of the individual audit judgments.

## Consequences

The [audit registry](../../harness/research/sector-expansion/source-audit.json)
and [analysis](../../report/analysis/sector_results.py) preserve literal and
audited fields. Report both, distinguishing adapter defects from upstream
annotations and rounding policy. The eight checks were selected after seeing
disagreements, so they cannot estimate the prevalence of reference defects.
Categorical source labels remain benchmark-relative. Do not call every
jury/reference disagreement an independently established factual error.

## Alternatives considered

Resampling answers or changing participant material would break the frozen
comparison. Treating every reference as infallible would confound measurement
errors with model behavior. Hiding the original scores would obscure analysis
flexibility. The retained two-grade analysis makes these choices inspectable.
