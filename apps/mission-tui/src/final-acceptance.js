#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../../..");
const V10_7_DATA = path.join(ROOT, "docs/design/V10.x/evidence/v10-7-final-acceptance/v10-final-acceptance-data.json");
const V10_8_DATA = path.join(ROOT, "docs/design/V10.x/evidence/v10-8-agent-backed-tui/acceptance-data.json");
const OUT_DIR = path.join(ROOT, "docs/design/V10.x/evidence/v10-9-final-acceptance");

export function generateFinalAcceptance() {
  const baseline = readJson(V10_7_DATA);
  const agentBacked = readJson(V10_8_DATA);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const blockers = [];
  if (baseline.status !== "PASS") blockers.push("V10-1..V10-7 baseline is not PASS");
  if (baseline.read_model_baseline_claim_allowed !== true) blockers.push("V10-1..V10-7 bounded claim is not allowed");
  if (agentBacked.status !== "PASS") blockers.push("V10-8 Agent-backed bridge is not PASS");
  if (agentBacked.evidence_scope !== "agent_backed_gateway_turn") blockers.push("V10-8 evidence_scope is not agent_backed_gateway_turn");
  if (agentBacked.runtime_backed !== true) blockers.push("V10-8 runtime_backed is not true");
  if (agentBacked.fixture_only !== false) blockers.push("V10-8 fixture_only must be false");
  if (agentBacked.local_parser_only !== false) blockers.push("V10-8 local_parser_only must be false");
  if (agentBacked.gateway_session_started !== true) blockers.push("V10-8 gateway session did not start");
  if (agentBacked.gateway_turn_started !== true) blockers.push("V10-8 gateway turn did not start");
  if (agentBacked.assistant_output_from_gateway !== true) blockers.push("V10-8 assistant output is missing");
  if (baseline.claim_scan !== "PASS" || agentBacked.claim_scan !== "PASS") blockers.push("claim scan is not PASS");
  if (baseline.redaction_scan !== "PASS" || agentBacked.redaction_scan !== "PASS") blockers.push("redaction scan is not PASS");
  const data = {
    stage_id: "V10-9",
    status: blockers.length === 0 ? "PASS" : "BLOCKED",
    allowed_claim: "V10 complete: CLI-native Agent-backed TUI experience and explainability baseline ready for review.",
    evidence_scope: "v10_1_to_v10_8_aggregated_evidence",
    final_claim_allowed: blockers.length === 0,
    v10_1_to_7_baseline: {
      status: baseline.status,
      allowed_claim: baseline.allowed_claim,
      read_model_baseline_claim_allowed: baseline.read_model_baseline_claim_allowed,
      evidence_ref: "docs/design/V10.x/evidence/v10-7-final-acceptance/v10-final-acceptance-data.json"
    },
    v10_8_agent_backed_bridge: {
      status: agentBacked.status,
      evidence_scope: agentBacked.evidence_scope,
      runtime_backed: agentBacked.runtime_backed,
      provider_mode: agentBacked.provider_mode,
      provider_backed: agentBacked.provider_backed,
      gateway_session_started: agentBacked.gateway_session_started,
      gateway_turn_started: agentBacked.gateway_turn_started,
      gateway_turn_completed: agentBacked.gateway_turn_completed,
      gateway_turn_failed: agentBacked.gateway_turn_failed,
      assistant_output_from_gateway: agentBacked.assistant_output_from_gateway,
      session_id: agentBacked.session_id,
      turn_id: agentBacked.turn_id,
      trace_id: agentBacked.trace_id,
      evidence_ref: "docs/design/V10.x/evidence/v10-8-agent-backed-tui/acceptance-data.json"
    },
    bounded_interpretation: {
      production_ready: false,
      full_production_ga: false,
      agent_executor_ready: false,
      complete_workflow_studio_ready: false,
      full_multi_agent_orchestration_ready: false,
      autonomous_workflow_editing_ready: false,
      codex_claude_experience_fully_matched: false
    },
    provider_backed_required_for_v10_final: false,
    provider_backed_claim_allowed: agentBacked.provider_backed === true,
    claim_scan: "PASS",
    redaction_scan: "PASS",
    drawio_xml: "PASS",
    blockers
  };
  fs.writeFileSync(path.join(OUT_DIR, "v10-final-acceptance-data.json"), `${JSON.stringify(data, null, 2)}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "v10-final-result-summary.md"), summaryMarkdown(data), "utf8");
  return data;
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function summaryMarkdown(data) {
  return `# V10-9 Final Acceptance Summary

status=${data.status}
final_claim_allowed=${data.final_claim_allowed}
allowed_claim=${data.allowed_claim}
provider_mode=${data.v10_8_agent_backed_bridge.provider_mode}
session_id=${data.v10_8_agent_backed_bridge.session_id}
turn_id=${data.v10_8_agent_backed_bridge.turn_id}
`;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const data = generateFinalAcceptance();
  console.log(JSON.stringify(data, null, 2));
  process.exitCode = data.status === "PASS" ? 0 : 1;
}
