# Chart scroll motion preserves static data

- **Date:** 2026-11-17
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** website

## Context

Lucas requested animation as users scroll to the charts. The research page
prioritises fast loading and inspectable source-backed data, with native SVG
charts readable before JavaScript runs.

## Decision

Reveal each model row once using IntersectionObserver and the browser's Web
Animations API. Fade and lift rows subtly, expand confidence intervals around
their centres, and fade markers at their final positions. Keep numeric labels
and all data coordinates unchanged. This small interaction needs no animation
dependency or additional hydration.

## Consequences

`website/src/components/FindingsExplorer.astro` owns the enhancement alongside
its existing chart script. Default styles remain visible, so missing JavaScript
or unsupported animation APIs cannot hide results. Reduced motion skips new
animations and cancels active ones when enabled. Filter changes cancel reveals
so newly selected data displays immediately. Re-entering a chart does not replay
its reveal, and animation never implies a count increasing from zero.
