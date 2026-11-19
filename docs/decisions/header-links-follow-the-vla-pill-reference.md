# Header links follow the VLA pill reference

- **Date:** 2026-11-17
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** website

## Context

Lucas requested that the header buttons match the supplied screenshot and
[vla.lbxa.net](https://vla.lbxa.net/): white pills with thin stone-grey borders,
compact medium-weight labels and a dark hover state.

## Decision

Use an explicit shadcn Button `pill` variant and `compact` size for the header
artifact links. Match the reference's 34px desktop height while retaining a
44px minimum height below the small-screen breakpoint.

## Consequences

The header links remain server-rendered anchors composed through shadcn's
`asChild`; keyboard focus styling and destinations remain intact. The visual
change is confined to the header in `website/src/pages/index.astro`, using
`website/src/components/ResearchLinks.tsx` and `ui/button.tsx`. Footer links
and Base UI selectors retain their existing variants.
