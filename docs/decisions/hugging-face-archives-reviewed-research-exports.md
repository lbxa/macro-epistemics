# Hugging Face archives reviewed research exports

- **Date:** 2026-11-19
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** harness, report

## Context

The project uses Hugging Face to share experiment and report data. Local run
directories also hold private observations and operational records. Report
builds and analyses read curated snapshots from the repository.

## Decision

Use the private `lbxa/macro-epistemics` bucket for reviewed copies of experiment
and report data. Keep raw and operational records in protected storage and
require explicit approval for public release.

## Consequences

Keep build inputs in the repository and use W&B for live tracking and versioned
evidence. Follow the [storage and sharing rules](../../AGENTS.md#research-data-storage-and-sharing)
to select and verify the files copied to Hugging Face.
