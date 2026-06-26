# PV17 Product Closed Loop Implementation Task Matrix

用途：把 PV17 开发计划拆成自动化开发可执行的任务矩阵。
阅读对象：开发 Agent、工程师、测试人员。
边界：本文只定义任务，不执行代码；PV16 `/bff/pv16/*` 来自 test-only BFF evidence route，PV17 只能把它作为参考，不能把它当作正式产品 API。

## 1. Read Order For Implementers

1. `TASKS.md`
2. `pv17_product_closed_loop_prd.md`
3. `pv17_product_closed_loop_target_architecture.md`
4. `pv17_product_closed_loop_bff_dto_contract.md`
5. `pv17_product_closed_loop_development_and_acceptance_plan.md`
6. `pv17_product_closed_loop_acceptance_runner_spec.md`
7. `pv17_product_closed_loop_acceptance_gate.md`
8. `pv17_product_closed_loop_implementation_readiness_audit.md`

## 2. Workstream Matrix

| Workstream | Stage | Files to touch | Required result | Tests/evidence |
| --- | --- | --- | --- | --- |
| Environment validation | PV17-E0 | dependency files only if needed | Python smoke can run or documented BLOCKED exists | API/CLI/pack smoke output |
| BFF DTO contracts | PV17-S1/S2/S4/S5 | `apps/api/routers/bff.py`, possible local BFF helper module | `/bff/pv17/*` route allowlist implemented with explicit DTOs | route log, DTO snapshots |
| Browser client | PV17-S1/S5 | `apps/workflow-console/src/api/workflowConsoleClient.ts`, `api/types.ts` | typed client methods for product state, entity mutation, run inspect, evidence summary | TS build/test, mocked client tests |
| Product Console UI | PV17-S1 | `App.tsx`, `ConsoleShell`, layout/panel components | user sees active workspace/project/app/workflow/station/health | browser screenshot, visible text assertions |
| Entity mutation UI | PV17-S2 | Console forms/panels, Station Agent panels | user can mutate product entities with audit refs and denial states | mutation report, denial fixture |
| Studio continuity | PV17-S3 | `WorkflowEditingPanel`, `WorkflowCanvas`, `WorkflowNodeCard`, `RightPanels` | graph/diff/version/confirm state stays in one context | graph round-trip, WorkflowDiff evidence |
| Runtime inspect UI | PV17-S4 | run panel / inspect drawer / right panels | user sees instance, station, trace, artifact, quality, approval refs | runtime inspect screenshot/report |
| Evidence review UI | PV17-S5 | evidence panel, operation evidence components | user sees claim-to-evidence, route boundary, redaction and lineage | evidence review screenshot/report |
| Acceptance automation | PV17-SA | future `tools/pv17/*`, Playwright spec | evidence package generated and runner fails missing evidence | acceptance report |

## 3. Non-Decision Defaults

- Route prefix: `/bff/pv17`.
- Evidence dir: `docs/design/V12-V15.x/evidence/pv17-product-closed-loop/`.
- Future runner command: `python3 tools/pv17/run_product_closed_loop_acceptance.py`.
- Future E2E helper command: `python3 tools/pv17/run_product_closed_loop_e2e.py`.
- Browser entry: main `apps/workflow-console` product route; `?studio=pv16-product-runtime-hardening` remains regression/reference only.
- Runtime path: BFF handoff to existing `GatewayService.workflow_instance_start` and inspect methods; no browser direct `/v1/rpc`.
- Data persistence: reuse current dev/local stores unless a separate persistence stage is approved.

## 4. Task Ordering

1. Restore local validation environment.
2. Add `/bff/pv17/system/health` and `/bff/pv17/product-console/state`.
3. Add typed `WorkflowConsoleClient` methods and DTO tests.
4. Add Product Console state UI and health/empty/failure states.
5. Add entity mutation routes and denial fixtures.
6. Connect Studio graph/diff/version/confirm flow.
7. Add runtime confirm-run and inspect DTOs through BFF.
8. Add Evidence Review panel.
9. Add Playwright browser scenario and evidence generation.
10. Add PV17 runner and close PV17-SA.

## 5. Stop Conditions

Stop implementation and return to docs if:

- product entity mutation requires direct runtime/store writes;
- `GatewayService.workflow_instance_start` cannot provide inspectable refs without inventing fake runtime evidence;
- existing frontend architecture cannot host a mainline Product Console without a large rewrite;
- test BFF must be used as the only source for `/bff/pv17/*`;
- local environment remains unresolved and no CI-equivalent runner is available;
- a required claim would imply production readiness or complete Studio.

## 6. Expected User Experience At PV17-SA

At PV17-SA, the reviewer should open one browser path and verify:

1. The active workspace, project, app and workflow are visible.
2. Station Agent configuration is visible and redacted.
3. A graph change can be proposed, reviewed, confirmed and versioned.
4. A run can be confirmed by the user.
5. Runtime inspect shows real refs for station, trace, artifact, quality and approval.
6. Evidence review explains exactly what the bounded claim proves and does not prove.
