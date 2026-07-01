# PV22 External App Contract Development And Acceptance Plan

用途：定义 PV22-R0 到 PV22-SA 的开发顺序、验收步骤和审计闭环。
阅读对象：开发、测试、架构、审计人员。
边界：本文是计划，不是实现证据；不得据此声明 PV22 已完成。

## 1. Stage Goal

PV22 要把 SDK、BFF template、reference app、capability token 和 method/event/error registry 收敛成可复现的外部应用接入契约。

## 1.1 Stage Prerequisite

PV22 是外部应用接入契约阶段，不替代工作流平台首页、业务场景产品化或真实业务产物验收。进入 PV22-S1 前必须满足以下条件之一：

- WP-M5A 已通过，且已落盘 `evidence/workflow-platform-main-entry/scenario-projection-report.json`、`business-output-report.json`、`mock-reduction-report.json`、`business-scenario-groups.json` 与三类业务场景产物证据。
- 用户显式批准延期 WP-M5A，并接受 PV22 先行会降低工作流平台业务体验闭环可信度的风险。

如果以上条件均不满足，PV22 只能停留在 R0 文档 readiness，不得进入 registry、SDK、template 或 reference app 实现。

当前审计状态：WP-M5A evidence package 已存在，且 `workflow_platform_wp_m5a_business_scenario_productization_plan_and_audit.md`、`workflow-platform-main-entry/acceptance-data.json` 和 `artifact-manifest.json` 已记录 WP-M5A 有界 PASS。因此 PV22 可以进入 WP-M5B readiness refresh 与 PV22-S1 bounded implementation；但仍不得把 WP-M5A/PV22 任一证据宣称为生产可用、完整工作流平台 GA 或外部生态完成。

## 1.2 WP-M5B Readiness Refresh

PV22-S1 开始前执行 WP-M5B：

| Check | Required result |
| --- | --- |
| PV13-based workflow platform host surface | 仍以 `apps/workflow-console/src/ui/v13/V13EditableStudio.tsx` 和 `v13-editable-studio.css` 为目标首页体验基线。 |
| Business scenario evidence | 引用 WP-M5A 三类业务场景与 mock-reduction 证据，不由 PV22 重新声明业务产物完成。 |
| External app route boundary | reference app 浏览器只允许访问 `/bff/*`，由 BFF/SDK 访问 Gateway。 |
| Contract implementation entry | 从 `core/protocol/contracts/pv22_external_app_contract.py` 冻结 method/event/error/capability subset。 |
| Evidence package | PV22 evidence 独立写入 `evidence/pv22-external-app-contract/`。 |

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

## 2.1 Substage Development / Acceptance Loop

每个子阶段执行顺序固定为：

1. 根据 PRD 与 Target Architecture 写入或更新本子阶段验收标准。
2. 审计是否存在致命/重大规格偏差；无新增 blocker 才进入代码实现。
3. 使用真实代码实体与真实 Gateway/SDK/BFF 路径执行自动化验收。
4. 写入 evidence package、PRD review report 和 command log。
5. 若 FAIL，回到本子阶段计划与实现，不得进入下一子阶段。

PV22 本轮允许把 PV22-S1..SA 合并到一个自动化 runner 中执行，但报告必须仍按 registry、SDK、template、negative fixtures、reference app、aggregate audit 分组。

## 3. Acceptance Commands To Define During Implementation

```bash
# PV22 aggregate + Python SDK/Gateway/BFF/reference app smoke
.venv/bin/python -m pytest tests/test_pv22_external_app_contract.py -q

# TypeScript SDK smoke
cd sdk/typescript && npm test

# Regression slices for existing SDK/template/reference app baselines
.venv/bin/python -m pytest tests/test_v3_5_python_sdk.py tests/test_v3_5_typescript_sdk.py tests/test_v3_5_bff_template_e2e.py tests/test_v3_5_bff_minimal_smoke.py tests/test_v3_5_reference_app.py -q
```

这些命令是目标形态，PV22-R0 不得把它们写成已通过事实。

## 4. Evidence Package

PV22-SA 应生成：

- `evidence/pv22-external-app-contract/sdk-smoke-report.json`
- `evidence/pv22-external-app-contract/bff-template-smoke-report.json`
- `evidence/pv22-external-app-contract/reference-app-e2e-report.html`
- `evidence/pv22-external-app-contract/reference-app-e2e-report.json`
- `evidence/pv22-external-app-contract/negative-fixtures.json`
- `evidence/pv22-external-app-contract/browser-network-log.json`
- `evidence/pv22-external-app-contract/contract-registry-snapshot.json`
- `evidence/pv22-external-app-contract/prd-review-report.json`
- `evidence/pv22-external-app-contract/acceptance-data.json`
- `evidence/pv22-external-app-contract/acceptance-report.html`
- `evidence/pv22-external-app-contract/no-false-green-scan.txt`
- `evidence/pv22-external-app-contract/artifact-manifest.json`

## 5. Go / No-Go

进入实质实现前必须满足：

- R0 文档完整。
- WP-M5A 已 PASS，或用户显式批准延期并记录风险；当前路线采用 WP-M5A PASS evidence 后进入 PV22。
- Contract subset 明确。
- Negative fixtures 明确。
- 不引入生产可用或开放生态完成声明。
- 不要求生产治理提前完成；但不得跳过工作流平台业务场景产品化、真实业务产物和 mock reduction 证据。
