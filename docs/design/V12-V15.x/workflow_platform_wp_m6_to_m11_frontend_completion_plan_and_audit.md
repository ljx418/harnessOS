# WP-M6 To WP-M11 Frontend Completion Plan And Audit

用途：把“百分百实现前端页面功能”的用户目标限定并落成可执行开发、验收和审计计划。
边界：本文只支撑 PRD 定义的 PV13-based Workflow Platform 前端功能闭环。它不证明生产可用、完整 Workflow Studio GA、无限制 Agent executor、外部生态完成或最终商业业务应用完成。

## 1. Scope Statement

本阶段目标是：

```text
PRD-defined frontend functionality complete for bounded review
```

该目标包含：

- PV13 Light Studio 仍是默认首页和工作流平台前端基线。
- 正常路径不再依赖 `scenarioData`、`fallbackGraph`、静态 timeline、静态 Inspector 或 proposal-only chat 作为业务事实来源。
- 用户能在 PV13 工作台中编辑 WorkflowSpecGraph、保存、刷新回读和审查 WorkflowDiff。
- 用户能在 PV13 工作台中发布、运行、人工审查和回看证据。
- 文档总结、代码审查、会议整理三个业务场景生成可审查产物和证据链。
- 失败态、权限态、离线态、校验失败、人工拒绝、取消/重试、键盘、响应式、可访问性和性能体验通过验收。
- 每个正向功能声明都有 evidence path。

该目标不包含：

- production ready。
- product-grade frontend complete。
- complete Workflow Studio ready / Workflow Studio GA。
- Agent executor ready 或 unrestricted automation。
- Xpert parity complete。
- 外部应用生态、商业化、计费、SLA 或生产部署完成。

## 2. Stage Plan

| Stage | User-visible outcome | Development target | Required evidence | Stop condition |
| --- | --- | --- | --- | --- |
| WP-M6 Data-driven closure | 用户看到的场景、节点、Inspector、timeline、quality、evidence 和 chat 初始上下文来自平台数据，而不是前端写死内容。 | 重构 `V13EditableStudio.tsx` 正常路径数据读取，补齐 `workflowConsoleClient.ts` typed methods 或 BFF DTO composition。 | `frontend-data-source-closure-report.json`、network log、DTO snapshot、fallback screenshots。 | 正常路径仍读取 `scenarioData` / `fallbackGraph` / 静态业务事实。 |
| WP-M7 Graph edit/save/readback | 用户能拖节点、连线、取消/删除连线、改配置、保存草稿、刷新后仍看到保存结果，并审查 Diff。 | 将画布交互绑定到 WorkflowSpecGraph DTO save/readback；Diff 基于后端保存状态。 | `graph-edit-save-readback-report.json`、before/after DTO、browser action log、Diff review log。 | 只有本地状态变化，没有 BFF 保存和刷新回读。 |
| WP-M8 Publish/run/human/evidence | 用户在同一工作台发布、运行、审批/拒绝并回看证据。 | 把 PV19/PV21 publish/run/human/evidence 能力做成 PV13 内连续路径。 | `workflow-inline-runtime-report.json`、runtime inspect、human action report、evidence panel report。 | 只能跳到分散 PV 页面完成，或 UI 构造运行结果。 |
| WP-M9 Business artifacts | 用户用三种业务场景拿到可审查产物，而不是只看到通过状态。 | 生成文档总结、代码审查、会议整理产物文件或机器可读产物内容，绑定 refs。 | `business-artifact-manifest.json`、content snapshots、input hash、quality/human/redaction refs。 | 只有摘要卡片、验收报告摘录或截图。 |
| WP-M10 Frontend quality | 用户能理解加载、错误、拒绝、离线、校验失败、人工拒绝和重试等状态，核心路径可键盘/响应式访问。 | 补齐 failure-state UI、a11y、responsive、performance、keyboard evidence。 | `frontend-quality-failure-state-report.json`、screenshots、a11y report、performance budget。 | happy path 通过但关键失败态不可见或不可操作。 |
| WP-M11 Aggregate audit | 人类能从一份中文 HTML 报告审计 PRD、架构、代码、功能和证据是否一致。 | 汇总 WP-M6 到 WP-M10，生成 claim-to-evidence matrix 和最终审计报告。 | `frontend-completion-aggregate-audit.html`、claim matrix、No False Green scan、artifact manifest。 | 任一 PRD 功能缺证却给出 PASS。 |

## 3. PRD Coverage Matrix

| PRD area | Covered by | Evidence requirement |
| --- | --- | --- |
| Default PV13 homepage and canvas | WP-M1 / WP-M2 retained, WP-M10 regression | Screenshots、browser action log、route assertions。 |
| Data-driven scenario projection | WP-M6 | Normal path data-source closure report。 |
| Node drag/connect/cancel and Inspector | WP-M7 / WP-M10 | Graph action log、Inspector DTO snapshot、failure-state screenshots。 |
| WorkflowDiff human review | WP-M7 | Diff DTO、human confirmation/rejection log。 |
| Publish / run / StationRun | WP-M8 | WorkflowVersion、WorkflowInstance、StationRun readback。 |
| Human Gate | WP-M8 / WP-M10 | approve/reject before/after state and screenshots。 |
| Evidence Review | WP-M8 / WP-M9 | artifact / trace / quality / audit / claim / redaction refs。 |
| Document summary scenario | WP-M9 | Input hash、summary artifact、quality refs、human review refs。 |
| Code review scenario | WP-M9 | Diff/code input hash、review artifact、risk refs、approval refs。 |
| Meeting brief scenario | WP-M9 | Transcript input hash、brief artifact、action items、review refs。 |
| Failure states, accessibility and performance | WP-M10 | Failure matrix、a11y、responsive、performance report。 |
| Completion claim safety | WP-M11 | Claim-to-evidence matrix and No False Green scan。 |

## 4. Architecture Coverage Matrix

| Architecture entity | Current role | WP-M6 to WP-M11 target |
| --- | --- | --- |
| `apps/workflow-console/src/App.tsx` | Browser bootstrap。 | 保持默认进入 PV13 工作流平台。 |
| `apps/workflow-console/src/ui/layout/WorkflowStudioLayout.tsx` | Route dispatcher。 | 保持无 query 和 `workflow-platform` 映射到 PV13；旧页面只作为历史/对照。 |
| `apps/workflow-console/src/ui/v13/V13EditableStudio.tsx` | PV13 首页、画布和当前能力融合页面。 | 去除正常路径 mock 依赖，承载图编辑、运行、人工、证据、三业务产物和失败态。 |
| `apps/workflow-console/src/ui/v13/v13-editable-studio.css` | PV13 视觉和交互样式。 | 保持力感画布体验，补齐状态、响应式、可访问性和文本不溢出。 |
| `apps/workflow-console/src/api/workflowConsoleClient.ts` | Frontend typed BFF client。 | 补齐 WP-M6 到 WP-M9 所需 typed methods，保持 browser 只走 BFF。 |
| `apps/api/routers/bff.py` | Main BFF route owner。 | 组合 `/bff/v13/*`、`/bff/pv19/*`、`/bff/pv20/*`、`/bff/pv21/*`、`/bff/workflow-platform/*`，必要时新增 facade。 |
| `core/workflows/store.py` | WorkflowSpec / version / instance / station persistence。 | 作为 BFF 后端持久化来源，browser 不直接调用。 |
| `apps/gateway/service.py` | Runtime gateway boundary。 | 通过 BFF 间接参与 run/evidence，不被 browser 绕过。 |
| `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/` | Existing evidence package。 | 新增 WP-M6 到 WP-M11 evidence，保留 WP-M1A 到 WP-M5A 历史证据索引。 |

## 5. Evidence Package Contract

WP-M6 到 WP-M11 的 evidence package 必须至少包含：

| File | Required by | Purpose |
| --- | --- | --- |
| `artifact-manifest.json` | all | 列出本阶段所有证据文件、hash、生成命令和审计结论。 |
| `browser-action-log.json` | all browser stages | 记录真实用户动作。 |
| `browser-network-log.json` | all browser stages | 证明只使用允许 BFF routes。 |
| `dto-snapshot.json` | all BFF/DTO stages | 保存关键 DTO before/after。 |
| `frontend-data-source-closure-report.json` | WP-M6 | 正常路径静态来源清零。 |
| `graph-edit-save-readback-report.json` | WP-M7 | 图编辑、保存、刷新回读、Diff。 |
| `workflow-inline-runtime-report.json` | WP-M8 | publish/run/human/evidence 连续路径。 |
| `business-artifact-manifest.json` | WP-M9 | 三业务产物、input hash、refs。 |
| `frontend-quality-failure-state-report.json` | WP-M10 | 失败态、a11y、响应式、性能。 |
| `claim-to-evidence-matrix.json` | WP-M11 | PRD 功能声明到证据映射。 |
| `frontend-completion-aggregate-audit.html` | WP-M11 | 中文聚合审计报告。 |
| `no-false-green-scan.txt` | all | 禁止虚假完成声明。 |

The machine-checkable minimum schemas for the WP-M6 through WP-M11 stage reports are:

- `schemas/frontend-data-source-closure-report.schema.json`
- `schemas/graph-edit-save-readback-report.schema.json`
- `schemas/workflow-inline-runtime-report.schema.json`
- `schemas/business-artifact-manifest.schema.json`
- `schemas/frontend-quality-failure-state-report.schema.json`
- `schemas/claim-to-evidence-matrix.schema.json`

## 6. Audit Opinion

```text
document_support=PASS_FOR_IMPLEMENTATION_AND_ACCEPTANCE
implementation_status=PASSED_BOUNDED_ACCEPTANCE
fatal_spec_drift=NONE_FOUND_IN_DOCUMENT_SCOPE
major_open_risks=post_acceptance_regression_risk_only
human_confirmation_required=NO_FOR_CURRENT_BOUNDED_EVIDENCE
chatgpt_external_audit_required=NO_AFTER_INTERNAL_AUDIT
allowed_next_step=POST_WP_M11_REVIEW_OR_NEXT_USER_SELECTED_STAGE
```

## 7. Post-Implementation Evidence

WP-M6 到 WP-M11 的有界实现证据已经落盘：

- `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/frontend-data-source-closure-report.json`
- `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/graph-edit-save-readback-report.json`
- `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/workflow-inline-runtime-report.json`
- `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/business-artifact-manifest.json`
- `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/frontend-quality-failure-state-report.json`
- `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/claim-to-evidence-matrix.json`
- `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/frontend-completion-aggregate-audit.html`
- `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/artifact-manifest.json`

该证据只支持 bounded review；后续若要进入生产治理、外部生态或商业业务应用完整产品化，必须另起阶段计划和验收门槛。
