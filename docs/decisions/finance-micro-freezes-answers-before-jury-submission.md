# Finance micro-experiment freezes answers before jury submission

- **Date:** 2026-11-14
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** harness, tasks, experiments

## Context

Lucas requested a DeepSeek V4 infrastructure micro-experiment with three jurors,
the $736 million to $708 million task, and three combinations of Veracity
awareness and submission. He selected Cloudflare and a shared US$5 model-spend
cap. The task bank's FinQA reference expresses signed change (-3.8%); the
question's positive decline magnitude is approximately 3.80%.

## Decision

Operationalise awareness as disclosure before answering and freeze numeric
answers plus stated confidence before any submission. Keep independent arithmetic
correctness distinct from the institutional jury outcome. Withheld or incomplete
verification has no binary jury label. Reuse the existing harness's scripted
publisher/challenger and model jurors for a controlled procedural review.

> ⚠️ NEEDS CONFIRMATION (Lucas Barbosa): the prepared design reuses one frozen
> disclosed answer in the submitted and withheld A branches. This isolates
> post-answer submission; it does not vary an announced promise of verification.

## Consequences

The prepared driver elicits two initial answers to one underlying task. It can
test evidence retention, confidence scoring and adjudication, not population
calibration. Positive decline is explicit in participant instructions; a signed
negative response is not silently relabelled. Native Cloudflare currently offers
V4 Pro 0813, while the initially offered V4 Pro 0423 is on OpenRouter. Resolve
that provider/version choice before a paid call; do not substitute silently.

Lucas subsequently confirmed Cloudflare V4 Pro 0813 and authorised local
orchestration for this one micro-experiment only, with the same US$5 cap.
Later campaigns retain their cloud requirement. The driver records the explicit
exception; it is not a fallback when a cloud runner fails.

Pass the configured W&B API host explicitly to SDK settings, defaulting to
`https://api.wandb.ai`. Local SDK settings otherwise inherited the historical
Forge API host during the first attempt. Retain that interrupted attempt and
its conservative request holds rather than relaunching under a fresh budget.

The existing Docker isolation requires a compatible orchestration host. Workers
AI inference credentials alone do not deploy Rust, Anvil and Docker. Cloudflare
Containers' documented lack of iptables in nested Docker prevents assuming that
the existing participant network isolation works there unchanged. Cloud runner
selection is still required for later campaigns.

See `harness/research/finance-micro/README.md` for the protocol and cloud handoff,
and `harness/src/veracity_harness/finance_micro.py` for the bounded driver. All
paid requests share the existing spending ledger; no source/reference material
or provider keys are mounted into participants.
