export const REQUIRED_WORKFLOW_TIMELINE_STATES = [
  "goal",
  "spec",
  "diff",
  "confirmation",
  "run",
  "runtime_report",
  "evidence"
];

export function buildWorkflowStateTimeline(goalText, options = {}) {
  const evidenceRef = options.evidenceRef || "docs/design/V11.x/evidence/v11-3-workflow-timeline/acceptance-data.json";
  const sanitizedGoal = redactInline(goalText || "用户自然语言目标");
  return {
    id: options.id || "v11-workflow-state-timeline",
    type: "workflow_timeline_block",
    status: "awaiting_confirmation",
    created_at: options.now || new Date().toISOString(),
    redacted: true,
    scenario_id: options.scenarioId || "US-V11-03",
    goal_ref: "goal-ref://v11/current-user-goal",
    workflow_spec_ref: "workflow-spec-ref://v11/proposed-spec",
    workflow_diff_ref: "workflow-diff-ref://v11/proposed-diff",
    runtime_report_ref: "runtime-report-ref://v11/pending-until-confirmed",
    evidence_refs: [evidenceRef],
    evidence_scope: "tui_read_model_fixture",
    confirmation_required: true,
    durable_mutation_before_confirmation: false,
    source: "user",
    timeline: [
      {
        state: "goal",
        label: `目标已捕获：${sanitizedGoal}`,
        status: "done",
        evidence_ref: evidenceRef
      },
      {
        state: "spec",
        label: "WorkflowSpec 草案已生成",
        status: "done",
        evidence_ref: "workflow-spec-ref://v11/proposed-spec"
      },
      {
        state: "diff",
        label: "WorkflowDiff proposal 已生成",
        status: "done",
        evidence_ref: "workflow-diff-ref://v11/proposed-diff"
      },
      {
        state: "confirmation",
        label: "等待用户 confirm / revise / reject",
        status: "awaiting_confirmation",
        blocked_reason: "durable mutation requires explicit user confirmation"
      },
      {
        state: "run",
        label: "工作流运行",
        status: "blocked",
        blocked_reason: "blocked until WorkflowDiff is confirmed"
      },
      {
        state: "runtime_report",
        label: "Runtime Report",
        status: "pending",
        blocked_reason: "no runtime report before run"
      },
      {
        state: "evidence",
        label: "Evidence Chain",
        status: "pending",
        blocked_reason: "evidence is recorded only after governed runtime action"
      }
    ]
  };
}

export function appendWorkflowStateTimeline(state, goalText, options = {}) {
  const timeline = buildWorkflowStateTimeline(goalText, options);
  state.transcript_items.push(timeline);
  state.workflow_state_timeline = timeline;
  return timeline;
}

export function summarizeWorkflowTimeline(timeline) {
  const states = new Set((timeline?.timeline || []).map((entry) => entry.state));
  const confirmation = (timeline?.timeline || []).find((entry) => entry.state === "confirmation");
  const run = (timeline?.timeline || []).find((entry) => entry.state === "run");
  return {
    has_required_states: REQUIRED_WORKFLOW_TIMELINE_STATES.every((state) => states.has(state)),
    confirmation_required: timeline?.confirmation_required === true,
    confirmation_state_visible: confirmation?.status === "awaiting_confirmation",
    run_blocked_before_confirmation: run?.status === "blocked",
    durable_mutation_before_confirmation: timeline?.durable_mutation_before_confirmation === true,
    evidence_scope: timeline?.evidence_scope || "unknown"
  };
}

function redactInline(value) {
  return String(value)
    .replace(/sk-[A-Za-z0-9_-]+/g, "[REDACTED_KEY]")
    .replace(/Bearer\s+[A-Za-z0-9._-]+/gi, "Bearer [REDACTED_TOKEN]")
    .slice(0, 120);
}
