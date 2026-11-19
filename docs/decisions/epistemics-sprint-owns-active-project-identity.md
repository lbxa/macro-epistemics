# Epistemics Sprint owns the active project identity

- **Date:** 2026-11-14
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** workspace, agent tooling, harness, report

## Context

Lucas requested that the copied project become a self-contained Epistemics
Sprint repository and that inherited skills and project references be adapted.
The checkout includes executable tooling as well as historical experiments whose
external artifact addresses and recorded source identities cannot be renamed
locally without breaking reproducibility.

## Decision

Use `apart-epistemics-sprint` for active environment and default upload identity.
Share repository skills through `.agents/skills/` and a relative Claude symlink.
Remove unavailable skill routing and obsolete local paths. Keep Veracity's
working package/API namespace, and identify imported reports, venue rules, and
evidence as historical rather than relabeling their results.

## Consequences

New work is independent of old sprint tracks and deadlines. The new research
question and venue remain open in `docs/reporting/paper-brief.md` and `venue.md`.
Frozen research scripts and remote run URLs retain their original identities;
reusing them for a new campaign requires explicit configuration review.

## Alternatives considered

Blind replacement would create nonexistent artifact URLs and misattribute old
experiments. Renaming every Veracity symbol would expand the migration into an
API/package change without advancing the requested project separation.
