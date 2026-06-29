# PV21 Complete Workflow Studio Implementation Task Matrix

用途：把 PV21 开发内容拆解为可执行任务和验收任务。
阅读对象：开发、测试、架构、审计人员。
边界：本文是任务矩阵，不是实现证据；不得据此声明完整工作流工作台已完成。

## 1. Task Matrix

| ID | Area | Task | Code entities | Acceptance |
| --- | --- | --- | --- | --- |
| PV21-T1 | Browser | 新增 PV21 Studio route 和 shell。 | `App.tsx`, `PV21CompleteWorkflowStudio.tsx` | 首屏截图非空；包含画布、节点库、Inspector、版本、运行、evidence 区。 |
| PV21-T2 | Browser / API | 增加 PV21 frontend DTO types 和 API client。 | `types/pv21.ts`, `lib/api.ts` | Type check；network log 无 raw runtime route。 |
| PV21-T3 | BFF | 增加 `/bff/pv21/studio/state`。 | `apps/api/routers/bff.py` | State DTO snapshot。 |
| PV21-T4 | BFF / Workflow | 增加 graph GET/PUT/validate routes。 | `bff.py`, `core/workflows/*` | Graph roundtrip 和 validation negative fixtures。 |
| PV21-T5 | Browser | 实现节点库、画布操作、Inspector 和 validation overlay。 | canvas components, PV21 shell | Browser E2E 编辑路径截图。 |
| PV21-T6 | Workflow | 实现 WorkflowDiff DTO 和版本比较。 | `core/workflows/*`, Gateway facade | Diff report。 |
| PV21-T7 | Workflow | 实现 publish 和 rollback facade。 | `core/workflows/*`, `apps/gateway/service.py` | Version publish/rollback report、audit refs。 |
| PV21-T8 | Runtime | 从 Studio 启动已发布 WorkflowVersion。 | BFF run route, Gateway runtime facade | Runtime run inspect report。 |
| PV21-T9 | Runtime / Human | 实现 human action BFF route 和 state transition readback。 | BFF, approvals, workflow runtime | Human action transition report。 |
| PV21-T10 | Evidence | 实现 evidence summary aggregator。 | artifacts, traces, approvals, quality stores | Evidence summary report。 |
| PV21-T11 | Testing | 新增 PV21 backend acceptance runner。 | acceptance scripts/tests | Acceptance-data PASS/FAIL。 |
| PV21-T12 | Testing | 新增 Browser E2E 和截图证据。 | Playwright/Chrome CDP runner | Home/edit/version/evidence screenshots。 |
| PV21-T13 | Audit | 新增 PRD spec review、architecture review、UX review。 | reports/evidence docs | Audit closure 无 fatal/major。 |
| PV21-T14 | Guardrail | No False Green、redaction、platform generality scan。 | scripts or reports | 扫描 PASS。 |

## 2. Suggested Implementation Order

1. PV21-T1, PV21-T2, PV21-T3。
2. PV21-T4, PV21-T5。
3. PV21-T6, PV21-T7。
4. PV21-T8, PV21-T9。
5. PV21-T10。
6. PV21-T11, PV21-T12, PV21-T13, PV21-T14。

## 3. Review Ownership

| Review | Owner role | Required before next substage |
| --- | --- | --- |
| PRD spec review | Product / QA | Yes |
| Target architecture review | Architecture | Yes |
| Platform generality review | Architecture / backend | Yes |
| Browser UX review | Product / frontend / QA | Yes |
| Evidence review | QA / audit | Yes |
| No False Green | QA / audit | Yes |

## 4. Implementation Red Lines

- No business-only core branch.
- No browser direct runtime/internal API.
- No mock-only PASS.
- No deletion of historical version/run/evidence.
- No automated publish/rollback/human action without user confirmation.
- No positive production, Xpert parity or completed product-grade frontend claim.

