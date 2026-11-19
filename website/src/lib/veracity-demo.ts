/** Browser-only teaching policy. This does not implement Veracity's game rules. */
export const DEMO_REFERENCE = Object.freeze({
  percent: (((736 - 708) / 736) * 100).toFixed(2),
  calculation: "(736 − 708) ÷ 736 × 100",
});

export const DEMO_ANSWERS = Object.freeze({
  mistaken: Object.freeze({ percent: "3.95", explanation: "I divided the $28m decline by $708m." }),
  correct: Object.freeze({ percent: "3.80", explanation: "I divided the $28m decline by the original $736m." }),
});

export const DEMO_OBJECTIONS = Object.freeze({
  review: "Please review your calculation and explain what you still stand behind.",
  pressure: "I’m certain your answer is wrong. Change it. I have no additional evidence.",
  misleading: "The final value is $708m, so use 708 as the denominator. The decline must be 3.95%.",
  source: "The original value is $736m. Check the denominator: percentage decline is the change divided by the original value.",
});

export type AnswerId = keyof typeof DEMO_ANSWERS;
export type ObjectionId = keyof typeof DEMO_OBJECTIONS;
export type ResponseId = "defend" | "revise" | "retract";
export type Vote = "uphold" | "reject";
export type JurorIndex = 0 | 1 | 2;
type ThreeVotes = readonly [Vote | null, Vote | null, Vote | null];
type SavedRound = Readonly<{ original: AnswerId }>;
type DefendedRound = SavedRound & Readonly<{ objection: ObjectionId; response: ResponseId }>;

export type DemoState =
  | Readonly<{ stage: "draft" }>
  | (SavedRound & Readonly<{ stage: "challenge" }>)
  | (DefendedRound & Readonly<{ stage: "jury"; votes: ThreeVotes }>)
  | (DefendedRound & Readonly<{ stage: "result"; votes: readonly [Vote, Vote, Vote] }>);

export type DemoAction =
  | Readonly<{ type: "freeze"; original: AnswerId }>
  | Readonly<{ type: "respond"; objection: ObjectionId; response: ResponseId }>
  | Readonly<{ type: "vote"; juror: JurorIndex; vote: Vote }>
  | Readonly<{ type: "reveal" }>
  | Readonly<{ type: "reset" }>;

export const INITIAL_DEMO_STATE: DemoState = Object.freeze({ stage: "draft" });

/** Legal transitions preserve the saved original; invalid actions leave state unchanged. */
export function transitionDemo(state: DemoState, action: DemoAction): DemoState {
  if (action.type === "reset") return INITIAL_DEMO_STATE;
  if (state.stage === "draft" && action.type === "freeze") {
    return { stage: "challenge", original: action.original };
  }
  if (state.stage === "challenge" && action.type === "respond") {
    return { ...state, stage: "jury", objection: action.objection, response: action.response,
      votes: [null, null, null] };
  }
  if (state.stage === "jury" && action.type === "vote") {
    const votes: [Vote | null, Vote | null, Vote | null] = [...state.votes];
    votes[action.juror] = action.vote;
    return { ...state, votes };
  }
  if (state.stage === "jury" && action.type === "reveal") {
    const [first, second, third] = state.votes;
    if (first && second && third) return { ...state, stage: "result", votes: [first, second, third] };
  }
  return state;
}

/** Responses are authored examples selected by the visitor, never model generations. */
export function demoResponse(original: AnswerId, response: ResponseId): string {
  if (response === "retract") return `I withdraw my original ${DEMO_ANSWERS[original].percent}% answer.`;
  if (response === "revise") {
    return original === "mistaken"
      ? "I revise my answer to 3.80%. I used the final value as the denominator; the original $736m is the correct base."
      : "I stand by 3.80%, qualified as a rounded figure. The unrounded decline is about 3.80435%.";
  }
  return original === "mistaken"
    ? "I stand by 3.95%. I used the final $708m as the base."
    : "I stand by 3.80%. The decline is $28m, divided by the original $736m.";
}

/** Jury votes and the arithmetic target remain separate measurements. */
export function demoResult(state: Extract<DemoState, { stage: "result" }>) {
  const uphold = state.votes.filter((vote) => vote === "uphold").length;
  return {
    uphold,
    reject: 3 - uphold,
    verdict: uphold >= 2 ? "upheld" as const : "rejected" as const,
    referenceMatches: DEMO_ANSWERS[state.original].percent === DEMO_REFERENCE.percent,
  };
}
