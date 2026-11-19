# Research landing page preserves the archive header and frozen evidence

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** website, research communication

## Context

Lucas requested a public-facing Macro-Epistemics landing-page draft in the supplied
self-contained Bun/Astro template. Its archive-style title rules and visual
identity should remain consistent across papers. The page should summarize the
research, offer small interactive evidence views, and connect the paper, film and
code without duplicating the manuscript.

## Decision

Retain the template's header layout, including the thick rule above the title and
the thinner rule below it. Generate the research page statically from frozen,
admitted result snapshots. Keep sector initial-answer results distinct from the
legal dispute pilot, and identify proposed work and human-benefit visions explicitly.
Use Astro's native image pipeline and load the film only on request.

## Consequences

The page owns research presentation, not experiment execution or grading. Native
HTML controls and a small local script support exploration without a client
framework or runtime data service. Counts, uncertainty and provenance remain
inspectable alongside the summaries. The local draft uses the existing paper
build and the ignored `video/` production assets; publishing and a final public
media location remain a separate step. See `website/README.md` for the build and
asset handoff.

## Alternatives considered

A manuscript-length page would preserve detail but obscure the central findings.
A new visual theme would weaken the requested continuity with Lucas's research
pages. A dashboard framework or autoplaying video would add browser work before
the reader can reach the research.
