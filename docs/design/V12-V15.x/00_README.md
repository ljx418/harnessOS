# HarnessOS V12-V15 Canonical Index

## Purpose

This package defines the post-V11 roadmap for closing the gap with Xpert-level
frontend interaction and productization.

Target gaps:

- Gap 1: Full product frontend and Studio experience.
- Gap 2: Product-grade Agent/Station entity model.
- Gap 3: Workflow DSL and visual workflow authoring.
- Gap 5: Plugin, Skill, Tool and MCP ecosystem.
- Gap 7: Product observability, tracing, metrics and evidence operations.
- Gap 8: Self-hosting, deployment and operations baseline.

## Feasibility Statement

Technically feasible, but only as a staged roadmap. HarnessOS already has
Gateway, workflow runtime slices, controlled executor boundaries, evidence
packages and Mission TUI foundations. The missing work is productization:
durable product entities, Studio UI, visual DSL, plugin lifecycle,
observability and deployable operations.

## Current Baseline

- V11 complete: real-time explainable Mission TUI interaction baseline ready
  for review.
- V11 remains bounded. It does not prove production ready, complete Workflow
  Studio ready, Agent executor ready, Xpert parity complete, unrestricted
  terminal automation or production deployment readiness.
- Xpert has been cloned and deployed locally as a reference product. The
  reference audit is recorded in `v12_to_v15_xpert_reference_audit.md`.
- A focused Xpert Studio canvas survey was completed and recorded under
  `evidence/xpert-reference/canvas-survey/`. It shows that Xpert's canvas
  experience is a full workbench made of navigation, entity sidebar, infinite
  canvas, node inspector, add menu, auto-layout, preview and publish controls.
- The roadmap has been recalibrated in
  `v12_to_v15_canvas_plan_recalibration.md`: V12 must now include a browser
  workbench shell and read-only canvas foundation, while V13 owns editable
  Workflow Studio and visual DSL.
- V12 browser implementation now uses a shadcn-style component foundation in
  `apps/workflow-console`: Radix primitives, Tailwind utilities, CVA,
  tailwind-merge, clsx, lucide-react and the existing XyFlow canvas. This
  reduces bespoke UI tuning while preserving HarnessOS evidence and BFF
  boundaries.
- The V12 browser surface is an engineering-quality, bounded review baseline,
  not a finished product experience. The product polish, interaction depth,
  editable canvas, extension lifecycle, observability and deployment gaps are
  tracked in `v12_to_v15_experience_gap_closure_plan.md`.
- The accepted V12 baseline proves a reviewable V12-0P product experience
  direction plus a real-data, BFF-shaped, read-only workbench foundation. The
  accepted evidence is recorded under
  `evidence/v12-gemini-generated-light-studio-review/`,
  `evidence/v12-current-stage-real-data/`,
  `evidence/v12-sd-chat-workflowdiff/`,
  `evidence/v12-si-interaction-depth/`,
  `evidence/v12-sq-product-polish/` and
  `evidence/v12-sa-aggregate/`.
- The current bounded project status is: V12 complete for product entity,
  browser workbench and read-only canvas foundation ready for review. This does
  not prove editable Studio, runtime execution, Xpert parity, product-grade
  frontend completion or production readiness.
- V13 editable Workflow Studio pilot implementation has passed bounded
  acceptance. The accepted evidence is recorded under
  `evidence/v13-workflow-studio-pilot/`, and the aggregate result is recorded
  in `reports/v13_workflow_studio_acceptance_report.json`. The V13 result
  proves an editable Studio pilot slice for review only. It does not prove
  complete Workflow Studio readiness, runtime execution, product-grade frontend
  completion, Xpert parity or production readiness.
- V14 governed extension ecosystem pilot implementation has passed bounded
  acceptance. The accepted evidence is recorded under
  `evidence/v14-extension-ecosystem/`, and the aggregate result is recorded in
  `reports/v14_extension_ecosystem_acceptance_report.json`. The V14 result
  proves scoped extension inspection, compatibility decisions, activation,
  binding and unsafe denial for review only. It does not prove unrestricted
  marketplace or production plugin runtime readiness.
- V15 observability, deployment and final interaction baseline implementation
  has passed bounded acceptance. The accepted evidence is recorded under
  `evidence/v15-observability-deployment/`, and the aggregate result is
  recorded in `reports/v15_observability_deployment_acceptance_report.json`.
  The V15 result supports frontend interaction baseline ready for review only.
  It does not prove production GA, Xpert parity, product-grade frontend
  completion, complete Workflow Studio readiness or Agent executor readiness.
- The post-V15 PV16 product-runtime hardening pilot has passed bounded
  acceptance. PV16 is a separate stage because the target PRD contains durable
  mutation, runtime-backed run/inspect and self-hosting hardening outcomes that
  V15 does not prove.
- The selected post-PV16 next stage was PV17 Product Closed Loop. PV17 has
  passed bounded review acceptance for one mainline product path:
  setup -> Product Console -> Mission Studio -> confirm run -> inspect ->
  evidence. PV17 evidence does not change the bounded claims for V12-V15/PV16
  and does not prove production readiness, complete Workflow Studio or Agent
  executor readiness.
- The selected post-PV17 next stage was PV18 Knowledge OPC Productization.
  PV18 selected Path C business pack productization and locked Knowledge as the
  first business domain. PV18 has passed bounded review acceptance with
  `/bff/pv18/knowledge/*`, browser Knowledge OPC workflow, real
  `data_service_mcp` evidence, screenshots and acceptance runner output. It
  does not prove production readiness, complete Workflow Studio, complete Agent
  executor or full commercial Knowledge productization.
- PV19 Runtime Workflow Platform Closed Loop has passed bounded review
  acceptance. It proves a bounded platform loop covering workbench
  orchestration, WorkflowDiff, publish WorkflowVersion, runtime-backed
  WorkflowInstance, human interaction and evidence review.
- PV20 Complete Agent Executor bounded review path has passed through S6. It
  proves a governed executor review path only and does not prove production
  readiness, unrestricted automation or complete Studio implementation.
- PV21 Complete Workflow Studio bounded candidate has passed bounded
  acceptance. It proves default Studio entry, BFF DTO boundary,
  graph save/validate/diff, publish/rollback, runtime run, human gate and
  evidence review for bounded review only.
- PV22 External App Contract documentation/readiness is complete. It defines
  SDK, BFF template, reference app, capability token and registry targets, but
  does not prove implementation evidence.
- The current product-entry alignment target is WP-M0 Workflow Platform Main
  Entry. WP-M0 documents that subsequent implementation should make the
  workflow platform the first product entry before PV22 implementation becomes
  the default next step. WP-M0 documents are not implementation evidence.
- V12 design now starts with component-level prototype review before full Figma
  or real browser implementation. The required component sketch gate is defined
  in `v12_component_prototype_plan.md`; execution details, evidence paths and
  per-component acceptance are defined in
  `v12_component_prototype_execution_plan.md`.
- This V12-V15 package is the accepted staged planning and target architecture
  baseline for bounded productization review. The current selected alignment
  target is WP-M0 Workflow Platform Main Entry.

## Allowed Planning Claim

V12-V15 planning complete: staged product experience and frontend interaction baseline roadmap ready for review.

## Allowed V15 Claim

V15 complete: frontend interaction baseline ready for review.

## Allowed PV16 Claim

PV16 complete: product-runtime hardening pilot ready for review.

## Allowed PV17 Claim

PV17 complete: product closed loop implementation ready for bounded review.

## Allowed PV18 Claim

PV18 complete: Knowledge OPC productization implementation ready for bounded review.

## Allowed PV19 Planning Claim

PV19 planning complete: runtime workflow platform closed loop development plan ready for implementation review.

## Allowed PV20 Bounded Review Claim

PV20 bounded review path complete through S6: governed Agent executor candidate evidence ready for bounded review.

## Allowed PV21 Planning Claim

PV21 planning complete: complete Workflow Studio candidate development plan ready for implementation review.

## Allowed WP-M0 Documentation Claim

WP-M0 complete: Workflow Platform main-entry documentation ready for implementation review.

## Forbidden Interpretations

- Xpert parity complete
- production ready
- full production GA
- complete Workflow Studio ready
- Agent executor ready
- unrestricted plugin ecosystem ready
- production deployment ready
- observability production complete
- autonomous workflow editing ready
- PV19 expanded into production or complete platform implementation
- runtime workflow platform closed loop complete without evidence
- 已完全追平 Xpert
- 生产可用
- 完整工作流工作台已完成
- Agent 执行器已完成
- WP-M0 文档证明工作流平台实现完成
- PV22 文档证明外部接入实现完成

## Canonical Documents

- `v12_to_v15_xpert_reference_audit.md`
- `v12_to_v15_canvas_plan_recalibration.md`
- `v12_to_v15_target_prd.md`
- `v12_to_v15_target_architecture.md`
- `v12_to_v15_development_and_acceptance_plan.md`
- `v12_to_v15_milestone_roadmap.md`
- `v12_to_v15_acceptance_gate.md`
- `v12_to_v15_interaction_experience_acceptance_plan.md`
- `v12_to_v15_automated_ux_test_matrix.md`
- `v12_to_v15_experience_gap_closure_plan.md`
- `v12_to_v15_current_gap_analysis.md`
- `v12_to_v15_current_gap_analysis.drawio`
- `v12_to_v15_no_false_green_claim_guard.md`
- `v12_to_v15_document_audit.md`
- `v12_current_design_readiness_audit.md`
- `v12_figma_prototype_review_plan.md`
- `v12_component_prototype_plan.md`
- `v12_component_prototype_execution_plan.md`
- `v12_0p_high_fidelity_prototype_plan.md`
- `v12_0p_component_design_decision_record.md`
- `v12_current_stage_acceptance_and_development_plan.md`
- `v12_current_stage_prd_spec_review.md`
- `v12_current_stage_audit_opinion.md`
- `v12_current_stage_audit_closure.md`
- `v12_remaining_stage_development_and_acceptance_plan.md`
- `v12_remaining_stage_prd_architecture_coverage_audit.md`
- `v12_sa_aggregate_validator_spec.md`
- `v12_to_v15_stage_document_support_audit_2026_06_24.md`
- `v13_implementation_readiness_audit.md`
- `v13_development_and_acceptance_plan.md`
- `v13_prd_architecture_coverage_audit.md`
- `v13_post_implementation_audit.md`
- `v14_v15_remaining_stage_development_and_acceptance_plan.md`
- `v14_development_and_acceptance_plan.md`
- `v14_implementation_readiness_audit.md`
- `v14_prd_architecture_coverage_audit.md`
- `v15_implementation_readiness_audit.md`
- `v15_prd_architecture_coverage_audit.md`
- `v14_v15_evidence_runner_spec.md`
- `post_v15_next_stage_development_and_acceptance_plan.md`
- `post_v15_prd_architecture_coverage_audit.md`
- `post_v15_acceptance_runner_spec.md`
- `post_pv18_runtime_platform_development_route.md`
- `pv19_runtime_workflow_platform_prd.md`
- `pv19_runtime_workflow_platform_target_architecture.md`
- `pv19_runtime_workflow_platform_development_and_acceptance_plan.md`
- `pv19_runtime_workflow_platform_milestone_roadmap.md`
- `pv19_runtime_workflow_platform_acceptance_gate.md`
- `pv19_runtime_workflow_platform_current_gap_analysis.md`
- `pv19_runtime_workflow_platform_bff_dto_contract.md`
- `pv19_runtime_workflow_platform_implementation_task_matrix.md`
- `pv19_runtime_workflow_platform_acceptance_runner_spec.md`
- `pv19_runtime_workflow_platform_implementation_readiness_audit.md`
- `pv19_runtime_workflow_platform_document_support_audit.md`
- `pv19_runtime_workflow_platform_gap_analysis.drawio`
- `pv20_complete_agent_executor_prd.md`
- `pv20_complete_agent_executor_target_architecture.md`
- `pv20_complete_agent_executor_development_and_acceptance_plan.md`
- `pv20_complete_agent_executor_acceptance_gate.md`
- `pv20_complete_agent_executor_implementation_task_matrix.md`
- `pv20_complete_agent_executor_implementation_readiness_audit.md`
- `pv21_complete_workflow_studio_prd.md`
- `pv21_complete_workflow_studio_target_architecture.md`
- `pv21_complete_workflow_studio_bff_dto_contract.md`
- `pv21_complete_workflow_studio_acceptance_runner_spec.md`
- `pv21_complete_workflow_studio_development_and_acceptance_plan.md`
- `pv21_complete_workflow_studio_milestone_roadmap.md`
- `pv21_complete_workflow_studio_acceptance_gate.md`
- `pv21_complete_workflow_studio_current_gap_analysis.md`
- `pv21_complete_workflow_studio_implementation_task_matrix.md`
- `pv21_complete_workflow_studio_implementation_readiness_audit.md`
- `pv21_complete_workflow_studio_document_support_audit.md`
- `pv21_complete_workflow_studio_gap_analysis.drawio`
- `workflow_platform_main_entry_prd.md`
- `workflow_platform_main_entry_target_architecture.md`
- `workflow_platform_main_entry_bff_dto_contract.md`
- `workflow_platform_main_entry_development_and_acceptance_plan.md`
- `workflow_platform_main_entry_acceptance_runner_spec.md`
- `workflow_platform_main_entry_milestone_roadmap.md`
- `workflow_platform_main_entry_acceptance_gate.md`
- `workflow_platform_main_entry_current_gap_analysis.md`
- `workflow_platform_main_entry_implementation_task_matrix.md`
- `workflow_platform_main_entry_implementation_readiness_audit.md`
- `workflow_platform_main_entry_document_support_audit.md`
- `workflow_platform_main_entry_gap_analysis.drawio`
- `post_v15_implementation_readiness_audit.md`
- `pv17_product_closed_loop_prd.md`
- `pv17_product_closed_loop_target_architecture.md`
- `pv17_product_closed_loop_bff_dto_contract.md`
- `pv17_product_closed_loop_implementation_task_matrix.md`
- `pv17_product_closed_loop_development_and_acceptance_plan.md`
- `pv17_product_closed_loop_acceptance_runner_spec.md`
- `pv17_product_closed_loop_milestone_roadmap.md`
- `pv17_product_closed_loop_acceptance_gate.md`
- `pv17_product_closed_loop_current_gap_analysis.md`
- `pv17_product_closed_loop_implementation_readiness_audit.md`
- `pv17_product_closed_loop_gap_analysis.drawio`
- `pv18_knowledge_opc_productization_prd.md`
- `pv18_knowledge_opc_productization_target_architecture.md`
- `pv18_knowledge_opc_productization_development_and_acceptance_plan.md`
- `pv18_knowledge_opc_productization_bff_dto_contract.md`
- `pv18_knowledge_opc_productization_acceptance_runner_spec.md`
- `pv18_knowledge_opc_productization_implementation_task_matrix.md`
- `pv18_knowledge_opc_productization_milestone_roadmap.md`
- `pv18_knowledge_opc_productization_acceptance_gate.md`
- `pv18_knowledge_opc_productization_current_gap_analysis.md`
- `pv18_knowledge_opc_productization_implementation_readiness_audit.md`
- `pv18_knowledge_opc_productization_gap_analysis.drawio`
- `schemas/pv18_knowledge_opc_acceptance_data.schema.json`
- `schemas/pv18_knowledge_opc_artifact_manifest.schema.json`
- `schemas/pv18_knowledge_opc_dto_snapshot.schema.json`

## V12 Implementation-Readiness Documents

- `v12_implementation_readiness_plan.md`
- `v12_product_entity_and_workbench_contracts.md`
- `v12_bff_route_and_browser_boundary.md`
- `v12_evidence_and_user_acceptance_plan.md`
- `v12_figma_prototype_review_plan.md`
- `v12_component_prototype_plan.md`
- `v12_component_prototype_execution_plan.md`

## V12 Machine-Readable Audit Artifacts

- `schemas/v12_product_entity_projection.schema.json`
- `schemas/v12_canvas_read_model.schema.json`
- `schemas/v12_browser_network_log.schema.json`
- `schemas/v12_acceptance_data.schema.json`
- `schemas/v12_component_prototype_review.schema.json`
- `schemas/v12_component_prototype_artifact_manifest.schema.json`
- `schemas/v12_remaining_stage_acceptance_data.schema.json`
- `schemas/v12_remaining_stage_artifact_manifest.schema.json`
- `schemas/v13_workflow_studio_acceptance_data.schema.json`
- `schemas/v13_workflow_studio_artifact_manifest.schema.json`
- `schemas/v14_extension_ecosystem_acceptance_data.schema.json`
- `schemas/v14_extension_ecosystem_artifact_manifest.schema.json`
- `schemas/v15_observability_deployment_acceptance_data.schema.json`
- `schemas/v15_observability_deployment_artifact_manifest.schema.json`
- `schemas/post_v15_product_runtime_hardening_acceptance_data.schema.json`
- `schemas/post_v15_product_runtime_hardening_artifact_manifest.schema.json`
- `fixtures/v12/product_entity_projection.sample.json`
- `fixtures/v12/canvas_read_model.sample.json`
- `fixtures/v12/browser_network_log.sample.json`
- `fixtures/v12/v12_acceptance_data.sample.json`
- `fixtures/v12/forbidden_direct_runtime_call.negative.json`
- `reports/v12_drawio_validation_report.json`
- `reports/v12_remaining_stage_fixed_document_report.json`
- `reports/v12_execution_name_scan_report.json`
- `reports/v13_document_support_audit_report.json`
- `reports/v13_workflow_studio_acceptance_report.json`
- `reports/v14_v15_document_support_audit_report.json`
- `reports/post_v15_document_support_audit_report.json`
- `evidence/v12-readiness/figma-prototype-url.txt`
- `evidence/v12-readiness/figma-prototype-review.md`
- `evidence/v12-component-prototype/index.html`
- `evidence/v12-component-prototype/xpert-style-concept-board.html`
- `evidence/v12-component-prototype/light-studio-component-detail-board.html`
- `evidence/v12-component-prototype/light-studio-annotated-component-sketches.html`
- `evidence/v12-component-prototype/component-prototype-review.md`
- `evidence/v12-component-prototype/component-prototype-review-data.json`
- `evidence/v12-component-prototype/artifact-manifest.json`
- `evidence/v12-component-prototype/component-prototype-schema-validation-report.json`
- `evidence/v12-component-prototype/static-render-report.json`
- `evidence/v12-component-prototype/xpert-style-concept-board.static-render-report.json`
- `evidence/v12-component-prototype/light-studio-component-detail-board.static-render-report.json`
- `evidence/v12-component-prototype/light-studio-annotated-component-sketches.static-render-report.json`
- `evidence/v12-component-prototype/validation-run-summary.json`
- `evidence/v12-component-prototype/index.html.png`
- `evidence/v12-component-prototype/xpert-style-concept-board.html.png`
- `evidence/v12-component-prototype/light-studio-component-detail-board.html.png`
- `evidence/v12-component-prototype/light-studio-annotated-component-sketches.html.png`
- `evidence/v12-component-prototype/prd-spec-review.md`
- `evidence/v12-component-prototype/v12-0a-acceptance-audit.md`
- `evidence/v12-component-prototype/v12-0a-ux-recheck.md`
- `evidence/v12-component-prototype/no-false-green-scan.txt`
- `evidence/v12-component-prototype/redaction-scan.txt`
- `evidence/v12-readiness/component-inventory-review.md`
- `evidence/v12-0p-high-fidelity-prototype/index.html`
- `evidence/v12-0p-high-fidelity-prototype/imag2-vs-html-comparison.html`
- `evidence/v12-0p-high-fidelity-prototype/imag2-vs-html-comparison.fullpage.png`
- `evidence/v12-0p-high-fidelity-prototype/index.html.png`
- `evidence/v12-0p-high-fidelity-prototype/prototype-review-data.json`
- `evidence/v12-0p-high-fidelity-prototype/artifact-manifest.json`
- `evidence/v12-0p-high-fidelity-prototype/prd-spec-review.md`
- `evidence/v12-0p-high-fidelity-prototype/v12-0p-acceptance-audit.md`
- `evidence/v12-0p-high-fidelity-prototype/no-false-green-scan.txt`
- `evidence/v12-0p-high-fidelity-prototype/redaction-scan.txt`
- `evidence/v12-0p-high-fidelity-prototype/static-render-report.json`
- `evidence/v12-gemini-generated-light-studio-review/index.html`
- `evidence/v12-gemini-generated-light-studio-review/styles.generated.css`
- `evidence/v12-gemini-generated-light-studio-review/index.local-render.png`
- `evidence/v12-gemini-generated-light-studio-review/validation-report.json`
- `evidence/v12-current-stage-real-data/v12-current-stage-acceptance-data.json`
- `evidence/v12-current-stage-real-data/v12-real-data-readonly-workbench.png`
- `evidence/v12-current-stage-real-data/bff-route-log.json`
- `evidence/v12-current-stage-real-data/browser-network-log.json`
- `evidence/v12-current-stage-real-data/schema-validation-report.json`
- `evidence/v12-current-stage-real-data/no-false-green-scan.txt`
- `evidence/v12-current-stage-real-data/redaction-scan.txt`
- `evidence/v12-sd-chat-workflowdiff/artifact-manifest.json`
- `evidence/v12-si-interaction-depth/artifact-manifest.json`
- `evidence/v12-sq-product-polish/artifact-manifest.json`
- `evidence/v12-sa-aggregate/artifact-manifest.json`

## V13-V15 Implementation-Readiness Documents

- `v13_workflow_studio_dsl_readiness_plan.md`
- `v13_implementation_readiness_audit.md`
- `v13_development_and_acceptance_plan.md`
- `v13_prd_architecture_coverage_audit.md`
- `v13_post_implementation_audit.md`
- `v14_v15_remaining_stage_development_and_acceptance_plan.md`
- `v14_development_and_acceptance_plan.md`
- `v14_implementation_readiness_audit.md`
- `v14_prd_architecture_coverage_audit.md`
- `v15_implementation_readiness_audit.md`
- `v15_prd_architecture_coverage_audit.md`
- `v14_v15_evidence_runner_spec.md`
- `v14_extension_ecosystem_readiness_plan.md`
- `v15_observability_deployment_readiness_plan.md`
- `post_v15_next_stage_development_and_acceptance_plan.md`
- `post_v15_prd_architecture_coverage_audit.md`
- `post_v15_implementation_readiness_audit.md`

## Stage Order

- V12: Product entity, browser workbench shell and read-only canvas foundation.
- V13: Editable Workflow Studio and visual DSL pilot slice.
- V14: Plugin, Skill, Tool and MCP ecosystem pilot.
- V15: Observability, deployment and frontend interaction baseline review.
- PV16: Product-runtime hardening pilot readiness and implementation evidence.
- PV17: Product Closed Loop bounded review.
- PV18: Knowledge OPC Productization bounded review.
- PV19: Runtime Workflow Platform Closed Loop bounded review.
- PV20: Complete Agent Executor bounded review path through S6.
- PV21: Complete Workflow Studio documentation/readiness; implementation remains pending.

## Current Go / No-Go

Go:

- V12-V15 planning audit.
- V12 accepted bounded baseline review: V12-0P high-fidelity direction,
  BFF-shaped browser workbench evidence, V12-SD/SI/SQ substage evidence and
  V12-SA aggregate reconciliation are ready for bounded review.
- V13 readiness planning using `v13_workflow_studio_dsl_readiness_plan.md`
  before editable Studio implementation starts.
- V13 accepted bounded implementation review: editable Workflow Studio pilot
  evidence, graph validation, browser interaction log, WorkflowDiff handoff,
  schema validation, claim scan and redaction scan are ready for bounded
  review.
- V14 readiness planning using `v14_extension_ecosystem_readiness_plan.md`
  before governed extension implementation starts.
- V15 readiness planning using
  `v15_observability_deployment_readiness_plan.md` before observability,
  deployment or final interaction baseline acceptance starts.
- PV16 product-runtime hardening bounded pilot review using
  `post_v15_next_stage_development_and_acceptance_plan.md`,
  `post_v15_prd_architecture_coverage_audit.md` and
  `post_v15_implementation_readiness_audit.md`, with accepted evidence under
  `evidence/post-v15-product-runtime-hardening/`.
- V12 implementation-readiness review using the V12 schema, browser workbench
  and read-only canvas contracts, BFF boundary, evidence and user acceptance
  contracts listed above.
- V12 Figma prototype review using `v12_figma_prototype_review_plan.md` before
  browser UI implementation starts.
- V12 component prototype review using `v12_component_prototype_plan.md` before
  full Figma prototype freeze or browser UI implementation starts.
- V12-0P high-fidelity prototype review using
  `v12_0p_high_fidelity_prototype_plan.md` and
  `evidence/v12-0p-high-fidelity-prototype/index.html` before V12
  implementation-readiness acceptance.
- V12-V15 interaction experience acceptance review using
  `v12_to_v15_interaction_experience_acceptance_plan.md`.

No-Go:

- Direct V13/V14/V15 implementation before the prior-stage evidence and
  stage-specific readiness review are accepted.
- Direct V12 implementation before the V12 implementation-readiness review
  accepts schema/DTO, canvas read-model, BFF route, browser denylist and
  evidence package contracts.
- Direct V12 browser UI implementation before the Figma prototype review is
  accepted.
- Direct V12 Figma freeze or browser UI implementation before the component
  prototype sketch report is accepted.
- Direct V13 implementation before the V13 readiness plan is accepted and V12
  entity/BFF/workbench/read-only-canvas evidence exists.
- Direct V14 implementation before the V14 readiness plan is accepted and
  V12/V13 evidence exists.
- Direct V15 final acceptance before the V15 readiness plan is accepted and
  V12-V14 evidence exists.
- Direct PV16 exit acceptance from planning documents alone, or before product
  mutation, runtime run/inspect, deployment hardening, UX hardening, PRD
  review, architecture review, audit closure, claim scan and redaction evidence
  all exist and validate.
- Xpert parity complete claim.
- Xpert-level UX complete or product-grade frontend complete claim.
- Production ready or full production GA claim.
- Complete Workflow Studio ready claim.
- Agent executor ready claim.
