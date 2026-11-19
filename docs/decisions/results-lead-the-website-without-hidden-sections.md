# Results lead the website without hidden sections

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** website, research communication

## Context

Lucas found the landing page cumbersome and requested primary data front and
centre, removal of the Veracity demo and removal of all accordions. Supplementary
content that needed an accordion should be removed from the page altogether.

## Decision

Place the cohort counts and two primary charts directly after the abstract.
Show all five models together, with a shared domain selector and challenge/outcome
controls beside the second chart. Remove the demo, folded tables, diagnostic
drill-downs, citation block and embedded film; retain direct artifact links.

## Consequences

Both default legal charts are server rendered and readable without JavaScript.
The client script initializes immediately instead of waiting for a disclosure.
Literal and post hoc audited grades, eligible counts, source-group uncertainty,
missingness and the objection-encoding limitation remain explicit. The full
download retains supplementary diagnostics and provenance, without moving all
the former accordion content into the main reading path.

This supersedes the page-layout choices in
[the demo decision](landing-page-demo-is-a-browser-only-teaching-round.md) and
[the earlier compact layout](landing-page-leads-with-demo-and-three-findings.md).
The underlying frozen evidence and report admission remain unchanged.
