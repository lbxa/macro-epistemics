# Contract micro keeps truncated juries and completed cells

- **Date:** 2026-11-15
- **Status:** Accepted
- **Deciders:** Lucas
- **Area:** harness, experiment recovery

## Context

After 27 settled native-model disputes, a DeepSeek juror reached the declared
4096-token output cap. LangChain's direct `response_format` path used SDK parse,
which raised `LengthFinishReasonError` before the harness received the truncated
completion or its usage. The active local chain then closed without a verdict.

## Decision

Retain that failed jury cell, its frozen defence and existing ballot, together
with all 27 settled cells. Import these observations into a new continuation
only after validating source cases, participant prompt hashes and baseline
identity. Copy original evidence and preserve its episode IDs and outcomes.
Do not resample an attempted cell. Continue only unattempted cells under the
same ledger and cap, and distinguish a completed batch containing failures.

For future calls, retain the same Cloudflare JSON-mode request through SDK
`extra_body` passthrough and normal create handling. A mocked HTTP response
verifies the JSON-mode wire field, length finish reason, retained token usage
and neuron-based charge. Classify length-limited responses as output-limit
failures and continue other jurors; never invent a vote or silently retry.

## Consequences

The original failed cell has a measured model defence but no settled jury
verdict. Its charge reservation remains unresolved. Author revision counts and
settled-jury denominators therefore differ. The continuation preserves source
versions and raw attempts; it cannot claim that every assigned jury settled.
