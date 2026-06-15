# V12-V15 Acceptance Gate

## Final Allowed Claim

V15 complete: Xpert-level frontend interaction baseline ready for review.

## Required Final Evidence

- Xpert reference audit exists and is marked planning/reference evidence only.
- V12 implementation-readiness documents exist and are accepted before V12
  implementation evidence is counted.
- V13/V14/V15 implementation-readiness documents exist and are accepted before
  their implementation or final evidence is counted.
- V12 product entity evidence package exists and PASS.
- V12 component prototype review package exists and PASS before Figma or
  browser implementation evidence is counted.
- V13 Studio/DSL evidence package exists and PASS.
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
| V12 | `evidence/v12-product-entity/` | Schemas, BFF route logs, browser screenshots, entity audit refs, ownership denial cases, redaction scan. |
| V12 | `evidence/v12-workbench-foundation/` | Onboarding screenshot, frontend/API health, workbench transcript, proposal timeline, browser denylist log. |
| V12 | `evidence/v12-canvas-foundation/` | Read-only canvas DTO, browser canvas screenshot, selected-node inspector screenshot, BFF-only network log, explicit non-editable Studio scope. |
| V12 | `evidence/v12-product-polish/` | Desktop and constrained screenshots, component inventory review, visual hierarchy assertions, node card legibility review, human UX review. |
| V12 | `evidence/v12-interaction-depth/` | Playwright action log, selected-node DTO snapshot, inspector update evidence, disabled action reason screenshot, goal-to-proposal-to-canvas trace. |
| V13 readiness | `v13_workflow_studio_dsl_readiness_plan.md` | Studio/DSL schemas, BFF routes, graph validation rules, graph fixtures, user scenarios. |
| V13 | `evidence/v13-workflow-studio-dsl/` | Studio screenshots, WorkflowSpecGraph, WorkflowDiffProposal, graph round-trip report, browser denylist log, confirmation transcript, add/configure/move/connect/auto-layout trace. |
| V14 readiness | `v14_extension_ecosystem_readiness_plan.md` | Manifest schemas, compatibility resolver, scoped activation rules, unsafe denial fixtures. |
| V14 | `evidence/v14-extension-ecosystem/` | Plugin/skill manifests, compatibility decisions, scoped activation refs, unsafe denial fixtures, tool/MCP capability decisions. |
| V15 readiness | `v15_observability_deployment_readiness_plan.md` | Observability DTOs, deployment smoke contract, health diagnostics, final scenario matrix. |
| V15 | `evidence/v15-observability-deployment/` | Trace timeline, metrics snapshot, audit export, incident refs, compose smoke output, health check results, final scenario matrix. |
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
| Documentation only | no | Cannot satisfy implementation acceptance. |
| Concept images | no | Planning only. |

## User Scenario Acceptance Matrix

| Scenario | PASS Condition | Blocking Failure |
| --- | --- | --- |
| Small studio project setup | User creates workspace/project/app and sees product inventory with audit refs. | Entity exists only in fixture docs or bypasses BFF ownership checks. |
| Product onboarding | User reaches browser onboarding/product shell and system status is available. | Frontend/API mismatch is visible or unresolved while smoke claims PASS. |
| Component prototype review | User reviews first-batch components before full-page Figma or implementation. | Full Figma or implementation starts before component decisions are accepted. |
| Browser canvas foundation | User opens HarnessOS workbench canvas shell, sees entity sidebar, node cards and inspector foundation from BFF DTOs. | Canvas evidence is static/drawio/Xpert reference only or browser bypasses BFF. |
| Product polish hardening | User can understand the active workspace/project/app, available actions, disabled reasons and evidence surface from a coherent product shell. | UI remains unreadable engineering prototype, lacks responsive evidence or has no human UX review. |
| Canvas interaction clarity | User selects nodes, sees inspector updates and receives visible reasons for unavailable add/layout/publish/run actions. | Clicks silently no-op, inspector is stale or disabled actions have no reason. |
| Chat workbench to Studio handoff | User discusses a goal, receives proposal timeline and opens WorkflowDiff in Studio. | Chat transcript is treated as runtime execution or bypasses WorkflowDiff. |
| Station Agent setup | User configures role, goal, memory policy, model, tools, skills and MCP refs per station. | Raw credential/prompt leaks or Agent profile claims executor readiness. |
| Visual workflow authoring | User creates/edits a workflow graph and receives a validated WorkflowDiffProposal. | Studio auto publishes/runs or graph cannot round-trip. |
| Workflow run and inspection | User confirms run and inspects trace, station outputs, quality refs and evidence refs. | Runtime evidence missing or planning docs used as runtime proof. |
| Extension install and binding | Approved plugin/skill/tool installs into workspace scope and unsafe package is denied. | Plugin executes unreviewed code or bypasses capability resolver. |
| Observability review | Operator sees trace, metrics, audit export and incident timeline without mutating runtime truth. | Dashboard constructs runtime truth or hides failure states. |
| Self-host smoke | Stack starts from documented env and completes one workflow smoke with health checks. | Smoke passes from docs only or lacks command output. |

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
- V14 implementation cannot start until V12/V13 evidence and V14 readiness are
  accepted.
- V15 final cannot start until V12/V13/V14 evidence and V15 readiness are
  accepted.
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
