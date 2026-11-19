# Gateway teardown follows participants

- **Date:** 2026-11-19
- **Status:** Accepted
- **Deciders:** Lucas Barbosa (verification repair requested)
- **Area:** Harness Docker lifecycle

## Context

Two integration cases left Docker networks with no listed containers. The
daemon refused to remove either network and reported active endpoints. The
arena's participant and gateway containers share endpoints on the same
networks and previously entered the same parallel removal batch. Docker also
reported a stale gateway endpoint after separate container removal phases.

## Decision

Remove participant containers in parallel, then explicitly disconnect their
networks from the gateway before removing it. Register the gateway for cleanup
as soon as Docker creates it so startup failures follow the same ordering.

## Consequences

Cleanup still reports Docker removal failures. Network removal checks that
cleanup completed even when the explicit disconnect fails. A regression test
checks the teardown order and bind-mount lifetime.
