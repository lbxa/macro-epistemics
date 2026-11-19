# Research reporting guide

Use these standards when planning, writing, illustrating, or reviewing the
project's LaTeX research report. They encode recurring decisions and observable
checks; routine LaTeX syntax remains reference material.

The active project is Macro-Epistemics. Its peer-review working revision
contains the five-model study and separately admitted numerical extensions;
the brief records the supported claims and remaining scientific gaps.
Use the `editor` skill while developing the report alongside cloud experiments.
The venue record describes the proposed publication route.

## Table of contents

| Read | File | Use it for |
| --- | --- | --- |
| 1 | [Paper brief](paper-brief.md) | Reader, question, contribution, admissible evidence, and gaps |
| 2 | [Venue](venue.md) | Official template, limits, anonymity, and submission stage |
| 3 | [Writing](writing.md) | Clear prose, mathematical arguments, and annotated examples |
| 4 | [Visuals](visuals.md) | Publication chart style, Matplotlib mean/SD figures, typography, palettes, tables, and diagrams |
| 5 | [LaTeX](latex.md) | Compiler, packages, notation, equations, and references |
| 6 | [Review](review.md) | Scientific support, reproducibility, PDF inspection, and completion |
| Active report | [Macro-Epistemics working revision](../../report/epistemics/README.md) | Primary study, targeted replications, uncertainty, and build commands |
| Report | [Historical baseline report](../../report/README.md#earlier-baseline-report) | Two-episode smoke evidence in `report/main.tex`; build separately with `make -C report baseline` |
| Report | [Historical seeded recruitment report](../../report/agentic/README.md) | Imported November manuscript, completed C1 results, source-pinned cloud registry, controls and review gaps; October case studies retained separately |
| Archive | [Historical venues](historical-venues.md) | Original sprint rules and template provenance for imported manuscripts |
| Lookup | [Writing sources](sources/writing-sources.md) | Knuth; Peyton Jones; Gopen and Swan; Williams and Bizup; Pinker; The Craft of Research |
| Lookup | [Visual sources](sources/visual-sources.md) | Rougier; Booktabs; PGF/TikZ |
| Lookup | [LaTeX sources](sources/latex-sources.md) | AMS guide; The LaTeX Companion; official venue sources |
| Reuse | [LaTeX example](templates/report-example.tex) | A minimal illustrative argument, equation, table, figure, and diagram |
| Reuse | [Research revision workflow](research-maturation.md) | Strengthen exploratory studies through experimental breadth, evaluator audits, seeded replication and iterative rewriting |
| Reuse | [Plot style](templates/figure.mplstyle) and [plot script](templates/figure-example.py) | Regenerable vector figure at an explicit publication width |

## Authority and provenance

The selected venue's official rules govern submission formatting. The project
brief governs which scientific claims the evidence supports. Neither formatting
rules nor stylistic preferences justify overstating a result. House defaults
apply where the venue and project have not specified a choice.

The source notes record primary material inspected on **2026-10-25**, including
versions or section locators and access limits. The standards are concise
paraphrases and project-specific applications, not copies of the books. A
publisher overview or sample is not evidence that the full paid book was read.
The original examples here demonstrate writing and formatting, not project
findings. Do not cite a writing guide as scientific support for a research claim.

Keep source notes stable during ordinary drafting. Revisit the primary source
when changing a rule, encountering an exception, or selecting a venue. Record
the new access date and locator with any revision. Recheck submission rules
for the selected year, track, and stage immediately before submission.

## First use

Fill the brief's open decisions before presenting a manuscript as a supported
research result. Start a submission from its official template; the article
example below is a practice artifact. Read or watch Peyton Jones for the paper's
central story, read the AMS guide for mathematical typesetting, and practice
reproducing an excellent paper's figure and results table with attribution to
the original. Use Rougier and Booktabs to explain the reproduction choices.

Test the house conventions on a representative passage with one quantitative
claim, figure, and table. The included example supplies **fictional counts** for
that purpose. Replace them with audited project evidence only when writing the
real report. Keep rules that prevent meaningful failures or capture preferences;
adjust rules that add work without improving comprehension or correctness.

## Preview the reusable example

From the repository root, with Python/Matplotlib, `latexmk`, pdfLaTeX, and the
standard AMS, Booktabs, graphics, Hyperref, and TikZ packages installed:

```sh
report_repo="$(pwd)"
report_preview="$(mktemp -d /tmp/veracity-report-preview.XXXXXX)"
python docs/reporting/templates/figure-example.py --output-dir "$report_preview"
(
  cd "$report_preview"
  latexmk -pdf -interaction=nonstopmode -halt-on-error "$report_repo/docs/reporting/templates/report-example.tex"
)
```

Open `report-example.pdf` in the printed preview directory, inspect the figure
at its actual size, and apply [the review checklist](review.md). Generated PDFs
and LaTeX build products belong in scratch/run output, not in this guide's
source directory. The example is a smoke check of the conventions; it does not
complete review of a future manuscript.

## Changelog

### 2026-11-17

- Prefer the shortest complete argument: remove repeated summaries while
  keeping evidence and qualifications. See the
  [concision decision](../decisions/report-concision-preserves-evidence.md).
- Capture the full experimental and editorial revision process in
  [research-maturation.md](research-maturation.md), so earlier projects can
  repeat it with their own claims and evidence. Preserve the distinction
  between working infrastructure, completed experiments, scientific support
  and submission readiness.

### 2026-10-25

- Capture the baseline chart conventions as reusable report guidance: restrained
  Matplotlib styling, manuscript-matched type, opaque same-hue SD fills, raw
  observations, and explicit small-sample/N/A rules. Link them from writing and
  review guidance so future reports preserve both visual quality and evidence.
- Keep detailed chart rules in [visuals.md](visuals.md), with writing and review
  guidance linking to that source. The current Times-based report uses STIX type
  and opaque blue mean/SD colors `#0072B2` / `#DCECF5`; preserve that visual
  convention when extending its figures.
