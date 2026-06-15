# V10 Stage Implementation Specs

## Purpose

This document turns the V10 PRD, architecture and milestone plan into
stage-specific implementation packages. It is the canonical engineering handoff
for V10-1 through V10-9. It does not authorize skipping stage gates.

## Current Decision

V10 documentation supports full stage-by-stage development planning.

```text
proceed_to_v10_1_readiness_review=true
proceed_to_v10_1_implementation=conditional_after_readiness_acceptance
proceed_to_v10_2_implementation=false_until_v10_1_evidence_pass
proceed_to_v10_3_implementation=false_until_v10_2_evidence_pass
proceed_to_v10_8_implementation=next_candidate_after_design_acceptance
proceed_to_v10_final_acceptance=false_until_v10_1_to_v10_8_evidence_exists
```

## V10-1 React/Ink CLI-Native Mission Shell

### Scope

- Create `apps/mission-tui` as the HarnessOS-native terminal UI package.
- Render top status line, single-column transcript stream, bottom composer and
  slash command palette.
- Load fixture-backed `MissionTuiState` through a read-model adapter.

### Required Implementation Units

- `MissionTuiState` parser and redaction validator.
- Status line component.
- Transcript stream component.
- Bottom composer component.
- Slash command palette component.
- 80x24 and 120x40 terminal snapshot harness.

### Required Evidence

- Real TUI screenshot at 80x24.
- Real TUI screenshot at 120x40.
- Component tests for status line, transcript stream, composer and command
  palette.
- No OpenHarness primary product copy in user-facing V10 TUI.

### Stop Conditions

- Concept image or HTML explainer is presented as real TUI runtime screenshot.
- Composer is not visible at 80x24.
- Primary copy says OpenHarness instead of HarnessOS.

## V10-2 Tool / Permission / Plan Blocks

### Scope

- Render tool started/completed/failed blocks.
- Render permission prompts with allow/deny choices.
- Render plan/todo blocks with current step visibility.

### Required Implementation Units

- `tool_block` renderer.
- `permission_block` renderer.
- `plan_block` renderer.
- Forbidden reason renderer.
- Keyboard focus model for allow/deny/revise.

### Required Evidence

- Fixture render for tool, permission and plan states.
- Negative fixture where denied action lacks forbidden reason fails.
- Risk, sandbox, command preview and evidence refs visible.

### Stop Conditions

- Permission prompt hides forbidden reason.
- UI creates an approve decision without user confirmation.
- Tool block lacks evidence refs.

## V10-3 Workflow Explainability Inline Blocks

### Scope

- Render workflow, station and Agent explainability blocks from V9 evidence.
- Show Agent role, goal, memory refs, tools, skills, MCP refs and policy state.

### Required Implementation Units

- `station_block` renderer.
- Agent descriptor projection adapter.
- Evidence link opener.
- Expand/collapse model.

### Required Evidence

- Roman Forum fixture shows multiple persona Agent station blocks.
- Local Markdown fixture shows document-read station state and summary output.
- Every station block has evidence refs.

### Stop Conditions

- Station/Agent block lacks role or goal.
- Agent block presents unavailable tools/skills/MCP as active.
- Source evidence cannot be opened.

## V10-4 Station Output And Quality Preview

### Scope

- Show station output previews, artifact refs, quality refs and quality status.
- Support video storyboard, markdown summary and coding proposal previews.

### Required Implementation Units

- `output_preview_block` renderer.
- Artifact ref preview adapter.
- Quality result preview adapter.
- Empty/error preview states.

### Required Evidence

- Video storyboard fixture shows storyboard artifacts and quality Agent checks.
- Quality status links to evidence refs.
- Raw artifact content is not stored in TUI state.

### Stop Conditions

- Output preview shows raw artifact content where only redacted preview refs are
  allowed.
- Quality status is report-only without linked evidence.

## V10-5 Natural-Language WorkflowDiff Preview

### Scope

- Let user request workflow changes in natural language.
- Render WorkflowDiff proposal with confirm, revise and reject controls.
- Keep proposal-first behavior before any apply/publish/run action.

### Required Implementation Units

- Natural-language revision input handler.
- `workflowdiff_block` renderer.
- Confirm/revise/reject action model.
- Forbidden action display for auto-apply/publish/run.

### Required Evidence

- WorkflowDiff proposal fixture renders affected station ids and actions.
- Negative fixture with `auto_apply_workflowdiff` fails.
- No source=agent direct durable mutation path exists.

### Stop Conditions

- WorkflowDiff is applied before explicit confirmation.
- TUI exposes Apply/Publish/Run as hidden direct mutation controls.

## V10-6 Evidence HTML Explainer Generator

### Scope

- Generate supporting HTML explainer from `MissionTuiState` and evidence refs.
- Provide richer media/audit view for scenario review.

### Required Implementation Units

- HTML explainer generator.
- Evidence ref resolver.
- Scenario summary renderer.
- No False Green / redaction scan hooks.

### Required Evidence

- Generated HTML for at least one scenario from fixture state.
- HTML clearly marks itself as supporting evidence, not primary TUI.
- HTML links back to runtime/evidence refs.

### Stop Conditions

- HTML explainer is described as the primary workflow UI.
- HTML report is counted as real TUI screenshot.

## V10-7 User Onboarding And Read-Model UX Acceptance

### Scope

- Provide first-run onboarding, scenario presets and read-model UX acceptance board.
- Aggregate V10-1 through V10-6 evidence.

### Required Implementation Units

- First-run guide in TUI.
- `/help`, `/new`, `/plan`, `/stations`, `/evidence`, `/diff` command docs.
- Final acceptance data generator.
- User scenario acceptance report.

### Required Evidence

- V10-1 through V10-6 evidence summaries exist.
- All required user scenarios have PASS or accepted PARTIAL with explicit
  limitation.
- No False Green PASS.
- Redaction PASS.
- Drawio XML PASS.
- Explicit boundary that V10-7 is not Agent-backed chatbot proof.

### Stop Conditions

- Any required scenario is missing.
- Any forbidden claim appears outside safe context.
- Any real screenshot requirement is replaced by concept images.

## V10-8 Agent-Backed Chatbot TUI Bridge

### Scope

- Connect Mission TUI composer input to existing `GatewayService`.
- Create or resume a Gateway session.
- Submit user input through `turn.start`.
- Render live Gateway/Agent events as terminal blocks.
- Show phase, session id, turn id and provider/fallback mode.

### Required Implementation Units

- Gateway session adapter.
- Gateway turn submitter.
- Stdio JSONL client that spawns `./.venv/bin/python -m apps.gateway.stdio_server`.
- Event-to-block reducer for `turn.started`, assistant output,
  `turn.completed`, `turn.failed`, tool events and approval requests.
- Live state machine reducer.
- Streaming assistant block renderer.
- Runtime error block renderer.
- `/trace` and `/session` commands.
- Acceptance data generator proving Gateway-backed evidence.
- Negative validator that rejects local-parser-only evidence for V10-8.

### Required Evidence

- Real terminal screenshot before submit.
- Real terminal screenshot after submit showing Agent-backed state.
- Raw Gateway event transcript.
- Acceptance JSON with Gateway session/turn booleans.
- Negative evidence that fixture-only/local-parser output cannot pass V10-8.
- No False Green PASS.
- Redaction PASS.

### Stop Conditions

- TUI input is handled only by local parser but claimed as Agent-backed.
- No `session_id` or `turn_id` is visible for Agent-backed mode.
- `turn.started` is missing.
- Assistant output is template text but claimed as Gateway runtime output.
- Provider-backed claim appears without provider evidence.
- source=agent can directly perform durable mutation.

## V10-9 Final V10 UX Acceptance

### Scope

- Aggregate V10-1 through V10-8 evidence.
- Execute final user scenario matrix including US-V10-06.
- Freeze final allowed claim only after V10-8 PASS.

### Required Evidence

- V10-1 through V10-8 evidence packages.
- US-V10-01 through US-V10-06 PASS or accepted PARTIAL with explicit limitation.
- Agent-backed Gateway turn evidence for US-V10-06.
- No False Green PASS.
- Redaction PASS.
- Drawio XML PASS.

### Stop Conditions

- V10 final acceptance runs from V10-1..V10-7 read-model evidence only.
- V10-8 is missing, PARTIAL without accepted limitation, FAIL or BLOCKED.
- Any forbidden final interpretation appears as a positive claim.
