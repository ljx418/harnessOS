# PV19 Runtime Workflow Platform Implementation Task Matrix

用途：把 PV19 后续实现拆成明确工程任务，避免后续 Agent 在入口、route、状态机、样例和验收上做二次决策。
阅读对象：开发、测试、架构、审计人员。
边界：本文是实现任务矩阵，不是代码实现，不产生 PASS 声明。

## 1. Stage Task Matrix

| Stage | Required implementation | Concrete code entities | Required tests/evidence |
| --- | --- | --- | --- |
| PV19-S1 工作台入口 | 新增 PV19 工作台入口，根路径不得作为空白交付体验。 | `apps/workflow-console/src/App.tsx`, `apps/workflow-console/src/ui/pv19/PV19RuntimeWorkbench.tsx`, `apps/workflow-console/src/ui/pv19/pv19-runtime-workbench.css` | browser screenshot, state DTO snapshot, `workbench_loads` E2E。 |
| PV19-S2 Graph roundtrip | 画布编辑生成可 readback 的 WorkflowSpecGraph，包含 human gate station。 | `WorkflowConsoleClient`, `apps/api/routers/bff.py`, `core/workflows/models.py`, `core/workflows/store.py` | `workflow-graph-roundtrip-report.json`, graph validation negative fixtures。 |
| PV19-S3 WorkflowDiff publish | WorkflowDiff 必须人工确认后发布 WorkflowVersion。 | `apps/api/routers/bff.py`, `WorkflowStore.publish_template`, `WorkflowVersion` | `workflow-version-publish-report.json`, publish-without-confirm denied。 |
| PV19-S4 Runtime run inspect | Run 必须引用已发布 `workflow_version_id` 并产生 WorkflowInstance / StationRun。 | `apps/api/routers/bff.py`, `apps/api/routers/runs.py`, `GatewayService`, `WorkflowInstance`, `StationRun` | `runtime-run-inspect-report.json`, browser route denylist。 |
| PV19-S5 Human gate | human action 必须更新 approval/handoff/workflow state，并保留 before/after。 | `apps/gateway/approvals.py`, handoff repository in `apps/api/routers/bff.py`, `WorkflowStore.update_instance`, `WorkflowStore.update_station_run` | `human-interaction-report.json`, `human_gate_ui_only_denied`。 |
| PV19-S6 Evidence review | 聚合 artifacts、trace、quality、audit、claim matrix。 | `apps/gateway/artifacts.py`, `apps/gateway/traces.py`, `apps/gateway/service.py`, `apps/api/routers/bff.py` | `evidence-review-report.json`, `claim-to-evidence-matrix.json`, redaction scan。 |
| PV19-SA Aggregate | 运行聚合验收并写入审计结论。 | `tools/pv19/run_runtime_workflow_platform_acceptance.py`, `apps/workflow-console/e2e/pv19_cdp_acceptance.mjs` | `acceptance-data.json`, `artifact-manifest.json`, `audit-closure.md`。 |

## 2. Fixed Product Decisions

| Decision | Locked choice |
| --- | --- |
| Browser entry | `?studio=pv19-runtime-workflow-platform` loads PV19 workbench. Root path must redirect to or visibly link to a real workbench; it cannot remain the accepted empty delivery path. |
| Primary business sample | Knowledge OPC workflow is the primary real-data sample. |
| Platform generality sample | folder-summary/reference workflow is the non-Knowledge reuse check. |
| Human gate representation | Use existing station approval fields and workflow waiting states; do not add a business-specific human node model. |
| BFF route set | Use `/bff/pv19/*` from the DTO contract; do not count `/bff/v13/*`, `/bff/pv17/*` or `/bff/pv18/*` as PV19 route evidence. |
| Evidence location | `docs/design/V12-V15.x/evidence/pv19-runtime-workflow-platform/`。 |

## 3. Implementation Blockers

- Any implementation task that requires new business-specific Core/Gateway/App shell branches must stop and update architecture docs before coding.
- Any inability to update backend runtime state from human action must stop before UI polish.
- Any route substitution away from `/bff/pv19/*` must stop unless the PV19 BFF DTO contract is revised first.
- Any claim that PV19 proves production readiness, complete Studio or complete Agent executor must fail acceptance.

