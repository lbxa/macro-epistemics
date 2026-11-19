# Shadcn controls render on the server

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** website, UI components

## Context

Lucas requested shadcn components for the website's UI controls. The results
page is a static Astro site with native selectors, SVG charts and no client
framework. Its archive header, light green/cream theme, primary data and absence
of accordions remain requirements.

## Decision

Use the official `@shadcn` registry for Button, NativeSelect, Field and Separator.
Render their React composition through Astro on the server, while the existing
chart script listens to native selectors. Keep the default legal figures useful
without JavaScript; do not hydrate React for these controls.

The current registry's NativeSelect is unavailable in the legacy Tailwind 3
registry. Use Tailwind 4's native Vite plugin, retain the existing configuration
through `@config`, and express project colors as semantic tokens in the existing
global stylesheet. Pin the React renderer to 5.0.7, compatible with Astro 6.2.1's
Vite 7 runtime. Keep system fonts rather than the preset's font download.

## Consequences

The server build gains React and the shadcn source dependencies; visitors do not
download React for this page. Native selectors retain browser keyboard/touch
behavior, with 44px targets and shadcn focus styles. Two small server components
own field and anchor child composition across the Astro/React boundary. Header
separators retain 4px/2px dimensions. The frozen aggregates, grading and chart
coordinates are unchanged. Future registry updates must preserve local control
height and separator variants.
