# Workflow Platform Main Entry Implementation Task Matrix

用途：把后续开发任务拆成实现、验收和审计可执行矩阵。
边界：当前阶段只完成文档，不执行代码实现。

## 1. WP-M0 Documentation Tasks

| Task | Output | Acceptance |
| --- | --- | --- |
| WP-M0-D1 PRD | `workflow_platform_main_entry_prd.md` | PV13 首页基线、用户目标、能力分类、No-Go 明确。 |
| WP-M0-D2 Architecture | `workflow_platform_main_entry_target_architecture.md` | 具体代码实体和交互关系明确。 |
| WP-M0-D3 Plan | `workflow_platform_main_entry_development_and_acceptance_plan.md` | WP-M1 到 WP-M5A/WP-M5B 顺序明确。 |
| WP-M0-D3B BFF/DTO Contract | `workflow_platform_main_entry_bff_dto_contract.md` | route allowlist、DTO snapshot、browser denylist 明确。 |
| WP-M0-D3C Runner Spec | `workflow_platform_main_entry_acceptance_runner_spec.md` | 自动化验收输出、场景和 PASS/FAIL 规则明确。 |
| WP-M0-D4 Roadmap | `workflow_platform_main_entry_milestone_roadmap.md` | 里程碑和用户可见结果明确。 |
| WP-M0-D5 Gate | `workflow_platform_main_entry_acceptance_gate.md` | 验收门槛和出门条件明确。 |
| WP-M0-D6 Gap | `workflow_platform_main_entry_current_gap_analysis.md` | 当前差距、风险和文档支撑度明确。 |
| WP-M0-D7 Drawio | `workflow_platform_main_entry_gap_analysis.drawio` | 不超过 8 页、中文、实体明确、PV13 基线明确。 |
| WP-M0-D8 Audit | `workflow_platform_main_entry_document_support_audit.md` | 文档支撑结论和残余风险明确。 |
| WP-M0-D9 Readiness Audit | `workflow_platform_main_entry_implementation_readiness_audit.md` | 实现前 Go/No-Go 和 fallback routes 明确。 |

## 2. WP-M1 PV13 Baseline Homepage Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M1-I0 | `/bff/v13/*` compatibility route ownership is verified. | Main BFF route smoke PASS, or bounded smoke-server source explicitly recorded with no runtime/BFF production claim。 |
| WP-M1-I1 | Root route defaults to `V13EditableStudio`. | Route assertion and PV13 screenshot PASS。 |
| WP-M1-I2 | `?studio=workflow-platform` renders `V13EditableStudio`. | Route assertion and DOM testid `v13-editable-studio` PASS。 |
| WP-M1-I3 | `?studio=v13-editable-studio` remains accessible for evidence replay. | Backward compatibility smoke PASS。 |
| WP-M1-I4 | `WorkflowPlatformMainEntry` is not the default homepage baseline. | Source scan and route assertion PASS。 |
| WP-M1-I5 | Browser only calls BFF route allowlist. | Network denylist PASS。 |

## 3. WP-M2 PV13 Canvas Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M2-I1 | Wheel zoom and viewport constraints in PV13 canvas. | Zoom action log PASS。 |
| WP-M2-I2 | Pan and node drag across all visible canvas regions. | Drag screenshots PASS。 |
| WP-M2-I3 | Port-based edge creation and free connect. | Edge create E2E PASS。 |
| WP-M2-I4 | Cancel edge creation. | Cancel action PASS。 |
| WP-M2-I5 | Edge arrow visibility and first-eye layout. | Edge quality report PASS。 |
| WP-M2-I6 | Inspector follows selected PV13 node. | Inspector screenshot and DTO PASS。 |

## 4. WP-M3 Runtime/Evidence Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M3-I1 | WorkflowDiff review in PV13-based main entry. | Diff DTO and screenshot PASS。 |
| WP-M3-I2 | Publish/rollback/run history in PV13-based panel. | Version lifecycle report PASS。 |
| WP-M3-I3 | WorkflowInstance / StationRun readback. | Runtime inspect report PASS。 |
| WP-M3-I4 | Human gate transition. | Human action report PASS。 |
| WP-M3-I5 | Evidence panel aggregation. | Evidence classification report PASS。 |
| WP-M3-I6 | PV21 capability parity against `WorkflowPlatformMainEntry`. | `workflow-platform-capability-parity-report.json` proves graph save/readback, validation, diff, publish, rollback, run, inspect, human action and evidence review PASS。 |
| WP-M3-I7 | Document/knowledge summary scenario end to end. | User scenario report proves document input, graph operations, run output, citations/evidence refs and human review PASS。 |
| WP-M3-I8 | Code review/risk scenario end to end. | User scenario report proves repo/PR/diff input, scan/test/risk workflow, issue output, test output and human review PASS。 |
| WP-M3-I9 | Meeting/interview brief scenario end to end. | User scenario report proves transcript input, extraction/classification/task workflow, brief output, action items and human review PASS。 |

## 5. WP-M4 Executor Integration Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M4-I1 | Agent/Tool/Skill/MCP resource panel inside PV13-based workspace. | Resource panel screenshot PASS。 |
| WP-M4-I2 | Governed execution trigger with approval boundary. | Approval fixture PASS。 |
| WP-M4-I3 | Denial/timeout/cancel/retry readback. | Negative fixtures PASS。 |
| WP-M4-I4 | Copy guard for unrestricted automation claims. | No False Green PASS。 |
| WP-M4-I5 | PV20 executor capability parity against `WorkflowPlatformMainEntry`. | `workflow-platform-capability-parity-report.json` proves executor state, execution contract, execution evidence, skill action, tool action, MCP action and approval/denial refs PASS。 |
| WP-M4-I6 | Governed Agent/Tool/Skill/MCP evidence for document/knowledge summary. | Scenario executor integration report PASS。 |
| WP-M4-I7 | Governed Agent/Tool/Skill/MCP evidence for code review/risk workflow. | Scenario executor integration report PASS。 |
| WP-M4-I8 | Governed Agent/Tool/Skill/MCP evidence for meeting/interview brief workflow. | Scenario executor integration report PASS。 |

## 6. WP-M5A Closure / WP-M5B Remaining Tasks

WP-M5 is split after the WP-M5A bounded acceptance update:

- WP-M5A: business scenario productization and data-driven projection [PASS bounded review].
- WP-M5B: PV22 external app handoff readiness [remaining].

## 6.1 WP-M5A Business Scenario Productization Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M5A-I1 | Define and serve scenario projection DTO for document summary, code review and meeting brief. | PASS: `scenario-projection-report.json` proves scenario catalog, input contracts, node templates, Inspector/timeline and evidence categories are DTO/evidence-driven or explicitly fallback。 |
| WP-M5A-I2 | Generate document/knowledge summary output. | PASS: `business-output-report.json` includes summary artifact refs, citation refs, quality status and human review refs。 |
| WP-M5A-I3 | Generate code review/risk output. | PASS: `business-output-report.json` includes file/line findings, risk level, test/static scan refs and approval refs。 |
| WP-M5A-I4 | Generate meeting/interview brief output. | PASS: `business-output-report.json` includes brief, action items, decisions, open questions, citation refs and review refs。 |
| WP-M5A-I5 | Reduce or label frontend static scenario data. | PASS: `mock-reduction-report.json` lists remaining `scenarioData`, `fallbackGraph`, static chat/timeline/Inspector usages and marks them fallback/design reference。 |
| WP-M5A-I6 | Produce Chinese HTML productization acceptance report. | PASS: Report separates scenario path evidence from business output evidence and includes screenshots, DTO snapshots, artifact refs and No False Green scan。 |
| WP-M5A-I7 | Block PV22 if business productization fails. | PASS: WP-M5A passed; WP-M5B readiness refresh and PV22-S1..SA bounded implementation have since passed。 |

## 6.2 WP-M5B PV22 Handoff Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M5B-I1 | PV22 docs reference WP-M5A-reviewed PV13-based Workflow Platform as target host surface. | Document scan PASS。 |
| WP-M5B-I2 | SDK/template/reference app acceptance paths point to platform entry. | PV22 readiness update PASS。 |
| WP-M5B-I3 | External app contract does not bypass workflow platform governance or business scenario evidence boundaries. | Architecture review PASS。 |
