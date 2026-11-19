# Task bank keeps an independent uv project

- **Date:** 2026-11-14
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** tasks, harness

## Context

Lucas supplied an occupational task-source bank and requested its integration
as a uv project in this monorepo. Its inspection and data-preparation scripts
use only Python's standard library. The existing `harness/` owns experiment
execution, model dependencies and HTTP integration with Veracity.

## Decision

Keep `tasks/` as an independent, non-package uv project with its own lockfile,
rather than coupling its environment to the harness through a root uv workspace.
Retain the imported database and source evidence unchanged. Copy authored
documentation into rebuilt bundles instead of generating static prose in code.

## Consequences

Task inspection needs no model dependencies or credentials. Use
`uv run --directory tasks --locked python task_db.py ...` from the repository
root; harness commands continue to select `--project harness`.

The 810 exported text inputs remain candidates, not admitted scenarios or new
experimental results. Adaptation and execution belong in `harness/` under the
existing admission rules. See `tasks/README.md`, `tasks/EXPERIMENT_PROTOCOL.md`
and `docs/benchmark.md`.

Original import checksums remain in
`tasks/source_metadata/imported_bundle_checksums.json`; the current bundle
manifest reflects the integrated scripts and documentation. Separate project
locks require explicitly selecting the intended project in commands.
