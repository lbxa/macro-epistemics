# Sector report retains source-located visible trajectories

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas
- **Area:** report, evidence admission

## Context

Lucas requested restoration of the black-outline model-output boxes and at
least three or four interesting agent examples in the main findings, using
W&B traces. The shared `modelexample` style was intact, but the sector rewrite
removed the old panel inputs from Results. Collection is still ongoing, so
newly inspected trajectories cannot support completed campaign rates.

## Decision

Restore four main-text panels using exact visible explanations, scripted
objections and one juror assessment from immutable artifact
`sector-study-da7e42f28ba54247:v35`. Label them post hoc illustrations and
separate model-reported reasoning from internal belief. Keep initial aggregate
statistics on v8 and leave full dispute-rate claims pending.

## Consequences

The [extractor](../../report/analysis/sector_excerpts.py) verifies W&B manifest
digests, local file hashes, frozen original answers and three-ballot outcomes.
The portable snapshot retains field pointers, row IDs and exact excerpt offsets.
Private SDK reasoning and whole agreements are excluded. The finance panel
preserves the unit-audit distinction; the science panel does not equate a
reference-relative loss with irrational concession.

Use the existing shared black-outline style with local paragraph spacing;
each selected panel and its source note stays together. Move detailed numerical
figures and the grading table to the appendix to retain the main-text limit.
A regression check requires all four panel inputs in the main Results. These
cases complement source-group statistics rather than replace them.
