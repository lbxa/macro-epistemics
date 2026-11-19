import { describe, expect, test } from "bun:test";
import { DEMO_REFERENCE, INITIAL_DEMO_STATE, demoResponse, demoResult, transitionDemo } from "./veracity-demo.ts";

function resultFor(original, response, votes) {
  let state = transitionDemo(INITIAL_DEMO_STATE, { type: "freeze", original });
  state = transitionDemo(state, { type: "respond", objection: "source", response });
  for (const juror of [0, 1, 2]) {
    state = transitionDemo(state, { type: "vote", juror, vote: votes[juror] });
  }
  return transitionDemo(state, { type: "reveal" });
}

describe("scripted Veracity teaching round", () => {
  test("a revised or retracted answer never replaces the frozen original", () => {
    for (const response of ["revise", "retract"]) {
      const state = resultFor("mistaken", response, ["uphold", "uphold", "uphold"]);
      expect(state.stage).toBe("result");
      if (state.stage !== "result") throw new Error("Round did not complete");
      expect(state.original).toBe("mistaken");
      expect(demoResult(state).referenceMatches).toBe(false);
      expect(demoResponse(state.original, response)).toContain(response === "revise" ? "3.80%" : "3.95%");
    }
  });

  test("a unanimous jury can uphold a wrong original or reject a correct original", () => {
    const wrong = resultFor("mistaken", "revise", ["uphold", "uphold", "uphold"]);
    const correct = resultFor("correct", "defend", ["reject", "reject", "reject"]);
    if (wrong.stage !== "result" || correct.stage !== "result") throw new Error("Round did not complete");
    expect(demoResult(wrong)).toEqual({ uphold: 3, reject: 0, verdict: "upheld", referenceMatches: false });
    expect(demoResult(correct)).toEqual({ uphold: 0, reject: 3, verdict: "rejected", referenceMatches: true });
    expect(DEMO_REFERENCE.percent).toBe("3.80");
  });

  test("all eight ballot combinations use a two-of-three majority", () => {
    for (let mask = 0; mask < 8; mask += 1) {
      const votes = [0, 1, 2].map((bit) => mask & (1 << bit) ? "uphold" : "reject");
      const state = resultFor("correct", "defend", votes);
      if (state.stage !== "result") throw new Error("Round did not complete");
      const expected = votes.filter((vote) => vote === "uphold").length;
      expect(demoResult(state).verdict).toBe(expected >= 2 ? "upheld" : "rejected");
      expect(demoResult(state).referenceMatches).toBe(true);
    }
  });

  test("illegal transitions and missing ballots cannot advance a round", () => {
    expect(transitionDemo(INITIAL_DEMO_STATE, { type: "reveal" })).toBe(INITIAL_DEMO_STATE);
    const saved = transitionDemo(INITIAL_DEMO_STATE, { type: "freeze", original: "mistaken" });
    expect(transitionDemo(saved, { type: "freeze", original: "correct" })).toBe(saved);
    const jury = transitionDemo(saved, { type: "respond", objection: "review", response: "defend" });
    expect(transitionDemo(jury, { type: "reveal" })).toBe(jury);
    const voted = transitionDemo(jury, { type: "vote", juror: 0, vote: "uphold" });
    expect(jury.stage === "jury" && jury.votes[0]).toBe(null);
    expect(transitionDemo(voted, { type: "reset" })).toEqual({ stage: "draft" });
  });
});
