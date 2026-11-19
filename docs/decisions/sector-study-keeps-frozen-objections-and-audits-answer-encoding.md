# Sector study keeps frozen objections and audits answer encoding

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** harness, benchmark, report

## Context

The frozen numerical false alternative is `r + max(abs(r)/4, 7)`, where `r`
is the stored reference. That transform is invertible except for an explicit
collision escape. An algorithm-aware participant could recover reference
answers from objections rather than source evidence. Participants in this
campaign receive neither the generator nor its condition tags; finding the
channel does not establish that models exploited it.

## Decision

Preserve the ongoing campaign and expose the flaw. Run an offline scripted
audit against all usable numerical originals, and supply a future candidate
policy based on the public original answer, with reference grading only as a
veto. The future policy remains separate and unintegrated: no current prompt,
observation or assignment is changed. This implements Lucas's authorization
to investigate and resolve validity issues autonomously, without implying
prior author approval of the interpretation.

## Consequences

The [audit and future policy](../../harness/src/veracity_harness/sector_objections.py)
recover all 287 stored numerical references in the current cohort, including
38 initial reference mismatches. The same inverse yields no newly correct
answers among 37 supported mismatch inputs under the future policy; one
nonscalar original is unsupported. These are scripted results, not model
performance or a guarantee that every exploit is closed. The future policy
still needs proposal-plausibility review and explicit versioned integration
before a new campaign. Retain both literal and source-audited grades: matching
a defective reference is not matching reality.
