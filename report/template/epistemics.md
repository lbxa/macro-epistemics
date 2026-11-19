# Apart Epistemics Sprint template provenance

Lucas supplied **Copy of Apart Research hackathon submission template.pdf** on
2026-11-14 and requested its formatting combined with the recommended section
structure in the chat. The unchanged [source PDF](apart-epistemics-template.pdf)
is retained here so another checkout can inspect it.

- Source attachment SHA-256:
  `dfd6265035b6e9e15c11b0ddccd986ee935359263ed4e2eca15e8623296af267`.
- Four pages, US Letter (612 × 792 pt), Google Docs PDF renderer.
- The [current sprint guidelines](https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15)
  link [this official template](https://docs.google.com/document/d/17b3JWki-ZkaqdmqGI5d0gof-HwlGuWU9Mc1_klNZXKs/edit).
  Both were checked on 2026-11-14. The native template was last modified
  2026-11-03. Its independently exported PDF has the same content and visible
  layout as the supplied copy, with a different document title and file hash.

## Structure and visual adaptation

The active LaTeX draft uses the user's headings **Introduction, Related Work,
Methodology, Results, Discussion, References**, plus the required **Limitations
and Dual-Use / Ethical Considerations** appendix. It retains the PDF's title
and author/affiliation block, abstract, Conclusion, Code and Data, optional
Author Contributions, and LLM Usage Statement. The user's names Methodology
and Discussion replace the PDF's Methods and Discussion and Limitations.

Visual inspection of the supplied PDF and extraction of its text coordinates
and the native template's explicit styles established these conventions:

- Single column on US Letter with one-inch text margins.
- Old Standard TT body type at 11 pt, approximately 15.7 pt body line spacing.
- Centered 20 pt bold title between a 3 pt top rule and a thinner bottom rule.
- Centered author/affiliation area and “With Apart Research” line.
- Centered 14 pt abstract heading and narrower abstract text block.
- Left-aligned 14 pt bold numbered main headings; 13 pt bold subheadings.
- No inherited Veracity running header, fixed October date, or arXiv styling.

`report/epistemics/preamble.tex` owns the adaptation. The author roster is not
known, so the draft has an explicit placeholder rather than six invented
authors. Italic draft placeholders replace the template's guidance and must be
removed before submission. The yellow instructions box is template guidance,
not manuscript content. No research contribution or result is copied from it.

### User-requested font override — 2026-11-14

Lucas requested LaTeX's native research font instead of the PDF's Old Standard
TT. The active manuscript therefore uses default **Computer Modern** for text
and mathematics. Preserve this explicit override when editing the report;
the section structure, page geometry, title rules, and heading sizes remain
adapted from Apart's template.

This is a LaTeX adaptation, not a claim of pixel-identical Google Docs
pagination. Review the final populated report against the source template and
the live venue requirements before calling it submission-ready.
