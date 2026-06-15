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
- The current V12 browser prototype is still an engineering-quality surface,
  not a finished product experience. The remaining product polish, interaction
  depth, canvas maturity, prototype quality and goal-to-workflow loop gaps are
  tracked in `v12_to_v15_experience_gap_closure_plan.md`.
- V12 design now starts with component-level prototype review before full Figma
  or real browser implementation. The required component sketch gate is defined
  in `v12_component_prototype_plan.md`; execution details, evidence paths and
  per-component acceptance are defined in
  `v12_component_prototype_execution_plan.md`.
- This V12-V15 package is the current planning and target architecture package
  for Xpert-inspired productization.

## Allowed Planning Claim

V12-V15 planning complete: Xpert-level frontend interaction and productization roadmap ready for review.

## Allowed Future V15 Claim

V15 complete: Xpert-level frontend interaction baseline ready for review.

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
- 已完全追平 Xpert
- 生产可用
- 完整工作流工作台已完成
- Agent 执行器已完成

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
- `fixtures/v12/product_entity_projection.sample.json`
- `fixtures/v12/canvas_read_model.sample.json`
- `fixtures/v12/browser_network_log.sample.json`
- `fixtures/v12/v12_acceptance_data.sample.json`
- `fixtures/v12/forbidden_direct_runtime_call.negative.json`
- `reports/v12_drawio_validation_report.json`
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
- `evidence/v12-0p-high-fidelity-prototype/index.html.png`
- `evidence/v12-0p-high-fidelity-prototype/prototype-review-data.json`
- `evidence/v12-0p-high-fidelity-prototype/artifact-manifest.json`
- `evidence/v12-0p-high-fidelity-prototype/prd-spec-review.md`
- `evidence/v12-0p-high-fidelity-prototype/v12-0p-acceptance-audit.md`
- `evidence/v12-0p-high-fidelity-prototype/no-false-green-scan.txt`
- `evidence/v12-0p-high-fidelity-prototype/redaction-scan.txt`
- `evidence/v12-0p-high-fidelity-prototype/static-render-report.json`

## V13-V15 Implementation-Readiness Documents

- `v13_workflow_studio_dsl_readiness_plan.md`
- `v14_extension_ecosystem_readiness_plan.md`
- `v15_observability_deployment_readiness_plan.md`

## Stage Order

- V12: Product entity, browser workbench shell and read-only canvas foundation.
- V13: Editable Workflow Studio and visual DSL productization.
- V14: Plugin, Skill, Tool and MCP ecosystem.
- V15: Observability, deployment and Xpert-level frontend interaction baseline.

## Current Go / No-Go

Go:

- V12-V15 planning audit.
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

- Direct V13/V14/V15 implementation before V12 evidence exists.
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
- Xpert parity complete claim.
- Xpert-level UX complete or product-grade frontend complete claim.
- Production ready or full production GA claim.
- Complete Workflow Studio ready claim.
- Agent executor ready claim.
