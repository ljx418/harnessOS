# PV19 Runtime Workflow Platform Development And Acceptance Plan

用途：把 PV19 完整工作流平台受控闭环拆成可执行开发与验收阶段。
阅读对象：开发、测试、产品、审计人员。
边界：本文是开发及验收计划；在实际代码和证据生成前，不产生任何 PASS 声明。

## 1. Stage Outline

| Stage | 用户可见效果 | 开发对象 | 验收证据 |
| --- | --- | --- | --- |
| PV19-R0 | Reviewer 看到 PV19 目标、代码实体、No-Go、drawio 和出门条件。 | 文档、drawio、索引、readiness audit。 | 文档存在性、drawio 页数、No False Green 扫描。 |
| PV19-S1 | 用户打开真实工作台入口，看到 canvas、节点库、Inspector、版本和运行区。 | `App.tsx`, workbench route, `WorkflowConsoleClient`, BFF state DTO。 | screenshot、DTO snapshot、route log。 |
| PV19-S2 | 用户编辑工作流并生成 WorkflowDiff。 | graph DTO、validation、diff、WorkflowSpecGraph readback。 | graph roundtrip、action log、negative fixture。 |
| PV19-S3 | 用户确认发布 WorkflowVersion。 | publish DTO、WorkflowStore、version readback。 | version report、audit ref、rollback/readback check。 |
| PV19-S4 | 用户运行发布版本并查看 runtime 进度。 | run start、inspect DTO、GatewayService/runtime methods。 | runtime report、event refs、artifact refs。 |
| PV19-S5 | 用户处理人工节点，流程继续或安全终止。 | human action DTO、approval/handoff/audit store。 | state transition report、audit trail。 |
| PV19-S6 | 用户审查结果、trace、quality、audit 和 claim evidence。 | evidence panel、artifact/trace/quality/audit read model。 | evidence summary、claim matrix、redaction scan。 |
| PV19-SA | Reviewer 接受 bounded runtime workflow platform closed loop 结论。 | aggregate runner、artifact manifest、audit closure。 | acceptance-data、artifact-manifest、audit closure。 |

## 2. Entry Conditions

PV19 实现不能开始，直到：

- PV19 PRD、目标架构、开发计划、里程碑、验收门槛、gap 分析、BFF DTO contract、runner spec、readiness audit 和 drawio 均存在。
- `pv19_runtime_workflow_platform_implementation_task_matrix.md` 和 `pv19_runtime_workflow_platform_document_support_audit.md` 已存在，并关闭入口、route、human gate、业务样例和任务粒度风险。
- 文档明确 PV19 是受控闭环完整，不是 production ready。
- 文档明确 V13/PV17/PV18 是已有 bounded evidence，不得改写成完整平台完成事实。
- 文档锁定一个业务样例作为验收 fixture，但平台核心不得业务定制。
- No False Green 扫描通过。

## 3. Evidence Package Proposal

后续实现证据建议落在：

```text
docs/design/V12-V15.x/evidence/pv19-runtime-workflow-platform/
```

最低文件：

- `acceptance-data.json`
- `artifact-manifest.json`
- `workbench-state-report.json`
- `workflow-graph-roundtrip-report.json`
- `workflow-version-publish-report.json`
- `runtime-run-inspect-report.json`
- `human-interaction-report.json`
- `evidence-review-report.json`
- `browser-network-log.json`
- `bff-route-log.json`
- `dto-snapshots.json`
- `artifact-lineage-report.json`
- `claim-to-evidence-matrix.json`
- `runtime-workbench-screenshot.png`
- `human-gate-screenshot.png`
- `evidence-review-screenshot.png`
- `prd-spec-review.md`
- `target-architecture-review.md`
- `platform-generality-review.md`
- `audit-closure.md`
- `no-false-green-scan.txt`
- `redaction-scan.txt`

## 4. Required Negative Fixtures

- `default_home_empty_blocks_acceptance`
- `publish_without_user_confirmation_denied`
- `run_unpublished_graph_denied`
- `human_gate_ui_only_denied`
- `browser_direct_rpc_denied`
- `runtime_truth_constructed_by_frontend_denied`
- `artifact_lineage_missing_blocks_pass`
- `raw_secret_redaction_required`
- `business_specific_core_customization_denied`

## 5. Acceptance Blockers

- 工作台入口仍然落到空白根路径，且无清晰用户路径。
- 画布编辑无法 readback 为 WorkflowSpecGraph。
- publish/run 只在 UI 模拟，没有后端版本或 runtime 证据。
- 人工交互不能改变后端 runtime 状态。
- Evidence panel 缺 artifact、trace、audit 或 claim refs。
- 浏览器直接调用 runtime/internal/store/connector route。
- 为业务样例向 workflow core、Gateway core 或 App shell 加业务专用逻辑。
- 文档或 UI 出现生产可用、完整 Studio、完整 Agent executor、Xpert parity 等正向完成声明。
