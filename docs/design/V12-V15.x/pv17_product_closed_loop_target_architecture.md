# PV17 Product Closed Loop Target Architecture

用途：定义路径1的目标架构、当前架构差异和代码实体交互。
阅读对象：架构、后端、前端、测试、审计人员。
边界：本文只定义目标实现路径；不改变代码，不证明实现已完成，不替代 browser E2E、BFF route log、DTO schema 或 runtime evidence。
PV16 `/bff/pv16/*` 来自 test-only BFF evidence route，PV17 只能把它作为参考，不能把它当作正式产品 API。

## 1. 架构意图

PV17 采用“主线化 PV16 pilot”的保守路径：复用已存在的 workflow-console、BFF、GatewayService、WorkflowStore、Station Agent contracts、artifact/trace/evidence 设施，把 test-only product-runtime journey 转成正式开发目标。

目标不是新增一个孤立页面，而是让用户在 `apps/workflow-console` 的主产品体验中通过 BFF DTO 串起正式 runtime 能力。

## 2. 当前到目标分层

```text
User
  -> apps/workflow-console/src/App.tsx
  -> ConsoleShell / WorkflowStudioLayout / WorkflowCanvas / panels
  -> WorkflowConsoleClient
  -> apps/api/routers/bff.py
  -> apps.gateway.service.GatewayService
  -> core.workflows.store.WorkflowRepository / WorkflowStore
  -> apps.gateway.artifacts / traces / approvals / connector_execution
  -> evidence package and acceptance runner
```

## 3. 具体代码实体状态

| Layer | 已实现/复用 | PV17 需修改 | PV17 待新增 |
| --- | --- | --- | --- |
| Browser shell | `App.tsx`, `ConsoleShell`, `WorkflowStudioLayout` | 合并 PV16 journey 到主线导航和状态模型 | `ProductClosedLoopView` 或等价主线状态 |
| Studio canvas | `WorkflowCanvas`, `WorkflowNodeCard`, `WorkflowEditingPanel`, `RightPanels` | 让 draft / patch / publish / run / inspect 使用同一上下文 | 闭环状态条、run inspect drawer、evidence summary panel |
| Browser client | `WorkflowConsoleClient` | 明确正式 `/bff/*` allowlist，避免依赖 `/bff/pv16/*` test route | product entity DTO client、run inspect DTO client |
| API BFF | `apps/api/routers/bff.py` | 将产品实体、workflow run inspect、evidence summary 收敛为正式 BFF DTO | workspace/project/app/Station Agent mutation routes |
| Runtime API | `apps/api/routers/runs.py` | 与 BFF run handoff 口径对齐 | 无；PV17 优先复用而不是绕过 |
| Gateway | `GatewayService` workflow、artifact、trace、approval、quality methods | 明确 BFF 调用路径和 scope/audit refs | claim-to-evidence read model 方法如需要再加 |
| Workflow domain | `core/workflows/models.py`, `core/workflows/store.py` | 确认 WorkflowPatch -> WorkflowVersion -> WorkflowInstance 连续性 | Product closed loop DTO schema |
| Station Agent | `core/station_agents/contracts.py` | 将 StationAgentDescriptor 映射到产品实体 DTO | Station Agent mutation audit projection |
| Packs/connectors | `core/packs/registry.py`, `apps/gateway/connectors.py`, `connector_execution.py` | 仅作为 capability refs 和 reference packs 展示 | 不在 PV17 product closed loop 中新增 business pack |
| Evidence | `apps/gateway/artifacts.py`, `traces.py`, `agent_operation_evidence_store.py` | 统一 run inspect、artifact lineage、route log、claim scan 引用 | PV17 evidence package schema 和 runner |

## 4. 目标交互链路

| 用户动作 | Browser | BFF | Gateway/Core | Evidence |
| --- | --- | --- | --- | --- |
| 进入产品 | `App.tsx` 加载主 Console | `GET /bff/...` health / inventory DTO | `GatewayService.method_list`, app/profile/workflow list | screenshot、DTO snapshot、route log |
| 创建产品实体 | Console 表单提交 | BFF mutation DTO + ownership policy | `ScopeContext`、Station Agent contract projection | audit ref、negative fixture |
| 编辑工作流 | Studio canvas / inspector | patch proposal / diff / publish DTO | `WorkflowRepository.propose_patch`, `publish_template` | WorkflowDiff、schema validation |
| 确认运行 | run button with `user_confirmed=true` | BFF run handoff DTO | `GatewayService.workflow_instance_start` 或 `/v1/runs` controlled path | runtime event refs |
| 检查运行 | Run Inspect drawer | instance/station/artifact/quality DTO | `workflow_instance_status`, `station_run_list`, `artifact_lineage`, `trace_list` | trace/artifact/quality refs |
| 审计证据 | Evidence panel | evidence summary DTO | read-only artifact/trace/audit stores | claim-to-evidence matrix、redaction scan |

## 5. 边界规则

- Browser 不能直接调用 `/v1/rpc`、`/internal/runtime`、`/runtime/store`、`/api/runtime`、`/debug/runtime`。
- Product entity mutation 不能写 runtime truth；它只能产生产品实体、scope、policy、audit refs。
- WorkflowDiff 不能静默 publish/run；publish/run 必须由用户确认。
- Observability / Evidence 只能读取 runtime evidence，不能构造 runtime truth。
- Agent/Station 配置不能暴露 raw secret、raw provider payload、raw artifact content。
- PV16 test-only route 可作为回归参考，不可作为 PV17 正式 API 完成声明。

## 6. 架构取舍

PV17 选择 modular monolith + BFF boundary，而不是新增独立 service。理由：

- 现有 `GatewayService`、`WorkflowStore`、BFF 和 workflow-console 已有可复用实体。
- 当前风险是产品路径断裂，不是服务拆分不足。
- BFF DTO 可把浏览器体验和 runtime truth 解耦，最小化误报风险。

代价是 PV17 仍不解决完整生产治理、租户 SLA、商业化计费和完整插件市场。这些保持在后续 backlog。
