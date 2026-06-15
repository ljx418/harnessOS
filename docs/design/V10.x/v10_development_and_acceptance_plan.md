# V10 Development And Acceptance Plan

## Stage Order

| Stage | Name | Status | Exit Claim |
| --- | --- | --- | --- |
| V10-0R | CLI-Native TUI Planning Correction Gate | complete for review | V10-0R complete: CLI-native TUI experience planning correction ready for review. |
| V10-1 | React/Ink CLI-Native Mission Shell | complete for review | V10-1 complete: CLI-native Mission TUI shell ready for review. |
| V10-2 | Tool / Permission / Plan Blocks | complete for review | V10-2 complete: terminal tool, permission and plan blocks ready for review. |
| V10-3 | Workflow Explainability Inline Blocks | complete for review | V10-3 complete: workflow explainability inline blocks ready for review. |
| V10-4 | Station Output And Quality Preview | complete for review | V10-4 complete: station output preview and quality view ready for review. |
| V10-5 | Natural Language WorkflowDiff Preview | complete for review | V10-5 complete: workflow modification proposal preview ready for review. |
| V10-6 | Evidence HTML Explainer Generator | complete for review | V10-6 complete: evidence explainer generator ready for review. |
| V10-7 | User Onboarding And Read-Model UX Acceptance | bounded baseline complete for review | V10-1..V10-7 complete: CLI-native read-model TUI experience baseline ready for review. |
| V10-8 | Agent-Backed Chatbot TUI Bridge | complete for review | V10-8 complete: Agent-backed Mission TUI chatbot bridge ready for review. |
| V10-9 | Final V10 UX Acceptance | complete for review | V10 complete: CLI-native Agent-backed TUI experience and explainability baseline ready for review. |

## V10-0R Acceptance

V10-0R passes when:

- canonical V10 docs exist,
- cockpit-first concept is explicitly superseded,
- implementation options are compared with CLI-native criteria,
- React/Ink CLI-native route is selected,
- terminal-native concept prompts exist,
- terminal-native local concept diagrams exist,
- HTML report is generated,
- drawio XML is valid,
- no false green guard exists,
- V10-1 implementation has not started.

## V10-1 Entry Checklist

- V10-0R accepted.
- Node package path accepted: `apps/mission-tui`.
- Runtime bridge contract accepted.
- Stage implementation specs accepted.
- User scenario acceptance gate accepted.
- No OpenHarness primary branding in user-facing V10 TUI copy.
- Terminal snapshot matrix accepted for 80x24 and 120x40.
- Test matrix accepted.

## Stage Acceptance Details

| Stage | Development Focus | Required Evidence |
| --- | --- | --- |
| V10-1 | React/Ink shell, top status line, transcript stream, bottom composer, command palette | real TUI screenshots at 80x24 and 120x40, component tests, no OpenHarness primary copy |
| V10-2 | tool blocks, permission prompts, plan/todo blocks | tool/permission fixture render, allow/deny visible, forbidden reason visible |
| V10-3 | workflow/station/Agent inline explainability blocks | V9 scenario fixture loaded, station role/goal/tools/evidence visible |
| V10-4 | station output, quality and artifact preview | output preview references artifact/evidence refs, quality status visible |
| V10-5 | WorkflowDiff proposal and natural-language revision flow | proposal-first evidence, confirm/revise/reject visible, no auto apply |
| V10-6 | HTML explainer export from TUI/evidence state | generated HTML, evidence links, media references, not primary TUI |
| V10-7 | read-model UX acceptance | user scenario matrix, real TUI screenshots, no false green/redaction PASS, fixture/local-parser boundary visible |
| V10-8 | Agent-backed TUI bridge through Gateway session/turn | real terminal interaction, Gateway `turn.started`/`turn.completed` or failure evidence, session_id/turn_id visible, fallback mode marked if no provider |
| V10-9 | final V10 acceptance | V10-1..V10-8 evidence packages, agent-backed scenario PASS, no false green/redaction/drawio PASS |

Detailed implementation packages are controlled by
`v10_stage_implementation_specs.md`. Scenario-specific gates are controlled by
`v10_user_scenario_acceptance_gate.md`. V10 final acceptance is controlled by
`v10_final_acceptance_framework.md`.

## V10 Test Matrix

- TUI shell renders top status line, single-column command stream and bottom composer.
- TUI live state line shows phase, session id, turn id and provider/fallback
  mode when Agent-backed bridge is active.
- User input submitted in Agent-backed mode calls Gateway `session.start` /
  `turn.start`; local-parser output cannot satisfy Agent-backed PASS.
- Gateway events map to visible TUI blocks without silent failure.
- 80x24 terminal snapshot remains readable without a side rail.
- 120x40 terminal snapshot may show a compact status rail without hiding the transcript.
- Tool calls render as bounded terminal blocks with started/completed/failed status.
- Permission prompts render allow/deny choices, risk, sandbox and forbidden reason.
- Plan/todo blocks render current step and completion state.
- TUI can load fixture state from V9 user scenario evidence.
- OpenHarness strings are absent from V10 primary UI copy except compatibility
  or boundary notes.
- Station inline block shows Agent role, goal, output preview, quality status and evidence refs.
- WorkflowDiff proposal is visible before confirmation.
- No hidden mutation button exists.
- Concept images and HTML reports are not accepted as real TUI screenshots.
- No False Green scan passes.
- Redaction scan passes.

## Required User Scenario Matrix

- US-V10-01 local Markdown workflow creation and observation.
- US-V10-02 Roman Forum parallel Agent discussion review.
- US-V10-03 video storyboard workflow output and quality preview.
- US-V10-04 coding proposal workflow with diff/test/review evidence.
- US-V10-05 natural-language workflow revision producing WorkflowDiff only.
- US-V10-06 Agent-backed chatbot turn where user input produces Gateway-backed
  assistant output, trace state and completion/failure evidence.

## Stop Conditions

- V10 TUI claims complete Workflow Studio.
- V10 TUI claims Agent executor readiness.
- source=agent can directly mutate runtime.
- UI hides forbidden reasons.
- station output preview lacks evidence refs.
- V10 final acceptance runs without V10-1 through V10-8 evidence packages.
- V10 final acceptance runs without V10-8 Agent-backed Gateway turn evidence.
- Required user scenarios are replaced by planning docs or concept images.
- Fixture-only/local-parser proposal evidence is claimed as Agent-backed
  chatbot evidence.
- Gateway-backed demo-fallback evidence is claimed as provider-backed LLM output
  without provider invocation evidence.
- V10 report uses cockpit images as current target direction.
- concept image is presented as real TUI runtime evidence.
- concept HTML cannot be opened.
- V10-0R starts runtime implementation before planning acceptance.
