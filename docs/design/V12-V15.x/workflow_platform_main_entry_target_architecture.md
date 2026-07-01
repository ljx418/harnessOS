# Workflow Platform Main Entry Target Architecture

用途：定义“PV13 前端页面作为工作流平台首页和前端基线”的目标架构、当前代码实体、待替换边界和交互关系。
边界：本文是架构设计文档，不是实现证据；不得据此声明运行时或产品完成。

## 1. Architecture Intent

后续 HarnessOS 前端产品的默认体验必须锚定 PV13 Light Studio 工作流平台，而不是继续在退化版首入口或分散 PV 阶段页之间切换。

目标入口路径：

```text
Browser
  -> apps/workflow-console/src/App.tsx
  -> WorkflowStudioLayout(state="workflow-platform" or no query fallback)
  -> V13EditableStudio
  -> v13-editable-studio.css
```

后续运行闭环、执行器、业务场景产品化和外部接入能力必须集成到该 PV13 基线体验中：

```text
V13EditableStudio baseline
  -> integrate PV19 runtime loop
  -> integrate PV20 governed executor evidence
  -> reuse PV21 graph/version/run/evidence bounded routes where useful
  -> use implemented WP-M5A scenario projection and business output evidence
  -> provide future PV22 external app host surface
```

当前新阶段的目标不是继续增加新的孤立页面，而是在上述入口路径内完成 WP-M6 到 WP-M11 的 PRD-defined frontend functionality closure：

```text
V13EditableStudio
  -> data-driven normal path through workflowConsoleClient
  -> persisted WorkflowSpecGraph edit/save/readback
  -> WorkflowDiff human review
  -> WorkflowVersion publish and WorkflowInstance run
  -> Human Gate and Evidence Review
  -> three scenario artifacts
  -> aggregate claim-to-evidence audit
```

## 2. Current Concrete Entities

| Layer | Current entity | Target status | Architecture role |
| --- | --- | --- | --- |
| Browser entry | `apps/workflow-console/src/App.tsx` | 需修改/锚定 | 无 query 默认进入 PV13 基线工作流平台。 |
| Route dispatcher | `apps/workflow-console/src/ui/layout/WorkflowStudioLayout.tsx` | 需修改/锚定 | `workflow-platform` 映射到 `V13EditableStudio`，保留历史 query pages。 |
| PV13 baseline page | `apps/workflow-console/src/ui/v13/V13EditableStudio.tsx` | 目标基线 | 首页、力感画布、场景、Inspector、WorkflowDiff pilot。 |
| PV13 baseline style | `apps/workflow-console/src/ui/v13/v13-editable-studio.css` | 目标基线 | 首页视觉、动效、画布、节点、侧栏和底部区域样式。 |
| Static scenario data | `V13EditableStudio.tsx` 内 `scenarioData` / `fallbackGraph` / local timeline and chat replies | 受限保留 | 当前仅作为演示体验和离线降级 fallback；WP-M5A accepted source 是 DTO/evidence-driven projection。 |
| Current degraded entry | `apps/workflow-console/src/ui/workflow-platform/WorkflowPlatformMainEntry.tsx` | 首页需替换 / 能力需迁移 | 不再作为目标首页继续迭代；其中已接入 PV21/PV20 的保存、校验、发布、运行、人工门禁和执行器能力是迁移对照。 |
| Current degraded style | `apps/workflow-console/src/ui/workflow-platform/workflow-platform-main-entry.css` | 需替换/降级历史参考 | 不再作为目标首页样式基线。 |
| Frontend BFF client | `apps/workflow-console/src/api/workflowConsoleClient.ts` | 已实现 / 已复用 | 已包含 PV20/PV21 typed methods；PV13 页面已通过该 client 集成 PV21/PV20 parity loop。 |
| Runtime platform | `PV19RuntimeWorkflowPlatform` | 已实现 bounded slice / 待集成 | 提供 publish/run/human/evidence closed loop baseline。 |
| Agent executor view | `PV20AgentExecutor` | 已实现 bounded slice / 待集成 | 提供 governed skill/tool/MCP execution evidence path。 |
| Complete Studio candidate | `PV21CompleteWorkflowStudio` | 已实现 bounded candidate / 待复用 | 提供 graph save/validate/diff/version/run/evidence 参考能力。 |
| BFF router | `apps/api/routers/bff.py` | 已实现且需复用 | 提供 `/bff/v13/*`、`/bff/pv19/*`、`/bff/pv20/*`、`/bff/pv21/*` DTO boundary；V13 routes 是 handoff-only compatibility，不是 runtime execution evidence。 |
| Scenario projection route | `/bff/workflow-platform/scenarios` and `/bff/workflow-platform/scenarios/{scenario_id}/outputs` | 已实现 | WP-M5A additive route，用于返回场景目录、输入要求、业务输出摘要和 evidence refs；不得破坏 V13/PV20/PV21 replay routes。 |
| V13 acceptance smoke BFF | `apps/workflow-console/e2e/bff_smoke_server.py` | 已实现 bounded harness source | 历史 V13 验收中也提供 `/bff/v13/*` route；当前主 BFF 已恢复正式 compatibility routes，smoke server 仅保留为 E2E harness fixture。 |
| Workflow store | `core/workflows/store.py` | 已实现且需复用 | 持久化 WorkflowSpec / WorkflowVersion / WorkflowInstance / StationRun。 |
| Runtime gateway | `apps/gateway/service.py` | 已实现且需复用 | 保持 Gateway/RPC/control-plane boundary。 |
| Evidence | `docs/design/V12-V15.x/evidence/*` | 已有多阶段证据 | 阶段验收和 claim-to-evidence 来源。 |

WP-M6 之后，`scenarioData`、`fallbackGraph`、静态 timeline、静态 Inspector 和 proposal-only chat 回复不得再作为正常路径业务事实来源。它们只能保留为显式离线 fallback、测试 fixture 或历史设计参考，且必须被 UI 状态、验收报告和 mock reduction report 标出。

## 3. Target Layering

```text
User
  -> PV13 Light Studio Workflow Platform Homepage
  -> V13 canvas / scene / inspector / workspace UI
  -> V13 WorkflowDiff pilot controls
  -> PV19/PV21 publish-run-human-evidence integration
  -> PV20 governed Agent/Tool/Skill/MCP integration
  -> WP-M5A scenario projection / business output review
  -> BFF route families
  -> WorkflowStore / GatewayService / Artifact and Evidence stores
```

## 3.1 Current-To-Target Architecture Delta

本节是 `workflow_platform_main_entry_gap_analysis.drawio` 第 2 页的 Markdown source of truth。后续开发和审计不得只依赖 drawio 图形理解架构差异。

| Area | Current architecture status | Target after WP-M6 to WP-M11 | Required proof |
| --- | --- | --- | --- |
| 入口与首页基线 | 已开发：`App.tsx`、`WorkflowStudioLayout.tsx`、`V13EditableStudio.tsx` 已使默认入口指向 PV13 基线。 | 保持 PV13 Light Studio 为唯一目标首页，不回退到 `WorkflowPlatformMainEntry`。 | Route assertions、PV13 screenshot、No regression scan。 |
| 前端静态数据 | 需收敛：`scenarioData`、`fallbackGraph`、静态 timeline、静态 Inspector、proposal-only chat 仍可能参与体验。 | WP-M6 后，正常路径业务事实全部来自 BFF/DTO 或 artifact refs；本地数据只作显式 fallback。 | `normal_path_static_sources == 0`、DTO snapshot、fallback UI screenshot。 |
| 能力来源 | 已开发但分散：PV19 runtime、PV20 governed executor、PV21 graph/version/run/evidence、WP-M5A scenario summaries 均是能力来源。 | 这些能力必须被组合进 PV13 工作台，不得只作为分散阶段页或摘要面板。 | Browser action log proves same-workbench path。 |
| 图编辑和保存 | 受限完成：PV13 画布交互和 PV21 graph route evidence 分别存在，但尚未证明完整编辑、保存、刷新回读和 Diff 在同一工作台闭环。 | WP-M7 通过 BFF DTO 支持节点、边、配置 mutation，并刷新回读 WorkflowSpecGraph。 | `graph-edit-save-readback-report.json`。 |
| 发布、运行、人工和证据 | 受限完成：有 PV19/PV21/PV20 bounded source/parity evidence。 | WP-M8 在 PV13 工作台内完成 publish、run、StationRun readback、Human Gate、Evidence Review。 | `workflow-inline-runtime-report.json`。 |
| 三业务产物 | 受限完成：WP-M5A 有机器可读输出摘要和 refs。 | WP-M9 生成文档总结、代码审查、会议整理三个可审查 artifact/content snapshot。 | `business-artifact-manifest.json`。 |
| 前端质量状态 | 当前主要覆盖 happy path 和部分边界。 | WP-M10 覆盖加载、空、错误、权限拒绝、BFF 离线、校验失败、人工拒绝、取消/重试、键盘、响应式、a11y、性能。 | `frontend-quality-failure-state-report.json`。 |
| 聚合审计 | 当前证据分散在多个 bounded stage。 | WP-M11 汇总 WP-FR-1 到 WP-FR-20，缺证即 BLOCKED。 | `claim-to-evidence-matrix.json` and aggregate HTML report。 |

### Frontend Function Coverage Decision

如果且仅如果 WP-M6 到 WP-M11 全部 PASS，本阶段开发完成后可以覆盖 PRD 定义的全部 PV13-based Workflow Platform 前端页面功能：

```text
coverage_target=PRD_DEFINED_FRONTEND_PAGE_FUNCTIONS_ONLY
coverage_status_now=NOT_IMPLEMENTED
coverage_status_after_wp_m11=YES_IF_ALL_WP_M6_TO_WP_M11_GATES_PASS
excluded_scope=production_ready, product_grade_frontend_complete, complete_workflow_studio_ga, unrestricted_agent_executor, external_ecosystem_completion
```

该覆盖结论包括：

- 首页 shell、workspace/state、场景导航、画布基础交互、节点/Inspector。
- 图编辑、保存、刷新回读、WorkflowDiff 人工审查。
- 发布、运行、StationRun、Human Gate、Evidence Review。
- 文档总结、代码审查、会议整理三个业务场景产物。
- 加载、空、错误、权限拒绝、离线、校验失败、人工拒绝、取消/重试。
- 键盘、焦点、响应式、a11y、性能。
- WP-FR-1 到 WP-FR-20 的 claim-to-evidence matrix。

该覆盖结论不包括生产治理、商业化、外部生态、完整 GA、无限制 Agent executor 或最终商业业务应用完成。

## 3.2 Concrete Code Entity Layers And Relationships

本节是 `workflow_platform_main_entry_gap_analysis.drawio` 第 3 页的 Markdown source of truth。箭头表示调用、数据或证据流方向。

```text
Layer 1 Browser / Route
  App.tsx [implemented]
    -> WorkflowStudioLayout.tsx [implemented]
    -> V13EditableStudio.tsx [modify]

Layer 2 PV13 UI
  V13EditableStudio.tsx [modify]
    -> WorkflowSpecGraphEditorAdapter [add]
    -> WorkflowRunControlAdapter [add]
    -> BusinessScenarioArtifactPanel [add/refactor]
    -> FailureState surfaces [add/refactor]
    -> FrontendCompletionAudit entry [add]
  v13-editable-studio.css [implemented, regress for state/responsive/a11y]
  scenarioData / fallbackGraph / static timeline / static Inspector / local chat [normal path remove, fallback only]

Layer 3 Frontend adapters and typed client
  WorkflowSpecGraphEditorAdapter [add]
    -> workflowConsoleClient.ts [modify]
  WorkflowRunControlAdapter [add]
    -> workflowConsoleClient.ts [modify]
  workflowConsoleClient.ts [modify]
    -> apps/api/routers/bff.py [modify/reuse]
  FrontendCompletionAuditRunner [add]
    -> evidence package and claim-to-evidence matrix [add]

Layer 4 BFF / DTO
  apps/api/routers/bff.py [modify/reuse]
    -> /bff/v13/*
    -> /bff/pv19/*
    -> /bff/pv20/*
    -> /bff/pv21/*
    -> /bff/workflow-platform/*
  WP-M6-M11 DTOs [add/stabilize]
    -> DataSourceClosureDTO
    -> GraphMutationDTO
    -> ArtifactClosureDTO
    -> QualityStateDTO
    -> ClaimEvidenceMatrix

Layer 5 Runtime / Evidence
  core/workflows/store.py [implemented]
    -> WorkflowSpec / WorkflowVersion / WorkflowInstance / StationRun
  apps/gateway/service.py [implemented]
    -> runtime/control-plane boundary
  docs/design/V12-V15.x/evidence/workflow-platform-main-entry/ [extend]
    -> WP-M6-M11 reports, screenshots, DTO snapshots, artifact manifests
```

### Entity Status Matrix

| Entity | Layer | Current status | Target action | Relationship / dependency |
| --- | --- | --- | --- | --- |
| `apps/workflow-console/src/App.tsx` | Browser / route | 已开发 | 保持默认入口，不做产品级扩张。 | Calls `WorkflowStudioLayout.tsx`。 |
| `apps/workflow-console/src/ui/layout/WorkflowStudioLayout.tsx` | Browser / route | 已开发 | 保持 no-query and `workflow-platform` route to PV13。 | Dispatches to `V13EditableStudio.tsx`。 |
| `apps/workflow-console/src/ui/v13/V13EditableStudio.tsx` | PV13 UI | 需修改 | 去正常路径 mock，承载 WP-M6 到 WP-M10。 | Uses adapters and `workflowConsoleClient.ts`。 |
| `apps/workflow-console/src/ui/v13/v13-editable-studio.css` | PV13 UI style | 已开发 | 做状态、响应式、a11y、文本不溢出回归。 | Styles PV13 shell, canvas, panels and failure states。 |
| `scenarioData` / `fallbackGraph` / static timeline / static Inspector / local chat | PV13 UI data | 需收敛 | 从正常路径移除，只允许显式 fallback。 | Replaced by BFF/DTO/artifact refs in WP-M6。 |
| `WorkflowPlatformMainEntry.tsx` | Historical shell | 历史对照 / 不再作为目标首页 | 保留 PV21/PV20 parity checklist，不继续作为首页视觉基线。 | Provides non-regression source for graph/runtime/executor capabilities。 |
| `WorkflowSpecGraphEditorAdapter` | Frontend adapter | 待新增 | 画布动作转 graph mutation DTO。 | Calls `workflowConsoleClient.ts`; supports WP-M7。 |
| `WorkflowRunControlAdapter` | Frontend adapter | 待新增 | 聚合 publish/run/human/evidence 用户动作。 | Calls `workflowConsoleClient.ts`; supports WP-M8。 |
| `BusinessScenarioArtifactPanel` | Frontend panel | 待新增或重构 | 展示三业务产物、input hash、quality、human review、redaction refs。 | Reads WP-M9 artifact DTOs。 |
| `FrontendCompletionAuditRunner` | Acceptance runner | 待新增 | 生成 WP-M11 claim-to-evidence matrix 和 HTML aggregate audit。 | Reads evidence package and PRD requirement IDs。 |
| `apps/workflow-console/src/api/workflowConsoleClient.ts` | Typed BFF client | 需修改 | 补齐 WP-M6 到 WP-M9 typed methods。 | Only browser-to-BFF call surface。 |
| `apps/api/routers/bff.py` | BFF boundary | 需扩展 / 复用 | 组合既有 route families，必要时新增 additive `/bff/workflow-platform/*` facade。 | Calls store/gateway/evidence sources; browser must not bypass。 |
| WP-M6-M11 DTOs | DTO contract | 待新增 / 固化 | Data source closure、graph mutation、artifact closure、quality state、claim evidence。 | Returned by BFF or generated by acceptance runner。 |
| `core/workflows/store.py` | Runtime persistence | 已开发 | 只经 BFF 间接使用。 | Stores WorkflowSpec, WorkflowVersion, WorkflowInstance, StationRun。 |
| `apps/gateway/service.py` | Runtime/control plane | 已开发 | 只经 BFF 间接使用。 | Runtime and evidence source。 |
| `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/` | Evidence package | 需追加 | 增加 WP-M6 到 WP-M11 evidence manifests and reports。 | Input to WP-M11 aggregate audit。 |

### Forbidden Relationship Matrix

| Forbidden relationship | Reason | Required guard |
| --- | --- | --- |
| Browser -> `core/workflows/store.py` direct call | Bypasses BFF/DTO boundary and audit refs。 | Browser network denylist。 |
| Browser -> `apps/gateway/service.py` direct call | Bypasses runtime/control-plane boundary。 | Browser network denylist。 |
| Browser -> unmanaged MCP/tool invocation | Violates governed executor boundary。 | `/bff/pv20/*` or approved facade only。 |
| UI local state -> runtime truth claim | Creates false green evidence。 | DTO readback and runtime inspect required。 |
| drawio / PRD / screenshot -> implementation evidence | Docs are not runtime/browser/BFF evidence。 | Claim-to-evidence matrix must reference real artifacts/logs。 |

## 4. Target Components

| Component | Type | Status | Responsibility |
| --- | --- | --- | --- |
| `V13EditableStudio` | Browser product shell and canvas | 已实现 / 目标基线 | 默认首页、工作流场景、画布、Inspector、仿真控制和 WorkflowDiff pilot。 |
| `WorkflowStudioLayout` | Route dispatcher | 已实现 | 把无 query 和 `workflow-platform` 映射到 PV13 基线。 |
| `App` | Browser bootstrap | 已实现 | 默认 fallback 不再进入退化入口。 |
| `WorkflowPlatformMainEntry` | Old experimental shell | 需替换 | 不再作为首页基线；可暂时保留为历史/对比文件。 |
| `workflowConsoleClient` | Typed BFF client | 已实现 / 已复用 | PV13 集成 PV21/PV20/WP-M5A 能力时的首选调用层，避免 browser 直接调用 runtime/store internals。 |
| `PV19RuntimeWorkflowPlatform` | Runtime source | 已集成为 bounded evidence source | 提供 publish/run/human/evidence loop 到 PV13 工作台的验收来源。 |
| `PV20AgentExecutor` | Executor source | 已集成为 bounded evidence source | 提供 governed Agent/Tool/Skill/MCP 能力到 PV13 资源面板的验收来源。 |
| `PV21CompleteWorkflowStudio` | Bounded candidate source | 已复用为 bounded evidence source | 提供 graph/version/run/evidence route and DTO reference。 |
| `WorkflowPlatformScenarioProjection` | DTO / additive route | 已实现 | WP-M5A 将场景列表、输入要求、业务产物摘要、证据引用和 mock/fallback 状态交给前端渲染。 |
| `WorkflowPlatformBffFacade` | Optional future BFF consolidation | 待设计 | 只有在 PV13 集成出现 route sprawl 或 WP-M5A 场景投影需要统一入口时才新增；不得先做大而全 facade。 |
| `WorkflowSpecGraphEditorAdapter` | Frontend adapter / target boundary | 待新增 | WP-M7 将画布节点、边、端口、配置变更转换为 BFF DTO，不直接写 runtime/store。 |
| `WorkflowRunControlAdapter` | Frontend adapter / target boundary | 待新增 | WP-M8 将 publish/run/human/evidence 用户动作聚合为 PV13 工作台内的受控操作入口。 |
| `BusinessScenarioArtifactPanel` | Frontend panel / target boundary | 待新增或重构 | WP-M9 展示三个业务场景的真实产物、input hash、quality、human review 和 redaction refs。 |
| `FrontendCompletionAuditRunner` | Acceptance runner / target boundary | 待新增 | WP-M11 汇总 WP-M6 到 WP-M10 证据并生成 claim-to-evidence matrix。 |

## 5. Current-To-Target Classification

| Classification | Items |
| --- | --- |
| 已实现且作为基线 | `V13EditableStudio.tsx`、`v13-editable-studio.css`、`?studio=v13-editable-studio`、V13 evidence package。 |
| 已实现但作为能力来源 | PV19 runtime loop、PV20 governed executor、PV21 bounded candidate、workflow store、BFF route families、evidence packages。 |
| 受限完成 / 需继续收敛 | `V13EditableStudio.tsx` 中业务场景、Inspector、timeline、chat、fallback graph 仍保留本地静态 fallback；WP-M5A accepted source 已迁移为 DTO/evidence-driven projection。 |
| 已关闭 | `App.tsx` 默认 fallback、`WorkflowStudioLayout.tsx` 的 `workflow-platform` 映射、相关 E2E 默认入口断言。 |
| 需替换/停止迭代 | `WorkflowPlatformMainEntry.tsx` 和 `workflow-platform-main-entry.css` 作为目标首页的继续优化路径。 |
| 需迁移且不得退化 | `WorkflowPlatformMainEntry.tsx` 中当前接入的 PV21 graph/diff/version/run/human/evidence 能力，以及 PV20 executor state/contract/evidence/action 能力。 |
| 已实现 | WP-M5A scenario projection DTO、business output DTO、business-output-report、mock reduction report、三场景机器可读输出摘要 evidence。 |
| 本阶段待新增 | WP-M6 正常路径数据驱动渲染、WP-M7 graph edit/save/readback、WP-M8 publish/run/human/evidence PV13 inline loop、WP-M9 三场景真实 artifact、WP-M10 failure/a11y/perf、WP-M11 aggregate audit。 |
| 本阶段需修改 | `V13EditableStudio.tsx` 需要从静态业务矩阵转为 BFF/DTO first；`workflowConsoleClient.ts` 需要补齐缺失 typed methods；`apps/api/routers/bff.py` 需要补齐 workflow-platform facade 或复用 PV21/PV20/PV19 route composition；acceptance runner 需要覆盖真实用户路径。 |
| No-Go | Browser direct runtime/store write、UI simulation as runtime evidence、docs as implementation evidence、complete Studio/product-grade/production claims。 |

## 6. Interaction Contracts

### Browser To BFF

- Browser 只能通过 BFF DTO route 读取或提交用户确认后的动作。
- PV13 基线不得绕过 `apps/api/routers/bff.py` 调用 WorkflowStore 或 Gateway internals。
- 当前允许的 BFF route families：`/bff/v13/*` compatibility、`/bff/pv19/*`、`/bff/pv20/*`、`/bff/pv21/*`、`/bff/workflow-platform/*`。
- WP-M1A 已确认 `/bff/v13/*` 由主 BFF 提供；这些 routes 仍限定为 PV13 compatibility / handoff-only，不得写成 runtime execution evidence。
- 如果后续新增 `WorkflowPlatformBffFacade`，必须保留 V13/PV19/PV20/PV21 evidence compatibility。
- WP-M6 到 WP-M11 的正常路径必须能通过 browser network log 证明所有业务事实、graph mutation、publish/run/human/evidence 操作均经由允许的 BFF DTO boundary。

### WP-M6 To WP-M11 Target Planes

| Plane | Current architecture | Target architecture | Acceptance focus |
| --- | --- | --- | --- |
| Data rendering | PV13 页面仍有静态业务矩阵和 fallback graph。 | 场景、节点、Inspector、timeline、quality、evidence、chat 初始上下文来自 BFF/DTO 或 artifact refs。 | normal path static sources 为 0。 |
| Graph editing | 有 PV21 能力来源和 PV13 画布交互，但正常路径未完整证明保存回读。 | PV13 画布编辑 WorkflowSpecGraph，并通过 BFF 保存、刷新回读、生成 Diff。 | edit/save/readback/diff E2E。 |
| Runtime actions | PV19/PV21 有 bounded route evidence，PV13 有 parity 面板。 | Publish、run、StationRun、Human Gate、Evidence Review 成为 PV13 工作台内一条连续路径。 | runtime inspect + human action + evidence panel。 |
| Business artifacts | WP-M5A 有机器可读输出摘要。 | 三个业务场景生成可审查产物文件和证据链。 | artifact content + input hash + review refs。 |
| Quality states | 当前以 happy path 和部分边界验收为主。 | 加载、空、错误、拒绝、离线、校验失败、人工拒绝、取消/重试均有 UI 和证据。 | failure-state screenshots + a11y/perf。 |
| Aggregate audit | 当前有多阶段 bounded reports。 | WP-M11 统一 claim-to-evidence matrix，缺证即 BLOCKED。 | aggregate audit PASS。 |

### UI Composition

- PV13 负责首页视觉、画布、场景和 Inspector 基线。
- PV19/PV21 的运行闭环只能以明确 DTO 和 evidence refs 接入 PV13 UI。
- PV20 的 Agent/Tool/Skill/MCP 能力只能以 governed bounded capability 呈现。
- WP-M5A 的文档总结、代码审查、会议整理必须以业务输出 DTO / artifact refs / human review refs 呈现，不能只展示 acceptance report。
- PV22 外部接入不得绕过 PV13 基线工作流平台 host surface，且必须在 WP-M5A 完成或明确延期后复审。

### Capability Migration Path

```text
V13EditableStudio
  -> workflowConsoleClient PV21 typed methods
  -> /bff/pv21 graph / diff / versions / runs / human-actions / evidence
  -> WorkflowStore / Gateway / Evidence refs

V13EditableStudio
  -> workflowConsoleClient PV20 typed methods
  -> /bff/pv20 executor state / contract / evidence / skill / tool / MCP actions
  -> governed approval / denial / redaction evidence

V13EditableStudio
  -> WorkflowPlatformScenarioProjection DTO
  -> document_summary / code_review / meeting_brief input contracts
  -> business output artifacts and evidence refs
  -> human review and quality gates
```

`WorkflowPlatformMainEntry` 的视觉实现不作为目标首页，但它当前已经证明的 PV21/PV20 用户动作必须作为 parity checklist 迁移到 PV13 工作台。WP-M3/WP-M4 的 acceptance runner 必须输出 `workflow-platform-capability-parity-report.json`，逐项证明能力未退化。

### UI To Evidence

- UI 可以展示 evidence refs，但不能构造 runtime truth。
- 设计稿、drawio、介绍页和截图必须标注 evidence class。
- No False Green scan 必须覆盖 UI copy、Markdown docs 和 acceptance report。

## 7. Architecture Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| 继续在退化版 `WorkflowPlatformMainEntry` 上迭代导致体验偏离 PV13。 | High | 文档和 drawio 明确 `V13EditableStudio` 是唯一首页前端基线。 |
| 直接切换 PV13 导致 `WorkflowPlatformMainEntry` 已接入的 PV21/PV20 闭环能力丢失。 | High | WP-M3/WP-M4 必须通过 capability parity report；缺失任一保存/校验/发布/运行/人工门禁/证据/执行器能力即 FAIL。 |
| Stage name drift: V13/PV19/PV20/PV21/PV22 被写成互相替代。 | High | PV13 是前端基线；PV19/PV20/PV21 是能力来源；PV22 是后续接入阶段。 |
| Canvas UX 被误认为 complete Workflow Studio GA。 | High | 验收文档禁止 GA/product-grade wording，并要求 action-level evidence。 |
| PV20 executor 被误写成 unrestricted Agent executor ready。 | High | Agent/Tool/Skill/MCP 文案统一为 governed bounded execution。 |
| 当前本地静态场景数据被误写成真实业务产物。 | Medium | WP-M5A 已增加 scenario projection、business output DTO、mock reduction scan；后续仍需保留 fallback 边界。 |
| WP-M6 到 WP-M11 期间仍保留正常路径 mock，却声明前端功能完整。 | High | `mock-reduction-report.normal_path_static_sources == 0` 是 WP-M6 和 WP-M11 硬门槛；缺失即 BLOCKED。 |
| 只把 PV21/PV20 能力放进面板，没有形成 PV13 内连续用户路径。 | High | WP-M7/WP-M8 必须用浏览器动作日志证明同一工作台完成编辑、保存、发布、运行、人工审查和证据回看。 |
| 三业务场景只有摘要，没有真实可审查产物文件。 | Medium | WP-M9 需要 artifact manifest、content snapshot、input hash 和 human review refs；否则仍只能声明受限完成。 |
| PV22 外部接入早于平台首页与业务场景稳定。 | Medium | PV22 implementation 前先通过 WP-M5B readiness refresh。 |
| `/bff/v13/*` 只存在于 V13 smoke server，却被误认为主 BFF 已完成。 | Medium | WP-M1A route ownership gate：主 BFF route smoke 或 bounded smoke label 必须 PASS。 |

## 8. Allowed Architecture Claim

```text
Workflow Platform main-entry target architecture is aligned to the PV13 frontend baseline, with WP-M5A bounded scenario projection and business output evidence implemented for review.
```

WP-M11 通过后仅允许在有界审查语境中追加：

```text
The PV13-based Workflow Platform frontend architecture has passed PRD-defined functionality closure for bounded review, with data-driven normal paths, persisted graph editing, runtime/human/evidence loop, scenario artifacts and aggregate audit evidence.
```

本文不能证明 implementation complete、runtime complete、production ready 或 complete Workflow Studio GA。
