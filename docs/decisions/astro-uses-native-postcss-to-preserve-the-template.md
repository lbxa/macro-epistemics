# Astro uses native PostCSS to preserve the template

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** website

## Context

The supplied Astro 6 template uses Tailwind 3 utilities and configuration. Its
older `@astrojs/tailwind` integration declares peer support only through Astro 5,
and the missing direct Tailwind dependency initially resolved to an incompatible
Tailwind 4 package. Lucas asked to preserve the header and visual aesthetics.

## Decision

Keep Astro 6 and the template's Tailwind 3 design. Run Tailwind and Autoprefixer
through Astro/Vite's documented native PostCSS configuration instead of the
older integration. Pin the existing runtime requirements in the package metadata.

## Consequences

The page retains its existing utility classes and archive title bars without a
visual migration. `website/postcss.config.cjs` owns the CSS pipeline;
`website/bun.lock` records the resolved dependencies. Type checking, linting,
static builds and rendered desktop/mobile checks verify the resulting page.
Upgrading to Tailwind 4 remains a separate design and dependency change.
