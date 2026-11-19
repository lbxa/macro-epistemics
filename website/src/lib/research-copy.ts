// Keep the static figures and their interactive captions editorially consistent.
export const initialChartCopy = {
  title: "Does confidence match reference accuracy?",
  subtitle: "Before the challenge · mean stated confidence and reference agreement",
  caption:
    "Accuracy is the share of usable initial answers matching the reference. " +
    "Confidence is the mean stated probability of being correct, recorded before the challenge. " +
    "Lines show 95% source-group bootstrap intervals for accuracy.",
} as const;

export const juryTargetCaption =
  "Jurors vote on the saved initial claim; the defence’s reference agreement is checked separately.";
