# PV20 Complete Agent Executor Implementation Readiness Audit

用途：在 PV20 实质开发前审计规格、架构、风险和验收是否足够支撑自动化开发。
阅读对象：开发、测试、审计人员。
边界：本文是开工审计，不是实现证据。

## 1. Audit Conclusion

当前结论：**CONDITIONALLY READY FOR PV20-S1 IMPLEMENTATION**。

条件是 PV20 必须采用受治理 executor candidate 路线，而不是 unrestricted automation 路线。实现前不得放宽 source=agent durable mutation guard，不得引入无边界 shell/filesystem/network 执行。

## 2. Document Coverage

| Area | Status | Notes |
| --- | --- | --- |
| PRD | PASS | `pv20_complete_agent_executor_prd.md` 明确目标体验和 No-Go。 |
| Architecture | PASS | `pv20_complete_agent_executor_target_architecture.md` 锁定具体代码实体。 |
| Plan | PASS | `pv20_complete_agent_executor_development_and_acceptance_plan.md` 拆分 R0-S6-SA。 |
| Acceptance gate | PASS | `pv20_complete_agent_executor_acceptance_gate.md` 定义出门条件和 stop conditions。 |
| Task matrix | PASS | `pv20_complete_agent_executor_implementation_task_matrix.md` 将任务映射到代码实体。 |
| Evidence path | PASS | 证据目录规划为 `docs/design/V12-V15.x/evidence/pv20-complete-agent-executor/`。 |

## 3. Risk Review

| Risk | Severity | Control |
| --- | --- | --- |
| Agent 获得 durable mutation 权限 | Critical | 保留 source=agent durable mutation denial；高风险动作只 handoff。 |
| 执行器被业务 Pack 定制污染 | Major | Executor core 只识别 generic AgentExecutionEnvelope。 |
| 浏览器绕过 BFF 调 runtime | Major | route boundary log 和 browser network denylist。 |
| 原始 prompt/secret 泄露 | Major | redaction scan、DTO denylist、artifact refs only。 |
| MCP/tool 调用越权 | Major | allowlist policy、scope check、negative fixtures。 |
| Timeout/cancel/retry 仅 UI 模拟 | Major | 必须写入 backend StationRun/attempt evidence。 |

## 4. Architecture Fit

PV20 可以基于当前代码继续推进：

- `WorkflowRepository` / `InMemoryWorkflowStore` 已支持 WorkflowInstance、StationRun、QualityEvaluation 和 WorkflowContext。
- `GatewayService` 已聚合 approval、trace、artifact 和 connector runtime。
- `station_agents/contracts.py` 已有 Agent descriptor、context envelope、capability decision 和 redaction helpers。
- `runtime_adapter/adapters.py` 已有 governance metadata injection boundary。
- 历史 V9 safety/runtime 代码可作为 policy/evidence 参考，但不能直接冒充 PV20 完成态。

## 5. Start Decision

可以进入 PV20-S1，但 S1 只能实现 AgentExecutionEnvelope / BFF read model / route boundary，不应直接实现 unrestricted executor。若 S1 发现必须放宽 red line，应立即停止并重新评估路线。

