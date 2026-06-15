# V12-V15 Current Gap Analysis

## Baseline

HarnessOS has strong runtime governance, evidence discipline and a growing
Mission TUI. It lacks the product surfaces and durable product entities needed
to feel like a mature Xpert-like platform.

V11 is complete as a bounded real-time explainable Mission TUI interaction
baseline ready for review. Xpert has been cloned and locally deployed as a
reference product. A focused Xpert Studio canvas survey was also completed.
The current gap is therefore no longer "can HarnessOS show anything"; the gap
is "can HarnessOS provide a cohesive product frontend with Studio, entity
management, extension lifecycle, observability and self-hosting evidence".

## Gap Summary

| Gap | Current HarnessOS | V15 Target | Owner Stage |
| --- | --- | --- | --- |
| Product frontend | V11 TUI baseline and partial workflow console evidence | Product Console + Mission Studio + Chat Workbench | V12/V13/V15 |
| Canvas workbench | No browser canvas workbench shell with entity sidebar, node cards and inspector foundation | Read-only canvas shell in V12, editable Workflow Studio in V13 | V12/V13 |
| Onboarding and environment health | Backend health checks exist, frontend/API mismatch can still block UX | Browser-visible onboarding, API health and config diagnostics | V12/V15 |
| Agent/Station entities | Runtime fixtures and descriptors | Durable StationAgentProfile and bindings | V12 |
| Workflow DSL | Bounded runtime graphs and docs | Visual WorkflowSpecGraph with versioning | V13 |
| Plugin/Skill ecosystem | MCP/connectors and skills mostly as docs/fixtures | Installable scoped plugin/skill/tool/MCP registry | V14 |
| Observability | Evidence packages and traces, limited product dashboard | Trace/metrics/audit/incident operations dashboard | V15 |
| Deployment | Local scripts and scattered docs | Compose/env/self-hosting smoke and runbook | V15 |

## Current Prototype Experience Gaps

The current V12 browser surface is a real HarnessOS implementation artifact,
but it is not yet strong enough to satisfy the intended product experience.

| Gap | Current State | Required Closure | Owner Stage |
| --- | --- | --- | --- |
| Visual polish | Shared components exist, but the workbench still reads as an engineering prototype. | Coherent hierarchy, density, node card styling, responsive constraints and component consistency review. | V12-Q / V15 |
| Interaction feedback | Selection and disabled states are shallow. | Click, selection, disabled, denied, loading and failure states must visibly update and explain the next safe action. | V12-I / V13 |
| Canvas maturity | Read-only XyFlow projection exists; product-level canvas interactions are incomplete. | V12 read-only clarity, V13 add/configure/move/connect/auto-layout/minimap/validation loop. | V12-C / V13 |
| Prototype quality | Figma prototype review is planned but not yet a high-fidelity accepted artifact. | Figma or approved high-fidelity fallback must describe shell, canvas, inspector, chat and evidence drawer. | V12-P / V12-Q |
| Goal-to-workflow loop | Goal intake, proposal, graph review, confirmation, run and evidence review are not one seamless loop. | Visible goal-to-proposal-to-canvas-to-run-to-evidence journey with evidence refs and no transcript-as-runtime overclaim. | V12-D / V13 / V15 |

## Priority Risks

- Overbuilding Studio before entity schemas are stable.
- Delaying all canvas work until V13, which would leave V12 without a usable
  browser workbench foundation.
- Treating Xpert reference screenshots as HarnessOS runtime evidence.
- Treating plugin install as trusted execution.
- Letting browser routes bypass BFF/DTO.
- Turning observability dashboards into runtime truth.
- Claiming Xpert parity before scenario evidence exists.
- Claiming product-grade frontend, Xpert-level UX or complete Workflow Studio
  from the current V12 engineering prototype.

## Current Documentation Support Level

| Area | Support Level | Notes |
| --- | --- | --- |
| V12 planning audit | supported | PRD, architecture, gap, roadmap, acceptance and drawio are present. |
| V12 implementation-readiness audit | supported after new V12 readiness docs are reviewed | Product/entity contracts, BFF/browser boundary, read-only canvas foundation and evidence acceptance docs are now explicit. |
| V12 direct implementation | conditional | Must wait for readiness acceptance of schema/DTO, BFF route, browser denylist and evidence package contracts. |
| V13-V15 stage implementation | supported after dependencies | V13/V14/V15 readiness docs now define schemas, boundaries, scenarios, evidence and stop conditions. |
| V13-V15 direct implementation without dependencies | not supported | Must wait for V12/V13/V14 evidence and stage-specific readiness review. |
| V15 final acceptance | not supported now | Requires V12-V14 evidence packages and deployment/observability evidence. |
