# V12-V15 Experience Gap Closure Plan

## Purpose

This document records the concrete product-experience gaps observed after the
current V12 browser workbench prototype. It turns those gaps into stage-owned
development goals, acceptance evidence and stop conditions.

This plan does not expand V12 into complete Workflow Studio. V12 remains the
product shell, entity foundation, browser workbench and read-only canvas
foundation stage. Editable graph authoring remains V13 work.

## Current Assessment

The current HarnessOS browser prototype is better than a static mock because it
uses the real workflow-console app, shared component primitives and XyFlow
canvas rendering. It is still not product-grade and still falls short of the
Xpert reference experience in five areas:

| Gap | Current Problem | User Impact | Owner Stage |
| --- | --- | --- | --- |
| Product visual quality | Layout, density, hierarchy and component polish still feel like an engineering prototype. | New users cannot quickly trust or understand the surface. | V12-Q / V15 |
| Interaction depth | Node selection exists, but action menus, linked inspector states, disabled reasons and keyboard/focus patterns are shallow. | Users cannot tell what is actionable, what is blocked and what changed. | V12-I / V13 |
| Canvas workbench maturity | Canvas has read-only nodes, but lacks product-level add menu, node configuration, edge authoring, auto-layout, minimap and history interactions. | Users cannot yet build workflows visually. | V12-C / V13 |
| Prototype and design review quality | Figma prototype remains blocked by MCP limits and current fallback artifacts are not high-fidelity enough. | Engineering can drift into low-quality UI without a strong product design contract. | V12-P / V12-Q |
| Goal-to-workflow loop | Natural-language goal intake, proposal timeline, graph review, revise/confirm/run and evidence review are not yet one continuous product flow. | Users cannot complete a coherent small-studio workflow from a browser surface. | V12-D / V13 / V15 |

## Stage-Owned Closure Targets

| Target | Required Implementation | Acceptance Evidence | Stop Condition |
| --- | --- | --- | --- |
| V12-Q Product polish hardening | Shared design tokens, shadcn-style component inventory, consistent shell/toolbar/card/tabs/badge/tooltip/inspector usage, responsive layout and empty/disabled/failure states. | Product shell screenshot, workbench screenshot, component inventory review, Playwright visual hierarchy assertions, human UX review. | V12 claims product-grade UI while still using one-off static mock controls or unreadable hierarchy. |
| V12-I Interaction depth foundation | Linked node selection, inspector update feedback, disabled action explanation, read-only add/layout/history placeholders, command hints and keyboard/focus state checks. | Playwright action log, selected-node DTO snapshot, disabled reason screenshot, keyboard/focus checklist. | Clicks, disabled actions, selection or failure states silently no-op. |
| V12-C Canvas foundation hardening | XyFlow read-only graph with legible node cards, port affordance, minimap/zoom controls, entity sidebar and selected-node inspector from BFF DTOs. | Canvas read-model, browser canvas screenshot, BFF-only network log, node legibility review. | Canvas is static image/drawio/Xpert screenshot or cannot explain selected node state. |
| V13-A Editable canvas loop | Add/configure/move/connect nodes, validate edges, auto-layout, graph round-trip and WorkflowDiff before publish/run. | Browser E2E, graph DTO, before/after WorkflowDiff, no auto publish/run transcript. | Studio mutates runtime truth or publishes/runs without confirmation. |
| V15-X Interaction baseline review | Scenario matrix comparing HarnessOS against Xpert-inspired interaction dimensions with automated evidence and human review. | V12-V15 evidence packages, screenshots, network logs, DTO snapshots, human UX review, No False Green and redaction PASS. | Xpert parity, complete Workflow Studio or production ready is claimed from planning/reference evidence. |

## User-Visible Closure Scenarios

1. **First-run comprehension**: a new user opens the browser product shell and
   can identify workspace, project, API health, workbench entry and evidence
   entry without reading documentation.
2. **Goal-to-proposal-to-canvas**: a user enters a natural-language goal, sees a
   proposal timeline, opens the proposed graph in the workbench and understands
   the read-only or editable status.
3. **Canvas inspection**: a user selects a Station Agent node and the inspector
   updates with role, goal, memory, model, tool, skill, MCP, quality and evidence
   refs.
4. **Action clarity**: a user tries an unavailable add/layout/publish/run action
   and receives a visible reason instead of a silent no-op.
5. **Editable graph pilot**: in V13, a user adds, configures, moves and connects
   workflow nodes, then reviews a WorkflowDiff before confirmation.
6. **Evidence review**: a user follows output, quality, trace and evidence refs
   from the same product surface without raw secret, raw prompt or raw artifact
   leakage.

## Automation And Human Review

Automated tests must cover:

- browser screenshot at desktop and at least one constrained viewport;
- visual hierarchy and node legibility assertions;
- selected-node inspector updates;
- disabled action visible reason;
- browser network denylist;
- goal-to-proposal-to-canvas visible flow;
- graph edit round-trip in V13;
- UI copy No False Green scan;
- redaction scan.

Human review must cover:

- whether the interface feels like a coherent product surface instead of an
  internal test harness;
- whether the graph canvas is readable at default zoom;
- whether the user can understand the current state and next safe action;
- whether disabled or denied actions explain why they are unavailable;
- whether product copy avoids Xpert parity, production readiness and complete
  Workflow Studio claims.

## Claim Guard

Allowed:

- V12-Q complete: product polish hardening slice ready for review.
- V12-I complete: interaction depth foundation slice ready for review.
- V13 complete: editable Workflow Studio pilot slice ready for review.
- V15 complete: Xpert-level frontend interaction baseline ready for review.

Forbidden:

- Xpert-level UX complete.
- Xpert-quality canvas ready.
- product-grade frontend complete.
- complete Workflow Studio ready.
- production ready.
- 已完全追平 Xpert.
- Xpert 级交互已完成.
- 低代码画布已完成.
- 产品级前端已完成.

