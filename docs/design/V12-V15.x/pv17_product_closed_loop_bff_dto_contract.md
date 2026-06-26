# PV17 Product Closed Loop BFF DTO Contract

用途：冻结 PV17 产品闭环的正式 BFF route、DTO、调用链和禁止路径。
阅读对象：前端、后端、测试、审计人员和自动化开发 Agent。
边界：本文是实现目标合约，不是已实现 API 证据；PV16 `/bff/pv16/*` 来自 test-only BFF evidence route，PV17 只能把它作为参考，不能把它当作正式产品 API。

## 1. Contract Decision

PV17 使用正式 `/bff/pv17/*` route 作为产品闭环阶段 API。实现位置默认在 `apps/api/routers/bff.py`，允许在同文件内拆 helper，但不新增独立 runtime service。

原因：

- `apps/api/__init__.py` 已将 `bff.py` 注册为正式 `/bff` router。
- `apps/workflow-console/src/api/workflowConsoleClient.ts` 已默认使用 `/bff` base path。
- PV17 目标是主线化产品体验，不是继续依赖 `apps/workflow-console/e2e/bff_smoke_server.py` 的 test-only route。

## 2. Route Allowlist

| Route | Method | Stage | Purpose | Backend mapping |
| --- | --- | --- | --- | --- |
| `/bff/pv17/system/health` | GET | S1 | 返回 API、Gateway、WorkflowStore、frontend config 诊断。 | `GatewayService.health_ping`, `method_list` |
| `/bff/pv17/product-console/state` | GET | S1 | 返回 workspace/project/app/workflow/Station Agent/run/evidence summary。 | `app.list`, `workflow.template.list`, `workflow.instance.list` |
| `/bff/pv17/entities/workspaces` | POST | S2 | 创建或更新 workspace projection。 | `ScopeContext` + local product projection |
| `/bff/pv17/entities/projects` | POST | S2 | 创建或更新 project projection。 | `ScopeContext` + ownership policy |
| `/bff/pv17/entities/apps` | POST | S2 | 创建或更新 app projection。 | `core/apps/profiles.py` reference |
| `/bff/pv17/entities/station-agents` | POST | S2 | 创建或更新 Station Agent profile projection。 | `core/station_agents/contracts.py` |
| `/bff/pv17/studio/workflows/{workflow_template_id}` | GET | S3 | 返回 Studio graph、draft、version、inspector DTO。 | `workflow_template_get`, `workflow_version_list`, `workflow_board_get` |
| `/bff/pv17/studio/workflows/{workflow_template_id}/patches` | POST | S3 | 创建 WorkflowDiff / patch proposal。 | `GatewayService.workflow_patch_propose` |
| `/bff/pv17/studio/workflows/{workflow_template_id}/publish` | POST | S3 | 用户确认后发布 WorkflowVersion。 | `GatewayService.workflow_template_publish` |
| `/bff/pv17/runtime/workflows/{workflow_template_id}/confirm-run` | POST | S4 | 用户确认后启动 WorkflowInstance。 | `GatewayService.workflow_instance_start` |
| `/bff/pv17/runtime/instances/{workflow_instance_id}/inspect` | GET | S4 | 返回 run、station、trace、artifact、quality、approval refs。 | `workflow_instance_status`, `station_run_list`, `artifact_lineage`, `trace_list` |
| `/bff/pv17/evidence/instances/{workflow_instance_id}/summary` | GET | S5 | 返回 claim-to-evidence、route boundary、redaction、lineage summary。 | artifact/trace/operation evidence read models |

事件订阅优先复用现有 `/bff/events/subscribe`。PV17 不新增 browser 直连 `/v1/rpc` 的路径。

## 3. DTO Families

| DTO | Required fields | Must not include |
| --- | --- | --- |
| `PV17SystemHealthDTO` | `schema_version`, `status`, `api_status`, `gateway_status`, `workflow_store_status`, `frontend_config_status`, `created_at` | raw env values, provider secrets |
| `PV17ProductConsoleStateDTO` | `schema_version`, `workspace`, `project`, `app`, `workflows`, `station_agents`, `active_run`, `evidence_summary`, `audit_refs` | raw artifact content, raw provider payload |
| `PV17EntityMutationRequestDTO` | `scope`, `entity_kind`, `operation`, `user_confirmed`, `idempotency_key`, `payload` | direct runtime/store refs |
| `PV17EntityMutationResultDTO` | `schema_version`, `status`, `entity_ref`, `audit_ref`, `policy_decision_ref`, `denied_reason`, `redaction_status` | secret values, raw credentials |
| `PV17StudioWorkflowDTO` | `schema_version`, `workflow_template`, `draft`, `versions`, `graph`, `inspector`, `patch_queue`, `audit_refs` | React layout internals as runtime truth |
| `PV17WorkflowPatchRequestDTO` | `source`, `actor_type`, `user_confirmed`, `operation`, `patch`, `expected_revision` | source=agent durable mutation authority |
| `PV17PublishRequestDTO` | `user_confirmed`, `expected_draft_revision`, `version`, `source`, `idempotency_key` | silent publish/run |
| `PV17RunConfirmRequestDTO` | `user_confirmed`, `workflow_template_id`, `workflow_version_id`, `scope`, `source`, `idempotency_key` | direct executor payload |
| `PV17RuntimeInspectDTO` | `schema_version`, `workflow_instance`, `station_runs`, `runtime_event_refs`, `trace_refs`, `artifact_refs`, `quality_refs`, `approval_refs`, `audit_refs` | fixture-only runtime proof |
| `PV17EvidenceSummaryDTO` | `schema_version`, `claims`, `route_boundary`, `redaction`, `artifact_lineage`, `trace_timeline`, `missing_evidence`, `allowed_claim` | production readiness claim |

## 4. Browser Denylist

PV17 browser acceptance must fail if any request contains:

- `/v1/rpc`
- `/internal/runtime`
- `/runtime/store`
- `/api/runtime`
- `/debug/runtime`
- raw provider URL with credentials
- direct artifact content URL not mediated by redacted metadata route

## 5. Mapping From PV16 Pilot

| PV16 test-only route | PV17 formal target |
| --- | --- |
| `/bff/pv16/system/health` | `/bff/pv17/system/health` |
| `/bff/pv16/product-runtime/state` | `/bff/pv17/product-console/state` |
| `/bff/pv16/entities/mutate` | `/bff/pv17/entities/*` with entity-specific routes |
| `/bff/pv16/runtime/confirm-run` | `/bff/pv17/runtime/workflows/{workflow_template_id}/confirm-run` |
| `/bff/pv16/runtime/inspect/{run_ref}` | `/bff/pv17/runtime/instances/{workflow_instance_id}/inspect` |
| `/bff/pv16/deployment/hardening-smoke` | Not in PV17 product closed loop; keep deployment hardening for separate governance stage |
| `/bff/pv16/product-runtime/journey` | Product journey is proven by browser scenario and evidence package, not a standalone formal API |

## 6. Implementation Rules

- Backend DTOs must be explicit Pydantic models or explicit serializer helpers with fixed required fields.
- Frontend DTO types must live beside `WorkflowConsoleClient` or existing `api/types.ts` patterns.
- Every mutation route must require `user_confirmed=true`, `source`, `idempotency_key` and scope.
- Every response must carry `schema_version`, `audit_ref` or `audit_refs`, and `redaction_status` where applicable.
- `source=agent` may propose patches but cannot publish, run or perform durable mutation.
- Errors must be visible to the browser as structured denial/failure DTOs, not hidden in logs.

## 7. Acceptance Requirements

PV17 route/DTO implementation cannot pass unless:

- browser route log shows only the allowlist;
- DTO snapshots exist for S1-S5;
- entity mutation negative fixtures exist;
- runtime inspect includes non-empty `runtime_event_refs`, `trace_refs`, `artifact_refs` and `quality_refs`;
- evidence summary maps every positive claim to evidence refs;
- No False Green and redaction scans pass.
