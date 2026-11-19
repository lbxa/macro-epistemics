# Select controls use compact registry dimensions

- **Date:** 2026-11-17
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** website

## Context

Lucas found the select menu buttons too padded and requested more compact UI
elements. The earlier implementation forced the registry's 32px triggers to
44px and used a 192px domain selector.

## Decision

Restore 32px select triggers with 4px vertical and 8px horizontal padding.
Reduce label spacing and use a 160px domain selector. Keep the existing Base UI
popup composition and the header pill buttons.

## Consequences

The current compact dimensions in `website/src/components/ResearchControls.tsx`
and `website/src/components/ui/select.tsx` supersede the 44px select target
described in the earlier shadcn controls decision and review. Keyboard behavior,
focus styling and chart data handling remain owned by the existing components.
