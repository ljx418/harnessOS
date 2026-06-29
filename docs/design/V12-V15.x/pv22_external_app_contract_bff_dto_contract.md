# PV22 External App Contract BFF / DTO Contract

用途：定义 PV22 外部 App 接入时 BFF facade、SDK DTO、错误模型和证据 DTO 的最小契约。
阅读对象：SDK、BFF、前端、后端、测试人员。
边界：本文是契约设计，不是实现证据；不得据此声明外部 App contract 已完成。

## 1. Contract Version

建议版本号：

```text
pv22.external_app_contract.v1
```

所有 PV22 evidence、DTO snapshot 和 acceptance data 都必须带该版本或显式子版本。

## 2. Required DTOs

| DTO | Required fields |
| --- | --- |
| `PV22ExternalAppProfileDTO` | schema_version, app_id, display_name, allowed_origins, default_capabilities, default_scope, compatibility_status. |
| `PV22CapabilityTokenRequestDTO` | app_id, project_id, workspace_id, requested_capabilities, requested_origins, expires_in_seconds, reason. |
| `PV22CapabilityTokenPreviewDTO` | app_id, scope, granted_capabilities, granted_origins, denied_capabilities, denied_origins, expires_at, redaction_status. |
| `PV22SdkSmokeResultDTO` | sdk_name, sdk_version, operations, status, error_refs, dto_snapshot_refs. |
| `PV22BffTemplateSmokeDTO` | template_id, routes, scope_binding_status, denylist_status, status. |
| `PV22ReferenceAppRunDTO` | app_id, route_boundary, operations, browser_requests, evidence_refs, status. |
| `PV22NegativeFixtureDTO` | fixture_id, request_summary, expected_error_code, actual_error_code, status. |
| `PV22ContractEvidenceDTO` | sdk_refs, template_refs, reference_app_refs, negative_fixture_refs, no_false_green_status, missing_refs. |

## 3. BFF Template Rules

External App BFF templates must:

- Accept browser requests only on app-owned business routes.
- Bind every upstream HarnessOS call to app/project/workspace scope.
- Forward or mint capability token only server-side.
- Map HarnessOS errors to stable external app errors.
- Log route boundary without secrets.
- Deny direct browser passthrough to `/v1/rpc`, `/v1/internal/*`, `/runtime/store`, `/debug/runtime`.

## 4. Stable Error Codes

| Error code | Meaning | Required fixture |
| --- | --- | --- |
| `AUTH_REQUIRED` | No token and dev mode disabled. | Missing token request. |
| `AUTH_FORBIDDEN` | Origin or token profile boundary mismatch. | Origin outside AppProfile. |
| `AUTH_INVALID` | Malformed Authorization header. | Bad bearer header. |
| `CAPABILITY_DENIED` | Token lacks requested capability. | Token without `workflows.write`. |
| `SCOPE_MISMATCH` | Requested scope differs from token scope. | Token scope A, request scope B. |
| `METHOD_FORBIDDEN` | Method is forbidden for external default auth. | Forbidden internal/debug method. |
| `APP_PROFILE_NOT_FOUND` | Unknown app profile. | Unknown app_id token. |

## 5. Route Boundary

PV22 evidence must distinguish:

| Route class | Browser allowed | BFF allowed | Notes |
| --- | --- | --- | --- |
| App-owned BFF routes | Yes | Yes | External app facade. |
| HarnessOS SDK HTTP routes from server | No browser direct | Yes | Server-side only. |
| `/v1/rpc` | No browser direct | Server-side only if contract method allowed. |
| `/v1/internal/*` | No | No by default. |
| raw runtime store/debug | No | No by default. |

## 6. No False Green Terms

PV22 DTOs and reports must not positively claim:

- production ready
- external ecosystem complete
- commercial readiness complete
- unrestricted third-party app access
- complete Workflow Studio ready
- Agent executor ready

