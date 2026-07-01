# Workflow Platform WP-M5A Business Scenario Productization Plan And Audit

用途：定义并记录 WP-M5A 业务场景产品化和数据驱动投影的开发计划、验收标准、实施结果和审计结论。
边界：本文记录的是有界实现和验收证据；不得据此声明完整 Workflow Studio、Agent executor ready、production ready、产品级前端完成或最终商业业务应用完成。

## Development Plan

- Keep `V13EditableStudio.tsx` as the PV13-based workflow platform homepage baseline.
- Add or compose a `WorkflowPlatformScenarioProjectionDTO` so the browser can render scenario catalog, input contracts, node templates, Inspector/timeline projection and evidence categories from BFF/DTO data.
- Add or compose a `WorkflowPlatformBusinessOutputDTO` so each required business scenario has a reviewable output summary, artifact refs, quality refs, audit refs, claim refs, redaction refs and human review refs.
- Productize the three required scenarios:
  - Document / knowledge summary: generate a summary output with citation/evidence refs and human review state.
  - Code review / change risk check: generate file/line findings, risk level, test/static scan refs and approval state.
  - Meeting / interview brief: generate brief, action items, decisions, open questions, citation refs and review state.
- Reduce frontend static business data usage. Any remaining `scenarioData`, `fallbackGraph`, static chat, static timeline or static Inspector values must be marked as fallback or design reference.
- Keep PV22 external app implementation gated by WP-M5A evidence. This gate is now satisfied by the PASS evidence recorded below; future regressions must re-check the same dependency before accepting PV22 follow-up work.

## Acceptance Criteria

- `scenario-projection-report.json` is PASS and proves scenario list, input requirements, node template, Inspector/timeline and evidence categories are DTO/evidence-driven or explicitly fallback.
- `business-output-report.json` is PASS and contains one output record for `document_summary`, `code_review` and `meeting_brief`.
- Each output record includes artifact refs, trace refs, quality refs, audit refs, claim refs, redaction refs and human review refs.
- `mock-reduction-report.json` is PASS and lists every remaining frontend static scenario source with its reason, boundary and removal condition.
- Browser network log contains only allowed BFF routes and does not call runtime/store internals directly.
- HTML acceptance report separates scenario path acceptance from business output evidence.
- PRD review, target architecture review, No False Green scan and redaction scan all pass.

## Implementation Result

WP-M5A 已按本计划完成有界实现：

- 主 BFF 新增 `/bff/workflow-platform/scenarios` 和 `/bff/workflow-platform/scenarios/{scenario_id}/outputs`。
- 前端 `V13EditableStudio.tsx` 通过 `workflowConsoleClient` 读取 scenario projection 和 business output DTO。
- 右侧 Inspector 增加业务输出摘要、artifact refs、human review refs、evidence categories 和 mock boundary。
- E2E smoke BFF 显式桥接 WP-M5A route，并复用主 BFF DTO builder，避免验收 fixture 与正式 DTO 语义分叉。
- `tests/test_v13_workflow_platform_bff.py` 覆盖主 BFF WP-M5A route、三业务场景、evidence refs 和 non-claim boundary。
- Chrome CDP E2E 生成 `06-wp-m5a-business-output.png`、`scenario-projection-report.json`、`business-output-report.json`、`mock-reduction-report.json`、`validation-command-log.json` 和 updated `artifact-manifest.json`。

证据目录：

```text
docs/design/V12-V15.x/evidence/workflow-platform-main-entry/
```

## Audit Opinion

```text
wp_m5a_readiness=PASS_FOR_BOUNDED_REVIEW
business_outputs_productized=BOUNDED_MACHINE_READABLE_SUMMARIES_PASS
scenario_projection_contract=IMPLEMENTED_AND_E2E_VALIDATED
mock_reduction_gate=PASS_WITH_REMAINING_FALLBACK_BOUNDARY
pv22_before_wp_m5a=NO_LONGER_BLOCKED_BY_WP_M5A
fatal_spec_drift=NONE
major_risk=FINAL_BUSINESS_DELIVERABLES_MISREAD_AS_COMPLETE
next_stage=PATH_D_PRODUCTION_GOVERNANCE_HARDENING_PLANNING_BY_DEFAULT
```

## Stop Conditions

- The implementation claims business output completion while only producing `user-scenario-report.json`, screenshots or acceptance report text.
- The browser uses local `scenarioData` / `fallbackGraph` as the accepted business output source without fallback labeling.
- Any required scenario lacks a business output record or human review ref.
- PV22 follow-up work proceeds without current WP-M5A PASS evidence or explicit user-approved deferral.
- UI, report or docs claim production ready, complete Workflow Studio GA, product-grade frontend complete, unrestricted automation, Agent executor ready or Xpert parity complete.

## Residual Boundaries

- WP-M5A 输出是机器可读业务输出摘要和证据引用，不是最终可交付的独立 Markdown 总结、PR 审查报告或会议纪要产品。
- `scenarioData`、`fallbackGraph` 和静态文案仍可作为视觉 fallback / design reference；不得作为 accepted business output source。
- PV22 implementation 仍必须经过 WP-M5B readiness refresh，不能直接把 WP-M5A 证据当外部 App 合同实现证据。
