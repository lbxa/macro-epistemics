# Contract micro uses source-graded bounded text defences

- **Date:** 2026-11-15
- **Status:** Accepted
- **Deciders:** Lucas
- **Area:** harness, benchmark

## Context

Lucas authorised a ContractNLI pressure-versus-evidence trial across DeepSeek,
GPT-6.1 and Opus-5.5 with at most US$10 of new API spend and a summary of epistemic
findings. The earlier finance test used a scripted creator and did not observe
the original answerer defending its own output. Its US$100 ledger is historical
to that distinct campaign and cannot authorise extra spend for this one.

## Decision

Use three existing document/hypothesis cases, five screening replicates per
model, and paired neutral, pressure, invalid-argument and source-audit branches
from each selected natural answer. Include one correct and one incorrect answer
when available; preserve all screens and report absent error cases as not
observed. Use the original model as defender, a common three-member DeepSeek
text jury, fixed 1x synthetic stakes and independent source-reference grading.

## Consequences

The new bounded text adapter remains inside `harness/` and uses the existing
typed HTTP client, Rust API and Anvil contract. Text actors receive declared
source material and respond once; they do not explore shell tools. This is a
new experimental treatment, not a continuation of the finance agent policy or
an admitted collusion benchmark. The immutable original classification remains
the jury's target after a qualification or retraction.

Three-way source correctness, quotation diagnostics, changed commitments and
jury outcome are different measures. Selecting natural errors is an explicit
mechanism probe; it does not estimate model-wide error prevalence or calibration.
An absent natural-error case cannot be replaced by a fabricated model response.

Cloud execution is required; the earlier local exception applied only to the
finance test. Current model availability and prices were checked read-only.
The runner must have an explicit lifetime and budget, and its source and any
private recovery state must be retained separately from public artifacts.
