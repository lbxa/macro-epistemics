# Base UI selects hydrate only the filter controls

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** website, UI components

## Context

Lucas explicitly selected shadcn's Base Nova Select, whose options open from a
button, replacing the earlier NativeSelect implementation. Its popup, keyboard
navigation and focus management need client-side React.

## Decision

Install the official Base Nova Select through an explicit `@shadcn-base` registry.
Use the documented items/root, trigger/value and content/group/item composition.
Hydrate the two existing filter groups with Astro `client:load`. Keep the other
components' base, the charts, abstract and resource links unchanged.

## Consequences

The filter controls now download React and Base UI. Without JavaScript, the
static legal charts remain readable and inactive controls remain hidden. React
owns popup and selection UI; Astro owns the chart DOM. Selections are retained
on the explorer's data attributes before a change event is emitted, so an early
selection is available when the chart script initializes. The deprecated
NativeSelect component is removed, and 44px targets and existing theme tokens
are retained.

This supersedes the native-select and zero-hydration choices in
[the prior shadcn decision](shadcn-controls-render-on-the-server.md), following
Lucas's explicit component preference. It does not switch the project's global
preset or change the research data.
