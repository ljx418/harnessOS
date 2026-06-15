# V10 Schema And Fixture Package

## Purpose

This package defines the machine-readable contracts and fixture families needed
to implement V10 without guessing from prose. It is a design-time contract; the
actual JSON files may be added during V10-1 through V10-9 implementation.

## Required Schema Families

| Schema | Stage | Purpose |
| --- | --- | --- |
| `mission_tui_state.schema.json` | V10-1 | Full state object rendered by the TUI. |
| `transcript_item.schema.json` | V10-1 | Shared envelope for all transcript blocks. |
| `status_line.schema.json` | V10-1 | Workspace/model/mode/sandbox/evidence status. |
| `available_action.schema.json` | V10-2 | User-visible action with risk and confirmation state. |
| `forbidden_action_reason.schema.json` | V10-2 | User-visible reason for denied actions. |
| `tool_block.schema.json` | V10-2 | Tool preview/result block. |
| `permission_block.schema.json` | V10-2 | Allow/deny prompt block. |
| `plan_block.schema.json` | V10-2 | Plan/todo block. |
| `station_block.schema.json` | V10-3 | Station/Agent explainability block. |
| `output_preview_block.schema.json` | V10-4 | Artifact/quality preview block. |
| `workflowdiff_block.schema.json` | V10-5 | Proposal-first workflow modification block. |
| `html_explainer_export.schema.json` | V10-6 | Supporting audit export from read-model state. |
| `v10_read_model_acceptance_data.schema.json` | V10-7 | Bounded read-model UX acceptance data. |
| `live_state.schema.json` | V10-8 | Phase/session/turn/provider state. |
| `gateway_event_trace.schema.json` | V10-8 | Gateway event transcript consumed by TUI. |
| `agent_backed_turn_acceptance.schema.json` | V10-8 | Agent-backed acceptance data. |
| `v10_final_acceptance_data.schema.json` | V10-9 | Final acceptance aggregation data. |

## Required Schema Rules

- Every schema uses `additionalProperties=false`.
- Every block requires `id`, `type`, `status`, `created_at`, and `redacted=true`.
- Every station, output preview, permission and WorkflowDiff block requires at
  least one evidence ref.
- `source=agent` direct durable mutation is always rejected.
- Raw prompt, raw provider payload, raw connector payload, raw artifact content,
  API key, Bearer token, signed URL and raw secret fields are forbidden.
- HTML explainer refs cannot populate real TUI screenshot fields.
- `provider_mode=local-parser` cannot satisfy V10-8 Agent-backed PASS.
- Agent-backed fixtures require Gateway session id, turn id and event trace.

## Required Positive Fixture Families

| Fixture Family | Required Examples |
| --- | --- |
| V10-1 shell | 80x24 state, 120x40 state, empty session, command palette open |
| V10-2 blocks | tool running/completed/failed, permission allow/deny, plan in progress |
| V10-3 explainability | local markdown station, Roman Forum persona stations |
| V10-4 previews | summary preview, storyboard preview, coding proposal preview |
| V10-5 WorkflowDiff | revision proposal, confirm pending, revise pending, reject pending |
| V10-6 HTML export | markdown report, Roman Forum report, storyboard report |
| V10-7 read-model baseline | all read-model scenarios PASS, accepted PARTIAL, blocked scenario negative |
| V10-8 Agent-backed bridge | Gateway turn completed, Gateway turn failed, fallback mode visible |
| V10-9 final | V10-1..V10-8 aggregated PASS, missing V10-8 negative |

## Required Negative Fixture Families

| Fixture | Expected Result |
| --- | --- |
| `station_without_evidence_ref.json` | FAIL |
| `workflowdiff_auto_apply_action.json` | FAIL |
| `permission_denial_without_reason.json` | FAIL |
| `html_report_as_runtime_screenshot.json` | FAIL |
| `openharness_primary_copy.json` | FAIL |
| `raw_secret_in_tui_state.json` | FAIL |
| `raw_provider_payload_in_preview.json` | FAIL |
| `source_agent_direct_mutation_action.json` | FAIL |
| `hidden_apply_publish_run_action.json` | FAIL |
| `concept_image_as_real_tui_screenshot.json` | FAIL |
| `local_parser_only_claimed_agent_backed.json` | FAIL |
| `gateway_turn_without_session_id.json` | FAIL |
| `gateway_turn_without_turn_started.json` | FAIL |

## Validation Expectations

When implementation starts, CI should include:

```text
pnpm --dir apps/mission-tui test
pnpm --dir apps/mission-tui build
./.venv/bin/python -m pytest tests/test_v10_*.py -q
xmllint --noout docs/design/V10.x/v10_current_gap_analysis.drawio
```

The V10 final acceptance validator must reject planning docs, concept images,
supporting HTML pages and local-parser output as substitutes for Agent-backed
Gateway turn evidence.
