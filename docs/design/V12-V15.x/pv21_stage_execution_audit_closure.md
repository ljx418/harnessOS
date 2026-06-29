# PV21 阶段执行与审计闭环

用途：记录 PV21 Complete Workflow Studio 候选阶段的实际开发、验收和审计结论。
阅读对象：后续自动化开发 Agent、ChatGPT 审计、人工评审者。
边界：本文是阶段闭环记录，不是生产可用声明；不得据此宣称 production ready、完整 Agent executor、外部应用接入完成。

## 实际完成范围

- 新增 `?studio=pv21-complete-workflow-studio` 作为默认工作台入口。
- 新增 `/bff/pv21/*` DTO 边界，浏览器只通过 BFF 访问后端能力。
- 支持 Workflow graph 读取、保存 Draft、校验、Diff、发布版本、版本历史、回滚。
- 支持基于已发布 `WorkflowVersion` 启动真实 runtime run。
- 支持人工门禁审批并推动 `WorkflowInstance` 从 `waiting_approval` 到 `completed`。
- 支持证据摘要，覆盖 trace、artifact、quality、approval、route boundary、No False Green 扫描。
- 保留平台通用性红线：业务样例只能通过 `WorkflowTemplate`/draft/version/input 进入平台，不允许定制 workflow core、Gateway core 或 App shell。

## 子阶段闭环

| 子阶段 | 目标 | 结论 | 证据 |
| --- | --- | --- | --- |
| S1 Entry State | 默认入口、state DTO、平台红线可见 | PASS | `01-pv21-studio-loaded.png` |
| S2 Canvas Validation | 保存 Draft、校验图、生成 Diff | PASS | `02-canvas-save-validate-diff.png` |
| S3 Version Rollback | 两次发布、版本历史、回滚候选 | PASS | `03-version-publish-history.png`、`07-pv21-full-page-completed.png` |
| S4 Runtime Human Gate | 发布版本运行、人工审批完成 | PASS | `04-run-waiting-approval.png`、`05-human-gate-approved.png` |
| S5 Evidence UX Guard | 证据审查、路由边界、红线扫描 | PASS | `06-evidence-review.png`、`acceptance-data.json` |

## 自动化验收命令

```bash
.venv/bin/python -m py_compile apps/api/routers/bff.py core/workflows/store.py
.venv/bin/pytest tests/test_pv21_complete_workflow_studio_bff.py tests/test_pv19_runtime_workflow_platform_bff.py tests/test_pv20_agent_execution_contract_bff.py -q
cd apps/workflow-console && node node_modules/typescript/bin/tsc -p tsconfig.json && node node_modules/vite/bin/vite.js build
cd apps/workflow-console && PV21_CDP_URL=http://127.0.0.1:9351 PV21_BASE_URL=http://127.0.0.1:4185 PV21_BFF_BASE=http://127.0.0.1:18141 node e2e/pv21_cdp_acceptance.mjs
```

## 自动化验收结果

- Python/BFF 回归：`4 passed`，覆盖 PV19、PV20、PV21。
- 前端构建：TypeScript 与 Vite build 通过；存在既有 chunk size 警告。
- 浏览器验收：CDP headless Chrome PASS，报告见 `docs/design/V12-V15.x/evidence/pv21-complete-workflow-studio/pv21-acceptance-report.html`。
- 禁止路由扫描：浏览器请求未命中 `/v1/rpc`、`/v1/internal`、`/internal/runtime`、`/runtime/store`、`/api/runtime`、`/debug/runtime`。

## 允许声明

`PV21 complete Workflow Studio candidate ready for bounded review.`

## 不允许声明

- 不声明 production ready。
- 不声明 Xpert parity complete。
- 不声明 product-grade frontend complete。
- 不声明 complete Workflow Studio ready。
- 不声明 Agent executor ready。
- 不声明外部应用接入契约或生产治理硬化完成。

## 残余风险

- 当前是候选工作台闭环，不是生产治理硬化；权限、租户、审计持久化仍需后续阶段扩展。
- 当前 graph 编辑是受控的最小可验收编辑，不等同于完整拖拽式 Workflow Studio。
- 当前 Agent 节点仍依赖 PV20 受治理执行契约，不等同于 unrestricted Agent executor。
