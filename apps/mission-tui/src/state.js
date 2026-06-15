import fs from "node:fs";
import { resolveReadablePath } from "./paths.js";

export const FORBIDDEN_RAW_KEYS = [
  "raw_prompt",
  "raw_provider_payload",
  "raw_connector_payload",
  "raw_artifact_content",
  "api_key",
  "bearer_token",
  "signed_url",
  "raw_secret"
];

export const ALLOWED_ACTIONS = new Set([
  "submit_goal",
  "open_command_palette",
  "expand_block",
  "open_evidence",
  "confirm_proposal",
  "revise_proposal",
  "reject_proposal",
  "export_html_explainer"
]);

export const FORBIDDEN_ACTIONS = new Set([
  "auto_apply_workflowdiff",
  "auto_publish_workflow",
  "agent_direct_mutation",
  "run_unrestricted_terminal",
  "claim_runtime_truth_from_html"
]);

export function loadState(filePath) {
  const absolutePath = resolveReadablePath(filePath);
  return JSON.parse(fs.readFileSync(absolutePath, "utf8"));
}

export function validateMissionTuiState(state) {
  const errors = [];
  if (!state || typeof state !== "object") {
    return ["state must be an object"];
  }
  if (state.runtime_truth_boundary !== "tui_read_model_not_runtime_truth") {
    errors.push("runtime_truth_boundary must remain tui_read_model_not_runtime_truth");
  }
  if (!state.status_line || typeof state.status_line !== "object") {
    errors.push("status_line is required");
  }
  if (!Array.isArray(state.transcript_items)) {
    errors.push("transcript_items must be an array");
  }
  if (!Array.isArray(state.evidence_refs) || state.evidence_refs.length === 0) {
    errors.push("top-level evidence_refs must be non-empty");
  }

  visitRawFields(state, [], errors);

  for (const item of state.transcript_items || []) {
    validateTranscriptItem(item, errors);
  }
  for (const action of state.available_actions || []) {
    if (FORBIDDEN_ACTIONS.has(action.id)) {
      errors.push(`forbidden action is exposed: ${action.id}`);
    }
    if (!ALLOWED_ACTIONS.has(action.id)) {
      errors.push(`unknown action is exposed: ${action.id}`);
    }
  }
  return errors;
}

function validateTranscriptItem(item, errors) {
  for (const key of ["id", "type", "status", "created_at"]) {
    if (!item[key]) errors.push(`${item.type || "unknown"} block missing ${key}`);
  }
  if (item.redacted !== true) {
    errors.push(`${item.id || "unknown"} must be redacted=true`);
  }
  if (["station_block", "output_preview_block", "permission_block", "workflowdiff_block", "workflow_timeline_block"].includes(item.type)) {
    if (!Array.isArray(item.evidence_refs) || item.evidence_refs.length === 0) {
      errors.push(`${item.id || item.type} requires at least one evidence_ref`);
    }
  }
  if (item.type === "permission_block" && item.decision === "denied") {
    if (!item.forbidden_reason_refs || item.forbidden_reason_refs.length === 0) {
      errors.push(`${item.id} denied permission requires forbidden_reason_refs`);
    }
  }
  if (item.type === "workflowdiff_block") {
    for (const action of item.actions || []) {
      if (FORBIDDEN_ACTIONS.has(action)) {
        errors.push(`${item.id} exposes forbidden WorkflowDiff action ${action}`);
      }
    }
    if (item.source === "agent" && item.durable_mutation === true) {
      errors.push(`${item.id} lets source=agent directly perform durable mutation`);
    }
  }
  if (item.type === "workflow_timeline_block") {
    validateWorkflowTimelineBlock(item, errors);
  }
}

function validateWorkflowTimelineBlock(item, errors) {
  if (!Array.isArray(item.timeline) || item.timeline.length === 0) {
    errors.push(`${item.id} requires non-empty timeline`);
    return;
  }
  const states = item.timeline.map((entry) => entry.state);
  for (const required of ["goal", "spec", "diff", "confirmation", "run", "runtime_report", "evidence"]) {
    if (!states.includes(required)) {
      errors.push(`${item.id} missing workflow timeline state ${required}`);
    }
  }
  const confirmationIndex = states.indexOf("confirmation");
  const runIndex = states.indexOf("run");
  if (runIndex >= 0 && confirmationIndex >= 0 && runIndex < confirmationIndex) {
    errors.push(`${item.id} run state appears before confirmation state`);
  }
  const confirmation = item.timeline.find((entry) => entry.state === "confirmation");
  const run = item.timeline.find((entry) => entry.state === "run");
  if (item.confirmation_required !== true) {
    errors.push(`${item.id} must require confirmation`);
  }
  if (confirmation && confirmation.status !== "awaiting_confirmation") {
    errors.push(`${item.id} confirmation must remain awaiting_confirmation`);
  }
  if (run && run.status === "done") {
    errors.push(`${item.id} run cannot be done before confirmation`);
  }
}

function visitRawFields(value, pathParts, errors) {
  if (!value || typeof value !== "object") return;
  if (Array.isArray(value)) {
    value.forEach((item, index) => visitRawFields(item, [...pathParts, String(index)], errors));
    return;
  }
  for (const [key, nested] of Object.entries(value)) {
    const normalized = key.toLowerCase();
    if (FORBIDDEN_RAW_KEYS.includes(normalized)) {
      errors.push(`forbidden raw field ${[...pathParts, key].join(".")}`);
    }
    visitRawFields(nested, [...pathParts, key], errors);
  }
}

export function summarizeAcceptance(state) {
  const scenarios = new Set();
  for (const item of state.transcript_items || []) {
    if (item.scenario_id) scenarios.add(item.scenario_id);
  }
  return {
    schema_version: "v10.mission_tui_acceptance.v1",
    status: validateMissionTuiState(state).length === 0 ? "PASS" : "FAIL",
    runtime_truth_boundary: state.runtime_truth_boundary,
    scenario_count: scenarios.size,
    block_count: state.transcript_items?.length || 0,
    evidence_ref_count: state.evidence_refs?.length || 0
  };
}
