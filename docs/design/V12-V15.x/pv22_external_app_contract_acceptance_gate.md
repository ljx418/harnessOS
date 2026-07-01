# PV22 External App Contract Acceptance Gate

用途：定义 PV22 出门验收门槛和失败条件。
阅读对象：测试、审计、开发、产品人员。
边界：本文是验收门槛，不是通过结果。

## PASS Conditions

- PV22-S1 及后续实现只有在 WP-M5A PASS 后执行；当前路线必须引用 `evidence/workflow-platform-main-entry/` 下 WP-M5A PASS 证据。如用户显式批准延期 WP-M5A，验收报告必须记录 deferred risk，且不得声明工作流平台业务场景产品化完成。
- Contract registry 明确列出 external method/event/error/capability subset。
- Python SDK smoke PASS。
- TypeScript SDK smoke PASS。
- FastAPI full/minimal BFF template smoke PASS。
- Reference app E2E PASS。
- `reference_app` 默认 AppProfile 可用，且不授予 admin/debug/internal capability。
- Negative fixtures 覆盖并通过 expected denial：
  - missing token
  - invalid token
  - origin mismatch
  - scope mismatch
  - capability denied
  - forbidden method
- Browser network log 证明外部浏览器不直连 `/v1/rpc` 或内部 runtime。
- PRD review report 逐项映射 PV22-F1 到 PV22-F9。
- Artifact manifest 覆盖 registry、SDK、template、negative fixture、reference app、browser network、redaction、No False Green 与 acceptance report。
- Redaction scan PASS。
- No False Green scan PASS。

## FAIL Conditions

- WP-M5A 未 PASS 且无用户显式延期批准时，PV22-S1 或后续实现已开始。
- 使用 PV22 SDK/template/reference app 证据替代工作流平台首页业务场景产品化、真实业务产物或 mock reduction 证据。
- 外部浏览器直连 raw Gateway 或 runtime store。
- `scope_mode=all` 被外部默认 auth 接受。
- Token 可越过 AppProfile allowed origins 或 default capabilities。
- Forbidden method 可由默认外部 token 调用。
- SDK 或 template smoke 只使用 mock，不读真实 Gateway/BFF 响应。允许 reference app 浏览器边界用 source scan 证明不直连 raw Gateway，但必须同时有真实 SDK/Gateway API path 证据。
- 报告出现生产可用、开放生态完成或商业化完成的正向声明。

## Allowed Claim

```text
PV22 external app contract ready for bounded integration review.
```

## Not Claimed

- production ready
- external ecosystem complete
- commercial readiness complete
- unrestricted third-party app access
- complete Workflow Studio ready
- Agent executor ready
