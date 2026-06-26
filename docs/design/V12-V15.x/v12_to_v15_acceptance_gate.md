# V12-V15 Acceptance Gate

## Final Allowed Claim

V15 complete: frontend interaction baseline ready for review.

## Required Final Evidence

- Xpert reference audit exists and is marked planning/reference evidence only.
- V12 implementation-readiness documents exist and are accepted before V12
  implementation evidence is counted.
- V13/V14/V15 implementation-readiness documents exist and are accepted before
  their implementation or final evidence is counted.
- V13 implementation-readiness audit exists, has no open fatal or major
  findings, and accepts the V13 evidence schema before V13 implementation
  starts.
- V12 product entity evidence package exists and PASS.
- V12 component prototype review package exists and PASS before Figma or
  browser implementation evidence is counted.
- V12 current-stage read-only real-data evidence package exists and PASS.
- V12-SD, V12-SI, V12-SQ and V12-SA evidence packages exist and PASS before the
  bounded V12 exit claim is used.
- V13 Studio/DSL pilot evidence package exists and PASS.
- V13 post-implementation audit exists and confirms the accepted bounded V13
  claim without runtime execution or complete Studio overclaim.
- V14 plugin/skill/tool/MCP evidence package exists and PASS.
- V15 observability/deployment evidence package exists and PASS.
- Browser onboarding / product shell screenshot exists.
- HarnessOS browser canvas/workbench shell screenshot exists.
- Product polish evidence exists: desktop screenshot, constrained-width
  screenshot, component inventory review and human UX review.
- Interaction trace evidence exists: node selection, inspector update, disabled
  action reason, add-menu placeholder and goal-to-proposal-to-canvas path.
- Canvas read-model DTO and selected-node inspector evidence exist.
- Frontend/API health configuration evidence exists.
- Browser E2E screenshots exist for key Studio paths.
- Interaction evidence packages exist for V12-V15 with automated UX checks and
  human review results.
- BFF route allowlist and browser denylist PASS.
- WorkflowSpec graph round-trip PASS.
- Plugin compatibility and unsafe-plugin denial PASS.
- Metrics, trace and audit export PASS.
- Deployment smoke PASS.
- No False Green scan PASS.
- Redaction scan PASS.
- Drawio XML valid.

## Stage Evidence Package Minimums

| Stage | Required Package | Minimum Contents |
| --- | --- | --- |
| V12 readiness | `docs/design/V12-V15.x/v12_*readiness/contracts/acceptance docs` | Product entity contracts, BFF route allowlist, browser denylist, evidence package format, user scenario matrix. |
| V12 design | `evidence/v12-component-prototype/` | Component sketch HTML report, first-batch component sketches, schema-valid review data, artifact manifest with hashes, reviewer decisions, design-only evidence scope, No False Green and redaction checks. |
| V12 design | `evidence/v12-gemini-generated-light-studio-review/` | V12-0P optimized prototype, local CSS, static render screenshot, validation report, artifact manifest, audit notes, design-only scope and dependency reduction notes. |
| V12 current subgate | `evidence/v12-current-stage-real-data/` | Live browser screenshot, BFF route log, browser network log, ProductEntityProjection, CanvasReadModel, CanvasInspectorProjection, schema validation, PRD review, No False Green scan and redaction scan. |
| V12 remaining plan | `v12_remaining_stage_development_and_acceptance_plan.md` | V12-SD, V12-SI, V12-SQ and V12-SA user-visible outcomes, route/DTO/evidence requirements, PRD review loop, audit closure loop and stop conditions. |
| V12 remaining coverage audit | `v12_remaining_stage_prd_architecture_coverage_audit.md` | PRD scenario coverage, target architecture plane coverage, remaining development outline, evidence package minimums and blocking risks. |
| V12 remaining schemas | `schemas/v12_remaining_stage_acceptance_data.schema.json` and `schemas/v12_remaining_stage_artifact_manifest.schema.json` | Machine-checkable acceptance-data and artifact-manifest contracts for V12-SD, V12-SI, V12-SQ and V12-SA. |
| V12-SA validator | `v12_sa_aggregate_validator_spec.md` | Aggregation rules for missing evidence, design-only misuse, Xpert reference misuse, claim-to-evidence mapping and allowed V12-SA exit claim. |
| V12 remaining fixed reports | `reports/v12_remaining_stage_fixed_document_report.json`, `reports/v12_execution_name_scan_report.json`, `reports/v12_drawio_validation_report.json` | Independent fixed-document hash report, execution-name migration scan and drawio XML/hash report. |
| V12 accepted bounded baseline | `evidence/v12-sd-chat-workflowdiff/`, `evidence/v12-si-interaction-depth/`, `evidence/v12-sq-product-polish/`, `evidence/v12-sa-aggregate/` | Chat proposal handoff, interaction feedback, product polish review, aggregate claim-to-evidence mapping, PRD review, audit closure, schema validation, No False Green scan and redaction scan. |
| V12 | `evidence/v12-product-entity/` | Schemas, BFF route logs, browser screenshots, entity audit refs, ownership denial cases, redaction scan. |
| V12 | `evidence/v12-workbench-foundation/` | Onboarding screenshot, frontend/API health, workbench transcript, proposal timeline, browser denylist log. |
| V12 | `evidence/v12-canvas-foundation/` | Read-only canvas DTO, browser canvas screenshot, selected-node inspector screenshot, BFF-only network log, explicit non-editable Studio scope. |
| V12 | `evidence/v12-product-polish/` | Desktop and constrained screenshots, component inventory review, visual hierarchy assertions, node card legibility review, human UX review. |
| V12 | `evidence/v12-interaction-depth/` | Playwright action log, selected-node DTO snapshot, inspector update evidence, disabled action reason screenshot, goal-to-proposal-to-canvas trace. |
| V13 readiness | `v13_workflow_studio_dsl_readiness_plan.md` | Studio/DSL schemas, BFF routes, graph validation rules, graph fixtures, user scenarios. |
| V13 readiness audit | `v13_implementation_readiness_audit.md` | Blocking readiness decision, V12 dependency check, PRD scope check, target architecture boundary check, route allowlist, evidence contract, No False Green and redaction controls. |
| V13 development plan | `v13_development_and_acceptance_plan.md` | V13-R0, V13-S1, V13-S2, V13-S3 and V13-SA development slices, acceptance criteria, evidence package minimums and stop conditions. |
| V13 coverage audit | `v13_prd_architecture_coverage_audit.md` | PRD scenario coverage, target architecture plane coverage, positive-claim evidence mapping and blocking risks. |
| V13 schemas | `schemas/v13_workflow_studio_acceptance_data.schema.json` and `schemas/v13_workflow_studio_artifact_manifest.schema.json` | Machine-checkable V13 acceptance data and artifact manifest contracts. |
| V13 accepted pilot | `evidence/v13-workflow-studio-pilot/` | Studio screenshots, node inspector screenshot, WorkflowSpecGraph, WorkflowDiffProposal, graph round-trip report, browser network log, BFF route log, confirmation transcript, add/configure/move/connect action trace, PRD review, architecture review, audit closure, No False Green and redaction scans. |
| V14 readiness | `v14_extension_ecosystem_readiness_plan.md` | Manifest schemas, compatibility resolver, scoped activation rules, unsafe denial fixtures. |
| V14 remaining plan | `v14_v15_remaining_stage_development_and_acceptance_plan.md` | V14-R0/S1/S2/S3/SA development slices, user-visible outcomes, required evidence, acceptance criteria and stop conditions. |
| V14 development plan | `v14_development_and_acceptance_plan.md` | Concrete V14 BFF routes, DTO fixtures, frontend states, real-data requirement, evidence package layout, runner behavior and verification commands. |
| V14 schemas | `schemas/v14_extension_ecosystem_acceptance_data.schema.json` and `schemas/v14_extension_ecosystem_artifact_manifest.schema.json` | Machine-checkable V14 acceptance data and artifact manifest contracts before implementation evidence is counted. |
| V14 implementation audit | `v14_implementation_readiness_audit.md` and `v14_prd_architecture_coverage_audit.md` | Entry decision, PRD coverage, architecture plane coverage, evidence-to-claim mapping and blocking risks. |
| V14 | `evidence/v14-extension-ecosystem/` | Plugin/skill manifests, compatibility decisions, scoped activation refs, unsafe denial fixtures, tool/MCP capability decisions. |
| V15 readiness | `v15_observability_deployment_readiness_plan.md` | Observability DTOs, deployment smoke contract, health diagnostics, final scenario matrix. |
| V15 remaining plan | `v14_v15_remaining_stage_development_and_acceptance_plan.md` | V15-R0/S1/S2/S3/SA development slices, user-visible outcomes, required evidence, acceptance criteria and stop conditions. |
| V15 schemas | `schemas/v15_observability_deployment_acceptance_data.schema.json` and `schemas/v15_observability_deployment_artifact_manifest.schema.json` | Machine-checkable V15 acceptance data and artifact manifest contracts before implementation evidence is counted. |
| V15 implementation audit | `v15_implementation_readiness_audit.md`, `v15_prd_architecture_coverage_audit.md` and `reports/v15_document_support_audit_report.json` | Entry decision after V14 PASS, PRD coverage, architecture plane coverage, evidence-to-claim mapping and blocking risks. |
| V15 | `evidence/v15-observability-deployment/` | Trace timeline, metrics snapshot, audit export, incident refs, compose smoke output, health check results, final scenario matrix. |
| PV16 readiness | `post_v15_next_stage_development_and_acceptance_plan.md`, `post_v15_prd_architecture_coverage_audit.md`, `post_v15_implementation_readiness_audit.md` | Product-runtime hardening scope, PRD/architecture coverage, route-boundary rules, schemas, runner behavior and stop conditions with no open fatal or major findings. |
| PV16 schemas and runner | `schemas/post_v15_product_runtime_hardening_acceptance_data.schema.json`, `schemas/post_v15_product_runtime_hardening_artifact_manifest.schema.json`, `tools/post_v15/run_product_runtime_hardening_acceptance.py` | Machine-checkable PV16 acceptance data and artifact manifest contracts plus runner rules for missing evidence, schema validation, route denylist, claim scan and redaction scan. |
| PV16 | `evidence/post-v15-product-runtime-hardening/` | Entity CRUD report, runtime run inspect report, deployment smoke output, deployment health report, UX hardening report, PRD review, architecture review, audit closure, claim-to-evidence matrix, No False Green scan and redaction scan. |
| V14-V15 runner spec | `v14_v15_evidence_runner_spec.md` | Required future runner behavior, artifact generation, schema validation, route boundary checks, claim scan and redaction scan rules. |
| V12-V15 UX | `evidence/v12-v15-interaction-experience/` | Playwright action logs, screenshots, network logs, DTO snapshots, UI copy scan, redaction scan, human review checklist. |
| V12-V15 UX test matrix | `v12_to_v15_automated_ux_test_matrix.md` | Required automated checks, user actions, expected evidence and blocking failures per stage. |

## Evidence Classification

| Evidence Type | Can Satisfy Final V15? | Notes |
| --- | --- | --- |
| Browser E2E with screenshots | yes | Required for Studio and product console UX. |
| Automated UX checks | yes | Required for visibility, state feedback, disabled-action reason and network denylist. |
| Human UX review | yes | Required for product clarity and interaction quality. |
| API/BFF test logs | yes | Required for route boundary and entity mutation. |
| Runtime workflow evidence | yes | Required for run/inspect scenarios. |
| Plugin lifecycle fixture | yes, bounded | Must include deny cases. |
| Observability smoke | yes | Must include trace/metrics/audit refs. |
| Xpert reference screenshot | no | Planning/reference evidence only. |
| Component sketch / HTML prototype report | no | Design review evidence only; cannot satisfy browser, BFF or runtime evidence. |
| Current V12 read-only BFF-shaped workbench evidence | bounded | Can satisfy the current V12 read-only foundation subgate; cannot satisfy editable Studio, runtime execution or final V15 acceptance by itself. |
| V12-SD/SI/SQ/SA evidence | bounded | Can support the bounded V12 exit claim for product entity, browser workbench and read-only canvas foundation ready for review; cannot satisfy V13 editable Studio, V14 extension or V15 production/runtime claims. |
| Documentation only | no | Cannot satisfy implementation acceptance. |
| Concept images | no | Planning only. |

## User Scenario Acceptance Matrix

| Scenario | PASS Condition | Blocking Failure |
| --- | --- | --- |
| Small studio project setup | User creates workspace/project/app and sees product inventory with audit refs. | Entity exists only in fixture docs or bypasses BFF ownership checks. |
| Product onboarding | User reaches browser onboarding/product shell and system status is available. | Frontend/API mismatch is visible or unresolved while smoke claims PASS. |
| Component prototype review | User reviews first-batch components before full-page Figma or implementation. | Full Figma or implementation starts before component decisions are accepted. |
| Browser canvas foundation | User opens HarnessOS workbench canvas shell, sees entity sidebar, node cards and inspector foundation from BFF DTOs. | Canvas evidence is static/drawio/Xpert reference only or browser bypasses BFF. |
| Current V12 read-only real-data gate | User opens the V12 workbench and sees BFF-shaped workspace/project/app/station-agent/canvas/inspector data reflected in the UI with disabled reasons for unavailable actions. | Route log does not show `/bff/v12/*`, schemas fail, screenshot is static-only, raw secret appears or the UI claims publish/run/edit readiness. |
| Product polish hardening | User can understand the active workspace/project/app, available actions, disabled reasons and evidence surface from a coherent product shell. | UI remains unreadable engineering prototype, lacks responsive evidence or has no human UX review. |
| Canvas interaction clarity | User selects nodes, sees inspector updates and receives visible reasons for unavailable add/layout/publish/run actions. | Clicks silently no-op, inspector is stale or disabled actions have no reason. |
| Chat workbench to Studio handoff | User discusses a goal, receives proposal timeline and opens WorkflowDiff in Studio. | Chat transcript is treated as runtime execution or bypasses WorkflowDiff. |
| Station Agent setup | User configures role, goal, memory policy, model, tools, skills and MCP refs per station. | Raw credential/prompt leaks or Agent profile claims executor readiness. |
| Visual workflow authoring | User creates/edits a workflow graph and receives a validated WorkflowDiffProposal. | Studio auto publishes/runs or graph cannot round-trip. |
| Workflow run and inspection | User confirms run and inspects trace, station outputs, quality refs and evidence refs. | Runtime evidence missing or planning docs used as runtime proof. |
| Extension install and binding | Approved plugin/skill/tool installs into workspace scope and unsafe package is denied. | Plugin executes unreviewed code or bypasses capability resolver. |
| Observability review | Operator sees trace, metrics, audit export and incident timeline without mutating runtime truth. | Dashboard constructs runtime truth or hides failure states. |
| Self-host smoke | Stack starts from documented env and completes one workflow smoke with health checks. | Smoke passes from docs only or lacks command output. |
| PV16 product-runtime hardening | User mutates product entities through BFF routes, confirms a runtime-backed workflow run, inspects trace/artifact/evidence refs and follows deployment hardening smoke. | Browser bypasses BFF/runtime gateway, runtime evidence is fixture-only, deployment smoke lacks command output or PV16 claim overstates production readiness. |

## Hard Gates

- V12 implementation cannot start until V12 readiness contracts are accepted.
- V12 full Figma prototype freeze cannot start until V12-0A component
  prototype review is accepted.
- V12 browser UI implementation evidence cannot be counted until V12-0A
  component prototype review and V12-0P Figma/high-fidelity prototype review are
  accepted.
- V12-0A component prototype review cannot pass while
  `artifact-manifest.json` is `PLANNED_NOT_EVIDENCE`, review JSON fails schema
  validation, or missing visual artifacts lack explicit
  `visual_artifact_exception_reason`.
- V13 implementation cannot start until V12 entity, BFF, workbench and
  read-only canvas foundation evidence plus V13 readiness are accepted.
- V13 implementation cannot start while `v13_implementation_readiness_audit.md`
  has open fatal or major findings.
- V13 PASS cannot be recorded unless V13 acceptance data and artifact manifest
  validate against the V13 schemas.
- V13 accepted pilot evidence can unblock V14 readiness, but it cannot be
  counted as runtime execution, production deployment or complete Studio
  evidence.
- The V12 bounded baseline can unblock V13 readiness review only after
  V12-SD/SI/SQ/SA evidence is reconciled and accepted. It cannot by itself
  prove V13 editable Studio implementation.
- V14 implementation cannot start until V12/V13 evidence, V14 readiness, V14
  acceptance schemas, V14 evidence manifest contract and V14 document-support
  audit are accepted.
- V15 final cannot start until V12/V13/V14 evidence and V15 readiness are
  accepted; this gate is now satisfied for the bounded V15 evidence package.
- V15 implementation cannot start until V15 readiness, V15 acceptance schemas,
  V15 evidence manifest contract and V15 document-support audit are accepted;
  this gate is now satisfied for the bounded V15 evidence package.
- Browser cannot call internal runtime routes directly.
- Browser onboarding cannot claim pass while API health/config is unavailable.
- WorkflowDiff cannot apply/publish/run without confirmation.
- Agent profiles cannot expose raw credential material.
- Plugin install cannot bypass compatibility or scope checks.
- Observability dashboards cannot construct runtime truth.
- Deployment smoke cannot pass from docs alone.
- V15 final cannot run while any V12-V14 evidence package is missing.
- V15 final cannot run while V12 canvas foundation or V13 editable Studio
  evidence is missing.
- V15 final cannot run while interaction evidence packages or human UX review
  results are missing.
- V15 final cannot run while product polish, interaction trace or
  goal-to-workflow loop evidence is missing.
- V15 final cannot use concept images, planning docs or screenshots alone as
  runtime evidence.
- V15 final cannot use component sketches or HTML prototype reports as browser,
  BFF or runtime implementation evidence.
- Xpert reference material cannot be counted as HarnessOS implementation
  evidence.

## Final Stop Conditions

- Forbidden completion claim appears outside a safe No False Green context.
- Any user scenario is FAIL or unaccepted BLOCKED.
- Browser network log shows direct internal runtime/store calls.
- Agent/Station configuration exposes raw secret, raw provider payload or raw
  artifact content.
- Plugin/skill/tool/MCP action runs outside scoped capability policy.
- Deployment smoke has no actual command output or health checks.
- Product frontend shows API/environment mismatch while final acceptance claims
  frontend interaction baseline.
- User input, selection, disabled action, failure or denied state has no
  visible feedback while interaction acceptance claims PASS.
- Product frontend claims product-grade, Xpert-level UX or complete Workflow
  Studio readiness from a V12 engineering prototype.
- Component prototype review is skipped while Figma freeze, browser UI
  implementation or final interaction acceptance claims PASS.
- Goal intake, proposal timeline, graph review, confirmation, run review and
  evidence review are disconnected while the scenario matrix claims PASS.

## Post-V15 Planning Gate

After the bounded V15 claim is accepted, any next implementation stage must
open a new readiness gate. The recommended next stage is PV16 product-runtime
hardening readiness and pilot evidence.

PV16 implementation cannot start until:

- `post_v15_next_stage_development_and_acceptance_plan.md` exists and is
  accepted as the stage plan;
- `post_v15_prd_architecture_coverage_audit.md` exists and has no open fatal
  findings;
- PV16 acceptance data and artifact manifest schemas exist;
- a PV16 acceptance runner exists and can fail missing evidence;
- route allowlist and browser denylist rules exist for product mutation and
  runtime handoff;
- the document-support audit records no open fatal or major implementation
  readiness findings.

This gate is closed for PV16 implementation entry by
`post_v15_implementation_readiness_audit.md`. PV16 exit acceptance is now also
closed for the bounded pilot because real PV16 evidence exists under
`evidence/post-v15-product-runtime-hardening/` and
`tools/post_v15/run_product_runtime_hardening_acceptance.py` passes.

PV16 evidence must not be used to claim production ready, complete Workflow
Studio ready, Agent executor ready, product-grade frontend complete or Xpert
parity.

## Post-PV16 PV17 Acceptance Gate

The selected post-PV16 stage was PV17 Product Closed Loop. PV17 bounded review
acceptance has passed. The following documentation gate was required before
implementation and now remains as audit trace:

- `pv17_product_closed_loop_prd.md` exists;
- `pv17_product_closed_loop_target_architecture.md` exists;
- `pv17_product_closed_loop_bff_dto_contract.md` exists;
- `pv17_product_closed_loop_implementation_task_matrix.md` exists;
- `pv17_product_closed_loop_development_and_acceptance_plan.md` exists;
- `pv17_product_closed_loop_acceptance_runner_spec.md` exists;
- `pv17_product_closed_loop_milestone_roadmap.md` exists;
- `pv17_product_closed_loop_acceptance_gate.md` exists;
- `pv17_product_closed_loop_current_gap_analysis.md` exists;
- `pv17_product_closed_loop_implementation_readiness_audit.md` exists;
- `pv17_product_closed_loop_gap_analysis.drawio` exists and has no more than
  8 pages;
- all PV17 documents state that PV16 `/bff/pv16/*` routes are test-only
  evidence routes, not formal product API proof;
- No False Green and redaction boundaries remain explicit.

PV17 implementation evidence is recorded under
`evidence/pv17-product-closed-loop/`, and
`reports/pv17_product_closed_loop_acceptance_report.json` reports PASS. This
does not upgrade HarnessOS to production ready, complete Workflow Studio ready,
Agent executor ready, Xpert parity complete or product-grade frontend complete.

The historical PV17 documentation gate only supported this document-stage
claim before implementation:

```text
PV17 product closed loop documentation ready for implementation review.
```

The current accepted PV17 claim is narrower and evidence-backed:

```text
PV17 complete: product closed loop implementation ready for bounded review.
```
