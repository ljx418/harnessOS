# Workflow Platform WP-M4 Executor Integration Plan And Audit

用途：定义 WP-M4 受治理 Agent/Tool/Skill/MCP 融合实现前计划、验收标准和审计结论。
边界：本文是子阶段计划和审计，不是实现证据。

## Development Plan

- The main entry must show Agent, Tool, Skill and MCP resources as governed capabilities.
- Executor evidence must reuse `/bff/pv20/*` state, contract, evidence and action routes.
- All three required business scenarios must show governed resource mapping.
- UI copy must not imply unrestricted automation or Agent executor readiness.

## Acceptance Criteria

- `agent-executor-integration-report.json` includes governed executor evidence for all three required business scenarios.
- At least one approval or denial boundary is recorded.
- Browser network log contains no direct runtime/store/tool/MCP calls outside BFF.
- No False Green scan passes.

## Audit Opinion

```text
wp_m4_readiness=GO
fatal_spec_drift=NONE
major_risk=NONE
implementation_may_start=true
```

