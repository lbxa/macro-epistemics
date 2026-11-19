# Reference adjudication is source-first and human

- **Date:** 2026-11-17
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** harness/research, report

## Context

Publication feedback calls for independent adjudication of disputed numerical,
legal and scientific references. Automated source checks and model juries do
not supply independent human judgments. Reviewing only selected disagreements
would not establish reference quality across the primary cohort, and showing
model outputs first could anchor the source review.

## Decision

Prepare source-first review for the complete primary cohort. Two qualified
reviewers independently solve the supplied tasks before seeing model answers,
historical grades or jury outcomes. Freeze and hash both source-review forms
before releasing the physically separate response-review stage. Keep the
operator join key withheld from the reviewer materials.

Assess answer correctness, explanation correctness and citation support
separately. Retain the initial judgments during reconciliation; unresolved
ambiguity remains explicit rather than being forced into a binary label.

## Consequences

The process requires human expertise and more review effort than a selected-case
audit. Packet generation, automated arithmetic checks and further model votes
cannot be reported as completed human adjudication. Metadata blinding does not
guarantee anonymity: source prose may reveal its origin.

The packet covers sources and original responses, not every challenge--defence
trajectory. Reproducibility bundles and source-first reviewer distributions
serve different audiences; give initial reviewers only stage 1, not the paper,
repository or complete supplement. The
[adjudication protocol](../../harness/research/sector-expansion/peer-review/ADJUDICATION.md)
owns distribution and reconciliation details.
