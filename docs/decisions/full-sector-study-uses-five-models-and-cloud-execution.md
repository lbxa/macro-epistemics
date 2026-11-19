# Full sector study uses five models and cloud execution

- **Date:** 2026-11-15
- **Status:** Accepted
- **Deciders:** Lucas
- **Area:** harness, experiment design, report

## Context

Lucas authorized adding GPT-OSS-120B and Inkling, executing the full
sector-stratified design, increasing API spending as needed, resolving issues
autonomously and iteratively updating the report over approximately five to
six hours. The earlier local exception and $10 micro-trial do not define the
new campaign. A configured cloud SSH host is reachable; Cloudflare remains
the sole inference provider.

## Decision

Freeze 120 benchmark-derived cases across finance, legal reasoning, science and
education, with distinct source-group IDs within domains. All five models
answer every case once, followed by four challenge conditions and five defence
seeds for every valid answer. Elicit source confidence before Veracity and jury
acceptance forecasts afterward. Keep reference grades independent of jury
outcomes and report benchmark adapters and modified controls explicitly.

Run the existing Rust/Anvil/harness stack on the isolated cloud host. Use one
new campaign ledger with an initial $1,500 guard under Lucas's broader spending
authorization; preserve the old micro-trial ledger. This guard is a ceiling,
not a spending target. Stop on pricing contradictions. Set a collection
deadline to reserve time for report analysis and rendered-page review.

## Consequences

The model roster is DeepSeek V4 Pro 0813, GLM-5.3, Kimi K2.6, GPT-OSS-120B and
Inkling 2 Small: five models across five developer families. Three blinded
GPT-OSS juror invocations form the main panel. GPT-OSS's higher native request
limit makes the full matrix feasible in the time window; this differs from
the pilot's DeepSeek panel. Replay one predeclared branch per case through a
DeepSeek panel for judge-family sensitivity, retaining separate estimates.
Never pool the pilot and full study as identical-protocol observations.

The common jury is homogeneous, and its ballots are not independent truth
measurements. Confidence forecasts are hidden from jurors. Source-grade
uncertainty, reference errors, missingness and generation failures remain
visible. The study measures occupational-domain strata, not representative
industry/GDP effects. Numerical MathDial feedback and financial answers use
explicit adapted endpoints; they are not full teaching-quality or official
benchmark-leaderboard scores. Finance has two benchmarks; other domain effects
remain partly confounded with benchmark format.

The [architecture contract](../../harness/research/sector-expansion/ARCHITECTURE.md)
owns recovery and evidence invariants. Failed/interrupted observations are
terminal and cannot be silently replaced. Results are admitted to the report
only after source, denominator and evidence checks; source-group clustered
uncertainty keeps all seeds and models within each resampled group.
