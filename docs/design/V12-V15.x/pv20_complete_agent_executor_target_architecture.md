# PV20 Complete Agent Executor Target Architecture

用途：定义 PV20 目标架构、代码实体和交互关系。
阅读对象：架构、开发、测试、审计人员。
边界：本文描述目标实现，不是运行证据；不得据此声明 Agent executor 已完成。

## 1. Architecture Intent

PV20 在 PV19 runtime-backed workflow platform 上增加受治理 Agent executor plane。执行器必须服务于 WorkflowInstance / StationRun，不能成为绕过工作流、审批和 evidence 的独立自动化通道。

## 2. Concrete Code Entity Map

| Layer | Current entity | PV20 responsibility |
| --- | --- | --- |
| Browser / BFF | `apps/workflow-console/src/ui/pv19/PV19RuntimeWorkflowPlatform.tsx` | 增加 Agent execution inspect 区域；只显示 BFF DTO。 |
| BFF | `apps/api/routers/bff.py` | 增加 `/bff/pv20/*` 或 PV19-compatible executor read model routes；不暴露 raw runtime/internal route。 |
| Gateway facade | `apps/gateway/service.py` | 注册 executor-facing workflow station operations，并聚合 approval/trace/artifact refs。 |
| Workflow truth | `core/workflows/store.py`, `core/workflows/models.py` | WorkflowInstance、StationRun、QualityEvaluation、WorkflowContext 继续作为状态事实。 |
| Agent contract | `core/station_agents/contracts.py` | 定义 Agent descriptor、context envelope、capability decision、run result 和 redaction helpers。 |
| Executor runtime | new `core/agent_executor/` or equivalent | 执行 AgentExecutionEnvelope，调用 allowlist skill/tool/MCP adapter，写入 StationRun evidence。 |
| Runtime adapter | `core/runtime_adapter/adapters.py` | 提供 LLM/simple/OpenHarness adapter boundary，并注入 governance metadata。 |
| Skill registry | `core/skills/registry.py`, `core/skills/loader.py` | 解析 allowlisted skill；未知 skill 必须拒绝。 |
| MCP / connector | `apps/gateway/connector_execution.py`, `apps/gateway/connectors.py` | 通过受治理 connector runtime 调用 MCP；直接内部调用必须拒绝。 |
| Policy | `core/policies/v9_agent_executor_safety.py`, `core/auth/tenant_boundary.py` | 提供 deny rules、human confirmation、redaction 和 source=agent durable mutation guard。 |
| Evidence | `apps/gateway/traces.py`, `apps/gateway/artifacts.py`, `apps/gateway/approvals.py` | 生成 trace refs、artifact refs、approval refs、incident timeline。 |

## 3. Target Interaction Flow

1. 用户在工作台发布含 Agent 节点的 WorkflowVersion。
2. Runtime 创建 WorkflowInstance 和 StationRun。
3. StationRun 进入 `queued`，executor 读取 AgentExecutionEnvelope。
4. Policy gate 校验 scope、tool policy、timeout、kill switch、approval requirement。
5. Executor 调用 allowlisted skill/tool/MCP 或 runtime adapter。
6. Executor 写入 redacted AgentExecutionResult、artifact refs、trace refs、quality refs。
7. 高风险 operation 进入 `waiting_approval`，只能由用户确认继续。
8. Evidence read model 汇总 station run、tool call、MCP call、artifact、trace、audit 和 denial evidence。

## 4. State Model

| State | Meaning | Required evidence |
| --- | --- | --- |
| queued | StationRun 已创建，等待 executor 接管。 | StationRun ref、AgentExecutionEnvelope ref。 |
| running | Executor 已开始执行。 | trace ref、policy decision ref、started_at。 |
| waiting_approval | 需要人工确认。 | approval ref、handoff reason、blocked operation。 |
| completed | Agent 节点完成。 | output artifact refs、execution result ref、quality refs。 |
| blocked | policy / redaction / scope 拒绝。 | denial reason、policy decision、incident timeline。 |
| cancelled | 用户或 kill switch 取消。 | cancel request ref、incident timeline。 |
| timeout | 超时终止。 | timeout policy ref、duration、incident timeline。 |

## 5. Architecture Red Lines

- Agent executor 不得直接改写 WorkflowTemplate / WorkflowVersion / Approval status。
- `source=agent` 不得执行 durable mutation；必须通过 handoff 或 human-confirmed operation。
- BFF 不得暴露 `/v1/rpc`、`/v1/internal/*`、raw connector payload 或 raw provider payload。
- Browser 不得构造 runtime status，只能展示 BFF DTO。
- 业务 Pack 不得新增 executor core 分支。

