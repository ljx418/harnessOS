# V12-V15 Automated UX Test Matrix

## Purpose

This document converts the V12-V15 interaction acceptance plan into executable
test intent. It defines the minimum automated UX checks that must be
implemented with Playwright or equivalent browser automation before a stage can
claim its interaction evidence package is PASS.

Automation proves visibility, state feedback, route boundaries and evidence
shape. It does not replace runtime evidence or human UX review.

## Common Test Evidence

Every automated UX run must produce:

- `test_run_id`
- `stage_id`
- `scenario_id`
- browser viewport
- page URL
- screenshot path
- Playwright action log or trace path
- browser network log path
- DTO snapshot path
- expected visible text assertions
- forbidden network route assertions
- redaction result
- No False Green UI copy result
- pass/fail status
- failure reason if any

## V12 Automated UX Tests

| Test ID | User Action | Expected Evidence | Blocking Failure |
| --- | --- | --- | --- |
| `ux_v12_product_entry_visible` | Open product shell or onboarding page. | Screenshot shows product entry, workspace/project area, API health or visible blocking status. | Blank page, unresolved API mismatch hidden, or no screenshot. |
| `ux_v12_visual_hierarchy_review_snapshot` | Capture product shell at desktop and constrained viewport. | Screenshots show readable navigation, toolbar, canvas, inspector and evidence regions with no text overlap. | Layout collapses, text overlaps, or screenshot is missing. |
| `ux_v12_canvas_shell_visible` | Open workbench canvas route. | Screenshot shows entity sidebar, central canvas area, top action bar and inspector region. | Canvas is static image/drawio/Xpert reference or absent. |
| `ux_v12_canvas_node_legibility_snapshot` | Inspect default zoom canvas. | Node labels, model/tool badges, status and selected state are readable without zooming. | Node cards are clipped, unreadable or visually indistinguishable. |
| `ux_v12_entity_sidebar_visible` | Inspect left side product/workbench navigation. | DOM/text assertions for workspace, project, Agent/station inventory or equivalent entity list. | User cannot identify current workspace/project context. |
| `ux_v12_select_node_updates_inspector` | Select one station-agent or proposal node. | Inspector updates with role, goal, model/tool/skill/MCP/evidence refs from `CanvasInspectorProjection`. | Click has no visible feedback or inspector remains stale. |
| `ux_v12_disabled_canvas_action_has_reason` | Click disabled add/layout/history/publish placeholder. | Visible disabled reason or bounded read-only explanation. | Disabled action silently no-ops. |
| `ux_v12_add_menu_placeholder_has_reason` | Open or click the V12 add-menu placeholder. | Visible explanation says editable graph authoring belongs to V13 or requires confirmation/readiness. | Add menu appears to create runnable workflow nodes in V12 or silently fails. |
| `ux_v12_goal_to_proposal_to_canvas_path_visible` | Enter or load a goal, view proposal timeline and open canvas review. | Action log and screenshot show goal intake, proposal timeline, canvas review and evidence refs. | Goal intake is disconnected from graph review or transcript is treated as runtime execution. |
| `ux_v12_browser_uses_bff_only` | Capture browser network while loading shell/canvas/inspector. | Calls limited to allowed BFF/static routes; denylist routes absent. | Browser calls `/v1/rpc`, internal runtime, workflow-store, station-run, credential or provider routes. |
| `ux_v12_xpert_reference_not_runtime_evidence` | Build V12 evidence package. | Evidence metadata marks Xpert assets as reference-only and HarnessOS screenshots as implementation evidence. | Xpert screenshot is counted as HarnessOS implementation/runtime evidence. |

## V13 Automated UX Tests

| Test ID | User Action | Expected Evidence | Blocking Failure |
| --- | --- | --- | --- |
| `ux_v13_add_node_visible_feedback` | Add station/tool/quality/evidence node from Studio UI. | New node appears, action log records BFF/DTO call, graph validation result exists. | Add has no visible feedback or bypasses BFF. |
| `ux_v13_configure_node_visible_feedback` | Configure role/model/tool/skill/MCP fields in node inspector. | Inspector shows validation state and graph DTO reflects proposed config. | Config change only changes local UI or writes raw secret/prompt. |
| `ux_v13_move_node_persists_in_dto` | Drag a node and save/propose change. | DTO or graph snapshot reflects updated position; screenshot shows changed layout. | Position only changes visually and is lost in graph round-trip. |
| `ux_v13_connect_nodes_validates_edge` | Connect two valid ports/nodes. | Edge appears, validation PASS, graph round-trip PASS. | Edge bypasses validation or cannot round-trip. |
| `ux_v13_auto_layout_and_minimap_visible` | Use auto-layout/minimap/zoom controls. | Canvas updates visibly and action log captures the layout command. | Layout controls silently no-op or hide graph state. |
| `ux_v13_invalid_edge_denied_with_reason` | Attempt invalid edge or dangling required edge. | Visible denial reason and validation error evidence. | Invalid edge silently accepted or silently fails. |
| `ux_v13_workflowdiff_before_after_visible` | Generate WorkflowDiffProposal. | Before/after graph refs and visible diff summary. | Diff hidden or only represented as raw JSON. |
| `ux_v13_no_publish_run_before_confirmation` | Attempt publish/run before confirmation. | Publish/run is blocked or requires explicit confirmation transcript. | Studio publishes/runs automatically. |

## V14 Automated UX Tests

| Test ID | User Action | Expected Evidence | Blocking Failure |
| --- | --- | --- | --- |
| `ux_v14_plugin_catalog_visible` | Open extension catalog. | Approved/incompatible/unsafe package states are visible. | Catalog cannot explain package status. |
| `ux_v14_compatibility_decision_visible` | Select a plugin/skill/tool/MCP package. | Compatibility decision, required scope and policy refs are visible. | User cannot see why package is allowed/denied. |
| `ux_v14_unsafe_package_denied_with_reason` | Attempt unsafe package activation. | Denial reason visible; policy decision and audit ref captured. | Unsafe package activates or denial is silent. |
| `ux_v14_agent_inspector_shows_scoped_capabilities` | Open Agent/station inspector after scoped activation. | Only scoped capabilities appear; unscoped capabilities absent. | Unscoped capability appears usable. |
| `ux_v14_secret_redacted_in_config_ui` | View plugin/tool config. | Secret fields show redacted refs only. | Raw secret/token/provider payload visible. |

## V15 Automated UX Tests

| Test ID | User Action | Expected Evidence | Blocking Failure |
| --- | --- | --- | --- |
| `ux_v15_trace_timeline_visible` | Open workflow run review. | Trace timeline with station/tool/runtime events. | Runtime state hidden or only available in raw logs. |
| `ux_v15_metrics_and_audit_visible` | Open operations dashboard. | Metrics snapshot and audit export refs visible, read-only. | Dashboard mutates runtime truth or lacks audit refs. |
| `ux_v15_incident_state_visible` | Open failed/denied run. | Incident or failure timeline visible with reason. | Failure is hidden behind success state. |
| `ux_v15_deployment_health_visible` | Open deployment/health panel from fresh local stack. | Frontend/API health, config status and smoke result visible. | Health mismatch hidden while final claims PASS. |
| `ux_v15_final_scenario_matrix_links_evidence` | Open final acceptance dashboard. | Every scenario links to runtime/evidence package refs and scope classification. | Scenario PASS lacks evidence refs or uses planning docs only. |
| `ux_v15_xpert_inspired_human_review_package_exists` | Open final interaction evidence package. | Human review covers visual hierarchy, canvas legibility, action clarity and goal-loop continuity. | Final claim lacks human product-quality review. |
| `ux_v15_no_false_green_and_redaction_pass` | Run UI copy and content scans. | No forbidden positive claim outside safe contexts; no raw secret/raw prompt/raw artifact content. | Forbidden claim or raw content appears. |

## Suggested Commands

Exact commands depend on the frontend app path implemented in V12. The expected
shape is:

```bash
pnpm --filter <frontend-app> test:e2e -- v12
pnpm --filter <frontend-app> test:e2e -- v13
pnpm --filter <frontend-app> test:e2e -- v14
pnpm --filter <frontend-app> test:e2e -- v15
./.venv/bin/python tools/claim_scan.py docs/design/V12-V15.x evidence
./.venv/bin/python tools/redaction_scan.py docs/design/V12-V15.x evidence
```

If the frontend app path is not yet finalized, V12 implementation must define
the concrete command and record it in the V12 evidence package.

## Evidence Package Shape

Recommended directory:

```text
docs/design/V12-V15.x/evidence/v12-v15-interaction-experience/
  v12/
    acceptance-data.json
    screenshots/
    network-log.json
    playwright-trace.zip
    dto-snapshots/
    human-review.md
  v13/
  v14/
  v15/
```

`acceptance-data.json` must include:

- `stage_id`
- `status`
- `automated_checks`
- `human_review_status`
- `screenshots`
- `network_log_ref`
- `dto_snapshot_refs`
- `redaction_scan`
- `claim_scan`
- `runtime_evidence_refs`
- `reference_evidence_refs`
- `created_at`

## Automation Stop Conditions

- Any required automated check is FAIL without accepted bounded PARTIAL.
- Screenshot is missing or does not show the intended UI state.
- Network log is missing.
- Browser calls forbidden internal routes.
- Disabled/invalid/failure action has no visible reason.
- DTO snapshot does not match visible UI state.
- UI copy contains forbidden completion claim.
- Redaction scan fails.
- Human review is missing for final V15 interaction baseline.
