# V12-V15 Development And Acceptance Plan

## Stage Order

| Stage | Goal | Status | Exit Claim |
| --- | --- | --- | --- |
| V12 | Product Entity, Browser Workbench Shell, Read-Only Canvas Foundation And Control Plane Foundation | planned | V12 complete: product entity, browser workbench and canvas foundation ready for review. |
| V13 | Editable Workflow Studio And Visual DSL Productization | planned | V13 complete: editable Workflow Studio pilot slice ready for review. |
| V14 | Plugin / Skill / Tool / MCP Ecosystem | planned | V14 complete: governed extension ecosystem pilot ready for review. |
| V15 | Observability, Deployment And Xpert-Level Frontend Interaction Baseline | planned | V15 complete: Xpert-level frontend interaction baseline ready for review. |

## V12: Product Entity, Browser Workbench Shell And Read-Only Canvas Foundation

Scope:

- Add durable workspace/project/app/station-agent entities.
- Add browser product shell with onboarding, project inventory and Agent
  inventory.
- Add browser workbench shell with Xpert-inspired layout: global navigation,
  entity sidebar, central canvas area, top action bar, right inspector
  foundation and evidence/status area.
- Add Figma prototype review as the pre-implementation UX gate for product
  shell, read-only canvas, selected-node inspector, Chat Workbench proposal
  timeline and evidence drawer.
- Add component-level prototype sketch gate before full Figma freeze or real
  browser implementation. V12 first decomposes the product shell and workbench
  into reusable components, creates imag2 or HTML wireframe sketches, and
  collects human decisions in an HTML prototype sketch report.
- Add V12-0P high-fidelity prototype freeze gate before real browser
  implementation. The gate turns accepted components and interaction contracts
  into an integrated Light Studio target screen with navigation, canvas,
  inspector, bottom workbench, state enum and user journey evidence.
- Add shadcn-style frontend component foundation with Radix primitives,
  Tailwind utilities, CVA/tailwind-merge/clsx and lucide icons so V12 browser
  surfaces do not rely on bespoke one-off controls.
- Add V12-Q product polish hardening: visual hierarchy, layout density,
  responsive constraints, shared component usage, readable node cards,
  disabled/denied/failure states and human UX review.
- Add V12-I interaction depth foundation: selected-node feedback, linked
  inspector state, visible disabled action reasons, read-only add/layout/history
  placeholders, keyboard/focus behavior and goal-to-proposal-to-canvas path.
- Add read-only canvas foundation for project, station-agent, proposal,
  tool/skill/MCP and evidence nodes from BFF DTOs.
- Add node selection and inspector foundation for Agent role, goal, memory,
  model, tools, skills, MCP refs, quality refs and evidence refs.
- Add Chat Workbench read/write boundary for natural-language goal intake,
  attachments and WorkflowDiff proposal handoff.
- Add Agent role/goal/memory/model/tool/skill/MCP configuration schemas.
- Add BFF/DTO route boundary for product entity reads and writes.
- Add audit refs for every product entity mutation.

Implementation packages:

- V12 readiness plan: `v12_implementation_readiness_plan.md`.
- Figma prototype review plan: `v12_figma_prototype_review_plan.md`.
- Component prototype plan: `v12_component_prototype_plan.md`.
- Product entity and workbench schema contracts:
  `v12_product_entity_and_workbench_contracts.md`.
- BFF route allowlist and browser denylist:
  `v12_bff_route_and_browser_boundary.md`.
- Evidence and user scenario acceptance:
  `v12_evidence_and_user_acceptance_plan.md`.
- `StudioWorkspace`, `StudioProject`, `StudioApp`, `StationAgentProfile`,
  `StationAgentBinding`, `ToolCapabilityBinding`, `SkillPackageBinding` and
  `McpCapabilityBinding` schemas.
- `WorkbenchConversation`, `GoalIntakeMessage`, `WorkbenchAttachmentRef` and
  `WorkbenchProposalTimeline` schemas.
- BFF route allowlist for workspace/project/app/Agent/station configuration.
- Product shell route map: onboarding, workspace inventory, project detail,
  Agent inventory, workbench, evidence browser.
- Browser denylist for direct runtime, workflow store and credential routes.
- Entity audit record contract with actor, tenant, workspace, project, app,
  request, correlation and policy refs.
- Product console read-model fixture for workspace/project/Agent inventory.
- `CanvasReadModel`, `CanvasNodeProjection` and
  `CanvasInspectorProjection` contracts.
- Browser E2E fixture for read-only canvas shell, selected node inspector,
  disabled add/layout/history controls if not implemented, and BFF-only
  network access.
- Xpert reference baseline check: browser can reach frontend, API health and
  onboarding without environment mismatch.
- Figma prototype review artifact for the intended HarnessOS browser
  workbench, recorded as UX review evidence only.
- Component prototype sketch report for top bar, product navigation, canvas,
  node card, inspector, Chat Workbench and proposal timeline, recorded as
  design review evidence only.
- shadcn-style component inventory and build evidence for the V12 product
  shell and read-only workbench.
- Product polish review: screenshots, visual hierarchy checks, responsive
  screenshots, component consistency review and human UX review.
- Interaction trace: node selection, inspector update, disabled action reason,
  add-menu placeholder, command hint and goal-to-proposal-to-canvas visible path.

Acceptance:

- V12 implementation-readiness audit accepts schema/DTO, BFF boundary,
  browser denylist and evidence package contracts before implementation starts.
- Component prototype sketch report PASS exists before full Figma prototype
  freeze or browser UI implementation evidence is accepted.
- Figma prototype review PASS exists before browser UI implementation evidence
  is accepted.
- V12-0P high-fidelity prototype review PASS exists before browser UI
  implementation evidence is accepted, unless a reviewed Figma prototype
  explicitly supersedes it.
- Component foundation build PASS exists and V12 product shell uses shared UI
  primitives for the core shell, toolbar, status and inspector surfaces.
- Entity schemas parse and reject unknown fields.
- Browser/BFF routes enforce workspace/project ownership.
- Agent profile cannot expose raw credential material.
- StationAgentBinding requires policy and capability refs.
- E2E fixture creates workspace -> project -> station agents -> bindings.
- User can open product shell, create project, open workbench and see a
  proposal timeline without claiming runtime execution.
- User can open the browser workbench, see entity sidebar, read-only canvas,
  selected-node inspector and canvas toolbar skeleton.
- User can recognize a coherent low-code workbench surface: shared navigation,
  toolbar, node card, inspector, chat and evidence components are visually
  consistent.
- User can understand the product shell without reading docs first: workspace,
  project, active app, API health, workbench entry and evidence entry are
  visible.
- User can select a node and see the inspector update with matching DTO data.
- User can click disabled add/layout/history/publish/run placeholders and see a
  visible reason instead of a silent no-op.
- User can follow the V12 goal loop from natural-language input to proposal
  timeline and canvas review without treating the transcript as runtime
  execution.
- Product polish hardening evidence includes at least one desktop screenshot,
  one constrained-width screenshot, a component inventory review and a human UX
  review result.
- Canvas shell screenshot is generated from HarnessOS browser UI, not from
  Xpert reference screenshots or static images.
- Entity mutation evidence includes audit refs and redacted credential refs.
- Product console screenshot shows workspace, project, station agents and
  available tool/skill/MCP bindings.
- Browser screenshot shows onboarding / product shell and API health check
  evidence.

Stop conditions:

- Entity writes bypass BFF/DTO.
- Agent profile claims Agent executor ready.
- Raw secret or provider payload appears in entity evidence.
- Browser can call internal runtime/store routes directly.
- Workbench transcript is treated as runtime evidence.
- V12 canvas shell is implemented as a static screenshot, concept image or
  drawio-only artifact.
- V12 skips component-level prototype review and goes directly to full Figma
  freeze or real browser implementation.
- V12 product shell remains a bespoke mockup without shared component
  primitives.
- V12 product shell remains an engineering prototype with unreadable hierarchy,
  unlinked inspector, missing disabled reasons or no goal-to-canvas path while
  the stage claims interaction evidence PASS.
- Figma prototype is used as HarnessOS runtime evidence.
- V12 claims editable Workflow Studio, complete Workflow Studio ready or Xpert
  parity complete.
- Product shell claims Xpert parity complete.
- V12 claims product-grade frontend complete or Xpert-level UX complete.

## V13: Editable Workflow Studio And Visual DSL Productization

Scope:

- Build on the V12 browser workbench shell and implement editable Studio
  canvas for WorkflowSpecGraph.
- Support node types: start, end, station, tool, branch, parallel, fan-in,
  fan-out, quality, evidence and handoff.
- Add Agent/Station inspector panels aligned with V12 StationAgentProfile and
  V14 future extension bindings.
- Add WorkflowDiffProposal, versioning, validation and publish proposal flow.
- Add product-level canvas interactions: add menu, node configuration, node
  drag, valid/invalid edge feedback, auto-layout, minimap/zoom, history/undo
  affordance and linked inspector updates.
- Add browser E2E tests and screenshot evidence.

Implementation packages:

- V13 readiness plan: `v13_workflow_studio_dsl_readiness_plan.md`.
- `WorkflowSpecGraph` schema with node/edge validation.
- `WorkflowVersion` append-only contract.
- `WorkflowDiffProposal` contract with before/after graph refs and
  confirmation state.
- Studio canvas route and BFF DTO contract.
- Node inspector DTOs for StationAgent, tool, evidence and quality nodes.
- Graph round-trip test fixtures for create, edit, validate, diff and reject.
- Browser E2E fixture for visual authoring and inspector review.

Acceptance:

- V13 implementation-readiness audit accepts Studio/DSL schemas, BFF routes,
  browser denylist, graph fixtures and evidence package plan.
- User creates and edits a workflow visually.
- User can add, select, move and connect nodes from the browser canvas.
- User can open an add menu, configure a node and see validation feedback
  without opening raw JSON.
- User can run auto-layout or view minimap/zoom controls with visible feedback.
- Workflow graph validates node/edge rules.
- WorkflowDiff waits for user confirmation before publish/run.
- Browser network test proves no direct runtime store writes.
- Studio read panels show artifacts/evidence without constructing runtime truth.
- Parallel and fan-in/fan-out graph examples round-trip through schema
  validation.
- Confirmation transcript proves no apply/publish/run before explicit user
  action.
- Studio and workbench share the same WorkflowDiffProposal ref.

Stop conditions:

- Studio auto applies, publishes or runs without confirmation.
- Browser calls internal runtime or workflow store routes directly.
- Visual DSL cannot round-trip through schema validation.
- Canvas actions silently no-op or hide validation failures.
- Studio UI copy claims complete Workflow Studio ready.

## V14: Plugin / Skill / Tool / MCP Ecosystem

Scope:

- Add plugin and skill manifests.
- Add install, compatibility, config and scoped activation flow.
- Add tool/MCP capability registry and Agent binding UI.
- Add deny-by-default policy for unsafe packages.
- Add marketplace-style browse/inspect/install/activate UX, inspired by Xpert
  plugin management but bounded by HarnessOS policy.

Implementation packages:

- V14 readiness plan: `v14_extension_ecosystem_readiness_plan.md`.
- `PluginPackageManifest`, `SkillPackageManifest`, `ToolCapabilityManifest`
  and `McpConnectorManifest` schemas.
- Compatibility resolver for runtime version, permissions, required secrets
  and workspace scope.
- Install, disable, update and uninstall evidence contracts.
- Skill package asset contract for `SKILL.md`, scripts, references and assets.
- Tool/MCP binding UI and API fixtures.
- Plugin detail page screenshot, compatibility report and install decision
  timeline.
- Unsafe package and incompatible package negative fixtures.

Acceptance:

- V14 implementation-readiness audit accepts manifests, compatibility resolver,
  scoped activation, unsafe denial fixtures and evidence package plan.
- Approved plugin installs into workspace scope.
- Unsafe or incompatible plugin is denied with visible reason.
- Skill package appears in Agent configuration only after scope binding.
- MCP/tool capability cannot run outside policy.
- Config secrets are stored as redacted refs only.
- Agent configuration shows only scoped tool/skill/MCP capabilities.
- Denied plugin/tool action records policy decision and audit ref.
- Agent configuration panels only expose scoped capabilities after activation.

Stop conditions:

- Plugin install executes unreviewed code.
- Plugin config leaks raw secret.
- Tool/MCP bypasses capability resolver.
- Skill package can mutate workflow/runtime without confirmation.

## V15: Observability, Deployment And Xpert-Level Frontend Interaction Baseline

Scope:

- Add trace timeline, metrics dashboard, audit export and incident timeline.
- Add deployment profiles, compose env, health checks and smoke tests.
- Add frontend/API health diagnostics, onboarding readiness and environment
  mismatch detection.
- Add final frontend interaction review against Xpert-inspired scenarios.
- Add final No False Green, redaction and evidence aggregation.

Implementation packages:

- V15 readiness plan: `v15_observability_deployment_readiness_plan.md`.
- `TraceTimeline`, `MetricsSnapshot`, `AuditExportPackage`,
  `IncidentTimeline`, `DeploymentProfile` and `HealthCheckResult` schemas.
- Product observability dashboard with trace, metrics, audit, incident and
  redaction panels.
- Self-hosting compose/env profile with storage, queue, provider and
  observability configuration.
- Frontend/API/browser health check contract, including API base URL,
  authentication/onboarding readiness and CORS/domain checks.
- Deployment smoke runner and rollback runbook.
- Final frontend scenario matrix covering product console, Studio, Agent
  setup, workflow run/inspect, plugin install, observability and deployment.

Acceptance:

- V15 implementation-readiness audit accepts observability DTOs, deployment
  smoke contract, health diagnostics, final scenario matrix and evidence
  aggregation rules.
- Operator can review traces, metrics, audit export and incident refs.
- Self-hosting smoke starts stack and completes one workflow run.
- Browser-visible onboarding and API health PASS from a fresh local deployment.
- Frontend scenario matrix covers Studio creation, Agent setup, run inspect,
  plugin install, observability review and deployment smoke.
- No forbidden Xpert parity or production GA claim appears.
- Observability dashboard remains read-only for runtime truth.
- Deployment smoke includes command output, health checks, runtime evidence and
  rollback notes.

Stop conditions:

- V15 final runs before V12-V14 evidence exists.
- Deployment smoke lacks actual health/run evidence.
- Dashboard claims production ready or full Xpert parity.
- Audit export or metrics panel constructs runtime truth.
- Browser shows environment/API mismatch but deployment smoke still claims PASS.

## User Scenario Gates

| Scenario | First Eligible Stage | Required PASS Evidence |
| --- | --- | --- |
| Create a small studio project | V12 | Browser screenshot, BFF log, entity audit refs, no raw credentials. |
| Start from product onboarding | V12/V15 | Browser onboarding screenshot, frontend/API health, environment config PASS. |
| Open browser canvas workbench | V12 | HarnessOS browser screenshot, read-only canvas DTO, selected-node inspector, BFF-only network log. |
| Discuss goal in workbench | V12/V13 | Workbench transcript, proposal timeline, WorkflowDiffProposal ref, evidence scope. |
| Configure station-specific Agents | V12 | Agent profile, role/goal/memory/tool/skill/MCP bindings, validation errors. |
| Build a visual multi-Agent workflow | V13 | Studio screenshot, WorkflowSpecGraph, graph round-trip, WorkflowDiffProposal. |
| Confirm and inspect a workflow run | V13/V15 | Confirmation transcript, runtime trace, artifact refs, quality refs, evidence refs. |
| Install a workspace skill/plugin | V14 | Manifest, compatibility decision, scoped activation, unsafe denial fixture. |
| Review operations evidence | V15 | Trace timeline, metrics snapshot, audit export, incident refs, redaction PASS. |
| Self-host and smoke test | V15 | Compose/env profile, health checks, workflow smoke, rollback notes. |

## Required Verification Commands

Commands will be finalized per stage. Initial planning checks:

```bash
xmllint --noout docs/design/V12-V15.x/v12_to_v15_current_gap_analysis.drawio
rg -n "Xpert parity complete|production ready|Agent executor ready|完整工作流工作台已完成|已完全追平 Xpert" docs/design/V12-V15.x
```

## Stage Entry Rules

- V12 implementation cannot start until `v12_implementation_readiness_plan.md`,
  `v12_product_entity_and_workbench_contracts.md`,
  `v12_bff_route_and_browser_boundary.md` and
  `v12_evidence_and_user_acceptance_plan.md` are accepted.
- V13 implementation cannot start until V12 entity, BFF, workbench and
  read-only canvas foundation evidence exists and
  `v13_workflow_studio_dsl_readiness_plan.md` is accepted.
- V14 implementation cannot start until V12 scoping and policy evidence exists.
- V14 implementation also requires V13 Studio/DSL evidence and
  `v14_extension_ecosystem_readiness_plan.md` acceptance.
- V15 final acceptance cannot run until V12-V14 evidence packages exist.
- V15 implementation-readiness requires
  `v15_observability_deployment_readiness_plan.md` acceptance.
- No stage may use Xpert reference screenshots as HarnessOS runtime evidence.
