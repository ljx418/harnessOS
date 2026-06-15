# V12 Figma Prototype Review Plan

## Purpose

V12 implementation must not start from abstract PRD text alone. Before browser
UI implementation, HarnessOS needs a Figma prototype that makes the intended
product experience reviewable by humans.

Before that full Figma prototype is frozen, V12 must pass the component-level
prototype sketch gate in `v12_component_prototype_plan.md`. The component sketch
gate decomposes the page into reviewable parts, lets the user accept or reject
the intended interaction direction, and reduces full-page Figma rework.

The prototype is a product-experience contract for V12. It is not runtime
evidence, not Xpert parity evidence, and not proof of complete Workflow Studio.

The prototype must align with the implementation component baseline:
shadcn-style product components backed by Radix primitives, lucide icons,
Tailwind/CVA variants and XyFlow canvas patterns. The review should reject
screens that look like ad-hoc mockups or generic flowcharts.

When Figma editing is unavailable or delayed, V12-0P may use the local
high-fidelity prototype package in
`evidence/v12-0p-high-fidelity-prototype/index.html` as the temporary
product-experience freeze input. That package remains design-only and must not
be counted as browser implementation evidence, BFF evidence, DTO evidence or
runtime evidence.

## Figma File

Canonical prototype file:

```text
https://www.figma.com/design/OU9PQsSpHwUsv1kiI7r8OP/HarnessOS
```

The file should contain editable Figma layers, not only screenshots or flattened
images.

## Required Prototype Screens

| Screen | Required Content | V12 Boundary |
| --- | --- | --- |
| Product Shell / Onboarding | Global navigation, workspace/project/app entry, API health and environment status. | Product shell only; no production readiness claim. |
| Browser Workbench Canvas | Xpert-inspired global nav, entity sidebar, top toolbar, read-only dot-grid canvas, node cards, edge links, minimap and canvas toolbar. | Read-only canvas foundation; no editable Workflow Studio claim. |
| Selected Node Inspector | Agent/station role, goal, memory, model, tools, skills, MCP refs, policy refs, evidence refs and validation messages. | Inspector projection only; no Agent executor readiness claim. |
| Chat Workbench / Proposal Timeline | Natural-language goal input, proposal timeline, WorkflowDiff handoff, confirm/revise/reject states. | Proposal handoff only; no silent publish/run. |
| Evidence / Quality Drawer | Runtime report refs, evidence chain refs, quality refs, redaction status and claim status. | Supporting review surface; does not construct runtime truth. |

## Required Pre-Figma Component Inputs

The Figma prototype should be built only after these V12-0A component
directions are accepted:

- global top bar;
- left product navigation;
- workspace/project/Agent sidebar;
- canvas workbench;
- Agent / Station node card;
- right inspector;
- Chat Workbench + proposal timeline.

The Figma prototype may refine visual detail, but it must not silently change
accepted component responsibilities or V12 boundaries.

## Component Quality Gate

The Figma redesign should include reusable component groups for:

- Product rail / global navigation item.
- Workspace/project/app switcher.
- Toolbar button, disabled action and tooltip.
- Status badge, quality badge and evidence scope badge.
- XyFlow-style node card with role, provider/model, status, evidence and port
  affordances.
- Selected-node inspector row and validation message.
- Chat Workbench message, proposal timeline item and WorkflowDiff handoff.
- Evidence/quality drawer row.

PASS requires the reviewer to recognize these as reusable product components,
not one-off rectangles.

## Required Interaction States

The prototype must show at least these states:

- Empty workspace / onboarding state.
- Canvas loaded with at least one trigger node, one station-agent node and one
  tool/skill/MCP node.
- Node selected state with right-side inspector open.
- Add/layout/history/publish actions visible as disabled, bounded or
  proposal-only controls when V12 cannot implement the behavior.
- Chat Workbench proposal state with `awaiting_user_confirmation` or
  `handoff_ready`.
- Browser boundary warning that the browser must use BFF/DTO routes only.

## Design Quality Criteria

The V12 prototype should move toward the Xpert canvas benchmark while preserving
HarnessOS semantics:

- Quiet product shell with dense but readable operational layout.
- Clear hierarchy: global navigation, entity sidebar, canvas, inspector and
  evidence drawer.
- Node cards must expose status, model/provider, role and evidence state.
- Inspector must make Agent capability boundaries visible.
- Toolbar actions must communicate whether they are read-only, disabled or
  proposal-only.
- UI copy must stay in Simplified Chinese.
- Prototype must avoid marketing hero layouts and decorative-only gradients.
- Prototype should match the density of a professional low-code workbench:
  compact buttons, clear toolbars, readable inspector forms and deliberate
  empty/disabled states.

## Prototype Review Checklist

| Check | PASS Condition |
| --- | --- |
| Editable Figma layers | Reviewer can inspect and edit major UI groups as layers. |
| Component sketch handoff | Reviewer can trace Figma screens back to accepted V12-0A component sketches. |
| Information architecture | Reviewer can identify workspace/project/app, canvas, node inspector, chat workbench and evidence surfaces. |
| V12 boundary visibility | Prototype clearly states V12 is read-only canvas foundation and proposal handoff. |
| Xpert reference usage | Prototype borrows workbench patterns but does not copy Xpert assets or claim parity. |
| Runtime truth boundary | Browser/BFF-only boundary is visible; prototype does not imply direct runtime writes. |
| No False Green | No positive claim says Xpert parity complete, complete Workflow Studio ready, production ready or Agent executor ready. |
| Component quality | Core controls resemble shadcn/Radix-style reusable product primitives, not isolated mockup shapes. |

## Required Evidence

V12 evidence package should include:

- `figma-prototype-url.txt`
- `figma-prototype-screenshot.png`
- `figma-prototype-review.md`
- `figma-prototype-review-data.json`
- `../v12-component-prototype/index.html` or equivalent component sketch
  report reference.

These files support UX review only. V12 PASS still requires HarnessOS browser
implementation screenshots, BFF logs, DTO snapshots, network denylist evidence,
redaction scan and No False Green scan.

## Stop Conditions

- Figma prototype is used as HarnessOS runtime evidence.
- Figma freeze starts before V12-0A component prototype report is accepted.
- Prototype is a single flattened screenshot with no editable structure.
- Prototype claims complete Workflow Studio, Xpert parity complete, production
  ready or Agent executor ready.
- Prototype hides V12 read-only canvas boundary.
- Prototype includes Apply / Publish / Run controls without disabled,
  proposal-only or confirmation semantics.
