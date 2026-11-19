# Macro-Epistemics research landing page

This is the self-contained Bun / Astro 6 site for **Macro-Epistemics: Confidence
Under Dispute**. It preserves the supplied archive header, including the thick
rule above the title and the thinner rule below it. The page is a short research
companion centered on the primary study. A short abstract and cohort counts lead
directly to two visible charts: initial confidence versus reference agreement,
and outcomes after a challenge. All five models remain visible together. One
domain selector updates both charts; challenge and outcome controls belong to
the second chart. The page has no demo, accordions or supplementary drill-downs.

## Local draft

From this directory:

Use Bun 1.3.14 and Node 22.12 or newer, matching the installed Astro 6 runtime.

```sh
bun install --frozen-lockfile
bun run prepare:assets
bun run dev
```

`prepare:assets` verifies the committed working paper and the archived PDF
pinned by the public evidence export. The working paper is the PDF served by
the website. Refresh it by copying a reviewed build and updating its hash.

`bun run build` prepares these assets before building. Cloudflare Workers Builds
publishes main to the existing `epistemics` Worker at `epistemics.lbxa.net`.
Wrangler's name matches that target.
The empty `previews` block enables Cloudflare's configured branch-preview
command, `npx wrangler preview`; static assets stay at the top level.
The custom `src/pages/404.astro` builds to `dist/404.html`, which Workers serves
with a 404 status for missing paths, including nested URLs. It matches the
Collusion companion's error page, with this project's own title and home link.

```sh
bunx astro sync
bun run typecheck
bun run test:research
bun run build
```

After admitting a new frozen result snapshot in the report, run
`bun run sync:research` to regenerate the public aggregates. The exporter rejects
unexpected cohort changes rather than silently mixing new or partial runs.

The parent repository's Rust verification gate does not check this site.
Inspect the rendered page at both narrow and desktop widths after changes.

## Content and rendering boundaries

- `src/pages/index.astro` owns the narrative, artifact links and archive header.
- `src/components/FindingsExplorer.astro` and `src/data/research.json` own the
  completed sector study's initial and dispute charts and uncertainty. The
  compact controls initialize immediately; no disclosure gates the data.
- Paper, code and data notes are direct resource links.
- `public/data/research.json` provides the same aggregates and provenance for
  download. It contains no credentials, raw model calls or recovery state.

Astro's native Vite pipeline runs Tailwind 4. The existing Tailwind configuration
is loaded through `@config` to retain the template's utilities. Official shadcn
components provide Button, FieldGroup, Field, FieldLabel and Separator. The
three filters use the exact Base Nova Select requested by Lucas: SelectTrigger,
SelectValue, SelectContent, SelectGroup and SelectItem, with `items` on the root.
Two small React islands hydrate the filter groups for popup, focus and keyboard
behavior. The charts, abstract and action links stay server-rendered. Without
JavaScript, both default legal charts remain visible and inactive controls stay
hidden. The archive header remains text, so the initial
render does not wait for an image or custom font.

Chart rows reveal once as they enter the viewport, using IntersectionObserver
and the native Web Animations API. Intervals expand around their centres and
markers fade into their final positions; numeric labels and SVG coordinates
always retain the actual data. Filter changes cancel any active reveal. Reduced
motion skips animation and cancels motion already playing. No-JavaScript and
unsupported-browser views retain fully visible static charts.

`components.json` records the official `@shadcn` registry, Radix/Nova style and
`@/` aliases. `src/styles/global.css` maps the research site's green/cream palette
onto semantic shadcn tokens. The explicit `@shadcn-base` registry pins the
Base Nova Select; use `bunx --bun shadcn@latest add @shadcn-base/select --dry-run`
when reviewing upstream changes. Other components retain their existing base.
`ResearchControls.tsx` owns interactive popup state. It publishes selection
values onto the Astro explorer's data attributes before dispatching
`research-filter-change`; this preserves early selections while the chart
script loads. The chart script owns data display and never mutates React's
controls. `ResearchLinks.tsx` remains server-only. Select triggers use the
compact 32px registry height with 4px vertical and 8px horizontal padding;
the header separators
retain their 4px/2px dimensions. The React renderer is pinned to 5.0.7 to match
Astro 6.2.1's Vite 7 dependency. Retain local component variants when updating
from the registry; inspect CLI diffs before replacing them.

Keep original and source-audited grades visible together. The audit is post hoc
and pending independent human review. Unavailable outputs stay in completion
denominators. Five repeated defence seeds do not create five source cases.
The completed primary matrix is pinned to `sector-study-da7e42f28ba54247:v128`:
12,000 assignments, 11,620 executed branches, 11,483 valid defences and 11,469
settled verdicts. The arithmetic follow-up is a separate one-source diagnostic,
not additional game settlements. The original legal pilot is no longer the
headline cohort. Future updates must pin an admitted artifact and regenerate
the displayed data before changing claims. Claims about internal beliefs,
general honesty, representative industry performance or improved human decisions
are not supported by these snapshots.

Disclose the frozen numerical objection encoding flaw alongside the findings.
Its 287 recovered references come from a scripted offline audit, not observed
model exploitation. The plotted primary cohort retains the original generator.
The current paper includes a separately collected numerical rerun with the
repaired policy. The public data export retains its original archive PDF pin.

Run `bun scripts/sync-research.mjs` to regenerate the aggregate data from the
paper's admitted snapshots. It validates hashes, artifact identity, assigned
and completed counts, grading sensitivity and diagnostic denominators before
writing identical `src/data/research.json` and `public/data/research.json`.

## Changelog

### 2026-11-19

- Serve the current working paper and keep the byte-pinned prior PDF under
  `report/data/` for evidence verification. See the
  [publication asset decision](../docs/decisions/publish-current-research-assets.md).

### 2026-11-18

- Link the working paper at `/files/confidence-correction-and-consensus.pdf`.

### Earlier updates

- 2026-11-17: Added the matching static 404 page for both research companions.
  Epistemics retains its own identity and returns visitors to its own home
  page; the existing Workers 404 routing needs no additional server code.
- 2026-11-17: Added the explicit previews block required by Wrangler 4.163's
  branch-preview command after the production-style build succeeded in Cloudflare.
- 2026-11-17: Aligned Wrangler with the production epistemics Worker.
- 2026-11-17: Renamed the header credit to AI Safety Research · Epistemics.
- 2026-11-17: Removed Research draft from the header date line, retaining
  November 2026.
- 2026-11-17: Added lightweight scroll-triggered chart reveals with interval
  drawing, marker fades, reduced-motion support and static fallbacks.
- 2026-11-17: Centred the bottom resource heading and links, including wrapped
  link rows on mobile.
- 2026-11-17: Removed the numbered Confidence/Defence labels above the chart
  titles, leaving the descriptive titles and data visible.
- 2026-11-17: Removed the visible Abstract heading while retaining the summary
  text and an accessible Research summary section label.
- 2026-11-17: Reduced select triggers from 44px to 32px, tightened their padding
  and label spacing, and narrowed the domain selector from 192px to 160px.
- 2026-11-17: Matched the header artifact links to the white, stone-bordered
  pill buttons on vla.lbxa.net. Kept shadcn variants, keyboard focus and
  server-rendered links, with 44px minimum touch targets on narrow screens.
- 2026-11-16: Replaced native selectors with the exact button-triggered Base Nova
  Select composition. Hydrated only the two filter groups and retained static
  charts, the supplied abstract and the no-JavaScript reading path.
- 2026-11-16: Added Lucas's supplied summary abstract verbatim and edited chart
  captions, grading labels, uncertainty notes and eligibility explanations.
  Kept reference agreement separate from response validity and jury acceptance.
- 2026-11-16: Converted active buttons, filters, field labels and separators to
  official shadcn components. Adopted the Tailwind 4 Vite plugin required by the
  current registry while retaining static charts, system fonts and no hydration.
- 2026-11-16: Replaced the Astro favicon with a solid dark-green rounded square.
  Versioned its link so browsers request the replacement.
- 2026-11-16: Put the primary charts and counts immediately after the abstract.
  Removed the demo, all accordions and their supplementary contents. Show all
  five models together, with one shared domain selector and local challenge
  controls. Retained full aggregate downloads and direct artifact links.
- 2026-11-16: Replaced the initial-only/pilot headlines with the completed v128
  study, separate arithmetic follow-up and benchmark-validity disclosure.
  Refreshed the PDF from verified report v1 and retained the compact layout.
- 2026-11-16: Shortened the default reading path to three findings and compact
  resource links. Moved the full explorer behind one disclosure, removed the
  table of contents and repeated methods/scope/vision sections, and retained
  the archive header and demo behavior.
- 2026-11-16: Added a browser-only Veracity teaching round below the abstract,
  plus links to the underlying game and original framework paper. Keep this
  scripted illustration separate from the measured research findings; see
  [the demo decision](../docs/decisions/landing-page-demo-is-a-browser-only-teaching-round.md).
- 2026-11-16: Adapted the archive template to Macro-Epistemics; added a concise
  evidence narrative, native responsive film poster, click-to-load player,
  prompt disclosures, resources and a versioned draft citation. Retained the
  unrelated template PDF privately in ignored `latex-export/`, outside public
  output. Replaced the older Tailwind integration with native PostCSS while
  preserving its Tailwind 3 utilities and header design.
