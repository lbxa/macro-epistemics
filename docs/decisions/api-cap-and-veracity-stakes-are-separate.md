# API cap and Veracity stakes are separate experimental quantities

- **Date:** 2026-11-14
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** harness, experiments

## Context

Lucas clarified that API costs and the Veracity stake are distinct, authorised
a US$100 API cap, and requested varied Veracity stakes for later plotting.
The earlier US$5 campaign ledger retains three cancelled-request holds.

## Decision

Raise the existing API ledger's cap through an explicitly authorised, audited
transaction; retain every request, charge, hold and pricing halt. Ordinary
construction must still reject a different cap. Stale ledger handles cannot
reserve against an obsolete limit. Do not create a replacement campaign ledger.

Use 1x and 10x party/juror bonds as a small first stake comparison. These are
synthetic Anvil wei, with no USD conversion. Keep jury size, reward shares,
disclosure design, model and scheduling seed fixed. Reuse validated frozen
initial answers across stake levels; create new jury rounds rather than resuming
the interrupted chain. Show each round's actual fee schedule before eliciting
its jury forecast. Initial arithmetic confidence precedes stake disclosure.

## Consequences

`CampaignSpending` owns cap amendments, audit records and transaction guards;
the existing contract retains settlement authority. `finance_micro` owns the
stake factor, immutable baseline reuse and flat measurement export. Changes in
initial confidence cannot be attributed to post-answer stake variation.

The amendment uses one SQLite transaction with an expected-old-cap check and an
authorisation reason. It never clears uncertain charges or a pricing halt.
The study rejects mismatched baseline models, providers or participant prompts;
baselines and prior failed attempts remain retained with hashes. SDK failures
still stop an attempt rather than regenerate responses. Tests cover the ledger
transaction, stale writers, baseline matching, stake scaling and exported units.

See `harness/research/finance-micro/README.md` for the bounded study and handoff.
