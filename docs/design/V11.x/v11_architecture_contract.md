# V11 Architecture Contract

## Purpose

This contract turns the V11 target architecture into implementation-level
boundaries. It is the audit checklist for whether V11 architecture is detailed
enough to support development.

## Contract Status

Status: active planning contract.

Allowed planning claim:

`V11 planning complete: real-time explainable Mission TUI development package ready for review.`

This contract does not approve V11 runtime implementation by itself. Each V11
stage still requires its own implementation, evidence and acceptance package.

## Plane Contract

| Plane | Required Owner | Required Inputs | Required Outputs | Hard Boundary |
| --- | --- | --- | --- | --- |
| Mission TUI Interaction | Mission TUI Shell | MissionTuiState, viewport size, focus state | rendered terminal blocks | no runtime truth writes |
| Conversation And Command | Conversation Controller | natural-language text, slash command, key event | MissionInputEvent, SlashCommandInvocation | no apply/publish/run authority |
| Gateway Session/Turn | Gateway Session Client | redacted input ref, session ref, model/provider config | GatewayTurnRef, Gateway event stream | no provider direct-call from UI |
| Event Stream And State Projection | Event Stream Reducer | Gateway events, local workflow events | MissionTuiState updates, event blocks | failed events remain failed |
| Workflow/Station/Agent Projection | Projection Adapter | WorkflowSpec, WorkflowDiff, RuntimeReport, EvidenceChain | station and Agent inspector blocks | projections are not runtime truth |
| Tool/Permission Visibility | Tool/Permission Presenter | tool events, policy decisions, approval requirements | tool blocks, permission blocks | no silent allow |
| Artifact/Quality/Evidence Review | Evidence Previewer | artifact refs, quality refs, evidence refs | redacted previews, evidence links | no raw content leakage |
| Governance/Acceptance | Claim and Evidence Guard | evidence packages, screenshots, scans, drawio | acceptance verdict | no planning-only runtime PASS |

## Required Interfaces

### MissionTuiState

```json
{
  "schema_version": "v11.mission_tui_state.v1",
  "session": {
    "session_id": "string",
    "turn_id": "string",
    "trace_id": "string",
    "provider_mode": "provider-backed|real_runtime_fixture|demo-fallback|local-parser",
    "sandbox": "workspace-write|readonly|unknown"
  },
  "phase": "idle|input_received|session_ready|turn_started|agent_running|streaming|tool_running|awaiting_confirmation|proposal_ready|running_workflow|runtime_report_ready|evidence_recorded|completed|failed|blocked",
  "transcript_blocks": [],
  "timeline": [],
  "stations": [],
  "selected_station_id": "string|null",
  "available_actions": [],
  "forbidden_reasons": [],
  "evidence_refs": [],
  "runtime_truth_boundary": "tui_display_truth_only"
}
```

### TuiRuntimeEvent

```json
{
  "schema_version": "v11.tui_runtime_event.v1",
  "event_id": "string",
  "event_type": "input.received|gateway.session.started|turn.started|assistant.delta|tool.started|tool.completed|tool.failed|permission.requested|workflow.state.changed|station.started|station.completed|quality.completed|evidence.recorded|turn.completed|turn.failed",
  "source": "user|gateway|workflow_projection|tool_projection|evidence_projection|local_ui",
  "session_id": "string",
  "turn_id": "string|null",
  "timestamp": "ISO-8601",
  "payload_ref": "redacted-ref"
}
```

### StationAgentProjection

```json
{
  "schema_version": "v11.station_agent_projection.v1",
  "station_id": "string",
  "station_status": "pending|running|awaiting_confirmation|completed|failed|blocked",
  "agent": {
    "agent_id": "string",
    "role": "string",
    "goal": "string",
    "memory_summary_ref": "redacted-ref",
    "tools": [],
    "skills": [],
    "mcp_refs": []
  },
  "attempt_ref": "string",
  "output_preview_ref": "redacted-ref",
  "quality_report_ref": "string",
  "evidence_refs": []
}
```

### ToolPermissionBlock

```json
{
  "schema_version": "v11.tool_permission_block.v1",
  "tool_call_id": "string",
  "operation": "string",
  "risk_level": "low|medium|high|blocked",
  "sandbox": "readonly|workspace-write|controlled-runtime|denied",
  "status": "started|completed|failed|permission_required|denied",
  "policy_decision_ref": "string",
  "capability_decision_ref": "string",
  "approval_ref": "string|null",
  "forbidden_reason": "string|null",
  "evidence_ref": "string"
}
```

## Runtime Boundary Contract

V11 TUI may:

- submit user input to the Gateway session/turn boundary;
- render live Gateway and workflow projection events;
- request confirmation through existing governed paths;
- show WorkflowDiff, RuntimeReport, EvidenceChain and quality previews;
- export a supporting HTML explanation page.

V11 TUI must not:

- write WorkflowDraft, WorkflowVersion, WorkflowInstance, StationRun or
  Artifact directly;
- create a new executor route;
- call providers directly from the UI layer;
- treat `source=agent` as durable mutation authority;
- auto apply, auto publish, auto run, auto commit, auto push or auto deploy;
- hide denied/failed/blocked runtime states.

## Evidence Contract

Every V11 stage package must include:

- `stage_id`
- `status`
- `evidence_scope`
- `runtime_backed`
- `provider_backed`
- `fixture_backed`
- `transcript_refs`
- `screenshot_refs`
- `json_evidence_refs`
- `claim_scan`
- `redaction_scan`
- `drawio_validation_ref`

Runtime-backed PASS cannot be satisfied by:

- planning docs,
- concept images,
- report-only screenshots,
- transcript-only claims,
- fallback/demo output marked as real provider-backed output.

## Architecture Audit Checklist

- All planes have an owner and hard boundary.
- All core entities have clear owner plane and evidence requirement.
- User input, Gateway event flow and display state transitions are documented.
- Agent/Station projection is separate from Agent executor readiness.
- Tool/permission blocks expose risk and forbidden reasons.
- Evidence preview is redacted and scoped.
- HTML is supporting only.
- No False Green terms remain bounded to safe contexts.

