# V10-8 Agent-Backed Chatbot TUI Bridge Plan

## Purpose

V10-8 upgrades the Mission TUI from a fixture/read-model renderer into an
Agent-backed chatbot front end. The user types into the terminal composer, the
TUI submits the turn to the existing Gateway/Agent runtime, and the terminal
shows observable live state instead of silently simulating a proposal.

V10-8 does not introduce a new runtime authority. It connects the TUI to the
existing Gateway boundary and keeps durable mutation behind governed
confirmation paths.

The implementation-level bridge contract is controlled by
`v10_8_agent_gateway_adapter_engineering_design.md`.

## Current Gap

Current V10 implementation evidence proves:

- local CLI rendering,
- local stdin handling,
- fixture/read-model validation,
- local proposal generation,
- no auto apply / publish / run.

It does not prove:

- Agent-backed conversation,
- live Gateway turn state,
- streaming assistant deltas,
- runtime error visibility,
- approval/tool events from a real turn,
- provider-backed response unless an enabled provider is configured.

## Target User Experience

1. User starts Mission TUI.
2. TUI creates or resumes a Gateway session.
3. User enters a natural-language message in the bottom composer.
4. TUI immediately shows:
   - `phase:submitting`,
   - captured user message,
   - session id,
   - turn id when created.
5. Gateway emits runtime events.
6. TUI maps events into visible blocks:
   - `turn.started` -> status line and trace block,
   - assistant text delta -> assistant message block,
   - tool event -> tool block,
   - approval request -> permission block,
   - runtime/evidence output -> output/evidence blocks,
   - `turn.completed` -> completed status,
   - `turn.failed` / timeout -> error block with recovery action.
7. User can continue chatting, ask for changes, inspect `/trace`, `/evidence`
   and `/diff`.

## Live State Machine

| Phase | Trigger | User Visible State | Exit |
| --- | --- | --- | --- |
| `idle` | TUI starts | composer ready | user submits text |
| `submitting` | user presses Enter | message captured, sending to Gateway | session/turn accepted or failed |
| `agent_running` | `turn.started` | session/turn id visible | deltas/tool/approval/completion |
| `streaming` | assistant delta | assistant block updates | completed, approval, error |
| `tool_running` | tool event | tool block with risk/sandbox/evidence | completed/failed/approval |
| `awaiting_approval` | approval request | allow/deny/reason visible | user decision or timeout |
| `proposal_ready` | WorkflowDiff/evidence proposal | confirm/revise/reject visible | user decision |
| `completed` | `turn.completed` | final response and evidence refs visible | next user turn |
| `failed` | runtime error/timeout | error block and retry/recover action visible | retry or new input |

## Interface Contract

The selected implementation transport is Gateway stdio JSONL:

```text
node apps/mission-tui
  -> ./.venv/bin/python -m apps.gateway.stdio_server
  -> initialize / session.start / turn.start
```

### TUI -> Gateway

```json
{
  "method": "turn.start",
  "params": {
    "session_id": "gateway session id",
    "input": "redacted display text",
    "source": "mission_tui",
    "scope": {
      "workspace_root": "redacted workspace ref"
    }
  }
}
```

### Gateway -> TUI Event Adapter

| Gateway Event | Mission TUI Block |
| --- | --- |
| `turn.started` | status/trace block |
| `item.delta` | streaming assistant block |
| `turn.completed` | completed assistant/result block |
| `turn.failed` | error block |
| tool call record | tool block |
| approval request | permission block |
| evidence/runtime report ref | evidence/output block |

## Required Implementation Units

- Gateway session adapter for `apps/mission-tui`.
- Agent turn submitter using existing `GatewayService`.
- Event-to-block reducer.
- Live state machine reducer.
- Streaming assistant block renderer.
- Runtime error block renderer.
- `/trace` command backed by captured turn events.
- `/session` command showing session id, turn id and provider mode.
- Demo/fallback marker when no provider key is configured.

## Acceptance Criteria

- Real terminal interaction shows state transition after Enter.
- TUI displays `session_id` and `turn_id` for an Agent-backed turn.
- At least one real Gateway turn emits `turn.started` and `turn.completed`.
- Assistant response appears from Gateway runtime output, not local template text.
- If provider is unavailable, UI visibly marks `demo/fallback runtime`.
- `/trace` shows captured runtime events in order.
- Runtime failure creates an `error_block`; no silent failure is allowed.
- TUI still cannot directly write WorkflowDraft / WorkflowVersion /
  WorkflowInstance / StationRun / Artifact.
- source=agent direct durable mutation remains denied.

## Required Evidence

- Terminal screenshot before submit.
- Terminal screenshot after submit showing `phase:agent_running` or
  `phase:completed`.
- Raw Gateway event transcript.
- JSON acceptance summary with `gateway_turn_started=true` and
  `gateway_turn_completed=true`.
- Negative evidence that fixture-only/local-parser mode cannot satisfy V10-8
  PASS.
- No False Green and redaction scans.

## Allowed Claim

```text
V10-8 complete: Agent-backed Mission TUI chatbot bridge ready for review.
```

## Forbidden Interpretations

- Agent executor ready
- full multi-Agent orchestration ready
- complete Workflow Studio ready
- production ready
- production terminal automation ready
- autonomous workflow editing ready
- provider-backed if no provider invocation evidence exists
