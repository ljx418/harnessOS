# PV20-S1 Agent Execution Contract Development Plan

用途：定义 PV20-S1 的开发步骤、验收标准和证据输出。
阅读对象：开发、测试、审计人员。
边界：S1 只证明 Agent executor contract/read model 可读，不证明 Agent executor 已完成或可执行工具链。

## 1. Scope

PV20-S1 的目标是建立受治理 Agent executor 的最小只读契约：

- `AgentExecutionEnvelopeDTO`：绑定 workflow_instance_id、station_run_id、agent_id、operation、context refs、policy refs、timeout、audit refs。
- `AgentExecutionResultDTO`：表达 S1 的 `contract_ready` / `not_executed` 状态，不伪造 tool、skill、MCP 执行结果。
- `/bff/pv20/*` route boundary：浏览器和测试只通过正式 BFF DTO 读取契约。

## 2. Development Tasks

| Task | Code entity | Output |
| --- | --- | --- |
| S1-T1 | `apps/api/routers/bff.py` | Add PV20 state/contract/evidence DTO helpers and routes. |
| S1-T2 | `tests/test_pv20_agent_execution_contract_bff.py` | Verify DTO shape, route boundary and no execution claim. |
| S1-T3 | `tools/pv20/run_agent_execution_contract_acceptance.py` | Generate S1 acceptance data, manifest, PRD review and no-false-green scan. |
| S1-T4 | `TASKS.md` | Mark PV20-R0 and PV20-S1 status after evidence passes. |

## 3. Acceptance Criteria

- BFF route returns `schema_version=pv20.agent_executor_contract.v1`.
- Envelope contains workflow, station, agent, operation, context, policy, timeout and audit refs.
- Result status is `contract_ready` and execution status is explicitly `not_executed_in_s1`.
- Evidence says S1 is not tool execution, not MCP execution, not Agent executor completion.
- No direct browser/internal route evidence is introduced.

## 4. Stop Conditions

- Implementation requires unrestricted shell/filesystem/network execution.
- Implementation adds direct `/v1/rpc` calls from browser.
- Implementation claims tool/MCP/skill execution before S2/S3.

