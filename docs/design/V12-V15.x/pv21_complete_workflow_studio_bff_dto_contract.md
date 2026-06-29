# PV21 Complete Workflow Studio BFF DTO Contract

用途：定义 PV21 `/bff/pv21/*` 的请求、响应、错误、权限和禁止路径，支撑后续自动化开发。
阅读对象：前端、后端、测试、架构、审计人员。
边界：本文是接口契约，不是实现证据；不得据此声明完整工作流工作台已完成。

## 1. Contract Principles

- Browser 只能调用 `/bff/pv21/*` 和静态资源。
- BFF 返回面向产品工作台的 DTO，不暴露 runtime store、raw provider payload、raw prompt、secret 或 connector internal payload。
- 所有 durable action 必须携带 `user_confirmation`。
- 所有 publish、rollback、run、human action 都必须返回 `audit_refs` 或 `denial`。
- 所有 DTO 必须携带 `workspace_id`、`project_id`、`app_id` 和 `workflow_id`，用于 scope review。
- 所有失败响应必须结构化，不能只返回字符串。

## 2. Common Types

### `PV21ScopeDTO`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `workspace_id` | string | yes | Workspace scope. |
| `project_id` | string | yes | Project scope. |
| `app_id` | string | yes | App scope. |
| `workflow_id` | string | yes | Workflow scope. |

### `PV21UserConfirmationDTO`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `confirmed` | boolean | yes | Must be true for publish, rollback, run and human action. |
| `reason` | string | yes | Human-readable reason. |
| `actor_id` | string | yes | User or reviewer id. |

### `PV21ErrorDTO`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `code` | string | yes | Stable machine-readable code. |
| `message` | string | yes | Simplified Chinese user-facing message. |
| `severity` | `info\|warning\|error\|fatal` | yes | UI handling level. |
| `field` | string | no | Related request field. |
| `node_id` | string | no | Related graph node. |
| `edge_id` | string | no | Related graph edge. |
| `audit_refs` | string[] | no | Denial or policy refs. |

## 3. Route Contracts

### `GET /bff/pv21/studio/state`

Purpose: load the initial complete Studio state.

Response `PV21StudioStateDTO`:

| Field | Type | Required |
| --- | --- | --- |
| `scope` | `PV21ScopeDTO` | yes |
| `node_library` | `PV21NodeTemplateDTO[]` | yes |
| `draft_graph` | `PV21WorkflowGraphDTO` | yes |
| `published_version` | `PV21WorkflowVersionDTO \| null` | yes |
| `version_history` | `PV21WorkflowVersionDTO[]` | yes |
| `run_history` | `PV21WorkflowRunSummaryDTO[]` | yes |
| `evidence_health` | `PV21EvidenceHealthDTO` | yes |
| `route_claims` | string[] | yes |

### `GET /bff/pv21/workflows/{workflow_id}/graph`

Purpose: read draft graph from backend truth.

Response: `PV21WorkflowGraphDTO`.

### `PUT /bff/pv21/workflows/{workflow_id}/graph`

Purpose: save draft graph.

Request:

| Field | Type | Required |
| --- | --- | --- |
| `scope` | `PV21ScopeDTO` | yes |
| `draft_revision` | number | yes |
| `nodes` | `PV21GraphNodeDTO[]` | yes |
| `edges` | `PV21GraphEdgeDTO[]` | yes |
| `layout` | object | yes |

Response:

| Field | Type | Required |
| --- | --- | --- |
| `graph` | `PV21WorkflowGraphDTO` | yes |
| `validation` | `PV21GraphValidationDTO` | yes |
| `audit_refs` | string[] | yes |

### `POST /bff/pv21/workflows/{workflow_id}/graph/validate`

Purpose: validate draft graph without publishing.

Request: `PV21WorkflowGraphDTO`.

Response: `PV21GraphValidationDTO`.

Validation must reject:

- unknown node type
- missing required node parameter
- invalid source/target handle
- disconnected required node
- run without published version
- business-specific node type registered in platform core

### `POST /bff/pv21/workflows/{workflow_id}/diff`

Purpose: compare draft graph with base version.

Request:

| Field | Type | Required |
| --- | --- | --- |
| `base_version_id` | string | yes |
| `draft_revision` | number | yes |

Response `PV21WorkflowDiffDTO`:

| Field | Type | Required |
| --- | --- | --- |
| `base_version_id` | string | yes |
| `draft_revision` | number | yes |
| `added_nodes` | string[] | yes |
| `removed_nodes` | string[] | yes |
| `changed_nodes` | string[] | yes |
| `changed_edges` | string[] | yes |
| `risk_summary` | string[] | yes |
| `publish_blocked` | boolean | yes |
| `user_confirmation_required` | boolean | yes |

### `GET /bff/pv21/workflows/{workflow_id}/versions`

Purpose: read version list and rollback candidates.

Response:

| Field | Type | Required |
| --- | --- | --- |
| `versions` | `PV21WorkflowVersionDTO[]` | yes |
| `published_version_id` | string | no |
| `rollback_candidates` | string[] | yes |

### `POST /bff/pv21/workflows/{workflow_id}/versions/publish`

Purpose: publish a draft as WorkflowVersion.

Request:

| Field | Type | Required |
| --- | --- | --- |
| `draft_revision` | number | yes |
| `diff_id` | string | yes |
| `user_confirmation` | `PV21UserConfirmationDTO` | yes |

Response:

| Field | Type | Required |
| --- | --- | --- |
| `version` | `PV21WorkflowVersionDTO` | yes |
| `audit_refs` | string[] | yes |
| `evidence_refs` | string[] | yes |

### `POST /bff/pv21/workflows/{workflow_id}/versions/{version_id}/rollback`

Purpose: mark a prior version as the active published version.

Request:

| Field | Type | Required |
| --- | --- | --- |
| `user_confirmation` | `PV21UserConfirmationDTO` | yes |
| `reason` | string | yes |

Response:

| Field | Type | Required |
| --- | --- | --- |
| `published_version` | `PV21WorkflowVersionDTO` | yes |
| `previous_version_id` | string | yes |
| `audit_refs` | string[] | yes |

Rollback must not delete prior versions, runs or evidence.

### `POST /bff/pv21/workflows/{workflow_id}/runs`

Purpose: run a published WorkflowVersion.

Request:

| Field | Type | Required |
| --- | --- | --- |
| `version_id` | string | yes |
| `user_confirmation` | `PV21UserConfirmationDTO` | yes |
| `input` | object | yes |

Response `PV21WorkflowRunDTO`:

| Field | Type | Required |
| --- | --- | --- |
| `run_id` | string | yes |
| `version_id` | string | yes |
| `state` | string | yes |
| `station_runs` | `PV21StationRunDTO[]` | yes |
| `trace_refs` | string[] | yes |
| `audit_refs` | string[] | yes |

### `GET /bff/pv21/runs/{run_id}/inspect`

Purpose: inspect WorkflowInstance and StationRun states.

Response: `PV21WorkflowRunDTO`.

### `POST /bff/pv21/runs/{run_id}/human-actions`

Purpose: answer a waiting human gate.

Request:

| Field | Type | Required |
| --- | --- | --- |
| `station_id` | string | yes |
| `decision` | `approve\|reject\|request_changes` | yes |
| `comment` | string | yes |
| `user_confirmation` | `PV21UserConfirmationDTO` | yes |

Response:

| Field | Type | Required |
| --- | --- | --- |
| `action_id` | string | yes |
| `resulting_run_state` | string | yes |
| `resulting_station_state` | string | yes |
| `audit_refs` | string[] | yes |

### `GET /bff/pv21/runs/{run_id}/evidence`

Purpose: aggregate evidence for Studio review.

Response `PV21EvidenceSummaryDTO`:

| Field | Type | Required |
| --- | --- | --- |
| `artifact_refs` | string[] | yes |
| `trace_refs` | string[] | yes |
| `quality_refs` | string[] | yes |
| `approval_refs` | string[] | yes |
| `claim_refs` | string[] | yes |
| `redaction_refs` | string[] | yes |
| `missing_refs` | string[] | yes |
| `no_false_green_status` | `pass\|fail\|not_run` | yes |

## 4. Forbidden Routes And Payloads

Browser must not call:

- `/v1/rpc`
- `/v1/internal/*`
- runtime store paths
- connector internal paths
- raw provider routes

BFF must not return:

- raw prompt
- raw provider payload
- secret value
- full connector stdout/stderr containing sensitive data
- private filesystem path outside evidence refs

## 5. Required Error Codes

| Code | Meaning |
| --- | --- |
| `PV21_SCOPE_DENIED` | Scope mismatch or tenant boundary denial. |
| `PV21_GRAPH_INVALID` | Graph validation failed. |
| `PV21_UNKNOWN_NODE_TYPE` | Node type is not registered in the generic node library. |
| `PV21_PUBLISH_BLOCKED` | Publish attempted with blocking validation errors. |
| `PV21_CONFIRMATION_REQUIRED` | Durable operation missing user confirmation. |
| `PV21_ROLLBACK_DENIED` | Rollback target invalid or unsafe. |
| `PV21_RUN_VERSION_REQUIRED` | Run attempted without published version. |
| `PV21_HUMAN_GATE_NOT_WAITING` | Human action attempted outside waiting gate. |
| `PV21_BROWSER_ROUTE_DENIED` | Browser tried a forbidden route. |
| `PV21_REDACTION_VIOLATION` | Response contains forbidden sensitive payload. |

