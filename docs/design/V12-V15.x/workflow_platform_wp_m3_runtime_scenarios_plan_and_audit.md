# Workflow Platform WP-M3 Runtime Scenarios Plan And Audit

用途：定义 WP-M3 运行闭环和三个必验业务场景实现前计划、验收标准和审计结论。
边界：本文是子阶段计划和审计，不是实现证据。

## Development Plan

- The main entry must support save, validate, WorkflowDiff, publish, run, Human Gate and Evidence Review in one product surface.
- The acceptance runner must execute the minimum Agent workflow and all three required business scenarios:
  - Document / knowledge summary.
  - Code review / change risk check.
  - Meeting / interview brief.
- Scenario inputs must come from real local repository data, not placeholder-only mock strings.
- Each scenario must carry its scenario id, input refs and goal into the run input payload.

## Acceptance Criteria

- `user-scenario-report.json` contains PASS records for the minimum Agent workflow and all three business scenarios.
- Each scenario includes user input snapshot, platform action sequence, WorkflowDiff, publish, run, Human Gate, evidence refs and output summary.
- `runtime-inspect-report.json` proves WorkflowVersion, WorkflowInstance and StationRun readback.
- `evidence-panel-report.json` proves artifact, trace, quality, audit, claim and redaction categories.

## Audit Opinion

```text
wp_m3_readiness=GO
three_required_business_scenarios=MANDATORY
fatal_spec_drift=NONE
major_risk=NONE
implementation_may_start=true
```

