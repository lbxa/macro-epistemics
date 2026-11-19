# Finance settlement and jury participation are separate

- **Date:** 2026-11-14
- **Status:** Accepted
- **Deciders:** Lucas
- **Area:** harness, finance micro-experiment

## Context

The five-seed plan assigns three jurors per round. During execution, seed
20261115 at 1000x settled the disclosed claim with two supporting reveals; the
third assigned juror never joined or voted. The contract legitimately settled
at quorum, while the strict live collector rejected admission because it
required three reveals. The child study completed, and its paired undisclosed
round had three supporting reveals. These are different observations, not an
API failure or a rejected claim.

## Decision

Preserve every assigned seed, including the collector rejection. Final analysis
reports contract settlement, assigned jurors, participation and actual deposits
separately. Apply the same rule to every outcome: a valid quorum settlement is
an observed verdict, while missing participation remains explicitly flagged.
Do not replace incomplete participation with a new draw or impute a missing
vote. This distinction was documented after the first participation gap was
observed; it is not a preregistered change to the live admission rule.

## Consequences

The frozen runtime and its source archive retain the original strict collector.
The live campaign can therefore finish with an admission failure even when all
child studies settle. A separate analysis artifact must preserve that status
and state how many rounds achieved all three reveals. Tables may report valid
settlements only with the participation gap marked, and must not describe such
a round as 3–0 or as a full three-vote replication. Scheduled total stake differs
from actual deposits when an assigned juror does not fund a bond.

This preserves a potentially meaningful participant behavior under the stake
treatment instead of conditioning the comparison on successful participation.
The reason for the missing action is not established by the settlement record;
do not label it intentional abstention or infer a stake effect from this case.
