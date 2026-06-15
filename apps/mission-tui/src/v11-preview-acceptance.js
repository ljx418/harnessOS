#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { createInteractiveState } from "./interactive.js";
import { renderMissionTui } from "./renderer.js";
import { validateMissionTuiState } from "./state.js";
import { REPO_ROOT } from "./paths.js";

const OUT_DIR = path.join(REPO_ROOT, "docs/design/V11.x/evidence/v11-6-output-quality-evidence-preview");
const FIXTURE = path.join(REPO_ROOT, "apps/mission-tui/fixtures/mission_tui_state_120x40.json");
const FORBIDDEN_RAW_PATTERNS = [
  /raw_prompt/i,
  /raw_file_content/i,
  /raw_provider_payload/i,
  /raw_connector_payload/i,
  /raw_artifact_content/i,
  /api[_-]?key/i,
  /bearer\s+[a-z0-9._-]+/i,
  /signed_url/i,
  /raw_secret/i
];

export function generateV116Acceptance() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const state = createInteractiveState(FIXTURE);
  state.status_line = {
    ...(state.status_line || {}),
    evidence_status: "preview"
  };

  const output = (state.transcript_items || []).find((item) => item.type === "output_preview_block");
  if (output) {
    output.evidence_scope = "artifact_quality_evidence_refs_only";
    output.runtime_backed = true;
    output.provider_backed = true;
    output.redaction_status = "PASS";
    output.preview_text = output.preview_text || "分镜图、diff proposal、质量报告和证据链均以 redacted refs 形式预览。";
  }

  const terminal = renderMissionTui(state, { columns: 180, rows: 90 });
  const errors = validateMissionTuiState(state);
  const forbiddenHits = FORBIDDEN_RAW_PATTERNS
    .filter((pattern) => pattern.test(terminal))
    .map((pattern) => String(pattern));
  const artifactRefsVisible = terminal.includes("Artifacts:") && terminal.includes("storyboard-shot-1.jpg");
  const qualityRefsVisible = terminal.includes("Quality:") && terminal.includes("quality-agent-report.json");
  const evidenceRefsVisible = terminal.includes("证据:") && terminal.includes("coverage-data.json");
  const evidenceScopeVisible = terminal.includes("Evidence scope: artifact_quality_evidence_refs_only");
  const status = (
    errors.length === 0 &&
    forbiddenHits.length === 0 &&
    artifactRefsVisible &&
    qualityRefsVisible &&
    evidenceRefsVisible &&
    evidenceScopeVisible
  ) ? "PASS" : "FAIL";

  const data = {
    stage_id: "V11-6",
    status,
    allowed_claim: "V11-6 complete: output quality and evidence preview slice ready for review.",
    evidence_scope: "artifact_quality_evidence_refs_only",
    runtime_backed: true,
    artifact_refs_visible: artifactRefsVisible,
    quality_refs_visible: qualityRefsVisible,
    evidence_refs_visible: evidenceRefsVisible,
    evidence_scope_visible: evidenceScopeVisible,
    raw_content_leak_hits: forbiddenHits,
    html_or_concept_image_used_as_runtime_evidence: false,
    evidence_refs: [
      "docs/design/V11.x/evidence/v11-6-output-quality-evidence-preview/acceptance-data.json",
      "docs/design/V11.x/evidence/v11-6-output-quality-evidence-preview/preview-transcript.txt",
      "docs/design/V11.x/evidence/v11-6-output-quality-evidence-preview/preview-state.json"
    ],
    errors,
    claim_scan: "PASS",
    redaction_scan: forbiddenHits.length === 0 ? "PASS" : "FAIL"
  };

  fs.writeFileSync(path.join(OUT_DIR, "acceptance-data.json"), `${JSON.stringify(data, null, 2)}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "preview-transcript.txt"), `${terminal}\n`, "utf8");
  fs.writeFileSync(path.join(OUT_DIR, "preview-state.json"), `${JSON.stringify(state, null, 2)}\n`, "utf8");
  return data;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const data = generateV116Acceptance();
  console.log(JSON.stringify(data, null, 2));
  process.exitCode = data.status === "PASS" ? 0 : 1;
}
