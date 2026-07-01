# WP-M5B PV22 Readiness Refresh Plan And Audit

用途：在 PV22-S1 实质实现前，确认外部应用接入契约已经对齐 WP-M5A 后的 PV13-based Workflow Platform host surface。
阅读对象：开发、测试、架构、审计人员。
边界：本文是实现前审计，不是 PV22 实现证据。

## 1. Stage Goal

WP-M5B 的目标不是新增业务功能，而是把 PV22 External App Contract 的进入条件从“WP-M5A 阻塞”刷新为“WP-M5A 已通过后的有界实现可进入”，并防止 PV22 绕开工作流平台首页、业务场景产物和治理边界。

## 2. Evidence Inputs

| Evidence | Required state |
| --- | --- |
| `evidence/workflow-platform-main-entry/acceptance-data.json` | WP-M1 到 WP-M5A bounded acceptance PASS。 |
| `evidence/workflow-platform-main-entry/scenario-projection-report.json` | 三个业务场景 DTO projection 可审。 |
| `evidence/workflow-platform-main-entry/business-output-report.json` | 文档总结、代码审查、会议简报输出摘要可审。 |
| `evidence/workflow-platform-main-entry/mock-reduction-report.json` | 明确哪些数据来自 BFF/DTO/evidence，哪些仍为 bounded placeholder。 |
| `evidence/workflow-platform-main-entry/artifact-manifest.json` | Evidence package 可复核。 |

## 3. PV22 Implementation Entry

| Area | Concrete entity | Entry rule |
| --- | --- | --- |
| Contract registry | `core/protocol/contracts/pv22_external_app_contract.py` | 先冻结 method/event/error/capability subset，再进入 SDK/template/reference app。 |
| App profile | `core/apps/profiles.py` | `reference_app` profile 必须绑定 allowed origins、default capabilities、contract metadata。 |
| Python SDK | `sdk/python/harnessos_client/*` | 通过真实 FastAPI TestClient `/v1/rpc` Gateway smoke。 |
| TypeScript SDK | `sdk/typescript/src/*` | 与 server default method subset 对齐并通过 `npm test`。 |
| BFF templates | `templates/bff/fastapi/*`, `templates/bff/fastapi_minimal/*` | Browser route 不直连 raw Gateway，BFF 通过 SDK 调用。 |
| Reference app | `examples/reference_app/*` | 前端只调用 `/bff/*`，并有真实 SDK/Gateway API path 证据。 |
| Evidence | `evidence/pv22-external-app-contract/*` | 独立记录 registry、SDK、template、negative fixture、reference app、redaction、No False Green、PRD review。 |

## 4. Audit Opinion Closure

| Audit opinion | Severity | Closure |
| --- | --- | --- |
| PV22-S1 不得绕过 WP-M5A | High | Closed: WP-M5A PASS evidence 已存在。 |
| PV22 不得替代工作流平台业务产物验收 | High | Closed by boundary: PV22 reports only external contract bounded review。 |
| Reference app 不得只跑 mock | Medium | Closed by plan: source boundary scan + real SDK/Gateway API path。 |
| Browser 不得直连 `/v1/rpc` | High | Closed by plan: browser-network-log 和 reference app source scan。 |
| Token/capability 负向夹具必须覆盖 | High | Closed by plan: missing/invalid token、origin/scope/capability/forbidden method/scope_mode=all。 |

## 5. Decision

Status: GO for PV22-S1..SA bounded automated implementation.

允许声明：

```text
PV22 external app contract ready for bounded integration review.
```

不得声明 production ready、external ecosystem complete、commercial readiness complete、unrestricted third-party app access、complete Workflow Studio ready 或 Agent executor ready。
