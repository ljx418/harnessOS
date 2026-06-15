# V10 Runtime Bridge Contract

## Purpose

The V10 Runtime Bridge converts existing runtime events, V9 evidence packages
and workflow projections into `MissionTuiState`. V10-8 extends this bridge so
Mission TUI can submit user turns to the existing Gateway/Agent runtime and
render live runtime events. It must not introduce a new runtime write path.

## Inputs

The bridge may read:

- Gateway/OpenHarness app state and transcript events.
- Gateway `session.start` / `turn.start` responses.
- Gateway turn event streams.
- V7/V8/V9 evidence packages.
- WorkflowSpec / WorkflowDiff projections.
- RuntimeReport / EvidenceChain projections.
- Station/Agent descriptors and artifact metadata.

The bridge must not read or store:

- raw credential material,
- raw provider payload,
- raw prompt beyond redacted display text,
- raw artifact body unless explicitly redacted into preview metadata.

## Event Mapping

| Source Event / Artifact | TUI Output |
| --- | --- |
| user input | `user_message` |
| `session.start` accepted | live state line with `session_id` |
| `turn.start` accepted / `turn.started` | live state line with `turn_id`, `agent_running` |
| assistant text delta / completion | `assistant_message` |
| plan/todo update | `plan_block` |
| tool started | `tool_block` with status `running` |
| tool completed | `tool_block` with status `completed` or `failed` |
| permission request | `permission_block` |
| station projection | `station_block` |
| artifact/quality projection | `output_preview_block` |
| WorkflowDiff projection | `workflowdiff_block` |
| runtime/evidence error | `error_block` |

## Agent-Backed Turn Contract

V10-8 uses the existing Gateway stdio JSONL transport. The Node Mission TUI
spawns `./.venv/bin/python -m apps.gateway.stdio_server`, writes JSONL
`RpcRequest` objects to stdin and parses JSONL `RpcResponse` objects from
stdout. Stderr is captured as warning/error evidence and must not be parsed as
Gateway events.

### Submit Payload

```json
{
  "session_id": "existing or newly created Gateway session",
  "input": "redacted user display text",
  "source": "mission_tui",
  "scope": {
    "workspace_root_ref": "redacted workspace reference"
  }
}
```

### Required Runtime Evidence

- `gateway_session_started=true`
- `gateway_turn_started=true`
- `gateway_turn_completed=true` or `gateway_turn_failed=true`
- `assistant_output_from_gateway=true`
- `fixture_only=false`
- `local_parser_only=false`
- `provider_mode` explicitly set to `provider-backed`, `demo-fallback` or
  `local-runtime`

### Live Phase Mapping

| Phase | Required Source |
| --- | --- |
| `idle` | TUI local state |
| `submitting` | user pressed Enter and submit started |
| `agent_running` | Gateway `turn.started` |
| `streaming` | assistant delta or runtime output |
| `tool_running` | tool call event |
| `awaiting_approval` | approval request |
| `completed` | Gateway `turn.completed` |
| `failed` | Gateway `turn.failed`, timeout or adapter error |

## Bridge Boundaries

- Bridge output is a read model only.
- Durable mutation must remain in existing governed runtime paths.
- `source=agent` direct durable mutation remains denied.
- The bridge can emit a confirmation request but cannot mark it approved.
- HTML explainer export consumes bridge output; it does not construct runtime
  truth.
- The bridge must visibly distinguish provider-backed, demo fallback and local
  parser modes.
- Local-parser proposal output cannot satisfy Agent-backed scenario PASS.

## Implementation Entry Requirements

Before V10-1 implementation starts:

- `MissionTuiState` fixture exists.
- Event mapping fixture exists for user, assistant, tool, permission, station,
  output preview and WorkflowDiff blocks.
- 80x24 and 120x40 render expectations are accepted.
- No False Green and redaction scan rules are accepted.

## Negative Cases

The bridge must reject or mark blocked:

- station block without `evidence_ref`,
- WorkflowDiff block with auto-apply action,
- permission block without forbidden reason when action is denied,
- HTML report passed as runtime screenshot,
- OpenHarness primary branding in V10 user-facing copy.
- local-parser output claimed as Agent-backed Gateway evidence.
- provider-backed claim without provider invocation or runtime mode evidence.
