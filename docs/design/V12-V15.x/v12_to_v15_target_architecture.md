# V12-V15 Target Architecture

## Architecture Intent

V12-V15 productizes the inherited HarnessOS runtime into a staged
Studio-grade product surface for bounded review. PV16 is the current
post-V15 hardening stage that must connect the accepted product frontend to
durable product mutation, controlled runtime run/inspect evidence and
deployment hardening. The architecture must reuse V4-V11 Gateway, runtime,
controlled executor, evidence and TUI boundaries. It adds product entities,
Studio/BFF surfaces, visual DSL, plugin lifecycle, operations planes and a
PV16 product-runtime hardening plane.

The architecture is benchmarked against Xpert's web product shell, Studio,
Agent model, workflow DSL, plugin system, file understanding and execution
observability. HarnessOS should preserve its stricter evidence and governance
model while closing the product-interaction gap.

The focused Xpert canvas survey recalibrates the architecture: the browser
workbench shell and canvas foundation are not optional V15 polish. They are V12
foundation work. Editable graph semantics remain V13 work.

V12 also introduces a two-step product design review path. V12-0A creates a
component prototype sketch pack and HTML review report before full-page design
freeze. V12-0P then maps the accepted component direction into Figma or an
approved high-fidelity prototype for browser shell, read-only canvas
foundation, inspector, Chat Workbench and evidence drawer. These artifacts
belong to the interaction acceptance plane. They do not own runtime truth and
cannot replace BFF, DTO, browser or runtime evidence.

V12-0P must additionally freeze the interaction experience contract before
implementation: left L1/L2 navigation hierarchy, canvas tactile interactions,
panel z-order, consistent state/design tokens and bottom workbench tab
semantics. This contract is recorded in
`v12_0p_interaction_experience_spec.md` and is required input to any Figma or
high-fidelity prototype review.

V12 browser implementation should use mature, open-source UI primitives rather
than hand-tuned one-off controls. The selected baseline is a shadcn-style
component layer built from Radix primitives, class-variance-authority,
tailwind-merge, clsx, lucide-react and Tailwind utilities, with the existing
`@xyflow/react` canvas retained for workflow graph rendering. This is an
implementation-quality guard: HarnessOS can tune product-specific semantics
while relying on mature primitives for buttons, tabs, tooltips, scroll areas,
dialogs, menus and iconography.

## Accepted V12 Architecture Baseline

The accepted V12 baseline implements and validates a bounded read-only slice:

```text
Reviewer
  -> V12ReadOnlyWorkbench browser route
  -> /bff/v12/* route allowlist
  -> ProductEntityProjection / CanvasReadModel / CanvasInspectorProjection DTOs
  -> Schema validation, route log, browser network log and screenshot evidence
```

This slice proves that the browser can consume real BFF-shaped data for the
workbench foundation without direct runtime/store access. It preserves the
target architecture direction by keeping product entity projection, canvas read
model, selected-node inspector and evidence packaging separate from runtime
truth. It is not the editable WorkflowSpecGraph path and does not replace the
future V13 Studio BFF.

The V12-SD/SI/SQ/SA evidence extends this baseline with proposal handoff,
visible interaction feedback, product polish hardening and aggregate
reconciliation. These remain browser/read-model and review-scope capabilities.
They do not mutate WorkflowSpecGraph, execute workflows or construct runtime
truth.

## Accepted V13 Architecture Baseline

The accepted V13 baseline implements and validates an editable Studio pilot
slice:

```text
Reviewer
  -> V13EditableStudio browser route
  -> /bff/v13/* route allowlist
  -> WorkflowSpecGraph / GraphValidationResult / NodeInspector / WorkflowDiffProposal DTOs
  -> Browser action log, route log, network log, screenshots and schema evidence
  -> Confirm-publish-handoff with publish_or_run_started=false
```

This slice proves that the browser can edit a pilot WorkflowSpecGraph through
the BFF boundary, receive validation feedback, inspect selected nodes and
review WorkflowDiff before handoff. It preserves the architecture boundary by
keeping graph draft state, proposal review and confirmation handoff separate
from runtime execution truth. It is not a complete Workflow Studio and it does
not replace V15 runtime run/inspect or deployment evidence.

## Accepted V14-V15 Architecture Baseline

The accepted V14 baseline validates a governed extension ecosystem pilot:

```text
Reviewer
  -> V14ExtensionEcosystem browser route
  -> /bff/v14/* route allowlist
  -> Package manifest / compatibility / scoped activation / unsafe denial DTOs
  -> Browser screenshots, route logs, policy refs and schema evidence
```

This slice proves scoped Plugin/Skill/Tool/MCP review and binding only. It does
not prove unrestricted marketplace behavior, plugin runtime execution or Agent
executor readiness.

The accepted V15 baseline validates a frontend interaction and operations
review baseline:

```text
Reviewer
  -> V15ObservabilityDeployment browser route
  -> /bff/v15/* route allowlist
  -> TraceTimeline / MetricsSnapshot / AuditExportPackage / DeploymentProfile DTOs
  -> Dashboard screenshots, command output, final matrix and schema evidence
```

This slice proves read-only operations/deployment review and bounded local
smoke evidence only. It does not prove production GA, complete Studio,
runtime-backed workflow execution or Xpert parity.

## Next Target Architecture Evolution

```text
Accepted V12 baseline
  -> Accepted V13 Studio BFF and editable WorkflowSpecGraph pilot
  -> Accepted V13 WorkflowDiffProposal confirmation and graph round-trip evidence
  -> V14 PluginPackageManifest / SkillPackageManifest / ToolCapabilityBinding
  -> V14 compatibility, scoped activation and unsafe denial evidence
  -> V15 TraceTimeline / MetricsSnapshot / AuditExportPackage
  -> V15 deployment smoke and final interaction baseline evidence
  -> PV16 durable product mutation through BFF-only DTOs
  -> PV16 controlled runtime run/inspect evidence
  -> PV16 deployment hardening smoke and product journey evidence
```

The relationship is additive and gated. V13 reuses the V12 browser workbench,
component system, BFF discipline and read-model evidence, then adds editable
graph semantics behind Studio-specific DTOs. V14 must reuse the V13 inspector
and Agent/Station configuration seams to bind approved capabilities. V15 must
reuse the runtime evidence chain to expose trace, metrics, audit and deployment
smoke without converting dashboards into runtime truth.

PV16 must then connect the accepted product shell and Studio pilot to real
product-runtime hardening evidence. The browser still cannot call internal
runtime or store routes directly: product mutations go through BFF DTOs,
confirmed WorkflowSpec runs go through the controlled runtime gateway, and
observability reads trace/artifact/evidence refs emitted by the runtime rather
than constructing runtime truth in the dashboard.

## Target Architecture Planes

```text
User
  -> Product Console / Mission Studio Plane
  -> shadcn-style Component System Plane
  -> Product Interaction Quality Plane
  -> Component Prototype Review Plane
  -> Canvas Workbench Shell And Inspector Plane
  -> Canvas Interaction Engine Plane
  -> Chat Workbench And Goal Intake Plane
  -> Goal-To-Workflow Loop Plane
  -> Studio BFF And DTO Plane
  -> Figma Prototype Review Plane
  -> Product Entity Control Plane
  -> Workflow DSL And Versioning Plane
  -> Agent/Station Configuration Plane
  -> Plugin / Skill / Tool / MCP Ecosystem Plane
  -> Runtime Gateway And Controlled Execution Plane
  -> Artifact / Evidence / Quality Plane
  -> Interaction Acceptance Automation Plane
  -> Observability / Audit / Operations Plane
  -> Deployment And Self-Hosting Plane
  -> PV16 Product-Runtime Hardening Plane
```

## Plane Responsibilities

| Plane | Owns | Must Not Own |
| --- | --- | --- |
| Product Console / Mission Studio | Web navigation, Studio canvas, inspector panels, evidence browser. | Direct runtime mutation. |
| shadcn-style Component System | Shared browser components, Radix-based interaction primitives, lucide icons, Tailwind/CVA variants and design token mapping. | Runtime truth, BFF policy or custom graph engine ownership. |
| Product Interaction Quality | Visual hierarchy, layout density, responsive behavior, focus states, disabled/denied/failure states and human UX review evidence. | Claiming product-grade frontend complete or replacing runtime evidence. |
| V12 Interaction Experience Contract | L1/L2 navigation hierarchy, canvas hover/select/drag/edge behavior, panel z-order, bottom workbench tabs, keyboard/focus requirements. | Browser implementation evidence, runtime truth or editable Studio semantics. |
| Component Prototype Review | Component-level sketches, component responsibilities, HTML prototype report, reviewer decisions and design-only evidence scope. | Full-page Figma freeze, runtime evidence, browser implementation evidence or WorkflowSpecGraph mutation. |
| Canvas Workbench Shell And Inspector | Entity sidebar, read-only graph projection, node selection, inspector foundation, canvas toolbar and evidence links. | Editing WorkflowSpecGraph before V13 or constructing runtime truth. |
| Current V12 Read-Only Workbench Gate | Browser projection of workspace/project/app/station-agent/canvas/inspector DTOs through `/bff/v12/*`, with route log, network log, screenshot and schema evidence. | Editable graph semantics, publish/run behavior, runtime execution evidence or production deployment evidence. |
| Canvas Interaction Engine | XyFlow node wrappers, ports, minimap, zoom, selection, add-menu placeholder, auto-layout hook points and graph editing affordances. | Publishing/running workflow or mutating runtime truth. |
| Accepted V12 Baseline | V12-0P direction, real-data read-only workbench, Chat proposal handoff, interaction depth, product polish and V12-SA evidence reconciliation. | Editable Studio completion, runtime execution, product-grade frontend completion, Xpert parity or production readiness. |
| Accepted V13 Studio Pilot | Editable WorkflowSpecGraph pilot, BFF-backed graph validation, selected-node inspector, WorkflowDiff review and handoff evidence. | Complete Workflow Studio, runtime execution, production workflow authoring, Xpert parity or Agent executor readiness. |
| Chat Workbench And Goal Intake | Natural-language project goal capture, attachments, proposal timeline and run handoff. | Treating chat transcript as runtime truth. |
| Goal-To-Workflow Loop | Goal intake, WorkflowDiff proposal timeline, graph review, revise/confirm handoff, run review and evidence review continuity. | Skipping confirmation or treating proposal as execution. |
| Studio BFF And DTO | Browser route allowlist, DTO validation, manual confirmation, read/write boundary. | Provider secrets or raw runtime store writes. |
| Figma Prototype Review | Human-reviewable browser shell and canvas interaction contract for V12. | Runtime evidence, BFF evidence or WorkflowSpecGraph mutation. |
| Product Entity Control Plane | Workspace, project, app, station agent, role binding, tool binding, skill binding. | Runtime execution state. |
| Workflow DSL And Versioning | WorkflowSpec, WorkflowVersion, node/edge schema, diff, validation, publish proposal. | Direct StationRun mutation from browser. |
| Agent/Station Configuration | Agent role, goal, memory policy, model, tools, skills, MCP refs, permission policy. | Unrestricted Agent executor readiness. |
| Plugin / Skill / Tool / MCP Ecosystem | Manifests, compatibility, install, activation, config, policy, sandbox. | Unsafe unreviewed code execution. |
| Runtime Gateway And Controlled Execution | Existing GatewayService, controlled executor, orchestration runtime, TUI event stream. | Studio bypass route. |
| Artifact / Evidence / Quality | Artifact refs, quality refs, evidence packages, redaction and claim scans. | Runtime truth construction from reports. |
| Interaction Acceptance Automation | Playwright scenarios, screenshot capture, DOM assertions, network denylist, UI copy scan and human review checklist. | Replacing runtime evidence or subjective human review entirely. |
| Observability / Audit / Operations | Trace, metrics, audit export, incident timeline, health checks, deployment evidence. | Product capability overclaims. |
| Deployment And Self-Hosting | Compose, env, storage, queue, observability, backup/restore docs. | Production GA claim before evidence. |
| PV16 Product-Runtime Hardening | Durable product mutation, controlled runtime run/inspect handoff, deployment hardening smoke and product journey evidence. | Direct browser runtime calls, destructive deployment changes, production GA or complete Studio claims. |

## Core Product Entities

| Entity | Purpose |
| --- | --- |
| `StudioWorkspace` | Product workspace boundary. |
| `StudioProject` | User project containing workflows, files, Agents and evidence. |
| `StudioFileAsset` | Project file and upload reference exposed through Studio/workbench. |
| `CanvasReadModel` | Read-only workbench canvas projection used by V12 before editable V13 graph semantics. |
| `CanvasNodeProjection` | Display node for project, station-agent, proposal, tool, skill, MCP, evidence or quality refs. |
| `CanvasInspectorProjection` | Right-side inspector DTO for selected entity/node details. |
| `WorkbenchConversation` | Chat goal intake and proposal review transcript. |
| `StationAgentProfile` | Durable Agent profile for one or more workflow stations. |
| `StationAgentBinding` | Binding of station to Agent role/model/tools/skills/MCP refs. |
| `WorkflowSpecGraph` | Visual DSL graph with nodes and edges. |
| `WorkflowVersion` | Immutable or append-only workflow version. |
| `WorkflowDiffProposal` | Proposed change requiring confirmation before publish/run. |
| `PluginPackageManifest` | Installed plugin or tool package manifest. |
| `SkillPackageManifest` | Workspace skill package metadata and files. |
| `ToolCapabilityBinding` | Scoped tool/MCP capability availability. |
| `PluginInstallDecision` | Compatibility, policy and scope decision for plugin package lifecycle. |
| `SkillInstallDecision` | Compatibility, policy and scope decision for skill package lifecycle. |
| `TraceTimeline` | Runtime trace read model. |
| `MetricsSnapshot` | Operational metrics and usage summary. |
| `AuditExportPackage` | Append-only audit export ref. |
| `DeploymentProfile` | Self-hosting profile and environment contract. |
| `InteractionEvidencePackage` | Per-stage UX evidence package with screenshots, network logs, DTO snapshots, UI copy scan and human review result. |
| `WorkbenchComponentInventory` | V12 component inventory covering shell, toolbar, node card, inspector, chat, evidence and disabled/denied states. |
| `ComponentPrototypeReview` | V12-0A design review record for component sketches, accepted/rejected decisions, design-only evidence refs and open questions. |
| `ProductPolishReview` | Human and automated review record for hierarchy, density, component consistency, responsive behavior and copy safety. |
| `CanvasInteractionTrace` | Browser action log for selection, disabled action reason, add-menu placeholder, node move/connect and inspector update behavior. |
| `GoalWorkflowLoopTrace` | Transcript and evidence refs connecting goal intake, proposal, graph review, confirmation, run review and evidence review. |

## Current-To-Target Change Classification

| Classification | Items |
| --- | --- |
| Inherit | GatewayService, controlled executor constraints, Evidence Chain, Runtime Report, Mission TUI V11 event model, V9 orchestration and coding workflow evidence. |
| Modify | Workflow console, TUI/Studio evidence projection, BFF route boundary, existing workflow stores, workbench goal intake. |
| Add | Product Console, canvas workbench shell, node inspector foundation, Studio canvas, durable StationAgent model, visual DSL, plugin lifecycle, observability dashboard, deployment profile, frontend/API health evidence. |
| Add | Figma prototype review artifact for V12 browser product shell and canvas UX before implementation. |
| Add | Component prototype review artifact for V12 component-level sketch approval before Figma freeze. |
| Add | shadcn-style frontend component system using Radix, Tailwind utilities, CVA, tailwind-merge, clsx and lucide-react in `apps/workflow-console`. |
| Add | Product interaction quality plane, canvas interaction trace and goal-to-workflow loop trace used to close the current engineering-prototype UX gap. |
| Add | V12-0P interaction experience contract for navigation IA, canvas tactile behavior, z-order, design tokens and bottom workbench tabs. |
| Add | Current-stage V12 read-only BFF-shaped acceptance slice using `/bff/v12/*` test routes, browser route logs, schema validation and screenshot evidence. |
| Add | Accepted V13 editable Studio pilot using `/bff/v13/*` test routes, WorkflowSpecGraph DTOs, graph validation, browser action logs, WorkflowDiff handoff and schema-valid evidence package. |
| Add | V14 governed extension ecosystem target: package manifests, compatibility resolver, scoped activation, unsafe denial, redacted config refs and Agent/Station binding review. |
| Add | V15 operations/deployment target: trace timeline, metrics snapshot, audit export, incident refs, deployment profile, health checks and final scenario matrix. |
| Add | PV16 product-runtime hardening target: durable entity mutation, runtime-backed run/inspect pilot, deployment health report, UX hardening report and aggregate claim-to-evidence matrix. |

## Critical Boundaries

- Studio browser routes must go through BFF route allowlist.
- Browser denylist must block direct `/v1/rpc`, internal runtime routes and
  direct workflow store writes.
- V12 canvas foundation is read-only projection. It can display nodes and
  inspector data, but cannot edit WorkflowSpecGraph or mutate runtime truth.
- V12 Figma prototype is supporting UX review evidence only. It cannot satisfy
  browser implementation, BFF boundary or runtime evidence requirements.
- V12 component prototype sketches and HTML reports are supporting UX review
  evidence only. They cannot satisfy Figma freeze, browser implementation, BFF
  boundary or runtime evidence requirements.
- shadcn-style components are product UI primitives only. They cannot bypass
  BFF/DTO policy and cannot turn read-only canvas projection into editable
  Workflow Studio semantics.
- Product polish evidence proves usability and consistency only. It cannot be
  summarized as product-grade frontend complete or Xpert-level UX complete.
- V12-0P interaction specs are product-experience contracts only. They cannot be
  used as browser implementation, BFF, DTO or runtime evidence.
- `@xyflow/react` remains the V12 canvas renderer. HarnessOS node cards,
  inspector panels and evidence states are custom product components layered on
  top of that renderer.
- Workflow graph edits produce `WorkflowDiffProposal`; publish/run requires
  confirmation.
- The accepted V13 confirm-publish-handoff produces review evidence only and
  must keep `publish_or_run_started=false` until a later runtime-backed stage
  proves execution.
- Chat workbench can propose, explain and hand off. It cannot silently publish
  or run workflow changes.
- Plugin install requires manifest validation, compatibility, tenant/workspace
  scope and policy checks.
- Tool/MCP invocation uses scoped capability binding.
- Observability is read-only unless it records audit/incident evidence through
  governed APIs.
- Interaction acceptance automation can prove visibility, route boundaries and
  UI state transitions. It cannot replace runtime evidence or human product
  quality review.

## Xpert-Inspired Frontend Target Areas

| Target Area | Required Architecture Support | Owner Stage |
| --- | --- | --- |
| Product shell and onboarding | Workspace/project inventory, browser-visible API health, route guards. | V12/V15 |
| Component prototype review | Component-level sketch pack, HTML report and reviewer decisions before full-page Figma or implementation. | V12-0A |
| Product polish and interaction quality | Shared components, visual hierarchy, responsive layout, focus states, disabled/denied/failure feedback and human review. | V12/V15 |
| Chat workbench | Conversation transcript, attachment refs, proposal timeline, tool-call blocks. | V12/V13 |
| Canvas workbench shell | Entity sidebar, read-only canvas, node selection, inspector foundation, canvas toolbar skeleton. | V12 |
| Canvas interaction loop | Selection trace, add/configure menu, node movement, edge creation, auto-layout, minimap and validation feedback. | V12/V13 |
| Goal-to-workflow loop | Goal intake, proposal timeline, graph review, revise/confirm/run and evidence review continuity. | V12/V13/V15 |
| Visual Studio canvas | WorkflowSpecGraph schema, editable nodes/edges, node inspector, graph diff/versioning. | V13 |
| Agent configuration panels | StationAgentProfile, memory/model/tool/skill/MCP bindings. | V12/V14 |
| Extension marketplace | Plugin/Skill/Tool/MCP manifests, install decisions, scoped activation. | V14 |
| Execution review | Trace timeline, run status, artifact/quality/evidence refs, tokens/cost where available. | V15 |
| Self-hosting operations | Compose profile, health checks, frontend/API config validation, rollback notes. | V15 |
