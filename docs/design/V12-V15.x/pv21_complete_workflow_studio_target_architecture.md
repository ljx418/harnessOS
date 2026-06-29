# PV21 Complete Workflow Studio Target Architecture

用途：定义 PV21 目标架构、代码实体、DTO 契约和交互关系。
阅读对象：架构、开发、测试、审计人员。
边界：本文描述目标实现，不是运行证据；不得据此声明完整工作流工作台已完成。

## 1. Architecture Intent

PV21 将 V13 editable Studio pilot、PV19 runtime workflow loop 和 PV20 governed Agent executor 组合成完整 Workflow Studio 候选架构。目标不是新增业务专用页面，而是在通用工作流平台上形成一条可审计的产品路径：

```text
Browser Studio -> BFF DTO -> Gateway facade -> Workflow Store / Runtime -> Agent Executor -> Evidence Read Model
```

浏览器只处理交互和 DTO 展示；运行事实必须来自后端 WorkflowVersion、WorkflowInstance、StationRun、artifact、trace、approval 和 quality stores。

## 2. Current To Target Mapping

| Area | Current baseline | PV21 target change |
| --- | --- | --- |
| Studio shell | V13/PV19/PV20 有独立受限页面。 | 统一为 PV21 Studio 工作台入口，默认可审查真实画布和版本/运行/evidence 区。 |
| Canvas graph | V13 pilot 支持可编辑图。 | 增加节点库、Inspector、连接规则、validation、long text/error/empty states。 |
| Versioning | PV19 支持 publish WorkflowVersion。 | 增加版本列表、版本比较、rollback、run history 和 audit refs。 |
| Runtime | PV19 支持 WorkflowInstance closed loop。 | 在 Studio 内直接运行已发布版本，并显示运行状态和 inspect。 |
| Agent execution | PV20 支持受控 executor 证据页。 | 将 Agent execution contract 嵌入节点 Inspector、运行 inspect 和 evidence summary。 |
| Evidence | PV19/PV20 分阶段 evidence。 | 聚合 artifact、trace、quality、approval、claim、redaction refs。 |

## 3. Concrete Code Entity Map

| Layer | Concrete entity | Status | PV21 responsibility |
| --- | --- | --- | --- |
| Browser routing | `apps/workflow-console/src/App.tsx` | 需修改 | 默认入口或 `studio=pv21-complete-workflow-studio` 路由到 PV21 工作台。 |
| Browser shell | `apps/workflow-console/src/ui/pv21/PV21CompleteWorkflowStudio.tsx` | 待新增 | 承载画布、节点库、Inspector、版本、运行和 evidence layout。 |
| Canvas components | `apps/workflow-console/src/components/canvas/*` or pv21-local components | 需修改/待新增 | 复用 XyFlow foundation，提供通用节点、连线、selection、validation overlay。 |
| BFF client | `apps/workflow-console/src/lib/api.ts` | 需修改 | 增加 PV21 DTO client methods；不得调用 raw `/v1/rpc`。 |
| Frontend types | `apps/workflow-console/src/types/pv21.ts` | 待新增 | 定义 PV21 Studio DTO、Graph DTO、Diff DTO、Version DTO、Run DTO、Evidence DTO。 |
| BFF routes | `apps/api/routers/bff.py` | 需修改 | 增加 `/bff/pv21/*` facade，聚合 Gateway/runtime/evidence read models。 |
| Gateway facade | `apps/gateway/service.py` | 需修改 | 暴露 workflow graph、version、run、human action、evidence operations。 |
| Workflow truth | `core/workflows/models.py`, `core/workflows/store.py` | 需修改 | 支持 graph validation readback、version compare、rollback refs、run history。 |
| Agent executor | `core/agent_executor/*`, `core/station_agents/contracts.py` | 已实现/需接入 | 将 AgentExecutionEnvelope / Result 绑定到 Studio inspect 和 evidence。 |
| Policy | `core/policies/*`, `core/auth/tenant_boundary.py` | 已实现/需接入 | 校验 scope、approval、durable mutation denial、redaction。 |
| Evidence | `apps/gateway/artifacts.py`, `apps/gateway/traces.py`, `apps/gateway/approvals.py` | 已实现/需聚合 | 为 Studio 提供 evidence summary 和 claim-to-evidence refs。 |
| Acceptance | `scripts/acceptance/*` or stage-specific runner | 待新增 | 自动执行 PV21 backend/browser/claim/redaction acceptance。 |

## 4. BFF Route Contract

PV21 建议使用独立 route namespace，避免与 PV19/PV20 页面契约互相污染。

| Route | Method | Purpose |
| --- | --- | --- |
| `/bff/pv21/studio/state` | GET | 获取 workspace/project/app/workflow、节点库、当前版本、run history 摘要。 |
| `/bff/pv21/workflows/{workflow_id}/graph` | GET | 获取 WorkflowGraph DTO。 |
| `/bff/pv21/workflows/{workflow_id}/graph` | PUT | 保存 draft graph；返回 revision 和 validation summary。 |
| `/bff/pv21/workflows/{workflow_id}/graph/validate` | POST | 执行 graph validation。 |
| `/bff/pv21/workflows/{workflow_id}/diff` | POST | 基于 draft 与目标版本生成 WorkflowDiff。 |
| `/bff/pv21/workflows/{workflow_id}/versions` | GET | 获取版本列表、当前 published version 和 rollback candidates。 |
| `/bff/pv21/workflows/{workflow_id}/versions/publish` | POST | 发布 WorkflowVersion；必须含 user confirmation。 |
| `/bff/pv21/workflows/{workflow_id}/versions/{version_id}/rollback` | POST | 回滚到指定版本；必须保留 audit refs。 |
| `/bff/pv21/workflows/{workflow_id}/runs` | POST | 运行指定 WorkflowVersion。 |
| `/bff/pv21/runs/{run_id}/inspect` | GET | 获取 WorkflowInstance / StationRun inspect DTO。 |
| `/bff/pv21/runs/{run_id}/human-actions` | POST | 对 waiting human gate 做人工操作。 |
| `/bff/pv21/runs/{run_id}/evidence` | GET | 获取 evidence summary。 |

## 5. DTO Set

| DTO | Required fields |
| --- | --- |
| `PV21StudioStateDTO` | workspace, project, app, workflow, node_library, current_draft, published_version, run_history, evidence_health. |
| `PV21WorkflowGraphDTO` | workflow_id, draft_revision, nodes, edges, layout, validation_status, updated_at. |
| `PV21GraphNodeDTO` | node_id, type, label, inputs, outputs, policy, executor_binding, ui_state. |
| `PV21GraphValidationDTO` | status, errors, warnings, affected_nodes, affected_edges, publish_blocked. |
| `PV21WorkflowDiffDTO` | base_version, draft_revision, added, removed, changed, risk_summary, user_confirmation_required. |
| `PV21WorkflowVersionDTO` | version_id, status, created_at, published_by, graph_hash, audit_refs, rollback_allowed. |
| `PV21WorkflowRunDTO` | run_id, version_id, state, station_runs, current_human_gate, trace_refs. |
| `PV21HumanActionDTO` | action_id, run_id, station_id, decision, actor, audit_ref, resulting_state. |
| `PV21EvidenceSummaryDTO` | artifact_refs, trace_refs, quality_refs, approval_refs, claim_refs, redaction_refs, missing_refs. |

## 6. Interaction Flow

1. `App.tsx` routes to `PV21CompleteWorkflowStudio`.
2. Browser loads `/bff/pv21/studio/state`.
3. User edits graph; browser saves draft via `/bff/pv21/workflows/{id}/graph`.
4. BFF calls Gateway facade, which writes draft state into workflow store.
5. User validates graph; Gateway returns validation result with affected node refs.
6. User requests diff; BFF returns `PV21WorkflowDiffDTO`.
7. User confirms publish; Gateway creates WorkflowVersion and audit refs.
8. User starts run; runtime creates WorkflowInstance and StationRun.
9. Agent nodes use governed executor contract from PV20.
10. Human gate uses BFF human action route and updates runtime state.
11. Evidence route aggregates artifact, trace, quality, approval, claim and redaction refs.
12. User rolls back; version history and run history remain visible.

## 7. Architecture Red Lines

- Browser must not call `/v1/rpc`, `/v1/internal/*` or raw runtime store routes.
- BFF must not leak raw provider payload, raw prompts, secrets or connector internals.
- Workflow graph operations must stay generic; business Pack behavior must live in Pack/domain adapters.
- Rollback must create audit evidence instead of deleting history.
- Validation failure must block publish and run.
- User confirmation is required for publish, rollback and human gate actions.

