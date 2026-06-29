# PV20-S4 Approval Handoff Development Plan

用途：定义 PV20-S4 approval handoff 与 denied mutation fixtures 的开发及验收步骤。
阅读对象：开发、测试、审计人员。
边界：S4 不开放任意审批动作；只证明 Agent executor 触发高风险 connector 时必须经过用户确认和 Gateway approval 轨道。

## Target Experience

用户确认执行 allowlisted MCP 节点后，系统生成 connector approval，经 `approval.respond` 决策，再用 retry context 完成执行。审计者能在 Agent execution contract/evidence 中看到 approval refs。缺少用户确认、`source=agent` 或未知 MCP/tool 都必须被拒绝，并生成可读失败响应。

## Implementation Scope

| Task | Code entity | Requirement |
| --- | --- | --- |
| S4-T1 | `apps/api/routers/bff.py` | Surface `approval_refs` in PV20 contract/evidence read model. |
| S4-T2 | `tests/test_pv20_agent_execution_contract_bff.py` | Add denied fixtures for missing confirmation, `source=agent`, unknown MCP/tool and approval readback. |
| S4-T3 | `tools/pv20/run_agent_execution_contract_acceptance.py` | Add S4 acceptance checks and no-false-green scan entries. |
| S4-T4 | Docs / TASKS | Mark S4 complete only after backend runner passes. |

## Acceptance Criteria

- `source=agent` cannot trigger skill/tool/MCP execution.
- Missing `user_confirmed=true` cannot trigger skill/tool/MCP execution.
- Unknown MCP connector/tool is denied before connector execution.
- Allowlisted MCP execution produces non-empty `approval_refs`.
- Contract/evidence readback records approval handoff without claiming unrestricted agent approval authority.
- Agent operation envelope still forbids direct `approval.respond`.

## Exit Condition

S4 exits when tests and PV20 runner pass with denial fixtures and approval refs. It does not prove complete human approval UI; browser-visible UX remains PV20-S6.
