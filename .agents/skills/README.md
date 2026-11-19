# Macro-Epistemics skills

This directory is the repository's skill source. `.claude/skills` is a relative
symlink here; edit skills here so Claude and Codex receive the same instructions.
Skills and their references travel with the repository. External CLIs, MCP
services, credentials, Docker, and compiler toolchains still need their normal
setup; a copied skill does not install them.

## Use the existing code

- `core/` owns the Rust `/v1` API and chain recovery. `contracts/` owns financial
  rules; neither the harness nor a new agent layer may implement alternate payouts.
- `harness/` is the sole Python harness. Read `harness/pyproject.toml` and
  `harness/uv.lock`; use `uv run --project harness --locked ...`. Do not scaffold
  a second harness from the LangChain, LangGraph, or Deep Agents quickstarts.
  Those skills are references for explicitly requested new examples or features.
- `visualizer/` owns the React viewer and `package-lock.json`. Its checks are
  `npm --prefix visualizer run check`, `npm --prefix visualizer test`, and
  `npm --prefix visualizer run build`; the root verification gate does not run them.
- `report/epistemics/` owns the active manuscript; `make -C report` builds it.
  Other report sources and snapshots are inherited research. Use `editor` for
  report writing and review. Read
  `docs/reporting/README.md` before report work. The active brief and venue record
  describe the current revision and proposed publication route.

## Route by the task

Use `code-craftsmanship` for repository changes, `anti-slop-code-architecture`
for non-trivial application boundaries, and `anti-slop-architecture-reviewer`
for architecture reviews. Use `tdd`, `quality-assurance`, and `verify` for Rust
behavior and checks. Use the relevant framework skills only when changing that
framework's actual implementation; fetch current docs with `context7-mcp` when
API or tool behavior matters.

`capture-tacit-knowledge` records package facts and directs trade-offs to
`docs/decisions/`. `entropy-reducer` checks the touched diff before handoff.
Optional integration skills (W&B, AgentLens, managed agents, GitHub) require
their documented tools and authorization; do not enable remote operations just
because their skill is present. Preserve existing experimental budgets and
private-observation boundaries.

Experiments run on cloud compute. Use `wandb-primary` to inspect
runs and retained evidence with the supplied key. Follow `AGENTS.md` for host,
project, credential loading, remote handoffs, and the distinction between live
monitoring and the harness's finished-run uploader.

See `AGENTS.md` for environment and tracking identifiers. Historical artifact
addresses, campaign names, source hashes, and append-only decisions retain
their original identity. `Veracity` remains the engine/package namespace.
