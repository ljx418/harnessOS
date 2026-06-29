# PV22 External App Contract PRD

用途：定义 PV22 Path B 外部应用接入契约阶段的产品目标、用户体验、功能边界和验收口径。
阅读对象：产品、架构、SDK、BFF、测试、审计人员。
边界：本文是开发规格，不是实现证据；不得据此声明生产可用、外部应用生态完成或商业化准备完成。

## 1. Background

PV17 到 PV21 已经证明 HarnessOS 可以通过有界 BFF / DTO 路径完成产品闭环、业务 OPC、runtime workflow、Agent executor 候选能力和 Workflow Studio 候选闭环。下一阶段需要把这些内部能力整理成外部应用可安全接入的契约，避免每个业务应用重新理解 Gateway、scope、capability、BFF facade 和事件模型。

PV22 的任务不是新增一个业务页面，而是让外部应用开发者可以按标准模板接入 HarnessOS：

```text
External App -> SDK / BFF Template -> Capability Token / Scope Binding -> Gateway RPC / BFF DTO -> Evidence
```

## 2. Product Goal

PV22 目标体验：

1. 外部 App 开发者可以阅读一份 contract，知道哪些 API、SDK、事件、错误和权限是稳定入口。
2. 开发者可以用 Python SDK 或 TypeScript SDK 完成最小 smoke：创建会话、提交 turn、读取事件、读取 artifact。
3. 开发者可以用 BFF template 构建自己的 app facade，而不让浏览器直连 `/v1/rpc` 或内部 runtime。
4. 应用所有请求都绑定 `app_id`、`project_id`、`workspace_id` 和 capability token。
5. 负向权限用例清晰可审：origin mismatch、scope mismatch、capability denied、forbidden method。
6. reference app 能以外部应用身份完成一条最小端到端路径，并生成证据包。

允许的阶段出口声明：

```text
PV22 external app contract ready for bounded integration review.
```

该声明只表示外部应用接入契约进入有界集成审查，不等于生产可用、开放生态完成或商业化完成。

## 3. Target Users

| User | Need | PV22 responsibility |
| --- | --- | --- |
| External app developer | 快速接入 HarnessOS 并完成最小调用。 | SDK quickstart、BFF template、reference app smoke。 |
| Platform engineer | 冻结可维护的外部 contract。 | Protocol version、method/event/error registry、compatibility policy。 |
| Security reviewer | 审查 scope、origin、capability 和 forbidden method。 | Token claims、negative fixtures、route boundary。 |
| Business app owner | 基于模板构建自己的业务 App。 | App profile、BFF facade、evidence checklist。 |

## 4. Functional Requirements

| ID | Requirement | Acceptance expectation |
| --- | --- | --- |
| PV22-F1 | 定义 external app protocol version 和稳定 contract 文档。 | Contract 文档列出 method/event/error/capability 范围。 |
| PV22-F2 | Python SDK smoke 覆盖 session、turn、event、artifact read。 | SDK 测试 PASS，输出 DTO snapshot。 |
| PV22-F3 | TypeScript SDK smoke 覆盖同等最小路径。 | SDK build/test PASS，输出 DTO snapshot。 |
| PV22-F4 | BFF template 支持 scope binding、capability forwarding 和 route denylist。 | Template smoke PASS，浏览器不直连 raw runtime。 |
| PV22-F5 | Reference app 作为外部 App 完成最小端到端路径。 | Browser/API evidence package PASS。 |
| PV22-F6 | Capability token 明确绑定 app/profile/origin/scope/capabilities。 | 正向 token PASS；越权 token FAIL。 |
| PV22-F7 | 错误模型稳定且开发者可处理。 | AUTH_REQUIRED、AUTH_FORBIDDEN、CAPABILITY_DENIED、SCOPE_MISMATCH、METHOD_FORBIDDEN 均有 fixtures。 |
| PV22-F8 | 兼容性策略明确。 | 版本号、deprecated 字段、migration notes 和 breaking-change gate 可审。 |
| PV22-F9 | 证据包可审。 | SDK logs、BFF route log、negative fixture report、No False Green、redaction PASS。 |

## 5. Scope

### In Scope

- `sdk/python` 和 `sdk/typescript` 的最小 smoke 契约。
- `templates/bff/fastapi`、`templates/bff/fastapi_minimal` 的接入模板验收。
- `examples/reference_app` 或等价 reference app 的外部接入路径。
- `apps/api/auth.py`、`core/apps/profiles.py`、`core/protocol/auth.py` 相关契约审查。
- Method/event/error/capability registry 的文档化与测试口径。

### Out Of Scope

- 生产 SLA、计费、限额、商业发布。
- 开放插件市场或第三方 MCP 商店。
- 完整业务 Pack 产品化。
- 生产多租户治理硬化；该工作属于 PV23。

## 6. Experience Flow

1. 开发者注册或选择一个 `AppProfile`。
2. 开发者生成或配置 capability token。
3. 开发者用 SDK 调用 HarnessOS 最小流程。
4. 浏览器应用通过自己的 BFF template 调用 HarnessOS，而不是直连 runtime。
5. 开发者查看 route log、error report 和 evidence package。
6. 审计人员验证 scope/capability/origin negative fixtures。

## 7. Red Lines

- 外部浏览器不得直接调用 `/v1/rpc`、`/v1/internal/*` 或 runtime store。
- Token 不得超出 AppProfile 的 allowed origins 或 default capabilities。
- External app 不得使用 `scope_mode=all`。
- Method registry 中标记 forbidden 的方法不得通过默认外部 auth 调用。
- 不得把 SDK smoke 或 template smoke 宣称为生产可用。

## 8. Success Metrics

| Metric | Target |
| --- | --- |
| Contract completeness | Method/event/error/capability 表完整覆盖最小外部接入路径。 |
| SDK smoke | Python 和 TypeScript smoke PASS。 |
| BFF template smoke | FastAPI full/minimal template PASS。 |
| Reference app E2E | 外部 app 最小路径 PASS。 |
| Negative fixtures | origin/scope/capability/forbidden method 全部 FAIL as expected。 |
| No False Green | 不出现 production ready、ecosystem complete、commercial ready 误报。 |

