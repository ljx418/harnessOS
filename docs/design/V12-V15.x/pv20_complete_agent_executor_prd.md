# PV20 Complete Agent Executor PRD

用途：定义 PV20 “Complete Agent Executor” 的产品目标、用户体验、边界和验收口径。
阅读对象：产品、架构、开发、测试、审计人员。
边界：本文是下一子阶段开发规格，不是实现证据；不得据此声明生产可用、无限制自动化、完整 Workflow Studio 或商业化完成。

## 1. Product Goal

PV20 的目标不是让 Agent 获得不受限的系统执行权，而是补齐一个可复用、可审计、可取消、可超时、可回放的受治理 Agent executor 候选能力。

本阶段完成后，用户应能在 PV19 工作流平台上看到一个含 Agent 节点的工作流被真实执行：Agent 节点按 station/node contract 获取 redacted context，调用 allowlist tool / skill / MCP 能力，产出 artifact / trace / quality / audit evidence，并在需要人工确认或高风险操作时停在 human gate。

允许出门声明：

```text
PV20 complete: governed Agent executor candidate ready for bounded review.
```

该声明仍不等于 production ready、unrestricted automation ready、complete Workflow Studio ready、Xpert parity complete 或 commercial agent platform ready。

## 2. Target Users And Jobs

| User | Job | PV20 target experience |
| --- | --- | --- |
| Workflow builder | 在工作流中配置 Agent 节点。 | Agent 节点显示 role、goal、tool policy、skill binding、MCP binding、timeout 和 approval policy。 |
| Operator | 启动含 Agent 节点的 workflow。 | Agent 节点真实进入 queued/running/completed/blocked/cancelled/timeout 状态。 |
| Human reviewer | 审查 Agent 建议和高风险动作。 | 高风险动作只生成 handoff / approval，不自动执行 durable mutation。 |
| Auditor | 验证执行器是否通用且受治理。 | 可看到 execution envelope、policy decision、tool/skill/MCP call refs、redaction、incident timeline。 |

## 3. Functional Requirements

| ID | Requirement | Acceptance signal |
| --- | --- | --- |
| PV20-F1 | 定义通用 AgentExecutionEnvelope。 | envelope 包含 workflow_instance_id、station_run_id、agent_id、operation、context_refs、tool_policy_ref、timeout_policy_ref、audit_ref。 |
| PV20-F2 | Executor 只能从 WorkflowInstance / StationRun 调用。 | 无独立绕过 runtime 的执行入口；BFF 只读 inspect/evidence 或用户确认入口。 |
| PV20-F3 | 支持至少两个非同构执行节点。 | 一个 skill/read-model 节点和一个 MCP/tool 节点均产生真实 execution evidence。 |
| PV20-F4 | 支持 allowlist tool / skill / MCP 调用。 | 未授权 tool、未知 skill、越权 MCP 调用被拒绝并生成 denial evidence。 |
| PV20-F5 | 支持 timeout、cancel、retry。 | 超时转 timeout/failed，cancel 转 cancelled，retry 生成新 attempt 并保留前序 evidence。 |
| PV20-F6 | 支持 approval/handoff。 | 高风险 operation 只生成待确认状态，用户确认后才继续。 |
| PV20-F7 | 支持 artifact、trace、quality、audit refs。 | evidence summary 不允许前端伪造 runtime truth。 |
| PV20-F8 | 支持 redaction 和 secret boundary。 | 原始 prompt、原始凭证、原始 provider payload 不进入 DTO 或报告。 |

## 4. Non-Goals

- 不做生产级多租户、SLA、计费或外部商业发布。
- 不允许 Agent 自动发布 workflow、自动审批、自动 git push、自动生产部署。
- 不把 PV20 说成完整 Workflow Studio。
- 不为某个业务 Pack 定制 executor core。
- 不把历史 V9 safety gate 的 policy decision 当作 PV20 runtime execution evidence。

## 5. Stage Boundary

PV20 必须复用并加强当前平台边界：

- `core/workflows/store.py` 继续作为 WorkflowVersion / WorkflowInstance / StationRun truth。
- `apps/gateway/service.py` 继续作为 Gateway facade。
- `apps/gateway/approvals.py`、`apps/gateway/traces.py`、`apps/gateway/artifacts.py` 继续作为 approval / trace / artifact 证据来源。
- `core/station_agents/contracts.py` 可作为 Agent descriptor / redacted context / capability decision 的基础。
- `core/runtime_adapter/adapters.py` 可作为受治理 runtime invocation 的 adapter boundary。
- `core/policies/v9_agent_executor_safety.py` 和 `core/policies/v9_controlled_executor_runtime.py` 只能作为 safety / evidence 参考，不能原样冒充 PV20 完成态。

