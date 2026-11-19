# Website builds restore the pinned film outside Git

- **Date:** 2026-11-17
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** website, deployment

## Context

Lucas authorised merging the finished website into main for publication.
GitHub's existing Cloudflare check identifies the production Worker as
`epistemics`. The live film URL returns 404 because the MP4 stays in the ignored
`video/` folder and is absent from a clean Git build.

## Decision

Keep the film outside source history and publish its approved bytes as the
`website-assets-v1` GitHub release asset. Asset preparation restores that public
file when absent, verifies its pinned SHA-256, and includes it in Astro's static
output. Align Wrangler's Worker name with the existing `epistemics` target.

## Architecture contract

- **Boundary and owner:** `website/scripts/prepare-assets.mjs` is the build-time
  artifact adapter. It owns preparing static website assets; research admission
  remains defined by the existing public export.
- **Capability and use case:** a clean Cloudflare build produces the same paper,
  captions, poster and film as the local approved website.
- **Change axes and concepts:** an admitted paper and a pinned film have explicit
  hashes. A future film revision needs a new release asset and hash together.
- **Invariants:** verify paper and movie bytes before using them. Never replace
  an unrelated local movie link or publish mismatching bytes.
- **Ports and adapters:** the existing build script uses public HTTPS, native
  filesystem operations and SHA-256; no model API or credential is involved.
- **Failure model:** HTTP errors, timeout, hash mismatch and link conflicts fail
  the build visibly. No background retry or additional lifecycle state is added.
- **Consistency and idempotency:** reuse verified local bytes. For a missing
  movie, download and verify before atomically renaming into the ignored cache;
  the hash and destination identify the cached artifact. Rerunning is safe.
- **Scope:** the build is a single artifact-preparation slice. There is no
  database, repository abstraction, transaction coordinator or SDK domain model.
- **Test strategy:** build an exported Git tree without local video, check its
  downloaded and emitted film hashes, and exercise a deliberately mismatching
  cached film to confirm rejection. Run website checks and repository gates.

## Consequences

Cloudflare can publish from main without committing the large video. Initial
clean builds need access to the public GitHub release; cached local builds do
not. Committed poster and captions remain sufficient when local render exports
are absent. The existing pinned report cannot be replaced by concurrent report
work. GitHub Actions' decision index must be regenerated from exactly the
records included in the release commit.
