# V12-V15 Interaction Experience Acceptance Plan

## Purpose

This document turns the V12-V15 interaction goals into concrete acceptance
criteria. It complements the product PRD and architecture documents by defining
how the user experience is verified, which checks can be automated, and which
checks still require human review.

Executable test intent is defined in
`v12_to_v15_automated_ux_test_matrix.md`.

## Interaction Experience Target

By V15, HarnessOS should provide an Xpert-inspired frontend interaction
baseline:

- browser product entry is understandable without reading docs first;
- workspace, project, Station Agent and workflow entities are visible;
- user can move from natural-language goal intake to proposal, Studio review,
  confirmation, run inspection and evidence review;
- canvas interactions make state, node selection, inspector data and available
  actions obvious;
- every action that could mutate workflow/runtime state remains confirmation
  gated and auditable;
- failures, denied actions and missing configuration are visible, not silent;
- screenshots, network logs, DTOs and evidence packages prove the experience.

This target does not mean complete Xpert parity, complete Workflow Studio
ready, production ready or Agent executor ready.

## UX Acceptance Layers

| Layer | What It Verifies | Automation Level |
| --- | --- | --- |
| Navigation comprehension | User can find workspace, project, workbench, canvas, evidence and operations surfaces. | Playwright + screenshot + text assertions. |
| Canvas readability | Entity sidebar, canvas area, node cards, selected-node inspector and toolbar are visible. | Playwright screenshot + DOM assertions. |
| Interaction feedback | Click, select, invalid action, disabled action, loading and failure states are visible. | Playwright interaction script + state assertions. |
| Runtime/evidence clarity | User can distinguish proposal evidence, runtime evidence, reference evidence and supporting screenshots. | JSON evidence validation + text scan. |
| Safety boundary clarity | UI makes confirmation gates, forbidden actions and BFF-only browser access visible. | Network denylist + copy scan + negative tests. |
| Product polish | Layout density, hierarchy, readability and workflow understandability are acceptable to a human reviewer. | Human review with checklist. |
| Product visual quality | Component consistency, spacing rhythm, responsive constraints, node card legibility and toolbar clarity are acceptable. | Playwright screenshots + human review. |
| Goal-loop continuity | User can follow goal intake, proposal timeline, graph review, revise/confirm, run review and evidence review without losing context. | Playwright action log + DTO/evidence refs + human review. |

## Automated Acceptance Plan

Each V12-V15 stage should generate an interaction evidence package containing:

- browser screenshot at desktop viewport;
- browser screenshot at narrow viewport when applicable;
- Playwright trace or action log;
- browser network log;
- route allowlist / denylist result;
- DTO snapshot used by the UI;
- selected entity or selected node inspector snapshot;
- UI copy No False Green scan;
- redaction scan;
- PRD scenario mapping.

### Required Automated Checks

V12:

- `ux_v12_product_entry_visible`
- `ux_v12_visual_hierarchy_review_snapshot`
- `ux_v12_canvas_shell_visible`
- `ux_v12_canvas_node_legibility_snapshot`
- `ux_v12_entity_sidebar_visible`
- `ux_v12_select_node_updates_inspector`
- `ux_v12_disabled_canvas_action_has_reason`
- `ux_v12_add_menu_placeholder_has_reason`
- `ux_v12_goal_to_proposal_to_canvas_path_visible`
- `ux_v12_browser_uses_bff_only`
- `ux_v12_xpert_reference_not_runtime_evidence`

V13:

- `ux_v13_add_node_visible_feedback`
- `ux_v13_move_node_persists_in_dto`
- `ux_v13_connect_nodes_validates_edge`
- `ux_v13_invalid_edge_denied_with_reason`
- `ux_v13_workflowdiff_before_after_visible`
- `ux_v13_no_publish_run_before_confirmation`

V14:

- `ux_v14_plugin_catalog_visible`
- `ux_v14_compatibility_decision_visible`
- `ux_v14_unsafe_package_denied_with_reason`
- `ux_v14_agent_inspector_shows_scoped_capabilities`
- `ux_v14_secret_redacted_in_config_ui`

V15:

- `ux_v15_trace_timeline_visible`
- `ux_v15_metrics_and_audit_visible`
- `ux_v15_incident_state_visible`
- `ux_v15_deployment_health_visible`
- `ux_v15_final_scenario_matrix_links_evidence`
- `ux_v15_no_false_green_and_redaction_pass`

## Human Review Checklist

Human review is still required because automation cannot fully judge product
clarity and interaction quality.

Reviewers should answer:

- Can a new user understand where to start within 60 seconds?
- Does the product shell feel coherent enough to be reviewed as a product
  surface, not only an engineering test page?
- Can a user identify the current workspace, project and workflow state?
- Can a user tell which Agent/Station produced which output?
- Can a user tell whether a piece of evidence is runtime-backed,
  fixture-backed, reference-only or supporting-only?
- Can a user identify why an action is disabled or denied?
- Can a user inspect output, quality and evidence without opening raw JSON?
- Does the canvas explain available actions without implying unsafe execution?
- Are node cards readable at default zoom and under constrained viewport?
- Does the user understand the path from natural-language goal to proposal,
  graph review, confirmation, run review and evidence review?
- Does the UI avoid claiming complete Studio, production readiness or full
  Xpert parity?

Human acceptance states:

- `PASS`
- `PASS_WITH_MINOR_ISSUES`
- `PARTIAL_ACCEPTED`
- `BLOCKED`
- `FAIL`

## Interaction Stop Conditions

- User input or click has no visible feedback.
- Disabled action lacks visible reason.
- Node selection does not update the inspector or leaves stale data visible.
- Add/layout/history/publish/run placeholders do not explain why the action is
  unavailable in the current stage.
- Failure or denied state is hidden behind a success state.
- Browser canvas screenshot is static/drawio/Xpert-reference only.
- UI uses Xpert screenshots as HarnessOS implementation evidence.
- UI copy claims complete Workflow Studio ready, Xpert parity complete,
  production ready or Agent executor ready.
- Browser calls direct internal runtime, workflow-store, station-run,
  credential or provider routes.
- Inspector exposes raw prompt, raw file content, raw provider payload, raw
  token, raw secret or raw artifact content.
- Final acceptance has no human review checklist result.
- Current engineering prototype is treated as product-grade frontend or
  Xpert-level UX complete.

## Final Interaction Acceptance Rule

V15 cannot claim:

`V15 complete: Xpert-level frontend interaction baseline ready for review.`

unless:

- V12 interaction evidence package exists and PASS;
- V13 interaction evidence package exists and PASS;
- V14 interaction evidence package exists and PASS;
- V15 interaction evidence package exists and PASS;
- all required automated UX checks pass or have accepted bounded PARTIAL;
- human review is PASS or PASS_WITH_MINOR_ISSUES;
- No False Green scan PASS;
- redaction scan PASS;
- drawio XML valid.
