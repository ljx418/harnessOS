# PV21 Complete Workflow Studio Development And Acceptance Plan

用途：把 PV21 完整 Workflow Studio 候选能力拆成开发、验收和审计步骤。
阅读对象：开发、测试、产品、审计人员。
边界：本文是开工计划；在代码和证据生成前不产生任何 PASS 声明。

## 1. Stage Outline

| Stage | 用户可见效果 | 开发对象 | 验收证据 |
| --- | --- | --- | --- |
| PV21-R0 | Reviewer 看到 PV21 目标、架构、任务、门槛和风险闭环。 | PRD、target architecture、plan、gate、gap、drawio、readiness audit。 | 文档存在性、No False Green、风险闭环。 |
| PV21-S1 | 默认 Studio 入口可打开真实工作台骨架和 current state。 | route、PV21 Studio shell、BFF state DTO、node library DTO。 | Browser screenshot、DTO snapshot、route boundary log。 |
| PV21-S2 | 用户可编辑通用 graph，并看到 Inspector / validation。 | canvas、node/edge operations、Inspector、graph validation。 | Graph roundtrip report、validation negative fixtures。 |
| PV21-S3 | 用户可审查 diff、发布版本、查看版本列表并回滚。 | WorkflowDiff、WorkflowVersion publish/rollback、audit refs。 | Version report、rollback report、audit refs。 |
| PV21-S4 | 用户可从 Studio 运行版本并处理 human gate。 | run route、inspect DTO、human action route、run history。 | Runtime report、human transition report。 |
| PV21-S5 | 用户可审查 evidence summary 和 No False Green。 | evidence aggregator、claim matrix、redaction scan、browser panel。 | Evidence report、claim scan、redaction scan、screenshots。 |
| PV21-SA | Reviewer 完成 PRD/架构/UX/证据聚合审查。 | aggregate runner、artifact manifest、audit closure。 | acceptance-data、artifact-manifest、stage audit closure。 |

## 2. Entry Conditions

PV21 实质开发不能开始，直到：

- PV21 PRD、目标架构、开发计划、里程碑、验收门槛、gap、任务矩阵、readiness audit 和 drawio 存在。
- 文档明确 PV21 是完整 Workflow Studio 候选能力，不是生产可用或 Xpert parity。
- 文档明确工作流平台必须保持通用性，业务 Pack 不能污染 workflow core、Gateway core 或 App shell。
- 文档锁定至少一条端到端真实用户路径：编辑 graph -> validation -> diff -> publish -> run -> human action -> evidence -> rollback。
- No False Green 和红线扫描通过。

## 3. Required Acceptance Data

后续实现证据建议落在：

```text
docs/design/V12-V15.x/evidence/pv21-complete-workflow-studio/
```

最低文件：

- `acceptance-data.json`
- `artifact-manifest.json`
- `studio-state-dto-snapshot.json`
- `workflow-graph-roundtrip-report.json`
- `graph-validation-report.json`
- `workflow-diff-report.json`
- `workflow-version-publish-rollback-report.json`
- `runtime-run-inspect-report.json`
- `human-action-transition-report.json`
- `evidence-summary-report.json`
- `browser-network-log.json`
- `route-boundary-log.json`
- `pv21-studio-home.png`
- `pv21-canvas-edit.png`
- `pv21-version-run-evidence.png`
- `prd-spec-review.md`
- `target-architecture-review.md`
- `ux-review.md`
- `platform-generality-review.md`
- `no-false-green-scan.txt`
- `redaction-scan.txt`

## 4. Negative Fixtures

- `browser_direct_rpc_denied`
- `invalid_edge_publish_blocked`
- `missing_required_node_param_publish_blocked`
- `unknown_node_type_denied`
- `business_specific_core_branch_denied`
- `agent_direct_publish_denied`
- `rollback_without_confirmation_denied`
- `human_action_without_waiting_gate_denied`
- `run_unpublished_draft_denied`
- `raw_prompt_leak_denied`
- `raw_secret_leak_denied`
- `history_delete_denied`

## 5. Acceptance Blockers

- 根路径或默认 Studio 入口仍是空白页，或只能显示静态摘要。
- 画布编辑只是前端状态，没有后端 draft graph readback。
- WorkflowDiff、publish、rollback 任一能力缺少后端版本和 audit 证据。
- Run 不是从已发布 WorkflowVersion 启动，或缺少 WorkflowInstance / StationRun readback。
- Human gate 没有真实后端状态转换。
- Evidence summary 缺少 artifact、trace、quality、approval、claim 或 redaction refs。
- 浏览器直连 runtime/internal API。
- 为某个业务 Pack 增加 workflow core、Gateway core 或 App shell 特例。
- 文档或 UI 做生产可用、Xpert parity、产品级前端完成或完整工作台已完成声明。

## 6. Substage Review Rule

每个 PV21 子阶段完成后必须执行：

1. PRD requirement checklist。
2. Target architecture entity checklist。
3. Backend acceptance runner。
4. Browser E2E with screenshots where UI changes exist。
5. No False Green scan。
6. Redaction scan。
7. Stage audit note。

如果出现 fatal 或 major 规格偏差，必须回到计划阶段修订，不得用文档解释替代缺失实现。

