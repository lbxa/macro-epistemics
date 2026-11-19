# Landing-page draft review — 16 November 2026

The draft preserves the supplied archive header and separates the frozen sector
initial-answer cohort from the earlier selected-case legal pilot. An independent
source review checked the displayed claims against the report snapshots.

## Verification

- `bun run sync:research` validates cohort counts, reference scores and source
  revisions before regenerating the identical source/public data exports.
- `bun run lint`, `bun run typecheck` and `bun run build` pass. Astro reports no
  errors, warnings or hints. The output is a static page.
- Chromium checks at 1440 × 1000 and 390 × 844 show no horizontal page overflow.
  Domain/model filtering selects the expected science/GPT-OSS-120B row and
  updates its accessible status text. Data tables scroll inside their own region.
- With JavaScript disabled, all four domain charts remain visible, inactive
  filters stay hidden, and the film remains a working direct link.
- The initial resource list contains no MP4. Activating the film plays the
  118-second 1920 × 1080 asset with an English caption track.
- A deliberately aborted movie request preserves the poster and reveals a
  retry/download path. Retrying successfully loads the video. The intentional
  network failure produces the expected browser console entry.
- Local artifact links resolve; the unrelated template PDF is outside public
  output. The citation identifies the draft date and both frozen artifact versions.

The native Astro poster emits responsive WebP variants of approximately 4–24 KB.
The header uses system fonts, the page has no hydrated framework, and PDF/video
prefetching is disabled. An unthrottled local mobile-width navigation recorded
LCP at 228 ms with the introductory H2 as the candidate. This is a local smoke
measurement, not a production performance claim; hosted mobile-network LCP still
needs measurement after deployment.

## Evidence and remaining scope

The sector view contains 581 interpretable initial answers from 600 attempts,
120 source groups, five model families and four domains. It retains literal
grades beside post hoc source-audit sensitivity. The pilot keeps five repeated
defence generations separate from new source cases and reports conditional
uncertainty. No ongoing dispute-phase rates are admitted here.

Screenshots and browser diagnostics are in ignored `output/playwright/`. No
public deployment, full screen-reader session or hosted-network performance
audit was performed. Re-run the asset preparation step when replacing the paper
or film, and regenerate the data only after admitting a new frozen cohort.

## Browser-only Veracity demo

The scripted demo sits directly after the abstract and before the film, with one
`demo` anchor. Visitors choose an original answer, challenge it, select a
scripted response and control three jury ballots. Links beside the demo lead to
the Veracity overview and original 2025 framework paper.

`bun run test:demo` passes four tests with 32 assertions: frozen-answer preservation
after revision/retraction, independence of jury and arithmetic, all eight ballot
combinations, guarded transitions, reset and immutable previous votes. Site lint,
type checking and static build pass with zero diagnostics. The repository gate
also passes, including all 522 harness tests; its log is
`.harness/verification/website-demo.log` at the repository root.

Chromium verification covered a saved 3.95% answer revised to 3.80% while a
unanimous jury still upheld the original. A second round retracted a correct
3.80% answer and rejected it by two votes to one; the independent arithmetic
check still marked the original correct. Reset restored the original answer,
objection and response defaults. New stage headings receive keyboard focus.
At 390px, the page has no horizontal overflow. Without JavaScript, a worked
example and the research links remain readable while inactive controls stay
hidden. Demo interactions made no fetch/XHR requests. All responses and votes
are labelled illustrative rather than measured model behavior.

## Shorter reading path

The simplified default page contains a brief abstract, the demo, three findings,
the film and compact research links. The full explorer and citation use native
disclosures. The archive header and its 4px/2px title rules remain unchanged.

At 1440px, the default reading path decreased from 1,258 visible words and
8,386px of page height to approximately 350 words and 3,161px. These are local
layout measurements with the demo in its initial state and disclosures closed,
not performance benchmarks. Essential cohort denominators and the saved-error
scope remain visible beside the findings.

Browser checks confirm that the expanded science/GPT-OSS-120B filter shows the
expected single row, the citation retains its draft date and frozen versions,
and the demo still compares a saved 3.95% original with independent arithmetic
after revision. At 390px, there is no horizontal overflow. Without JavaScript,
the demo's static example remains visible and the native chart disclosure opens
all four domain charts. Lint, type checking, the four demo tests and the static
build pass after the layout changes. Screenshots are in ignored
`output/playwright/simple-*.png`.

## Completed-study update

This update supersedes the initial-only evidence scope above. The default page
keeps the archive header, immediately following scripted demo, three findings
and closed explorer. It now admits sector artifact v128: 120 source cases,
12,000 assigned branches, 11,620 executed, 11,483 valid defences and 11,469
settled verdicts. Failed and unavailable work remains distinguishable.

The explorer covers all 20 initial and 80 dispute cells across five models,
four domains and four challenge conditions. It shows literal and post hoc
audited grading, eligible denominators, source-group bootstrap intervals and
descriptive variation across five defence seeds. The one-source arithmetic
diagnostic and offline objection-validity audit remain separate; the page
explicitly identifies the unintegrated candidate fix and the absence of evidence
that participants exploited the encoding.

Read-only W&B inspection confirmed the completed primary and diagnostic runs
and their immutable artifact digests. The paper download matches report archive
v1, SHA256 `9ab732be30fca65d052e027c1e50b1e07e86c0320ebd8d5e077c5c4cb56b9afc`.
Asset preparation now preserves that admitted PDF when the concurrent working
manuscript changes.

Chromium checks on the fresh local preview verified all four domain/condition
examples against exported counts, initial confidence filtering, an unobserved
0/0 cell, the condition-specific validity notice, arithmetic seed tables,
provenance links and PDF delivery. At 1440px and 390px there is no horizontal
page overflow; wide tables scroll within their own regions. With JavaScript
disabled, the legal audit chart and demo's worked example remain usable. A
failed lazy data request preserves the static chart and explains the fallback.
The aggregate loads only after opening the explorer; the MP4 loads only after
activation and plays with its caption track. A fresh preview also serves the
native Astro poster correctly; an older running preview had a stale Sharp
loader failure. Screenshots are in ignored `output/playwright/latest-*.png`.

Research-export tests, demo tests, lint, Astro/TypeScript checks and the static
build pass. The complete repository verification gate passes, including 532
harness tests; log: `.harness/verification/website-completed-study.log`.
No paid model calls or public deployment were performed. Hosted-network
performance and a full screen-reader review remain outside this local check.

## Primary data without disclosures

The current page supersedes the demo-led and folded-explorer layouts above.
After the preserved archive header and brief abstract, cohort counts lead
directly to two always-visible figures. A shared domain selector updates both;
challenge and measure controls belong to the defence figure. All five models
remain visible together. The demo, citation block, diagnostic tables, seed-block
drill-down and embedded film are removed from this page. Full aggregates,
data notes, paper, code, film and Veracity remain direct links.

Lint, Astro/TypeScript checks, research-export tests and the static build pass.
Chromium checks compared all 20 initial cells and 320 model/domain/condition/
metric combinations with the admitted export, including the plotted defence
interval endpoints. There are exactly two figures, ten model rows, three
filters and zero `details` or `summary` elements. No demo script or MP4 loads
on navigation. At 1280px, 1440px and 390px, there is no horizontal page overflow.

With JavaScript disabled, both legal figures and their ten model rows remain
readable; inactive controls stay hidden. The archive rules remain 4px and 2px.
Five-seed final-agreement rates and SD appear only when that outcome is selected,
so they cannot be mistaken for variation in another metric. Source-group
intervals, outcome-specific denominators, missingness, grading sensitivity and
the frozen numerical-objection flaw remain explicit. Browser captures are in
ignored `output/playwright/results-first-*.png`.

The complete repository gate also passes, including all 36 Docker integration
tests; log: `.harness/verification/results-first-website.log`. No report source,
frozen result aggregate or model run was changed for this layout revision.

## Shadcn controls

All active action controls now use the official shadcn registry: ten Button
anchors, three NativeSelect controls with FieldGroup/Field/FieldLabel, and
Separator for the header rules and chart sections. Registry source is retained
under `src/components/ui/`, with project tokens in the existing global stylesheet.
Tailwind 4's Vite integration replaces the old PostCSS pipeline. The template's
configuration remains explicitly loaded, and the light palette and system fonts
are retained.

Astro server-renders the React component composition; there are no hydrated
React islands. A production browser requested only the existing chart script,
with no React renderer, font or movie requests. Astro emits an unused renderer
asset into `dist/`; the page does not reference or request it. No-JavaScript
checks preserve both default figures, ten model rows and all ten action links,
with inactive filters hidden.

Browser verification at 1440px and 390px confirms no horizontal page overflow,
44px default control targets, labelled native selects and unchanged 4px/2px
title rules. A keyboard-focused select has the theme's visible focus ring. The
page retains its light theme when the browser prefers dark mode. All 20 initial
cells and 320 defence metric combinations, including interval positions, match
the admitted export through the new controls. Download semantics are preserved,
and a clean production browser reports no console or page errors.

Lint now includes TSX. Astro/TypeScript checks (35 files), research-export tests,
the static build and a frozen Bun install pass. The complete repository gate
passes, including 552 harness unit tests and 36 Docker integration tests; log:
`.harness/verification/shadcn-controls.log`. Screenshots are in ignored
`output/playwright/shadcn-*.png`. The Astro previews were restarted after changing
the renderer and CSS integration. No experiment calls or public deployment
were performed.

## Website editorial pass

Lucas's supplied 86-word summary abstract is preserved verbatim, with Veracity
linked inline. The left-aligned abstract has its own heading and precedes the
existing cohort counts and results figures. The editor pass clarifies original
versus post hoc audited grading, mean stated confidence, response-format
validity, the jury's saved-claim target and outcome-specific denominators.
Shared caption text keeps the static and interactive figures consistent.

The broad abstract findings were checked against the admitted primary aggregate:
under audited grading, losses are 76/10,133 eligible defences, repairs are
46/1,350, and juries uphold 1,081/1,341 settled initially mismatching claims.
These pooled counts repeat source cases across conditions and defence seeds;
they do not add independent tasks or establish general model behavior. The
existing grading and leakage qualifications remain visible, including pending
independent adjudication and the absence of observed model exploitation.

Browser checks confirm the supplied abstract's exact rendered wording, readable
layout at 1440px and 390px, zero accordions, ten action links and three filters.
The no-JavaScript view keeps the same abstract and initial caption, both figures
and original-grade labels. Empty-cell descriptions now say that no observations
are eligible instead of announcing an undefined interval. Screenshots are in
ignored `output/playwright/abstract-editor-*.png`. Frozen data and the pinned
paper download are unchanged; the separate working paper's experimental
extensions are not admitted by this copy edit.

Website lint, Astro/TypeScript checks (36 files), research-export tests and the
final static build pass. The complete repository verification gate passes,
including all 36 Docker integration tests; log:
`.harness/verification/website-editor-abstract.log`. No report source or
experimental result was modified by this editorial pass.

## Base Nova button-triggered selects

Lucas explicitly replaced the earlier NativeSelect choice with the Base Nova
Select composition. The current three filters use Select/items, Trigger/Value
and Content/Group/Item from the official first-party registry. Two React islands
hydrate only the filter groups. The preceding zero-hydration observations
describe the earlier implementation and do not apply to these popup controls.

Browser verification exercised the actual popup options across all 20 initial
cells and 320 defence metric combinations, including interval endpoints; all
match the admitted export. ArrowDown opens the listbox, Escape dismisses it and
focus returns to the trigger. At 390px, all three triggers are buttons 44px high,
the popup fits between x=17 and x=375, and there is no page overflow. No native
select is visible in the results UI, and the page still has no accordions.
Captures are in ignored `output/playwright/base-select-*.png`.

A clean production browser successfully hydrates both islands and updates both
charts after choosing Science. It reports no console or page errors. Without
JavaScript, both default legal figures, ten model rows, all ten action links and
the supplied abstract remain readable; inactive filter triggers stay hidden.
The static chart DOM remains owned by Astro, with current choices retained on
the explorer before its change event is dispatched.

Lint, Astro/TypeScript checks, research-export tests, a frozen Bun install and
the production build pass. The full repository gate passes with 554 harness
unit tests and 36 Docker integration tests; log:
`.harness/verification/base-select-controls.log`. No research data or model
experiment was changed by this component correction.

## Header pill buttons

Lucas's supplied screenshot and the live vla.lbxa.net header were inspected.
The header artifact links now use a local shadcn `pill` variant and `compact`
size: white surfaces, thin stone-grey borders, fully rounded ends, 12px
medium-weight labels and a dark hover state. Desktop height matches the live
reference at 34px; narrow screens retain a 44px minimum touch target.

Browser checks at 1440px and 390px confirm the dimensions, all four original
anchor destinations, dark hover, visible keyboard focus and no horizontal
overflow. Final screenshots are in ignored `output/playwright/header-pills-*.png`.
The resource links and three popup selectors retain their existing variants.

Website lint, type checks, research-export tests and the production build pass.
The complete repository verification gate also passes, including all 36 Docker
integration tests; log: `.harness/verification/header-pill-buttons.log`.
The bounded entropy review found no new utility duplication or boundary drift.

## Compact select spacing

Lucas requested less padding on the select buttons. The three triggers now use
the registry's 32px height with 4px vertical and 8px horizontal padding. Field
and label gaps are tighter, and the domain trigger is 160px wide. These current
dimensions replace the earlier 44px select checks above.

Browser checks at 1440px and 390px confirm all three trigger dimensions,
successful domain/challenge/measure changes, keyboard opening and dismissal,
returned focus and no horizontal overflow. The mobile popup fits fully within
the viewport. Captures are in ignored `output/playwright/compact-select-*.png`.
Header pills and research data remain unchanged.

Website lint, type checks, research-export tests and build pass. The full
repository gate passes, including all 36 Docker integration tests; log:
`.harness/verification/compact-select-padding.log`. The bounded entropy pass
found no new utility duplication or boundary drift.

## Summary without a visible heading

Removed the visible Abstract heading at Lucas's request. The summary paragraph
remains in place, with an accessible Research summary section label. Removed
the unused heading-specific CSS. The built HTML confirms the heading is absent
and the summary remains present. Website lint, type checks and build pass; the
full repository gate passes in
`.harness/verification/remove-abstract-heading.log`. No new drift was found.

## Charts without numbered labels

Removed the numbered Confidence/Defence labels above both chart titles and
their unused CSS. Built-HTML checks retain both descriptive titles and all ten
model rows. Website lint, type checks and build pass, as does the full repository
gate in `.harness/verification/remove-numbered-section-labels.log`.
The bounded entropy review found no new drift.

## Publication readiness

Validated the staged website in an exported Git tree with a frozen Bun install,
lint, type checks, research-export tests and a static build. With no local video
exports present, asset preparation downloads the public website-assets-v1 film
and verifies its SHA-256. The restored cache and emitted MP4 match the approved
local film; a deliberately corrupted temporary cache is rejected. The paper
remains pinned to its admitted hash. Wrangler targets the existing epistemics
Worker used by the repository's Cloudflare main-branch integration.

Only website files and their decision records are included in the publication
commit. Its decision index is regenerated from that exact set of records; the
other uncommitted report and experiment work stays in the shared checkout.

## Scroll-triggered chart reveals

Added native IntersectionObserver/Web Animations reveals for the ten chart
rows. Rows lift and fade subtly; confidence intervals expand around their
centres and markers appear at their actual coordinates. No counts animate
from zero. Browser instrumentation confirms ten row reveals and 45 interval
and marker animations, with identical SVG data before and after motion and no
replay when returning to a row. Captures are in ignored
`output/playwright/chart-motion-*.png`.

Mobile checks confirm live reduced-motion changes cancel active animations,
initial reduced motion creates none, and filter changes during a reveal cancel
it immediately. The production build was checked with normal motion, reduced
motion, JavaScript disabled and animation APIs removed. Both charts and all ten
rows remain visible in each case, with no overflow, console errors or page
errors. Modern-browser filter changes and unsupported-API chart updates pass.

Website lint, type checks, research-export tests and build pass. The full
repository verification gate passes in
`.harness/verification/scroll-chart-reveals.log`. Native browser APIs keep the
enhancement local without an animation dependency. The bounded entropy review
found no new drift.

## Centred bottom resources

Centred the Work with the data heading and its six resource links. Browser
checks at 1440px and 390px confirm centred link rows, including the wrapped
mobile row, with no horizontal overflow. Captures are in ignored
`output/playwright/resources-centered-*.png`. Website lint, type checks and
build pass. The full repository gate passes in
`.harness/verification/center-bottom-resources.log`. The bounded entropy review
found no new drift.

## Matching research 404 pages

Added `src/pages/404.astro` to match the Collusion companion's simple error
page, retaining Epistemics branding and a link to this site's home page.
Astro emits `dist/404.html`; both Workers configurations already use
`not_found_handling: "404-page"`.

Production-style local Workers checks cover both sites at 1280 × 844 and
390 × 844. Nested missing URLs return the custom HTML with a 404 status,
no horizontal overflow and no client scripts. Each home link reaches the
correct research site by keyboard and with JavaScript disabled. Both pages
include `noindex`. Screenshots are in ignored `output/playwright/404-*.png`.

Epistemics lint, type checks and the production build pass. Its full repository
gate also passes, including all 36 Docker integration tests; log:
`.harness/verification/website-404.log`. Collusion's unchanged page retains its
previous passing full gate and passes the paired browser check. Local Wrangler
state is now ignored. Frozen research exports, papers and film are unchanged;
no public deployment was performed.

# November 18 paper checkpoint

The paper links resolve to `/files/confidence-correction-and-consensus.pdf`.
The built asset matches the reviewed 65-page manuscript, SHA-256
`04fe75d345d73b686af306aee2e69554fcf535b2d84854b935635005232d93af`.
The earlier Macro-Epistemics PDF still matches the hash in the public data.
Astro and TypeScript checks, four research tests and the static build pass.
