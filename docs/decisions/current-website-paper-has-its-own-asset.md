# The current website paper has its own asset

- **Date:** 2026-11-18
- **Status:** Superseded by publish-current-research-assets.md
- **Deciders:** Lucas Barbosa
- **Area:** website, report

## Context

Lucas approved publishing the current PDF with the project checkpoint. The
public research export already pins the earlier Macro-Epistemics PDF by URL
and SHA-256 as part of its archived evidence.

## Decision

Point the site's paper links at the current working manuscript under its own
filename. Keep the earlier PDF at the URL recorded in the research export.

## Consequences

Both PDFs ship as static assets. The build checks their hashes so a local
rebuild cannot replace either approved snapshot silently. Updating the
working paper does not require rewriting the frozen research export.
