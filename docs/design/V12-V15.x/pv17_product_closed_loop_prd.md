# PV17 Product Closed Loop PRD

用途：定义路径1作为当前阶段目标的产品规格。
阅读对象：产品、架构、开发、测试、审计人员和外部 Agent。
边界：本文是开发规格，不是实现证据；不得把本文、drawio、截图或 docs/present 页面当作 runtime / BFF / DTO / browser E2E / production evidence。
PV16 `/bff/pv16/*` 来自 test-only BFF evidence route，PV17 只能把它作为参考，不能把它当作正式产品 API。

## 1. 阶段定位

PV17 是 post-PV16 的下一阶段，目标是把已通过 bounded review 的 V12-V15/PV16 片段推进为一条主线产品闭环：

```text
setup -> Product Console -> Mission Studio -> confirm run -> inspect -> evidence
```

PV16 已证明一条 product-runtime hardening pilot ready for review，但 PV16 的 `/bff/pv16/*` 主要来自 `apps/workflow-console/e2e/bff_smoke_server.py` 的 test-only BFF 和 Playwright 证据链。PV17 不能把这些 test-only route 直接描述为正式产品 API；PV17 的产品目标是定义后续如何把这些能力主线化到 `apps/api/routers/bff.py`、`apps/api/routers/runs.py`、`apps/gateway/service.py`、`core/workflows/store.py` 和 `apps/workflow-console`。

## 2. 目标用户

| 用户 | 目标体验 | PV17 要证明的内容 |
| --- | --- | --- |
| 小团队操作者 | 从浏览器创建项目、配置 Station Agent、进入 Studio、确认运行并查看证据。 | 一条可审查的产品闭环，而不是分散的阶段页面。 |
| 技术审计者 | 从 UI、BFF route log、DTO、runtime refs、artifact refs、trace refs 追溯每个正向声明。 | 证据链能区分正式主线路径、test-only pilot 和规划文档。 |
| 平台开发者 | 知道哪些代码实体需要新增、修改、复用，哪些边界不能绕过。 | 开发计划能直接转成实现任务和验收任务。 |

## 3. 当前事实

| Area | 当前事实 | 代码或证据入口 |
| --- | --- | --- |
| 浏览器入口 | `apps/workflow-console/src/App.tsx` 支持 `?studio=` 阶段页面和主 Console。 | `apps/workflow-console/src/ui/layout/WorkflowStudioLayout.tsx` |
| PV16 页面 | PV16 页面可展示实体 mutation、runtime inspect、deployment hardening 和 journey。 | `apps/workflow-console/src/ui/pv16/PV16ProductRuntimeHardening.tsx` |
| PV16 BFF 证据 | `/bff/pv16/*` 位于 e2e smoke server，是验收证据路径。 | `apps/workflow-console/e2e/bff_smoke_server.py` |
| 正式 BFF | 主线 BFF 已有 workflow、instance、patch、agent、evidence、artifact、event routes。 | `apps/api/routers/bff.py` |
| runtime API | `/v1/runs`、`/v1/runs/stream`、`/v1/rpc` 已由 GatewayService 支撑。 | `apps/api/routers/runs.py` |
| workflow runtime | WorkflowTemplate、WorkflowDraft、WorkflowVersion、WorkflowInstance、StationRun、QualityEvaluation 已有模型和 store。 | `core/workflows/models.py`, `core/workflows/store.py` |
| Station Agent 边界 | StationAgentDescriptor、AgentCapabilityDecision、AgentInvocationEvidence 已有 bounded contracts。 | `core/station_agents/contracts.py` |
| packs/connectors | meeting、knowledge、video_studio pack 和 connector registry/runtime 已存在。 | `core/packs/registry.py`, `apps/gateway/connectors.py`, `apps/gateway/connector_execution.py` |

## 4. PV17 目标体验

PV17 完成后，用户应能在一个浏览器产品路径中完成：

1. 打开 Product Console，看到当前 workspace、project、app、workflow、Station Agent 和系统健康状态。
2. 创建或选择 workspace/project/app，所有 durable mutation 通过 BFF DTO，并返回 audit refs。
3. 打开 Mission Studio，加载 WorkflowTemplate / WorkflowDraft / WorkflowVersion，看到节点、边、Inspector、质量规则、审批点和证据 refs。
4. 通过 WorkflowDiff 或显式编辑确认一次 publish / run，不允许 source=agent 静默执行 durable mutation。
5. 运行 WorkflowInstance，并在 UI 中看到 station run 状态、runtime events、trace refs、artifact refs、quality refs 和 approval refs。
6. 打开 Evidence / Operations 视图，检查 claim-to-evidence、redaction、route boundary、artifact lineage 和 trace timeline。
7. 在失败、空数据、加载、权限拒绝、运行失败、证据缺失时看到明确状态和下一步。

## 5. 功能范围

| 能力 | PV17 目标 | 主要实体 |
| --- | --- | --- |
| Product Console | 把分散阶段页面整合为一个主线入口。 | `App.tsx`, `ConsoleShell`, `WorkflowStudioLayout` |
| Product entity mutation | 正式化 workspace/project/app/Station Agent mutation DTO 和 audit refs。 | `apps/api/routers/bff.py`, `core/apps/profiles.py`, `core/station_agents/contracts.py` |
| Studio graph continuity | 从 draft / patch / version 到 run 的上下文连续。 | `WorkflowConsoleClient`, `WorkflowEditingPanel`, `core/workflows/store.py` |
| Runtime run/inspect | 用户确认后启动 WorkflowInstance，并用 BFF DTO 展示运行状态和证据 refs。 | `apps/api/routers/runs.py`, `GatewayService.workflow_instance_start`, `GatewayService.station_run_list` |
| Evidence review | 统一 trace、artifact、quality、approval、operation evidence 和 route logs。 | `apps/gateway/artifacts.py`, `apps/gateway/traces.py`, `apps/api/agent_operation_evidence_store.py` |
| Browser boundary | 浏览器只走 `/bff/*` 和明确允许的 public route，不直连 internal runtime/store。 | Playwright network log, route denylist |

## 6. 非目标

- 不声明 HarnessOS 生产可用。
- 不声明 Xpert parity complete。
- 不声明 product-grade frontend complete。
- 不声明 complete Workflow Studio ready。
- 不声明 Agent executor ready。
- 不把 PV16 test-only BFF 路由迁移计划等同于正式实现。
- 不把 Meeting / Knowledge / Video Studio reference pack 说成最终业务产品。

## 7. 允许声明

PV17 文档完成后允许的声明：

```text
PV17 product closed loop development plan ready for implementation review.
```

PV17 后续实现通过验收后才可使用新的 bounded claim；该 claim 必须由证据包和 runner 单独定义。
