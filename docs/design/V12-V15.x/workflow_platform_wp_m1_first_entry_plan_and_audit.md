# Workflow Platform WP-M1 First Entry Plan And Audit

用途：定义 WP-M1 首入口实现前计划、验收标准和审计结论。
边界：本文是子阶段计划和审计，不是实现证据。

## Development Plan

- Default `/` must render the Workflow Platform main entry.
- Historical stage routes such as `?studio=pv21-complete-workflow-studio`, `?studio=pv20-agent-executor` and `?studio=pv19-runtime-workflow-platform` must remain available for evidence replay.
- The first screen must show workspace, project, workflow, graph, run and evidence state from BFF DTOs.
- Browser calls must stay inside the documented BFF allowlist.

## Acceptance Criteria

- `workflow-platform-main-entry` is visible on `/` without manual query parameters.
- Route assertion records default entry as `workflow-platform`.
- Browser network log contains allowed `/bff/pv21/*` and `/bff/pv20/*` calls only.
- Chinese HTML acceptance report includes first-screen screenshot and PRD review.
- No False Green scan rejects GA, production, unrestricted execution, product-completeness and external-parity claims.

## Audit Opinion

```text
wp_m1_readiness=GO
fatal_spec_drift=NONE
major_risk=NONE
implementation_may_start=true
```
