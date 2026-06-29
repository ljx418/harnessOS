# Workflow Platform Main Entry Implementation Task Matrix

用途：把后续开发任务拆成实现、验收和审计可执行矩阵。
边界：当前阶段只完成文档，不执行代码实现。

## 1. WP-M0 Documentation Tasks

| Task | Output | Acceptance |
| --- | --- | --- |
| WP-M0-D1 PRD | `workflow_platform_main_entry_prd.md` | 用户目标、能力分类、No-Go 明确。 |
| WP-M0-D2 Architecture | `workflow_platform_main_entry_target_architecture.md` | 具体代码实体和交互关系明确。 |
| WP-M0-D3 Plan | `workflow_platform_main_entry_development_and_acceptance_plan.md` | WP-M1 到 WP-M5 顺序明确。 |
| WP-M0-D3B BFF/DTO Contract | `workflow_platform_main_entry_bff_dto_contract.md` | route allowlist、DTO snapshot、browser denylist 明确。 |
| WP-M0-D3C Runner Spec | `workflow_platform_main_entry_acceptance_runner_spec.md` | 自动化验收输出、场景和 PASS/FAIL 规则明确。 |
| WP-M0-D4 Roadmap | `workflow_platform_main_entry_milestone_roadmap.md` | 里程碑和用户可见结果明确。 |
| WP-M0-D5 Gate | `workflow_platform_main_entry_acceptance_gate.md` | 验收门槛和出门条件明确。 |
| WP-M0-D6 Gap | `workflow_platform_main_entry_current_gap_analysis.md` | 当前差距、风险和文档支撑度明确。 |
| WP-M0-D7 Drawio | `workflow_platform_main_entry_gap_analysis.drawio` | 不超过 8 页、中文、实体明确。 |
| WP-M0-D8 Audit | `workflow_platform_main_entry_document_support_audit.md` | 文档支撑结论和残余风险明确。 |
| WP-M0-D9 Readiness Audit | `workflow_platform_main_entry_implementation_readiness_audit.md` | 实现前 Go/No-Go 和 fallback routes 明确。 |

## 2. WP-M1 First Entry Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M1-I1 | Root route defaults to Workflow Platform main entry. | Route assertion and screenshot PASS。 |
| WP-M1-I2 | Stage query pages remain accessible for evidence replay. | Backward compatibility smoke PASS。 |
| WP-M1-I3 | First-screen state shows workspace/project/workflow/run/evidence summary. | Text assertion and screenshot PASS。 |
| WP-M1-I4 | Browser only calls BFF route allowlist. | Network denylist PASS。 |

## 3. WP-M2 Canvas Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M2-I1 | Wheel zoom and viewport constraints. | Zoom action log PASS。 |
| WP-M2-I2 | Pan and node drag across all visible canvas regions. | Drag screenshots PASS。 |
| WP-M2-I3 | Port-based edge creation and free connect. | Edge create E2E PASS。 |
| WP-M2-I4 | Cancel edge creation. | Cancel action PASS。 |
| WP-M2-I5 | Edge arrow visibility and first-eye layout. | Edge quality report PASS。 |

## 4. WP-M3 Runtime/Evidence Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M3-I1 | WorkflowDiff review in main entry. | Diff DTO and screenshot PASS。 |
| WP-M3-I2 | Publish/rollback/run history in one panel. | Version lifecycle report PASS。 |
| WP-M3-I3 | WorkflowInstance / StationRun readback. | Runtime inspect report PASS。 |
| WP-M3-I4 | Human gate transition. | Human action report PASS。 |
| WP-M3-I5 | Evidence panel aggregation. | Evidence classification report PASS。 |
| WP-M3-I6 | Document/knowledge summary scenario end to end. | User scenario report proves document input, graph operations, run output, citations/evidence refs and human review PASS。 |
| WP-M3-I7 | Code review/risk scenario end to end. | User scenario report proves repo/PR/diff input, scan/test/risk workflow, issue output, test output and human review PASS。 |
| WP-M3-I8 | Meeting/interview brief scenario end to end. | User scenario report proves transcript input, extraction/classification/task workflow, brief output, action items and human review PASS。 |

## 5. WP-M4 Executor Integration Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M4-I1 | Agent/Tool/Skill/MCP resource panel. | Resource panel screenshot PASS。 |
| WP-M4-I2 | Governed execution trigger with approval boundary. | Approval fixture PASS。 |
| WP-M4-I3 | Denial/timeout/cancel/retry readback. | Negative fixtures PASS。 |
| WP-M4-I4 | Copy guard for unrestricted automation claims. | No False Green PASS。 |
| WP-M4-I5 | Governed Agent/Tool/Skill/MCP evidence for document/knowledge summary. | Scenario executor integration report PASS。 |
| WP-M4-I6 | Governed Agent/Tool/Skill/MCP evidence for code review/risk workflow. | Scenario executor integration report PASS。 |
| WP-M4-I7 | Governed Agent/Tool/Skill/MCP evidence for meeting/interview brief workflow. | Scenario executor integration report PASS。 |

## 6. WP-M5 PV22 Handoff Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M5-I1 | PV22 docs reference Workflow Platform as target host surface. | Document scan PASS。 |
| WP-M5-I2 | SDK/template/reference app acceptance paths point to platform entry. | PV22 readiness update PASS。 |
| WP-M5-I3 | External app contract does not bypass workflow platform governance. | Architecture review PASS。 |
