/** Static admission adapter: reuse report grades/intervals; export public aggregates only. */
import { createHash } from "node:crypto";
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import sector from "../../report/data/sector-study.json";
import statistics from "../../report/epistemics/sector-statistics.json";
import diagnostics from "../../report/epistemics/sector-diagnostic-statistics.json";
import arithmetic from "../../report/data/arithmetic-diagnostic.json";
import leakage from "../../harness/research/sector-expansion/objection-leakage.json";

const inputPaths = [
  "report/data/sector-study.json", "report/epistemics/sector-statistics.json",
  "report/epistemics/sector-diagnostic-statistics.json", "report/data/arithmetic-diagnostic.json",
  "harness/research/sector-expansion/objection-leakage.json",
  "website/public/files/macro-epistemics-paper.pdf",
];
const root = new URL("../../", import.meta.url);
const inputHashes = Object.fromEntries(inputPaths.map((path) => [path,
  createHash("sha256").update(readFileSync(new URL(path, root))).digest("hex"),
]));
function admit(condition, message) {
  if (!condition) throw new Error(`Research export rejected: ${message}`);
}
admit(sector.provenance.artifact.endsWith(":v128"), "review a new primary artifact before exporting");
admit(sector.provenance.artifact === statistics.provenance.artifact
  && sector.provenance.artifact === diagnostics.artifact
  && sector.provenance.analysis_sha256 === statistics.provenance.analysis_sha256,
  "primary statistics use a different admitted artifact or analysis revision");
admit(inputHashes["report/data/sector-study.json"] === diagnostics.input_sha256.study
  && inputHashes["report/epistemics/sector-statistics.json"] === diagnostics.input_sha256.statistics,
  "diagnostic statistics do not match the exact primary inputs");
admit(leakage.source_sha256["cases.json"] === sector.provenance.cases_sha256,
  "validity audit uses a different task set");
admit(arithmetic.probe.manifest.parent_cases_sha256 === sector.provenance.cases_sha256,
  "arithmetic diagnostic uses a different task set");
admit(sector.initials.length === 600 && sector.cases.length === 120
  && sector.branches.length === 12000, "the admitted cohort has changed");
admit(inputHashes["website/public/files/macro-epistemics-paper.pdf"] === "9ab732be30fca65d052e027c1e50b1e07e86c0320ebd8d5e077c5c4cb56b9afc",
  "paper PDF differs from the independently verified v1 artifact");

const models = [
  { id: "@cf/deepseek-ai/deepseek-v4-pro-0813", label: "DeepSeek V4 Pro" },
  { id: "@cf/zai-org/glm-5.3", label: "GLM 5.3" },
  { id: "@cf/moonshotai/kimi-k2.6", label: "Kimi K2.6" },
  { id: "@cf/openai/gpt-oss-120b", label: "GPT-OSS-120B" },
  { id: "@cf/thinkingmachines/inkling-2-small", label: "Inkling 2 Small" },
];
const domains = [
  { id: "finance", label: "Finance", benchmarks: "FinQA · TAT-QA" },
  { id: "legal", label: "Legal", benchmarks: "ContractNLI" },
  { id: "science", label: "Science", benchmarks: "SciFact" },
  { id: "education", label: "Education", benchmarks: "MathDial" },
];
const arms = [
  { id: "review", label: "Neutral review" }, { id: "pressure", label: "Empty pressure" },
  { id: "misleading", label: "Misleading objection" }, { id: "audit", label: "Source audit" },
];
const endpoints = [
  { id: "correction", label: "Repair of initial mismatches", denominator: "valid defences of initial reference mismatches" },
  { id: "concession", label: "Loss of initial matches", denominator: "valid defences of initially reference-matching answers" },
  { id: "wrong_upheld", label: "Jury upholds initial mismatches", denominator: "settled panels judging initial reference mismatches" },
  { id: "accuracy", label: "Final reference agreement", denominator: "all valid defences" },
];
function measure(stat, count) {
  admit(stat && Number.isInteger(stat.completed), "missing report metric");
  admit(stat.completed === 0 ? stat.mean === null
    : Math.abs(count / stat.completed - stat.mean) < 1e-10, "count differs from report estimate");
  return { count, n: stat.completed, groups: stat.eligible_groups, mean: stat.mean,
    low: stat.ci_low, high: stat.ci_high };
}
const initial = models.flatMap(({ id: model }) => domains.map(({ id: domain }) => {
  const rows = sector.initials.filter((row) => row.model === model && row.domain === domain);
  const usable = rows.filter((row) => typeof row.correct === "boolean" && typeof row.confidence === "number");
  const stats = statistics.initial[model][`domain:${domain}`];
  const literalCorrect = usable.filter((row) => row.literal_correct).length;
  const auditedCorrect = usable.filter((row) => row.correct).length;
  admit(rows.length === 30 && usable.length === stats.accuracy.completed, "initial denominator differs");
  return { model, domain, assigned: rows.length, completed: usable.length, literalCorrect,
    auditedCorrect, confidence: stats.confidence.mean,
    literal: measure(stats.literal_accuracy, literalCorrect), audited: measure(stats.accuracy, auditedCorrect) };
}));

const disputes = models.flatMap(({ id: model }) => domains.flatMap(({ id: domain }) => arms.map(({ id: arm }) => {
  const rows = sector.branches.filter((row) => row.model === model && row.domain === domain && row.arm === arm);
  const valid = rows.filter((row) => row.defence_status === "complete");
  const settled = rows.filter((row) => typeof row.jury_upheld === "boolean");
  const stat = statistics.branches[model][`domain:${domain}`][arm];
  const cell = diagnostics.cells.find((row) => row.model === model && row.domain === domain && row.arm === arm);
  admit(cell && rows.length === 150 && cell.valid_defences === valid.length
    && cell.jury.settled === settled.length, "branch completion differs from report ledger");
  const metrics = Object.fromEntries(endpoints.map(({ id }) => {
    const scores = Object.fromEntries(["audited", "literal"].map((grade) => {
      const initialKey = grade === "literal" ? "literal_initial_correct" : "initial_correct";
      const finalKey = grade === "literal" ? "literal_final_correct" : "final_correct";
      const eligible = id === "wrong_upheld" ? settled : valid;
      const count = eligible.filter((row) => id === "accuracy" ? row[finalKey] === true
        : id === "correction" ? row[initialKey] === false && row[finalKey] === true
        : id === "concession" ? row[initialKey] === true && row[finalKey] === false
        : row[initialKey] === false && row.jury_upheld === true).length;
      return [grade, measure(stat[grade === "literal" ? `literal_${id}` : id], count)];
    }));
    return [id, scores];
  }));
  return { model, domain, arm, assigned: rows.length, executed: rows.filter((row) => row.initial_correct !== null).length,
    validDefences: valid.length, settled: settled.length, metrics,
    seedAccuracy: { seeds: [101, 102, 103, 104, 105], rates: stat.seed_accuracy_means,
      completed: stat.seed_completed, sd: stat.seed_accuracy_sd } };
})));

const initialCompleted = initial.reduce((sum, row) => sum + row.completed, 0);
const executed = disputes.reduce((sum, row) => sum + row.executed, 0);
const validDefences = disputes.reduce((sum, row) => sum + row.validDefences, 0);
const settledVerdicts = disputes.reduce((sum, row) => sum + row.settled, 0);
const total = (arm, endpoint) => disputes.filter((row) => row.arm === arm).reduce((sum, row) => ({
  count: sum.count + row.metrics[endpoint].audited.count, eligible: sum.eligible + row.metrics[endpoint].audited.n,
}), { count: 0, eligible: 0 });
const auditMismatchSupported = diagnostics.cells.filter((row) => row.arm === "audit").reduce((sum, row) => ({
  count: sum.count + row.mismatch_supported, eligible: sum.eligible + row.mismatch_n,
}), { count: 0, eligible: 0 });
const summary = { initialAssigned: sector.initials.length, initialCompleted, sourceGroups: sector.cases.length,
  modelCount: models.length, domainCount: domains.length, unavailable: sector.initials.length - initialCompleted,
  auditChangedGrades: initial.reduce((sum, row) => sum + row.auditedCorrect - row.literalCorrect, 0),
  branchesAssigned: sector.branches.length, executed, structurallyUnavailable: sector.branches.length - executed,
  validDefences, settledVerdicts, abortedPanels: executed - settledVerdicts,
  pressureLoss: total("pressure", "concession"), auditRepair: total("audit", "correction"), auditMismatchSupported };
admit(initialCompleted === 581 && executed === 11620 && validDefences === 11483
  && settledVerdicts === 11469, "completed primary headline denominators changed");

const authorReplies = arithmetic.probe.calls.filter((row) => row.condition === "author_checked");
const arithmeticDiagnostic = {
  sourceCases: 1, seedBlocks: arithmetic.probe.manifest.seeds.length, callsPerBlock: 3,
  expression: "1084 × 108.51", correctProduct: "117624.84", defendedProduct: "117628.84",
  conditions: [
    { id: "calculate", label: "Calculate the bare product" },
    { id: "claim_only", label: "Judge the false claim alone" },
    { id: "defended", label: "Judge it with the frozen defence" },
    { id: "checked_evidence", label: "Add a checked decomposition" },
  ],
  results: arithmetic.probe.summary.map((row) => ({ model: row.model, condition: row.condition,
    validCalls: row.valid_calls, correctCalls: row.correct_calls, blockMean: row.block_mean,
    blockSd: row.block_sd, majorityCorrect: row.majority_correct, validMajorities: row.valid_majorities,
    blocks: arithmetic.probe.blocks.filter((block) => block.model === row.model && block.condition === row.condition)
      .map(({ seed, valid, correct }) => ({ seed, valid, correct })) })),
  author: { assigned: authorReplies.length, usable: authorReplies.filter((row) => row.status === "complete").length,
    corrected: authorReplies.filter((row) => row.correct === true).length,
    withdrew: authorReplies.filter((row) => row.parsed?.original_still_supported === false).length },
};
const benchmarkValidity = { numericOriginals: leakage.numeric_originals,
  recoveredReferences: leakage.legacy_reference_matches, initialMismatches: leakage.initial_reference_mismatches,
  recoveredMismatches: leakage.legacy_new_matches_from_errors,
  futureSupportedErrors: leakage.initial_reference_mismatches - leakage.future_unsupported_errors,
  futureNewMatches: leakage.future_new_matches_from_errors, futureUnsupportedErrors: leakage.future_unsupported_errors,
  futurePolicyIntegrated: leakage.future_policy_integrated, observedModelExploitation: false };

const research = { version: 2, summary, models, domains, arms, endpoints, initial, disputes,
  arithmeticDiagnostic, benchmarkValidity,
  provenance: {
    sectorArtifact: sector.provenance.artifact, sectorDigest: "7d7230ca4d18fc07c1bb8e0009cdbc1d",
    sectorRun: "https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/da7e42f28ba54247",
    sectorAnalysis: sector.provenance.analysis_sha256, sectorMethod: statistics.method,
    diagnosticAnalysis: diagnostics.analysis_sha256, sectorCompletedAt: sector.provenance.progress.updated_at,
    arithmeticArtifact: arithmetic.probe.artifact, arithmeticDigest: arithmetic.probe.digest,
    arithmeticRun: `https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/${arithmetic.probe.manifest.wandb_run_id}`,
    validityArtifact: "lbxa-corp/apart-epistemics-sprint/sector-validity-audit-da7e42f28ba54247:v0",
    validityDigest: "698f703d0ff227544c8bb9f7d4e833ff",
    validityRun: "https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/79009dae600f475d",
    leakageAnalysis: leakage.analysis_sha256, inputHashes,
    reportArtifact: "lbxa-corp/apart-epistemics-sprint/sector-report-da7e42f28ba54247:v1",
    reportDigest: "1e687f354c1e79d4f6ab05ad157fce52",
    reportPdfSha256: inputHashes["website/public/files/macro-epistemics-paper.pdf"],
    reportRun: "https://forge.coreweave.com/wandb/lbxa-corp/apart-epistemics-sprint/runs/d6279cd7cd7b4136",
  },
};
const output = JSON.stringify(research, null, 2) + "\n";
for (const path of ["src/data/research.json", "public/data/research.json"]) {
  const destination = new URL(`../${path}`, import.meta.url);
  mkdirSync(fileURLToPath(new URL("./", destination)), { recursive: true });
  writeFileSync(destination, output);
}
console.log(`Admitted ${initial.length} initial cells, ${disputes.length} dispute cells; `
  + `${settledVerdicts}/${executed} executed primary panels settled. No raw calls exported.`);
