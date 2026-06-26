# PV17 Product Closed Loop Development And Acceptance Plan

用途：把路径1拆成可执行开发与验收阶段。
阅读对象：开发、测试、产品、审计人员。
边界：本文是开发及验收计划；在实际代码和证据生成前，不产生任何 PASS 声明。
PV16 `/bff/pv16/*` 来自 test-only BFF evidence route，PV17 只能把它作为参考，不能把它当作正式产品 API。

## 1. Stage Outline

| Stage | 用户可见效果 | 开发对象 | 验收证据 |
| --- | --- | --- | --- |
| PV17-R0 | Reviewer 看到路径1已选、范围、风险、代码实体和 No-Go。 | 文档、drawio、索引、stage gate。 | 文档存在性、drawio 页数、No False Green 扫描。 |
| PV17-S1 | 用户打开一个主线 Product Console，看到 workspace/project/app/workflow/Station Agent/system health。 | `App.tsx`, `ConsoleShell`, `WorkflowConsoleClient`, `apps/api/routers/bff.py`。 | browser screenshot、BFF route log、DTO snapshot、health/config evidence。 |
| PV17-S2 | 用户通过正式 BFF 创建或更新 workspace/project/app/Station Agent，并看到 audit refs 和 denial reason。 | BFF mutation routes、Station Agent DTO、scope/ownership policy。 | entity mutation report、negative fixtures、redaction scan。 |
| PV17-S3 | 用户在 Studio 中从 WorkflowDiff/patch 到 WorkflowVersion，再确认 run。 | `WorkflowEditingPanel`, `WorkflowCanvas`, `WorkflowRepository`, `GatewayService.workflow_patch_*`, `workflow_template_publish`。 | graph round-trip、WorkflowDiff、publish handoff、network denylist。 |
| PV17-S4 | 用户运行 WorkflowInstance，并在同一 UI 中 inspect station runs、trace、artifact、quality、approval。 | `GatewayService.workflow_instance_start/status`, `station_run_list`, `artifact_lineage`, `trace_list`, BFF inspect DTO。 | runtime run inspect report、event log、trace/artifact/quality refs、screenshots。 |
| PV17-S5 | 用户在 Evidence/Operations 视图检查 claim-to-evidence、route boundary、redaction、artifact lineage。 | evidence panel、operation evidence store、acceptance runner。 | claim-to-evidence matrix、No False Green、redaction、route denylist。 |
| PV17-SA | Reviewer 接受一个 bounded 产品闭环实现结论。 | aggregate runner、artifact manifest、audit closure。 | acceptance-data、artifact-manifest、audit closure、allowed claim。 |

## 2. 入口前置条件

PV17 实现不能开始，直到：

- 本地 Python 环境恢复或被文档化，解决 `.venv/bin/python` shim 和 `pydantic_settings` 缺失问题。
- 轻量 smoke 能重新执行或明确记录阻塞：
  - `tests/test_api_runs.py`
  - `tests/test_cli_headless.py`
  - `tests/test_pack_registry.py`
  - Meeting / Knowledge pack assembly tests
- PV17 文档和 drawio 通过本计划的文档验收。
- `pv17_product_closed_loop_bff_dto_contract.md`、`pv17_product_closed_loop_implementation_task_matrix.md`、`pv17_product_closed_loop_acceptance_runner_spec.md` 和 `pv17_product_closed_loop_implementation_readiness_audit.md` 已读并纳入实现计划。

## 3. Evidence Package Proposal

后续实现证据建议落在：

```text
docs/design/V12-V15.x/evidence/pv17-product-closed-loop/
```

最低文件：

- `acceptance-data.json`
- `artifact-manifest.json`
- `product-console-report.json`
- `entity-mutation-report.json`
- `studio-workflow-version-report.json`
- `runtime-run-inspect-report.json`
- `evidence-review-report.json`
- `browser-network-log.json`
- `bff-route-log.json`
- `dto-snapshots.json`
- `claim-to-evidence-matrix.json`
- `product-console-screenshot.png`
- `studio-run-inspect-screenshot.png`
- `evidence-review-screenshot.png`
- `prd-spec-review.md`
- `target-architecture-review.md`
- `audit-closure.md`
- `no-false-green-scan.txt`
- `redaction-scan.txt`

Future runner/report names:

- `tools/pv17/run_product_closed_loop_e2e.py`
- `tools/pv17/run_product_closed_loop_acceptance.py`
- `docs/design/V12-V15.x/reports/pv17_product_closed_loop_acceptance_report.json`

## 4. 验收阻断条件

- Browser 直连 internal runtime/store。
- BFF DTO 不能证明来自正式 `apps/api/routers/bff.py` 或受控 public route。
- runtime-backed inspect 只有 fixture，没有 runtime event refs、trace refs、artifact refs、quality refs。
- Durable mutation 缺少 `user_confirmed=true`、ownership check 或 audit refs。
- UI 无法让用户理解当前 workspace/project/app/workflow/station/run/evidence 上下文。
- 任何文档或 UI 把 PV17 说成 production ready、Xpert parity complete、product-grade frontend complete、complete Workflow Studio ready 或 Agent executor ready。

## 5. 允许的实现后声明

PV17 实现完成前不允许新的完成声明。后续如果 PV17-SA 证据通过，建议只允许：

```text
PV17 complete: product closed loop implementation ready for bounded review.
```

该声明仍不等于生产可用、完整 Workflow Studio、Agent executor ready 或 Xpert parity。
