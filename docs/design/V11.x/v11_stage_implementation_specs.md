# V11 Stage Implementation Specs

## Purpose

This document turns the V11 PRD and target architecture into stage-level
implementation specs. It is intentionally scoped to V11 real-time TUI
interaction and explainability. It does not authorize rebuilding inherited
runtime/evidence/governance planes.

## Global Stage Evidence Rules

- Gray items in the drawio are inherited and must not be rebuilt.
- Yellow items may be modified or strengthened.
- Orange-red items are new V11 implementation scope.
- `MissionTuiState` is display truth only.
- GatewayService remains the only session/turn boundary.
- Runtime-backed PASS requires runtime or provider-backed evidence, not
  planning docs, concept images or report-only screenshots.
- Failed, denied, blocked and timeout states must be visible and cannot satisfy
  completed acceptance.
- `V11-N complete` cannot be claimed unless all earlier V11 stages are PASS or
  explicitly accepted as bounded non-blocking with evidence.
- Final V11 requires at least one provider-backed CLI turn. Runtime fixtures may
  support bounded scenarios; TUI read-model fixtures only prove rendering.
- HTML explainer is always supporting-only and cannot replace runtime evidence.

## V11-0: Architecture Contract And Boundary Freeze

Implementation scope:

- Freeze architecture change classification.
- Align PRD, target architecture, architecture contract, gap analysis, drawio,
  development plan and acceptance gate.
- Validate drawio XML.

Inputs:

- V10 baseline evidence.
- V4-V9 inherited runtime/evidence/governance docs.
- `v11_current_gap_analysis.drawio`.

Outputs:

- Accepted architecture contract.
- Updated drawio with gray/yellow/orange-red change classification.
- Document audit result.

Acceptance:

- Each target component is classified as inherited, modified or new.
- No gray runtime plane is treated as V11 implementation scope.
- Drawio XML validates.

Stop conditions:

- V11 documents imply rebuilding GatewayService, controlled executor,
  WorkflowStore, Artifact Store or Evidence Chain.
- Runtime truth boundary is unclear.

## V11-1: Real-Time TUI Event Stream

Implementation scope:

- Add event emission for immediate user input acknowledgement.
- Add visible phase changes for session start, turn start, agent running,
  streaming, failed, blocked and completed states.
- Add a reducer path from Gateway/local events into `MissionTuiState`.
- Ensure failed Gateway turns are visible and cannot pass completion.

Inputs:

- Existing `apps/mission-tui` shell and Gateway bridge.
- Gateway `session.start`, `turn.start` and event records.
- `TuiRuntimeEvent` contract.

Outputs:

- Real-time event reducer.
- Visible status line update after user input.
- CLI transcript and JSON evidence.
- `events.jsonl` and `tui-state-snapshots.json`.

Acceptance:

- User presses enter and sees a visible state change without silent wait.
- Provider-backed turn shows session, turn, trace, provider mode and final
  status.
- Failed provider turn shows failed state and trace.
- No runtime truth writes are introduced.
- `input.received` appears before related `turn.started`.
- `turn.failed` is never counted as completed for the same turn.

Stop conditions:

- TUI waits for final result before showing any running state.
- `turn.failed` is counted as completed.
- Gateway is bypassed.

## V11-2: Composer, Slash Commands And Keyboard UX

Implementation scope:

- Improve command parser and command help.
- Add discoverable `/help`, `/status`, `/stations`, `/station <id>`,
  `/evidence`, `/diff`, `/trace`, `/quality`, `/artifacts`, `/explain`,
  `/retry`, `/revise`, `/exit`.
- Preserve input history and invalid command feedback.

Inputs:

- Existing command parser.
- `SlashCommandInvocation` contract.
- `AvailableAction` and `ForbiddenActionReason` projections.

Outputs:

- Command transcript.
- Invalid-command evidence.
- Keyboard shortcut/help evidence.

Acceptance:

- Commands are discoverable from `/help`.
- Invalid command produces visible error.
- `/retry` and `/revise` do not hide previous failed or rejected attempts.
- Commands cannot apply/publish/run durable changes directly.

Stop conditions:

- Slash command performs a durable mutation.
- Invalid command silently no-ops.

## V11-3: Workflow State Timeline

Implementation scope:

- Render timeline states from `WorkflowStateTimeline`.
- Bind timeline to WorkflowSpec, WorkflowDiff, confirmation, runtime report and
  evidence refs.
- Show blockers and forbidden reasons on timeline.

Inputs:

- V4 WorkflowSpec / WorkflowDiff / RuntimeReport / EvidenceChain projections.
- V9 runtime fixture refs where available.

Outputs:

- Timeline transcript.
- Timeline JSON evidence.

Acceptance:

- Timeline shows goal/spec/diff/confirmation/run/evidence states.
- WorkflowDiff cannot auto apply, publish or run.
- Blocked states remain visible.

Stop conditions:

- Timeline implies runtime execution when only planning evidence exists.
- Confirmation state is skipped before mutation.

## V11-4: Station/Agent Inspector

Implementation scope:

- Render station and Agent details from inherited V8/V9 Station Agent evidence.
- Show role, goal, memory summary, tools, skills, MCP refs, attempt, output,
  quality and evidence refs.
- Keep evidence scope visible.

Inputs:

- V8 Station Agent descriptors.
- V9 orchestration and user scenario evidence.
- `StationAgentProjection` contract.

Outputs:

- Station inspector transcript.
- Agent projection JSON evidence.

Acceptance:

- Each visible station has station id, status, Agent role and evidence refs.
- Tools, skills and MCP refs are visible when present.
- Inspector does not claim production Agent executor readiness.

Stop conditions:

- Fixture evidence is shown as real runtime without scope.
- Agent projection is treated as Agent executor readiness.

## V11-5: Tool Execution And Permission Blocks

Implementation scope:

- Render tool lifecycle blocks.
- Render permission, denied and forbidden-reason blocks.
- Show risk, sandbox, policy/capability decision and evidence refs.

Inputs:

- V6/V9 controlled executor, policy and evidence refs.
- `ToolPermissionBlock` contract.

Outputs:

- Tool started/completed/failed blocks.
- Permission and denied blocks.
- Negative fixture evidence.

Acceptance:

- Tool lifecycle is visible.
- Permission-required and denied states are not hidden.
- Risk and sandbox are visible.
- No unrestricted connector, external LLM, git commit, git push or production
  deploy action is introduced.

Stop conditions:

- Tool block hides risk or sandbox.
- Permission UI grants approval by display alone.

## V11-6: Output, Quality And Evidence Preview

Implementation scope:

- Render output, quality and evidence preview from redacted refs.
- Show evidence scope, runtime backing, provider backing and redaction status.
- Link previews to runtime reports and evidence chains.

Inputs:

- V4 Evidence Chain and Runtime Report.
- V9 evidence packages and user scenario artifacts.

Outputs:

- Preview transcript.
- Evidence preview JSON.
- Redaction scan.

Acceptance:

- Artifact refs, quality refs and evidence refs are visible.
- Raw prompt, raw file content, raw provider payload, raw connector payload,
  raw token, raw secret and raw artifact content do not appear.
- HTML or concept image is not counted as runtime evidence.

Stop conditions:

- Raw content leaks into preview or evidence.
- Evidence scope is missing.

## V11-7: HTML Explainer From Live Session

Implementation scope:

- Generate a supporting HTML explainer from live-session evidence.
- Include architecture, state, station, tool, output, quality and evidence
  sections.
- Mark HTML as supporting only.

Inputs:

- V11 stage evidence package.
- Controlled screenshot assets.

Outputs:

- HTML explainer.
- Playwright screenshot of explainer.
- JSON data source.

Acceptance:

- HTML is generated from evidence refs, not fabricated claims.
- HTML clearly states it is supporting, not runtime truth.
- Screenshot is controlled and does not expose desktop secrets.

Stop conditions:

- HTML report replaces CLI/runtime evidence.
- Screenshot includes unrelated desktop or secrets.

## V11-8: User Scenario End-To-End Validation

Implementation scope:

- Validate key user scenarios against V11 interaction and explainability.
- Preserve evidence scope for each scenario.

Required scenarios:

- Multi-Agent discussion with persona stations, multiple rounds and synthesis.
- Video storyboard workflow with storyboard refs and quality Agent review.
- Coding proposal workflow with plan, diff, sandbox test and review handoff.
- Local document workflow with scan progress, summaries, quality and evidence.
- Workflow revision with WorkflowDiff and confirm/revise/reject.
- Failure recovery with visible error, retry/revise options and trace.

Outputs:

- Scenario matrix JSON.
- CLI transcript refs.
- Evidence refs.
- Human-readable summary.

Acceptance:

- Each scenario is PASS or bounded PARTIAL/BLOCKED with reason.
- Runtime-backed scenarios cannot pass from planning docs.
- At least one scenario demonstrates failure visibility.

Stop conditions:

- Scenario PASS lacks evidence refs.
- Fixture-backed scenario is overclaimed as production runtime.

## V11-9: Final Acceptance

Implementation scope:

- Aggregate V11-0 through V11-8 evidence.
- Run No False Green and redaction scans.
- Validate drawio XML.
- Produce final review package.

Outputs:

- V11 final acceptance data.
- Final HTML review page.
- Claim scan.
- Redaction scan.
- Drawio validation result.

Acceptance:

- V11-1 through V11-8 evidence exists.
- No FAIL or unaccepted BLOCKED items.
- No forbidden positive claim outside safe context.
- Redaction PASS.
- Drawio XML PASS.

Allowed final claim:

`V11 complete: real-time explainable Mission TUI interaction baseline ready for review.`

Forbidden final interpretations:

- production ready,
- Agent executor ready,
- complete Workflow Studio ready,
- full multi-Agent orchestration ready,
- autonomous workflow editing ready,
- unrestricted terminal worker ready,
- production terminal automation ready,
- Codex/Claude Code parity complete.
