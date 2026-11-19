# Contract micro runs through Cloudflare only

- **Date:** 2026-11-15
- **Status:** Accepted
- **Deciders:** Lucas
- **Area:** harness, experiment providers

## Context

Lucas explicitly instructed that this three-model trial rely solely on
Cloudflare. The earlier preparation selected OpenRouter and stopped on rejected
credentials. That is superseded provider planning, not a requirement for Lucas
to replace an OpenRouter key. No paid model calls had been dispatched.

## Decision

Use Cloudflare's native DeepSeek V4 Pro 0813 and its unified AI Gateway catalog
for GPT-6.1 Sol and Claude Opus 5.5, with Cloudflare authentication and billing.
Keep the original US$10 API limit, source grading, frozen-answer branches and
common three-member jury. Do not substitute models or fall back to OpenRouter.

Use live Cloudflare pricing metadata. Where a third-party completion provides
usage without a monetary receipt, retain a conservative usage-based cost bound
as a distinct ledger state; do not label it a confirmed provider charge.
Include all published token/cache tiers and a 5% credit-purchase allowance.
Missing usage, timeouts and unknown charges keep their full reservation.

## Consequences

The native Workers AI catalog and the unified third-party catalog are different
discovery endpoints. A missing GPT/Opus entry in the native catalog does not
establish that Cloudflare cannot serve it. Gateway management permissions are
also distinct from model invocation permissions.

The previous source-graded bounded-text decision remains applicable to the
protocol. This decision supersedes its original provider selection. Cloud
orchestration remains required unless Lucas grants a new local exception;
Cloudflare model access alone does not provision the Rust/Anvil runner.
