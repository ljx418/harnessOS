# V12-V15 Current Gap Analysis

## Baseline

HarnessOS has strong runtime governance, evidence discipline and a growing
Mission TUI. It lacks the product surfaces and durable product entities needed
to feel like a mature Xpert-like platform.

V11 is complete as a bounded real-time explainable Mission TUI interaction
baseline ready for review. Xpert has been cloned and locally deployed as a
reference product. A focused Xpert Studio canvas survey was also completed.
The V12-0P design direction, current V12 read-only real-data workbench subgate
and V12-SD/SI/SQ/SA evidence have now produced a bounded V12 baseline ready for
review. V13 editable Studio pilot, V14 governed extension ecosystem pilot and
V15 observability/deployment/final interaction baseline evidence have also
passed bounded acceptance. PV16 product-runtime hardening pilot evidence has
also passed bounded acceptance. The current gap is therefore no longer "can
HarnessOS show anything", "can it edit a pilot graph", "can it bind governed
extensions", "can it show operations/deployment review evidence" or "can it
demonstrate a bounded product-runtime hardening pilot"; the gap is "which
post-PV16 target should be selected next without overclaiming production,
Xpert parity or Agent executor readiness".

## Gap Summary

| Gap | Current HarnessOS | V15 Target | Owner Stage |
| --- | --- | --- | --- |
| Product frontend | V11 TUI baseline and partial workflow console evidence | Product Console + Mission Studio + Chat Workbench | V12/V13/V15 |
| Canvas workbench | V12 read-only workbench foundation and V13 editable Studio pilot exist for bounded review with BFF-shaped DTOs, route logs, schema validation, screenshots and aggregate evidence | Final interaction baseline with run/inspect continuity | V15 |
| Onboarding and environment health | Backend health checks exist, frontend/API mismatch can still block UX | Browser-visible onboarding, API health and config diagnostics | V12/V15 |
| Agent/Station entities | BFF-shaped StationAgentProfile projection is visible in the accepted V12 baseline; durable mutation/audit expansion belongs to later editable and extension stages | Durable StationAgentProfile and bindings | V13/V14 |
| Workflow DSL | V13 pilot WorkflowSpecGraph, validation and WorkflowDiff evidence exist | Runtime-backed run/inspect continuity and final matrix evidence | V15 |
| Plugin/Skill ecosystem | V14 governed extension ecosystem pilot evidence exists with manifests, scoped activation and unsafe denial | Durable ecosystem/runtime hardening after separate approval | Post-V15 option |
| Observability | V15 operations dashboard evidence exists with trace, metrics, audit and incident DTOs | Runtime-backed observability expansion after separate approval | Post-V15 option |
| Deployment | V15 bounded local smoke evidence exists with command/HTTP output | Production deployment hardening after separate approval | Post-V15 option |

## Current Prototype Experience Gaps

The current V12 browser surface is a real HarnessOS implementation artifact,
but it is not yet strong enough to satisfy the intended product experience.

| Gap | Current State | Required Closure | Owner Stage |
| --- | --- | --- | --- |
| Visual polish | Shared components exist, but the workbench still reads as an engineering prototype. | Coherent hierarchy, density, node card styling, responsive constraints and component consistency review. | V12-SQ / V15 |
| Interaction feedback | Selection and disabled states are shallow. | Click, selection, disabled, denied, loading and failure states must visibly update and explain the next safe action. | V12-SI / V13 |
| Canvas maturity | Read-only XyFlow projection exists; product-level canvas interactions are incomplete. | V12 read-only clarity, V13 add/configure/move/connect/auto-layout/minimap/validation loop. | V12-GC / V13 |
| Prototype quality | V12-0P high-fidelity and Gemini-optimized prototype packages exist for bounded design review. | Final accepted prototype path must remain aligned with implementation and human review decisions. | V12-GP / V12-SQ |
| Goal-to-workflow loop | Goal intake, proposal, graph review, confirmation, run and evidence review are not one seamless loop. | Visible goal-to-proposal-to-canvas-to-run-to-evidence journey with evidence refs and no transcript-as-runtime overclaim. | V12-SD / V13 / V15 |

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
| V12 implementation-readiness audit | supported for bounded baseline review | Product/entity contracts, BFF/browser boundary, read-only canvas foundation, V12-SD/SI/SQ evidence and V12-SA aggregate evidence are explicit. |
| V12 direct implementation | complete for this bounded stage | Further V12 work should be treated as bugfix or evidence hardening unless a new V12 scope is explicitly accepted. |
| V13 implementation | complete for bounded pilot review | V13 evidence supports editable Studio pilot slice only; it does not support complete Studio or runtime execution claims. |
| V14 implementation | complete for bounded pilot review | V14 evidence supports governed extension ecosystem pilot only; it does not support unrestricted marketplace or plugin runtime readiness. |
| V15 implementation | complete for bounded baseline review | V15 evidence supports frontend interaction baseline ready for review only; it does not support production GA, Xpert parity, product-grade frontend completion, complete Studio readiness or Agent executor readiness. |
| Post-V15 planning | complete for PV16 readiness | `post_v15_next_stage_development_and_acceptance_plan.md` and `post_v15_prd_architecture_coverage_audit.md` define the product-runtime hardening plan and PRD/architecture coverage. |
| Post-V15 bounded implementation | complete for PV16 bounded pilot review | PV16 UI, BFF smoke routes, schemas, runner spec, runner implementation, route denylist, evidence package and implementation-readiness audit exist with no open fatal or major findings. |
| Post-V15 exit claim | supported for PV16 bounded pilot review | PV16 real evidence exists and `tools/post_v15/run_product_runtime_hardening_acceptance.py` passes. |
| V15 final acceptance | supported for bounded review | V12/V13/V14/V15 evidence packages, schemas, runners, PRD reviews, architecture reviews, claim scans and redaction scans have passed for the bounded allowed claim. |

## Post-V15 Remaining Gap

The remaining gap after bounded V15 acceptance is not a missing V12-V15 review
artifact. The accepted post-V15 pilot is PV16 product-runtime hardening:

- durable workspace/project/app/Station Agent mutation with audit refs;
- runtime-backed confirmed workflow run and inspect evidence;
- self-hosting hardening with command output, health checks and rollback notes;
- full setup-to-Studio-to-run-to-operations interaction continuity.

PV16 now has planning, schemas, runner specification, implementation-readiness
audit support, implementation evidence and a PASS from the post-V15 acceptance
runner. These items must not be counted as V15 proof or as production,
complete Studio, Xpert parity or Agent executor readiness.

## PV16 Development And Acceptance Plan Summary

| PV16 Slice | User-Visible Outcome | Required Evidence |
| --- | --- | --- |
| PV16-R0 | Reviewer sees scope, PRD coverage, architecture boundaries and stop conditions before implementation. | Stage plan, PRD/architecture coverage audit, implementation-readiness audit, schemas and runner spec. |
| PV16-S1 | User creates or updates workspace, project, app and Station Agent records through BFF-only routes. | Entity CRUD report, route log, browser network log, audit refs, ownership/policy negative fixtures. |
| PV16-S2 | User confirms a WorkflowSpec run and inspects runtime-backed progress, output, trace and evidence refs. | Runtime run inspect report, event log, trace/artifact/quality refs, screenshot evidence, browser denylist. |
| PV16-S3 | Operator completes bounded self-host/deployment hardening smoke with command output. | Deployment smoke output, health report, config redaction scan, rollback notes. |
| PV16-S4 | Reviewer follows setup, Studio, run review and operations as one coherent journey. | UX hardening report, screenshots, automated UX matrix and human review. |
| PV16-SA | Reviewer accepts one bounded product-runtime hardening pilot decision. | Acceptance data, artifact manifest, claim-to-evidence matrix, No False Green scan and redaction scan. |
