# PV20 Complete Agent Executor Implementation Task Matrix

用途：把 PV20 任务拆到明确代码实体、验收证据和风险控制。
阅读对象：开发、测试、审计人员。
边界：本文不是实现证据；任务完成必须以代码和验收报告为准。

| Task | Code entities | Done means | Evidence |
| --- | --- | --- | --- |
| PV20-T1 AgentExecutionEnvelope | `core/agent_executor/*`, `core/station_agents/contracts.py` | envelope schema covers scope, station, operation, refs and policies. | DTO snapshot. |
| PV20-T2 Executor service | new executor service, `apps/gateway/service.py` | executor receives station run, applies policy and writes result. | backend execution report. |
| PV20-T3 Skill adapter | `core/skills/registry.py`, executor adapter | allowlisted skill/read-model node executes and records refs. | skill execution report. |
| PV20-T4 Tool/MCP adapter | `apps/gateway/connector_execution.py`, executor adapter | allowlisted MCP/tool node executes through governed connector boundary. | MCP/tool report. |
| PV20-T5 Policy gate | `core/policies/*`, `core/auth/tenant_boundary.py` | denied operations return stable denial evidence. | negative fixture report. |
| PV20-T6 Human gate | `apps/gateway/approvals.py`, BFF route | high-risk action pauses and resumes only after user confirmation. | approval-handoff report. |
| PV20-T7 Timeout/cancel/retry | executor runtime, StationRun attempt state | timeout/cancel/retry mutate backend state and preserve evidence. | lifecycle report. |
| PV20-T8 Evidence read model | `apps/api/routers/bff.py`, evidence helper | evidence panel summarizes refs without raw payload. | evidence summary and redaction scan. |
| PV20-T9 Browser path | workflow console PV20 UI | user can run and inspect Agent execution path. | screenshots and network log. |
| PV20-T10 Acceptance runner | `tools/pv20/*`, tests | aggregate runner validates artifacts and no false green. | acceptance-data and artifact-manifest. |

## Coding Red Lines

- Do not add direct browser calls to `/v1/rpc`, `/v1/internal/*` or executor internals.
- Do not use business-specific branches inside executor core.
- Do not write raw secrets, raw prompt text or provider payload into DTO/evidence.
- Do not remove existing V9/PV16 no-executor-ready guards until PV20 evidence passes.

