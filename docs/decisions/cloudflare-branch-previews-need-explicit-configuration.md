# Cloudflare branch previews need explicit configuration

- **Date:** 2026-11-17
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** website, deployment

## Context

Cloudflare successfully built the release and restored the pinned video, but
the branch deploy failed. Its configured command is `npx wrangler preview`, and
Wrangler 4.163 requires an explicit `previews` block before deployment.

## Decision

Add an empty `previews` object to `website/wrangler.jsonc`, following the
[provider's configuration](https://developers.cloudflare.com/workers/previews/configuration/).
Keep assets, compatibility settings and production routes at the top level.

## Consequences

The existing Cloudflare branch workflow can create its preview while main uses
the existing production deployment. No new resource binding or secret is added.
