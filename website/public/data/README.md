# Macro-Epistemics: displayed research data

`research.json` (schema version 2) is the sanitized public aggregate used by the
landing page. It keeps the completed primary study, a one-source arithmetic
diagnostic and an offline validity audit distinct.

The landing page plots the primary study directly. The separate diagnostic,
seed-block detail and provenance remain available in this download and the
paper rather than in expandable page sections.

- **Completed primary study:** 600 initial attempts, 581 interpretable initial
  answers, 120 source groups, five model families and four domains. There are
  12,000 assigned branches: 11,620 execute, 11,483 have valid defences and 11,469
  settle. The 380 structurally unavailable assignments follow 19 unavailable
  initial answers; 151 executed panels abort. Each model receives 30 sources per
  domain and five defence seeds per condition. Repeats are not new sources.
- **Grading and uncertainty:** literal reference grades remain alongside a
  post hoc source-audit sensitivity pending independent adjudication. A source
  grade is not infallible truth. Endpoint denominators differ: loss uses valid
  defences of initial matches; repair uses valid defences of initial mismatches;
  mismatch-upheld uses settled panels of initial mismatches; final agreement
  uses all valid defences. The report owns the 2,000 within-stratum source-group
  bootstrap intervals. Seeds stay within source. Five seed-level final-agreement
  rates and their descriptive sample SD are included separately. A collapsed
  boundary interval does not establish certainty about new cases.
- **Arithmetic diagnostic:** one source, five seed blocks, three standalone
  calls per block and judge family. Counts, block outcomes and descriptive block
  SDs are retained; no source-level confidence interval is claimed. These calls
  are not additional primary settlements. Four of five checked-author replies
  are usable; all four correct and withdraw the original.
- **Benchmark validity:** an offline inverse recovers 287 stored numerical
  references from the misleading objections, including 38 initial mismatches.
  This is a scripted encoding audit, not observed model exploitation. A tested
  future policy adds zero correct matches among 37 supported initial errors;
  one nonscalar error is unsupported. That policy was not deployed in this
  campaign and does not close every possible leakage channel.

The provenance object records immutable W&B artifact identities, verified
digests, run URLs, analysis revisions and SHA256 hashes of the report inputs.
The primary artifact is v128; the arithmetic and validity artifacts are separate
v0 selections. The paper's v1 artifact PDF is independently hash-matched to the
downloadable draft. W&B may require project access; the aggregate download does not.

From `website/` in the monorepo, `bun scripts/sync-research.mjs` regenerates and
validates this file against the admitted report snapshots. Run
`bun test scripts/sync-research.test.mjs` for cohort, endpoint, uncertainty and
public-export checks. This file contains no raw model calls, spending ledgers,
credentials, private run state or full source documents.
