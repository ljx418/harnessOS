# V10 TUI State Contract

## Purpose

This contract defines the minimum implementation shape for the CLI-native
Mission TUI. It is the handoff between runtime/evidence projections and
React/Ink rendering. It does not create runtime truth.

## MissionTuiState

Required fields:

```json
{
  "schema_version": "v10.cli_native_mission_tui_state.v1",
  "session_id": "string",
  "workspace_root": "string",
  "goal": "string",
  "status_line": {
    "workspace": "string",
    "model": "string",
    "mode": "plan|default|review",
    "sandbox": "read-only|workspace-write",
    "evidence_status": "none|ready|partial|failed"
  },
  "live_state": {
    "phase": "idle|submitting|agent_running|streaming|tool_running|awaiting_approval|proposal_ready|completed|failed",
    "gateway_session_id": "string|null",
    "gateway_turn_id": "string|null",
    "trace_id": "string|null",
    "provider_mode": "provider-backed|demo-fallback|local-parser|local-runtime",
    "fixture_only": "boolean",
    "last_event_type": "string|null"
  },
  "transcript_items": [],
  "selected_item_id": "string|null",
  "available_actions": [],
  "forbidden_reasons": [],
  "evidence_refs": [],
  "runtime_truth_boundary": "tui_read_model_not_runtime_truth"
}
```

## Transcript Item Types

| Type | Purpose | Required Display Fields |
| --- | --- | --- |
| `user_message` | User input | text, created_at |
| `assistant_message` | Assistant output stream/result | text, status |
| `trace_block` | Gateway turn event trace | session_id, turn_id, event_count, last_event_type |
| `plan_block` | Plan/todo visibility | steps, current_step_id, status |
| `tool_block` | Tool preview/result | tool_name, risk_level, sandbox, evidence_refs |
| `permission_block` | Confirmation prompt | decision_id, allow_label, deny_label, forbidden_reason_refs |
| `station_block` | Station/Agent state | station_id, agent_role, agent_goal, status, evidence_refs |
| `output_preview_block` | Output/artifact preview | artifact_refs, quality_refs, evidence_refs |
| `workflowdiff_block` | Workflow change proposal | workflow_diff_ref, affected_station_ids, actions |
| `error_block` | Recoverable/error state | message, recovery_hint, evidence_refs |

## Block Rules

- Every block has `id`, `type`, `status`, `created_at`, and `redacted=true`.
- source=agent must not directly perform durable mutation.
- Every station, output preview, permission and WorkflowDiff block must include
  at least one `evidence_ref`.
- Blocks can be expanded/collapsed, but the collapsed view must still show
  status, risk if present, and evidence availability.
- Concept images and HTML reports cannot populate `transcript_items`.
- V10-8 Agent-backed PASS requires `live_state.fixture_only=false`,
  `gateway_session_id`, `gateway_turn_id` and a Gateway event trace.
- `provider_mode=local-parser` cannot satisfy Agent-backed acceptance.

## Action Model

Allowed action ids:

- `submit_goal`
- `open_command_palette`
- `expand_block`
- `open_evidence`
- `confirm_proposal`
- `revise_proposal`
- `reject_proposal`
- `export_html_explainer`

Forbidden action ids:

- `auto_apply_workflowdiff`
- `auto_publish_workflow`
- `agent_direct_mutation`
- `run_unrestricted_terminal`
- `claim_runtime_truth_from_html`

## Redaction

Forbidden raw fields:

- raw prompt
- raw provider payload
- raw connector payload
- raw artifact content
- API key
- Bearer token
- signed URL
- raw secret
