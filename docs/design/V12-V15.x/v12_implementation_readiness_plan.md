# V12 Implementation Readiness Plan

## Current Decision

V12 is the next implementation-readiness candidate.

Allowed:

- V12 product entity schema and DTO implementation planning.
- V12 BFF route and browser boundary implementation planning.
- V12 product shell, onboarding, browser workbench shell, read-only canvas
  foundation and workbench foundation planning.
- V12 component-level prototype sketch planning before full Figma prototype or
  real browser implementation.
- V12 Figma prototype review before browser UI implementation.
- V12 shadcn-style component foundation and XyFlow canvas implementation
  planning.
- V12 evidence package and user scenario acceptance planning.

Blocked:

- Direct V13 Workflow Studio runtime implementation.
- Direct V14 plugin runtime implementation.
- Direct V15 final acceptance.
- Direct V12 browser UI implementation before the Figma prototype review is
  accepted.
- Direct V12 full Figma prototype freeze or browser UI implementation before
  the V12 component prototype sketch report is accepted.
- Any claim of Xpert parity complete, production ready, complete Workflow
  Studio ready or Agent executor ready.

## V12 Objective

V12 turns the V11 CLI/TUI baseline into a browser-visible product foundation.
The user should be able to open a product shell, see onboarding and API health,
create or inspect a workspace/project/app, configure station Agent profiles, and
use a Chat Workbench to produce a WorkflowDiff proposal handoff. After the
focused Xpert canvas survey, V12 also owns the first browser canvas shell:
entity sidebar, read-only canvas projection, selected-node inspector and
BFF-only network evidence.

V12 does not prove a complete Workflow Studio, production plugin marketplace,
production deployment or full Xpert parity.

## Required Contracts Before Implementation

| Contract | Required Document |
| --- | --- |
| Product entity and workbench schemas | `v12_product_entity_and_workbench_contracts.md` |
| BFF routes, browser allowlist and denylist | `v12_bff_route_and_browser_boundary.md` |
| Evidence package and user acceptance | `v12_evidence_and_user_acceptance_plan.md` |
| Component-level prototype sketch gate | `v12_component_prototype_plan.md` |
| Component-level prototype execution details | `v12_component_prototype_execution_plan.md` |
| Figma product prototype and UX review | `v12_figma_prototype_review_plan.md` |
| V12-0P high-fidelity prototype freeze | `v12_0p_high_fidelity_prototype_plan.md` |
| shadcn-style component foundation | `v12_to_v15_target_architecture.md` and this plan |
| V12-V15 roadmap and architecture alignment | `v12_to_v15_development_and_acceptance_plan.md` |
| No False Green guard | `v12_to_v15_no_false_green_claim_guard.md` |

Machine-readable readiness artifacts:

- `schemas/v12_product_entity_projection.schema.json`
- `schemas/v12_canvas_read_model.schema.json`
- `schemas/v12_browser_network_log.schema.json`
- `schemas/v12_acceptance_data.schema.json`
- `schemas/v12_component_prototype_review.schema.json`
- `schemas/v12_component_prototype_artifact_manifest.schema.json`
- `fixtures/v12/*.json`
- `reports/v12_drawio_validation_report.json`
- `evidence/v12-component-prototype/index.html`
- `evidence/v12-component-prototype/component-prototype-review-data.json`
- `evidence/v12-component-prototype/artifact-manifest.json`
- `evidence/v12-readiness/figma-prototype-url.txt`
- `evidence/v12-readiness/figma-prototype-review.md`
- `evidence/v12-0p-high-fidelity-prototype/index.html`
- `evidence/v12-0p-high-fidelity-prototype/prototype-review-data.json`
- `evidence/v12-0p-high-fidelity-prototype/artifact-manifest.json`
- `evidence/v12-0p-high-fidelity-prototype/prd-spec-review.md`

Frontend implementation baseline:

- `apps/workflow-console/components.json`
- `apps/workflow-console/tailwind.config.ts`
- `apps/workflow-console/postcss.config.js`
- `apps/workflow-console/src/components/ui/*`
- `apps/workflow-console/src/styles/shadcn.css`

## Implementation Slices

### V12-0A Component Prototype Sketch Gate

Produce and review:

- Global top bar.
- Left product navigation.
- Workspace/project/Agent sidebar.
- Canvas workbench.
- Agent / Station node card.
- Edge, port and state affordance.
- Right inspector.
- Chat Workbench and proposal timeline.
- WorkflowDiff / proposal panel.
- Evidence / quality / trace drawer.
- Disabled, failure and permission-denied states.

Process:

- Generate or draw component-level sketches before a full-page Figma freeze.
- Prefer imag2 concept images where useful; fallback to local HTML/CSS
  wireframes if image generation is unavailable.
- Summarize sketches, component goals, boundaries and reviewer decisions in an
  HTML prototype sketch report.
- Review first-batch components before continuing to full-page Figma or real
  browser implementation.

Exit evidence:

- `docs/design/V12-V15.x/evidence/v12-component-prototype/index.html` exists.
- `docs/design/V12-V15.x/evidence/v12-component-prototype/component-prototype-review-data.json`
  exists, parses and validates against
  `schemas/v12_component_prototype_review.schema.json`.
- `docs/design/V12-V15.x/evidence/v12-component-prototype/artifact-manifest.json`
  exists, parses, validates against
  `schemas/v12_component_prototype_artifact_manifest.schema.json`, and is not
  left in `PLANNED_NOT_EVIDENCE` status for V12-0A PASS.
- First-batch components are accepted or accepted with bounded revisions.
- Every component records user goal, visible data, allowed actions, disabled
  actions, acceptance checks and design-only evidence scope.
- Any missing image/wireframe fallback records an explicit
  `visual_artifact_exception_reason`.
- No False Green review confirms the sketches do not claim Xpert parity,
  product-grade frontend complete, complete Workflow Studio, production ready
  or Agent executor ready.

### V12-0P Figma Prototype Review Gate

Produce and review:

- Product shell / onboarding screen.
- Browser workbench canvas screen.
- Selected node inspector screen.
- Chat Workbench proposal timeline screen.
- Evidence / quality drawer screen.
- Component inventory mapping: shell, toolbar, tabs, button, badge, card,
  tooltip, scroll area, node card, inspector row, chat timeline and evidence
  drawer.

Exit evidence:

- Figma URL recorded.
- Prototype contains editable layers, not only screenshots.
- Component-level prototype sketch report has been accepted before Figma freeze.
- Prototype review confirms V12 read-only canvas and proposal-only boundary.
- No False Green review confirms the prototype does not claim Xpert parity,
  complete Workflow Studio, production ready or Agent executor ready.

### V12-0P High-Fidelity Prototype Freeze

If Figma editing is unavailable or delayed, a local high-fidelity HTML
prototype may serve as the V12-0P product-experience freeze artifact, provided
it remains design-only and satisfies the same boundaries as the Figma review.

Produce and review:

- integrated Light Studio target screen;
- L1/L2 navigation hierarchy;
- read-only canvas with curved edges, ports, node states and minimap;
- selected-node inspector;
- bottom Chat / proposal / Trace / quality / evidence workbench;
- state enum and user journey explanation;
- PRD fit review, No False Green scan, redaction scan and static render.

Exit evidence:

- `docs/design/V12-V15.x/evidence/v12-0p-high-fidelity-prototype/index.html`
  exists.
- `prototype-review-data.json` records `runtime_backed=false`,
  `browser_implementation_backed=false`, `bff_backed=false` and
  `figma_backed=false` unless a real Figma prototype is later linked.
- `index.html.png` static render exists.
- PRD spec review confirms the prototype is sufficient for
  implementation-readiness audit input.
- No False Green and redaction scans pass.

### V12-0C shadcn-style Component Foundation

Implement:

- Tailwind utilities with preflight disabled to avoid destabilizing existing
  console styles.
- shadcn-style `Button`, `Badge`, `Card`, `Tabs`, `ScrollArea`, `Separator`
  and `Tooltip` components.
- Radix interaction primitives for tabs, tooltip, scroll area and separator.
- lucide icon mapping for navigation, toolbar, state and evidence surfaces.
- CVA/tailwind-merge/clsx variant handling for stable component states.

Exit evidence:

- `npm --prefix apps/workflow-console run build` PASS.
- V12 workbench imports the shared UI primitives instead of bespoke one-off
  controls for the core shell.
- UI copy remains Simplified Chinese.
- Existing V4-V11 console routes still compile.

### V12-1 Product Entity Foundation

Implement or validate:

- `StudioWorkspace`
- `StudioProject`
- `StudioApp`
- `StudioFileAsset`
- `StationAgentProfile`
- `StationAgentBinding`
- `ToolCapabilityBinding`
- `SkillPackageBinding`
- `McpCapabilityBinding`
- `EntityAuditRecord`

Exit evidence:

- JSON schema parse PASS.
- Unknown field negative fixture rejected.
- Workspace/project/app ownership negative fixture rejected.
- Raw credential fields rejected.

### V12-2 Product Shell And Onboarding

Implement:

- Onboarding route.
- Workspace inventory route.
- Project detail route.
- Agent inventory route.
- API health and config diagnostics panel.
- Product shell layout that can host the canvas/workbench surface.

Exit evidence:

- Browser screenshot.
- Browser network log.
- API health result.
- Frontend/API base URL consistency check.
- Figma prototype review accepted before implementation evidence is accepted.
- Product shell uses shared component primitives where available instead of
  per-screen bespoke controls.

### V12-2B Read-Only Canvas Workbench Foundation

Implement:

- `CanvasReadModel`.
- `CanvasNodeProjection`.
- `CanvasInspectorProjection`.
- Entity sidebar.
- Central read-only canvas area.
- Selected-node inspector foundation.
- Top action bar and canvas toolbar skeleton.
- Disabled or bounded placeholders for add, layout, history and publish actions
  if full behavior is not implemented in V12.

Exit evidence:

- Browser screenshot of the HarnessOS canvas/workbench shell.
- BFF DTO response for read-only canvas projection.
- Browser network log proving no direct internal runtime/store route calls.
- Node selection screenshot showing inspector data for one station Agent.
- Explicit evidence scope: read-only projection, not editable Studio.
- Browser workbench uses XyFlow for graph rendering and shadcn-style product
  components for surrounding shell, toolbar, inspector and evidence surfaces.

### V12-3 Chat Workbench Foundation

Implement:

- `WorkbenchConversation`
- `GoalIntakeMessage`
- `WorkbenchAttachmentRef`
- `WorkbenchProposalTimeline`
- WorkflowDiff proposal handoff reference.

Exit evidence:

- User goal transcript.
- Proposal timeline.
- WorkflowDiff proposal ref.
- Explicit statement that transcript is not runtime evidence.

### V12-4 BFF And Browser Boundary

Implement:

- BFF route allowlist.
- Browser route denylist.
- DTO validation.
- Entity mutation audit refs.

Exit evidence:

- Browser cannot call internal runtime/store routes.
- BFF rejects wrong workspace/project/app scope.
- Entity mutation records actor, request, correlation and audit refs.

### V12-5 V12 End-To-End Acceptance

Run:

- Product onboarding scenario.
- Small studio project setup scenario.
- Browser canvas workbench foundation scenario.
- Station Agent setup scenario.
- Chat workbench to WorkflowDiff handoff scenario.
- Browser denylist scenario.
- Redaction and No False Green scans.

Exit claim:

V12 complete: product entity, browser workbench and canvas foundation ready for review.

## V12 Stop Conditions

- Product entity mutation bypasses BFF/DTO validation.
- Figma prototype review is missing before browser UI implementation evidence is
  accepted.
- Browser can call `/v1/rpc`, internal runtime, internal executor, workflow
  store or credential routes directly.
- Workbench transcript is treated as runtime execution evidence.
- Canvas shell is only a concept image, drawio, static screenshot, or Xpert
  reference screenshot.
- Read-only canvas foundation is described as complete Workflow Studio.
- Agent profile exposes raw credential, raw token, raw provider payload or raw
  artifact content.
- Product shell claims Xpert parity complete.
- V12 evidence package relies on Xpert reference screenshot as HarnessOS
  implementation evidence.
- shadcn-style component adoption is treated as visual parity proof by itself
  without HarnessOS browser screenshot, network and DTO evidence.
