# PV20-S6 Browser Agent Executor Evidence Development Plan

用途：定义 PV20-S6 浏览器可见 Agent executor evidence path 的开发和验收步骤。
阅读对象：开发、测试、审计人员。
边界：S6 只证明浏览器能看到 PV20 executor contract/evidence 并触发受限执行动作；不证明完整工作台、完整审批 UI 或生产可用前端。

## Target Experience

用户打开 `?studio=pv20-agent-executor` 后，能看到 Agent executor 当前 state、contract、execution refs、allowed claim、not claimed 边界，并能通过按钮触发 allowlisted skill、read-only local tool、allowlisted MCP route。浏览器页面必须清楚展示失败信息，不把 MCP fixture 缺失伪造成成功。

## Implementation Scope

| Task | Code entity | Requirement |
| --- | --- | --- |
| S6-T1 | `apps/workflow-console/src/App.tsx` / `WorkflowStudioLayout.tsx` | Add `pv20-agent-executor` entry. |
| S6-T2 | `apps/workflow-console/src/api/types.ts` | Add minimal PV20 DTO types. |
| S6-T3 | `apps/workflow-console/src/api/workflowConsoleClient.ts` | Add PV20 BFF client methods. |
| S6-T4 | `apps/workflow-console/src/ui/pv20/PV20AgentExecutor.tsx` | Build browser evidence page with state/contract/evidence/action buttons. |
| S6-T5 | Frontend tests/build | Verify route registration and BFF-only client paths. |

## Acceptance Criteria

- Route `?studio=pv20-agent-executor` renders a non-empty PV20 evidence page.
- Browser client uses only `/bff/pv20/*` routes.
- Page shows allowed claim and not-claimed boundaries.
- Skill/tool/MCP buttons require BFF confirmation payloads.
- MCP failure is shown as failure when local fixture is unavailable.
- No claim says complete Agent executor, complete Workflow Studio, production ready or unrestricted MCP.

## Exit Condition

S6 exits when frontend tests/build pass and PV20 backend runner remains PASS. Browser screenshot automation can be added if a dev server is running; absence of screenshot evidence must not be treated as complete product-grade frontend.
