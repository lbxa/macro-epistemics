import { describe, expect, test } from "bun:test";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import research from "../src/data/research.json";
import statistics from "../../report/epistemics/sector-statistics.json";

describe("admitted public research data", () => {
  test("accounts for unavailable and aborted assignments without counting them as answers", () => {
    const s = research.summary;
    expect(s.branchesAssigned).toBe(s.executed + s.structurallyUnavailable);
    expect(s.executed).toBe(s.settledVerdicts + s.abortedPanels);
    expect(s.structurallyUnavailable).toBe(s.unavailable * 4 * 5);
    expect(research.disputes.reduce((sum, row) => sum + row.validDefences, 0)).toBe(s.validDefences);
    expect(s.pressureLoss).toEqual({ count: 20, eligible: 2543 });
    expect(s.auditRepair).toEqual({ count: 17, eligible: 334 });
    expect(s.auditMismatchSupported).toEqual({ count: 314, eligible: 334 });
  });

  test("uses the report's source-group intervals and keeps endpoint denominators distinct", () => {
    expect(research.disputes).toHaveLength(5 * 4 * 4);
    for (const row of research.disputes) {
      const reference = statistics.branches[row.model][`domain:${row.domain}`][row.arm];
      for (const [endpoint, grades] of Object.entries(row.metrics)) {
        for (const [grade, measure] of Object.entries(grades)) {
          const report = reference[grade === "literal" ? `literal_${endpoint}` : endpoint];
          expect([measure.mean, measure.low, measure.high, measure.groups])
            .toEqual([report.mean, report.ci_low, report.ci_high, report.eligible_groups]);
          expect(measure.count).toBeLessThanOrEqual(measure.n);
          expect(measure.groups).toBeLessThanOrEqual(30);
          if (measure.n === 0) expect(measure.mean).toBeNull();
        }
      }
      for (const grade of ["literal", "audited"]) {
        expect(row.metrics.concession[grade].n + row.metrics.correction[grade].n).toBe(row.validDefences);
        expect(row.metrics.accuracy[grade].n).toBe(row.validDefences);
        expect(row.metrics.wrong_upheld[grade].n).toBeLessThanOrEqual(row.settled);
      }
      expect(row.seedAccuracy.rates).toHaveLength(5);
      expect(row.seedAccuracy.rates).toEqual(reference.seed_accuracy_means);
      expect(row.seedAccuracy.sd).toBe(reference.seed_accuracy_sd);
    }
  });

  test("keeps the one-source diagnostic separate and retains five three-call blocks", () => {
    const diagnostic = research.arithmeticDiagnostic;
    expect(diagnostic.sourceCases).toBe(1);
    expect(diagnostic.seedBlocks).toBe(5);
    expect(diagnostic.results).toHaveLength(8);
    for (const row of diagnostic.results) {
      expect(row.blocks.map((block) => block.seed)).toEqual([101, 102, 103, 104, 105]);
      expect(row.blocks.every((block) => block.valid === 3)).toBe(true);
      expect(row.blocks.reduce((sum, block) => sum + block.correct, 0)).toBe(row.correctCalls);
      expect(row.validCalls).toBe(15);
      expect(row).not.toHaveProperty("ciLow");
    }
    expect(diagnostic.author).toEqual({ assigned: 5, usable: 4, corrected: 4, withdrew: 4 });
    expect(research.benchmarkValidity.futurePolicyIntegrated).toBe(false);
    expect(research.benchmarkValidity.observedModelExploitation).toBe(false);
  });

  test("publishes only aggregate data and reproducible provenance", () => {
    const publicBytes = readFileSync(new URL("../public/data/research.json", import.meta.url));
    expect(publicBytes.equals(readFileSync(new URL("../src/data/research.json", import.meta.url)))).toBe(true);
    const forbidden = new Set(["parsed", "explanation", "spending", "calls", "records", "messages", "Authorization"]);
    const inspect = (value) => {
      if (!value || typeof value !== "object") return;
      for (const [key, child] of Object.entries(value)) {
        expect(forbidden.has(key)).toBe(false);
        inspect(child);
      }
    };
    inspect(research);
    for (const [path, digest] of Object.entries(research.provenance.inputHashes)) {
      const bytes = readFileSync(new URL(`../../${path}`, import.meta.url));
      expect(createHash("sha256").update(bytes).digest("hex")).toBe(digest);
    }
  });
});
