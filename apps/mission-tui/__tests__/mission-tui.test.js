import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { loadState, validateMissionTuiState } from "../src/state.js";
import { renderMissionTui } from "../src/renderer.js";
import { generateAcceptance } from "../src/acceptance.js";
import { applyInteractiveInput, createInteractiveState } from "../src/interactive.js";
import { parseGatewayResponseLine } from "../src/gateway-stdio-client.js";
import { applyGatewaySessionStarted, applyGatewayTurnResult, validateV11EventOrdering } from "../src/gateway-event-reducer.js";
import { applySlashCommand, createAgentBackedState, submitAgentBackedTurn } from "../src/agent-backed-interactive.js";
import { loadDotenvEnv, parseDotenv } from "../src/dotenv.js";
import { generateV113Acceptance } from "../src/v11-timeline-acceptance.js";
import { generateV114Acceptance } from "../src/v11-inspector-acceptance.js";
import { generateV115Acceptance } from "../src/v11-tool-permission-acceptance.js";
import { generateV116Acceptance } from "../src/v11-preview-acceptance.js";
import { generateV117Acceptance } from "../src/v11-html-explainer-acceptance.js";
import { generateV118Acceptance } from "../src/v11-scenario-acceptance.js";
import { generateV119Acceptance } from "../src/v11-final-acceptance.js";

const ROOT = path.resolve("../..");
const PACKAGE_ROOT = path.join(ROOT, "apps/mission-tui");
const fixture = (name) => path.join(ROOT, "apps/mission-tui/fixtures", name);

test("renders CLI-native shell with status line and bottom composer", () => {
  const state = loadState(fixture("mission_tui_state_80x24.json"));
  assert.deepEqual(validateMissionTuiState(state), []);
  const output = renderMissionTui(state, { columns: 80, rows: 24 });
  assert.match(output, /HarnessOS/);
  assert.match(output, /› 输入消息或 \/command/);
  assert.match(output, /WorkflowDiff/);
  assert.doesNotMatch(output, /OpenHarness/);
});

test("CLI default fixture resolves when launched from package cwd", () => {
  const output = execFileSync(process.execPath, ["src/cli.js", "--validate", "--json"], {
    cwd: PACKAGE_ROOT,
    encoding: "utf8"
  });
  const parsed = JSON.parse(output);
  assert.equal(Array.isArray(parsed.errors), true);
  assert.deepEqual(parsed.errors, []);
});

test("renders all required V10 user scenarios in wide fixture", () => {
  const state = loadState(fixture("mission_tui_state_120x40.json"));
  assert.deepEqual(validateMissionTuiState(state), []);
  const scenarios = new Set(state.transcript_items.map((item) => item.scenario_id).filter(Boolean));
  for (const id of ["US-V10-01", "US-V10-02", "US-V10-03", "US-V10-04", "US-V10-05"]) {
    assert.equal(scenarios.has(id), true, `${id} missing`);
  }
  const output = renderMissionTui(state, { columns: 120, rows: 40 });
  assert.match(output, /Document Scanner Agent/);
  assert.match(output, /Stoic Persona Agent/);
  assert.match(output, /Storyboard Agent/);
  assert.match(output, /Coding Proposal Agent/);
  assert.match(output, /确认前不会 apply \/ publish \/ run/);
});

test("rejects negative fixtures that would create false green", () => {
  for (const name of [
    "station_without_evidence_ref.json",
    "workflowdiff_auto_apply_action.json",
    "raw_secret_in_tui_state.json"
  ]) {
    const state = loadState(fixture(name));
    assert.notEqual(validateMissionTuiState(state).length, 0, `${name} should fail`);
  }
});

test("generates V10 shell and final acceptance evidence", () => {
  const result = generateAcceptance();
  assert.equal(result.status, "PASS");
  assert.equal(result.read_model_baseline_claim_allowed, true);
  assert.equal(result.final_claim_allowed, false);
  assert.equal(result.final_v10_completion_blocked_until_v10_8, true);
  assert.equal(result.stage_evidence.length, 6);
  assert.equal(result.user_scenarios.length, 5);
  assert.equal(fs.existsSync(path.join(ROOT, "docs/design/V10.x/evidence/v10-1-mission-tui-shell/real-tui-80x24.txt")), true);
  assert.equal(fs.existsSync(path.join(ROOT, "docs/design/V10.x/evidence/v10-7-final-acceptance/v10-final-acceptance-data.json")), true);
});

test("interactive mode appends live user input without durable mutation", () => {
  const state = createInteractiveState(fixture("mission_tui_state_80x24.json"));
  const before = state.transcript_items.length;
  applyInteractiveInput(state, "帮我创建一个罗马广场讨论工作流", "2026-06-09T00:00:00.000Z");
  assert.ok(state.transcript_items.length > before);
  assert.equal(state.status_line.model, "local-interactive-no-provider");
  assert.equal(state.transcript_items.some((item) => item.type === "user_message" && item.text.includes("罗马广场")), true);
  const diff = state.transcript_items.find((item) => item.id === state.selected_item_id);
  assert.equal(diff.type, "workflowdiff_block");
  assert.equal(diff.durable_mutation, false);
  assert.equal(state.workflow_state_timeline.type, "workflow_timeline_block");
  assert.equal(state.workflow_state_timeline.confirmation_required, true);
  assert.equal(state.workflow_state_timeline.timeline.find((entry) => entry.state === "run").status, "blocked");
  assert.deepEqual(validateMissionTuiState(state), []);
});

test("parses gateway stdio response shape and rejects invalid lines", () => {
  const payload = parseGatewayResponseLine('{"id":"1","result":{"ok":true},"error":null}');
  assert.equal(payload.id, "1");
  assert.throws(() => parseGatewayResponseLine('{"id":"1","result":{}}'), /missing error/);
});

test("gateway reducer renders session, turn, trace, and assistant output", () => {
  const state = createInteractiveState(fixture("mission_tui_state_80x24.json"));
  applyGatewaySessionStarted(state, {
    session_id: "sess_test",
    model: "fake-model",
    backend: "simple"
  }, "2026-06-09T00:00:00.000Z");
  const summary = applyGatewayTurnResult(state, {
    session_id: "sess_test",
    turn_id: "turn_test",
    trace_id: "trace_test",
    final_text: "reply from gateway",
    events: [
      { type: "turn.started", session_id: "sess_test", turn_id: "turn_test", item_id: "item_started", timestamp: "2026-06-09T00:00:01.000Z", data: { trace_id: "trace_test" } },
      { type: "item.delta", session_id: "sess_test", turn_id: "turn_test", item_id: "item_delta", timestamp: "2026-06-09T00:00:02.000Z", data: { text: "reply from gateway", trace_id: "trace_test", mode: "mock" } },
      { type: "turn.completed", session_id: "sess_test", turn_id: "turn_test", item_id: "item_done", timestamp: "2026-06-09T00:00:03.000Z", data: { trace_id: "trace_test" } }
    ]
  }, { now: "2026-06-09T00:00:04.000Z" });
  assert.equal(summary.gateway_turn_started, true);
  assert.equal(summary.gateway_turn_completed, true);
  assert.equal(summary.assistant_output_from_gateway, true);
  assert.equal(state.interactive_session.phase, "completed");
  const output = renderMissionTui(state, { columns: 160, rows: 40 });
  assert.match(output, /gateway:sess_test/);
  assert.match(output, /turn:turn_test/);
  assert.match(output, /provider_mode:demo-fallback/);
  assert.match(output, /reply from gateway/);
  assert.deepEqual(validateMissionTuiState(state), []);
});

test("agent-backed turn uses a gateway client and is not local-parser evidence", async () => {
  const state = await createAgentBackedState({ fixture: fixture("mission_tui_state_80x24.json") });
  applyGatewaySessionStarted(state, {
    session_id: "sess_fake",
    model: "fake-model",
    backend: "simple"
  }, "2026-06-09T00:00:00.000Z");
  const fakeClient = {
    async startTurn(params) {
      assert.equal(params.session_id, "sess_fake");
      assert.match(params.input, /多Agent/);
      return {
        session_id: "sess_fake",
        turn_id: "turn_fake",
        trace_id: "trace_fake",
        final_text: "Gateway-backed response",
        events: [
          { type: "turn.started", session_id: "sess_fake", turn_id: "turn_fake", item_id: "event_1", timestamp: "2026-06-09T00:00:01.000Z", data: { trace_id: "trace_fake" } },
          { type: "item.delta", session_id: "sess_fake", turn_id: "turn_fake", item_id: "event_2", timestamp: "2026-06-09T00:00:02.000Z", data: { text: "Gateway-backed response", trace_id: "trace_fake" } },
          { type: "turn.completed", session_id: "sess_fake", turn_id: "turn_fake", item_id: "event_3", timestamp: "2026-06-09T00:00:03.000Z", data: { trace_id: "trace_fake" } }
        ]
      };
    }
  };
  const result = await submitAgentBackedTurn(
    state,
    fakeClient,
    "我想做一个多Agent的工作流，期望可以实现对同一个话题的不同角度讨论",
    { now: "2026-06-09T00:00:00.000Z" }
  );
  assert.equal(result.status, "PASS");
  assert.deepEqual(result.ordering_errors, []);
  assert.equal(state.v11_event_log.some((event) => event.event_type === "input.received"), true);
  assert.equal(state.v11_event_log.some((event) => event.event_type === "agent.running"), true);
  assert.equal(state.v11_event_log.some((event) => event.event_type === "turn.started"), true);
  assert.deepEqual(validateV11EventOrdering(state), []);
  assert.equal(state.status_line.mode, "agent-backed");
  assert.equal(state.interactive_session.gateway_backed, true);
  assert.equal(state.interactive_session.runtime_backed, true);
  assert.notEqual(state.status_line.model, "local-interactive-no-provider");
  assert.deepEqual(validateMissionTuiState(state), []);
});

test("agent-backed turn emits visible V11 state changes before gateway result", async () => {
  const state = await createAgentBackedState({ fixture: fixture("mission_tui_state_80x24.json") });
  applyGatewaySessionStarted(state, {
    session_id: "sess_stream",
    model: "fake-model",
    backend: "simple"
  }, "2026-06-09T00:00:00.000Z");
  const phases = [];
  const fakeClient = {
    async startTurn() {
      phases.push(`during:${state.interactive_session.phase}`);
      return {
        session_id: "sess_stream",
        turn_id: "turn_stream",
        trace_id: "trace_stream",
        final_text: "Gateway-backed streaming response",
        events: [
          { type: "turn.started", session_id: "sess_stream", turn_id: "turn_stream", item_id: "stream_1", timestamp: "2026-06-09T00:00:01.000Z", data: { trace_id: "trace_stream" } },
          { type: "item.delta", session_id: "sess_stream", turn_id: "turn_stream", item_id: "stream_2", timestamp: "2026-06-09T00:00:02.000Z", data: { text: "Gateway-backed streaming response", trace_id: "trace_stream" } },
          { type: "turn.completed", session_id: "sess_stream", turn_id: "turn_stream", item_id: "stream_3", timestamp: "2026-06-09T00:00:03.000Z", data: { trace_id: "trace_stream" } }
        ]
      };
    }
  };
  const result = await submitAgentBackedTurn(
    state,
    fakeClient,
    "请展示 V11 实时状态",
    {
      now: "2026-06-09T00:00:00.000Z",
      onStateChange: (_, info) => phases.push(info.phase)
    }
  );
  assert.equal(result.status, "PASS");
  assert.deepEqual(phases.slice(0, 3), ["input_received", "agent_running", "during:agent_running"]);
  assert.ok(state.v11_state_snapshots.length >= 3);
  assert.deepEqual(validateV11EventOrdering(state), []);
});

test("agent-backed failed gateway turn is visible but cannot satisfy acceptance", async () => {
  const state = await createAgentBackedState({ fixture: fixture("mission_tui_state_80x24.json") });
  applyGatewaySessionStarted(state, {
    session_id: "sess_failed",
    model: "fake-model",
    backend: "simple"
  }, "2026-06-09T00:00:00.000Z");
  const fakeClient = {
    async startTurn() {
      return {
        session_id: "sess_failed",
        turn_id: "turn_failed",
        trace_id: "trace_failed",
        final_text: "Error calling LLM: Connection error.",
        events: [
          { type: "turn.started", session_id: "sess_failed", turn_id: "turn_failed", item_id: "event_failed_1", timestamp: "2026-06-09T00:00:01.000Z", data: { trace_id: "trace_failed" } },
          { type: "turn.failed", session_id: "sess_failed", turn_id: "turn_failed", item_id: "event_failed_2", timestamp: "2026-06-09T00:00:02.000Z", data: { trace_id: "trace_failed", message: "Error calling LLM: Connection error." } }
        ]
      };
    }
  };
  const result = await submitAgentBackedTurn(
    state,
    fakeClient,
    "请测试失败 turn 不应通过验收",
    { now: "2026-06-09T00:00:00.000Z" }
  );
  assert.equal(result.status, "FAIL");
  assert.equal(result.gateway_turn_started, true);
  assert.equal(result.gateway_turn_completed, false);
  assert.equal(result.gateway_turn_failed, true);
  assert.notDeepEqual(state.v11_event_log, []);
  assert.equal(state.v11_event_log.some((event) => event.event_type === "turn.failed"), true);
  assert.equal(state.interactive_session.phase, "failed");
  assert.deepEqual(validateMissionTuiState(state), []);
});

test("V11 event ordering rejects a turn event before input", () => {
  const state = createInteractiveState(fixture("mission_tui_state_80x24.json"));
  state.v11_event_log = [
    { event_type: "turn.started", turn_id: "turn_bad", timestamp: "2026-06-09T00:00:00.000Z" },
    { event_type: "input.received", turn_id: null, timestamp: "2026-06-09T00:00:01.000Z" }
  ];
  assert.match(validateV11EventOrdering(state).join("\n"), /input\.received must precede/);
});

test("V11 slash commands inspect state without durable mutation", () => {
  const state = createInteractiveState(fixture("mission_tui_state_120x40.json"));
  state.interactive_session = {
    ...(state.interactive_session || {}),
    phase: "ready",
    session_id: "test-session",
    turn_id: "test-turn",
    trace_id: "test-trace",
    provider_mode: "provider-backed",
    trace: [{ event: "turn.started", message: "started" }]
  };

  const commands = [
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
  for (const command of commands) {
    const result = applySlashCommand(state, command, { now: "2026-06-10T00:00:00Z" });
    assert.equal(result.handled, true);
    assert.equal(result.status, "PASS");
  }
  const invalid = applySlashCommand(state, "/bad_command", { now: "2026-06-10T00:00:00Z" });
  assert.equal(invalid.handled, true);
  assert.equal(invalid.status, "FAIL");
  const text = JSON.stringify(state.transcript_items);
  assert.match(text, /WorkflowDiff/);
  assert.match(text, /确认前不会 apply\/publish\/run/);
  assert.match(text, /未知命令/);
  assert.doesNotMatch(text, /auto_apply_workflowdiff/);
  assert.equal(state.runtime_truth_boundary, "tui_read_model_not_runtime_truth");
  assert.deepEqual(validateMissionTuiState(state), []);
});

test("V11-3 workflow timeline acceptance generates bounded evidence", () => {
  const result = generateV113Acceptance();
  assert.equal(result.status, "PASS");
  assert.equal(result.workflow_timeline_rendered, true);
  assert.equal(result.required_states_present, true);
  assert.equal(result.confirmation_required, true);
  assert.equal(result.confirmation_state_visible, true);
  assert.equal(result.run_blocked_before_confirmation, true);
  assert.equal(result.durable_mutation_before_confirmation, false);
  assert.equal(result.runtime_backed, false);
  assert.equal(fs.existsSync(path.join(ROOT, "docs/design/V11.x/evidence/v11-3-workflow-timeline/acceptance-data.json")), true);
  assert.equal(fs.existsSync(path.join(ROOT, "docs/design/V11.x/evidence/v11-3-workflow-timeline/timeline-transcript.txt")), true);
});

test("V11-4 station and Agent inspector acceptance generates bounded evidence", () => {
  const result = generateV114Acceptance();
  assert.equal(result.status, "PASS");
  assert.ok(result.station_count >= 5);
  assert.equal(result.station_agent_fields_visible, true);
  assert.equal(result.agent_executor_ready_claim, false);
  assert.equal(fs.existsSync(path.join(ROOT, "docs/design/V11.x/evidence/v11-4-station-agent-inspector/agent-projection.json")), true);
});

test("V11-5 tool and permission acceptance shows risk and denial", () => {
  const result = generateV115Acceptance();
  assert.equal(result.status, "PASS");
  assert.equal(result.tool_lifecycle_visible, true);
  assert.equal(result.permission_denial_visible, true);
  assert.equal(result.risk_and_sandbox_visible, true);
  assert.equal(result.unrestricted_actions_introduced, false);
});

test("V11-6 preview acceptance shows refs without raw content", () => {
  const result = generateV116Acceptance();
  assert.equal(result.status, "PASS");
  assert.equal(result.artifact_refs_visible, true);
  assert.equal(result.quality_refs_visible, true);
  assert.equal(result.evidence_refs_visible, true);
  assert.deepEqual(result.raw_content_leak_hits, []);
});

test("V11-7 HTML explainer acceptance can validate supporting-only export without screenshot side effect", () => {
  const result = generateV117Acceptance({ captureScreenshot: false, writeEvidence: false });
  assert.equal(result.html_supporting_only, true);
  assert.equal(result.evidence_refs_present, true);
  assert.equal(result.html_replaces_runtime_evidence, false);
  assert.equal(fs.existsSync(path.join(ROOT, "docs/design/V11.x/evidence/v11-7-live-session-html-explainer/index.html")), true);
});

test("V11-8 user scenario matrix covers required scenarios without planning-only runtime evidence", () => {
  const result = generateV118Acceptance();
  assert.equal(result.status, "PASS");
  assert.equal(result.scenario_count, 6);
  assert.equal(result.pass_count, 6);
  assert.equal(result.planning_docs_as_runtime_evidence, false);
  assert.ok(result.runtime_backed_scenario_count >= 4);
});

test("V11-9 final acceptance aggregates V11 evidence without forbidden final claims", () => {
  generateV117Acceptance();
  const result = generateV119Acceptance();
  assert.equal(result.status, "PASS");
  assert.equal(result.stage_count, 9);
  assert.deepEqual(result.missing_stages, []);
  assert.deepEqual(result.failed_stages, []);
  assert.equal(result.provider_backed_cli_turn_evidence, true);
  assert.equal(result.user_scenario_matrix_pass, true);
  assert.equal(result.no_false_green_scan, "PASS");
  assert.equal(result.redaction_scan, "PASS");
  assert.equal(result.drawio_xml, "PASS");
});

test("dotenv parser supports local V10 provider configuration without exposing secret values", () => {
  const parsed = parseDotenv("DEEPSEEK_API_KEY=secret\nMINIMAX_API_KEY='mini-secret'\n# comment\nV10_AGENT_TUI_MODEL=deepseek-chat\n");
  assert.equal(parsed.DEEPSEEK_API_KEY, "secret");
  assert.equal(parsed.MINIMAX_API_KEY, "mini-secret");
  assert.equal(parsed.V10_AGENT_TUI_MODEL, "deepseek-chat");
});

test("dotenv loader skips empty and placeholder provider keys", () => {
  const tmpDir = fs.mkdtempSync(path.join(ROOT, ".tmp-v10-dotenv-"));
  try {
    fs.writeFileSync(
      path.join(tmpDir, ".env.v10-llm.local"),
      "DEEPSEEK_API_KEY=your-deepseek-api-key-here\nMINIMAX_API_KEY=\nV10_AGENT_TUI_MODEL=deepseek-chat\n",
      "utf8"
    );
    const loaded = loadDotenvEnv({ cwd: tmpDir, files: [".env.v10-llm.local"] });
    assert.equal(loaded.env.DEEPSEEK_API_KEY, undefined);
    assert.equal(loaded.env.MINIMAX_API_KEY, undefined);
    assert.equal(loaded.env.V10_AGENT_TUI_MODEL, "deepseek-chat");
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
});

test("interactive multi-agent discussion input is visible in current viewport", () => {
  const state = createInteractiveState(fixture("mission_tui_state_120x40.json"));
  applyInteractiveInput(
    state,
    "我想做一个多Agent的工作流，期望可以实现对同一个话题的不同角度讨论，最后有一个Agent能对讨论做出总结，要求至少执行三四轮讨论",
    "2026-06-09T00:00:00.000Z"
  );
  const output = renderMissionTui(state, { columns: 120, rows: 40 });
  assert.match(output, /phase:awaiting_confirmation/);
  assert.match(output, /多Agent/);
  assert.match(output, /Stoic Perspective Agent/);
  assert.match(output, /Socratic Question Agent/);
  assert.match(output, /Pragmatist Agent/);
  assert.match(output, /Summary And Quality Agent/);
  assert.match(output, /4 轮/);
  assert.match(output, /对话记录|讨论/);
  assert.match(output, /确认前不会 apply \/ publish \/ run/);
  assert.match(output, /\/history/);
  const diff = state.transcript_items.find((item) => item.id === state.selected_item_id);
  assert.equal(diff.durable_mutation, false);
  assert.deepEqual(validateMissionTuiState(state), []);
});
