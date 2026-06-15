const REDACTION_PATTERNS = [
  [/Bearer\s+[A-Za-z0-9._-]+/g, "Bearer [redacted]"],
  [/sk-[A-Za-z0-9._-]+/g, "sk-[redacted]"],
  [/api[_-]?key\s*[:=]\s*['"]?[^'"\s]+/gi, "api_key=[redacted]"]
];

export function applyGatewaySessionStarted(state, sessionResult, now = new Date().toISOString()) {
  recordV11Event(state, {
    event_type: "gateway.session.started",
    source: "gateway",
    session_id: sessionResult.session_id,
    turn_id: null,
    payload_ref: "gateway-session-started"
  }, now);
  state.status_line = {
    ...(state.status_line || {}),
    mode: "agent-backed",
    model: sessionResult.model || state.status_line?.model || "-",
    evidence_status: "gateway-session"
  };
  state.composer_hint = "输入自然语言目标，或使用 /trace /session /exit";
  state.interactive_session = {
    ...(state.interactive_session || {}),
    session_id: sessionResult.session_id,
    turn_id: null,
    provider_backed: sessionResult.backend === "openharness",
    gateway_backed: true,
    runtime_backed: true,
    persisted: true,
    backend: sessionResult.backend || "unknown",
    provider_mode: providerModeFromBackend(sessionResult.backend),
    phase: "ready",
    focus_latest: true,
    trace: [
      ...(state.interactive_session?.trace || []),
      {
        event: "gateway_session_started",
        message: `Gateway session ${sessionResult.session_id} started via ${sessionResult.backend || "unknown"} backend`,
        created_at: now
      }
    ]
  };
  appendTraceBlock(state, {
    id: "gateway-session-started",
    status: "completed",
    created_at: now,
    message: `Gateway session started: ${sessionResult.session_id}`,
    session_id: sessionResult.session_id,
    backend: sessionResult.backend || "unknown",
    event_type: "gateway.session.started"
  });
  return state;
}

export function applyGatewayTurnResult(state, turnResult, options = {}) {
  const now = options.now || new Date().toISOString();
  const events = Array.isArray(turnResult.events) ? turnResult.events : [];
  const eventTypes = events.map((event) => event.type);
  const hasFailed = eventTypes.includes("turn.failed");
  for (const event of events) {
    recordV11Event(state, {
      event_type: normalizeV11EventType(event.type),
      source: "gateway",
      session_id: event.session_id || turnResult.session_id,
      turn_id: event.turn_id || turnResult.turn_id,
      payload_ref: event.item_id || `gateway-event-${state.v11_event_log?.length || 0}`
    }, event.timestamp || now);
  }
  const providerMode = providerModeFromTurn(turnResult, state.interactive_session?.backend);
  state.status_line = {
    ...(state.status_line || {}),
    mode: "agent-backed",
    model: state.status_line?.model || turnResult.model || "-"
  };
  state.interactive_session = {
    ...(state.interactive_session || {}),
    session_id: turnResult.session_id,
    turn_id: turnResult.turn_id,
    trace_id: turnResult.trace_id,
    provider_mode: providerMode,
    provider_backed: providerMode === "provider-backed",
    gateway_backed: true,
    runtime_backed: true,
    phase: hasFailed ? "failed" : "completed",
    focus_latest: true,
    trace: [
      ...(state.interactive_session?.trace || []),
      ...events.map((event) => ({
        event: event.type,
        message: eventMessage(event),
        created_at: event.timestamp || now
      }))
    ]
  };
  for (const event of events) {
    appendTraceBlock(state, {
      id: event.item_id || `gateway-event-${state.transcript_items.length + 1}`,
      status: event.type === "turn.failed" ? "failed" : "completed",
      created_at: event.timestamp || now,
      message: eventMessage(event),
      session_id: event.session_id,
      turn_id: event.turn_id,
      trace_id: event.data?.trace_id || turnResult.trace_id,
      event_type: event.type
    });
  }
  if (turnResult.final_text) {
    state.transcript_items.push({
      id: `gateway-assistant-${state.transcript_items.length + 1}`,
      type: "assistant_message",
      status: hasFailed ? "failed" : "completed",
      created_at: now,
      redacted: true,
      text: redactDisplayText(turnResult.final_text),
      scenario_id: "US-V10-06",
      evidence_refs: ["docs/design/V10.x/evidence/v10-8-agent-backed-tui/acceptance-data.json"]
    });
  }
  state.evidence_refs = Array.from(
    new Set([
      ...(state.evidence_refs || []),
      "docs/design/V10.x/evidence/v10-8-agent-backed-tui/acceptance-data.json"
    ])
  );
  recordV11StateSnapshot(state, now, `turn-result-${turnResult.turn_id || "unknown"}`);
  return {
    session_id: turnResult.session_id,
    turn_id: turnResult.turn_id,
    trace_id: turnResult.trace_id,
    event_types: eventTypes,
    provider_mode: providerMode,
    gateway_turn_started: eventTypes.includes("turn.started"),
    gateway_turn_completed: eventTypes.includes("turn.completed"),
    gateway_turn_failed: eventTypes.includes("turn.failed"),
    assistant_output_from_gateway: Boolean(turnResult.final_text)
  };
}

export function recordInputReceived(state, input, now = new Date().toISOString()) {
  recordV11Event(state, {
    event_type: "input.received",
    source: "user",
    session_id: state.interactive_session?.session_id || null,
    turn_id: state.interactive_session?.turn_id || null,
    payload_ref: `input-${(state.v11_event_log || []).length + 1}`
  }, now);
  appendTraceBlock(state, {
    id: `v11-input-received-${state.transcript_items.length + 1}`,
    status: "completed",
    created_at: now,
    message: "用户输入已收到，TUI 已进入运行状态。",
    session_id: state.interactive_session?.session_id,
    turn_id: state.interactive_session?.turn_id,
    event_type: "input.received",
    evidence_refs: ["docs/design/V11.x/evidence/v11-1-real-time-event-stream/acceptance-data.json"]
  });
  return state;
}

export function recordAgentRunning(state, now = new Date().toISOString()) {
  recordV11Event(state, {
    event_type: "agent.running",
    source: "local_ui",
    session_id: state.interactive_session?.session_id || null,
    turn_id: state.interactive_session?.turn_id || null,
    payload_ref: `agent-running-${(state.v11_event_log || []).length + 1}`
  }, now);
  appendTraceBlock(state, {
    id: `v11-agent-running-${state.transcript_items.length + 1}`,
    status: "running",
    created_at: now,
    message: "Gateway turn 请求已提交，等待运行时返回事件。",
    session_id: state.interactive_session?.session_id,
    turn_id: state.interactive_session?.turn_id,
    event_type: "agent.running",
    evidence_refs: ["docs/design/V11.x/evidence/v11-1-real-time-event-stream/acceptance-data.json"]
  });
  return state;
}

export function validateV11EventOrdering(state) {
  const events = state.v11_event_log || [];
  const errors = [];
  const firstInput = events.findIndex((event) => event.event_type === "input.received");
  const firstTurnStarted = events.findIndex((event) => event.event_type === "turn.started");
  if (firstInput === -1) errors.push("missing input.received");
  if (firstTurnStarted === -1) errors.push("missing turn.started");
  if (firstInput !== -1 && firstTurnStarted !== -1 && firstInput > firstTurnStarted) {
    errors.push("input.received must precede related turn.started");
  }
  const turnStartedById = new Map();
  for (const [index, event] of events.entries()) {
    if (!event.turn_id) continue;
    if (event.event_type === "turn.started") turnStartedById.set(event.turn_id, index);
    if (["assistant.delta", "tool.started", "turn.completed", "turn.failed"].includes(event.event_type)) {
      const startedIndex = turnStartedById.get(event.turn_id);
      if (startedIndex === undefined || startedIndex > index) {
        errors.push(`${event.event_type} must follow turn.started for ${event.turn_id}`);
      }
    }
  }
  return errors;
}

export function appendGatewayWarning(state, message, now = new Date().toISOString()) {
  appendTraceBlock(state, {
    id: `gateway-warning-${state.transcript_items.length + 1}`,
    status: "warning",
    created_at: now,
    message: redactDisplayText(message),
    event_type: "gateway.stderr"
  });
}

export function appendGatewayError(state, message, now = new Date().toISOString()) {
  state.interactive_session = {
    ...(state.interactive_session || {}),
    phase: "failed",
    focus_latest: true
  };
  state.transcript_items.push({
    id: `gateway-error-${state.transcript_items.length + 1}`,
    type: "error_block",
    status: "failed",
    created_at: now,
    redacted: true,
    message: redactDisplayText(message),
    scenario_id: "US-V10-06"
  });
}

function appendTraceBlock(state, block) {
  state.transcript_items.push({
    type: "gateway_event_block",
    redacted: true,
    scenario_id: "US-V10-06",
    evidence_refs: ["docs/design/V10.x/evidence/v10-8-agent-backed-tui/acceptance-data.json"],
    ...block
  });
}

function recordV11Event(state, event, now) {
  if (!Array.isArray(state.v11_event_log)) state.v11_event_log = [];
  const record = {
    schema_version: "v11.tui_runtime_event.v1",
    event_id: `v11-event-${state.v11_event_log.length + 1}`,
    timestamp: now,
    ...event
  };
  state.v11_event_log.push(record);
  recordV11StateSnapshot(state, now, record.event_id);
}

function recordV11StateSnapshot(state, now, eventId) {
  if (!Array.isArray(state.v11_state_snapshots)) state.v11_state_snapshots = [];
  state.v11_state_snapshots.push({
    event_id: eventId,
    timestamp: now,
    phase: state.interactive_session?.phase || "unknown",
    session_id: state.interactive_session?.session_id || null,
    turn_id: state.interactive_session?.turn_id || null,
    transcript_count: state.transcript_items?.length || 0
  });
}

function normalizeV11EventType(type) {
  if (type === "item.delta") return "assistant.delta";
  return type || "unknown";
}

function eventMessage(event) {
  if (event.type === "item.delta") return redactDisplayText(event.data?.text || "assistant delta");
  if (event.type === "turn.failed") return redactDisplayText(event.data?.message || "turn failed");
  if (event.type === "turn.completed") return "Gateway turn completed";
  if (event.type === "turn.started") return "Gateway turn started";
  return event.type || "gateway event";
}

function providerModeFromTurn(turnResult, backend) {
  const events = Array.isArray(turnResult.events) ? turnResult.events : [];
  if (events.some((event) => event.data?.mode === "mock")) return "demo-fallback";
  if (events.some((event) => event.data?.model && !event.data?.mode)) return "provider-backed";
  if (turnResult.final_text && !/demo mode|no LLM API key detected/i.test(turnResult.final_text)) {
    return "provider-backed";
  }
  return providerModeFromBackend(backend);
}

function providerModeFromBackend(backend) {
  if (backend === "openharness") return "provider-backed";
  if (backend === "simple") return "local-runtime";
  return "local-runtime";
}

function redactDisplayText(text) {
  return String(text || "").replace(REDACTION_PATTERNS[0][0], REDACTION_PATTERNS[0][1])
    .replace(REDACTION_PATTERNS[1][0], REDACTION_PATTERNS[1][1])
    .replace(REDACTION_PATTERNS[2][0], REDACTION_PATTERNS[2][1]);
}
