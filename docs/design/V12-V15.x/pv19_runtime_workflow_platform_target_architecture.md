# PV19 Runtime Workflow Platform Target Architecture

用途：定义 PV19 “完整工作流平台受控闭环”的目标架构、当前差异和具体代码实体交互。
阅读对象：架构、后端、前端、测试、审计人员。
边界：本文定义后续实现路径；实际完成状态必须以代码、browser E2E、BFF route log、DTO snapshot、runtime report 和 evidence package 为准。

## 1. Architecture Intent

PV19 采用 modular monolith + BFF boundary 的保守路径，把 V13 Studio pilot、PV17 product closed loop 和 PV18 real business evidence 汇合成一个通用平台闭环。

目标不是新增孤立业务页面，而是证明工作流平台可以通过通用 DSL、版本、Runtime、人工卡点和 Evidence 机制运行真实业务工作流。

## 2. Current To Target Flow

```text
User
  -> apps/workflow-console/src/App.tsx
  -> apps/workflow-console/src/ui/pv19/PV19RuntimeWorkbench.tsx
  -> WorkflowConsoleClient
  -> apps/api/routers/bff.py /bff/pv19/*
  -> apps.gateway.service.GatewayService
  -> core.workflows.models / core.workflows.store
  -> apps.api.routers.runs / workflow runtime methods
  -> approvals / traces / artifacts / quality / audit stores
  -> PV19 evidence package and acceptance runner
```

## 3. Code Entity Status

| Layer | 已实现/复用 | PV19 需修改 | PV19 待新增 |
| --- | --- | --- | --- |
| Browser shell | `App.tsx`, `WorkflowStudioLayout`, V13/PV17/PV18 routes | 将默认体验指向 `?studio=pv19-runtime-workflow-platform`，根路径不得作为空白交付体验 | `apps/workflow-console/src/ui/pv19/PV19RuntimeWorkbench.tsx` |
| Canvas Studio | V13 editable graph、node inspector、WorkflowDiff | 让 graph edit 可发布为 runtime version | runtime-backed run panel、human gate panel |
| Browser client | `WorkflowConsoleClient` | 统一 PV19 DTO 方法和 route allowlist | PV19 workflow draft/version/run/human/evidence client methods |
| BFF | `apps/api/routers/bff.py` | 聚合 graph、version、run、human、evidence DTO | 固定新增 `/bff/pv19/*` route set，不使用 PV16/PV17/PV18 test-only route 作为 PV19 完成证据 |
| Runs API | `apps/api/routers/runs.py` | 与 WorkflowVersion run handoff 对齐 | 无；优先复用正式 run path |
| Gateway | `apps/gateway/service.py` | 串接 workflow version、runtime events、artifact、trace、approval | 新增通用 `pv19.workflow_closed_loop_projection` 聚合方法或等价内部 helper，必须业务无关 |
| Workflow domain | `core/workflows/models.py`, `core/workflows/store.py` | 确认 WorkflowSpecGraph -> WorkflowVersion -> WorkflowInstance 连续性 | 不新增业务专用模型；human gate 用 `Station.approval_required`、`WorkflowTemplate.approval_points`、`WorkflowInstanceStatus.WAITING_APPROVAL`、`StationRunStatus.WAITING_APPROVAL` 表达 |
| Human loop | approval/handoff/audit 相关 store | 让人工动作影响 runtime 状态 | PV19 human interaction DTO |
| Evidence | artifact registry、trace store、quality refs | 聚合 runtime evidence 和 claim matrix | PV19 evidence summary schema 和 runner |
| Business sample | `packs/knowledge`、folder summary/reference workflow | Knowledge OPC 作为主样例，folder-summary/reference workflow 作为非 Knowledge 复用检查；二者不得污染平台核心 | sample workflow fixture |

## 4. Planned BFF Interface

PV19 实现固定使用以下 BFF DTO route。后续若要提升为非 PV19 正式 API，必须另立迁移计划；本阶段不得用其他阶段 test-only route 替代这些 route 的验收证据：

```text
GET  /bff/pv19/workbench/state
GET  /bff/pv19/workflows/{workflow_id}/graph
POST /bff/pv19/workflows/{workflow_id}/graph/validate
POST /bff/pv19/workflows/{workflow_id}/diff
POST /bff/pv19/workflows/{workflow_id}/versions/publish
POST /bff/pv19/workflows/{workflow_id}/runs
GET  /bff/pv19/runs/{run_id}/inspect
POST /bff/pv19/runs/{run_id}/human-actions
GET  /bff/pv19/runs/{run_id}/evidence
```

最低 DTO：

- `PV19WorkbenchStateDTO`
- `PV19WorkflowGraphDTO`
- `PV19GraphValidationDTO`
- `PV19WorkflowDiffDTO`
- `PV19WorkflowVersionDTO`
- `PV19RunStartDTO`
- `PV19RunInspectDTO`
- `PV19HumanActionDTO`
- `PV19EvidenceSummaryDTO`

所有 DTO 必须包含 `schema_version`、scope、redaction status 和 evidence/audit refs。

## 4.1 Human Gate Model

PV19 不新增业务专用 `HumanGateNode`。人工交互用现有 workflow domain 表达：

| Concept | Required representation |
| --- | --- |
| Human gate node | `Station.approval_required=true` plus `metadata.node_kind="human_gate"`。 |
| Human gate policy | `WorkflowTemplate.approval_points[]` and station `metadata.approval_policy`。 |
| Waiting state | `WorkflowInstanceStatus.WAITING_APPROVAL` and/or `StationRunStatus.WAITING_APPROVAL`。 |
| Human action | BFF `PV19HumanActionDTO` calls approval/handoff store and updates workflow repository state. |
| Audit | approval trace record, handoff audit record and PV19 human-interaction report. |

如果实现发现现有模型无法表达上述语义，必须先更新 PV19 文档和 readiness audit，再进入代码修改。

## 5. Runtime Interaction

| Step | Browser | BFF | Runtime/Core | Evidence |
| --- | --- | --- | --- | --- |
| 打开工作台 | 加载 active workflow 和 canvas | state DTO | workflow list / health | screenshot、DTO snapshot |
| 编辑图 | add/connect/configure/human gate | graph validate/diff | WorkflowSpecGraph validation | action log、diff |
| 发布版本 | confirm publish | version publish DTO | WorkflowVersion append/readback | audit ref、version snapshot |
| 启动运行 | user_confirmed run | run start DTO | WorkflowInstance start | route log、runtime event |
| 人工处理 | approve/reject/input/retry | human action DTO | state transition | audit trail、trace ref |
| 审查证据 | evidence panel | evidence summary DTO | artifact/trace/quality/audit read model | claim matrix、redaction |

## 6. Boundary Rules

- Browser 不能直接调用 `/v1/rpc`、internal runtime/store、connector runtime 或 debug route。
- WorkflowDiff 不能静默 publish/run；必须有用户确认。
- Runtime 必须按发布 WorkflowVersion 执行，不得按前端临时 graph 执行。
- 人工交互必须写入后端受控状态和 audit trail，不得只是 UI 文案。
- Evidence view 只能读取 artifact、trace、quality、audit，不得构造 runtime truth。
- 业务样例只能位于 pack/domain adapter/BFF facade/UI fixture，不得在 Core/Gateway/App shell 加业务专用分支。

## 7. Architecture Tradeoff

PV19 继续选择在现有 BFF、Gateway、WorkflowStore 和 workflow-console 中演进，而不是拆分新服务。理由：

- 当前风险是闭环断裂和证据不足，不是服务边界不足。
- 已有 V13/PV17/PV18 代码实体可复用。
- BFF DTO 能把产品体验和 runtime truth 解耦。

代价是 PV19 仍不解决生产 SLA、多租户、商业计费、完整外部生态和完整 Agent executor。
