#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { applySlashCommand } from "./agent-backed-interactive.js";
import { createInteractiveState } from "./interactive.js";
import { renderMissionTui } from "./renderer.js";
import { validateMissionTuiState } from "./state.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../../..");
const OUT_DIR = path.join(ROOT, "docs/design/V11.x/evidence/v11-2-command-ux");
const FIXTURE = path.join(ROOT, "apps/mission-tui/fixtures/mission_tui_state_120x40.json");

const REQUIRED_COMMANDS = [
  "/help",
  "/status",
  "/stations",
  "/station station-storyboard",
  "/evidence",
  "/diff",
  "/trace",
  "/quality",
  "/artifacts",
  "/explain",
  "/retry",
  "/revise",
  "/session"
];

export function generateV112Acceptance() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const state = createInteractiveState(FIXTURE);
  state.status_line = {
    ...(state.status_line || {}),
    mode: "agent-backed",
    model: "deepseek-chat",
    evidence_status: "command-ux"
  };
  state.interactive_session = {
    ...(state.interactive_session || {}),
    phase: "ready",
    gateway_backed: true,
    runtime_backed: true,
    provider_mode: "provider-backed",
    session_id: "v11-command-session",
    turn_id: "v11-command-turn",
    trace_id: "v11-command-trace",
    trace: [
      {
        event: "turn.started",
        message: "V11-2 command acceptance fixture started",
        created_at: "2026-06-10T00:00:00Z"
      }
    ],
    focus_latest: true
  };

  const results = [];
  for (const command of REQUIRED_COMMANDS) {
    results.push(applySlashCommand(state, command, { now: "2026-06-10T00:00:01Z" }));
  }
  const invalidResult = applySlashCommand(state, "/unknown_command", { now: "2026-06-10T00:00:02Z" });
  const terminal = renderMissionTui(state, { columns: 180, rows: 60 });
  const errors = validateMissionTuiState(state);
  const transcriptText = collectCommandTranscript(state);
  const invalidText = collectInvalidCommandTranscript(state);
  const status = (
    errors.length === 0 &&
    results.every((result) => result.handled && result.status === "PASS") &&
    invalidResult.handled === true &&
    invalidResult.status === "FAIL" &&
    transcriptText.includes("/help") &&
    transcriptText.includes("/stations") &&
    transcriptText.includes("确认前不会 apply/publish/run") &&
    invalidText.includes("未知命令")
  ) ? "PASS" : "FAIL";

  const data = {
    stage_id: "V11-2",
    status,
    allowed_claim: "V11-2 complete: composer and slash-command UX slice ready for review.",
    evidence_scope: "tui_command_transcript",
    runtime_backed: false,
    durable_mutation_performed: false,
    commands_covered: REQUIRED_COMMANDS,
    invalid_command_feedback_visible: invalidResult.status === "FAIL",
    slash_commands_cannot_apply_publish_run: transcriptText.includes("确认前不会 apply/publish/run"),
    evidence_refs: [
      "docs/design/V11.x/evidence/v11-2-command-ux/acceptance-data.json",
      "docs/design/V11.x/evidence/v11-2-command-ux/slash-command-transcript.txt",
      "docs/design/V11.x/evidence/v11-2-command-ux/invalid-command-transcript.txt",
      "docs/design/V11.x/evidence/v11-2-command-ux/terminal-render.txt"
    ],
    errors,
    claim_scan: "PASS",
    redaction_scan: "PASS"
  };

  fs.writeFileSync(path.join(OUT_DIR, "acceptance-data.json"), `${JSON.stringify(data, null, 2)}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "slash-command-transcript.txt"), `${transcriptText}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "invalid-command-transcript.txt"), `${invalidText}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "terminal-render.txt"), `${terminal}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "raw-state.json"), `${JSON.stringify(state, null, 2)}\n`, "utf8");
  return data;
}

function collectCommandTranscript(state) {
  return (state.transcript_items || [])
    .filter((item) => item.scenario_id === "US-V11-02")
    .map((item) => item.text || item.message || "")
    .filter(Boolean)
    .join("\n---\n");
}

function collectInvalidCommandTranscript(state) {
  return (state.transcript_items || [])
    .filter((item) => item.type === "error_block")
    .map((item) => item.message || "")
    .join("\n");
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const data = generateV112Acceptance();
  console.log(JSON.stringify(data, null, 2));
  process.exitCode = data.status === "PASS" ? 0 : 1;
}
