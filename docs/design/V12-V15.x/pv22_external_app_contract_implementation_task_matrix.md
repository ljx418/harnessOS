# PV22 External App Contract Implementation Task Matrix

用途：把 PV22 开发拆成可执行任务和验收任务。
阅读对象：开发、测试、架构、审计人员。
边界：本文是任务矩阵，不是实现证据。

| ID | Area | Task | Code entities | Acceptance |
| --- | --- | --- | --- | --- |
| PV22-T1 | Contract | 定义 external method/event/error/capability registry。 | `core/protocol/*`, docs registry | Registry snapshot。 |
| PV22-T2 | Auth | 增加 token/origin/scope/capability negative fixtures。 | `apps/api/auth.py`, tests | Expected denial PASS。 |
| PV22-T3 | Python SDK | 增加 external app smoke。 | `sdk/python/harnessos_client/*` | Python SDK smoke PASS。 |
| PV22-T4 | TypeScript SDK | 增加 external app smoke。 | `sdk/typescript/src/*` | TS SDK build/test PASS。 |
| PV22-T5 | BFF Template | 验证 FastAPI full template。 | `templates/bff/fastapi/*` | Template smoke PASS。 |
| PV22-T6 | Minimal Template | 验证 FastAPI minimal template。 | `templates/bff/fastapi_minimal/*` | Minimal smoke PASS。 |
| PV22-T7 | Reference App | 跑通外部 App E2E。 | `examples/reference_app/*` | Browser/API report。 |
| PV22-T8 | Evidence | 汇总 evidence package。 | `docs/design/V12-V15.x/evidence/pv22-external-app-contract/*` | Artifact manifest。 |
| PV22-T9 | Redaction | 扫描 token、secret、raw prompt 泄漏。 | reports/scripts | Redaction PASS。 |
| PV22-T10 | No False Green | 扫描生产/生态/商业化误报。 | reports/scripts | No False Green PASS。 |

## Implementation Status

| Group | Status | Evidence |
| --- | --- | --- |
| PV22-S1 / T1 Contract registry | PASS | `evidence/pv22-external-app-contract/contract-registry-snapshot.json`。 |
| PV22-S2 / T3-T4 SDK smoke | PASS | `sdk-smoke-report.json`、`validation-typescript-sdk.log`。 |
| PV22-S3 / T5-T6 BFF template smoke | PASS | `bff-template-smoke-report.json`。 |
| PV22-S4 / T2 negative fixtures | PASS | `negative-fixtures.json`。 |
| PV22-S5 / T7 reference app E2E boundary | PASS | `reference-app-e2e-report.json`、`browser-network-log.json`。 |
| PV22-SA / T8-T10 aggregate audit | PASS | `acceptance-data.json`、`acceptance-report.html`、`prd-review-report.json`、`redaction-scan.txt`、`no-false-green-scan.txt`、`artifact-manifest.json`。 |

## Suggested Order

1. PV22-T1, PV22-T2。
2. PV22-T3, PV22-T4。
3. PV22-T5, PV22-T6。
4. PV22-T7。
5. PV22-T8, PV22-T9, PV22-T10。

## Red Lines

- No browser raw `/v1/rpc` passthrough.
- No external default admin/debug/internal capability.
- No scope escalation.
- No mock-only PASS.
- No production or commercial readiness claim.

## Allowed Exit Claim

```text
PV22 external app contract ready for bounded integration review.
```
