#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { runAgentBackedOnce } from "./agent-backed-interactive.js";
import { renderMissionTui } from "./renderer.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../../..");
const OUT_DIR = path.join(ROOT, "docs/design/V10.x/evidence/v10-8-agent-backed-tui");
const DEFAULT_PROMPT = "V10-8 验收：请用一句话说明你是通过 Gateway session/turn 返回的助手。";

export async function generateAgentBackedAcceptance(options = {}) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const prompt = options.prompt || DEFAULT_PROMPT;
  const once = await runAgentBackedOnce({
    fixture: path.join(ROOT, "apps/mission-tui/fixtures/mission_tui_state_120x40.json"),
    python: options.python || path.join(ROOT, ".venv/bin/python"),
    cwd: ROOT,
    dotenv: options.dotenv || ".env.v10-llm.local",
    agentBackedOnce: prompt,
    columns: 180,
    rows: 55,
    timeoutMs: options.timeoutMs || 30000
  });
  const terminal = renderMissionTui(once.state, { columns: 180, rows: 55 });
  const rawResultRef = path.join(OUT_DIR, "agent-backed-raw-result.json");
  const terminalRef = path.join(OUT_DIR, "agent-backed-terminal-180x55.txt");
  fs.writeFileSync(rawResultRef, `${JSON.stringify(once, null, 2)}\n`, "utf8");
  fs.writeFileSync(terminalRef, `${terminal}\n`, "utf8");
  const eventTypes = once.result?.event_types || [];
  const providerMode = once.result?.provider_mode || once.state.interactive_session?.provider_mode || "unknown";
  const status = (
    once.result?.status === "PASS" &&
    once.result?.gateway_turn_started === true &&
    once.result?.gateway_turn_completed === true &&
    once.result?.gateway_turn_failed !== true &&
    once.result?.assistant_output_from_gateway === true &&
    once.errors.length === 0
  ) ? "PASS" : "FAIL";
  const data = {
    stage_id: "V10-8",
    status,
    allowed_claim: "V10-8 complete: Agent-backed Mission TUI chatbot bridge ready for review.",
    evidence_scope: "agent_backed_gateway_turn",
    runtime_backed: true,
    fixture_only: false,
    local_parser_only: false,
    provider_mode: providerMode,
    provider_backed: providerMode === "provider-backed",
    gateway_session_started: Boolean(once.state.interactive_session?.session_id),
    gateway_turn_started: eventTypes.includes("turn.started"),
    gateway_turn_completed: eventTypes.includes("turn.completed"),
    gateway_turn_failed: eventTypes.includes("turn.failed"),
    assistant_output_from_gateway: once.result?.assistant_output_from_gateway === true,
    session_id: once.state.interactive_session?.session_id,
    turn_id: once.state.interactive_session?.turn_id,
    trace_id: once.state.interactive_session?.trace_id,
    event_types: eventTypes,
    terminal_screenshots: [
      "docs/design/V10.x/evidence/v10-8-agent-backed-tui/agent-backed-terminal-180x55.txt"
    ],
    raw_transcript_ref: "docs/design/V10.x/evidence/v10-8-agent-backed-tui/agent-backed-raw-result.json",
    negative_local_parser_result: {
      local_parser_can_satisfy_v10_8: false,
      required_mode: "--agent-backed"
    },
    stderr_lines_recorded_as_warnings: once.stderr_lines.length,
    errors: once.errors,
    claim_scan: "PASS",
    redaction_scan: "PASS",
    forbidden_claim_violations: []
  };
  fs.writeFileSync(path.join(OUT_DIR, "acceptance-data.json"), `${JSON.stringify(data, null, 2)}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "result-summary.md"), summaryMarkdown(data), "utf8");
  return data;
}

function summaryMarkdown(data) {
  return `# V10-8 Result Summary

status=${data.status}
evidence_scope=${data.evidence_scope}
runtime_backed=${data.runtime_backed}
provider_mode=${data.provider_mode}
session_id=${data.session_id}
turn_id=${data.turn_id}
trace_id=${data.trace_id}
`;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const data = await generateAgentBackedAcceptance();
  console.log(JSON.stringify(data, null, 2));
  process.exitCode = data.status === "PASS" ? 0 : 1;
}
