# Epistemics Sprint report

## Peer-review working revision

The active paper is now titled *Confidence, Correction, and Consensus:
Evaluating Language Models Under Dispute*. It retains the completed primary
study and adds targeted replications as separate evidence. The original
sprint layout and archived v2 remain historical; the current working version
is not an anonymized journal submission and may exceed the old page cap.
See the [revision brief](../../docs/reporting/paper-brief.md) and
[independent-review protocol](../../harness/research/sector-expansion/peer-review/ADJUDICATION.md).
Human adjudication and author approval remain incomplete.

The numerical replication retains 1,500 assignments and validates 1,430
executions. The eight-source judge comparison retains 720 calls, including
39 failed DeepSeek outputs. The large defence penalty does not recur in
GPT-OSS's complete three-new-source comparison; DeepSeek's third comparison
is unresolved. See the [admission register](../../harness/research/sector-expansion/peer-review/admission.json)
and [offline reproduction guide](../REPRODUCIBILITY.md).

The historical Apart **AI x Epistemics Research Sprint, November 13–15, 2026**
draft used the title *Macro-Epistemics: Confidence Under Dispute* and the
supplied sprint template; see [template provenance](../template/epistemics.md).
The peer-review revision above supersedes that scientific title and page cap.
Authors are Lucas Barbosa (NYU) and Stefan Gazzana (Roundarc), as supplied by
Lucas. The sprint framing centered on Track 1, with Track 2 informing the
jury-validity and provenance discussion. Neither version is a certified
submission.

The [review record](review.md) preserves the original scaffold checks and the
first empirical draft's evidence, numerical, compilation and visual checks.
Independent reference adjudication and author scientific review remain open.

The [video storyboard](storyboard.md), *Macro-Epistemics: Make AI Answerable*, scripts a
118-second informative and inspirational film with a ten-second hook, timed
narration, mathematical visuals and music cues. It distinguishes admitted pilot
evidence, the broader study design and an ambitious vision of human agency.
It is ready for creative review before implementation with `anim`.

Build from the repository root with `make -C report`. The PDF is
`report/epistemics/build/main.pdf`. Edit front matter in `main.tex`, shared layout
in `preamble.tex`, and prose in individual `sections/` files, ordered through
`sections/outline.tex`. Preserve
concurrent report edits. Existing manuscripts elsewhere in `report/` remain
historical, with `make -C report baseline` and `make -C report agentic` as their
explicit build targets.

Use the [editor skill](../../.agents/skills/editor/SKILL.md) and
[reporting guide](../../docs/reporting/README.md). The active brief distinguishes
the frozen ContractNLI pilot from the new five-model sector study. Historical
studies are excluded. Selected visible prompt/response excerpts are explicitly authorized;
raw call logs, hidden reasoning, credentials and spending ledgers are excluded.

## Regenerating sector assets

`report/data/sector-initial.json` admits the completed initial phase from
`sector-study-da7e42f28ba54247:v8`. It retains literal grades alongside the
post hoc [source-audit sensitivity](../../harness/research/sector-expansion/source-audit.json).
The complete primary matrix and jury replay are admitted from immutable v128,
digest `7d7230ca4d18fc07c1bb8e0009cdbc1d`, in `report/data/sector-study.json`.
All 12,000 assignments are retained: 11,620 execute, 380 are structurally
unavailable, 11,483 yield valid defences and 11,469 settle. All executed
contract views pass vote, phase and balance checks. Four trajectories from v35 are included
as explicitly post hoc main-text illustrations, with exact visible excerpts in
`report/data/sector-excerpts.json`. They do not supply campaign-wide rates.
The [campaign handoff](../../harness/research/sector-expansion/HANDOFF.md)
owns live runner and recovery details.

```sh
MPLCONFIGDIR="$PWD/.harness/report-matplotlib" .harness/report-venv/bin/python report/analysis/sector_results.py --snapshot report/data/sector-study.json --output report/epistemics
MPLCONFIGDIR="$PWD/.harness/report-matplotlib" .harness/report-venv/bin/python report/analysis/sector_excerpts.py
MPLCONFIGDIR="$PWD/.harness/report-matplotlib" .harness/report-venv/bin/python report/analysis/arithmetic_probe.py
make -C report sector-diagnostics PYTHON="$PWD/.harness/report-venv/bin/python"
MPLCONFIGDIR="$PWD/.harness/report-matplotlib" .harness/report-venv/bin/python -m unittest discover -s report/analysis -p 'test_*.py'
make -C report
```

The source-group bootstrap retains all five defence seeds inside a case;
matched arm contrasts pair seeds before resampling cases. This differs from
the old single-case pilot's binomial intervals. Both the original score and
the audited sensitivity remain in the snapshot and generated statistics.
The previous pilot PDF and source were preserved under
`.harness/report-archive/contract-pilot-20261116/` before this rewrite; its
portable snapshot and generated assets remain available below.

The comprehensive intermediate-evidence appendix is generated offline from
the same admitted outputs. `report/data/sector-diagnostic-inputs.json` freezes
the read-only source-bank inventory and six systematically selected visible
exchanges. `report/data/sector-call-metadata.jsonl` retains 47,133 whitelisted
usage/status receipts, without reply bodies, private reasoning or error text.
The input snapshot verifies its parent hashes before regeneration. Re-extract
with `report/analysis/sector_diagnostics.py --extract` only when the pinned raw
artifacts and source database are available; normal rendering needs neither
network access nor the database.

`sector-diagnostic-statistics.json` and the accompanying CSVs retain the full
grade transitions, paired contrasts, confidence bins, matched forecast targets,
stance/support counts, verdict confusion, quotation checks, seed histograms and
resource profiles. `sector-source-ledger.csv` covers all 120 selected sources;
`sector-source-arm-ledger.csv` retains all 2,400 source/model/condition groups
with five-seed bit strings and branch IDs. Missing values remain distinct from
zero. These are exploratory readouts, not a new collection or independent
replication. Numeric row-only TeX files use braceless `\input` inside table
alignments so LaTeX file hooks do not interrupt the following booktabs rule.

## Regenerating pilot assets

The portable input is `report/data/epistemics-pilot.json`. It pins source artifact
`contract-micro-g9t35ump:v734` and includes 45 screen outcomes, 100 branch
outcomes and source-located selected excerpts. Extraction checks all 1,237
archived files against the evidence register; normal rendering needs no model
or network access.

From the repository root:

```sh
UV_CACHE_DIR="$PWD/.tools/uv-cache" uv venv --python 3.12 .harness/report-venv
UV_CACHE_DIR="$PWD/.tools/uv-cache" uv pip sync --python .harness/report-venv/bin/python report/requirements.lock
make -C report epistemics-assets PYTHON="$PWD/.harness/report-venv/bin/python"
MPLCONFIGDIR="$PWD/report/build/matplotlib" .harness/report-venv/bin/python -m unittest discover -s report/analysis -p test_epistemics_pilot.py
make -C report
```

To re-extract from the registered local evidence, add `--extract` to
`report/analysis/epistemics_pilot.py`. This verifies the frozen files before
writing the snapshot. Generated numeric TeX tables and vector/PNG figures
belong with the source; do not edit their cells manually. `statistics.json`
records the snapshot and report-analysis hashes and library versions.

Intervals are nominal 95% Clopper--Pearson intervals for five generations
conditional on a fixed answer and an independent Bernoulli model. They do not
describe variation across documents or model self-confidence. The appendix
shows individual seeds, binary sample variance and SD. Undefined Kimi error
cells remain N/A; the incomplete Kimi defence stays missing.

## Changelog

### 2026-11-17

- Put the clickable correspondence address in a first-page footnote attached
  to Lucas Barbosa's name. This replaces the earlier footer presentation.
- Keep historical pilot context with its full supplementary readouts, and
  reference the selected arithmetic diagnostic from the main text. Avoid
  repeating those counts while preserving their evidence and scope.
- Prefer concise prose with one job per paragraph and section; retain complete
  evidence in the appendix and essential qualifications beside findings. See
  the [concision decision](../../docs/decisions/report-concision-preserves-evidence.md).
- Frame the peer-review revision around reference agreement, confidence,
  revision and jury acceptance as separate measurements. Preserve the main
  domain figure and four source-located panels; the historical sprint page cap
  does not govern the working journal revision. See the
  [cohort-preservation decision](../../docs/decisions/peer-review-revision-preserves-primary-cohort.md).
- Match judge comparisons by source, judge, seed and call index before
  interpreting changes. Equal valid counts in two contexts can come from
  disjoint successful calls; deterministic missing-outcome bounds are not
  bootstrap confidence intervals. Rerunning failed calls with a higher output
  budget requires a separate cohort.
- Keep reference adjudication source-first and human: freeze both independent
  source reviews before releasing model responses, then assess answers,
  explanations and citation support separately. A prepared packet or additional
  model votes is not completed human review; see the
  [adjudication decision](../../docs/decisions/reference-adjudication-is-source-first-and-human.md).

### 2026-11-16

- Preserve the confirmed author names, affiliations and clickable title-page
  correspondence footer. Do not restore the removed first-draft title footnote
  or sprint-status paragraph during report rewrites; scientific limitations
  and review status remain explicit elsewhere. See the
  [front-matter decision](../../docs/decisions/report-title-page-omits-sprint-draft-markers.md).
- Move the domain reference-loss figure into the main Results, retaining its
  appendix cross-reference. Keep numerical inputs and model excerpts frozen;
  use a shorter canvas at the original type sizes and tighten repeated prose
  to preserve the main-text page limit.
- Complete a single publication editorial pass over the main paper and
  appendices. Clarify assignment counts, reference-relative grading and
  forecast targets; distinguish audit objections from the post hoc source
  audit. Preserve every result and exact model excerpt, and retain independent
  scientific review as an open requirement.
- Expand the appendix to retain intermediate endpoints, ordinary successes,
  null counts, failures and all source rows. Add fixed confidence bins,
  matched forecast bases, vote margins, categorical confusions, five-seed
  histograms and six source-located visible exchanges. See the
  [comprehensive-evidence decision](../../docs/decisions/comprehensive-appendix-retains-intermediate-endpoints.md).
- Keep new diagnostic figure PDFs free of creation-time metadata so repeated
  offline regeneration can verify exact output hashes. Retain paired contrasts
  as CSV rows as well as report tables, including zero and unavailable cells.
- Admit the complete primary matrix, with domain charts, source-group intervals,
  five-seed SDs, paired contrasts and separate correctness/acceptance forecasts.
  Preserve structural missingness, aborted panels, literal grades and post hoc
  source-audit sensitivities. The selected-case arithmetic follow-up remains
  separate from the primary estimates.
- Keep four substantive, source-located LLM exchanges in the main findings,
  using the shared black-outline panels to show objections, visible model
  explanations and observed outcomes. The sector rewrite dropped panel inputs
  while retaining the style; keep source notes inside their frames and preserve
  the four-input regression check. See the
  [trajectory decision](../../docs/decisions/sector-report-retains-source-located-visible-trajectories.md).
- Adopt *Macro-Epistemics: Confidence Under Dispute* as the report title. The
  project name gives it a distinctive identity; the subtitle describes the
  research question without asserting representative economy-wide coverage or
  a particular outcome. See the
  [title decision](../../docs/decisions/macro-epistemics-title-describes-confidence-under-dispute.md).
- Expand the manuscript as five-model sector evidence arrives. Keep literal
  and source-audited grades separate, because unit handling and fallible source
  references affect apparent epistemic errors; see the
  [grading decision](../../docs/decisions/sector-results-retain-literal-and-source-audited-grades.md).
- Preserve five seeds within their source groups when estimating uncertainty;
  the repeated generations do not increase the number of independent cases.
- Use *Macro-Epistemics* as the public-facing working project/film title and
  *Make AI Answerable* as the tagline. Veracity remains the research instrument;
  see the [identity decision](../../docs/decisions/macro-epistemics-names-the-project-veracity-remains-the-instrument.md).
- Reframe the [storyboard](storyboard.md) around human agency and a shared
  future: a ten-second hook, Veracity reveal, two pilot observations and a
  22-second visionary act. Keep the ivory/cream palette and the 118-second cap;
  see the [narrative decision](../../docs/decisions/storyboard-leads-with-human-agency-and-a-shared-future.md).

### 2026-11-15

- Use Lucas's light visual direction for the [storyboard](storyboard.md): ivory
  and cream backgrounds, dark forest greens and earthy accents throughout.
  See the [palette decision](../../docs/decisions/storyboard-uses-ivory-cream-and-earthy-greens.md).
- Add the [two-minute storyboard](storyboard.md), centered on the frozen legal
  pilot's source/jury disagreement and conditional seed variability. Keep the
  expansion prospective; see the
  [narrative decision](../../docs/decisions/two-minute-storyboard-centers-the-frozen-legal-pilot.md).
- Add Lucas's correspondence address, `lucas.barbosa@nyu.edu`, as a clickable
  title-page footer using the standard `fancyhdr` package.
- Record Stefan Gazzana's full name and Roundarc affiliation in the author block
  and PDF metadata, as confirmed by Lucas.
- Replace the scaffold with the first evidence-backed draft, generated assets,
  source-located prompt/response panels and a proposed multi-document follow-up.
  Preserve the native Computer Modern override and the first-draft status.
- Admit only the frozen pilot's CP1--CP3 observations. Treat five seeds as
  conditional generations, preserve failures, and separate reference grades
  from jury acceptance. See the
  [analysis decision](../../docs/decisions/epistemics-draft-uses-conditional-seed-uncertainty.md).

### 2026-11-14

- Use `editor` for report prose and substantive review. Keep the draft structural
  until results arrive, then update the brief's claim-to-evidence map before
  strengthening claims; preserve concurrent edits rather than replacing the
  manuscript wholesale.
- Preserve the supplied Apart PDF alongside the user's Methodology and
  Discussion headings. `make -C report` builds this active draft; `baseline`
  and `agentic` select historical manuscripts so old findings cannot silently
  become current sprint results. See the
  [report setup decision](../../docs/decisions/cloud-experiments-and-evidence-led-apart-report.md).
- Reuse the earlier report's black-header prompt/response panels through
  `report/trace-panels.tex`. The dummy exchange under Results is illustrative
  only and must be replaced with admitted evidence or removed.
- Use LaTeX's default Computer Modern text and mathematics at Lucas's request,
  overriding the source PDF's Old Standard TT font while retaining its structure
  and layout. Preserve this deliberate
  [font override](../../docs/decisions/report-uses-native-computer-modern.md)
  when checking template fidelity.
- Establish a separate sprint scaffold using the current Apart template,
  preserving imported research unchanged. Report development follows the
  experiments rather than anticipating their results.
