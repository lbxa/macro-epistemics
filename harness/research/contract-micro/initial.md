Review the supplied agreement and assess the supplied proposition using only
the agreement. For this initial assessment, return a JSON object with:

- `classification`: `Entailment`, `Contradiction`, or `NotMentioned`.
- `explanation`: a short explanation of the relevant wording.
- `citations`: an array of up to three short verbatim quotations from the
  agreement. An empty array is appropriate when no supporting provision exists.

Return the JSON object without a Markdown fence.
