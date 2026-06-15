# HarnessOS V10.x Canonical Index

Current V10 baseline:

- V9 user scenario special acceptance is ready for review.
- V10 focuses on CLI-native TUI experience and user-facing explainability.
- V10-0R supersedes the cockpit-first concept package.
- V10-0R is planning correction and concept validation only.
- V10 implementation evidence now includes a dependency-free CLI-native Mission
  TUI renderer, fixture-backed read model validation, real terminal render
  captures, Agent-backed Gateway session/turn evidence and final UX acceptance
  aggregation.
- V10-1 through V10-7 are now bounded as CLI/read-model UX baseline evidence.
- V10-8 Agent-backed Chatbot TUI Bridge is complete for review with
  evidence_scope=agent_backed_gateway_turn.
- V10-9 final UX acceptance is complete for review after aggregating V10-1
  through V10-8 evidence.
- HTML explainer pages are supporting audit artifacts, not the primary TUI.

Allowed current bounded claim:

V10-1..V10-7 complete: CLI-native read-model TUI experience baseline ready for review.

Allowed V10-8 claim:

V10-8 complete: Agent-backed Mission TUI chatbot bridge ready for review.

Allowed final V10 claim:

V10 complete: CLI-native Agent-backed TUI experience and explainability baseline ready for review.

Evidence boundary:

- V10-1 evidence_scope=real_tui_render_fixture.
- V10-2 evidence_scope=fixture_render.
- V10-3 evidence_scope=v9_evidence_backed_fixture_render.
- V10-4 evidence_scope=v9_evidence_backed_fixture_render.
- V10-5 evidence_scope=fixture_render.
- V10-6 evidence_scope=supporting_html_export.
- V10-7 aggregates V10-1 through V10-6 evidence and US-V10-01 through
  US-V10-05 scenario evidence.
- V10-8 must use evidence_scope=agent_backed_gateway_turn and must include
  session_id, turn_id, `turn.started`, `turn.completed` or explicit failure
  evidence. Fixture-only/local-parser evidence cannot satisfy V10-8 PASS.
- Current implementation uses a dependency-free CLI-native block renderer; a
  full React/Ink dependency migration remains a future implementation choice,
  not a completed claim.

Forbidden interpretations:

- production ready
- full production GA
- Agent executor ready
- complete Workflow Studio ready
- full multi-Agent orchestration ready
- unrestricted terminal worker ready

## Canonical Documents

- `v10_target_prd.md`
- `v10_target_architecture.md`
- `v10_agent_backed_tui_bridge_plan.md`
- `v10_8_agent_gateway_adapter_engineering_design.md`
- `v10_cli_native_interaction_concepts.md`
- `v10_tui_state_contract.md`
- `v10_runtime_bridge_contract.md`
- `v10_test_fixture_matrix.md`
- `v10_schema_and_fixture_package.md`
- `v10_stage_implementation_specs.md`
- `v10_user_scenario_acceptance_gate.md`
- `v10_final_acceptance_framework.md`
- `v10_implementation_readiness_audit.md`
- `v10_milestone_roadmap.md`
- `v10_development_and_acceptance_plan.md`
- `v10_current_gap_analysis.md`
- `v10_current_gap_analysis.drawio`
- `v10_no_false_green_claim_guard.md`

## Evidence

- `evidence/v10-1-mission-tui-shell/acceptance-data.json`
- `evidence/v10-1-mission-tui-shell/real-tui-80x24.txt`
- `evidence/v10-1-mission-tui-shell/real-tui-120x40.txt`
- `evidence/v10-2-tool-permission-plan-blocks/acceptance-data.json`
- `evidence/v10-3-workflow-explainability-blocks/acceptance-data.json`
- `evidence/v10-4-output-quality-preview/acceptance-data.json`
- `evidence/v10-5-workflowdiff-preview/acceptance-data.json`
- `evidence/v10-6-html-explainer/acceptance-data.json`
- `evidence/v10-7-final-acceptance/v10-final-acceptance-data.json`
- `evidence/v10-7-final-acceptance/v10-final-user-scenario-matrix.json`
- `evidence/v10-8-agent-backed-tui/acceptance-data.json`
- `evidence/v10-8-agent-backed-tui/agent-backed-terminal-180x55.txt`
- `evidence/v10-8-agent-backed-tui/agent-backed-raw-result.json`
- `evidence/v10-9-final-acceptance/v10-final-acceptance-data.json`
- `evidence/v10-cli-interactive-observability/multi-agent-discussion-smoke.txt`
- `evidence/v10-0-tui-experience-planning/index.html`
- `evidence/v10-0-tui-experience-planning/acceptance-data.json`
- `evidence/v10-0-tui-experience-planning/concept-terminal-message-stream.svg`
- `evidence/v10-0-tui-experience-planning/concept-command-palette-onboarding.svg`
- `evidence/v10-0-tui-experience-planning/concept-tool-permission-blocks.svg`
- `evidence/v10-0-tui-experience-planning/concept-station-output-preview.svg`
- `evidence/v10-0-tui-experience-planning/concept-workflowdiff-review.svg`

## Historical / Superseded

- `docs/history/design/V10.x/superseded/v10-0-cockpit-first/host-generated-cockpit.png` is
  retained as historical visual evidence only. It is not the current V10 target
  direction and is not runtime evidence.
