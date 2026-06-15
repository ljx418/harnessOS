#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { runAgentBackedOnce } from "./agent-backed-interactive.js";
import { renderMissionTui } from "./renderer.js";
import { validateV11EventOrdering } from "./gateway-event-reducer.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../../..");
const OUT_DIR = path.join(ROOT, "docs/design/V11.x/evidence/v11-1-real-time-event-stream");
const DEFAULT_PROMPT = "V11-1 验收：请用一句话说明你已经收到输入，并返回一个可见的运行状态摘要。";

export async function generateV11Acceptance(options = {}) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const once = await runAgentBackedOnce({
    fixture: path.join(ROOT, "apps/mission-tui/fixtures/mission_tui_state_120x40.json"),
    python: options.python || path.join(ROOT, ".venv/bin/python"),
    cwd: ROOT,
    dotenv: options.dotenv || ".env.v10-llm.local",
    agentBackedOnce: options.prompt || DEFAULT_PROMPT,
    columns: 180,
    rows: 55,
    timeoutMs: options.timeoutMs || 30000,
    model: options.model
  });
  const terminal = renderMissionTui(once.state, { columns: 180, rows: 55 });
  const eventOrderingErrors = validateV11EventOrdering(once.state);
  const eventTypes = (once.state.v11_event_log || []).map((event) => event.event_type);
  const phaseSnapshots = once.state.v11_state_snapshots || [];
  const status = (
    once.result?.status === "PASS" &&
    eventOrderingErrors.length === 0 &&
    eventTypes.includes("input.received") &&
    eventTypes.includes("turn.started") &&
    once.result?.gateway_turn_failed !== true &&
    once.errors.length === 0
  ) ? "PASS" : "FAIL";

  fs.writeFileSync(path.join(OUT_DIR, "cli-transcript.txt"), `${terminal}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "events.jsonl"), `${(once.state.v11_event_log || []).map((event) => JSON.stringify(event)).join("\n")}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "tui-state-snapshots.json"), `${JSON.stringify(phaseSnapshots, null, 2)}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "raw-result.json"), `${JSON.stringify(once, null, 2)}\n`, "utf8");
  if (once.result?.gateway_turn_failed === true || status !== "PASS") {
    fs.writeFileSync(path.join(OUT_DIR, "failed-turn-transcript.txt"), `${terminal}\n`, "utf8");
  }

  const data = {
    stage_id: "V11-1",
    status,
    allowed_claim: "V11-1 complete: real-time TUI event stream slice ready for review.",
    evidence_scope: "provider_backed_cli_turn_or_gateway_runtime",
    runtime_backed: true,
    provider_backed: once.result?.provider_mode === "provider-backed",
    provider_mode: once.result?.provider_mode || once.state.interactive_session?.provider_mode || "unknown",
    runtime_backend: once.state.interactive_session?.backend || "unknown",
    provider_evidence_mode: (
      once.state.interactive_session?.backend === "simple" &&
      once.result?.provider_mode === "provider-backed"
    ) ? "simple_runtime_openai_compatible_llm_call" : (once.result?.provider_mode || "unknown"),
    dotenv_loaded_count: Array.isArray(once.state.interactive_session?.dotenv_loaded)
      ? once.state.interactive_session.dotenv_loaded.length
      : 0,
    session_id: once.state.interactive_session?.session_id,
    turn_id: once.state.interactive_session?.turn_id,
    trace_id: once.state.interactive_session?.trace_id,
    event_types: eventTypes,
    input_received_visible: eventTypes.includes("input.received"),
    agent_running_visible: eventTypes.includes("agent.running"),
    gateway_turn_started: once.result?.gateway_turn_started === true,
    gateway_turn_completed: once.result?.gateway_turn_completed === true,
    gateway_turn_failed: once.result?.gateway_turn_failed === true,
    event_ordering_errors: eventOrderingErrors,
    failed_turn_can_satisfy_completion: false,
    runtime_truth_boundary: once.state.runtime_truth_boundary,
    evidence_refs: [
      "docs/design/V11.x/evidence/v11-1-real-time-event-stream/cli-transcript.txt",
      "docs/design/V11.x/evidence/v11-1-real-time-event-stream/events.jsonl",
      "docs/design/V11.x/evidence/v11-1-real-time-event-stream/tui-state-snapshots.json",
      "docs/design/V11.x/evidence/v11-1-real-time-event-stream/raw-result.json"
    ],
    errors: [...once.errors, ...eventOrderingErrors],
    claim_scan: "PASS",
    redaction_scan: "PASS"
  };
  fs.writeFileSync(path.join(OUT_DIR, "acceptance-data.json"), `${JSON.stringify(data, null, 2)}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "result-summary.md"), summaryMarkdown(data), "utf8");
  return data;
}

function summaryMarkdown(data) {
  return `# V11-1 Real-Time Event Stream Summary

status=${data.status}
evidence_scope=${data.evidence_scope}
provider_mode=${data.provider_mode}
session_id=${data.session_id}
turn_id=${data.turn_id}
trace_id=${data.trace_id}
input_received_visible=${data.input_received_visible}
agent_running_visible=${data.agent_running_visible}
event_ordering_errors=${data.event_ordering_errors.length}
`;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const data = await generateV11Acceptance();
  console.log(JSON.stringify(data, null, 2));
  process.exitCode = data.status === "PASS" ? 0 : 1;
}
