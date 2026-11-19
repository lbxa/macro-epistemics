# Parallel sandbox lifecycle and stepped mechanics tests

- **Date:** 2026-11-14
- **Status:** Accepted
- **Deciders:** Repository maintainers (requested integration-test speedup)
- **Area:** harness, testing

## Context

The development goal is at least 20% less time in
`harness/tests/test_integration.py`, without dropping protocol or isolation checks.
Five mechanics test cases inherited real-time clocks from research configs even
though their assertions concern vouchers, mandates, and offer delivery. Sequential
Docker startup also costs seconds per participant and scales with jury size.

## Decision

Use stepped clocks and the original phase windows in mechanics fixtures; keep the
dedicated real-time session test unchanged. Start participant sandboxes with at
most four workers and remove resources concurrently within each cleanup phase.
Finish all startup workers before propagating failure or cancellation, and finish
container removal attempts before removing networks, volumes, or bind-mount staging.

Build the integration module's unchanged sandbox image once per pytest worker.
Run the integration gate with two pytest workers and `--dist=loadgroup`; keep all
swarm ordering cases and the largest-jury payout case in the `swarm` group. Unit
tests retain their existing single-process default.

## Consequences

The tests retain every original case and assertion, real Docker sandboxes,
per-participant private networks, actual HTTP requests, and Anvil settlements.
Research configs and live clock semantics are unchanged. Live experiment setup
also benefits from parallel startup. Roster order remains deterministic; Docker
resource creation order does not. Four workers bound daemon load and stay below
the Docker client's default connection pool capacity.

Grouping prevents two 17-participant arenas from overlapping and exhausting
Docker's default address pools. A large arena may overlap a smaller one; every
case still owns fresh chains, containers, networks, and files. The fast integration
command and the verification gate explicitly select two workers and grouped
scheduling. Ungrouped parallel runs do not provide that resource bound.

`harness/tests/test_sandbox_lifecycle.py` checks overlap, worker draining on
failure/cancellation, and cleanup dependency ordering. The Docker isolation test
uses the concurrent startup path as well.

The watchdog unit fixture expires its real timeout only after the hung model
request starts. Its former 20 ms setup deadline sometimes fired before any
request reservation under CPU load, testing scheduler speed instead of the
intended retained-hold invariant. The request still must be cancelled and its
hold retained, with a separate five-second bound on the fixture itself.

## Alternatives considered

Sharing engines or participant containers across tests would risk leaking chain,
filesystem, or network state. Reducing test cases or replacing chain/sandbox calls
with mocks would weaken integration coverage. Neither is needed for these gains.

## Measurements

Measured on 2026-11-14 with Python 3.12.14, pytest 9.1.1, pytest-xdist 3.8.0,
Docker 29.9.2 (rootless, VFS), four CPU cores of quota, and the same prebuilt debug
Rust engine and pinned Anvil. All 28 original integration cases and assertions
passed in each measured implementation.

| Implementation | Duration | Reduction from baseline |
| --- | ---: | ---: |
| Original, sequential | 1,350.02 s (22m30s) | — |
| Stepped mechanics clocks and parallel arena lifecycle, sequential pytest | 1,121.45 s (18m41s) | 16.9% |
| Final integration command, including image reuse and two grouped workers | 858.25 s (14m18s) | 36.4% |

The baseline is the sum of successful pytest case durations (setup, call, and
teardown): 18 cases from the first run and the remaining 10 rerun after resolving
an environment routing problem. Failed environment attempts are excluded. Both
optimized durations are complete suite elapsed times, including pytest overhead;
parallel case durations are not summed. Case names were matched across all 28
cases. These are individual measured runs, not statistical performance guarantees.

The cloud daemon's `host-gateway` address could not reach the host relay, and its
default bridge subnets overlapped the host network for larger juries. A temporary
pytest plugin mapped the relay hostname to the reachable host address and assigned
non-overlapping private subnets (distinct ranges per worker). It also recorded
lifecycle timings. This environment adaptation changed no HTTP handlers, chain
behavior, participant isolation, or assertions, and is not part of the repository
change. The first 18 baseline cases used the default private subnets; the larger
baseline cases and subsequent runs used the explicit subnets.

Reproduce on a working local Docker/Anvil setup from the repository root:

```sh
uv sync --project harness --locked
uv run --project harness --locked pytest harness/tests/test_integration.py -m integration -n 2 --dist=loadgroup --durations=30 --junitxml=/tmp/integration-fast.xml
```

`bash scripts/verify-harness.sh` selects the same worker configuration for all
integration tests after the unit tests. Remove `-n 2 --dist=loadgroup` to measure
the single-process path. Compare elapsed suite time when workers overlap.

### Per-test duration percentiles

Calculated from the retained JUnit XML for the same 28 passing cases, including
setup and teardown. Percentiles use linear interpolation at index `(n - 1) * p`.
Failed environment attempts and the nameless interrupted-case record are excluded;
the `@swarm` scheduling suffix is removed when matching case names.

| Run | Per-test p50 | Per-test p99 | Suite duration |
| --- | ---: | ---: | ---: |
| Original, sequential | 39.10 s | 94.22 s | 22m30s |
| Clock/lifecycle optimizations, sequential pytest | 37.41 s | 80.10 s | 18m41s |
| Final image reuse and two grouped workers | 47.46 s | 115.86 s | 14m18s |

The sequential optimizations reduced p50 by 4.3% and p99 by 15.0%. Final parallel
execution increased per-test p50 by 21.4% and p99 by 23.0% relative to the original
baseline, while reducing suite elapsed time by 36.4%. The final result improves
suite throughput with higher individual-case latency under shared resource
contention. Summed parallel case duration increased by 23.0%; that includes waiting
and must not be interpreted as CPU consumption.

Each distribution contains one observation per case from a single measured run.
With only 28 observations, p99 is near the maximum and is sensitive to individual
slow cases. Repeated runs would be needed to estimate repeat-run tail latency.
