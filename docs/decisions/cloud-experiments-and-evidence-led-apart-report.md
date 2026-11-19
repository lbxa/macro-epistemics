# Cloud experiments and an evidence-led Apart report

- **Date:** 2026-11-14
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** experiments, agent tooling, report

## Context

Lucas will be mobile over the weekend and wants experiments to execute in the
cloud with W&B access through the supplied key. The report is an important
deliverable developed concurrently, but it is too early to write material
contributions. Lucas supplied Apart's template PDF and the recommended outline.

## Decision

Document credential loading, verified W&B scope, remote run recovery, and
evidence retention in `AGENTS.md`. Cloud compute owns experiment execution;
finished-run uploads alone do not supply live monitoring. Adapt `editor` from
its copied textbook workflow to research writing with complete reasoning and
traceable evidence.

Create a separate active report scaffold under `report/epistemics/`, using the
supplied Apart PDF's formatting and Lucas's section names. Make it the default
report build, with explicit historical build targets. Prepare title, metadata,
and placeholders now; let actual results determine substantive prose.

## Consequences

Read-only access was verified at the standard W&B host for
`lbxa-corp/apart-epistemics-sprint`; the check created no runs. Remote compute
provisioning and live instrumentation must be verified before a campaign is
launched; these documentation changes do not claim they are already configured.
Keys stay out of Git and participant observations. The current Apart template
and sprint guidelines supersede old venue rules. Authors, track, final title,
and empirical contributions remain open. A clean scaffold build does not make
the final populated report submission-ready.

## Alternatives considered

Reusing a historical manuscript as the active report would import old findings
and venue assumptions. Writing speculative methods or results now would commit
the report to claims before experimental evidence exists.
