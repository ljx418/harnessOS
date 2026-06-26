# V12-V15 Target PRD

## Product Vision

HarnessOS should evolve from a CLI/TUI-first governed runtime into a usable
small-studio product. V12-V15 establish the staged product frontend,
governance and review baseline; PV16 is the current stage that must harden the
remaining product-runtime journey so a reviewer can create, inspect, edit, run
and audit multi-Agent workflows through a coherent frontend while the system
preserves the evidence, governance and runtime boundaries built in V4-V11.

The target is not to clone Xpert. The target is to close the major product
experience gap: a visible Studio, durable Agent/Station entities, workflow DSL,
plugin/skill/tool ecosystem, observability and deployable operations.

The concrete reference baseline is recorded in
`v12_to_v15_xpert_reference_audit.md`. Xpert is used as a product-experience
benchmark for workbench completeness, visual authoring, durable Agent
configuration, plugin lifecycle and execution observability. It is not used as
a claim that HarnessOS must clone Xpert or that V15 proves full Xpert parity.

The focused Xpert canvas survey recorded in
`evidence/xpert-reference/canvas-survey/index.html` recalibrates this PRD:
Xpert-level frontend interaction requires a browser workbench shell and canvas
foundation before the full visual DSL. Therefore V12 must already expose a
browser surface with navigation, entity sidebar, canvas area, node selection,
inspector foundation and BFF-only data access. V13 then makes that canvas
editable and schema-backed.

V12 browser implementation must be preceded by two prototype gates. First,
V12-0A decomposes the target workbench into component-level sketches for
topbar, navigation, canvas, node card, inspector, Chat Workbench and proposal
timeline. The sketches are reviewed in an HTML prototype report before full-page
prototype freeze. Second, V12-0P turns accepted component direction into a
Figma or approved high-fidelity prototype for product shell, workbench canvas,
inspector, Chat Workbench and evidence drawer. These prototype artifacts are
human-reviewable product experience contracts. They are not runtime evidence
and must not be used to claim Xpert parity or complete Workflow Studio.

V12-0P must also make interaction behavior explicit. The high-fidelity prototype
cannot be accepted unless it demonstrates L1/L2 navigation, canvas hover/select
/ drag / edge feedback, panel z-order, consistent design tokens and detailed
bottom workbench tabs for chat, proposal, run log, evidence, debug and
suggestions.

## Accepted V12 Baseline And Next Stage Target

The accepted V12 baseline is V12-0P plus a real-data read-only workbench
foundation, followed by V12-SD, V12-SI, V12-SQ and V12-SA bounded evidence. It
is intentionally narrower than the complete V12-V15 product vision:

1. A reviewer can open the V12-0P high-fidelity prototype and understand the
   intended product shell, canvas, inspector, Chat Workbench, evidence drawer
   and disabled action semantics.
2. A reviewer can open the HarnessOS browser workbench and see real BFF-shaped
   DTO data for workspace, project, app, station-agent, canvas and selected-node
   inspector state.
3. The browser workbench shows read-only canvas foundation behavior only:
   entity sidebar, node cards, inspector update, evidence/status refs and
   disabled reasons for unavailable publish/run/editing actions.
4. The evidence package proves route usage, schema validation, screenshot
   capture, redaction scan and No False Green scan for this bounded subgate.
5. The V12-SD/SI/SQ/SA evidence packages prove a bounded Chat Workbench
   proposal handoff, interaction depth foundation, product polish hardening and
   aggregate evidence reconciliation for review.

The current bounded V12 claim is: V12 complete for product entity, browser
workbench and read-only canvas foundation ready for review.

This baseline does not prove runtime execution, product-grade frontend
completion, Xpert parity or production deployment.

V13 has now completed a bounded editable Workflow Studio pilot slice. A
reviewer can open the V13 Studio pilot, edit the WorkflowSpecGraph visually,
see graph validation, inspect a selected node, review WorkflowDiff and confirm
a handoff without publish/run. The accepted V13 evidence is recorded under
`evidence/v13-workflow-studio-pilot/` and summarized in
`reports/v13_workflow_studio_acceptance_report.json`.

The current bounded V13 claim is: V13 complete for editable Workflow Studio
pilot slice ready for review.

This V13 result does not prove complete Workflow Studio, runtime execution,
product-grade frontend completion, Xpert parity, unrestricted automation or
production deployment.

V14 has completed a bounded governed extension ecosystem pilot. A reviewer can
inspect Plugin/Skill/Tool/MCP manifests, see compatibility decisions, bind an
approved capability to a scoped Agent/Station context and see unsafe packages
denied with visible reasons and audit refs. The accepted V14 evidence is
recorded under `evidence/v14-extension-ecosystem/` and summarized in
`reports/v14_extension_ecosystem_acceptance_report.json`.

The current bounded V14 claim is: V14 complete for governed extension
ecosystem pilot ready for review.

V15 has completed a bounded frontend interaction baseline. A reviewer can
inspect read-only trace, metrics, audit, incident and deployment-smoke evidence
from the browser, and can follow the final V12/V13/V14/V15 evidence matrix
without overclaiming production readiness. The accepted V15 evidence is
recorded under `evidence/v15-observability-deployment/` and summarized in
`reports/v15_observability_deployment_acceptance_report.json`.

The current bounded V15 claim is: V15 complete for frontend interaction
baseline ready for review.

The current completed post-V15 target is PV16: product-runtime hardening pilot
evidence. PV16 proves the bounded product outcomes not covered by V12-V15
bounded review evidence: durable product mutation, runtime-backed workflow run
and inspection, deployment hardening smoke and a coherent
setup-to-Studio-to-run-to-operations product journey. PV16 must not be used to
claim production readiness, complete Workflow Studio readiness, Agent executor
readiness, Xpert parity or product-grade frontend completion.

The accepted post-PV16 implementation target is PV17 Product Closed Loop. PV17
does not change the accepted PV16 bounded claim. It proves a bounded mainline
browser journey through setup, Product Console, Mission Studio, confirmed run,
runtime inspect and evidence review. PV17 evidence is recorded under
`evidence/pv17-product-closed-loop/` and summarized in
`reports/pv17_product_closed_loop_acceptance_report.json`.

## Target User Experience

Across the accepted V12-V15 baseline and the current PV16 target, a user can:

1. Open a web product shell, create a small-studio workspace and create a
   project.
2. Create Station Agents from the project console and configure role, goal,
   memory policy, model profile, tools, skills, MCP refs and permission
   boundaries.
3. Open a Studio canvas, build a workflow visually with start/end, station,
   tool, branch, parallel, fan-in/fan-out, evidence, quality and handoff nodes.
4. Ask the workbench to turn a natural-language goal into a WorkflowDiff
   proposal, then inspect before/after graph changes before confirmation.
5. Run a confirmed workflow and watch state progress in Studio, Mission TUI and
   execution review panels.
6. Inspect every Agent output, tool call, artifact, quality result, trace and
   evidence ref from one product surface.
7. Install or enable approved plugins, workspace skills, tools and MCP
   connectors, then bind them only to allowed Agent scopes.
8. Review trace timelines, metrics, audit export, claim scan and redaction
   results from an operations dashboard.
9. Self-host the product with documented environment, storage, queue and
   observability settings, and prove one workflow smoke from the browser.

## Current Experience Gap Closure Targets

The current V12 browser prototype proves that HarnessOS can render a browser
workbench with shared UI primitives and XyFlow. It does not yet prove a
product-grade frontend. V12-V15 must explicitly close these user-facing gaps:

| Gap | Target User Experience | Owner Stage |
| --- | --- | --- |
| Product visual quality | The product shell has a coherent hierarchy, controlled density, consistent components, readable node cards, clear status language and responsive behavior. | V12-SQ / V15 |
| Interaction depth | Selection, disabled actions, invalid actions, loading, failure and denied states all produce visible feedback and explain the safe next action. | V12-SI / V13 |
| Interaction specification depth | Navigation hierarchy, canvas tactile behavior, z-order, bottom tabs and accessibility behavior are specified before high-fidelity freeze. | V12-0P |
| Canvas workbench maturity | The canvas evolves from V12 read-only graph inspection to V13 add/configure/move/connect/auto-layout graph authoring. | V12-GC / V13 |
| Prototype and design review quality | Figma or approved high-fidelity fallback prototypes define the product shell, canvas, inspector, chat workbench and evidence drawer before implementation acceptance. | V12-GP / V12-SQ |
| Goal-to-workflow loop | A user can move from natural-language goal intake to proposal timeline, graph review, revise/confirm/run and evidence review without losing context. | V12-SD / V13 / V15 |

These targets are user-experience gates. They do not permit Xpert parity
complete, product-grade frontend complete or complete Workflow Studio ready
claims.

## Recalibrated User Experience Ladder

| Stage | User Experience Target | Evidence Boundary |
| --- | --- | --- |
| V12 | User opens a browser workbench with product navigation, workspace/project inventory, read-only canvas foundation, selected-node inspector and Chat Workbench proposal timeline. | Proves product shell and read-model projection only; does not prove complete Workflow Studio. |
| V13 | User edits WorkflowSpecGraph visually with nodes, edges, inspector, validation, WorkflowDiff and confirmation. | Proves editable Studio pilot slice; does not prove full Xpert parity or autonomous workflow editing. |
| V14 | User installs or enables scoped skills/tools/MCP capabilities and sees them bind into Agent/Station inspector panels. | Proves governed extension ecosystem pilot; does not prove unrestricted plugin ecosystem. |
| V15 | User completes the browser scenario matrix with trace, metrics, audit, deployment smoke and final interaction review. | Proves frontend interaction baseline ready for review; does not prove production GA. |
| PV16 | User creates or updates product entities, confirms a WorkflowSpec run, inspects runtime-backed progress/evidence and verifies a local hardening smoke. | Proves product-runtime hardening pilot only; does not prove production readiness or complete Studio. |
| PV17 | User follows one mainline browser product path from setup through Product Console, Studio, confirmed run, runtime inspect and evidence review. | Proves a bounded product closed loop ready for review; does not prove production readiness, complete Workflow Studio or Agent executor readiness. |

## Required User Scenarios

| Scenario | Target Experience | Required Evidence |
| --- | --- | --- |
| Canvas workbench foundation | User opens a browser workbench, sees entity sidebar, canvas area, node cards and inspector foundation before full editing is enabled. | Browser E2E, BFF route log, read-only DTO, canvas screenshot, no direct runtime store write. |
| Current V12 real-data read-only gate | User opens the V12 browser workbench and sees BFF-shaped workspace/project/app/station-agent/canvas/inspector data reflected in the UI with no publish/run/edit claim. | `evidence/v12-current-stage-real-data/`, BFF route log, browser network log, schema validation, screenshot, No False Green and redaction scans. |
| V12 accepted bounded baseline | User reviews the read-only workbench, Chat proposal handoff, visible interaction states, product polish evidence and aggregate reconciliation without seeing editable Studio or runtime execution claims. | `evidence/v12-sd-chat-workflowdiff/`, `evidence/v12-si-interaction-depth/`, `evidence/v12-sq-product-polish/`, `evidence/v12-sa-aggregate/`, PRD review, audit closure, schema validation and No False Green scans. |
| V13 editable Studio pilot | User adds, configures, moves and connects WorkflowSpecGraph nodes, sees validation feedback and reviews WorkflowDiff before confirmation. | V13 browser E2E, Studio BFF route log, graph DTOs, graph round-trip report, WorkflowDiff proposal, confirmation transcript and browser denylist evidence. |
| V14 governed extension pilot | User inspects package manifests, sees compatibility decisions, scopes an approved capability to an Agent/Station and sees unsafe packages denied with a visible reason. | V14 readiness audit, manifest schemas, compatibility report, scoped activation refs, unsafe-denial fixtures, browser screenshots, BFF route log, audit refs and redaction scan. |
| V15 operations and deployment baseline | User reviews trace/metrics/audit evidence, runs local deployment smoke and completes the final V12-V15 scenario matrix without overclaiming production readiness. | V15 readiness audit, observability DTOs, dashboard screenshots, command output, health checks, smoke result, final scenario matrix, No False Green scan and redaction scan. |
| PV16 product-runtime hardening pilot | User creates or updates workspace/project/app/Station Agent records through BFF-only routes, confirms a WorkflowSpec run, inspects runtime-backed progress/output/trace/evidence refs and follows one setup-to-operations journey. | `evidence/post-v15-product-runtime-hardening/`, entity CRUD report, runtime run inspect report, deployment health report, UX hardening report, PRD review, architecture review, acceptance runner output, No False Green and redaction scans. |
| Gemini V12-0P optimized prototype review | User reviews a dependency-reduced V12-0P Light Studio prototype that preserves the accepted V12 naming and design-only boundary. | `evidence/v12-gemini-generated-light-studio-review/`, local CSS, static render screenshot, validation report, artifact manifest and audit notes. |
| Figma prototype review | User and reviewer inspect the intended V12 browser workbench before implementation and confirm the information architecture, read-only canvas boundary and proposal-only controls. | Figma URL, prototype screenshot, review data, No False Green check; supporting UX review only. |
| Component prototype review | User and reviewer inspect the intended V12 workbench component-by-component before full-page Figma or browser implementation. | Component sketch report, imag2 or HTML wireframe refs, reviewer decisions, No False Green check; design evidence only. |
| Studio workflow creation | User creates a multi-Agent workflow in the visual Studio and saves a WorkflowSpec version. | Browser E2E, BFF route log, WorkflowSpec version, no direct runtime store write from browser. |
| Station Agent setup | User configures role, goal, memory, model, tools, skills and MCP for each station. | Entity records, audit refs, redacted credential refs, validation failures for missing policy. |
| Workflow run and inspect | User runs a confirmed workflow and sees progress, outputs, quality and evidence. | Runtime events, trace refs, artifact refs, quality refs, evidence package. |
| Plugin/Skill install | User installs an approved tool or skill package and sees it available to selected Agent scopes. | Plugin manifest, compatibility check, scoped activation, denial for unsafe package. |
| Observability review | Operator sees traces, metrics, errors, token/cost usage, claim/redaction scans and audit export. | Metrics report, trace timeline, audit export package, redaction PASS. |
| Self-hosting smoke | User starts the stack locally from documented compose/env setup and completes one workflow smoke. | Docker compose output, health checks, smoke workflow result, rollback notes. |
| Xpert-inspired onboarding | User can start from a browser onboarding / workspace entry and understand how to create the first project. | Browser screenshot, frontend/API health check, no environment mismatch, onboarding copy review. |
| Chat workbench + Studio loop | User can discuss a goal in chat, open the proposed workflow in Studio, inspect nodes and return to run review. | Chat transcript, WorkflowDiffProposal, Studio screenshot, execution review screenshot, evidence refs. |
| First-run comprehension | A new user can identify where to start, which workspace/project is active, what the system health is and how to open the workbench within 60 seconds. | Browser screenshot, visible text assertions, human review checklist. |
| Goal-to-graph-to-run review | User enters a natural-language goal, sees a proposal timeline, opens graph review, revises or confirms and follows the run evidence. | Transcript, proposal refs, graph screenshot, confirmation transcript, runtime/evidence refs. |
| Canvas action clarity | User tries available and unavailable canvas actions and receives clear feedback or disabled reasons. | Playwright action log, disabled reason screenshot, inspector state snapshot. |
| Product polish review | Reviewer checks visual hierarchy, component consistency, canvas legibility, responsive layout and no overclaim copy. | Human UX review, visual screenshots, No False Green UI scan. |

## Product Boundaries

V12-V15 must not weaken governance:

- Browser cannot directly write runtime truth.
- Studio writes only through BFF/DTO and governed WorkflowSpec APIs.
- Agent cannot directly perform durable mutation without confirmation or valid
  authorization.
- Plugin install cannot bypass compatibility, tenant/workspace scope or
  permission checks.
- Observability cannot construct runtime truth.
- Deployment docs cannot claim production GA before final evidence exists.
- Frontend screenshots and concept images cannot satisfy runtime evidence by
  themselves.
- Xpert reference screenshots are planning/reference evidence only.

## Xpert-Inspired Capabilities To Match

| Xpert Capability Class | HarnessOS Target |
| --- | --- |
| Web product console | Mission Studio / Product Console with project/workspace navigation. |
| Studio canvas workbench | Browser canvas shell, entity sidebar, node cards, inspector, add/layout/history controls and BFF-only data access. |
| Agent graph and workflow models | Durable StationAgent, WorkflowSpec, WorkflowVersion and visual DSL nodes. |
| Toolsets, skills, knowledgebases | Scoped Plugin/Skill/Tool/MCP registry with compatibility and policy checks. |
| File/project workspace | Workspace/project files and artifact refs exposed in Studio. |
| Chat/Workbench UI | Studio + Mission TUI dual surface with shared evidence model. |
| Tracing/metrics/checkpoints | Trace, metrics, audit export and evidence operations dashboard. |
| Docker/self-hosting | Compose/dev deployment and operations runbook. |

## Success Criteria For The Current Product-Runtime Target

These criteria describe the full target experience that remains under staged
review. V12-V15 already provide bounded review evidence; PV16 now provides the
missing runtime-backed and durable mutation pilot evidence needed for the
bounded product-runtime hardening review claim.

- A non-developer user can complete the primary small-studio workflow from the
  browser: create project, configure agents, build workflow, confirm run,
  inspect output and review evidence.
- A technical operator can self-host the stack and diagnose API/frontend/runtime
  health from documented dashboards and logs.
- A reviewer can verify that every positive product claim has evidence and that
  every scenario distinguishes runtime-backed evidence from reference
  screenshots or planning docs.
- A reviewer can run automated interaction checks and inspect a human review
  checklist proving navigation, canvas readability, disabled-action feedback,
  node inspector clarity, evidence classification and No False Green UI copy.
