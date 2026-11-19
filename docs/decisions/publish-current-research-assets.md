# Publish current research assets

- **Date:** 2026-11-19
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** Website and report

## Context

Lucas asked to present Macro-Epistemics as an independent project with a single
attribution in the repository README. The earlier PDF and film also carried
event branding. The evidence export pins the earlier PDF by SHA-256.

## Decision

Publish the current working manuscript on the website. Retain the exact bytes
of the earlier PDF in [the research data directory](../../report/data/archived-sector-paper.pdf).
Retire the earlier film from the website.

## Consequences

The website build verifies both PDF hashes. The frozen evidence export keeps
the archived report's artifact identity, digest and SHA-256 using its new
repository path. The website build no longer downloads or serves the film.
