# PV22 External App Contract Acceptance Gate

用途：定义 PV22 出门验收门槛和失败条件。
阅读对象：测试、审计、开发、产品人员。
边界：本文是验收门槛，不是通过结果。

## PASS Conditions

- Contract registry 明确列出 external method/event/error/capability subset。
- Python SDK smoke PASS。
- TypeScript SDK smoke PASS。
- FastAPI full/minimal BFF template smoke PASS。
- Reference app E2E PASS。
- Negative fixtures 覆盖并通过 expected denial：
  - missing token
  - invalid token
  - origin mismatch
  - scope mismatch
  - capability denied
  - forbidden method
- Browser network log 证明外部浏览器不直连 `/v1/rpc` 或内部 runtime。
- Redaction scan PASS。
- No False Green scan PASS。

## FAIL Conditions

- 外部浏览器直连 raw Gateway 或 runtime store。
- `scope_mode=all` 被外部默认 auth 接受。
- Token 可越过 AppProfile allowed origins 或 default capabilities。
- Forbidden method 可由默认外部 token 调用。
- SDK 或 template smoke 只使用 mock，不读真实 Gateway/BFF 响应。
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

