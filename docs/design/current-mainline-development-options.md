# harnessOS Current Mainline Development Options

文档状态：当前主线事实核查与下一阶段开发选项。
日期：2026-06-27。
用途：把当前业务实际实现、未完成内容和可选技术路径放到同一入口，避免旧 `TASKS.md`、V3.0 closeout、V12-V15/PV16 pilot 证据互相混淆。
边界：本文是开发计划和事实核查文档，不是运行证据、生产证据或产品完成声明。

## 1. Fact Check

### 当前已能作为实现事实讨论

| Area | Current fact | Evidence entry |
| --- | --- | --- |
| API / Gateway | FastAPI app includes health, BFF routes, `/v1/runs`, `/v1/runs/stream`, `/v1/rpc`, sessions and events. | `main.py`, `apps/api/__init__.py`, `apps/api/routers/runs.py` |
| RPC registry | Gateway registers session, turn, trace, approval, artifact, job, connector, workflow, pack and agent methods. | `apps/gateway/service.py` |
| Multi-app scope | Built-in app profiles exist for meeting, knowledge, interview, investment and video_studio. | `core/apps/profiles.py` |
| Pack registry | Pack manifest loading, duplicate rejection, PackAssemblyResult and assembly status exist. | `core/packs/registry.py` |
| Connector registry/runtime | Built-in connector definitions, health, security descriptors, submit/poll/cancel/collect and MCP stdio execution exist. | `apps/gateway/connectors.py`, `apps/gateway/connector_execution.py` |
| Meeting reference pack | Active pack with `meeting.workflow`, FunASR / Meeting MCP contracts and artifact lineage. | `packs/meeting/manifest.json`, `packs/meeting/workflow.py` |
| Knowledge reference pack | Active pack with data_service MCP workflow, artifacts and boundary checks. | `packs/knowledge/manifest.json`, `packs/knowledge/workflow.py` |
| Video Studio planning | Active pack creates planning and lineage artifacts. | `packs/video_studio/manifest.json`, `packs/video_studio/workflow.py` |
| SDK / templates | Python SDK, TypeScript SDK, BFF templates and reference app assets exist. | `sdk/`, `templates/`, `examples/reference_app/` |

### 当前不能作为完成声明

| Claim | Reality |
| --- | --- |
| Production readiness | Not proven. V15/PV16 only provide bounded smoke / hardening evidence. |
| Complete Workflow Studio GA | Not proven. PV21 proves a bounded candidate closed loop only, not product-grade GA readiness. |
| Complete Agent executor GA | Not proven. PV20 proves a governed bounded review path only, not unrestricted production automation. |
| Product-grade frontend complete | Not proven. V12-V15 are bounded review slices. |
| External app contract complete | Not proven. PV22-R0 documents the target and gates only; SDK/template/reference-app evidence still needs implementation. |
| Full Meeting / Knowledge productization | Not proven. They are reference packs / validation samples. |
| Interview / Investment productization | Not implemented. Their packs are stub / planned. |
| Real Video Studio rendering | Not proven. Current workflow produces planning and render manifest artifacts. |

### Environment finding

The local environment has been restored for the current PV17 implementation pass:

```text
pydantic_settings 2.14.2
pytest 9.1.1
30 passed, 6 warnings
```

The restored smoke covered API runs, CLI headless, pack registry, Meeting pack assembly, Knowledge pack assembly, PV17 BFF routes and the PV17 acceptance runner tests. Remaining warnings are existing dependency / Pydantic deprecation warnings, not current PV17 failures.

## 2. Current Gap

The main project gap is no longer V3.0 Core completion. V3.0 is documented as final closeout, with Meeting / Knowledge reference pack validation passed.

The active gap for the previous stage has been resolved: **Path A - Product Closed Loop** was selected, implemented and accepted as PV17 bounded review evidence. PV17 turns the V12-V15/PV16 bounded review slices into one mainline product path without overclaiming production, Xpert parity or Agent executor readiness.

The selected next stage after PV17 was **Path C - Business Pack Productization**, with **Knowledge** as the first business domain. PV18 has now implemented and accepted a bounded Knowledge OPC productization review path with real `data_service_mcp` evidence.

PV19 Runtime Workflow Platform Closed Loop has passed bounded review acceptance with formal `/bff/pv19/*` routes, backend acceptance evidence and Chrome CDP browser screenshot evidence. **PV20 - Complete Agent Executor bounded review path** has passed through S6: Agent execution contract/read model, allowlisted local skill execution, allowlisted read-only local tool execution, allowlisted local MCP fixture execution, approval handoff/denial refs, bounded timeout/cancel/retry/redaction fixtures and a browser-visible evidence page. This is not a production/general availability claim; full product-grade human handoff UX, unrestricted MCP, production scheduler and production readiness remain open.

**PV21 - Complete Workflow Studio bounded candidate** has passed bounded review acceptance with default Studio entry, `/bff/pv21/*` DTO routes, graph save/validate/diff, version publish/rollback, runtime run, human gate and evidence review. This is not a complete Workflow Studio GA or product-grade frontend claim. **PV22 - Path B External App Contract** has documentation/readiness; PV22-R0 documents the SDK/BFF template/reference app/capability token contract target, while SDK smoke, template smoke, auth negative fixtures and reference app E2E remain implementation work. The current product-entry alignment gap is **WP-M0 - Workflow Platform Main Entry**: subsequent implementation must first converge the default user experience around one workflow platform entry before PV22 external integration implementation proceeds as the default path. Path D production governance hardening, broader business pack productization and commercial readiness remain later stages.

### WP-M0 - Workflow Platform Main Entry Alignment

Status: selected documentation alignment stage after PV21 bounded candidate and PV22-R0 readiness. Canonical docs:

- `docs/design/V12-V15.x/workflow_platform_main_entry_prd.md`
- `docs/design/V12-V15.x/workflow_platform_main_entry_target_architecture.md`
- `docs/design/V12-V15.x/workflow_platform_main_entry_bff_dto_contract.md`
- `docs/design/V12-V15.x/workflow_platform_main_entry_development_and_acceptance_plan.md`
- `docs/design/V12-V15.x/workflow_platform_main_entry_acceptance_runner_spec.md`
- `docs/design/V12-V15.x/workflow_platform_main_entry_milestone_roadmap.md`
- `docs/design/V12-V15.x/workflow_platform_main_entry_acceptance_gate.md`
- `docs/design/V12-V15.x/workflow_platform_main_entry_current_gap_analysis.md`
- `docs/design/V12-V15.x/workflow_platform_main_entry_implementation_task_matrix.md`
- `docs/design/V12-V15.x/workflow_platform_main_entry_implementation_readiness_audit.md`
- `docs/design/V12-V15.x/workflow_platform_main_entry_document_support_audit.md`
- `docs/design/V12-V15.x/workflow_platform_main_entry_gap_analysis.drawio`

Goal: make Workflow Platform the first product entry and align later implementation around one user path: workspace -> canvas -> Agent/Tool/Skill/MCP resources -> WorkflowDiff -> publish/run -> human gate -> evidence review.

Implementation order after this document gate:

1. WP-M1 first entry and information architecture.
2. WP-M2 canvas interaction hardening.
3. WP-M3 runtime/evidence convergence.
4. WP-M4 governed Agent executor product integration.
5. WP-M5 PV22 external app handoff review.

Acceptance: WP-M0 is documentation support only. It permits implementation review, not any implementation-complete claim.

`TASKS.md` has been rewritten to make this distinction explicit.

## 3. Technical Paths

### Path A - Product Closed Loop

Status: selected and implemented as PV17 bounded review evidence. Canonical docs:

- `docs/design/V12-V15.x/pv17_product_closed_loop_prd.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_target_architecture.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_bff_dto_contract.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_implementation_task_matrix.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_development_and_acceptance_plan.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_acceptance_runner_spec.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_milestone_roadmap.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_acceptance_gate.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_current_gap_analysis.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_implementation_readiness_audit.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_gap_analysis.drawio`

Goal: make one coherent browser path usable for review: setup -> Studio -> run -> inspect -> evidence.

Implementation outline:

- Add or harden BFF-only routes for workspace/project/app/Station Agent mutation.
- Connect WorkflowSpec versioning to a runtime-backed run/inspect path.
- Ensure Studio and operations views read DTOs, route logs and evidence refs rather than runtime truth directly.
- Add browser E2E and screenshots for create/edit/confirm/run/inspect.
- Keep all copy clear that this is not production readiness or complete Studio unless later evidence proves it.

Acceptance:

- Browser scenario PASS with screenshots.
- BFF route log and DTO schema validation.
- Runtime-backed run/inspect report.
- Browser denylist proving no direct Core/runtime store access.
- No False Green and redaction scans.

Evidence entry:

- `docs/design/V12-V15.x/evidence/pv17-product-closed-loop/`
- `docs/design/V12-V15.x/reports/pv17_product_closed_loop_acceptance_report.json`
- `docs/design/V12-V15.x/reports/pv17_stage_execution_plan.md`
- `docs/design/V12-V15.x/reports/pv17_prd_architecture_audit_closure.md`

Best when:

- The priority is a visible product experience or OPC demo.

### Path B - Platform External App Contract

Goal: turn existing SDK / BFF / template / reference app assets into a coherent external app integration stage.

Status: selected as PV22. PV22-R0 documentation/readiness is complete; implementation and acceptance remain pending.

Canonical docs:

- `docs/design/V12-V15.x/pv22_external_app_contract_prd.md`
- `docs/design/V12-V15.x/pv22_external_app_contract_target_architecture.md`
- `docs/design/V12-V15.x/pv22_external_app_contract_bff_dto_contract.md`
- `docs/design/V12-V15.x/pv22_external_app_contract_development_and_acceptance_plan.md`
- `docs/design/V12-V15.x/pv22_external_app_contract_milestone_roadmap.md`
- `docs/design/V12-V15.x/pv22_external_app_contract_acceptance_gate.md`
- `docs/design/V12-V15.x/pv22_external_app_contract_current_gap_analysis.md`
- `docs/design/V12-V15.x/pv22_external_app_contract_implementation_task_matrix.md`
- `docs/design/V12-V15.x/pv22_external_app_contract_implementation_readiness_audit.md`
- `docs/design/V12-V15.x/pv22_external_app_contract_document_support_audit.md`

Implementation outline:

- Freeze a protocol version and method/event/error registry subset for external apps.
- Validate Python and TypeScript SDK clients against real Gateway RPC.
- Harden capability token / scope binding / auth denial behavior.
- Make BFF templates and reference app run through documented smoke tests.
- Document compatibility and migration guarantees.

Acceptance:

- Python SDK smoke PASS.
- TypeScript SDK build/test PASS.
- Minimal and full BFF template smoke PASS.
- Reference app E2E PASS.
- Auth/scope negative fixtures PASS.
- Redaction and No False Green scans.

Best when:

- The priority is adoption by other apps, developers or partners.

### Path C - Business Pack Productization

Goal: choose one business domain and move it from reference/stub/planning status toward a productized workflow.

Status: implemented and accepted for PV18 bounded review with Knowledge as the first domain. Canonical docs and evidence:

- `docs/design/V12-V15.x/pv18_knowledge_opc_productization_prd.md`
- `docs/design/V12-V15.x/pv18_knowledge_opc_productization_target_architecture.md`
- `docs/design/V12-V15.x/pv18_knowledge_opc_productization_bff_dto_contract.md`
- `docs/design/V12-V15.x/pv18_knowledge_opc_productization_acceptance_runner_spec.md`
- `docs/design/V12-V15.x/pv18_knowledge_opc_productization_implementation_task_matrix.md`
- `docs/design/V12-V15.x/pv18_knowledge_opc_productization_development_and_acceptance_plan.md`
- `docs/design/V12-V15.x/pv18_knowledge_opc_productization_milestone_roadmap.md`
- `docs/design/V12-V15.x/pv18_knowledge_opc_productization_acceptance_gate.md`
- `docs/design/V12-V15.x/pv18_knowledge_opc_productization_current_gap_analysis.md`
- `docs/design/V12-V15.x/pv18_knowledge_opc_productization_implementation_readiness_audit.md`
- `docs/design/V12-V15.x/pv18_knowledge_opc_productization_gap_analysis.drawio`
- `docs/design/V12-V15.x/schemas/pv18_knowledge_opc_acceptance_data.schema.json`
- `docs/design/V12-V15.x/schemas/pv18_knowledge_opc_artifact_manifest.schema.json`
- `docs/design/V12-V15.x/schemas/pv18_knowledge_opc_dto_snapshot.schema.json`
- `docs/design/V12-V15.x/evidence/pv18-knowledge-opc-productization/acceptance-data.json`
- `docs/design/V12-V15.x/reports/pv18_knowledge_opc_productization_acceptance_report.json`
- `docs/design/V12-V15.x/reports/pv18_stage_execution_and_audit_closure.md`

Recommended order:

1. Knowledge, because it already has data_service MCP and citation artifacts.
2. Meeting, because it already has real-audio reference validation but depends on adjacent services.
3. Video Studio, if the next goal is creative workflow planning before real rendering.
4. Interview, if the target is lower-risk OPC service packaging.
5. Investment only after stronger risk, citation, compliance and human-review boundaries.

Implementation outline:

- Define one user-facing workflow with inputs, outputs, quality gates and handoff.
- Keep domain code inside Pack / Connector / RuntimeAdapter boundaries.
- Add E2E sample data, artifact lineage, trace, audit and failure recovery.
- Add business quality evaluation only after platform evidence is stable.

Acceptance:

- Domain E2E PASS with deterministic fixtures.
- Artifact lineage and trace coverage.
- Policy / approval negative cases.
- Human-readable report and failure explanation.
- No Core/Gateway business special-case added.

Best when:

- The priority is OPC commercialization or one vertical product.

### Path D - Production Governance Hardening

Goal: close the platform gaps needed before any production-readiness discussion.

Status: backlog option. Not selected for PV18.

Implementation outline:

- Tenant isolation and auth policy hardening.
- Credential lifecycle, secret redaction and revocation.
- Audit retention, export and incident timelines.
- Deployment runbooks, health checks, rollback and smoke automation.
- CI matrix for default regression and explicit integration tests.

Acceptance:

- Tenant isolation denial fixtures.
- Credential rotation/revocation evidence.
- Audit export and incident timeline evidence.
- Deployment smoke with rollback notes.
- CI default suite and explicit integration suite documented.

Best when:

- The priority is enterprise, self-hosting or compliance-heavy deployment.

### PV19 - Runtime Workflow Platform Closed Loop

Goal: make the next stage about the full workflow platform loop rather than another isolated business page.

Status: implemented and accepted for bounded review. Canonical docs and evidence:

- `docs/design/V12-V15.x/pv19_runtime_workflow_platform_prd.md`
- `docs/design/V12-V15.x/pv19_runtime_workflow_platform_target_architecture.md`
- `docs/design/V12-V15.x/pv19_runtime_workflow_platform_development_and_acceptance_plan.md`
- `docs/design/V12-V15.x/pv19_runtime_workflow_platform_milestone_roadmap.md`
- `docs/design/V12-V15.x/pv19_runtime_workflow_platform_acceptance_gate.md`
- `docs/design/V12-V15.x/pv19_runtime_workflow_platform_current_gap_analysis.md`
- `docs/design/V12-V15.x/pv19_runtime_workflow_platform_bff_dto_contract.md`
- `docs/design/V12-V15.x/pv19_runtime_workflow_platform_acceptance_runner_spec.md`
- `docs/design/V12-V15.x/pv19_runtime_workflow_platform_implementation_readiness_audit.md`
- `docs/design/V12-V15.x/pv19_runtime_workflow_platform_gap_analysis.drawio`
- `docs/design/V12-V15.x/evidence/pv19-runtime-workflow-platform/backend-acceptance-report.json`
- `docs/design/V12-V15.x/evidence/pv19-runtime-workflow-platform/acceptance-data.json`
- `docs/design/V12-V15.x/evidence/pv19-runtime-workflow-platform/pv19-acceptance-report.html`

Implementation outline:

- Make the real workbench entry visible and non-empty.
- Connect graph edit, WorkflowDiff and publish into WorkflowVersion readback.
- Run a published WorkflowVersion through the runtime as WorkflowInstance.
- Add at least one human interaction gate that changes backend runtime state.
- Aggregate artifacts, trace, quality, audit and claim evidence in one review path.
- Keep the business sample outside workflow core, Gateway core and App shell.

Acceptance:

- Browser E2E PASS with screenshots.
- BFF route log and DTO snapshot PASS.
- Runtime run inspect report PASS.
- Human interaction state transition and audit trail PASS.
- Claim-to-evidence, redaction and No False Green scans PASS.

Best when:

- The priority is being able to say the platform has a runtime-backed workflow orchestration, run, human interaction and evidence closed loop ready for bounded review.

### PV20 - Complete Agent Executor

Goal: make Agent nodes in runtime workflows execute through a governed, reusable executor contract instead of UI simulation or business runner shortcuts.

Status: implemented for bounded review through PV20-S6. Canonical docs and evidence:

- `docs/design/V12-V15.x/pv20_complete_agent_executor_prd.md`
- `docs/design/V12-V15.x/pv20_complete_agent_executor_target_architecture.md`
- `docs/design/V12-V15.x/pv20_complete_agent_executor_development_and_acceptance_plan.md`
- `docs/design/V12-V15.x/pv20_complete_agent_executor_acceptance_gate.md`
- `docs/design/V12-V15.x/pv20_complete_agent_executor_implementation_task_matrix.md`
- `docs/design/V12-V15.x/pv20_complete_agent_executor_implementation_readiness_audit.md`
- `docs/design/V12-V15.x/pv20_s1_agent_execution_contract_development_plan.md`
- `docs/design/V12-V15.x/pv20_s1_agent_execution_contract_audit.md`
- `docs/design/V12-V15.x/pv20_s2_skill_read_model_execution_development_plan.md`
- `docs/design/V12-V15.x/pv20_s2_skill_read_model_execution_audit.md`
- `docs/design/V12-V15.x/pv20_s3_tool_mcp_execution_development_plan.md`
- `docs/design/V12-V15.x/pv20_s3_tool_mcp_execution_audit.md`
- `docs/design/V12-V15.x/pv20_s3b_mcp_fixture_execution_development_plan.md`
- `docs/design/V12-V15.x/pv20_s3b_mcp_fixture_execution_audit.md`
- `docs/design/V12-V15.x/pv20_s4_approval_handoff_development_plan.md`
- `docs/design/V12-V15.x/pv20_s4_approval_handoff_audit.md`
- `docs/design/V12-V15.x/pv20_s5_timeout_cancel_retry_redaction_development_plan.md`
- `docs/design/V12-V15.x/pv20_s5_timeout_cancel_retry_redaction_audit.md`
- `docs/design/V12-V15.x/pv20_s6_browser_agent_executor_evidence_development_plan.md`
- `docs/design/V12-V15.x/pv20_s6_browser_agent_executor_evidence_audit.md`
- `docs/design/V12-V15.x/evidence/pv20-complete-agent-executor/acceptance-data.json`
- `docs/design/V12-V15.x/evidence/pv20-complete-agent-executor/frontend-s6-acceptance.md`

Implementation outline:

- Define AgentExecutionEnvelope and AgentExecutionResult DTOs bound to WorkflowInstance / StationRun.
- Implement governed executor service with policy, scope, timeout, cancel, retry and redaction.
- Support at least one allowlisted skill/read-model node and one allowlisted MCP/tool node.
- Preserve human confirmation for high-risk durable operations.
- Aggregate execution evidence into browser-visible BFF read models.

Acceptance:

- Backend executor E2E PASS with real StationRun / execution evidence.
- Browser E2E PASS with screenshots.
- Negative fixtures for unknown tool, unknown skill, MCP scope escape, agent direct publish/approval, timeout, cancel, retry and redaction.
- No False Green scan proving no production, unrestricted automation, complete Studio or commercial readiness claim.

### PV21 - Complete Workflow Studio

Goal: turn the V13 editable Studio pilot, PV19 runtime workflow loop and PV20 governed Agent executor evidence into one coherent Workflow Studio candidate experience.

Status: implemented and accepted for bounded candidate review. Canonical docs and evidence:

- `docs/design/V12-V15.x/pv21_complete_workflow_studio_prd.md`
- `docs/design/V12-V15.x/pv21_complete_workflow_studio_target_architecture.md`
- `docs/design/V12-V15.x/pv21_complete_workflow_studio_bff_dto_contract.md`
- `docs/design/V12-V15.x/pv21_complete_workflow_studio_acceptance_runner_spec.md`
- `docs/design/V12-V15.x/pv21_complete_workflow_studio_development_and_acceptance_plan.md`
- `docs/design/V12-V15.x/pv21_complete_workflow_studio_milestone_roadmap.md`
- `docs/design/V12-V15.x/pv21_complete_workflow_studio_acceptance_gate.md`
- `docs/design/V12-V15.x/pv21_complete_workflow_studio_current_gap_analysis.md`
- `docs/design/V12-V15.x/pv21_complete_workflow_studio_implementation_task_matrix.md`
- `docs/design/V12-V15.x/pv21_complete_workflow_studio_implementation_readiness_audit.md`
- `docs/design/V12-V15.x/pv21_complete_workflow_studio_document_support_audit.md`
- `docs/design/V12-V15.x/pv21_complete_workflow_studio_gap_analysis.drawio`
- `docs/design/V12-V15.x/pv21_stage_execution_audit_closure.md`
- `docs/design/V12-V15.x/evidence/pv21-complete-workflow-studio/acceptance-data.json`
- `docs/design/V12-V15.x/evidence/pv21-complete-workflow-studio/pv21-acceptance-report.html`

Implemented bounded scope:

- Default Studio entry routes to `?studio=pv21-complete-workflow-studio`.
- `/bff/pv21/*` DTO routes cover state, graph, validation, diff, versions, runs, human actions and evidence.
- Canvas graph save/validate/diff, version publish/rollback, runtime run, human gate and evidence review are covered by backend and CDP browser evidence.
- Preserve platform generality and reject business-specific workflow core/Gateway/App shell branches.

Acceptance completed:

- Browser/CDP evidence PASS with home/edit/version/evidence screenshots.
- BFF route log and DTO snapshot PASS.
- Graph roundtrip, validation, version publish/rollback, runtime run, human transition and evidence summary PASS.
- No False Green, redaction and platform generality scans PASS.
- Remaining boundary: not a production-ready, product-grade, complete Workflow Studio GA claim.

## 4. Recommended Sequence

1. Restore local validation environment.
2. Run lightweight smoke for API, CLI, Pack Registry, Meeting assembly and Knowledge assembly.
3. Treat PV17 as complete for bounded review only.
4. Treat PV18 Knowledge OPC as complete for bounded review only.
5. Treat PV19 as complete for bounded review only.
6. Treat PV20 Complete Agent Executor bounded review path as complete through S6.
7. Treat PV21 Complete Workflow Studio as complete for bounded candidate review only.
8. Treat PV22-R0 External App Contract documentation/readiness as complete, but do not start PV22-S1 as the default path until the Workflow Platform host surface is aligned.
9. Treat WP-M0 Workflow Platform Main Entry as the current documentation alignment gate, then proceed to WP-M1 first entry, WP-M2 canvas interaction hardening, WP-M3 runtime/evidence convergence and WP-M4 governed executor product integration.
10. Start PV22-S1 registry freeze only after WP-M5 confirms that external apps are targeting the stable Workflow Platform surface, or after an explicit readiness audit records the risk of doing PV22 earlier.

## 4.1 Accepted Post-PV18 Route

The accepted long-range route is recorded in
`docs/design/V12-V15.x/post_pv18_runtime_platform_development_route.md`.

| Order | Stage | Intent |
| --- | --- | --- |
| 1 | PV19 Runtime-backed Workflow Studio Closed Loop | Prove workbench orchestration, publish, runtime run, human interaction and evidence review as one bounded platform loop. |
| 2 | Complete Agent Executor | Make Agent nodes execute through a governed, reusable executor contract instead of UI simulation or business runner shortcuts. |
| 3 | PV21 Complete Workflow Studio | Bounded candidate for Studio versioning, publish/run/rollback and audit loop is complete; GA/product-grade Studio remains unclaimed. |
| 4 | WP-M0 Workflow Platform Main Entry | Documentation gate that makes the workflow platform the first product entry and aligns later implementation around it. |
| 5 | WP-M1-M4 Workflow Platform MVP Candidate | Implement first entry, canvas interaction hardening, runtime/evidence convergence and governed executor product integration. |
| 6 | PV22 Path B External App Contract | Stabilize SDK, BFF template, reference app, capability token and method/event/error registry for external apps after the host surface is stable. PV22-R0 documentation/readiness is complete; implementation remains pending. |
| 7 | Path D Production Governance Hardening | Close tenant, credential, audit retention, deployment recovery and operations hardening gaps. |
| 8 | Business Pack Productization | Productize selected packs without contaminating workflow core, Gateway core or App shell. |
| 9 | Open-source / Commercial Readiness | Prepare contributor, release, deployment, license, quota, billing and public review materials. |

## 5. No-Go

- Do not claim HarnessOS is production ready.
- Do not claim Xpert parity complete.
- Do not claim product-grade frontend complete.
- Do not claim complete Workflow Studio ready.
- Do not claim Agent executor ready.
- Do not treat docs, screenshots, content images or presentation pages as runtime / BFF / DTO / browser E2E / production evidence.
