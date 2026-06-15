# V10 Target Architecture

## Architecture Summary

V10 adds a user-facing CLI-native TUI experience layer without moving runtime
truth into the UI.

```text
User
  -> CLI-native Agent-backed Mission TUI
  -> Composer / Slash Commands / Keyboard Controller
  -> Gateway Session + Turn Adapter
  -> Existing GatewayService / Agent Runtime
  -> Gateway Event Stream
  -> TUI Event Reducer + Live State Machine
  -> Terminal Transcript Blocks
  -> WorkflowSpec / WorkflowDiff / RuntimeReport / EvidenceChain projections
  -> Controlled Runtime / Existing V9 evidence packages
```

## New Components

### CLI-Native Agent-Backed Mission TUI

Primary V10 terminal UI. It owns the single-column message stream, bottom
composer, slash commands, keyboard navigation, tool blocks, permission prompts
and live Agent/Gateway turn rendering. It does not own runtime truth.

### Gateway Session + Turn Adapter

Submits composer input to the existing Gateway boundary:

- creates or resumes a Gateway session,
- calls `turn.start` with redacted user input,
- records session id, turn id and trace refs,
- maps Gateway runtime events to TUI blocks,
- marks provider/fallback mode visibly.

It must not bypass `GatewayService` or create a new executor route.

### Live State Machine Reducer

Tracks observable user-facing phases:

- `idle`,
- `submitting`,
- `agent_running`,
- `streaming`,
- `tool_running`,
- `awaiting_approval`,
- `proposal_ready`,
- `completed`,
- `failed`.

The reducer exists so the user can always see whether the system is waiting,
running, blocked, failed or done.

### TUI Read Model Adapter

Loads normalized state from existing HarnessOS evidence and runtime projections:

- workflow goal,
- WorkflowSpec and WorkflowDiff,
- station and Agent descriptors,
- station output previews,
- quality checks,
- evidence refs,
- available actions and forbidden reasons.

### Terminal Transcript Blocks

The default surface is a transcript of typed blocks:

- user and assistant messages,
- plan/todo blocks,
- tool started/completed blocks,
- permission and forbidden-reason blocks,
- station/Agent output blocks,
- WorkflowDiff preview blocks.

Wide terminals may show a compact status rail, but the rail is secondary.

### Inline Explainability Blocks

Expandable terminal blocks show:

- selected station,
- Agent role / goal / memory / tools / skills / MCP refs,
- input and output preview refs,
- quality result,
- policy and capability decision,
- evidence links.

### HTML Explainer Generator

Creates scenario-specific HTML reports when terminal space is too small or when
human review needs richer media. It reuses the V9 evidence packaging pattern.
It is not the primary TUI and cannot count as a real TUI screenshot.

## Runtime Data Flow

```text
User input
  -> Composer command parser
  -> Gateway Session + Turn Adapter
  -> GatewayService session.start / turn.start
  -> Agent runtime events
  -> Mission TUI event reducer and live state machine
  -> TUI Read Model Adapter for workflow/evidence projections
  -> Existing V7/V8/V9 workflow projections and evidence packages
  -> Terminal transcript blocks
  -> Optional HTML explainer export
```

Durable workflow changes must flow through existing governed confirmation or
handoff paths. The TUI only displays proposals and confirmation requests.

## Block Model

| Block | Purpose | Source | Mutation Authority |
| --- | --- | --- | --- |
| StatusLine | workspace/model/mode/sandbox/evidence summary | app state/read model | none |
| Composer | natural-language input and slash commands | user input | none |
| LiveStateLine | phase/session/turn/provider status | Gateway events | none |
| PlanBlock | plan/todo visibility | assistant/read model | none |
| ToolBlock | tool preview and result status | runtime event/read model | none |
| PermissionBlock | allow/deny UI and forbidden reason | governed policy decision | confirmation only |
| StationBlock | Agent role, output preview, quality and evidence | station projection | none |
| WorkflowDiffBlock | proposed workflow modification | WorkflowDiff projection | proposal only |
| ErrorBlock | runtime failure, timeout or bridge error | Gateway event/adapter | none |

## Runtime Truth Boundary

The TUI may:

- show state,
- request confirmation,
- open evidence,
- render previews,
- create proposal objects.

The TUI must not:

- write WorkflowDraft / WorkflowVersion / WorkflowInstance / StationRun /
  Artifact directly,
- treat source=agent as durable mutation authority,
- execute unrestricted connector.call or external_llm.call,
- mark review summary as approval.

## Interface Shape

Minimum read-model object for V10-1/V10-2:

```json
{
  "schema_version": "v10.cli_native_mission_tui_state.v1",
  "session_id": "string",
  "goal": "string",
  "status_line": {"workspace": "string", "model": "string", "mode": "string", "sandbox": "string"},
  "live_state": {"phase": "idle|submitting|agent_running|streaming|tool_running|awaiting_approval|proposal_ready|completed|failed", "session_id": "string", "turn_id": "string", "provider_mode": "provider-backed|demo-fallback|local-parser"},
  "transcript_items": [],
  "workflow": {"workflow_spec_ref": "string", "workflow_diff_ref": "string"},
  "stations": [],
  "selected_station_id": "string",
  "available_actions": [],
  "forbidden_reasons": [],
  "evidence_refs": [],
  "runtime_truth_boundary": "tui_read_model_not_runtime_truth"
}
```

## Agent-Backed Bridge Boundary

V10-8 may prove Agent-backed conversation only when:

- Gateway `session.start` succeeds,
- Gateway `turn.start` succeeds,
- at least `turn.started` and `turn.completed` or `turn.failed` are captured,
- assistant output is derived from Gateway runtime output,
- fallback/demo mode is visibly marked when no provider invocation exists.

Fixture/read-model/local-parser evidence can still support UI regression, but
it cannot satisfy V10-8 Agent-backed PASS.
