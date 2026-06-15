# V12-V15 Target PRD

## Product Vision

HarnessOS should evolve from a CLI/TUI-first governed runtime into a usable
small-studio product. By V15, a user should be able to create, inspect, edit,
run and audit multi-Agent workflows through a polished product frontend while
the system preserves the evidence, governance and runtime boundaries built in
V4-V11.

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

## Target User Experience

At the end of V15, a user can:

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
| Product visual quality | The product shell has a coherent hierarchy, controlled density, consistent components, readable node cards, clear status language and responsive behavior. | V12-Q / V15 |
| Interaction depth | Selection, disabled actions, invalid actions, loading, failure and denied states all produce visible feedback and explain the safe next action. | V12-I / V13 |
| Interaction specification depth | Navigation hierarchy, canvas tactile behavior, z-order, bottom tabs and accessibility behavior are specified before high-fidelity freeze. | V12-0P |
| Canvas workbench maturity | The canvas evolves from V12 read-only graph inspection to V13 add/configure/move/connect/auto-layout graph authoring. | V12-C / V13 |
| Prototype and design review quality | Figma or approved high-fidelity fallback prototypes define the product shell, canvas, inspector, chat workbench and evidence drawer before implementation acceptance. | V12-P / V12-Q |
| Goal-to-workflow loop | A user can move from natural-language goal intake to proposal timeline, graph review, revise/confirm/run and evidence review without losing context. | V12-D / V13 / V15 |

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

## Required User Scenarios

| Scenario | Target Experience | Required Evidence |
| --- | --- | --- |
| Canvas workbench foundation | User opens a browser workbench, sees entity sidebar, canvas area, node cards and inspector foundation before full editing is enabled. | Browser E2E, BFF route log, read-only DTO, canvas screenshot, no direct runtime store write. |
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

## Success Criteria By V15

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
