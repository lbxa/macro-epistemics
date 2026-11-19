# Contract micro uses native frontier models and frozen recovery

- **Date:** 2026-11-15
- **Status:** Accepted
- **Deciders:** Lucas
- **Area:** harness, experiment execution

## Context

The first Opus request returned HTTP 402, while a native DeepSeek request
successfully returned a source-correct answer. Lucas instructed us to use only
frontier models available through the supplied Cloudflare access and stated
that we cannot administer or fund the Cloudflare account.

An independent local reproduction also showed that LangChain caches its HTTP
clients across model instances. Closing a client's root SDK connection after
each generation caused the next instance to reuse a closed transport.

## Decision

Use native DeepSeek V4 Pro 0813, GLM-5.3 and Kimi K2.6. This replaces the original
GPT/Opus comparison; it is not evidence about those excluded models. The live
native catalog and input schemas expose token prices and sampling seeds for
all three. Request low reasoning for DeepSeek/GLM and high for Kimi, whose
lowest enabled reasoning setting is high; retain that difference explicitly.

Keep model clients alive for the entire run and vary sampling seeds at request
time. Close transports only after generation has ended. For recovery, reuse
completed screening records only when provider, initial prompt hash and source
cases match. Never overwrite or resample a retained answer. Model subsets and
continuations use the original US$10 ledger, including all earlier holds, and
retain distinct run outputs, source versions and remote run identities.

## Consequences

The original Opus rejection and failed DeepSeek transport attempt remain
separate infrastructure observations. Their conservative reservations remain
in the shared ledger; subsequent runs cannot reset the cap. Exact frozen text,
not a reconstructed equivalent answer, is used in challenge branches. This
supersedes earlier roster planning while preserving the benchmark protocol.
