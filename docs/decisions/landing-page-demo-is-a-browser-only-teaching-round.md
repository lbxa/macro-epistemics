# Landing page demo is a browser-only teaching round

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** website

## Context

Lucas requested a playable Veracity demo immediately beneath the landing-page
abstract, with no dedicated backend, and links to the underlying Veracity work.
The research page must keep illustrative interactions distinct from measured
model behavior and the actual protocol.

## Decision

Use a deterministic, scripted round in the browser. Visitors choose and freeze
an answer, submit an objection, select a response, and control three juror votes.
A separate arithmetic check evaluates the original answer. The original remains
fixed even after a revision or retraction. Link to the Veracity project and its
original 2025 framework paper from the demo and research resources.

## Consequences

The demo has no model calls, real funds, persistence, experiment collection or
game-service connection. Equal demo bonds explain the roles without simulating
contract settlement, payouts or commit-reveal cryptography. Its local UI states
are draft, challenge, jury and result; reset starts a new round atomically.
Invalid or inactive actions do not advance the round. Native controls, a static
fallback and browser checks cover accessibility and the core distinction between
jury agreement and source correctness. The actual game and financial authority
remain in the existing service and contract.
