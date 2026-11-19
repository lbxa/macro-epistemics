# Engine receipt-test isolation

The first cloud admission-test invocation failed three fixtures because the
test counted every new database in the shared `.harness/runs` directory while
the numerical collector was also creating databases. Those scripted tests
made no model calls, but reused protocol-derived episode identities.

The corrected test gives Rust a private temporary working directory, reusing
the built binary and contract artifact through symlinks. Five tests pass
locally and five pass on the cloud host while collection remains active.
The corrected test source SHA256 is
`c95d048ed25a60408d5498d5964f3e660e60ad1119d8d87a29ddcc4a0f5acd8d`.
The production collector and frozen admission helper were not changed.

A proposed reversible relocation of the three old test stores was abandoned
because the container denied inspection of `/proc/526/fd/0`. No original
database was moved or deleted, and no claim that all process descriptors
were inspected is made.

Instead, `quarantine_test_stores.py` creates a read-only symlink view after
numerical collection finishes. It excludes only the three stores matching
retained pytest evidence, deployment/configuration identity, the exact
scripted objection and its stored artifact hash, and the scripted explanation
markers. The ownership manifest retains their original locations and file
hashes. Unknown duplicates remain errors. Completed numerical branches must
all appear in the view; the independent admission helper still checks every
receipt, vote, frozen input and terminal view.

Use `.harness/peer-review-objection-engine-view` as the admission helper's
`--engine-runs` input. Its `manifest.json` records the final included paths,
excluded fixture proofs, source hashes and the reason original stores remain
in place. This is an operational test-isolation record, not a new experimental
condition or a result about model behavior.

The final view contains 1,430 numerical-collection stores and excludes exactly
three proven fixture stores. Its manifest SHA256 is
`8fcbdc1b3aa049e22f63e4c1729fb79bfbc20e8778d7168e3c5b6da6dd319c52`.
The retained local copy is `.harness/peer-review-engine-view-manifest.json`.
