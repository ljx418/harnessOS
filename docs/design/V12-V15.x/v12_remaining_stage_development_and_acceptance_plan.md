# V12 Remaining Stage Development And Acceptance Record

## Purpose

This document records the accepted execution plan and completed acceptance
contract for the remaining V12 work after the V12 read-only real-data gate.
It remains the audit trail for V12-SD, V12-SI, V12-SQ and V12-SA, and it is
also the dependency reference before V13 readiness review.

The record is intentionally bounded. It supports these V12 substages only:

- V12-SD: Chat Workbench to WorkflowDiff proposal handoff.
- V12-SI: interaction depth foundation.
- V12-SQ: product polish hardening.
- V12-SA: aggregate evidence reconciliation.

It does not authorize V13 implementation, editable Workflow Studio claims,
runtime execution claims, production deployment claims or Xpert parity claims.

## Naming Rule

This plan uses `V12-G*` for V12 gates and `V12-S*` for V12 development
substages. The former `M12-*` milestone labels are historical only and must not
be used as executable names in new evidence packages, audit reports or commit
messages.

| Current Name | Type | Meaning |
| --- | --- | --- |
| V12-G0P | Gate | V12-0P optimized prototype/design gate. |
| V12-GR | Gate | Read-only real-data workbench gate. |
| V12-SD | Substage | Chat Workbench to WorkflowDiff handoff. |
| V12-SI | Substage | Interaction depth foundation. |
| V12-SQ | Substage | Product polish hardening. |
| V12-SA | Aggregate | Aggregate evidence reconciliation. |

## Current Accepted Baseline

| Baseline Item | Status | Evidence |
| --- | --- | --- |
| V12-0P high-fidelity direction | accepted for bounded design review | `evidence/v12-0p-high-fidelity-prototype/` |
| Gemini optimized V12-0P prototype | accepted for bounded design review | `evidence/v12-gemini-generated-light-studio-review/` |
| V12 read-only real-data workbench gate | accepted for bounded current-stage review | `evidence/v12-current-stage-real-data/` |
| V12-SD Chat to WorkflowDiff handoff | accepted for bounded review | `evidence/v12-sd-chat-workflowdiff/` |
| V12-SI interaction depth foundation | accepted for bounded review | `evidence/v12-si-interaction-depth/` |
| V12-SQ product polish hardening | accepted for bounded review | `evidence/v12-sq-product-polish/` |
| V12-SA aggregate reconciliation | accepted for bounded review | `evidence/v12-sa-aggregate/` |
| Bounded V12 exit | accepted for review | Product entity, browser workbench and read-only canvas foundation ready for review. |
| MVP effect | not accepted as a full product claim | V12 does not prove editable Studio, runtime execution, product-grade frontend completion, Xpert parity or production readiness. |

## Documentation Coverage Assessment

| Area | Current Coverage | Gap | Required Closure |
| --- | --- | --- | --- |
| PRD target | strong | No open V12 fatal or major documentation gap for the bounded claim. | Preserve this document as the substage execution record. |
| Target architecture | strong | V12-SD, V12-SI and V12-SQ route and DTO evidence are tied to the accepted V12 baseline. | Keep evidence package paths fixed for review. |
| Milestones | strong | V12-SD/SI/SQ/SA are named execution substages and mapped in the milestone roadmap. | Keep future execution names in V13/V14/V15 format. |
| Acceptance gates | strong for bounded V12 | Substage-specific stop conditions and evidence package expectations exist. | Do not use V12 evidence as V13 editable Studio or runtime evidence. |
| Gap drawio | strong for human direction review | Diagram is directional, not a replacement for executable acceptance. | Keep drawio as review artifact; use this document for execution. |
| Audit closure | medium | Current subgate closure exists; remaining substages need repeatable closure criteria. | Every substage must produce PRD review, audit opinion and audit closure. |

Audit opinion: documentation is sufficient to support the accepted bounded V12
review claim and to start V13 readiness planning. It is not sufficient to start
V13 implementation until the V13 readiness audit accepts schemas, routes,
fixtures, evidence package structure and stop conditions.

## Global Rules Used For Remaining V12 Substages

Every remaining V12 substage must complete this loop before implementation:

1. Define user-visible outcome and non-goals.
2. Define DTOs, routes, UI states and evidence package path.
3. Run PRD specification review against `v12_to_v15_target_prd.md`.
4. Run target architecture review against
   `v12_to_v15_target_architecture.md`.
5. Produce audit opinion and close all fatal or major findings.
6. Enter implementation only after no open fatal or major audit item remains.

Every remaining V12 substage must complete this loop after implementation:

1. Run live browser or real BFF-shaped acceptance.
2. Validate schema, route log, browser network log, screenshot and scans.
3. Re-run PRD specification review.
4. Re-run target architecture review.
5. Produce audit closure.
6. Mark PASS only if user-visible behavior and evidence both match the plan.

If a substage cannot use live browser evidence in the current environment, it
must fall back to a documented headless browser acceptance runner that records
equivalent screenshot, route, network and schema evidence.

## V12-SD: Chat Workbench To WorkflowDiff Proposal Handoff

### Target User Experience

The user enters a natural-language goal in the V12 workbench. The workbench
shows a proposal timeline with parsed intent, changed areas, risk notes and a
WorkflowDiff proposal reference. The user can revise, reject or open graph
review. The UI must make clear that no publish, run or durable graph mutation
has occurred.

### Required Architecture

| Layer | Requirement |
| --- | --- |
| Browser UI | Chat input, transcript, proposal timeline, proposal status, graph-review entry and disabled publish/run reasons. |
| BFF route | `/bff/v12/workbench/*` or equivalent V12 BFF-shaped test route. |
| DTO | `WorkbenchConversation`, `GoalIntakeMessage`, `WorkbenchProposalTimeline`, bounded `WorkflowDiffProposalRef`. |
| Evidence | Transcript fixture, proposal DTO, browser screenshot, BFF route log, browser network log, redaction scan, No False Green scan. |

### Acceptance Criteria

- User can submit or load a goal and see a proposal timeline.
- Proposal contains a WorkflowDiff reference or explicit pending reason.
- Proposal can be revised or rejected without runtime execution.
- Graph review entry is visible but cannot silently publish or run.
- Browser network log stays inside allowed BFF routes.
- UI copy never treats transcript or proposal as runtime evidence.

### Stop Conditions

- Chat transcript is stored or described as runtime truth.
- Proposal auto-applies, publishes or runs.
- WorkflowDiff reference is missing while the UI claims proposal readiness.
- Browser calls internal runtime or workflow store routes directly.

## V12-SI: Interaction Depth Foundation

### Target User Experience

The user can select nodes, attempt unavailable actions, encounter invalid or
denied states and understand the next safe action from visible feedback.
Inspector content, node highlight, bottom workbench state and evidence/status
copy must stay synchronized.

### Required Architecture

| Layer | Requirement |
| --- | --- |
| Browser UI | Selection state, disabled action tooltips or reasons, denied/failure/loading states, focus-visible states and bottom tab state. |
| BFF route | Existing `/bff/v12/*` plus any interaction trace test endpoint needed for acceptance. |
| DTO | `CanvasInteractionTrace`, selected-node DTO snapshot, disabled action reason list, failure/denied state fixture. |
| Evidence | Browser action log, screenshots for selection and disabled states, route/network log, DTO snapshot and accessibility/focus note. |

### Acceptance Criteria

- Selecting a node updates canvas highlight and inspector with matching DTO id.
- Disabled add, layout, publish and run controls expose visible reasons.
- Invalid edge or denied action fixtures render a visible blocked state.
- Loading and failure states are represented without layout collapse.
- Keyboard focus states are visible for primary controls.

### Stop Conditions

- Clicks silently no-op.
- Inspector remains stale after selection.
- Disabled actions have no reason.
- Failure, denied or loading states are invisible.
- Interaction evidence is only a static screenshot without action log.

## V12-SQ: Product Polish Hardening

### Target User Experience

The V12 workbench should feel like a coherent low-code product surface rather
than an engineering prototype. A reviewer should understand the active
workspace, project, app, health state, canvas, inspector, chat area, evidence
refs and unavailable actions within the first review pass.

### Required Architecture

| Layer | Requirement |
| --- | --- |
| Component system | Shared UI primitives for navigation, buttons, tabs, tooltip, scroll area, status, node card and inspector shell. |
| Layout | Desktop and constrained-width layouts with stable dimensions and no incoherent overlaps. |
| Copy | Simplified Chinese user-facing copy, bounded claims and visible disabled reasons. |
| Evidence | Desktop screenshot, constrained screenshot, component inventory review, human UX review, visual overlap scan and claim scan. |

### Acceptance Criteria

- Desktop and constrained screenshots show readable hierarchy.
- Node cards, toolbar, inspector and bottom tabs use consistent component
  treatment.
- Text does not overflow or overlap in core workbench surfaces.
- Disabled and read-only states are visually distinct.
- Human UX review records no fatal or major readability issue.

### Stop Conditions

- UI remains unreadable or visually incoherent while claiming polish PASS.
- Primary text overlaps, clips or hides core controls.
- Component usage is bespoke and inconsistent for core surfaces.
- Human UX review is missing.

## V12-SA: V12 Aggregate Evidence Reconciliation

### Target User Experience

A reviewer can inspect one V12 evidence map and understand which V12 user
experiences are proven, which are design-only and which remain future work.

The aggregate validator contract is defined in
`v12_sa_aggregate_validator_spec.md`.

### Required Inputs

| Input | Required Status |
| --- | --- |
| V12-G0P optimized prototype package | PASS for design-only review |
| V12-GR read-only real-data gate | PASS for bounded current-stage review |
| V12-SD Chat to WorkflowDiff handoff | PASS or explicitly bounded partial |
| V12-SI interaction depth foundation | PASS or explicitly bounded partial |
| V12-SQ product polish hardening | PASS or explicitly bounded partial |
| PRD review | No open fatal or major mismatch |
| Audit closure | No open fatal or major false-green risk |

### Acceptance Criteria

- Evidence map links every V12 positive claim to evidence.
- Design-only, browser-backed, BFF-backed and runtime-backed evidence are
  clearly classified.
- Missing evidence is `BLOCKED`.
- Design-only evidence used as browser evidence is `FAIL`.
- Xpert reference material used as HarnessOS implementation or runtime evidence
  is `FAIL`.
- No forbidden completion claim appears outside safe guard or stop-condition
  contexts.
- Remaining V13/V14/V15 dependencies are listed as future work.
- The exit claim remains bounded unless every V12 gate has accepted PASS.

### Stop Conditions

- Any positive V12 claim lacks evidence.
- Prototype evidence is counted as runtime or browser implementation evidence.
- Current V12-GR subgate is treated as full V12 completion.
- V13 starts from incomplete V12 dependency evidence.

## Required Evidence Package Layout

Each remaining substage wrote or must preserve evidence under:

```text
docs/design/V12-V15.x/evidence/<stage-id>/
  acceptance-data.json
  browser-screenshot.png
  browser-network-log.json
  bff-route-log.json
  schema-validation-report.json
  prd-spec-review.md
  target-architecture-review.md
  audit-opinion.md
  audit-closure.md
  no-false-green-scan.txt
  redaction-scan.txt
```

The exact DTO filenames may vary by substage, but each evidence package must
include enough structured data to replay the acceptance reasoning without
trusting screenshots alone.

`acceptance-data.json` must validate against
`schemas/v12_remaining_stage_acceptance_data.schema.json`.

`artifact-manifest.json` must validate against
`schemas/v12_remaining_stage_artifact_manifest.schema.json`.

The default local acceptance command is:

```bash
python3 tools/v12/run_v12_remaining_stage_acceptance.py
```

## Current Development Direction Review Checklist

Before starting the next implementation task, the reviewer should inspect:

- `v12_to_v15_current_gap_analysis.drawio`, especially pages 2, 3, 5 and 7.
- This document's V12-SD, V12-SI, V12-SQ and V12-SA sections and evidence
  package paths.
- The current-stage evidence package under `evidence/v12-current-stage-real-data/`.

If the reviewer finds that the drawio overstates completion, hides remaining
V12 risks or implies editable Studio/runtime readiness, development must pause
and the documents must be corrected before V13 readiness or implementation
resumes.
