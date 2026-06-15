import readline from "node:readline";
import { renderMissionTui } from "./renderer.js";
import { loadState } from "./state.js";
import { appendWorkflowStateTimeline } from "./workflow-timeline.js";

export function createInteractiveState(fixturePath) {
  const state = loadState(fixturePath);
  return {
    ...state,
    status_line: {
      ...(state.status_line || {}),
      model: "local-interactive-no-provider",
      mode: "interactive"
    },
    composer_hint: "输入自然语言目标，或使用 /help /stations /evidence /diff /exit",
    interactive_session: {
      session_id: "v10-local-interactive-session",
      provider_backed: false,
      persisted: false,
      runtime_backed: false,
      focus_latest: true,
      phase: "waiting_input",
      trace: []
    }
  };
}

export function applyInteractiveInput(state, input, now = new Date().toISOString()) {
  const text = String(input || "").trim();
  if (!text) return state;
  recordTrace(state, "input_received", "已收到键盘输入", now);
  if (text === "/help") {
    setPhase(state, "help_open");
    appendAssistant(state, "可用命令：/stations 查看工位，/evidence 查看证据，/diff 查看待确认变更，/exit 退出。自然语言输入会创建本地 intent/proposal，不会自动运行。", now);
    return state;
  }
  if (text === "/stations") {
    setPhase(state, "stations_open");
    appendAssistant(state, summarizeStations(state), now);
    return state;
  }
  if (text === "/evidence") {
    setPhase(state, "evidence_open");
    appendAssistant(state, `当前 evidence refs: ${(state.evidence_refs || []).join(", ") || "无"}`, now);
    return state;
  }
  if (text === "/diff") {
    setPhase(state, "proposal_ready");
    appendWorkflowDiff(state, now);
    return state;
  }
  if (text === "/trace") {
    setPhase(state, "trace_open");
    appendAssistant(state, summarizeTrace(state), now);
    return state;
  }
  if (text === "/history") {
    setPhase(state, "history_open");
    appendAssistant(state, `当前 transcript blocks: ${(state.transcript_items || []).length}。交互视图默认显示最新内容，历史内容已折叠以保证输入反馈可见。`, now);
    return state;
  }
  if (text === "/clear") {
    setPhase(state, "view_cleared");
    state.transcript_items = state.transcript_items.slice(-2);
    appendAssistant(state, "已清理当前视图，只保留最近上下文；这不会删除 runtime evidence。", now);
    return state;
  }
  setPhase(state, "captured");
  appendUser(state, text, now);
  recordTrace(state, "goal_captured", "自然语言目标已进入本地 intent/proposal 管线", now);
  setPhase(state, "planning");
  appendAssistant(state, `已捕获目标：${redactDisplayText(text)}。正在生成本地 WorkflowDiff proposal；当前不会 apply / publish / run。`, now);
  if (isMultiAgentDiscussionGoal(text)) {
    appendMultiAgentDiscussionProposal(state, text, now);
  } else {
    appendPlan(state, now);
    appendWorkflowDiff(state, now, { goalText: text });
  }
  appendWorkflowStateTimeline(state, text, { now });
  setPhase(state, "awaiting_confirmation");
  recordTrace(state, "proposal_ready", "WorkflowDiff proposal 已生成，等待用户确认或修改", now);
  return state;
}

export async function runInteractiveSession(options = {}) {
  const state = createInteractiveState(options.fixture);
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

  paint();
  for await (const line of rl) {
    if (line.trim() === "/exit") {
      rl.close();
      break;
    }
    applyInteractiveInput(state, line);
    paint();
  }
  return 0;
}

function appendUser(state, text, now) {
  state.transcript_items.push({
    id: `interactive-user-${state.transcript_items.length + 1}`,
    type: "user_message",
    status: "completed",
    created_at: now,
    redacted: true,
    text: redactDisplayText(text),
    scenario_id: "US-V10-live"
  });
}

function appendAssistant(state, text, now) {
  state.transcript_items.push({
    id: `interactive-assistant-${state.transcript_items.length + 1}`,
    type: "assistant_message",
    status: "completed",
    created_at: now,
    redacted: true,
    text,
    scenario_id: "US-V10-live"
  });
}

function appendPlan(state, now) {
  state.transcript_items.push({
    id: `interactive-plan-${state.transcript_items.length + 1}`,
    type: "plan_block",
    status: "completed",
    created_at: now,
    redacted: true,
    current_step_id: "draft-proposal",
    steps: [
      { id: "capture-goal", text: "捕获用户目标", status: "done" },
      { id: "draft-proposal", text: "生成 WorkflowDiff proposal", status: "done" },
      { id: "await-confirmation", text: "等待用户确认后才可进入运行", status: "pending" }
    ],
    scenario_id: "US-V10-live"
  });
}

function appendWorkflowDiff(state, now, options = {}) {
  state.selected_item_id = `interactive-diff-${state.transcript_items.length + 1}`;
  state.transcript_items.push({
    id: state.selected_item_id,
    type: "workflowdiff_block",
    status: "pending_confirmation",
    created_at: now,
    redacted: true,
    source: "user",
    durable_mutation: false,
    proposal_goal: options.goalText ? redactDisplayText(options.goalText) : "本地 WorkflowDiff proposal",
    affected_station_ids: options.affectedStationIds || ["station-intent", "station-review"],
    actions: ["confirm_proposal", "revise_proposal", "reject_proposal"],
    evidence_refs: ["docs/design/V10.x/evidence/v10-cli-local-validation/validation-summary.json"],
    scenario_id: "US-V10-live"
  });
}

function appendMultiAgentDiscussionProposal(state, text, now) {
  state.transcript_items.push({
    id: `interactive-plan-${state.transcript_items.length + 1}`,
    type: "plan_block",
    status: "proposal_ready",
    created_at: now,
    redacted: true,
    current_step_id: "await-confirmation",
    steps: [
      { id: "capture-topic", text: "捕获讨论主题和目标", status: "done" },
      { id: "create-personas", text: "创建 3 个不同视角的讨论 Agent", status: "done" },
      { id: "set-rounds", text: "设置 4 轮讨论：开场、反驳、澄清、综合", status: "done" },
      { id: "summarizer", text: "增加总结 Agent 输出共识、分歧和后续问题", status: "done" },
      { id: "await-confirmation", text: "等待用户确认后才可进入运行", status: "pending" }
    ],
    scenario_id: "US-V10-live"
  });
  for (const station of buildDiscussionStations(text)) {
    state.transcript_items.push({
      ...station,
      created_at: now,
      status: "proposed",
      redacted: true,
      scenario_id: "US-V10-live",
      evidence_refs: ["docs/design/V10.x/evidence/v10-cli-local-validation/validation-summary.json"]
    });
  }
  state.transcript_items.push({
    id: `interactive-output-${state.transcript_items.length + 1}`,
    type: "output_preview_block",
    status: "proposal_ready",
    created_at: now,
    redacted: true,
    preview_text: "预计产出：4 轮多 Agent 对话记录、每轮观点差异表、总结 Agent 的共识/分歧/下一步建议。当前只是 proposal，未运行真实 Agent。",
    artifact_refs: ["artifact-ref://v10/proposed-roman-forum-discussion"],
    quality_refs: ["quality-ref://v10/discussion-round-count-and-summary-agent"],
    evidence_refs: ["docs/design/V10.x/evidence/v10-cli-local-validation/validation-summary.json"],
    scenario_id: "US-V10-live"
  });
  appendWorkflowDiff(state, now, {
    affectedStationIds: ["station-stoic", "station-socratic", "station-pragmatist", "station-summarizer"],
    goalText: text
  });
  appendAssistant(state, "等待确认：已生成 Stoic Perspective Agent / Socratic Question Agent / Pragmatist Agent / Summary And Quality Agent。输入 confirm_proposal 确认，revise_proposal 修改，reject_proposal 放弃；当前 proposal 不会自动运行。", now);
}

function buildDiscussionStations(text) {
  const topic = redactDisplayText(text).slice(0, 72);
  return [
    {
      id: "station-stoic",
      type: "station_block",
      agent_role: "Stoic Perspective Agent",
      agent_goal: `从斯多葛主义视角讨论：${topic}`,
      tools: ["persona.reason", "discussion.round"],
      skills: ["philosophy-dialogue", "counterargument"]
    },
    {
      id: "station-socratic",
      type: "station_block",
      agent_role: "Socratic Question Agent",
      agent_goal: "通过追问澄清概念、前提和论证漏洞",
      tools: ["persona.question", "discussion.challenge"],
      skills: ["questioning", "dialogue-synthesis"]
    },
    {
      id: "station-pragmatist",
      type: "station_block",
      agent_role: "Pragmatist Agent",
      agent_goal: "从可执行方案、影响和权衡角度提出现实判断",
      tools: ["impact.analysis", "tradeoff.map"],
      skills: ["practical-reasoning"]
    },
    {
      id: "station-summarizer",
      type: "station_block",
      agent_role: "Summary And Quality Agent",
      agent_goal: "汇总三四轮讨论，输出共识、分歧、证据缺口和可行动建议",
      tools: ["discussion.summarize", "quality.check"],
      skills: ["synthesis", "quality-review"]
    }
  ];
}

function summarizeStations(state) {
  const stations = (state.transcript_items || [])
    .filter((item) => item.type === "station_block")
    .map((item) => `${item.id}: ${item.agent_role} / ${item.agent_goal}`)
    .slice(0, 8);
  return stations.length ? `当前工位：${stations.join("；")}` : "当前没有 station block。";
}

function redactDisplayText(text) {
  return String(text)
    .replace(/Bearer\s+[A-Za-z0-9._-]+/g, "Bearer [redacted]")
    .replace(/sk-[A-Za-z0-9._-]+/g, "sk-[redacted]");
}

function isMultiAgentDiscussionGoal(text) {
  return /多\s*Agent|多智能体|讨论|不同角度|总结|三四轮|4\s*轮|四轮/.test(text);
}

function setPhase(state, phase) {
  state.interactive_session = {
    ...(state.interactive_session || {}),
    focus_latest: true,
    phase
  };
}

function recordTrace(state, event, message, now) {
  state.interactive_session = state.interactive_session || {};
  state.interactive_session.trace = state.interactive_session.trace || [];
  state.interactive_session.trace.push({ event, message, created_at: now });
}

function summarizeTrace(state) {
  const trace = state.interactive_session?.trace || [];
  if (!trace.length) return "当前没有 trace 事件。";
  return trace.map((item, index) => `${index + 1}. ${item.event}: ${item.message}`).join("；");
}
