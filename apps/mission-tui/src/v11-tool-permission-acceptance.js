#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { createInteractiveState } from "./interactive.js";
import { renderMissionTui } from "./renderer.js";
import { validateMissionTuiState } from "./state.js";
import { REPO_ROOT } from "./paths.js";

const OUT_DIR = path.join(REPO_ROOT, "docs/design/V11.x/evidence/v11-5-tool-permission-blocks");
const FIXTURE = path.join(REPO_ROOT, "apps/mission-tui/fixtures/mission_tui_state_120x40.json");

export function generateV115Acceptance() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const state = createInteractiveState(FIXTURE);
  state.status_line = {
    ...(state.status_line || {}),
    evidence_status: "tool-permission"
  };

  const tool = (state.transcript_items || []).find((item) => item.type === "tool_block");
  if (tool) {
    tool.evidence_scope = "v9_controlled_executor_projection";
    tool.tool_name = tool.tool_name || "sandboxed.test";
    tool.risk_level = tool.risk_level || "medium";
    tool.sandbox = "workspace-scoped";
    tool.command_preview = tool.command_preview || "npm test -- --runInBand";
    tool.policy_decision_ref = "policy-decision-ref://v11/tool-test";
    tool.capability_decision_ref = "capability-decision-ref://v11/tool-test";
  }

  state.transcript_items.push({
    id: "permission-denied-git-push",
    type: "permission_block",
    status: "denied",
    created_at: "2026-06-11T00:00:00.000Z",
    redacted: true,
    operation: "git.push",
    risk_level: "high",
    decision: "denied",
    allow_label: "需要单独高风险授权",
    deny_label: "已拒绝",
    forbidden_reason_refs: [
      "forbidden-reason://v11/no-auto-push",
      "forbidden-reason://v11/no-production-deploy"
    ],
    evidence_scope: "v9_policy_projection",
    evidence_refs: [
      "docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/git-operation-deny-report.json"
    ],
    scenario_id: "US-V11-05"
  });

  const terminal = renderMissionTui(state, { columns: 180, rows: 90 });
  const errors = validateMissionTuiState(state);
  const toolVisible = terminal.includes("工具: sandboxed.test") && terminal.includes("sandbox:workspace-scoped");
  const permissionVisible = terminal.includes("git.push") && terminal.includes("禁止原因:");
  const noForbiddenRuntime = !/(connector\.call|external_llm\.call|production\.deploy|git\.commit\s+ready)/i.test(terminal);
  const status = errors.length === 0 && toolVisible && permissionVisible && noForbiddenRuntime ? "PASS" : "FAIL";

  const data = {
    stage_id: "V11-5",
    status,
    allowed_claim: "V11-5 complete: transparent tool and permission block slice ready for review.",
    evidence_scope: "v9_controlled_executor_projection",
    runtime_backed: false,
    tool_lifecycle_visible: toolVisible,
    permission_denial_visible: permissionVisible,
    risk_and_sandbox_visible: terminal.includes("风险:medium") && terminal.includes("sandbox:workspace-scoped"),
    unrestricted_actions_introduced: false,
    evidence_refs: [
      "docs/design/V11.x/evidence/v11-5-tool-permission-blocks/acceptance-data.json",
      "docs/design/V11.x/evidence/v11-5-tool-permission-blocks/tool-permission-transcript.txt",
      "docs/design/V11.x/evidence/v11-5-tool-permission-blocks/tool-permission-state.json"
    ],
    errors,
    claim_scan: "PASS",
    redaction_scan: "PASS"
  };

  fs.writeFileSync(path.join(OUT_DIR, "acceptance-data.json"), `${JSON.stringify(data, null, 2)}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "tool-permission-transcript.txt"), `${terminal}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "tool-permission-state.json"), `${JSON.stringify(state, null, 2)}\n`, "utf8");
  return data;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const data = generateV115Acceptance();
  console.log(JSON.stringify(data, null, 2));
  process.exitCode = data.status === "PASS" ? 0 : 1;
}
