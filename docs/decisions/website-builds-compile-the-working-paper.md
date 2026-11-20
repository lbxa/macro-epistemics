# Website builds compile the working paper

- **Date:** 2026-11-20
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** website, report

## Context

The [previous process](publish-current-research-assets.md) copied a compiled
paper into the repository and required a separate checksum update. Lucas
requested automatic compilation and publication through the website pipeline.

## Decision

The Cloudflare Workers build runs the website's existing asset preparation
step before Astro. It compiles the manuscript from the build's checkout using
the report Makefile and stages only the resulting PDF at the existing public
URL. The Linux build uses a checksum-pinned TinyTeX archive and the frozen
TeX Live 2025 package repository when the local compiler is absent.

## Consequences

The working PDF is a generated static asset. A failed compilation stops the
site build. The earlier PDF stays byte-pinned in the research data directory
for the public evidence export.
