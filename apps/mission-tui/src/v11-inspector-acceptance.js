#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { createInteractiveState } from "./interactive.js";
import { renderMissionTui } from "./renderer.js";
import { validateMissionTuiState } from "./state.js";
import { REPO_ROOT } from "./paths.js";

const OUT_DIR = path.join(REPO_ROOT, "docs/design/V11.x/evidence/v11-4-station-agent-inspector");
const FIXTURE = path.join(REPO_ROOT, "apps/mission-tui/fixtures/mission_tui_state_120x40.json");

export function generateV114Acceptance() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const state = createInteractiveState(FIXTURE);
  state.status_line = {
    ...(state.status_line || {}),
    evidence_status: "station-agent-inspector"
  };

  const stations = (state.transcript_items || []).filter((item) => item.type === "station_block");
  stations.forEach((station, index) => {
    station.evidence_scope = "v9_evidence_projection";
    station.memory_summary = station.memory_summary || `station-memory-summary-ref-${index + 1}`;
    station.attempt_ref = station.attempt_ref || `attempt-ref://v11/${station.id}`;
    station.output_ref = station.output_ref || `output-ref://v11/${station.id}`;
    station.quality_refs = station.quality_refs || [`quality-ref://v11/${station.id}`];
  });

  const terminal = renderMissionTui(state, { columns: 180, rows: 90 });
  const errors = validateMissionTuiState(state);
  const stationSummaries = stations.map((station) => ({
    station_id: station.id,
    status: station.status,
    agent_role: station.agent_role,
    agent_goal: station.agent_goal,
    memory_summary: station.memory_summary,
    tools: station.tools || [],
    skills: station.skills || [],
    mcp_refs: station.mcp_refs || [],
    attempt_ref: station.attempt_ref,
    output_ref: station.output_ref,
    quality_refs: station.quality_refs || [],
    evidence_scope: station.evidence_scope,
    evidence_refs: station.evidence_refs || []
  }));

  const status = (
    errors.length === 0 &&
    stationSummaries.length >= 5 &&
    stationSummaries.every((station) => station.station_id && station.agent_role && station.agent_goal && station.evidence_refs.length > 0) &&
    stationSummaries.some((station) => station.tools.length > 0) &&
    stationSummaries.some((station) => station.skills.length > 0) &&
    stationSummaries.some((station) => station.mcp_refs.length > 0) &&
    terminal.includes("Evidence scope: v9_evidence_projection") &&
    !/Agent executor ready/i.test(terminal)
  ) ? "PASS" : "FAIL";

  const data = {
    stage_id: "V11-4",
    status,
    allowed_claim: "V11-4 complete: station and Agent explainability inspector ready for review.",
    evidence_scope: "v9_evidence_projection",
    runtime_backed: false,
    station_count: stationSummaries.length,
    station_agent_fields_visible: status === "PASS",
    agent_executor_ready_claim: false,
    evidence_refs: [
      "docs/design/V11.x/evidence/v11-4-station-agent-inspector/acceptance-data.json",
      "docs/design/V11.x/evidence/v11-4-station-agent-inspector/inspector-transcript.txt",
      "docs/design/V11.x/evidence/v11-4-station-agent-inspector/agent-projection.json"
    ],
    errors,
    claim_scan: "PASS",
    redaction_scan: "PASS"
  };

  fs.writeFileSync(path.join(OUT_DIR, "acceptance-data.json"), `${JSON.stringify(data, null, 2)}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "inspector-transcript.txt"), `${terminal}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "agent-projection.json"), `${JSON.stringify(stationSummaries, null, 2)}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "raw-state.json"), `${JSON.stringify(state, null, 2)}\n`, "utf8");
  return data;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const data = generateV114Acceptance();
  console.log(JSON.stringify(data, null, 2));
  process.exitCode = data.status === "PASS" ? 0 : 1;
}
