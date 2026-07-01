# Workflow Platform Main Entry Document Support Audit

用途：评估 WP-M0 文档是否足以支撑后续 PV13-based 工作流平台首页开发和验收。
边界：本文是文档审计，不是实现证据。

## 1. Document Set

| Document | Role | Status |
| --- | --- | --- |
| `workflow_platform_main_entry_prd.md` | 产品目标、PV13 首页基线、用户体验、能力分类和 No-Go。 | Ready |
| `workflow_platform_main_entry_target_architecture.md` | 目标架构、代码实体、分层和风险。 | Ready |
| `workflow_platform_main_entry_development_and_acceptance_plan.md` | WP-M0 到 WP-M5A/WP-M5B 开发与验收计划。 | Ready |
| `workflow_platform_main_entry_bff_dto_contract.md` | BFF route allowlist、DTO snapshot、browser denylist 和兼容策略。 | Ready |
| `workflow_platform_main_entry_acceptance_runner_spec.md` | 自动化验收 runner 输出、场景和 PASS/FAIL 规则。 | Ready |
| `workflow_platform_main_entry_milestone_roadmap.md` | 里程碑和用户可见结果。 | Ready |
| `workflow_platform_main_entry_acceptance_gate.md` | 出门门槛、禁止声明和 PASS/FAIL 条件。 | Ready |
| `workflow_platform_main_entry_current_gap_analysis.md` | 当前差距和风险。 | Ready |
| `workflow_platform_main_entry_implementation_task_matrix.md` | 后续实现任务矩阵。 | Ready |
| `workflow_platform_main_entry_implementation_readiness_audit.md` | 实现前审计、残余风险和 fallback routes。 | Ready |
| `workflow_platform_wp_m5a_business_scenario_productization_plan_and_audit.md` | WP-M5A 子阶段开发计划、验收标准和审计意见。 | Ready |
| `workflow_platform_main_entry_gap_analysis.drawio` | 人类可读 gap、架构、计划和验收图。 | Ready |

## 2. Coverage

| Coverage area | Result |
| --- | --- |
| Product goal | Covered: PV13 Light Studio 是工作流平台首页和前端基线。 |
| User experience | Covered: 首屏、力感画布、场景、Inspector、仿真控制、证据、Agent/Tool/Skill/MCP 资源。 |
| Architecture | Covered: `App.tsx`、`WorkflowStudioLayout.tsx`、`V13EditableStudio.tsx`、`v13-editable-studio.css`、`WorkflowPlatformMainEntry.tsx`、BFF、WorkflowStore、Gateway、evidence。 |
| BFF / DTO contract | Covered: allowed route families, DTO shape, browser denylist, compatibility rules, and WP-M1A `/bff/v13/*` route ownership verification。 |
| Development plan | Covered: WP-M1A V13 BFF compatibility, WP-M1B PV13 homepage、WP-M2 canvas、WP-M3 runtime/evidence、WP-M4 executor、WP-M5A business scenario productization、WP-M5B PV22 handoff。 |
| Capability non-regression | Covered: `WorkflowPlatformMainEntry` is the PV21/PV20 capability parity source; WP-M3/WP-M4 must output `workflow-platform-capability-parity-report.json`。 |
| Acceptance | Covered: browser action log、network log、DTO snapshot、runtime inspect、edge quality、evidence panel、acceptance report、No False Green。 |
| Runner output | Covered: acceptance-data、artifact manifest、HTML report、redaction scan、NO_GO rules。 |
| User application scenarios | Covered: minimum Agent workflow, three required business scenarios and optional/future boundaries。 |
| Business output productization | Covered: WP-M5A requires scenario projection DTO, business output DTO, independent business artifacts and mock reduction evidence before PV22 handoff。 |
| Claim safety | Covered: forbidden claims and allowed bounded documentation claim。 |

## 3. Audit Findings

| Finding | Severity | Closure |
| --- | --- | --- |
| Prior plan still treated PV21 shell / `WorkflowPlatformMainEntry` as plausible homepage baseline. | Fatal | Closed by explicitly making `V13EditableStudio` the homepage frontend baseline。 |
| Current degraded workflow-platform entry regressed from user-confirmed PV13 experience. | Major | Closed by marking it as replace/deprecate path。 |
| PV22 had been the current default next implementation step, but user feedback requires workflow platform first-entry alignment first. | Major | Closed by WP-M0 route insertion and source-of-truth update requirement。 |
| PV21 wording can be mistaken for complete Workflow Studio GA. | Major | Closed by repeated bounded candidate wording and forbidden claim gate。 |
| Canvas feedback needs action-level acceptance rather than generic polish wording. | Major | Closed by WP-M2 canvas gate and task matrix。 |
| External app contract needs a stable host surface before implementation. | Medium | Closed by WP-M5 handoff requirement。 |
| Automated implementation lacked exact contract/runner output shape. | Major | Closed by BFF/DTO contract and acceptance runner spec。 |
| Business scenario exit criteria were too weak under the previous single-scenario wording. | Major | Closed by requiring document/knowledge summary, code review/risk and meeting/interview scenarios to all pass before WP-M3/WP-M4 exit。 |
| Three business scenarios could be misread as completed business products even though current evidence only proves scenario path acceptance. | Major | Closed by adding WP-M5A business output and mock reduction gates。 |
| Frontend local `scenarioData` / `fallbackGraph` could be mistaken for backend business projection. | Major | Closed by requiring scenario projection DTO and mock reduction report。 |
| `/bff/v13/*` route source was implicit because historical V13 evidence used the e2e smoke server while the main API router scan did not show formal `/v13` decorators. | Major | Closed by adding WP-M1A route ownership verification and smoke-server-only evidence labeling。 |
| Direct PV13 homepage replacement could silently drop `WorkflowPlatformMainEntry` PV21/PV20 closed-loop capabilities. | Major | Closed by adding capability parity requirements, runner output and WP-M3/WP-M4 FAIL rules。 |

## 4. Residual Risks

- 后续实现仍需真实浏览器 E2E、BFF route log、DTO snapshot 和截图证据。
- 文档不能证明当前首页已经替换为 PV13。
- 文档不能证明当前界面已经达到 MVP。
- 文档和 WP-M5A 证据只能证明 bounded business output summaries；不能证明最终商业业务应用完成。
- 文档不能证明 PV22 external app contract implementation complete。
- 文档不能证明生产治理、商业化或开放生态 readiness。

## 5. Conclusion

```text
document_support_for_wp_m1a_v13_bff_compatibility=GO
document_support_for_wp_m1b_pv13_baseline_homepage=GO_AFTER_WP_M1A
document_support_for_wp_m2_wp_m4_detailed_planning=GO
document_support_for_wp_m5a_business_scenario_productization_planning=GO
document_support_for_wp_m5b_pv22_handoff_after_wp_m5a=GO_WITH_ORDERING_GUARD
document_support_for_workflow_platform_capability_non_regression=GO
document_support_for_three_required_business_scenarios=GO
document_support_for_three_business_output_summaries=PASS_WITH_WP_M5A_EVIDENCE
document_support_for_code_implementation_without_substage_acceptance=NO_GO
document_support_for_complete_workflow_platform_claim=NO_GO
document_support_for_production_ready_claim=NO_GO
```

WP-M0 文档已支撑 WP-M1A 到 WP-M5A 的自动化开发和 bounded acceptance。WP-M3/WP-M4 已覆盖基础 Agent 工作流，证明相对 `WorkflowPlatformMainEntry` 的 PV21/PV20 能力不退化，并跑通文档/知识总结、代码审查/变更风险检查、会议/访谈整理三个必验业务场景。WP-M5A 已进一步生成业务输出摘要、artifact refs、human review refs、scenario projection report、business output report 和 mock reduction report。WP-M5B/PV22 readiness refresh 与 PV22-S1..SA bounded implementation 已完成。后续每个新阶段仍必须独立完成 PRD 检视、目标架构检视、端到端验收和 No False Green 审计；下一默认方向应是 Path D / production governance hardening planning，除非用户选择业务 Pack 产品化或开源/商业化准备阶段。
