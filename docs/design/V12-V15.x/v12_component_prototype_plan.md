# V12 Component Prototype Plan

## Purpose

V12 must not jump directly from PRD text to real browser implementation or a
full Figma screen. The next V12 design step is a component-level prototype pack:
split the target workbench into reviewable components, generate concept
sketches, collect human feedback, then freeze the accepted component direction
before Figma high-fidelity prototyping and real implementation.

This is a V12 design and acceptance gate. It is not runtime evidence, not
Figma evidence, not complete Workflow Studio evidence and not Xpert parity
evidence.

## V12 Prototype Sequence

```text
V12-0A Component sketch pack
  -> component-by-component human review
  -> HTML prototype sketch report
  -> accepted component direction
  -> V12-0P Figma or high-fidelity prototype gate
  -> V12 implementation-readiness audit
  -> V12 real browser implementation
```

V12 implementation cannot count browser UI evidence until V12-0A and V12-0P
are accepted.

V12-0P cannot start from images alone. It must consume the detailed interaction
contract in:

```text
docs/design/V12-V15.x/v12_0p_interaction_experience_spec.md
```

That contract freezes the L1/L2 navigation hierarchy, canvas hover/select/drag
and edge behavior, panel z-order, design-language consistency and bottom
workbench tab semantics before high-fidelity frames are accepted.

## Component Breakdown

| Component | User Question It Must Answer | Required States |
| --- | --- | --- |
| Global top bar | Where am I, what is active, and what can I safely do now? | workspace/project, environment, saved/published status, preview, proposal-only publish/run. |
| Left product navigation | Which product area am I in? | workspace, Agent, workflow, skill, MCP, evidence, ops, selected state. |
| Workspace / project / Agent sidebar | What entities exist in this project? | project tree, Agent list, workflow list, status, binding summary. |
| Canvas workbench | What workflow structure am I inspecting or editing? | dot grid, zoom/minimap, read-only/editable badge, add menu, auto-layout, selected node. |
| Agent / Station node card | What does this station Agent do? | role, goal, model, status, tools, skills, MCP refs, evidence refs, ports. |
| Edge / port / state affordance | How do nodes connect and what is valid? | input/output ports, valid edge, invalid edge, blocked edge, pending validation. |
| Right inspector | What exactly is selected and why is it allowed/blocked? | overview, configuration, policy, quality, evidence, validation, disabled reason. |
| Chat Workbench | How do I turn natural language into a proposed workflow? | goal input, assistant reply, proposal timeline, attachment refs, confirm/revise/reject. |
| WorkflowDiff / Proposal panel | What changes before I confirm? | before/after graph summary, changed nodes, risk, confirmation state. |
| Evidence / Quality / Trace drawer | How do I audit the result? | output refs, quality refs, trace refs, evidence scope, redaction, claim status. |
| Disabled / failure / permission state | Why can I not proceed? | visible reason, required action, policy/capability/audit refs. |

## Sketch Deliverables

Each component sketch must include:

- component name;
- user goal;
- visible data;
- primary actions;
- disabled or denied actions;
- empty/loading/failure states where applicable;
- boundary notes;
- acceptance checks;
- concept image or wireframe reference;
- artifact manifest entry with hash or explicit not-yet-evidence status;
- `visual_artifact_exception_reason` when a reviewer accepts a bounded
  text-only fallback;
- reviewer decision.
- interaction contract coverage for navigation, canvas, panels, tabs and
  accessibility where the component participates in those systems.

Preferred sketch source:

1. imag2-generated component concept image.
2. Local HTML/CSS wireframe if image generation is unavailable.
3. Figma component frame only after the component direction is accepted.

## First Batch

The first V12-0A review batch contains:

1. Global top bar.
2. Left product navigation.
3. Canvas workbench.
4. Agent / Station node card.
5. Right inspector.
6. Chat Workbench + Proposal Timeline.

This first batch is the minimum required before deciding whether the overall
Workbench direction is viable.

## HTML Prototype Sketch Report

The component sketches must be summarized in:

```text
docs/design/V12-V15.x/evidence/v12-component-prototype/index.html
```

The report must show:

- V12 target experience summary;
- component inventory;
- each component sketch;
- accepted / rejected / needs revision decision;
- key user flows assembled from components;
- explicit V12 boundaries;
- No False Green check;
- questions requiring human decision.

## Acceptance Criteria

V12-0A PASS requires:

- first-batch components are present;
- every component has a user goal and acceptance checks;
- at least one visual sketch or wireframe exists for each first-batch
  component;
- `component-prototype-review-data.json` validates against
  `schemas/v12_component_prototype_review.schema.json`;
- `artifact-manifest.json` validates against
  `schemas/v12_component_prototype_artifact_manifest.schema.json`;
- HTML prototype sketch report exists;
- reviewer marks each first-batch component as accepted or accepted with
  bounded revision;
- UI copy does not claim Xpert parity, product-grade frontend complete,
  complete Workflow Studio, production ready or Agent executor ready;
- prototype artifacts are marked as design evidence only.
- the V12-0P interaction contract has no unresolved critical gap for
  navigation hierarchy, canvas interactions, z-order, bottom workbench tabs or
  accessibility.

## Stop Conditions

- Component sketches are skipped and real browser implementation starts.
- A single full-page mock replaces component-level review.
- Sketches are generic flowchart blocks without product interaction details.
- Component artifacts are treated as runtime, BFF or browser implementation
  evidence.
- Reviewer rejects any first-batch component and the design still proceeds to
  Figma freeze.
- A text-only fallback is accepted without a recorded
  `visual_artifact_exception_reason`.
- The HTML report or sketches claim Xpert-level UX complete, product-grade
  frontend complete, complete Workflow Studio ready, production ready or Agent
  executor ready.
- V12-0P starts without resolving L1/L2 navigation, canvas interactions, panel
  z-order or bottom workbench tab semantics.
