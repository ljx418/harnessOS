# V12 BFF Route And Browser Boundary

## Intent

V12 product shell and Chat Workbench must communicate through BFF routes and
DTOs. The browser must never call internal runtime, workflow store, executor or
credential routes directly.

## BFF Route Allowlist

Read routes:

- `GET /bff/v12/workspaces`
- `GET /bff/v12/workspaces/:workspace_id/projects`
- `GET /bff/v12/projects/:project_id`
- `GET /bff/v12/projects/:project_id/apps`
- `GET /bff/v12/apps/:app_id/station-agents`
- `GET /bff/v12/apps/:app_id/canvas`
- `GET /bff/v12/canvas/nodes/:node_ref/inspector`
- `GET /bff/v12/apps/:app_id/workbench/conversations`
- `GET /bff/v12/workflow-diff/:proposal_id`
- `GET /bff/v12/evidence/:evidence_ref`
- `GET /bff/v12/system/health`

Mutation routes:

- `POST /bff/v12/workspaces`
- `POST /bff/v12/projects`
- `POST /bff/v12/apps`
- `POST /bff/v12/apps/:app_id/station-agents`
- `POST /bff/v12/station-agent-bindings`
- `POST /bff/v12/workbench/conversations`
- `POST /bff/v12/workbench/messages`
- `POST /bff/v12/workbench/proposals/:proposal_id/revise`
- `POST /bff/v12/workbench/proposals/:proposal_id/reject`
- `POST /bff/v12/workbench/proposals/:proposal_id/confirm-handoff`

Mutation requirements:

- DTO validation.
- Workspace/project/app ownership check.
- Actor authorization check.
- Policy decision ref.
- Audit ref.
- Redaction check.

## Browser Denylist

The browser must not call:

- `/v1/rpc`
- `/v1/events/subscribe`
- `/v1/internal/runtime`
- `/v1/internal/executor`
- `/v1/internal/workflow-store`
- `/v1/internal/station-run`
- `/v1/internal/credential`
- `/v1/internal/provider`

## Runtime Truth Boundary

V12 BFF may create product entities and proposal handoff refs. It must not:

- directly mutate `WorkflowDraft`
- directly publish `WorkflowVersion`
- directly create `WorkflowInstance`
- directly mutate `StationRun`
- directly write `Artifact`
- directly invoke provider credentials

WorkflowDiff proposal confirmation may only produce governed handoff evidence
for later runtime stages. It is not proof of runtime execution.

## Canvas Boundary

V12 canvas routes may return:

- `CanvasReadModel`
- `CanvasNodeProjection`
- `CanvasInspectorProjection`

V12 canvas routes must not:

- write `WorkflowSpecGraph`
- create or mutate graph edges
- publish workflow versions
- run workflow instances
- create station runs
- write artifacts
- expose raw prompt, raw credential, raw provider payload or raw artifact
  content

Any add/layout/history buttons shown in the V12 browser canvas must be either:

- disabled with visible reason, or
- implemented as read-model/UI-local preview only with explicit evidence scope.

Editable canvas behavior belongs to V13.

## Browser Evidence Requirements

Every V12 browser E2E run must capture:

- page screenshot
- canvas/workbench shell screenshot when canvas routes are exercised
- browser network log
- BFF request log refs
- denied direct route attempts
- API health result
- frontend API base URL
- redaction scan result
- claim scan result

## Required Tests

- `browser_no_direct_v1_rpc`
- `browser_no_direct_internal_runtime`
- `browser_no_direct_internal_workflow_store`
- `browser_no_direct_internal_credential`
- `wrong_workspace_project_denied`
- `station_agent_create_records_policy_and_audit_ref`
- `workbench_message_uses_redacted_text_ref`
- `confirm_handoff_does_not_publish_or_run`
- `api_health_visible_in_product_shell`
- `canvas_read_model_uses_bff_route`
- `canvas_inspector_uses_bff_route`
- `canvas_does_not_write_workflow_spec_graph`
- `canvas_toolbar_disabled_actions_show_reason`
