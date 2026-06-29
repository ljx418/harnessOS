# PV20 Complete Agent Executor Acceptance Gate

用途：定义 PV20 出门门槛、阻断项和允许声明。
阅读对象：开发、测试、审计人员。
边界：本文定义 gate，不是实现证据。

## 1. Gate Matrix

| Gate | Requirement | Exit condition |
| --- | --- | --- |
| G1 文档完整 | PRD、架构、计划、任务矩阵、readiness audit 存在。 | PASS before coding。 |
| G2 Contract | AgentExecutionEnvelope 和 AgentExecutionResult DTO 稳定。 | schema / snapshot PASS。 |
| G3 Runtime truth | Executor 从 WorkflowInstance / StationRun 驱动。 | backend report PASS。 |
| G4 Skill node | allowlisted skill/read-model 节点真实执行。 | execution report PASS。 |
| G5 Tool/MCP node | allowlisted MCP/tool 节点真实执行。 | call refs and denial fixtures PASS。 |
| G6 Human gate | 高风险动作等待人工确认。 | waiting_approval -> completed/blocked transition PASS。 |
| G7 Timeout/cancel/retry | 三类控制面动作均有状态证据。 | timeout/cancel/retry report PASS。 |
| G8 Evidence | artifact、trace、quality、policy、approval、incident refs 完整。 | evidence summary PASS。 |
| G9 Browser E2E | 人类可见路径可走通。 | screenshots and network log PASS。 |
| G10 No False Green | 禁止声明没有证据的能力。 | scan PASS。 |

## 2. Allowed Exit Claim

```text
PV20 complete: governed Agent executor candidate ready for bounded review.
```

## 3. Forbidden Claims

- HarnessOS production ready.
- unrestricted automation ready.
- complete Workflow Studio ready.
- Xpert parity complete.
- commercial agent platform ready.
- Agent can autonomously publish, approve, push, deploy or mutate durable workflow truth without human-confirmed governance.

## 4. Stop Conditions

出现以下任一情况必须打回计划阶段或找用户确认：

- 需要打开 unrestricted shell、unrestricted filesystem 或 unrestricted network 才能完成验收。
- 需要真实生产凭证或外部付费 API 才能通过默认验收。
- 执行器实现必须修改 workflow core 为某个业务 Pack 特例。
- 无法证明 Agent output 与 artifact / trace / audit refs 的对应关系。

