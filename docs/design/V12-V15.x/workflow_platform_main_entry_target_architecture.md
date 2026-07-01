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
| No-Go | Browser direct runtime/store write、UI simulation as runtime evidence、docs as implementation evidence、complete Studio/product-grade/production claims。 |

## 6. Interaction Contracts

### Browser To BFF

- Browser 只能通过 BFF DTO route 读取或提交用户确认后的动作。
- PV13 基线不得绕过 `apps/api/routers/bff.py` 调用 WorkflowStore 或 Gateway internals。
- 当前允许的 BFF route families：`/bff/v13/*` compatibility、`/bff/pv19/*`、`/bff/pv20/*`、`/bff/pv21/*`、`/bff/workflow-platform/*`。
- WP-M1A 已确认 `/bff/v13/*` 由主 BFF 提供；这些 routes 仍限定为 PV13 compatibility / handoff-only，不得写成 runtime execution evidence。
- 如果后续新增 `WorkflowPlatformBffFacade`，必须保留 V13/PV19/PV20/PV21 evidence compatibility。

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
| PV22 外部接入早于平台首页与业务场景稳定。 | Medium | PV22 implementation 前先通过 WP-M5B readiness refresh。 |
| `/bff/v13/*` 只存在于 V13 smoke server，却被误认为主 BFF 已完成。 | Medium | WP-M1A route ownership gate：主 BFF route smoke 或 bounded smoke label 必须 PASS。 |

## 8. Allowed Architecture Claim

```text
Workflow Platform main-entry target architecture is aligned to the PV13 frontend baseline, with WP-M5A bounded scenario projection and business output evidence implemented for review.
```

本文不能证明 implementation complete、runtime complete、production ready 或 complete Workflow Studio GA。
