# Contract micro allows one local orchestration trial

- **Date:** 2026-11-15
- **Status:** Accepted
- **Deciders:** Lucas
- **Area:** harness, experiment execution

## Context

Cloudflare model catalogs are accessible but the supplied account cannot be
provisioned with a Containers runner using the available credentials. Lucas
explicitly authorised local orchestration for this trial, with models remaining
on Cloudflare.

## Decision

Allow this ContractNLI three-model micro-experiment to orchestrate Rust/Anvil
locally when the explicit CLI exception flag is supplied. Record that exception
and the runner identity in the retained run configuration. Keep all model calls
on Cloudflare and one new shared API ledger capped at US$10.

## Consequences

The normal cloud execution requirement remains the default. This exception
does not authorise weekend campaigns, other experiments, OpenRouter calls or
extra spending. Keep live remote progress and frozen evidence in W&B so the
local test remains inspectable from another device.
