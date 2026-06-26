# PV17 Stage Execution Plan

用途：记录 PV17 本轮自动化开发、验收标准和阶段出门条件。
阅读对象：开发、测试、产品、审计人员和外部 Agent。
边界：本文是阶段执行记录和验收计划，不替代 evidence package、BFF route log、DTO snapshots、browser E2E 或 runtime evidence。

## 1. Stage Goal

PV17 本轮目标限定为 Product Closed Loop：

```text
setup -> Product Console -> Mission Studio -> confirm run -> inspect -> evidence
```

本轮不进入 Path B 外部 app contract、Path C business pack productization 或 Path D production governance hardening。

## 2. Development Scope

| Stage | 开发目标 | 验收标准 |
| --- | --- | --- |
| PV17-S1 | Product Console 展示 workspace / project / app / workflow / Station Agent / system health。 | browser screenshot、`/bff/pv17/system/health`、`/bff/pv17/product-console/state` DTO snapshot。 |
| PV17-S2 | 用户确认后通过正式 BFF mutation 配置 Station Agent，并保留 denial fixture。 | mutation report 含 `user_confirmed=true`、policy decision、audit ref、negative fixture。 |
| PV17-S3 | Mission Studio 支持提出 WorkflowPatch 并由用户确认 publish WorkflowVersion。 | versioning report 含 WorkflowDiff、expected revision、confirmation transcript、workflow version id。 |
| PV17-S4 | 用户确认运行后 inspect WorkflowInstance。 | runtime report 含 runtime event refs、trace refs、artifact refs、quality refs、approval refs。 |
| PV17-S5 | Evidence Review 展示 claim-to-evidence、route boundary、redaction 和 lineage。 | evidence report、claim matrix、browser network log、BFF route log 均 PASS。 |
| PV17-SA | 聚合验收并输出 bounded review 结论。 | `tools/pv17/run_product_closed_loop_acceptance.py` 返回 PASS。 |

## 3. Real Data Rule

本轮验收数据来自：

- 正式 FastAPI app：`apps.api:create_app`。
- 正式 BFF route：`apps/api/routers/bff.py` 下 `/bff/pv17/*`。
- 真实 GatewayService、本地 workflow repository、trace/artifact/approval/quality stores。
- 浏览器实际打开 `apps/workflow-console` 并点击 PV17 页面控件。

以下材料不能作为本轮实现通过证据：

- PV16 test-only BFF route；
- docs / drawio / presentation HTML；
- 静态 JSON 自造 PASS；
- 只截图但无 DTO、route log 和 runtime refs 的材料。

## 4. Commands

```text
.venv/bin/python tools/pv17/run_product_closed_loop_e2e.py
.venv/bin/python tools/pv17/run_product_closed_loop_acceptance.py
```

回归命令：

```text
.venv/bin/python -m pytest tests/test_api_runs.py tests/test_cli_headless.py tests/test_pack_registry.py tests/test_meeting_pack_assembly.py tests/test_knowledge_pack_assembly.py tests/test_pv17_product_closed_loop_bff.py tests/test_pv17_acceptance_runner.py
cd apps/workflow-console && node node_modules/typescript/bin/tsc -p tsconfig.test.json && node --test dist-test/__tests__/*.test.js && node node_modules/typescript/bin/tsc -p tsconfig.json && node node_modules/vite/bin/vite.js build
```

## 5. Exit Condition

允许出门声明仅限：

```text
PV17 complete: product closed loop implementation ready for bounded review.
```

该结论不等于 production ready，不等于完整 Workflow Studio，不等于 Agent executor ready，不等于 Xpert parity complete。
