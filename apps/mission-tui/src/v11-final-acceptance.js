#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { REPO_ROOT } from "./paths.js";

const OUT_DIR = path.join(REPO_ROOT, "docs/design/V11.x/evidence/v11-9-final-acceptance");

const STAGE_ACCEPTANCE_FILES = [
  ["V11-0", "docs/design/V11.x/evidence/v11-0-architecture-contract/architecture-contract-acceptance.json"],
  ["V11-1", "docs/design/V11.x/evidence/v11-1-real-time-event-stream/acceptance-data.json"],
  ["V11-2", "docs/design/V11.x/evidence/v11-2-command-ux/acceptance-data.json"],
  ["V11-3", "docs/design/V11.x/evidence/v11-3-workflow-timeline/acceptance-data.json"],
  ["V11-4", "docs/design/V11.x/evidence/v11-4-station-agent-inspector/acceptance-data.json"],
  ["V11-5", "docs/design/V11.x/evidence/v11-5-tool-permission-blocks/acceptance-data.json"],
  ["V11-6", "docs/design/V11.x/evidence/v11-6-output-quality-evidence-preview/acceptance-data.json"],
  ["V11-7", "docs/design/V11.x/evidence/v11-7-live-session-html-explainer/acceptance-data.json"],
  ["V11-8", "docs/design/V11.x/evidence/v11-8-user-scenarios/acceptance-data.json"]
];

const FORBIDDEN_POSITIVE_CLAIMS = [
  /production ready/i,
  /full production GA/i,
  /Agent executor ready/i,
  /complete Workflow Studio ready/i,
  /full multi-Agent orchestration ready/i,
  /autonomous workflow editing ready/i,
  /Codex\/Claude Code parity complete/i,
  /生产可用/,
  /完整工作流工作台已完成/,
  /Agent 执行器已完成/
];

export function generateV119Acceptance() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const stageResults = STAGE_ACCEPTANCE_FILES.map(([stageId, relPath]) => readStage(stageId, relPath));
  const missingStages = stageResults.filter((result) => result.missing).map((result) => result.stage_id);
  const failedStages = stageResults.filter((result) => result.status !== "PASS").map((result) => result.stage_id);
  const scenarioData = readJson("docs/design/V11.x/evidence/v11-8-user-scenarios/acceptance-data.json");
  const scenarioPass = scenarioData?.status === "PASS" && scenarioData?.scenario_count >= 6 && scenarioData?.planning_docs_as_runtime_evidence === false;
  const providerBacked = readJson("docs/design/V11.x/evidence/v11-1-real-time-event-stream/acceptance-data.json")?.provider_backed === true;
  const htmlSupporting = readJson("docs/design/V11.x/evidence/v11-7-live-session-html-explainer/acceptance-data.json")?.html_replaces_runtime_evidence === false;
  const drawio = validateDrawio();
  const claimScan = scanEvidenceClaims();
  const redactionPass = stageResults.every((result) => result.redaction_scan !== "FAIL");
  const status = (
    missingStages.length === 0 &&
    failedStages.length === 0 &&
    scenarioPass &&
    providerBacked &&
    htmlSupporting &&
    drawio.status === "PASS" &&
    claimScan.status === "PASS" &&
    redactionPass
  ) ? "PASS" : "FAIL";

  const data = {
    stage_id: "V11-9",
    status,
    allowed_claim: "V11 complete: real-time explainable Mission TUI interaction baseline ready for review.",
    stage_count: stageResults.length,
    missing_stages: missingStages,
    failed_stages: failedStages,
    provider_backed_cli_turn_evidence: providerBacked,
    user_scenario_matrix_pass: scenarioPass,
    html_supporting_only: htmlSupporting,
    no_false_green_scan: claimScan.status,
    no_false_green_hits: claimScan.hits,
    redaction_scan: redactionPass ? "PASS" : "FAIL",
    drawio_xml: drawio.status,
    drawio_error: drawio.error,
    forbidden_interpretations: {
      production_ready: false,
      agent_executor_ready: false,
      complete_workflow_studio_ready: false,
      codex_claude_code_parity_complete: false
    },
    evidence_refs: [
      "docs/design/V11.x/evidence/v11-9-final-acceptance/final-acceptance-data.json",
      "docs/design/V11.x/evidence/v11-9-final-acceptance/stage-results.json"
    ],
    stage_results: stageResults
  };

  fs.writeFileSync(path.join(OUT_DIR, "final-acceptance-data.json"), `${JSON.stringify(data, null, 2)}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "stage-results.json"), `${JSON.stringify(stageResults, null, 2)}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "final-summary.md"), renderSummary(data), "utf8");
  return data;
}

function readStage(stageId, relPath) {
  const data = readJson(relPath);
  return {
    stage_id: stageId,
    path: relPath,
    missing: data === null,
    status: data?.status || "MISSING",
    allowed_claim: data?.allowed_claim || null,
    evidence_scope: data?.evidence_scope || null,
    runtime_backed: data?.runtime_backed ?? null,
    redaction_scan: data?.redaction_scan || "UNKNOWN",
    claim_scan: data?.claim_scan || "UNKNOWN"
  };
}

function readJson(relPath) {
  const absPath = path.join(REPO_ROOT, relPath);
  if (!fs.existsSync(absPath)) return null;
  return JSON.parse(fs.readFileSync(absPath, "utf8"));
}

function validateDrawio() {
  try {
    execFileSync("xmllint", ["--noout", "docs/design/V11.x/v11_current_gap_analysis.drawio"], {
      cwd: REPO_ROOT,
      stdio: "pipe"
    });
    return { status: "PASS", error: null };
  } catch (error) {
    return { status: "FAIL", error: error.message };
  }
}

function scanEvidenceClaims() {
  const evidenceDir = path.join(REPO_ROOT, "docs/design/V11.x/evidence");
  const files = listFiles(evidenceDir).filter((file) => /\.(json|txt|md|html)$/i.test(file));
  const hits = [];
  for (const file of files) {
    const content = fs.readFileSync(file, "utf8");
    for (const pattern of FORBIDDEN_POSITIVE_CLAIMS) {
      if (pattern.test(content)) {
        hits.push({ file: path.relative(REPO_ROOT, file), pattern: String(pattern) });
      }
    }
  }
  return { status: hits.length === 0 ? "PASS" : "FAIL", hits };
}

function listFiles(dir) {
  if (!fs.existsSync(dir)) return [];
  const result = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) result.push(...listFiles(fullPath));
    else result.push(fullPath);
  }
  return result;
}

function renderSummary(data) {
  const lines = [
    "# V11 Final Acceptance Summary",
    "",
    `Status: ${data.status}`,
    "",
    `Allowed claim: ${data.allowed_claim}`,
    "",
    "| Check | Result |",
    "| --- | --- |",
    `| Stage evidence count | ${data.stage_count} |`,
    `| Missing stages | ${data.missing_stages.join(", ") || "none"} |`,
    `| Failed stages | ${data.failed_stages.join(", ") || "none"} |`,
    `| Provider-backed CLI turn | ${data.provider_backed_cli_turn_evidence} |`,
    `| User scenario matrix | ${data.user_scenario_matrix_pass} |`,
    `| HTML supporting only | ${data.html_supporting_only} |`,
    `| No False Green | ${data.no_false_green_scan} |`,
    `| Redaction | ${data.redaction_scan} |`,
    `| Drawio XML | ${data.drawio_xml} |`,
    "",
    "V11 final acceptance does not claim production readiness, Agent executor readiness, complete Workflow Studio readiness, or Codex/Claude Code parity."
  ];
  return `${lines.join("\n")}\n`;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const data = generateV119Acceptance();
  console.log(JSON.stringify(data, null, 2));
  process.exitCode = data.status === "PASS" ? 0 : 1;
}
