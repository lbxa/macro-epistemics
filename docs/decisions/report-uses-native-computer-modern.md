# Report uses native Computer Modern

- **Date:** 2026-11-14
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** report

## Context

The initial scaffold reproduced the supplied Apart PDF's Old Standard TT font.
Lucas requested LaTeX's native default research font instead.

## Decision

Use default Computer Modern for text and mathematics in the active report.
Retain Apart's section structure and the existing layout. This explicit font
override supersedes the Old Standard TT choice in the initial scaffold.

## Consequences

The shared preamble no longer loads OldStandard or overrides native font
encoding. The report intentionally differs from the source PDF's typography;
future edits must preserve Lucas's preference rather than restore that font.
Rebuild and inspect pagination after the font change.
