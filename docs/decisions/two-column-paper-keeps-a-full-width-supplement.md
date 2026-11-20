# The two-column paper keeps a full-width supplement

- **Date:** 2026-11-20
- **Status:** Superseded by appendix-prose-flows-in-two-columns.md
- **Deciders:** Lucas Barbosa (two-column layout and numbered output panels)
- **Area:** report

## Context

Lucas requested two-column typesetting and figure captions and references for
the model-output boxes. The evidence appendix uses multipage tables with repeated
headers. LaTeX's `longtable` requires single-column mode.

## Decision

The working paper and references use two columns. Wide figures can span both
columns. The supplement uses a single full-width column for its evidence tables,
figures and explanatory text. Each visible model-output panel receives its own
figure number and caption, including panels that share a float.

## Consequences

The [Results source](../../report/epistemics/sections/results.tex) controls
captions and cross-references. The frozen excerpts remain in their generated
inputs, with their original trace IDs. The
[document outline](../../report/epistemics/sections/outline.tex) controls the
transition to the supplement. Venue-specific typesetting remains open.
