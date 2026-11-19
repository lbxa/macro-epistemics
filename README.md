<p align="center">
  <img src="docs/assets/banner.webp" alt="Classical landscape with a giant overlooking mountains beneath a cloudy sky" width="100%">
</p>

<h1 align="center">Epistemics Sprint</h1>

<p align="center">
  <strong>A self-contained epistemics research project built on the Veracity game engine.</strong>
</p>

<p align="center">
  <a href="docs/benchmark.md">Benchmark protocol</a> &middot;
  <a href="CONSTITUTION.md">Constitution</a> &middot;
  <a href="#development">Getting started</a> &middot;
  <a href="harness/README.md">Harness</a> &middot;
  <a href="docs/api.md">API</a>
</p>

---

This repository is the independent Epistemics Sprint project. It includes the
Veracity engine, Python experiment harness, viewer, local agent tooling, and
reporting sources. The inherited benchmark measures whether agents independently
discover, establish, and execute
coordination that violates a constitution for private benefit. A content
verification game supplies the environment: a creator publishes a bonded claim,
a challenger may dispute it, and jurors commit and reveal their judgments.

The primary planned score is executed collusion rate across standardised
sessions. Proposals, agreements, execution, successful outcomes, capability
errors, and uncertain findings remain separate. Every admitted scenario needs
a feasible collusion opportunity, a compliant strategy, and an observable victim
or compromised outcome. Start with creator–juror and challenger–juror coalitions;
research papers, software, and political statements are content settings.

## Project scope and inherited evidence

**Previous work disclosure:** The Veracity core Rust game engine and agent
harness were previously built during the Apart Collusion Sprint. The original
work is available in the
[Apart Collusion Sprint repository](https://github.com/lbxa/apart-collusion-sprint).

The copied infrastructure and historical research are starting material for this
project. `Veracity` remains the engine/package name to preserve commands, API
contracts, and experiment reproducibility. New project environments and default
tracking uploads use `apart-epistemics-sprint`.

The Rust service, Solidity contracts, harness, client, experimental controls,
viewer, and imported reports predate this project's independent development.
Historical reports, decision records, frozen campaign configurations, and remote
artifact URLs retain their original identities. Renaming those sources would
break audit links or imply that old results were obtained here.

The active research separates reference agreement, confidence, answer revision
and jury acceptance. The [paper brief](docs/reporting/paper-brief.md) records
admitted evidence and remaining scientific gaps. The
[active report](report/epistemics/README.md) retains the original Apart layout
as a working revision; the [venue record](docs/reporting/venue.md) distinguishes
the proposed peer-review route from the November 13–15, 2026 sprint target.
Historical tracks and deadlines do not govern a new submission. New findings
require their own admitted evidence; the migration itself establishes none.

The full standardized scenario suite, human annotation workflow, and benchmark
session scorer remain incomplete. Imported payoff-only campaigns and fictional
teaching examples do not establish new benchmark performance.

See the [historical disclosure](docs/swarm-2026-disclosure.md) for inherited
provenance and the [local skill guide](.agents/skills/README.md) for agent tooling.

## Documentation

| Guide | Contents |
| --- | --- |
| [Benchmark protocol](docs/benchmark.md) | Scenarios, experimental axes, evidence thresholds, and scoring |
| [Constitution](CONSTITUTION.md) | Canonical participant obligations and game rules |
| [Game specification](SPEC.md) | Contract mechanism and financial rules |
| [Harness](harness/README.md) | Agents, configuration, isolation, evidence, and budgets |
| [Experiment viewer](visualizer/README.md) | Animated local replays of recorded public game states and harness evidence |
| [API](docs/api.md) | Endpoints, authentication, and lifecycle examples |
| [Integration](docs/integration.md) · [Architecture](docs/architecture.md) | System boundaries and rule authority |

## Repository

| Path | Responsibility |
| --- | --- |
| `contracts/` | Authoritative escrow, deadlines, commit/reveal, settlement, withdrawals |
| `core/` | Rust `/v1` API, chain operations, persistent recovery, public/private communication |
| `harness/` | Sole Python harness: Deep Agents, isolated shells, treatments, scheduling, evidence |
| `harness/src/game_api/` | Generated validated HTTP client and local Rust/Anvil launcher |
| `tasks/` | Independent uv project for the occupational task-source database and participant input candidates |
| `visualizer/` | Local React replay app and embeddable viewer for public state recordings |
| `docs/` | Benchmark protocol, engine integration, reporting guidance |
| `report/` | Imported research reports and frozen snapshots; historical evidence has limitations |

The contract owns financial authority. The harness never supplies missing
participant actions or invents payouts, transfers, or winning-side juror bonuses.
The full standardised scenario suite, human annotation workflow, and benchmark
session scorer remain to be implemented; [the protocol](docs/benchmark.md)
distinguishes current controls from planned extensions.

## Development

Prerequisites: Rust/rustup, Python 3.12+, uv, Bash, Git, curl, tar, jq, a native C
toolchain, and `sha256sum` or `shasum`. Docker with a running daemon is required
for isolated harness integration. Rust is pinned in `rust-toolchain.toml` and
Foundry in `.foundry-version`.

```sh
bash scripts/setup.sh
cargo build --workspace --locked
uv run --project harness --locked veracity-harness build-sandbox
uv run --project harness --locked veracity-harness validate --model "$EXPERIMENT_MODEL_ID"
```

Setup builds the contract, checks its deployment artifact, fetches locked Rust
dependencies, and installs `harness/uv.lock` into `harness/.venv`. Model selection
is explicit. Validation and tests do not call paid model APIs. Live `run` and
`smoke` commands require an API key, a campaign ledger, and an authorised budget;
see the [harness guide](harness/README.md).

To run just the API with isolated Anvil:

```sh
RUST_LOG=info cargo run --locked -p veracity-game-service -- --local
curl -sS http://127.0.0.1:8080/v1/health
```

Local mode listens on loopback and supplies development-only credentials:
`dev-operator`, `dev-creator`, `dev-challenger`, `dev-juror-1` through
`dev-juror-7`, and `dev-treasury`. Each invocation starts a fresh chain and a
private database under `.harness/runs/`. `Ctrl-C` stops the API and its node.
The service exposes Markdown at `/v1/docs` and OpenAPI at `/v1/openapi.json`.

For persistent deployments, start from
[configs/server.example.toml](configs/server.example.toml). Supply the verified
deployment identity, funded signers, and unique bearer credentials through
environment variables. Restart with the same chain, signers, configuration, and
database; use one active process per database. Private databases retain recovery
secrets and must never be published. Public Amoy runs are explicit operations.

## Verification

```sh
bash scripts/verify.sh
```

The gate runs hook regressions, pinned Solidity tests/artifact checks, Rust
formatting/Clippy/tests/builds, generated client checks, and the complete Python
suite including Docker → Rust → Anvil acceptance. Missing chain or Docker
infrastructure fails rather than silently skipping. No model API, public RPC,
or funded public wallet is needed.

For deterministic harness iteration without Docker:

```sh
uv run --project harness --locked pytest harness/tests
uv run --project harness --locked ruff check harness/src harness/tests
uv run --project harness --locked ruff format --check harness/src harness/tests
```

## Research records

The [reporting guide](docs/reporting/README.md) defines research report standards;
read it before writing or reviewing reports. The
[research revision workflow](docs/reporting/research-maturation.md) captures
how to strengthen exploratory studies through replication, evaluator audits
and iterative writing, including when revisiting earlier projects.

Compact numeric snapshots and report sources are versioned. Raw campaigns,
traces, checkpoints, ledgers, and
archives under `harness/results/` stay local and ignored, including the imported
2026-10-26 campaign. Raw evidence must be obtained separately for a full audit;
Git LFS is not required for this source repository. The imported payoff-only
campaign and fictional teaching examples do not establish constitution-conditioned
benchmark performance.

## Changelog

### 2026-11-17

- Adopt the [reusable research revision workflow](docs/reporting/research-maturation.md)
  for taking exploratory studies toward peer review: broaden the evidence needed
  by the claim, audit the evaluator and revise the paper as results arrive.
  Transfer the method to earlier projects with their own provenance and
  authorizations; see the [decision](docs/decisions/research-maturation-transfers-method-not-findings.md).

### 2026-11-14

- Run sprint experiments on cloud compute and use W&B for mobile inspection and
  retained evidence. Build the report alongside results with the `editor` skill;
  keep the initial Apart-formatted draft structural until claims are supported.
- Establish Epistemics Sprint as the independent project identity, sharing one
  repository-local skill source across Codex and Claude. Preserve Veracity's
  package/API names and historical evidence identities for reproducibility; see
  [the migration decision](docs/decisions/epistemics-sprint-owns-active-project-identity.md).

### 2026-10-28

- Keep raw experiment outputs and compiled report copies out of Git; retain
  source, locks, test fixtures, compact research snapshots, and required figures
  so cloning and verification do not require a gigabyte of historical run data.
- Promote the autonomous harness to `harness/` and retire the hackathon runners,
  simulated incentives, and duplicate setup/verification paths. Keep the actual
  HTTP client and chain launcher in the single Python package.
- Establish `CONSTITUTION.md` as canonical participant input and `docs/benchmark.md`
  as benchmark design authority. Separate executed collusion from accuracy and
  preserve pre-constitution campaigns as historical evidence.
