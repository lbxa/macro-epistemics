# Standalone sector tools pin the canonical W&B API

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** harness, tracking

## Context

The repository permits the standard `https://api.wandb.ai` API unless
`WANDB_BASE_URL` explicitly selects another host. The main sector runner
already supplies that setting. A report-upload SDK invocation instead chose
the Forge API default when the environment variable was unset. Its artifact
was recoverable through the canonical API; the report run was finished there.
An optional image preview also required Pillow, which is absent from the
locked cloud harness. The figure files were already retained in the artifact.

## Decision

Give standalone diagnostic and evidence-archive SDK clients the same explicit
host selection as the main runner. Honor an explicit environment override.
Use stored PNG/PDF artifact files for report delivery without adding an
optional preview dependency to the frozen experimental environment.

This implements Lucas's authority to resolve infrastructure issues
autonomously; it does not change account billing or access settings.

## Consequences

The change applies to future helper invocations. Completed model outputs,
protocol source hashes, costs and artifacts remain frozen. The final report
artifact was validated and its tracking run completed through the canonical
API. Future inspection commands should also explicitly set `WANDB_BASE_URL`
when using an SDK whose default differs from repository policy.

## Alternatives considered

Relying on SDK defaults can move the credential destination as the SDK changes.
Installing Pillow solely for a redundant preview would modify the locked cloud
environment without improving the retained research evidence.
