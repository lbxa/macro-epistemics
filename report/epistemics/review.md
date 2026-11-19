# First-page correspondence footnote — 2026-11-17

Lucas Barbosa's author name links to the correspondence footnote. The email
address has a verified mailto annotation on page one. The fixed-epoch
`make -C report` build passes without warnings. Rendered review covers pages
one and two, which contain the footnote and the reflowed introduction. Text
layout on pages 3–65 matches the prior draft.

Repository verification reaches the Docker-dependent harness checks and times
out. The Docker daemon also times out on a separate probe. Log
`/tmp/apart-correspondence-verify.log`.

PDF SHA256 `04fe75d345d73b686af306aee2e69554fcf535b2d84854b935635005232d93af`.

# Second concision pass — 2026-11-17

Codex-assisted editorial review at base revision
`6088e01ebdf77766fae9f9a80ea1e716a3973111`, preserving the dirty research
checkout. This pass changes prose and float placement, not admitted evidence.

| Prose estimate / pages | Before | After |
| --- | ---: | ---: |
| Main prose | 2,565 | 2,018 |
| Main and appendix prose | 9,543 | 7,985 |
| Main pages | 11 | 10 |
| Total pages | 68 | 65 |

The same TeXcount `-sum -brief` method excludes generated table/panel inputs
and bibliography, retaining section headings, captions and mathematical
expressions. Reductions are 21.3% and 16.3%, respectively. Comparison copy:
`/tmp/apart-concision-pass2-before`; computed audit:
`report/epistemics/build/editor-pass2-audit.json`.

Pilot context now accompanies its supplementary readouts; the main arithmetic
illustration points to the full diagnostic. Methods and interpretations are
shorter without dropping selection rules, missingness, grade uncertainty or
source weighting. All 113 data-derived files, 17 citation keys, 98 labels,
19 figures, 38 tables and four frozen main panels are preserved. The human
review protocol explicitly freezes both source reviews before releasing answers.

The fixed-epoch clean Makefile build exits zero with no layout/reference
warnings (`/tmp/apart-editor-pass2-clean-build.log`). PDF SHA256:
`ee86a04a9a84aeaaaf29e0cc3ead336dec598ae7f6ab75eee25af3b7bedbcd87`.
It contains ten main pages, two reference pages and 53 appendix pages.
All 65 rendered pages were checked in contact sheets, with full-page checks
of main figures/panels, provenance and the adjudication protocol. Fonts,
margins and numerical assets are unchanged.

Verification: 71 report tests and 554 harness regressions pass. The initial
restricted harness attempt encountered loopback denials; the permitted rerun
passes. The full `bash scripts/verify.sh` passes Foundry/Rust checks, formatting,
Clippy and builds, then stalls at `docker info`. Bounded daemon probes time
out despite opening Docker. The gate was interrupted (exit 130); its 36
Docker integration checks remain unverified for this pass. Logs:
`/tmp/apart-editor-pass2-tests.log`,
`/tmp/apart-editor-pass2-harness-unit-local.log` and
`/tmp/apart-editor-pass2-verify.log`. Whitespace and decision-index checks pass.

Decision: **editorially reviewed draft; full verification blocked by Docker**.
Human adjudication, author approval and venue/release checks remain open.
No new experiments, paid calls or public release; archived manuscripts remain unchanged.

# Concision revision — 2026-11-17

Codex-assisted editorial and rendered-page review of the current dirty
checkout, following Lucas's request for concise, high-signal prose. The
scientific evidence selection is unchanged. Independent human scientific
approval remains pending.

| Measure | Before | After |
| --- | ---: | ---: |
| Main prose estimate | 4,044 | 2,565 |
| Main and appendix prose estimate | 11,485 | 9,543 |
| Main pages | 13 | 11 |
| Total pages, including references and appendices | 72 | 68 |

Word estimates use TeXcount `-sum -brief` on the same section files in both
versions, including headings and captions but excluding generated inputs
(tables and quoted panels) and bibliography. Main prose decreases 36.6%;
all section prose decreases 16.9%. The pre-edit copy is retained at
`/tmp/apart-concision-before` for this comparison.

The introduction states the question and contribution; Results retain the
counts; Discussion interprets them; Conclusion states the implication.
Repeated caveats and operational detail are condensed without dropping
grading uncertainty, concentrated missingness or replication limits. All
113 data-derived figure, table, CSV and JSON files match the pre-edit bytes;
all 17 citation keys and four frozen main panels remain. The appendix's
outdated description of the revised objection policy now points to its
completed, separately admitted rerun.

Clean build: `latexmk -C -outdir=build main.tex` in `report/epistemics`, then
`SOURCE_DATE_EPOCH=1794821400 FORCE_SOURCE_DATE=1 make -C report`, exit zero.
Compiler remains pdfTeX 1.40.27 / TeX Live 2025. Log:
`/tmp/apart-concision-clean-build.log`. No layout, citation or reference
warnings remain. Current PDF: `report/epistemics/build/main.pdf`, SHA256
`1e50e0f2627c8ab32f42edbc0949294dbf8ce4406074ebb41956c3a5d60731fc`.
It comprises 11 main pages, two reference pages and 55 appendix pages.

Rendered review covers all 68 pages in contact sheets, with full-page checks
of both main figures, all four main panels and the repaired appendix reading
order. Panel explanations stay with their boxes. The domain figure remains
in Results §4.1. Pilot figures no longer interrupt the independent-review
protocol. Existing type sizes and margins are unchanged.

The report suite passes all 71 tests. `bash scripts/verify.sh` exits zero,
including 554 harness regressions and 36 Docker-isolated integration tests,
plus Rust, Solidity, hooks, formatting, Clippy and builds. Logs:
`/tmp/apart-concision-report-tests.log` and `/tmp/apart-concision-verify.log`.
Diff whitespace checks pass. No model calls or new experiments were run.

Decision: **editorially validated research draft; not submission-ready**.
Human adjudication, author approval and venue/release checks remain open.
The archived v0 PDF and supplementary ZIP below predate this local editorial
revision and remain unchanged.

# Peer-review revision — 2026-11-16

Implemented the publication feedback through delegated prose, evidence,
experiment and independent code-review work. The title is now *Confidence,
Correction, and Consensus: Evaluating Language Models Under Dispute*.
The primary cohort, four quoted panels and domain figure remain intact.
Expanded primary-source related work and two separately admitted numerical
replications support a narrower interpretation of the selected judge failure.

Three immutable artifacts were downloaded through the standard W&B API and
checked against their digests and file hashes. `peer-review/admission.json`
binds them to the portable results and receipt-backed execution register.
The projection contains no recovery databases, signing material, private
transcripts or SDK reasoning. All 1,500 numerical assignments and 720 judge
calls remain accounted for; 39 failed DeepSeek calls remain missing.

The main text reports both the complete GPT-OSS near-null replication and
the incomplete DeepSeek comparison. Its zero paired change covers two
sources, not three. All-assigned missing-outcome bounds [−28.9, +31.1] pp
are distinguished from confidence intervals. Source weighting, original
education strata, grading sensitivities, single-source intervals and
unequal completion are disclosed. No independent human labels are invented.

Final PDF SHA256:
`dff73414aa279b7c0e633060684576a8a3c79520e30297aa4ebb7f0d4fc8eb9b`.
There are 72 pages: 13 main, two references and 57 appendix. This working
revision supersedes the historical sprint page cap; it is not a journal
submission. The fixed-epoch Makefile build passes without layout/reference
warnings. Rendered checks cover the changed main text, both main quantitative
figures, all four quoted panels and the new appendix tables/plots. Original
numerical assets and source-located panels remain unchanged.

The full repository gate passes with 554 default harness tests and 36
Docker-isolated integration tests, plus Rust, Solidity, hooks, formatting,
Clippy and builds. The offline report suite passes 71 tests; focused analysis
and adjudication tests pass 38. Ruff checks pass for the added report and
operational scripts. Offline reproduction of historical statistics remains
unchanged; the portable extension rows reproduce their new source summaries.

Open publication gates are qualified independent reference adjudication,
author scientific approval, source reuse checks, final venue selection and
anonymous venue formatting. A prespecified larger-output-budget sensitivity
could resolve the truncated DeepSeek comparisons without replacing this
cohort. No submission, reviewer contact or public release was performed.

Post-archive check: finished report run `be3b408f03d8402e` retains
`sector-peer-review-report-da7e42f28ba54247:v0`, digest
`c7fe3d37428f6455487b558d1bec6912`. Its 213 payload files and manifest
were verified before packaging. A fresh standard-API download of the PDF,
13,341,482-byte supplement and manifest matches their recorded SHA256s.
The external `peer-review/publication.json` supplies the immutable pointer;
this admission note does not alter the archived manuscript or its review status.

# Main-text figure placement — 2026-11-16

Moved the four-domain reference-loss plot into Results §4.1 (Figure 1,
page 5), beside the headline table. Removed its appendix duplicate and kept
a cross-reference. The shorter chart canvas retains the original font sizes,
values and intervals. Condensed repeated main-text prose to preserve the
eight-page limit and all four model-output panels; class-label definitions
remain in the protocol appendix.

The rebuilt PDF has 63 pages: eight main, one references and 54 appendix.
SHA256: `b38b2282e6fac380962bdd0779644aae810b0391476acee31326fa2085dfc59f`.
Inspected the rendered figure page; the build reports no layout or reference
warnings. Frozen statistics and numerical tables remain unchanged. The full
repository verification passes, including 502 harness unit tests and 36
integration tests. This local layout revision supersedes the PDF below;
the archived v2 manuscript remains immutable. Scientific review gaps remain.

# Publication editorial pass — 2026-11-16

Completed one editorial pass through the main paper, references and all
appendices at Lucas's request. Collection is complete; this pass changes no
experimental outputs, grades, analysis or model quotations. All 105 frozen
data, table, figure, CSV and statistics assets checked against report artifact
v1 remain byte-identical.

The edit clarifies the assignment equation, valid-output denominators,
reference-relative Brier targets, and the distinction between audit objections
and the post hoc source audit. It narrows the encoding-countermeasure claim
to the audited inputs, replaces an ambiguous inference from selected
trajectories, distinguishes ranking from the mean confidence gap, and removes
an orphaned sentence at a main-text page break. The final abstract has 227
whitespace-delimited words. Bibliographic entries were checked against their
primary ACL/arXiv pages; LiveBench now uses the revised 2025 title,
*A Challenging, Contamination-Limited LLM Benchmark*. The official Apart
requirements were rechecked on November 16.

Final PDF: `report/epistemics/build/main.pdf`, SHA256
`a27e07ec36b52997bff0aa3f444399c98813c10d9ebf31f2cffb388048b185e8`.
It retains eight main pages, one reference page and 55 appendix pages.
Native Computer Modern, author affiliations, correspondence footer, four
main-text panels, all supplementary readouts and the required ethics appendix
are preserved. The clean pdfTeX/latexmk build passes with no layout/reference
warnings or missing glyphs (`/tmp/apart-editor-final-build.log`). All 53 report
tests pass (`/tmp/apart-editor-tests.log`). Rendered review covers all 64 pages,
with separate final-size checks of the revised main pages and preserved
quantitative figures. No clipping, broken panels or unresolved references
were found.

The full repository verification gate also exits zero: Rust/Solidity tests,
formatting, Clippy, hooks, builds and 532 harness tests pass in 448.60 seconds
(`/tmp/apart-editor-verify.log`). Whitespace and decision-index checks pass;
all 35 PDF fonts are embedded. The bounded entropy review found no new drift.

This is editorial preparation for publication, with independent adjudication
of disputed references and author scientific approval still open. Neither
submission nor public release was performed. Prior admitted report versions
retain their original status and hashes.

The editorial source and PDF are archived in finished report-only W&B run
`1652b0d5a0a64c2a`, artifact `sector-report-da7e42f28ba54247:v2`, digest
`5a6c61802b1b27fbbd717e7de8802630`. The external admission register is
`harness/research/sector-expansion/report-publication-editorial.json`.

# Structural scaffold review — 2026-11-14

- **Stage:** structural draft, not submission-ready.
- **Source:** `report/epistemics/main.tex`, `preamble.tex`, and
  `sections/outline.tex`; uncommitted working-tree changes.
- **Output:** `report/epistemics/build/main.pdf`, three US Letter pages.
- **Authority:** Lucas's recommended outline and supplied Apart template PDF;
  live AI x Epistemics sprint guidelines checked on 2026-11-14. Template identity,
  checksum, and adaptation are recorded in `report/template/epistemics.md`.
- **Build:** `make -C report clean`, then `make -C report`, both exit 0.
  pdfLaTeX 1.40.27, TeX Live 2025, latexmk 4.86a. No bibliography pass is needed
  while the References section is a placeholder. Final build log:
  `report/epistemics/build/main.log` (local ignored output).
- **Warnings:** no font substitution, overfull/underfull box, undefined
  reference, or LaTeX warning in the final log. The first build's arbitrary-size
  math-font substitutions were resolved with the standard `fix-cm` package.
- **Visual review:** rendered all three final pages with Poppler and inspected
  the complete pages at readable manuscript scale. Checked title rules, type,
  author/abstract positioning, heading hierarchy, body margins, footnote
  separation, page breaks, and appendix. No clipping, overlap, or unreadable
  labels found. Compared the title and body styling with the supplied template.
- **Scientific review:** all research sections explicitly say pending. No
  numerical findings, citations, invented author identities, or material
  contribution claims have been added. The draft status is visible.

## Open checks

- Confirm the final title, author roster/affiliations, track, and question.
- Admit cloud experiment evidence and create the claim-to-evidence map before
  replacing placeholders with substantive prose, plots, tables, or conclusions.
- Complete the abstract at 150–250 words after results are established.
- Complete limitations, dual-use/ethics, personal-data handling, and LLM-use
  disclosures from the actual work. Remove all draft guidance before submission.
- Recheck the eight-page main-text cap and compare the final populated report
  with the supplied template. Review every final page and verify all citations.

**Decision:** structure and initial formatting ready for iterative development;
empirical content and final submission review remain open.

## Computer Modern revision — 2026-11-14

At Lucas's request, removed OldStandard and the explicit T1 encoding override
so the manuscript uses LaTeX's native Computer Modern fonts. Retained the
section structure and layout. `make -C report` succeeded with no LaTeX warnings,
undefined references, or overfull/underfull boxes. `pdffonts` confirms embedded
Type 1 Computer Modern regular, bold, and italic faces. Re-rendered and inspected
all three Letter pages for title fit, wrapping, heading hierarchy, footnote
spacing, and appendix layout; no clipping or overlap found. Scientific content
remains placeholders, and the open submission checks above still apply.

## Shared AI panel example — 2026-11-14

Loaded the earlier report's black-header panel style from the shared
`report/trace-panels.tex` and added a dummy prompt/response under Results.
Its title and source note explicitly identify invented illustrative content.
Both `make -C report` and `make -C report agentic` succeeded. The active draft
still has three pages and no LaTeX warnings or overflowing boxes. Inspected
all three rendered pages, including the panel's header, divider, text wrapping,
source note, and resulting page breaks. Computer Modern is retained, and no
historical experiment excerpts are included in the active draft.

## First empirical draft — 2026-11-15

**Reviewer:** Codex, automated scientific/editorial and rendered-page review.
This record does not claim independent human approval. The earlier scaffold
reviews above are historical; the following record describes the current PDF.

**Source revision:** `c7cfbd779718116ad679a22719bb68ec31ae5825`, with
uncommitted report, analysis, evidence and decision changes. Existing harness
changes from the experiment were preserved. Manuscript:
`report/epistemics/main.tex`; output: `report/epistemics/build/main.pdf`.
PDF SHA256:
`5eafd8efe13f798c2c795bb4560a512a8e357a0dae24df771e32904d12bb9d39`.

**Venue and stage:** Apart AI x Epistemics Research Sprint, November 13–15,
2026; Track 1 first draft, with related Track 2 discussion. Official rules
were rechecked on November 15. The PDF has eight main-text pages, one reference
page and four appendix pages; its abstract has 210 words. Lucas supplied the
author block: Lucas Barbosa (NYU) and Stefan without an affiliation. The Apart
layout and requested native Computer Modern override are retained.

### Scientific and editorial checks

| Check | Status and evidence |
| --- | --- |
| Claim-to-evidence mapping | Pass for the draft's scoped CP1–CP3 observations in `docs/reporting/paper-brief.md`; no historical campaign is admitted as new evidence. |
| Frozen inputs and analysis | Pass. Artifact `contract-micro-g9t35ump:v734`, digest `fc3d2a8f00f10f0ffb65e3fcc795a92b`; all 1,237 archived files verified before extraction. Report-analysis SHA256 `a589c049e11a49e1e7c90335310ebc780501664a8e994155d7e2d730772d99fe`; snapshot SHA256 `8ccc5ce4d4234628de4010d0c9dd763c67882fdc1c5c86643c5c27b422ea2d60`. |
| Observation units and denominators | Pass. Methods and captions distinguish 45 screens, 100 assigned branches, 99 completed defences, 95 settled verdicts and 94 full three-ballot panels. One error document is not treated as 40 independent documents. |
| Uncertainty and missingness | Pass within the stated model. Five-generation cells use sample variance/SD with denominator four and nominal exact 95% Clopper–Pearson intervals. The independent Bernoulli assumption and conditional scope are explicit. Kimi's absent error stratum is N/A; its incomplete defence and all missing verdicts remain visible. No pooled jury interval or between-arm significance claim is made. |
| Prompt and response evidence | Pass. Two selected panels use exact contiguous visible excerpts with source paths, field/file hashes and character offsets. Selection is identified as post hoc. Source audits supply guidance over the same agreement, not new external facts. Hidden reasoning and private raw calls are excluded. |
| Main-track scope | Pass. Assertion–defence revision and reference/jury disagreement are observed. Numerical confidence calibration, downstream decision quality, intentional gaming and benchmark-refresh efficacy remain unmeasured. |
| Alternative explanations | Pass. Discussion and ethics appendix identify selection, one-case error scope, reasoning-setting differences, common-family jurors, public benchmark exposure, possible annotation error and absent non-Veracity control. |
| Reader comprehension and internal consistency | Pass for a first draft. Read abstract, introduction, methods, results, discussion and conclusion continuously; hypotheses, endpoints and uncertainty are defined before interpretation. Abstract, generated tables, figure captions and conclusion agree. |
| References | Pass. Scientific citations were checked against primary paper/publication pages; official sprint rules and SciPy exact-interval documentation were checked directly. Automatic cross-references resolve. |
| Legal interpretation and author scientific approval | Open. The supplied reference is a benchmark grade, not certified legal truth. Lucas and Stefan should arrange independent adjudication of `293/nda-1` and review the scientific interpretation before submission. |
| Final submission | Not applicable to this task. No submission was requested or performed. Recheck live rules and obtain author approval before treating the draft as submission-ready. |

### Regeneration and deterministic verification

The report environment uses Python 3.12.11, Matplotlib 3.11.2, NumPy 2.5.4,
SciPy 1.18.1, Pillow 13.0.0 and Colorspacious 1.1.2, pinned in
`report/requirements.lock`. It is separate from the harness environment.
From the repository root, the executed asset and test commands were:

```sh
MPLCONFIGDIR="$PWD/.harness/report-matplotlib" .harness/report-venv/bin/python report/analysis/epistemics_pilot.py --extract
MPLCONFIGDIR="$PWD/.harness/report-matplotlib" .harness/report-venv/bin/python -m unittest discover -s report/analysis -p 'test_*.py'
```

Both exited 0. All 26 report tests passed, including nine pilot tests covering
intervals/variance, absent strata, missingness, duplicated cells, exact excerpt
offsets and rejection of tampered archived input. Ruff check and formatting
passed for the two new analysis/test files. All three charts and three numeric
tables are generated from the frozen snapshot, along with the excerpt panels
and source quotations; no numeric table cells were authored manually.

`bash scripts/verify.sh` exited 0, including Solidity/Rust/hook checks and
503 harness tests in 407.30 seconds. Local log:
`/tmp/apart-epistemics-report-verify.log`. No model API calls were made for this
report work. `git diff --check` and the generated decision-index check passed.

### Compilation and visual acceptance

The active output was cleaned with `latexmk -C -outdir=build main.tex` from
`report/epistemics`, then rebuilt using `make -C report` from the repository
root. Subsequent local revisions were rebuilt and their affected pages
reinspected. All builds exited 0. Compiler: pdfLaTeX 1.40.27, TeX Live 2025;
driver: latexmk 4.86a. References use LaTeX's native `thebibliography`, so no
external bibliography pass is required. Final logs:
`report/epistemics/build/main.log` and
`/tmp/apart-epistemics-first-draft-build.log`.

- **Pass:** no LaTeX warnings, undefined references/citations, missing glyphs,
  duplicate labels or overfull/underfull boxes in the final log.
- **Pass:** all 13 Letter pages rendered with Poppler at 96 dpi and inspected
  at manuscript scale. Checked title and author fit, abstract, paragraphs,
  equation margins, table rules, panel wrapping, float order, captions,
  references, source hashes and appendix breaks. No clipping or overlap found.
  Compared title/body layout with the supplied template; the deliberate font
  override and populated content preclude pixel-identical pagination.
- **Pass:** all 19 PDF fonts are embedded. Charts have manuscript-compatible
  typography, vector PDFs and 300-dpi PNG companions at 6.5-inch width.
- **Pass:** all three figures inspected in original color, grayscale and full
  deuteranopia simulation. Numbers, shapes and hatching retain meaning without
  color. Exact intervals are distinguished from descriptive variance/SD.
- **Pass:** final revisions were compared page by page; changed pages 4 and 7
  were reinspected individually. Final render directory:
  `/tmp/apart-epistemics-final-v2/`. Accessibility previews are in
  `/tmp/apart-epistemics-review/`.
- **Accepted non-LaTeX diagnostics:** FontTools reports legacy low font
  timestamps for Cmr10, and Colorspacious 1.1.2 emits a Python 3.12 docstring
  escape warning. Neither changes calculations or rendering. No accepted
  material layout warning remains.
- **Not applicable:** theorem/proof validation, SD shading and external
  bibliography tooling; this empirical draft uses exact-interval point plots,
  raw binary observations and a native bibliography.

**Decision:** first empirical draft ready for author review. Independent
reference adjudication, human scientific review and final submission approval
remain open. The proposed next study is document-level replication with
prospective source-confidence reports and separate jury forecasts, crossed
judge families and document-clustered uncertainty. It has not been executed.

## Author metadata correction — 2026-11-15

Lucas confirmed the co-author as **Stefan Gazzana**, affiliated with
**Roundarc**. Updated the active manuscript's author declarations, visible
affiliation, PDF author metadata and current reporting documentation. Historical
author records above and in imported briefs remain as originally recorded.

`make -C report` exited 0. The rebuilt PDF remains 13 pages, with no LaTeX
warnings, undefined references or overfull/underfull boxes. Codex rendered and
visually inspected page 1 at manuscript scale: both author names and affiliations
fit without overlap. Text and layout extraction for pages 2–13 matches the
pre-update PDF. No scientific content or numerical assets changed.

PDF: `report/epistemics/build/main.pdf`; SHA256:
`6bd3f46f815f02cb4ce701d3c1f5f64a2546f27a976f72eae8b5f82925e617a9`.
Build log: `/tmp/apart-epistemics-author-update-build.log`; page preview:
`/tmp/apart-epistemics-author-update.png`. The first draft's open scientific
review checks remain open.

## Title-page disclosure removal — 2026-11-15

At Lucas's request, removed the title-page paragraph beginning “First empirical
draft, November 15, 2026” through “independent reference adjudication remains
open,” together with its preceding spacing. `make -C report` exited 0. The PDF
remains 13 pages; only page 1 differs in text/layout extraction from the prior
PDF. Codex rendered and inspected that page: the disclosure is absent, with no
clipping or overlap. No LaTeX warnings, undefined references or overfull/underfull
boxes were found. This presentation change does not alter the evidence or the
review status recorded above.

PDF SHA256:
`84d317617325fb5fe7b36f0c6702a3c9697e1274ab8fd1b7df6947c4d7879a09`.
Build log: `/tmp/apart-epistemics-disclosure-removal-build.log`.

## Title footnote removal — 2026-11-15

At Lucas's request, removed the title's footnote command, including its marker
and the “First draft for the AI x Epistemics Research Sprint” text.
`make -C report` exited 0. The PDF remains 13 pages. The freed space lets the
Introduction begin on page 1 and reflows main-text pages 2–8; text/layout
extraction for pages 9–13 is unchanged. Codex rendered and inspected all eight
affected pages. The marker and footnote are absent, and no clipping, overlap,
LaTeX warnings, undefined references or overfull/underfull boxes were found.
Manuscript findings and author metadata are unchanged.

PDF SHA256:
`43af9d9a7cd2939394f7f77d370e83fdb936124ee08dd9b82773db8f58623ce4`.
Build log: `/tmp/apart-epistemics-footnote-removal-build.log`; rendered previews:
`/tmp/apart-epistemics-footnote-removed.png` and
`/tmp/apart-epistemics-footnote-review/`.

## Correspondence footer — 2026-11-15

At Lucas's request, added “Correspondence: lucas.barbosa@nyu.edu” to the
title-page footer, with a `mailto:` link and no footnote marker. The first page
uses a dedicated `fancyhdr` page style; the other pages retain their existing
empty style. The installed package is fancyhdr 5.2, dated February 7, 2025.

`make -C report` exited 0. The PDF remains 13 pages, with no warnings, undefined
references or overfull/underfull boxes. Codex rendered and visually inspected
page 1: the footer is readable and separated from body text. Text/layout
extraction for pages 2–13 matches the pre-update PDF. Findings, author metadata
and the open scientific review checks are unchanged.

PDF SHA256:
`0eadb6ef6a45c67a301fd31101447c922137659a60a743e0b680745fca0438ed`.
Build log: `/tmp/apart-epistemics-correspondence-build.log`; page preview:
`/tmp/apart-epistemics-correspondence.png`.

## Scientific title update — 2026-11-16

Lucas requested an avant-garde, objective and concise title incorporating the
macro-epistemics direction and delegated its wording. Selected
**Macro-Epistemics: Confidence Under Dispute**. Updated the visible two-line
title, LaTeX title, PDF metadata and current title references in the report
README, paper brief and venue record. Historical review titles remain intact.
The [title decision](../../docs/decisions/macro-epistemics-title-describes-confidence-under-dispute.md)
records the scope of this naming change.

`make -C report` exited 0. The current sector-study PDF remains 13 pages, with
no warnings, undefined references or overfull/underfull boxes. PDF metadata
matches the new title. Codex rendered and visually inspected page 1 at
manuscript scale: the title fits, and author affiliations and the correspondence
footer remain readable. Text/layout extraction for pages 2–13 matches the
pre-update PDF. This check concerns the title and layout; it does not admit
additional experiment evidence or replace the sector study's scientific review.

PDF SHA256:
`bb45ee89cf07e74db1bf6caad7a1225e6f2d6285d0122b130a6bbd51afc2a98a`.
Build log: `/tmp/apart-epistemics-title-update-20261116.log`; page preview:
`/tmp/apart-epistemics-title-update-20261116.png`.

## Restored visible model trajectories — 2026-11-16

**Scope and cause.** Lucas requested the black-outline output boxes and at
least three or four substantive agent examples in the main report. The shared
`modelexample` environment was still loaded; the sector rewrite had removed
the old panel inputs from Results. Restored four generated panels using the
existing style. Each panel, its source note and its observed forecasts/votes
stay together. The main Results now discusses the four examples individually.

**Evidence admission.** Read the existing W&B run without changing it or making
model calls. Pinned `sector-study-da7e42f28ba54247:v35`, digest
`140e490593b5152b2a7759e70974d752`, cutoff November 16 at 06:11:41 UTC.
All six downloaded exports match W&B manifest digests and SHA256 hashes.
Cases and all initial response bytes match the previously admitted v8 files.
Each selected defence matches its original answer hash and has three verified
ballots. The portable snapshot retains exact field pointers, row IDs, character
offsets and hashes for contiguous visible excerpts. Private SDK reasoning and
complete agreements are excluded.

The brief admits SS4 as four post hoc illustrations, not treatment rates or
independent evidence of internal belief. X1 shows a 99%-confident arithmetic
error corrected on neutral review; X2 preserves the finance unit-audit
distinction; X3 shows a persistent legal reference disagreement and a divided
jury; X4 rejects the false objection while weakening the original claim.
The scientific/legal interpretations still need independent adjudication.
Initial aggregate statistics remain pinned to v8. The ongoing campaign and its
budget, runner, observations and ledger were not modified.

**Analysis and checks.** `report/analysis/sector_excerpts.py` extracts and
regenerates the four panels. Code SHA256:
`3b3c9f8d20881f507d1a34abe968a66262fd90089c0747276d61f28e67303544`.
Snapshot SHA256:
`739c3c8c368b3a96c5586bab181ca43ff1c6738cba5bdc62032d49188ee454da`.
The locked report environment passed all 41 deterministic report tests,
including five new checks for contiguous offsets, tampering rejection,
four framed outputs and all four main-section inputs. Ruff check/format,
decision-index validation and `git diff --check` passed. No Rust or harness
runtime code changed; no new model experiments were run.

Commands from the repository root:

```sh
MPLCONFIGDIR="$PWD/.harness/report-matplotlib" .harness/report-venv/bin/python report/analysis/sector_excerpts.py --source harness/results/sector-excerpts-20261116/v35
MPLCONFIGDIR="$PWD/.harness/report-matplotlib" .harness/report-venv/bin/python -m unittest discover -s report/analysis -p 'test_*.py'
make -C report
```

Normal regeneration omits `--source` and uses the portable snapshot without
network access. A separate clean-output build from `report/epistemics` also
passed: `latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error
-outdir=/tmp/apart-epistemics-excerpts-clean main.tex`. Toolchain is unchanged:
pdfLaTeX 1.40.27 / TeX Live 2025 and latexmk 4.86a. No new dependency was added.

**Rendered acceptance.** The PDF has eight main-text pages, one references
page and seven appendix pages. All 16 final pages were inspected at manuscript
scale using Poppler renders; changed pages were re-rendered after local layout
repairs. Panels X1–X4 are on pages 5, 6, 6 and 7, with legible black outlines,
black title tabs, role labels, separators and source notes. Detailed numerical
plots and the grading table were retained in the appendix. All 13 PDF fonts
are embedded. Both incremental and clean logs have no warnings, undefined
references, missing glyphs or overfull/underfull boxes. Quantitative assets and
their source data were not regenerated or changed by this editorial pass.

Final PDF: `report/epistemics/build/main.pdf`, SHA256
`531637b12b38894b52cf4e5ebadca062b02757775ac2a114bb253460f8be57b4`.
Logs: `/tmp/apart-epistemics-excerpts-build.log` and
`/tmp/apart-epistemics-excerpts-clean-build.log`. Rendered checks:
`/tmp/apart-epistemics-excerpts-review/`.

**Decision:** restored case panels and draft ready for author review. Full
dispute estimates, independent source adjudication and final scientific
approval remain open. This automated review does not certify submission
readiness.

## Complete five-model study — 2026-11-16

This record supersedes the earlier interim counts for the active manuscript;
the earlier reviews remain historical. Reviewer: Codex, automated scientific,
editorial and rendered-page review. Independent human scientific approval is
not claimed.

**Source and output.** Base revision
`c7cfbd779718116ad679a22719bb68ec31ae5825`, with preserved concurrent changes.
The title, Lucas Barbosa / Stefan Gazzana author block, affiliations,
correspondence footer and all four main-text framed examples are retained.
The final PDF has **29 pages: eight main, one references, twenty appendix**.
The abstract has 223 whitespace-delimited words. PDF SHA256:
`fc25f5eb4105d2e732c3abdd0d6b35e7a4ca50ef2f17f49a480444e9b8acb688`.

**Frozen evidence.** Final matrix/replay artifact
`sector-study-da7e42f28ba54247:v128`, digest
`7d7230ca4d18fc07c1bb8e0009cdbc1d`; selected excerpts remain pinned to v35,
digest `140e490593b5152b2a7759e70974d752`. The separate validity audit is v0,
digest `698f703d0ff227544c8bb9f7d4e833ff`. Contract-evidence v0 has digest
`bd0ff1ba88bcafab1b9351c6d5166daf`; arithmetic-diagnostic v0 has digest
`17469e0e688c710966d533d7e2e4bd79`. The brief maps SS1–SS11 to these inputs.
All downloaded files pass manifest MD5 and SHA256 checks; all 23,466 archived
episode members pass their per-file hashes. Evidence-register input hashes
match the final matrix export. Initial and primary-branch bytes are unchanged
from the earlier admitted complete phases.

**Observation units.** The study retains 600 initial attempts, 581 usable
answers, 12,000 primary assignments, 11,620 executed episodes, 11,483 valid
defences and 11,469 settled verdicts. The 380 unavailable assignments are
exactly nineteen missing initials times twenty branches. The 151 aborted
primary panels remain distinct from settlement. Replay contributes 113
executed episodes, 109 paired verdicts and one disagreement; it is not pooled
as additional independent sources. The diagnostic retains 124/125 usable
standalone calls and executes no new settlements. No failed seed is replaced.

**Scientific checks.** Source-group bootstrap intervals retain repeated seeds
within the source and original sampling strata. Paired contrasts match seeds
before source averaging; all intervals are pointwise and exploratory.
Five-seed means and sample SD use the same aggregate observation unit. Empty
error strata are N/A, boundary intervals are explicitly limited, and residual
finance report overlap is disclosed. Literal grades remain alongside the
post hoc eight-case sensitivity; thirty changed initials do not become an
estimated reference-defect prevalence. Legal/scientific mismatches remain
reference-relative, and the grade covers the final number/label rather than
every explanatory assertion. Initial confidence, original-correct forecasts,
current-answer confidence and jury-acceptance forecasts have separate targets.
Unscored checked-author jury forecasts are not assigned verdicts from a
different defence context.

The selected arithmetic diagnostic uses five blocks of three calls per
condition/family. Its exact product is checked with Decimal. The reported
15/15 versus 3/15 and 14/15 versus 0/15 comparisons match the retained rows;
checked arithmetic restores both to 15/15. Its SD is conditional on one source,
with no document-level CI or claim about an internal anchoring mechanism.
The objection inverse is an offline scripted audit, not observed model cheating;
the tested candidate policy is not silently substituted into this cohort.

**Analysis identity.** Sector analysis SHA256:
`5094b8456925660256da36c020491a2d3a0924deee5e5d3360615a834217932b`.
Arithmetic analysis SHA256:
`45a1259bc2b4e78ff310387fcb398a4aa3b13bba7a86ed860f4eddfb2bd207f9`.
Portable matrix SHA256:
`c44d7a3f3963941a0eb661c4a01832005c1742713aaade8b2aeba347d56883f6`.
Portable diagnostic SHA256:
`7adda78242567ce46f90c326005766fc875caae94727e0eac68c1378762e23f2`.
Generated statistics record the current analysis hash and locked library versions.

**Verification.** The final complete `scripts/verify.sh` gate passes Rust,
Solidity, hooks, formatting, Clippy, builds and **532 harness tests in 415.00 s**;
log `/tmp/apart-sector-final-verify-4.log`. All **45 report tests** pass, as do
Ruff checks/format checks and `git diff --check`. Clean LaTeX compilation passes
after fixing a fragile filename command in a new caption. Final log
`/tmp/apart-sector-clean-build.log` has no warnings, undefined references,
missing glyphs or overfull/underfull boxes. The build uses
`SOURCE_DATE_EPOCH=1794821400 FORCE_SOURCE_DATE=1`; native Computer Modern
text/math and embedded plot fonts are preserved.

**Rendered acceptance.** All final pages were checked using Poppler at
manuscript scale. The final added benchmark-behavior page is inspected directly;
the other 28 pages are pixel-identical to the fully inspected preceding PDF.
The four framed main examples, arithmetic panel, all tables, source-group
intervals, seed variation, missing-data cells and labels are legible and within
margins. Domain and benchmark figures, including the arithmetic follow-up, were
checked in grayscale and deuteranomaly simulation. Shape/position and printed
values preserve distinctions when colors converge. Final renders are in
`/tmp/apart-sector-admission-review/`; accessibility checks are in
`/tmp/apart-sector-final-review/` and `/tmp/apart-sector-review/`.

**Open scientific work.** Independently adjudicate disputed numerical and
categorical references, preregister the selected-case defence/evidence effect
on fresh sources, and cross task formats and judge families more fully.
Provider seeds remain best effort; the common defence instruction explicitly
discourages concession to disagreement. No internal-belief, intent, general
industry ranking or isolated platform-effect claim is admitted. Author review,
source-reuse review for any future public data release and submission remain
outside this automated acceptance. No submission or new public release was made.
# Comprehensive intermediate-evidence expansion — 2026-11-16

Review: Codex-assisted editorial, numerical and rendered-page review. This
extends the previously admitted report without new model calls or replacement
outputs. Base revision is `c7cfbd779718116ad679a22719bb68ec31ae5825`, with the
existing dirty research workspace retained. Independent human scientific
approval remains pending.

The PDF is `report/epistemics/build/main.pdf`, SHA256
`9ab732be30fca65d052e027c1e50b1e07e86c0320ebd8d5e077c5c4cb56b9afc`:
64 letter-size pages, comprising eight main pages, one reference page and
55 appendix pages. The four main Results panels, title, authors and
correspondence footer are preserved. Appendix N adds 24 numbered tables,
six new diagnostic figures, three separately identified pilot figures and
six visible exchange panels.

Evidence and calculations:

- The parent remains complete sector artifact v128, digest
  `7d7230ca4d18fc07c1bb8e0009cdbc1d`; standalone arithmetic and pilot cohorts
  retain their own pinned parents and are not pooled into primary estimates.
- The intermediate input snapshot SHA256 is
  `00b5ed8c818874337305f66020dd138d8462491e86378fa3b6b099c97cb8fccc`.
  It records the frozen bank inventory, deterministic example selection,
  parent file hashes and safe metadata projection. Call-metadata SHA256 is
  `bf807ef99ea3450129259fce700c351680049caa85d761c4a1e56e9d9963eb36`.
- All 12,000 assignments reconcile: 380 unavailable initials' branches,
  137 further unavailable defences, 11,483 valid defences and 11,469 verdicts.
  The source/arm export contains 2,400 unique groups with five ordered bits;
  the source ledger contains all 120 sources. All 120 paired contrasts,
  including zeros and N/A cells, are retained in a separate CSV.
- Original-grade/jury confusion counts sum to 11,469. The repaired-original,
  support, high-confidence and literal-quotation subsets were checked against
  the full snapshot. Initial confidence contributes once per model/source.
  Confidence-bin, update and paired intervals preserve source groups and
  sampling strata; all additional readouts are explicitly exploratory.
- The 47,133 usage/status projections reconcile with 47,008 primary/replay
  requests and 125 separate diagnostic calls. Schema-normalization overlays
  are not counted as new calls. Reply/error bodies, private SDK reasoning,
  credentials and spending/recovery databases are absent from this projection.
- Six examples retain exact contiguous prefixes, source pointers, offsets and
  hashes. Selection is reproducible within each post hoc pattern, and the
  displayed examples do not estimate frequencies or reveal internal cognition.
  Routine support, rejected mismatches and matching originals rejected by
  jurors accompany the more unusual outcomes.

Regeneration and verification:

```sh
MPLCONFIGDIR="$PWD/.harness/report-matplotlib" .harness/report-venv/bin/python report/analysis/sector_diagnostics.py --extract
make -C report sector-diagnostics PYTHON="$PWD/.harness/report-venv/bin/python"
MPLCONFIGDIR="$PWD/.harness/report-matplotlib" .harness/report-venv/bin/python -m unittest discover -s report/analysis -p 'test_*.py'
SOURCE_DATE_EPOCH=1794821400 FORCE_SOURCE_DATE=1 make -C report
bash scripts/verify.sh
```

The locked report environment and native pdfTeX 1.40.27/TeX Live 2025 build
pass. The final build starts from cleaned active-manuscript auxiliaries and
stabilizes references. Log: `/tmp/apart-expanded-clean-final.log`. There are
no TeX layout/reference warnings or missing glyphs, and all 35 fonts are
embedded. Numeric-row inputs avoid LaTeX file-hook interference with booktabs;
float barriers keep diagnostic families together. Fixed metadata makes the
six new vector figures reproducible. Repeating the offline analysis produces
identical hashes for all 53 checked tables, figures, CSVs and statistics files
(`/tmp/apart-expanded-repro-check.json`). All 53 report tests pass; Ruff checks
and formatting pass. The full repository gate exits zero, including Rust,
Solidity, hooks and 532 harness tests in 424.36 seconds
(`/tmp/apart-expanded-verify.log`).

Rendered review covers every page, using 1,350-pixel page renders and contact
sheets, with separate inspection of quantitative figures at final report
width. The main eight pages remain within the recorded venue limit. Table
headers repeat across pages; missing data stays distinct from zero; ordinary
and null outcomes remain visible. Model markers and facet labels preserve
meaning in grayscale. The six framed excerpts remain unbroken and their
source notes remain inside the frames. Pilot captions explicitly identify
selected-error correction matrices and do not describe them as all pilot
verdicts.

Open gaps remain scientific: independent adjudication of disputed references,
semantic checking of complete explanations and citation support, and author
review. The data does not identify internal beliefs, deceptive intent, a
general Veracity effect, model speed or representative industry performance.
Decision: **validated expanded research draft; not submission-ready**.

Admission verification: finished W&B report run `23ef1e166c254fcc` retains
`sector-report-da7e42f28ba54247:v1`, digest
`1e687f354c1e79d4f6ab05ad157fce52`. Every one of its 175 manifest entries
matches the curated local bundle. A fresh canonical-API download of both
`main.pdf` and `manifest.json` matches the archived bytes exactly. The external
`report-publication-expanded.json` records this check; the earlier v0 report
is preserved.
