# Finance network recovery retries only unresolved cells

- **Date:** 2026-11-15
- **Status:** Accepted
- **Deciders:** Lucas
- **Area:** harness, finance micro-experiment

## Context

The five-seed micro-experiment lost connectivity during seed 20261116. Logs
recorded Cloudflare connection failures and W&B DNS failures. At recovery,
read-only DNS, authenticated W&B and authenticated Cloudflare catalog checks
succeeded. The dispatcher was suspended briefly to stop further launches while
checking connectivity, then resumed without changing its frozen runtime.

Three studies were affected. The disclosed rounds at 10x and 100x had already
settled; their undisclosed rounds had no verdict. Neither 1000x condition had
a verdict. The 100x disclosed round retained a valid 2–1 settlement alongside
an execution-error flag. A separate 1000x participation gap in seed 20261115
remains a measured behavior and is not eligible for replacement.

## Decision

Complete the original queued assignments, then use new labelled attempts for
only the four unresolved cells, with the same seed, model, prompts, frozen
answers, stakes and shared US$100 ledger. Preserve every original attempt,
execution error and uncertain request hold. Never replay an existing chain or
replace a valid settlement because of its vote split or participation coverage.

## Consequences

Recovery adds an explicit single-condition option to the existing study driver;
it does not create another agent harness. Archive that source separately from
the original campaign runtime. Final analysis retains all attempts, selects at
most one valid settlement per assigned seed/condition/stake cell, and records
the recovery relationship and both source versions. Failed calls remain in the
campaign cost even when a later attempt supplies a verdict.

This operational recovery rule was documented after the outage. It is not
presented as preregistered. It distinguishes an external connectivity failure
from observed jury behavior, rather than conditioning results on unanimity or
full participation. If another failure occurs, inspect it before making a new
recovery assignment; there is no automatic model retry policy.

## Operational scheduling clarification

Once all twenty original assignments have launched and captured the original
source hashes, recovery may use a worker slot freed by a completed assignment.
The last original study can therefore overlap the first recovery study, while
total concurrency remains at most two. All original source hashes were checked
before adding the recovery-only condition selector. This changes neither the
eligible cells nor the rule preserving existing settlements.

Automatic approval review rejected a combined 1000x recovery launch because it
could duplicate conditions. Read-only checks confirmed both original 1000x
conditions remained pending, with no jury configuration, run directory or
verdict, and that the rejected command created no recovery directory. Recovery
was split into four explicit single-condition attempts. The condition-specific
launch passed approval review. The rejected combined intent remains in the
recovery plan with no model calls; it is not an executed trial.
