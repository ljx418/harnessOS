# Tasks - harnessOS

本文是当前开发主线入口。旧 Phase 0-5 清单已经与 V3.0、V12-V15/PV16、V3.5 后续文档发生口径漂移；从现在起，任务判断优先以本文和下列 source of truth 为准。

## Source Of Truth

| 用途 | 文档 |
| --- | --- |
| 当前主线选项与事实核查 | `docs/design/current-mainline-development-options.md` |
| V3.0 Core / Pack / Connector closeout | `docs/design/V3.0/CURRENT-STATUS_v3.md` |
| V3.0 gap / V3.x+ backlog | `docs/design/V3.0/v3_current_gap_analysis.md` |
| V3.0 development plan | `docs/design/V3.0/v3_development_plan_multi_app_core.md` |
| V12-V15/PV16 product evidence boundary | `docs/design/V12-V15.x/v12_to_v15_current_gap_analysis.md` |
| PV17 selected product closed loop stage | `docs/design/V12-V15.x/pv17_product_closed_loop_development_and_acceptance_plan.md` |
| PV18 selected Knowledge OPC productization stage | `docs/design/V12-V15.x/pv18_knowledge_opc_productization_development_and_acceptance_plan.md` |
| PV19 selected runtime workflow platform closed loop stage | `docs/design/V12-V15.x/pv19_runtime_workflow_platform_development_and_acceptance_plan.md` |
| PV20 selected Complete Agent Executor stage | `docs/design/V12-V15.x/pv20_complete_agent_executor_development_and_acceptance_plan.md` |
| PV21 selected Complete Workflow Studio stage | `docs/design/V12-V15.x/pv21_complete_workflow_studio_development_and_acceptance_plan.md` |
| PV21 stage execution closure | `docs/design/V12-V15.x/pv21_stage_execution_audit_closure.md` |
| PV22 selected External App Contract stage | `docs/design/V12-V15.x/pv22_external_app_contract_development_and_acceptance_plan.md` |
| WP-M0 through WP-M5A Workflow Platform PV13 baseline and business-scenario productization | `docs/design/V12-V15.x/workflow_platform_main_entry_development_and_acceptance_plan.md` |
| WP-M0 PV13 baseline BFF/DTO contract and acceptance runner | `docs/design/V12-V15.x/workflow_platform_main_entry_bff_dto_contract.md` |
| WP-M5A business-scenario productization substage plan | `docs/design/V12-V15.x/workflow_platform_wp_m5a_business_scenario_productization_plan_and_audit.md` |
| WP-M6 through WP-M11 PRD-defined frontend functionality completion plan | `docs/design/V12-V15.x/workflow_platform_wp_m6_to_m11_frontend_completion_plan_and_audit.md` |
| WP-M6 through WP-M11 document support audit | `docs/design/V12-V15.x/workflow_platform_wp_m6_to_m11_document_support_audit.md` |
| WP-M6 through WP-M11 implementation readiness audit | `docs/design/V12-V15.x/workflow_platform_wp_m6_to_m11_implementation_readiness_audit.md` |
| WP-M6 substage readiness note | `docs/design/V12-V15.x/workflow_platform_wp_m6_substage_readiness_note.md` |
| WP-M6 through WP-M11 report schemas and audit reports | `docs/design/V12-V15.x/schemas/` and `docs/design/V12-V15.x/reports/` |
| Post-PV18 long-range route | `docs/design/V12-V15.x/post_pv18_runtime_platform_development_route.md` |
| PV19 documentation support audit | `docs/design/V12-V15.x/pv19_runtime_workflow_platform_document_support_audit.md` |
| ChatGPT / human project intro | `docs/present/harnessos-project-introduction/00_CHATGPT_CONTEXT_INDEX.md` |

## Current Status

### Frozen Baseline

- [x] Gateway protocol control plane: `/v1/runs`, `/v1/runs/stream`, `/v1/rpc`, session list/read/transcript/events, stdio JSONL and headless CLI baseline exist.
- [x] V3.0 Multi-App Core: `AppProfile`、`ScopeContext`、scope-aware Gateway/Core service paths and namespace isolation are frozen as baseline.
- [x] V3.0 Pack / Connector: Pack manifest loading, PackAssemblyResult, ConnectorRegistry, connector health/capabilities and connector execution runtime are baseline.
- [x] V3.0 Job / Artifact / Governance: job lifecycle, connector jobs, artifact metadata/lineage, large-file read blocking and trace/approval scope guards are baseline.
- [x] Meeting reference pack: `packs/meeting` validates platform boundaries with FunASR / Meeting MCP integration, legacy facade equivalence and strict/resilience real-audio evidence.
- [x] Knowledge reference pack: `packs/knowledge` validates data_service MCP lifecycle, artifact set, data boundary and connector replacement.
- [x] V12-V15/PV16 bounded product evidence: browser workbench foundation, editable Studio pilot, governed extension ecosystem pilot, observability/deployment baseline and product-runtime hardening pilot have bounded review evidence.
- [x] PV17 Product Closed Loop bounded review: formal `/bff/pv17/*` routes, Product Console / Mission Studio / confirm run / inspect / evidence browser path and acceptance runner evidence passed.
- [x] PV18 Knowledge OPC bounded review implementation: Path C selected Knowledge as first business domain, then implemented `/bff/pv18/knowledge/*`, the browser Knowledge OPC workbench, real `data_service_mcp` acceptance, screenshots, evidence package and acceptance runner report for bounded review.
- [x] PV19 Runtime Workflow Platform bounded review implementation: formal `/bff/pv19/*` routes, WorkflowDiff, WorkflowVersion publish, runtime-backed WorkflowInstance, human interaction, evidence review, backend acceptance runner and Chrome CDP browser screenshot evidence passed.
- [x] PV20 Complete Agent Executor bounded review path complete through S6: governed reusable Agent executor candidate evidence exists, with no unrestricted automation or production-readiness claim.
- [x] PV20-S1 Agent execution contract bounded review: formal `/bff/pv20/*` contract read routes, AgentExecutionEnvelope / AgentExecutionResult DTOs, WorkflowInstance / StationRun binding and acceptance runner evidence passed.
- [x] PV20-S2 allowlisted local skill execution bounded review: user-confirmed `/bff/pv20/*/agent-skill-executions` route, bundled skill executor, StationRun metadata readback, artifact ref and acceptance runner evidence passed.
- [x] PV20-S3A allowlisted local tool execution bounded review: user-confirmed `/bff/pv20/*/agent-tool-executions` route, read-only artifact metadata tool boundary, StationRun readback and acceptance runner evidence passed.
- [x] PV20-S3B allowlisted local MCP fixture execution bounded review: user-confirmed `/bff/pv20/*/agent-mcp-executions` route, `connector.submit`, `approval.respond`, retry context, stdio MCP fixture, StationRun readback and acceptance runner evidence passed.
- [x] PV21 Complete Workflow Studio bounded candidate implementation: default PV21 Studio entry, `/bff/pv21/*` DTO boundary, graph save/validate/diff, publish/rollback, runtime run, human gate and evidence review passed bounded acceptance. This does not prove production readiness, product-grade frontend completion or a complete Workflow Studio GA claim.
- [x] PV22 External App Contract bounded implementation: PRD, target architecture, BFF/DTO contract, development plan, milestone roadmap, acceptance gate, gap analysis, implementation task matrix, readiness audit, document support audit, contract registry, `reference_app` AppProfile, SDK/Gateway smoke, BFF template smoke, capability negative fixtures, reference app boundary/API path and aggregate evidence package have passed bounded acceptance. This does not prove production readiness, external ecosystem completion, commercial readiness, complete Workflow Studio GA or Agent executor readiness.
- [x] WP-M0 Workflow Platform PV13 baseline main-entry documentation alignment: PRD, target architecture, BFF/DTO contract, acceptance runner spec, development/acceptance plan, roadmap, acceptance gate, gap analysis, task matrix, readiness/support audits and drawio now define the next product-entry implementation target. The target homepage/frontend baseline is the PV13 Light Studio workflow platform experience implemented by `V13EditableStudio.tsx` and `v13-editable-studio.css`; the current degraded `WorkflowPlatformMainEntry` surface is a deviation to replace, not the target baseline. This is documentation support only, not implementation evidence.
- [x] WP-M1A through WP-M4 Workflow Platform PV13 baseline main-entry bounded implementation: formal `/bff/v13/*` compatibility routes, root and `?studio=workflow-platform` route remap to `V13EditableStudio`, PV13 canvas zoom/drag/connect/cancel hardening, PV21 capability parity loop and PV20 governed executor parity loop passed Chrome CDP bounded acceptance with evidence under `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/`. This does not prove a production-grade workflow platform, complete Workflow Studio GA, unrestricted Agent executor or production readiness.
- [x] WP-M5A Workflow Platform business-scenario productization bounded implementation: `/bff/workflow-platform/*` scenario projection and business output DTOs, PV13 workbench business-output panel, mock-reduction boundary, three required business scenario output summaries, Chrome CDP E2E screenshots, command logs and manifest evidence passed bounded acceptance under `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/`. This proves reviewable machine-readable business output summaries and evidence refs only; it does not prove standalone final business deliverables, production readiness or complete Workflow Studio GA.
- [x] WP-M6 through WP-M11 Workflow Platform frontend completion bounded implementation: `/bff/workflow-platform/*` frontend data-source closure, business artifact, quality-state and claim-evidence DTOs, PV13 typed client/UI projection, graph edit/save/readback evidence, inline publish/run/human/evidence evidence, three business artifact manifests, quality/failure-state evidence, claim-to-evidence matrix, schema validation, Chrome CDP E2E screenshots, command logs and aggregate HTML audit passed bounded acceptance under `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/`. This supports `PRD-defined frontend functionality complete for bounded review` only; it does not prove production readiness, product-grade frontend completion, complete Workflow Studio GA, unrestricted Agent executor or final commercial business-app completion.

### Bounded / Limited Completion

- [ ] Full product experience is not complete. V12-V15/PV16 evidence proves bounded review slices only.
- [ ] Complete Workflow Studio is not complete as a GA/product-grade claim. PV21 proves a bounded candidate closed loop only; WP-M6 through WP-M11 target PRD-defined frontend completion for bounded review, not GA/product-grade completion.
- [ ] Complete Agent executor is not complete as a production/general availability claim. PV20-S6 proves a bounded Agent executor review path: contract/read model, allowlisted local skill, read-only local tool, allowlisted local MCP fixture execution, approval handoff refs, bounded timeout/cancel/retry/redaction fixtures and browser-visible evidence page. Full product-grade human handoff UX, unrestricted MCP, production scheduler and production readiness remain open.
- [x] PV19 Runtime Workflow Platform bounded review has passed. It proves a bounded runtime workflow platform closed loop only; it does not prove production readiness, complete Workflow Studio, complete Agent executor or Xpert parity.
- [ ] Production deployment is not complete. V15/PV16 prove smoke / hardening evidence only; Path D production governance remains after WP-M11 or explicit user reselection.
- [ ] PV17 is bounded review evidence only; it does not prove production readiness, complete Workflow Studio or Agent executor readiness.
- [ ] Meeting and Knowledge are reference packs / validation samples, not final productized business apps.
- [x] WP-M5A business-scenario productization bounded review has passed. It proves DTO/evidence-driven scenario projection, business output summaries, artifact refs and human review refs for document summary, code review and meeting brief; it does not prove final standalone commercial deliverables or production business-app completion.
- [x] PV18 Knowledge OPC bounded review implementation has passed. It proves a bounded Knowledge OPC productization review path only; it does not prove production readiness, complete Workflow Studio, complete Agent executor or full commercial Knowledge productization.
- [ ] Video Studio currently generates planning and lineage artifacts; it does not prove real rendering execution.
- [ ] Interview and Investment remain stub / planned packs.
- [x] Local Python environment restored for current smoke: `.venv` was rebuilt with Python 3.12, `pydantic_settings` and `pytest` import successfully, and the current lightweight smoke suite passed.

## Current Backlog

### P0 - Mainline Synchronization And Validation

- [x] Replace stale `TASKS.md` with current source-of-truth structure.
- [x] Add `docs/design/current-mainline-development-options.md` with fact check, open gaps and technical path options.
- [x] Restore or document a working local Python environment.
- [x] Re-run lightweight smoke after environment restore:
  - `tests/test_api_runs.py`
  - `tests/test_cli_headless.py`
  - `tests/test_pack_registry.py`
  - Meeting / Knowledge pack assembly tests
- [ ] Reconcile outdated V3.0 TODO wording that still appears in old archived sections or downstream docs.

### P1 - Selected Product / Platform Stage

The completed selected stage was Path A, documented as PV17 Product Closed Loop. The completed post-PV17 stage is Path C, documented as PV18 Knowledge OPC Productization. PV19 Runtime Workflow Platform Closed Loop, PV20 Complete Agent Executor bounded review path, PV21 Complete Workflow Studio bounded candidate, WP-M5A Workflow Platform business-scenario productization, WP-M5B readiness refresh, PV22 External App Contract bounded implementation, and WP-M6 through WP-M11 PRD-defined frontend functionality completion have passed bounded review acceptance. Path D / production governance hardening, business Pack productization and open-source/commercial readiness are deferred unless the user explicitly reselects them.

- [x] Path A: Product closed loop.
  Built a bounded user-facing Product Console / Studio / run-inspect-evidence loop with browser evidence, BFF-only DTOs and runtime-backed inspection.
- [x] PV22-R0 / Path B documentation target: Platform external app contract.
  Defined the stage as a bounded external integration contract: SDK smoke, BFF templates, reference app, capability token, scope binding and method/event/error registry.
- [x] WP-M0 documentation target: Workflow Platform PV13 baseline main-entry alignment.
  Defined the next implementation direction as a single workflow platform first entry that uses the PV13 Light Studio page as the visual and interaction baseline, while converging PV19 runtime loop, PV20 governed executor evidence, PV21 save/publish/run/readback capabilities and PV22 external app handoff. `WorkflowPlatformMainEntry` is not the target homepage baseline, but its current PV21/PV20 closed-loop capabilities are now the capability parity source and must not be silently regressed during WP-M3/WP-M4. This is not implementation evidence.
- [x] WP-M1A..WP-M4 implementation and acceptance: Workflow Platform PV13 baseline main entry.
  Implemented main BFF `/bff/v13/*` compatibility routes, switched the default workflow platform route to `V13EditableStudio`, added explicit canvas connection cancellation, integrated PV21 save/validate/diff/publish/rollback/run/human/evidence parity and PV20 governed Skill/Tool/MCP executor parity into the PV13 page, and generated Chrome CDP acceptance evidence. This is bounded review evidence only.
- [x] WP-M5A implementation and acceptance: Business-scenario productization and data-driven projection.
  Implemented bounded scenario projection DTOs, business output DTOs, PV13 UI projection, mock-reduction report, three required business output summaries and acceptance evidence. This is bounded review evidence only; it does not claim final standalone document summary, code review or meeting brief products.
- [x] PV22-S1..SA implementation and acceptance.
  Consolidated SDK, BFF templates, reference app, auth / capability token and method/event/error registry into an accepted bounded integration review stage after WP-M5A PASS and WP-M5B readiness refresh. Evidence is under `docs/design/V12-V15.x/evidence/pv22-external-app-contract/`.
- [x] WP-M6 Frontend full data-driven closure.
  Remove normal-path dependency on frontend static business facts in PV13. Scenario, graph, Inspector, timeline, quality, evidence and chat initial context must come from BFF/DTO or artifact refs; fallback remains explicit only.
- [x] WP-M7 WorkflowSpecGraph edit/save/readback.
  Complete PV13 canvas graph edit, node configuration, save draft, refresh readback and WorkflowDiff review through BFF DTO routes.
- [x] WP-M8 Publish/run/human/evidence inline loop.
  Complete publish, run, StationRun inspect, Human Gate approve/reject and Evidence Review as one PV13 workbench path.
- [x] WP-M9 Three business scenario artifact closure.
  Produce auditable document summary, code review and meeting brief artifacts with input hash, quality refs, human review refs and redaction refs.
- [x] WP-M10 Frontend quality and failure-state gate.
  Cover loading, empty, error, permission denied, BFF offline, validation failure, human reject, cancel/retry, keyboard, responsive, a11y and performance evidence.
- [x] WP-M11 Aggregate frontend completion audit.
  Map WP-FR-1 through WP-FR-20 to evidence and generate a human-readable Chinese HTML audit report. Only this stage may allow the bounded claim `PRD-defined frontend functionality complete for bounded review`.
- [x] Path C-R0: Knowledge OPC productization documentation.
  Selected Knowledge as the first business domain and completed the document package needed for implementation review.
- [x] Path C-S1..SA: Knowledge OPC productization implementation.
  Promote `packs/knowledge` from reference pack baseline into a bounded, browser-reviewable OPC business flow with BFF DTOs, citation/quality/evidence gates, platform generality review and acceptance runner evidence. Knowledge OPC must validate the workflow platform without introducing Knowledge-only core/runtime/Gateway/App shell customization.
- [x] PV19-R0 documentation target: Runtime Workflow Platform Closed Loop.
  Defined the stage as a bounded platform closed loop: workbench orchestration -> WorkflowDiff -> publish WorkflowVersion -> runtime-backed WorkflowInstance -> human interaction -> evidence review.
- [x] PV19-S1..SA implementation and acceptance.
  Implemented formal `/bff/pv19/*` DTOs, browser workbench path, backend acceptance runner and Chrome CDP screenshot evidence for bounded review.
- [x] PV20-R0 planning and readiness audit: Complete Agent Executor.
  Defined the governed Agent executor contract, architecture, task matrix, acceptance gate and high-risk audit before implementation. PV20 must preserve workflow platform generality and must not grant unrestricted agent mutation authority.
- [x] PV20-S1 Agent execution contract/read model.
  Implemented formal `/bff/pv20/*` state/contract/evidence read routes, bound AgentExecutionEnvelope to WorkflowInstance / StationRun, and generated acceptance evidence. This does not execute tool, skill or MCP calls.
- [x] PV20-S2 allowlisted skill/read-model execution.
  Implemented governed bundled skill/read-model execution with user confirmation, StationRun metadata readback, artifact ref and no MCP/tool refs.
- [x] PV20-S3A allowlisted local tool execution.
  Implemented a governed read-only artifact metadata tool with user confirmation, route boundary, StationRun readback and no MCP refs.
- [x] PV20-S3B real MCP fixture execution.
  Implemented a governed local `data_service_mcp.knowledge_query_v2` stdio fixture path through `connector.submit`, `approval.respond`, retry context and StationRun readback.
- [x] PV20-S4 approval handoff and denied mutation fixtures.
  Added approval refs readback, source/user-confirmation denial fixtures and runner evidence for bounded review.
- [x] PV20-S5 timeout, cancel, retry and redaction fixtures.
  Added bounded retry-context, failed connector fixture, cancelled connector fixture and DTO redaction scan evidence in the PV20 runner.
- [x] PV20-S6 browser-visible Agent executor evidence path.
  Added `?studio=pv20-agent-executor`, PV20 BFF client methods, frontend DTO types, evidence page and frontend acceptance record.
- [x] PV21-S1..SA implementation and acceptance: Complete Workflow Studio bounded candidate.
  Added PV21 Studio entry, `/bff/pv21/*` routes, frontend DTO/client/page, graph save/validation/diff, version publish/rollback, runtime run, human gate, evidence summary, backend acceptance and Chrome CDP screenshot evidence. This remains a bounded candidate, not a GA/product-grade claim.
- [ ] Path D: Production governance hardening.
  Focus on tenant isolation, credential lifecycle, audit retention, deployment runbooks, smoke automation and operational recovery.

### P2 - Long-Range Backlog

- [x] Record accepted post-PV18 development route:
  PV19 Runtime-backed Workflow Studio Closed Loop -> Complete Agent Executor -> Complete Workflow Studio -> Path B external app contract -> Path D production governance hardening -> business Pack productization -> open-source / commercial readiness.
- [x] Complete Workflow Studio bounded candidate versioning, publish/run/rollback and audit loop.
- [x] Complete Agent Executor bounded review path through PV20-S6.
  This is a bounded review completion only; it does not permit production-ready, unrestricted automation or complete Workflow Studio claims.
- [x] Complete Workflow Studio bounded candidate implementation for PV21.
  This proves a bounded candidate closed loop only; it does not permit production-ready, product-grade frontend or complete Workflow Studio GA claims.
- [x] External App Contract bounded implementation package for PV22.
  This proves a bounded external app contract integration review path only; it does not prove production readiness, external ecosystem completion, commercial readiness or unrestricted third-party app access.
- [ ] Productize Meeting / Knowledge / Interview / Investment / Video Studio as real business apps.
- [ ] External plugin / skill / tool / MCP ecosystem examples and compatibility policy.
- [ ] Open-source / commercial readiness: contributor docs, release pipeline, license/CLA, deployment docs and billing / rate-limit strategy.

## Archived Legacy Plan Mapping

旧 Phase 计划保留为历史语境，不再作为当前实施顺序。若重新启用其中任务，必须在新的 stage plan 中承接。

| Legacy area | Current mapping |
| --- | --- |
| Phase 0 foundation | Mostly covered by Gateway protocol, API server, CLI and V3.0 Core baseline. Remaining item: verify local dependency environment and CI smoke. |
| Phase 1 Meeting / Interview / Knowledge MVP | Meeting / Knowledge are reference packs; Interview remains planned/stub. Treat as business pack productization backlog, not Core blocker. |
| Phase 2 production and governance | Partially covered by V3.0 governance and V12-V15/PV16 bounded evidence. Full tenant, credential, audit retention, deployment and SLA work remains backlog. |
| Phase 3 multi-agent automation | Several later V4-V11 slices exist as bounded evidence, but complete Agent executor and production multi-agent automation remain backlog. |
| Phase 4 local video workflow | Video Studio planning artifacts exist; real media execution, render polling, retry and batch production remain backlog. |
| Phase 5-C / 5-D MCP integration | V3.0 closeout says FunASR / data_service / Meeting-to-Knowledge validation passed. Keep as regression, not active unfinished mainline. |
| Phase 5 open-source / commercial readiness | Still backlog; should be re-planned as a separate stage with concrete release and documentation gates. |

## No-Go

- Do not claim HarnessOS is production ready.
- Do not claim Xpert parity complete.
- Do not claim product-grade frontend complete.
- Do not claim complete Workflow Studio ready.
- Do not claim Agent executor ready.
- Do not treat docs, screenshots, content images or presentation pages as runtime / BFF / DTO / browser E2E / production evidence.
- Do not customize the generic workflow platform for Knowledge OPC; Knowledge-specific behavior must stay inside the pack/domain BFF/view/runner boundary or be abstracted as reusable platform capability.

## Current Default Next Step

PV17 Product Closed Loop, PV18 Knowledge OPC Productization, PV19 Runtime Workflow Platform Closed Loop, PV20-S1 through PV20-S6, PV21 Complete Workflow Studio bounded candidate, WP-M1A through WP-M5A Workflow Platform PV13 baseline main-entry/business-scenario bounded implementation, WP-M5B readiness refresh, PV22 External App Contract bounded implementation, and WP-M6 through WP-M11 PRD-defined frontend functionality completion have passed their current bounded review acceptance. The current default next step is stage-audit closeout and then a user-selected follow-up stage such as Path D production governance hardening, business Pack productization, or open-source/commercial readiness. Do not treat any bounded review evidence as production readiness, final productized business-app completion, complete platform GA evidence, external ecosystem completion, unrestricted third-party app access or product-grade frontend completion.
