# V10 Test Fixture Matrix

## Purpose

This matrix defines the fixtures and checks required to implement V10 without
guessing UX behavior from prose.

The canonical schema/fixture package is `v10_schema_and_fixture_package.md`.

## Required Fixtures

| Fixture | Stage | Purpose |
| --- | --- | --- |
| `mission_tui_state_minimal.json` | V10-1 | Shell/status/composer render |
| `mission_tui_state_80x24.json` | V10-1 | Narrow terminal snapshot |
| `mission_tui_state_120x40.json` | V10-1 | Wide terminal snapshot |
| `tool_permission_blocks.json` | V10-2 | Tool/risk/sandbox/allow/deny render |
| `workflow_station_blocks.json` | V10-3 | Station/Agent explainability render |
| `output_quality_preview.json` | V10-4 | Artifact/quality/evidence preview |
| `workflowdiff_proposal.json` | V10-5 | Natural-language revision proposal |
| `html_explainer_export.json` | V10-6 | HTML export from read-model state |
| `v10_user_scenario_matrix.json` | V10-7 | Final scenario acceptance |
| `gateway_turn_started_completed.json` | V10-8 | Agent-backed Gateway session/turn happy path |
| `gateway_turn_failed.json` | V10-8 | Runtime failure rendered as visible error block |

## Negative Fixtures

| Fixture | Expected Result |
| --- | --- |
| `station_without_evidence_ref.json` | FAIL |
| `workflowdiff_auto_apply_action.json` | FAIL |
| `permission_denial_without_reason.json` | FAIL |
| `html_report_as_runtime_screenshot.json` | FAIL |
| `openharness_primary_copy.json` | FAIL |
| `raw_secret_in_tui_state.json` | FAIL |
| `local_parser_only_claimed_agent_backed.json` | FAIL |
| `gateway_turn_without_session_id.json` | FAIL |
| `gateway_turn_without_turn_started.json` | FAIL |

## Test Commands

Planned commands:

```text
pnpm --dir apps/mission-tui test
pnpm --dir apps/mission-tui build
./.venv/bin/python -m pytest tests/test_v10_*.py -q
xmllint --noout docs/design/V10.x/v10_current_gap_analysis.drawio
```

## Acceptance Oracles

- 80x24 render keeps the composer visible and does not require a side rail.
- 120x40 render may show a compact rail but the transcript remains primary.
- Tool blocks show risk, sandbox, command preview and evidence refs.
- Permission prompts show allow/deny and forbidden reason.
- Station blocks show Agent role, goal, output, quality and evidence refs.
- WorkflowDiff stays proposal-first until user confirmation.
- HTML explainer is marked supporting export, not runtime TUI.
- Agent-backed bridge shows phase, session id, turn id and provider/fallback
  mode.
- Agent-backed PASS requires Gateway `turn.started` and `turn.completed` or
  explicit `turn.failed` evidence.
- Local parser / fixture output cannot satisfy Agent-backed PASS.
