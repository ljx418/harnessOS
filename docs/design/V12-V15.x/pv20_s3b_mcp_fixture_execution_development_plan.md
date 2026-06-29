# PV20-S3B MCP Fixture Execution Development Plan

用途：定义 PV20-S3B 真实本地 MCP fixture 执行的开发与验收步骤。
阅读对象：开发、测试、审计人员。
边界：S3B 只允许受治理的本地 stdio MCP fixture；不得开放任意 MCP、shell、外部网络、生产凭证或生产动作。

## Target Experience

用户在 Agent executor panel 中确认执行一个 allowlisted MCP 节点后，系统必须通过 Gateway connector runtime 触发真实 `connector.submit`，如果 connector 要求审批，则必须生成 approval、调用 `approval.respond`，再用 retry context 完成 MCP stdio 调用。执行结果必须回写 StationRun metadata，并在 PV20 contract/evidence read model 中显示 `mcp_call_refs`、artifact refs、approval refs 和 redacted status。

## Implementation Scope

| Task | Code entity | Requirement |
| --- | --- | --- |
| S3B-T1 | `core/agent_executor/runtime.py` | Add allowlisted MCP execution evidence builder; only allow `data_service_mcp.knowledge_query_v2`. |
| S3B-T2 | `apps/api/routers/bff.py` | Add `/bff/pv20/runs/{run_id}/agent-mcp-executions`; require user confirmation and route through Gateway RPC only. |
| S3B-T3 | `tests/test_pv20_agent_execution_contract_bff.py` | Create local stdio MCP fixture, configure `data_service_mcp`, and verify approval + execution + readback. |
| S3B-T4 | `tools/pv20/run_agent_execution_contract_acceptance.py` | Extend acceptance evidence to S3B and keep no-false-green scan for unrestricted MCP. |
| S3B-T5 | Docs / TASKS | Mark S3B complete only after automated evidence passes. |

## Acceptance Criteria

- `agent-mcp-executions` rejects missing user confirmation.
- Execution uses `connector.submit`; direct connector/runtime internals are not exposed through browser routes.
- Connector approval is created and approved through `approval.respond`.
- MCP result produces non-empty `mcp_call_refs` and artifact refs.
- Contract readback preserves skill, local tool and MCP refs separately.
- Unknown MCP connector/tool is denied.
- Evidence may claim only allowlisted local MCP fixture execution, not unrestricted MCP or production readiness.

## Exit Condition

S3B exits only when backend tests and PV20 acceptance runner pass with a real local stdio MCP fixture. If fixture execution fails or becomes a mock-only result, S3B must be marked blocked/pending.
