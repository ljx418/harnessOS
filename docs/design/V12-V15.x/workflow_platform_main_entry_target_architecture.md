# Workflow Platform Main Entry Target Architecture

用途：定义工作流平台首入口目标架构、当前代码实体、待新增/待修改边界和交互关系。
边界：本文是架构设计文档，不是实现证据；不得据此声明运行时或产品完成。

## 1. Architecture Intent

后续 HarnessOS 前端产品不应继续以 V13/PV19/PV20/PV21 分散页面作为主要体验。目标架构需要把已验收的 bounded slices 收敛成一个 Workflow Platform entry shell，并让用户从同一入口完成：

```text
打开工作空间
  -> 编辑或审查 WorkflowSpecGraph
  -> 配置 Agent / Tool / Skill / MCP
  -> 审查 WorkflowDiff
  -> 发布 WorkflowVersion
  -> 运行 WorkflowInstance
  -> 处理 Human gate
  -> 查看 Evidence package
```

## 2. Current Concrete Entities

| Layer | Current entity | Status | Architecture role |
| --- | --- | --- | --- |
| Browser entry | `apps/workflow-console/src/App.tsx` | 需修改/锚定 | 决定根入口和 query-state fallback。 |
| Studio shell | `apps/workflow-console/src/ui/layout/WorkflowStudioLayout.tsx` | 需修改/锚定 | 统一 V13/PV19/PV20/PV21 stage surface。 |
| Editable canvas | `V13EditableStudio` | 已实现 bounded slice | 提供 graph editing/canvas interaction baseline。 |
| Runtime platform | `PV19RuntimeWorkflowPlatform` | 已实现 bounded slice | 提供 publish/run/human/evidence closed loop baseline。 |
| Agent executor view | `PV20AgentExecutor` | 已实现 bounded slice | 提供 governed skill/tool/MCP execution evidence path。 |
| Complete Studio candidate | `PV21CompleteWorkflowStudio` | 已实现 bounded candidate | 提供当前最接近首入口的 bounded workflow studio surface。 |
| BFF router | `apps/api/routers/bff.py` | 已实现且需扩展/整合 | 提供 `/bff/pv19/*`、`/bff/pv20/*`、`/bff/pv21/*` DTO boundary。 |
| Workflow store | `core/workflows/store.py` | 已实现且需复用 | 持久化 WorkflowSpec / WorkflowVersion / WorkflowInstance / StationRun。 |
| Runtime gateway | `apps/gateway/service.py` | 已实现且需复用 | 保持 Gateway/RPC/control-plane boundary。 |
| Evidence | `docs/design/V12-V15.x/evidence/*` | 已有多阶段证据 | 阶段验收和 claim-to-evidence 来源。 |

## 3. Target Layering

```text
User
  -> Workflow Platform Main Entry
  -> Workflow Studio Shell
  -> Canvas Interaction Layer
  -> Inspector / Resource / Evidence Panels
  -> Workflow Platform BFF Facade
  -> PV19 / PV20 / PV21 bounded route families
  -> WorkflowStore / GatewayService / Artifact and Evidence stores
```

## 4. Target Components

| Component | Type | Status | Responsibility |
| --- | --- | --- | --- |
| `WorkflowPlatformMainEntry` | Browser product shell | 待新增或由 PV21 shell 提升 | 默认首入口、工作空间上下文、主导航和全局状态。 |
| `WorkflowPlatformCanvas` | Canvas layer | 需修改 | 统一节点拖拽、滚轮缩放、自由连线、取消连线、箭头可见性和首眼布局。 |
| `WorkflowPlatformInspector` | Detail panel | 需修改 | 统一 node / edge / Agent / Tool / MCP / evidence detail。 |
| `WorkflowPlatformRunPanel` | Runtime panel | 需修改 | 展示 publish、rollback、run history、WorkflowInstance 和 StationRun。 |
| `WorkflowPlatformEvidencePanel` | Evidence panel | 需修改 | 汇总 artifact、trace、quality、audit、claim、redaction。 |
| `WorkflowPlatformAgentPanel` | Resource panel | 需修改 | 展示受治理 Agent/Tool/Skill/MCP 能力，不暗示 unrestricted automation。 |
| `WorkflowPlatformBffFacade` | BFF consolidation target | 待新增/待设计 | 对后续首入口提供稳定 DTO facade，内部可复用 PV19/PV20/PV21 route families。 |

## 5. Current-To-Target Classification

| Classification | Items |
| --- | --- |
| 已实现 | PV19 runtime closed loop、PV20 bounded executor path、PV21 bounded Studio candidate、workflow store、BFF route families、evidence packages。 |
| 需修改 | Root entry copy/state、WorkflowStudioLayout stage routing、canvas interaction quality、edge rendering/cancel behavior、evidence aggregation layout、PV20/PV21 evidence aggregation wording。 |
| 待新增 | Workflow Platform main-entry doc gate、single target information architecture、future BFF facade naming、unified acceptance runner/report shape。 |
| No-Go | Browser direct runtime/store write、UI simulation as runtime evidence、docs as implementation evidence、complete Studio/product-grade/production claims。 |

## 6. Interaction Contracts

### Browser To BFF

- Browser 只能通过 BFF DTO route 读取或提交用户确认后的动作。
- 首入口不得绕过 `apps/api/routers/bff.py` 调用 WorkflowStore 或 Gateway internals。
- 后续如果新增 `WorkflowPlatformBffFacade`，必须保留 PV19/PV20/PV21 evidence compatibility。

### BFF To Runtime

- `WorkflowDiff` 必须显式人工确认。
- `WorkflowVersion` 发布和 `WorkflowInstance` 运行必须有 route log、DTO snapshot 和 runtime inspect evidence。
- `StationRun`、approval、artifact、trace、quality 和 audit refs 必须可回读。

### UI To Evidence

- UI 可以展示 evidence refs，但不能构造 runtime truth。
- 设计稿、drawio、介绍页和截图必须标注 evidence class。
- No False Green scan 必须覆盖 UI copy、Markdown docs 和 acceptance report。

## 7. Architecture Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Stage name drift: V13/PV19/PV20/PV21/PV22 被写成互相替代。 | High | 用 WP-M0 作为首入口对齐门禁，明确它不是新完成 claim。 |
| Canvas UX 被误认为 complete Workflow Studio GA。 | High | 验收文档禁止 GA/product-grade wording，并要求 action-level evidence。 |
| PV22 外部接入早于平台首入口稳定。 | Medium | PV22 implementation 前先通过 WP-M0 文档和首入口开发门禁。 |
| PV20 executor 被误写成 unrestricted Agent executor ready。 | High | Agent/Tool/Skill/MCP 文案统一为 governed bounded execution。 |

## 8. Allowed Architecture Claim

```text
Workflow Platform main-entry target architecture is documented and ready for implementation review.
```

本文不能证明 implementation complete、runtime complete、production ready 或 complete Workflow Studio GA。
