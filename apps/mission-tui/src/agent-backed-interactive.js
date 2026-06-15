import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { GatewayStdioClient } from "./gateway-stdio-client.js";
import {
  appendGatewayError,
  appendGatewayWarning,
  applyGatewaySessionStarted,
  applyGatewayTurnResult,
  recordAgentRunning,
  recordInputReceived,
  validateV11EventOrdering
} from "./gateway-event-reducer.js";
import { renderMissionTui } from "./renderer.js";
import { validateMissionTuiState } from "./state.js";
import { createInteractiveState } from "./interactive.js";
import { loadDotenvEnv } from "./dotenv.js";
import { REPO_ROOT } from "./paths.js";

export async function createAgentBackedState(options = {}) {
  const state = createInteractiveState(options.fixture);
  const resolvedModel = options.model || process.env.V10_AGENT_TUI_MODEL || "gateway-default";
  state.status_line = {
    ...(state.status_line || {}),
    model: resolvedModel,
    mode: "agent-backed"
  };
  state.runtime_truth_boundary = "tui_read_model_not_runtime_truth";
  state.composer_hint = "正在连接 Gateway...";
  state.interactive_session = {
    ...(state.interactive_session || {}),
    gateway_backed: true,
    runtime_backed: true,
    provider_backed: false,
    provider_mode: "local-runtime",
    phase: "connecting",
    focus_latest: true
  };
  return state;
}

export async function connectGatewaySession(state, client, options = {}) {
  const now = options.now || new Date().toISOString();
  client.on("stderr-line", (line) => appendGatewayWarning(state, line));
  client.on("protocol-error", (event) => appendGatewayError(state, `Gateway protocol error: ${event.message}`));
  await client.initialize({});
  const session = await client.startSession({
    model: options.model || client.env?.V10_AGENT_TUI_MODEL || undefined,
    app_id: options.appId || "default",
    project_id: options.projectId || "v10",
    workspace_id: options.workspaceId || "local"
  });
  applyGatewaySessionStarted(state, session, now);
  return session;
}

export async function submitAgentBackedTurn(state, client, input, options = {}) {
  const now = options.now || new Date().toISOString();
  const text = String(input || "").trim();
  if (!text) return { status: "SKIPPED" };
  state.transcript_items.push({
    id: `gateway-user-${state.transcript_items.length + 1}`,
    type: "user_message",
    status: "completed",
    created_at: now,
    redacted: true,
    text: redactDisplayText(text),
    scenario_id: "US-V10-06"
  });
  state.interactive_session = {
    ...(state.interactive_session || {}),
    phase: "input_received",
    focus_latest: true
  };
  recordInputReceived(state, text, now);
  options.onStateChange?.(state, { phase: "input_received" });
  const sessionId = state.interactive_session?.session_id;
  if (!sessionId) {
    appendGatewayError(state, "Gateway session is not connected", now);
    return { status: "FAIL", error: "missing session_id" };
  }
  state.interactive_session.phase = "agent_running";
  recordAgentRunning(state, now);
  options.onStateChange?.(state, { phase: "agent_running" });
  try {
    const turnResult = await client.startTurn({
      session_id: sessionId,
      input: text,
      domain: options.domain || undefined
    });
    const summary = applyGatewayTurnResult(state, turnResult, { now });
    const ordering_errors = validateV11EventOrdering(state);
    const status = (
      summary.gateway_turn_started === true &&
      summary.gateway_turn_completed === true &&
      summary.gateway_turn_failed !== true &&
      summary.assistant_output_from_gateway === true &&
      ordering_errors.length === 0
    ) ? "PASS" : "FAIL";
    return { status, ...summary, ordering_errors };
  } catch (error) {
    appendGatewayError(state, error.message || String(error), now);
    const ordering_errors = validateV11EventOrdering(state);
    return { status: "FAIL", error: error.message || String(error), ordering_errors };
  }
}

export function applySlashCommand(state, input, options = {}) {
  const now = options.now || new Date().toISOString();
  const text = String(input || "").trim();
  if (!text.startsWith("/")) return { handled: false };
  appendCommandInput(state, text, now);
  const [command, ...args] = text.slice(1).split(/\s+/).filter(Boolean);
  const normalized = (command || "").toLowerCase();
  const handlers = {
    help: () => [
      "可用命令：/help /status /stations /station <id> /evidence /diff /trace /quality /artifacts /explain /retry /revise /session /exit",
      "命令只检查和生成提案，不会 apply / publish / run durable mutation。"
    ],
    status: () => [
      `phase=${state.interactive_session?.phase || "-"} session=${state.interactive_session?.session_id || "-"} turn=${state.interactive_session?.turn_id || "-"}`,
      `mode=${state.status_line?.mode || "-"} model=${state.status_line?.model || "-"} provider_mode=${state.interactive_session?.provider_mode || "-"}`
    ],
    session: () => [
      `session_id=${state.interactive_session?.session_id || "-"} turn_id=${state.interactive_session?.turn_id || "-"} trace_id=${state.interactive_session?.trace_id || "-"}`
    ],
    stations: () => stationBlocks(state).map((item) => `${item.id}: ${item.agent_role || "-"} · ${item.status || "-"}`),
    station: () => describeStation(state, args[0]),
    evidence: () => evidenceRefs(state),
    diff: () => diffSummaries(state),
    trace: () => traceSummaries(state),
    quality: () => qualityRefs(state),
    artifacts: () => artifactRefs(state),
    explain: () => [
      "Mission TUI 只呈现 display/read-model truth。",
      "Gateway Session/Turn 是 provider/runtime 入口。",
      "WorkflowDiff 在确认前不会 apply / publish / run。",
      "Evidence/Runtime Report/HTML explainer 都不能构造 runtime truth。"
    ],
    retry: () => [
      "已生成 retry proposal 说明：需要用户确认后才可进入受控 runtime。",
      "当前命令不会直接重新运行 station，也不会创建 durable mutation。"
    ],
    revise: () => [
      "已进入 revise proposal 说明：请继续输入修改目标。",
      "当前命令只修改前台意图，不会 apply / publish / run。"
    ]
  };
  const handler = handlers[normalized];
  if (!handler) {
    appendCommandOutput(state, {
      now,
      status: "failed",
      type: "error_block",
      message: `未知命令：/${normalized || ""}。输入 /help 查看可用命令。`
    });
    return { handled: true, status: "FAIL", command: normalized || "unknown" };
  }
  const lines = handler();
  appendCommandOutput(state, {
    now,
    status: "completed",
    type: "assistant_message",
    message: (Array.isArray(lines) && lines.length ? lines : ["暂无可展示内容。"]).join("\n")
  });
  state.interactive_session = {
    ...(state.interactive_session || {}),
    focus_latest: true
  };
  return { handled: true, status: "PASS", command: normalized };
}

export async function runAgentBackedInteractiveSession(options = {}) {
  const dotenv = resolveDotenv(options);
  const model = options.model || dotenv.env.V10_AGENT_TUI_MODEL || undefined;
  const state = await createAgentBackedState({ ...options, model });
  const client = new GatewayStdioClient({
    python: options.python,
    cwd: options.cwd || REPO_ROOT,
    timeoutMs: options.timeoutMs,
    env: dotenv.env
  });
  state.interactive_session.dotenv_loaded = dotenv.loaded;
  const columns = Number(options.columns || process.stdout.columns || 100);
  const rows = Number(options.rows || process.stdout.rows || 32);
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: true
  });
  const paint = () => {
    process.stdout.write("\x1Bc");
    process.stdout.write(`${renderMissionTui(state, { columns, rows })}\n`);
    process.stdout.write("> ");
  };
  try {
    await connectGatewaySession(state, client, { ...options, model });
  } catch (error) {
    appendGatewayError(state, error.message || String(error));
  }
  paint();
  for await (const line of rl) {
    if (line.trim() === "/exit") {
      rl.close();
      break;
    }
    if (line.trim().startsWith("/")) {
      applySlashCommand(state, line);
      paint();
      continue;
    }
    await submitAgentBackedTurn(state, client, line, {
      ...options,
      onStateChange: () => paint()
    });
    paint();
  }
  client.close();
  return 0;
}

export async function runAgentBackedOnceCli(options = {}) {
  const { state, result, errors } = await runAgentBackedOnce(options);
  const output = options.json
    ? JSON.stringify({ result, errors, state }, null, 2)
    : renderMissionTui(state, { columns: options.columns, rows: options.rows });
  if (options.out) {
    fs.mkdirSync(path.dirname(options.out), { recursive: true });
    fs.writeFileSync(options.out, `${output}\n`, "utf8");
  } else {
    console.log(output);
  }
  return result?.status === "PASS" && errors.length === 0 ? 0 : 1;
}

export async function runAgentBackedOnce(options = {}) {
  const dotenv = resolveDotenv(options);
  const model = options.model || dotenv.env.V10_AGENT_TUI_MODEL || undefined;
  const state = await createAgentBackedState({ ...options, model });
  const client = new GatewayStdioClient({
    python: options.python,
    cwd: options.cwd || REPO_ROOT,
    timeoutMs: options.timeoutMs,
    env: dotenv.env
  });
  state.interactive_session.dotenv_loaded = dotenv.loaded;
  let result;
  try {
    await connectGatewaySession(state, client, { ...options, model });
    result = await submitAgentBackedTurn(state, client, options.agentBackedOnce, options);
  } finally {
    client.close();
  }
  const errors = validateMissionTuiState(state);
  return { state, result, errors, stderr_lines: client.stderrLines };
}

function resolveDotenv(options = {}) {
  const files = options.dotenv
    ? [options.dotenv]
    : [".env.v10-llm.local"];
  return loadDotenvEnv({ cwd: options.cwd || REPO_ROOT, files });
}

function appendCommandInput(state, text, now) {
  state.transcript_items.push({
    id: `slash-user-${state.transcript_items.length + 1}`,
    type: "user_message",
    status: "completed",
    created_at: now,
    redacted: true,
    text,
    scenario_id: "US-V11-02"
  });
}

function appendCommandOutput(state, options) {
  const item = {
    id: `slash-output-${state.transcript_items.length + 1}`,
    type: options.type,
    status: options.status,
    created_at: options.now,
    redacted: true,
    scenario_id: "US-V11-02"
  };
  if (options.type === "error_block") item.message = options.message;
  else item.text = options.message;
  state.transcript_items.push(item);
}

function stationBlocks(state) {
  return (state.transcript_items || []).filter((item) => item.type === "station_block");
}

function describeStation(state, stationId) {
  const item = stationBlocks(state).find((station) => station.id === stationId);
  if (!item) return [`未找到工位：${stationId || "-"}`];
  return [
    `${item.id}: ${item.agent_role || "-"}`,
    `目标：${item.agent_goal || "-"}`,
    `Tools：${(item.tools || []).join(", ") || "-"}`,
    `Skills：${(item.skills || []).join(", ") || "-"}`,
    `MCP：${(item.mcp_refs || []).join(", ") || "-"}`,
    `证据：${(item.evidence_refs || []).join(", ") || "-"}`
  ];
}

function evidenceRefs(state) {
  const refs = new Set(state.evidence_refs || []);
  for (const item of state.transcript_items || []) {
    for (const ref of item.evidence_refs || []) refs.add(ref);
  }
  return [...refs].slice(0, 24);
}

function diffSummaries(state) {
  const diffs = (state.transcript_items || []).filter((item) => item.type === "workflowdiff_block");
  return diffs.map((item) => `${item.id}: ${item.status} · actions=${(item.actions || []).join("/") || "-"} · 确认前不会 apply/publish/run`);
}

function traceSummaries(state) {
  const trace = state.interactive_session?.trace || [];
  return trace.map((item, index) => `${index + 1}. ${item.event}: ${item.message}`);
}

function qualityRefs(state) {
  const refs = new Set();
  for (const item of state.transcript_items || []) {
    for (const ref of item.quality_refs || []) refs.add(ref);
  }
  return [...refs];
}

function artifactRefs(state) {
  const refs = new Set();
  for (const item of state.transcript_items || []) {
    for (const ref of item.artifact_refs || []) refs.add(ref);
  }
  return [...refs];
}

function redactDisplayText(text) {
  return String(text || "")
    .replace(/Bearer\s+[A-Za-z0-9._-]+/g, "Bearer [redacted]")
    .replace(/sk-[A-Za-z0-9._-]+/g, "sk-[redacted]");
}
