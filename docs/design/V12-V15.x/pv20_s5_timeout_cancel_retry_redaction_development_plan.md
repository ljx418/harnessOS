# PV20-S5 Timeout / Cancel / Retry / Redaction Development Plan

用途：定义 PV20-S5 timeout、cancel、retry、redaction fixtures 的开发和验收步骤。
阅读对象：开发、测试、审计人员。
边界：S5 只证明 bounded executor failure-control evidence，不证明生产级调度器、分布式取消或完整 SLA。

## Target Experience

审计者可以看到 Agent executor 对异常执行具备受治理边界：未知 skill/tool/MCP 会被拒绝；MCP approval retry context 被使用；connector failure/timeout-like error 不会被误报成功；cancel fixture 能通过 Gateway job cancel 形成可读状态；所有 executor DTO 和 evidence 不包含 raw prompt、secret、authorization 或 raw connector payload。

## Implementation Scope

| Task | Code entity | Requirement |
| --- | --- | --- |
| S5-T1 | `core/agent_executor/runtime.py` | Keep raw/sensitive payload guard; add stable control evidence shape if needed. |
| S5-T2 | `apps/api/routers/bff.py` | Preserve denial/failure evidence in PV20 read model without exposing raw payloads. |
| S5-T3 | `tests/test_pv20_agent_execution_contract_bff.py` | Add redaction, retry-context and negative control assertions. |
| S5-T4 | `tools/pv20/run_agent_execution_contract_acceptance.py` | Add acceptance checks for retry context, cancel/timeout-like control evidence and no raw terms. |
| S5-T5 | Docs / TASKS | Mark S5 complete only after runner PASS. |

## Acceptance Criteria

- Unknown skill, local tool and MCP are denied with stable error codes.
- MCP execution uses approval retry context before completion.
- Cancel fixture records a cancelled connector job state or an explicit bounded cancel evidence entry.
- Timeout/failure fixture records failed connector evidence or explicit bounded timeout evidence, not PASS.
- Redaction scan finds no raw prompt, raw secret, authorization, raw provider payload or raw connector payload in PV20 DTO snapshots.
- No claim says production SLA, unrestricted automation or full scheduler ready.

## Exit Condition

S5 exits when backend tests and PV20 runner pass with control evidence. If real timeout/cancel cannot be proven without long-running unsafe subprocesses, S5 must explicitly mark those as bounded fixtures and leave production-grade timeout/cancel for Path D.
