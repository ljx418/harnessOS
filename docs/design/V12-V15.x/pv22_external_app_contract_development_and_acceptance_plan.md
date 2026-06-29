# PV22 External App Contract Development And Acceptance Plan

用途：定义 PV22-R0 到 PV22-SA 的开发顺序、验收步骤和审计闭环。
阅读对象：开发、测试、架构、审计人员。
边界：本文是计划，不是实现证据；不得据此声明 PV22 已完成。

## 1. Stage Goal

PV22 要把 SDK、BFF template、reference app、capability token 和 method/event/error registry 收敛成可复现的外部应用接入契约。

## 2. Substages

| Stage | Goal | Development output | Acceptance output |
| --- | --- | --- | --- |
| PV22-R0 | 文档与 readiness。 | PRD、架构、DTO、任务矩阵、验收门槛。 | readiness audit Go/No-Go。 |
| PV22-S1 | Contract registry。 | external method/event/error/capability registry。 | registry snapshot + no forbidden method drift。 |
| PV22-S2 | SDK smoke。 | Python/TypeScript smoke scripts。 | SDK smoke PASS + DTO snapshots。 |
| PV22-S3 | BFF template smoke。 | FastAPI full/minimal template test harness。 | template route boundary PASS。 |
| PV22-S4 | Capability negative fixtures。 | token/origin/scope/capability denial fixtures。 | expected-denial report PASS。 |
| PV22-S5 | Reference app E2E。 | reference app external flow。 | browser/API evidence PASS。 |
| PV22-SA | Aggregate audit. | evidence package + report. | claim-to-evidence, redaction, No False Green PASS。 |

## 3. Acceptance Commands To Define During Implementation

```bash
# Python SDK smoke
.venv/bin/pytest tests/test_pv22_python_sdk_external_contract.py -q

# TypeScript SDK smoke
cd sdk/typescript && npm test

# BFF template smoke
.venv/bin/pytest tests/test_pv22_bff_template_contract.py -q

# Reference app E2E
cd examples/reference_app && npm run test:e2e
```

这些命令是目标形态，PV22-R0 不得把它们写成已通过事实。

## 4. Evidence Package

PV22-SA 应生成：

- `evidence/pv22-external-app-contract/sdk-smoke-report.json`
- `evidence/pv22-external-app-contract/bff-template-smoke-report.json`
- `evidence/pv22-external-app-contract/reference-app-e2e-report.html`
- `evidence/pv22-external-app-contract/negative-fixtures.json`
- `evidence/pv22-external-app-contract/browser-network-log.json`
- `evidence/pv22-external-app-contract/no-false-green-scan.txt`
- `evidence/pv22-external-app-contract/artifact-manifest.json`

## 5. Go / No-Go

进入实质实现前必须满足：

- R0 文档完整。
- Contract subset 明确。
- Negative fixtures 明确。
- 不引入生产可用或开放生态完成声明。
- 不要求业务 Pack 或生产治理提前完成。

