# V10-8 Agent Gateway Adapter Engineering Design

## Decision

V10-8 implements the Agent-backed Mission TUI bridge through the existing
Gateway stdio JSONL server:

```text
node apps/mission-tui/src/cli.js --agent-backed
  -> spawn ./.venv/bin/python -m apps.gateway.stdio_server
  -> JSONL RPC initialize
  -> JSONL RPC session.start
  -> JSONL RPC turn.start
  -> map RpcResponse.result.events to Mission TUI blocks
```

This is the selected implementation path because `apps/mission-tui` is a Node
CLI package while `GatewayService` is Python. The Node TUI must not import
Python modules directly and must not create a parallel runtime route.

## Public CLI Interface

```text
node apps/mission-tui/src/cli.js --agent-backed
node apps/mission-tui/src/cli.js --agent-backed --model deepseek-chat
node apps/mission-tui/src/cli.js --agent-backed --domain knowledge
node apps/mission-tui/src/cli.js --agent-backed --python ./.venv/bin/python
```

`--interactive` remains local-parser mode. `--agent-backed` is the only mode
that may satisfy V10-8 Agent-backed PASS.

## Stdio Transport Contract

### Process

The TUI starts:

```text
./.venv/bin/python -m apps.gateway.stdio_server
```

Fallback if `./.venv/bin/python` is missing:

```text
python3 -m apps.gateway.stdio_server
```

### Requests

Each request is one JSON object followed by `\n`.

```json
{"id":"v10-init","method":"initialize","params":{}}
{"id":"v10-session","method":"session.start","params":{"model":"deepseek-chat"}}
{"id":"v10-turn-1","method":"turn.start","params":{"session_id":"sess_x","input":"用户输入","domain":"optional"}}
```

### Responses

Each valid stdout line is parsed as `RpcResponse`.

```json
{"id":"v10-turn-1","result":{"session_id":"sess_x","turn_id":"turn_y","final_text":"...","events":[{"type":"turn.started"},{"type":"turn.completed"}]},"error":null}
```

Any stderr output is captured into a TUI warning/error block. Non-JSON stdout
lines are treated as protocol pollution and create an error block; they cannot
count as Gateway events.

## Mission TUI State Mapping

| Gateway RPC / Event | Live State | TUI Block |
| --- | --- | --- |
| process started | `submitting` | trace block |
| `initialize` success | `submitting` | trace block |
| `session.start` success | `submitting` | status line with `gateway_session_id` |
| `turn.start` request sent | `agent_running` | user message + trace block |
| event `turn.started` | `agent_running` | trace block |
| event `item.delta` | `streaming` | assistant message append/update |
| event tool start/result | `tool_running` | tool block |
| approval event | `awaiting_approval` | permission block |
| event `turn.completed` | `completed` | assistant result + evidence refs |
| event `turn.failed` | `failed` | error block with recovery hint |
| RPC error | `failed` | error block with code/message |
| process timeout | `failed` | error block with timeout recovery |

## Required Node Modules

Implement in `apps/mission-tui/src`:

- `gateway-stdio-client.js`: owns child process, request ids, stdout JSONL
  parsing, stderr capture, timeout handling and process cleanup.
- `gateway-event-reducer.js`: converts `RpcResponse` and Gateway events into
  `MissionTuiState` mutations.
- `agent-backed-interactive.js`: interactive loop for `--agent-backed`.

Existing renderers should be reused. Do not fork a second TUI renderer.

## Error And Recovery Rules

| Failure | Required UI |
| --- | --- |
| Python executable missing | `error_block`, recovery: configure `--python` or `.venv` |
| stdio process exits early | `error_block`, recovery: retry `/reconnect` |
| invalid JSON stdout | `error_block`, protocol pollution details |
| stderr warning | warning trace block, not turn failure unless process exits |
| `session.start` error | `failed`, code/message visible |
| `turn.start` error | `failed`, code/message visible |
| turn timeout | `failed`, retry guidance |
| no assistant output | `completed` only if `turn.completed` exists; otherwise `failed` |

No failure may be silent. The composer must remain visible after failure.

## Security And No False Green Rules

- `source=agent` still cannot directly perform durable mutation.
- The TUI must not call workflow write RPC methods directly.
- `--agent-backed` may call only:
  - `initialize`,
  - `session.start`,
  - `turn.start`,
  - optional read-only `session.events`,
  - optional read-only `session.transcript`,
  - optional `session.close`.
- `provider_mode=provider-backed` requires runtime/provider evidence from the
  Gateway result or environment-derived runtime mode.
- Demo/fallback output must be labeled `provider_mode=demo-fallback` or
  `provider_mode=local-runtime`.
- Local parser output cannot satisfy V10-8 PASS.

## Acceptance Data Shape

```json
{
  "stage_id": "V10-8",
  "status": "PASS|PARTIAL|FAIL|BLOCKED",
  "evidence_scope": "agent_backed_gateway_turn",
  "gateway_session_started": true,
  "gateway_turn_started": true,
  "gateway_turn_completed": true,
  "gateway_turn_failed": false,
  "assistant_output_from_gateway": true,
  "fixture_only": false,
  "local_parser_only": false,
  "provider_mode": "provider-backed|demo-fallback|local-runtime",
  "session_id": "sess_x",
  "turn_id": "turn_x",
  "trace_id": "trace_x",
  "event_types": ["turn.started", "item.delta", "turn.completed"],
  "terminal_screenshots": [],
  "raw_gateway_transcript_ref": "path",
  "negative_local_parser_only_result": "PASS|FAIL",
  "claim_scan": "PASS|FAIL",
  "redaction_scan": "PASS|FAIL"
}
```

## Test Plan

### Unit Tests

- `gateway-stdio-client` parses valid JSONL responses.
- stderr warning becomes warning trace and does not corrupt JSON parsing.
- invalid stdout line creates protocol error block.
- missing session id rejects Agent-backed PASS.
- missing `turn.started` rejects Agent-backed PASS.
- local-parser mode rejects Agent-backed PASS.
- failed turn renders error block and keeps composer visible.

### Integration Tests

- Spawn real `apps.gateway.stdio_server`.
- Send `initialize`.
- Send `session.start`.
- Send `turn.start` with a harmless prompt.
- Assert response includes session id, turn id, events and final text or
  explicit failure.
- Render terminal state and assert phase is `completed` or `failed`, not silent.

### Evidence Commands

```text
npm --prefix apps/mission-tui test
./.venv/bin/python -m pytest tests/test_v10_*.py -q
xmllint --noout docs/design/V10.x/v10_current_gap_analysis.drawio
```

V10-8 additionally requires a real terminal screenshot from `--agent-backed`.

## Implementation Stop Conditions

- Implementation bypasses stdio Gateway and calls Python internals directly.
- TUI calls workflow write RPC methods as part of Agent-backed chat.
- `--interactive` local-parser mode is presented as Agent-backed.
- No session id / turn id / event trace is visible.
- Runtime errors are only logged and not rendered.
- Final V10 acceptance is attempted before V10-8 evidence exists.

