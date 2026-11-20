# Repository Guidelines

## Project Structure & Module Organization

Macro-Epistemics is an independent research project. Keep `apart-epistemics-sprint`
as the active environment and default tracking identifier. Retain Veracity's
existing package and API names. Imported reports, frozen campaigns, remote
evidence URLs, and append-only decisions keep their historical identifiers.
Read `.agents/skills/README.md` for local skill routing and package-specific checks.

This repository implements the `SPEC.md` game engine and `/v1` API plus the Python experiment harness in `harness/`. `core/src/` contains `api`, `game`, `chain`, `chat`, `forum`, `store`, and configuration modules. `contracts/` owns Solidity rules, Foundry tests, and the deployment artifact. The harness owns agents, treatments, observations, and metrics; it calls HTTP. Keep financial authority in the contract.

`docs/api.md` is the harness integration guide; `docs/architecture.md` records boundaries. `configs/` and `examples/` contain deployment and request templates. Shared skills live in `.agents/skills/`; `.claude/skills` points there. Agent definitions and hooks live in `.codex/` and `.claude/`.

`docs/private-chat.md` defines the experimental chat API. Prohibited chat is delivered and flagged; membership is enforced. Participant history settings never remove the operator's retained audit transcript. Keep chat bodies out of public game state and logs.

`docs/public-forum.md` defines the core-owned public forum. Assigned episode participants share history; operator transcript/audit access is distinct. The harness publishes and reads public deliberation through HTTP. Keep message bodies out of ordinary logs and metadata audits.

## Build, Test, and Development Commands

- `bash scripts/setup.sh`: install pinned local Foundry, build contracts, and fetch locked dependencies.
- `cargo run -p veracity-game-service -- --local`: start the API with isolated Anvil.
- `bash scripts/verify-fast.sh`: run shell fixtures and decision-index validation. Both Stop hooks use this entry point with a 30-second cap.
- `bash scripts/verify.sh --no-docker`: run the fast checks, Foundry, Rust with real Anvil, and Python regressions on demand.
- `bash scripts/verify.sh`: run the full gate in CI or explicitly, including serial Docker acceptance.
- `cargo build --workspace --locked`: build workspace packages.
- `cargo test --workspace --locked`: run unit, integration, and documentation tests.
- `cargo test -p veracity-game-service`: test the service during iteration.
- `bash scripts/verify-harness.sh`: run Python client/agent regressions and serial Docker-isolated engine acceptance after building Rust. Pass `--no-docker` for the Python checks alone.
- `cargo fmt --all`: format Rust sources.
- `cargo clippy --workspace --all-targets --all-features --locked -- -D warnings`: reject lint warnings.

Rust tooling is pinned in `rust-toolchain.toml`; Foundry in `.foundry-version`. Commit `Cargo.lock`, `harness/uv.lock`, and intentional artifact updates. Setup requires uv and creates `harness/.venv`.

## Coding Style & Naming Conventions

Use Rust 2024 and rustfmt's default four-space indentation. Use `snake_case` for modules, functions, and variables; `PascalCase` for types and traits; and `SCREAMING_SNAKE_CASE` for constants. Prefer explicit ownership, typed errors, and narrow module boundaries. Share dependency versions through `[workspace.dependencies]` when needed. Workspace members inherit the unsafe-code prohibition.

## Testing Guidelines

Follow the shared `tdd` skill: witness the intended failure, implement, and expand outward. Rust integration tests live in `core/tests/`, contract tests in `contracts/test/`, and Python pytest regressions in `harness/tests/`. Prove deadlines, conservation, commitments, role boundaries, and recovery with actual Anvil. Default tests require no public networks, funded public wallets, or model APIs. Never skip chain tests silently. No coverage percentage is configured.

## Benchmark authority

`CONSTITUTION.md` is the short canonical participant constitution and game-rule summary.
`docs/benchmark.md` defines scenarios, experimental axes, evidence thresholds, and
session scoring. Measure executed coordination separately from proposals,
agreements, success, and capability errors. Every admitted scenario needs a
feasible collusion opportunity, compliant strategy, and observable victim or
compromised outcome. Keep evaluator labels and coalition plans out of agent inputs.
The sole harness is `harness/`; its `src/game_api/` owns the retained HTTP client.
Historical payoff-only campaigns are not constitution-conditioned benchmark evidence.

## Cloud experiments and W&B access

Experiment runs execute on cloud compute so Lucas can inspect
and direct them from another device. Use the repository's `wandb-primary` skill
for runs, metrics, logs, and artifacts, and its Launch reference when the chosen
runner uses W&B Launch. W&B tracking alone does not provide compute. Do not run
weekend campaigns on a laptop or depend on an open local terminal.

The W&B API key has already been supplied. Load `WANDB_API_KEY` from the process
environment or the ignored root `.env` with `python-dotenv`, preserving existing
environment values. Never print the key, pass it as a command-line argument,
commit it, or put it in report sources or run artifacts. Inject it into cloud
workers through their secret mechanism. Do not ask for it again unless it is
unavailable or rejected. `bash scripts/setup.sh` installs the locked SDK in
`harness/.venv`; use that environment for W&B helpers.

Connection scope:

- Use `WANDB_BASE_URL` when explicitly configured. Otherwise the standard API
  host is `https://api.wandb.ai`. Historical Forge URLs are evidence addresses,
  not authority to send the supplied key to another host.
- Use project `apart-epistemics-sprint` for new work. Set `WANDB_ENTITY` to the
  verified user/team that owns it. If unset, discover the authenticated default
  entity with `wandb.Api().default_entity` and inspect project access before
  selecting a team. A read-only check on 2026-11-14 verified the supplied key
  against `https://api.wandb.ai`, default entity `lbxa-corp`, and accessible
  project `lbxa-corp/apart-epistemics-sprint`. Use that scope unless the user
  supplies another one. Historical Forge campaigns remain separate.
- For a read-only connection check, create `wandb.Api(timeout=30)` after loading
  the environment, then query the target project or known run. Do not create a
  dummy run with `wandb.init()` to test authentication. On failure, distinguish
  missing credentials, wrong host/entity, project permissions, and unavailable
  network. Never dump the environment or raw credential-bearing errors.

Run inspection helpers from the repository root, after loading the W&B variables:

```sh
harness/.venv/bin/python .agents/skills/wandb-primary/scripts/wandb_run_ops.py \
  project-snapshot --entity "$WANDB_ENTITY" --project apart-epistemics-sprint --sample 12
```

At the start of experiment work, recover cloud state before dispatching anything.
Record the project URL, remote runner/queue identity, run IDs and URLs, source
revision, configuration, seeds, model versions, budget/spend, and next action in
the campaign handoff. Keep a durable cloud copy so a fresh checkout can resume
inspection. Log live status, progress, safe diagnostics, and partial/final
evidence remotely during execution. The existing `veracity-harness-wandb` CLI
uploads finished runs and skips running ones; it alone is not live monitoring.

Use versioned artifacts and file hashes when admitting results into `/report`.
Keep assigned, completed, failed, and missing runs distinguishable. A missing
upload does not prove an unplayed run. Artifacts exclude recovery SQLite and
spending ledgers, and raw model calls are opt-in; protect those separately when
remote recovery needs them. Participant inputs must never receive the W&B key
or operator-only evidence. Keep existing budget and launch authorization limits;
the supplied key does not authorize arbitrary spend, deletion, or public sharing.

## Research data storage and sharing

- **Local workspace or restricted runner.** Keep working and raw data in
  ignored locations such as `harness/results/` and `.harness/`. Exclude raw
  model calls and traces, private transcripts and operator audits, recovery
  databases, checkpoints, spending ledgers, and caches from Hugging Face
  exports. Keep credentials and signing material in the environment's secret
  store or protected recovery storage.
- **Repository.** Keep the curated snapshots in `report/data/` that report
  builds or analyses read. Uploading a copy does not change those dependencies.
- **Private Hugging Face archive.** When a data upload is requested, use the
  [`lbxa/macro-epistemics` bucket](https://huggingface.co/buckets/lbxa/macro-epistemics).
  Put reviewed experiment summaries, run manifests, and result tables under
  `harness/results/`, and reviewed report datasets and supporting evidence
  under `report/data/`. W&B continues to track live runs and versioned evidence.
- **Upload and verify.** Confirm the destination is private. Use the `hf` CLI
  to preview an explicitly selected file set. Check the selected files,
  including archive contents, for secrets and private data before uploading.
  Verify the remote paths and sizes and record the bucket location, source
  run or snapshot version, and file hashes in the handoff.
- **Public release.** Get explicit approval for the specific files and
  destination before publishing data or changing bucket visibility. A link
  to a private bucket still requires Hugging Face access.

## Decision Records

Writing a decision record is part of "done", for every agent and without being
asked. When a change encodes a choice with real trade-offs — a constraint the
code does not show, a rejected alternative, behavior that looks like a bug but
is intended, a parked experiment — add `docs/decisions/<short-statement>.md`
from `docs/decisions/_template.md` in the same change. Use today's date, no
number in the filename, and people (not agents) as deciders. Never invent the
rationale: mark unverified parts `> ⚠️ NEEDS CONFIRMATION (who)`. Records are
append-only; supersede rather than rewrite. Do not edit `docs/decisions/INDEX.md`;
the Stop hook regenerates it and `scripts/verify.sh` rejects a stale one. Small
package facts stay in the package README changelog; see `docs/decisions/README.md`.

## Commit & Pull Request Guidelines

Use focused, imperative subjects such as `Add Cargo verification hooks`. Pull requests should describe behavior, link spec sections or issues, and report verification results and blockers.

## Agent-Specific Instructions

Use Context7 for current dependency and tool documentation: resolve the library ID, then query the full question. Author source and documentation directly with editing tools. Never commit wallet keys, credentials, or private observations. Both Stop hooks share `scripts/agent-hooks/stop-checks.sh`; disclose failures even when a repeated failure permits handoff.

## Research Reports

A LaTeX research report is a main project deliverable. Before planning, drafting,
or reviewing a report, use the [reporting guide and table of contents](docs/reporting/README.md).
Apply the repository's [editor skill](.agents/skills/editor/SKILL.md) to all
report prose, mathematical exposition, captions, and substantive review, even
when no separate editing pass is requested.
Read in this order:

1. [Paper brief](docs/reporting/paper-brief.md): reader, research question, actual evidence, and unresolved claims.
2. [Venue](docs/reporting/venue.md): selected official template and submission rules. Venue requirements take precedence over house formatting.
3. [Writing](docs/reporting/writing.md): argument, mathematical exposition, and reader comprehension.
4. [Visuals](docs/reporting/visuals.md) and [LaTeX](docs/reporting/latex.md): figures, tables, diagrams, notation, and build conventions.
5. [Review](docs/reporting/review.md): evidence, compilation, and rendered-page acceptance checks.

Develop `/report` alongside the experiments. Draft claims only when the
experiments support them. As results arrive, update the brief's evidence map
and then the affected methods, results, discussion, captions, and limitations
in small coherent revisions. Preserve concurrent edits and inspect the latest
diff before changing shared report files. Do not overwrite another writer's work.

Update the brief as evidence changes. Do not turn historical, mock, scripted, or
heuristic outputs into claims about model behavior on the integrated protocol.
Report completion requires the brief's claim-to-evidence mapping, a reproducible
PDF build, final-size visual inspection, and a recorded review with open gaps.
Source notes and reusable examples are indexed in the reporting guide; consult
them for technical lookup rather than expanding this entry point.
The active manuscript is `report/epistemics/main.tex`. `make -C report`
builds `report/epistemics/build/main.pdf`. Keep the existing section
structure and [working layout](report/template/epistemics.md), including
the limitations and ethics appendix. Use LaTeX's native Computer Modern text
and mathematics.

The inherited baseline manuscript lives in `report/main.tex`, with prose in
`report/sections/` and shared formatting in `report/preamble.tex`. Build it with
`make -C report baseline`. Its admitted smoke evidence remains historical; the reusable
teaching example in `docs/reporting/templates/` uses fictional counts. Neither
constitutes new project evidence.
