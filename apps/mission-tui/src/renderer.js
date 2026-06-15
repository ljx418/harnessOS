const BLOCK_TITLES = {
  user_message: "用户",
  assistant_message: "助手",
  plan_block: "计划",
  tool_block: "工具",
  permission_block: "审批",
  station_block: "工位 / Agent",
  output_preview_block: "产物预览",
  workflow_timeline_block: "工作流状态线",
  workflowdiff_block: "WorkflowDiff",
  gateway_event_block: "Gateway 事件",
  error_block: "错误"
};

export function renderMissionTui(state, options = {}) {
  const columns = Number(options.columns || 80);
  const rows = Number(options.rows || 24);
  const headerLines = [renderStatusLine(state, columns), rule(columns)];
  const selectedSummary = renderSelectedSummary(state, columns);
  if (selectedSummary) {
    headerLines.push(selectedSummary);
    headerLines.push(rule(columns));
  }
  const transcriptLines = [];
  for (const item of state.transcript_items || []) {
    transcriptLines.push(...renderBlock(item, columns));
    transcriptLines.push("");
  }
  const footerLines = [rule(columns), renderComposer(state, columns)];
  return fitRows(headerLines, transcriptLines, footerLines, rows, {
    focusLatest: state.interactive_session?.focus_latest === true
  }).join("\n");
}

function renderSelectedSummary(state, columns) {
  const selected = (state.transcript_items || []).find((item) => item.id === state.selected_item_id);
  if (!selected) return "";
  if (selected.type === "workflowdiff_block") {
    return clip(`当前选中: WorkflowDiff proposal · 确认前不会 apply / publish / run · actions:${(selected.actions || []).join("/")}`, columns);
  }
  if (selected.type === "output_preview_block") {
    return clip(`当前选中: 产物预览 · ${(selected.quality_refs || []).length} quality refs · ${(selected.evidence_refs || []).length} evidence refs`, columns);
  }
  return clip(`当前选中: ${BLOCK_TITLES[selected.type] || selected.type} · ${selected.status}`, columns);
}

function renderStatusLine(state, columns) {
  const s = state.status_line || {};
  const session = state.interactive_session || {};
  const phase = `phase:${session.phase || "-"}`;
  const turn = session.turn_id ? `  turn:${session.turn_id}` : "";
  const gateway = session.gateway_backed ? `  gateway:${session.session_id || "-"}` : "";
  const providerMode = session.provider_mode ? `  provider_mode:${session.provider_mode}` : "";
  const provider = session.provider_backed === false ? "  provider:local" : "";
  return clip(`HarnessOS  ${s.workspace || "-"}  ${phase}${gateway}${turn}  mode:${s.mode || "-"}  model:${s.model || "-"}${provider}${providerMode}  sandbox:${s.sandbox || "-"}  evidence:${s.evidence_status || "-"}`, columns);
}

function renderComposer(state, columns) {
  const hint = state.composer_hint || "输入目标或 /command";
  return clip(`› ${hint}`, columns);
}

function renderBlock(item, columns) {
  const title = BLOCK_TITLES[item.type] || item.type;
  const heading = `▣ ${title}  ${item.status || ""}  ${item.id || ""}`;
  const body = [];
  switch (item.type) {
    case "user_message":
    case "assistant_message":
      body.push(item.text || "");
      break;
    case "plan_block":
      body.push(`当前步骤: ${item.current_step_id || "-"}`);
      for (const step of item.steps || []) {
        body.push(`${step.status === "done" ? "✓" : "·"} ${step.id}: ${step.text}`);
      }
      break;
    case "tool_block":
      body.push(`工具: ${item.tool_name}  风险:${item.risk_level}  sandbox:${item.sandbox}`);
      body.push(`命令预览: ${item.command_preview || "redacted-ref-only"}`);
      break;
    case "permission_block":
      body.push(`操作: ${item.operation}  风险:${item.risk_level}`);
      body.push(`选择: [${item.allow_label || "确认"}] [${item.deny_label || "拒绝"}]`);
      if (item.forbidden_reason_refs?.length) body.push(`禁止原因: ${item.forbidden_reason_refs.join(", ")}`);
      break;
    case "station_block":
      body.push(`Agent: ${item.agent_role}  目标: ${item.agent_goal}`);
      if (item.memory_summary) body.push(`Memory: ${item.memory_summary}`);
      if (item.attempt_ref) body.push(`Attempt: ${item.attempt_ref}`);
      if (item.tools?.length) body.push(`Tools: ${item.tools.join(", ")}`);
      if (item.skills?.length) body.push(`Skills: ${item.skills.join(", ")}`);
      if (item.mcp_refs?.length) body.push(`MCP: ${item.mcp_refs.join(", ")}`);
      if (item.output_ref) body.push(`Output: ${item.output_ref}`);
      if (item.quality_refs?.length) body.push(`Quality: ${item.quality_refs.join(", ")}`);
      break;
    case "output_preview_block":
      body.push(`摘要: ${item.preview_text || "-"}`);
      body.push(`Artifacts: ${(item.artifact_refs || []).join(", ") || "-"}`);
      body.push(`Quality: ${(item.quality_refs || []).join(", ") || "-"}`);
      break;
    case "workflow_timeline_block":
      body.push(`目标: ${item.goal_ref || "-"}`);
      body.push(`确认门: ${item.confirmation_required === true ? "需要用户确认" : "未要求确认"}`);
      for (const entry of item.timeline || []) {
        const marker = entry.status === "done" ? "✓" : entry.status === "blocked" ? "!" : "·";
        const reason = entry.blocked_reason ? ` · ${entry.blocked_reason}` : "";
        body.push(`${marker} ${entry.state}: ${entry.label || entry.state} [${entry.status}]${reason}`);
      }
      break;
    case "workflowdiff_block":
      if (item.proposal_goal) body.push(`目标: ${item.proposal_goal}`);
      body.push(`变更: ${(item.affected_station_ids || []).join(", ")}`);
      body.push(`动作: ${(item.actions || []).join(" / ")}`);
      body.push("确认前不会 apply / publish / run");
      break;
    case "gateway_event_block":
      body.push(`事件: ${item.event_type || "-"}  session:${item.session_id || "-"}  turn:${item.turn_id || "-"}`);
      if (item.trace_id) body.push(`Trace: ${item.trace_id}`);
      if (item.backend) body.push(`Backend: ${item.backend}`);
      body.push(item.message || "");
      break;
    default:
      body.push(item.message || item.text || "");
  }
  if (item.evidence_scope) body.push(`Evidence scope: ${item.evidence_scope}`);
  if (item.evidence_refs?.length) body.push(`证据: ${item.evidence_refs.join(", ")}`);
  return [clip(heading, columns), ...body.map((line) => clip(`  ${line}`, columns))];
}

function rule(columns) {
  return "─".repeat(Math.min(columns, 120));
}

function clip(value, columns) {
  const text = String(value);
  if (text.length <= columns) return text;
  if (columns <= 1) return text.slice(0, columns);
  return `${text.slice(0, columns - 1)}…`;
}

function fitRows(headerLines, transcriptLines, footerLines, rows, options = {}) {
  const total = [...headerLines, ...transcriptLines, ...footerLines];
  if (total.length <= rows) return total;
  const availableTranscriptRows = Math.max(1, rows - headerLines.length - footerLines.length);
  if (options.focusLatest) {
    const visibleRows = Math.max(1, availableTranscriptRows - 1);
    const hiddenRows = Math.max(0, transcriptLines.length - visibleRows);
    const tail = transcriptLines.slice(-visibleRows);
    const folded = hiddenRows > 0 ? [`… 已折叠历史内容 ${hiddenRows} 行，可用 /history 查看`] : [];
    return [...headerLines, ...folded, ...tail, ...footerLines];
  }
  const visibleRows = Math.max(0, availableTranscriptRows - 1);
  return [...headerLines, ...transcriptLines.slice(0, visibleRows), "…", ...footerLines];
}
