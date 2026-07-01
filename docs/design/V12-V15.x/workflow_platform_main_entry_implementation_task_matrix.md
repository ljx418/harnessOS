# Workflow Platform Main Entry Implementation Task Matrix

用途：把后续开发任务拆成实现、验收和审计可执行矩阵。
边界：当前阶段只完成文档，不执行代码实现。

## 1. WP-M0 Documentation Tasks

| Task | Output | Acceptance |
| --- | --- | --- |
| WP-M0-D1 PRD | `workflow_platform_main_entry_prd.md` | PV13 首页基线、用户目标、能力分类、No-Go 明确。 |
| WP-M0-D2 Architecture | `workflow_platform_main_entry_target_architecture.md` | 具体代码实体和交互关系明确。 |
| WP-M0-D3 Plan | `workflow_platform_main_entry_development_and_acceptance_plan.md` | WP-M1 到 WP-M11 顺序明确。 |
| WP-M0-D3B BFF/DTO Contract | `workflow_platform_main_entry_bff_dto_contract.md` | WP-M1 到 WP-M11 route allowlist、DTO snapshot、browser denylist 明确。 |
| WP-M0-D3C Runner Spec | `workflow_platform_main_entry_acceptance_runner_spec.md` | WP-M1 到 WP-M11 自动化验收输出、场景和 PASS/FAIL 规则明确。 |
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
- WP-M5B: PV22 external app handoff readiness [PASS bounded review].

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

## 7. WP-M6 Frontend Full Data-Driven Closure Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M6-I1 | Inventory every `V13EditableStudio.tsx` normal-path data source. | Source inventory identifies scenarioData, fallbackGraph, timeline, Inspector, chat and any other static business facts。 |
| WP-M6-I2 | Define BFF/DTO source for scenario catalog, selected scenario, graph, Inspector, timeline, quality, evidence and chat initial context. | DTO snapshot maps each UI region to BFF/DTO/artifact refs。 |
| WP-M6-I3 | Replace normal-path static rendering with typed BFF/client data. | Browser network log and UI screenshots prove BFF/DTO first rendering。 |
| WP-M6-I4 | Preserve explicit offline fallback with user-visible boundary. | fallback-status DTO and screenshot mark fallback reason and non-claim。 |
| WP-M6-I5 | Generate data-source closure report. | `frontend-data-source-closure-report.json` shows `normal_path_static_sources == 0`。 |
| WP-M6-I6 | Run PRD and No False Green review. | No claim that fallback/mock is real projection。 |

## 8. WP-M7 WorkflowSpecGraph Edit/Save/Readback Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M7-I1 | Bind node drag to graph mutation DTO. | Drag action changes backend graph after save and survives refresh。 |
| WP-M7-I2 | Bind legal edge create and delete/cancel to graph mutation DTO. | Edge before/after DTO and screenshots PASS。 |
| WP-M7-I3 | Bind node configuration updates to BFF DTO. | Role/goal/tool/skill/MCP/quality config readback PASS。 |
| WP-M7-I4 | Validate graph and expose visible reasons for invalid edges or missing fields. | Validation DTO and failure screenshots PASS。 |
| WP-M7-I5 | Generate WorkflowDiff from saved backend graph. | Diff DTO references saved graph revision and human review log PASS。 |
| WP-M7-I6 | Produce graph edit/save/readback report. | `graph-edit-save-readback-report.json` PASS。 |

## 9. WP-M8 Publish / Run / Human / Evidence Inline Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M8-I1 | Add PV13 inline publish action for validated graph. | WorkflowVersion readback and audit refs PASS。 |
| WP-M8-I2 | Add PV13 inline run action for active version. | WorkflowInstance and StationRun readback PASS。 |
| WP-M8-I3 | Add Human Gate approve/reject in PV13 workbench. | Before/after state digest PASS。 |
| WP-M8-I4 | Add Evidence Review in PV13 workbench. | artifact/trace/quality/audit/claim/redaction categories visible。 |
| WP-M8-I5 | Prove path does not rely on separate PV19/PV21 pages. | Browser action log shows continuous PV13 workbench path。 |
| WP-M8-I6 | Produce inline runtime report. | `workflow-inline-runtime-report.json` PASS。 |

## 10. WP-M9 Three Business Scenario Artifact Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M9-I1 | Document summary scenario artifact. | Input hash, summary artifact/content snapshot, citation/quality/human/redaction refs PASS。 |
| WP-M9-I2 | Code review scenario artifact. | Input hash, review artifact/content snapshot, file/risk/test/audit/human refs PASS。 |
| WP-M9-I3 | Meeting brief scenario artifact. | Input hash, brief/action item artifact/content snapshot, decision/open-question/human refs PASS。 |
| WP-M9-I4 | Present artifacts in PV13 workbench. | User can inspect output and evidence without reading only acceptance report。 |
| WP-M9-I5 | Produce business artifact manifest. | `business-artifact-manifest.json` lists all three scenarios and evidence refs。 |
| WP-M9-I6 | PRD review and claim guard. | No final commercial deliverable or production business app claim。 |

## 11. WP-M10 Frontend Quality And Failure-State Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M10-I1 | Loading and empty states. | Screenshots and assertions PASS。 |
| WP-M10-I2 | Error, permission denied and BFF offline states. | Visible recovery/retry path PASS。 |
| WP-M10-I3 | Validation failure and human reject states. | Reason and next action visible PASS。 |
| WP-M10-I4 | Cancel/retry/timeout user states. | Deterministic fixture or BFF state setup PASS。 |
| WP-M10-I5 | Keyboard, focus and responsive checks. | Keyboard log, focus screenshots and desktop/constrained screenshots PASS。 |
| WP-M10-I6 | Accessibility and performance checks. | a11y report and performance budget PASS or explicit bounded exception。 |
| WP-M10-I7 | Produce quality/failure-state report. | `frontend-quality-failure-state-report.json` PASS。 |

## 12. WP-M11 Aggregate Frontend Completion Audit Tasks

| Task | Implementation target | Acceptance |
| --- | --- | --- |
| WP-M11-I1 | Collect all WP-M6 to WP-M10 evidence manifests. | Missing evidence marks BLOCKED。 |
| WP-M11-I2 | Map WP-FR-1 to WP-FR-20 to evidence. | `claim-to-evidence-matrix.json` PASS。 |
| WP-M11-I3 | Re-run No False Green scan. | Forbidden positive claims absent outside No-Go/risk/prohibited contexts。 |
| WP-M11-I4 | Re-run PRD and target architecture review. | No spec drift or architecture bypass。 |
| WP-M11-I5 | Generate Chinese HTML aggregate audit report. | `frontend-completion-aggregate-audit.html` includes screenshots, current vs target architecture, scenarios and risks。 |
| WP-M11-I6 | Define next-stage options. | Path D, business Pack productization and open-source/commercial readiness remain separate post-WP-M11 choices。 |
