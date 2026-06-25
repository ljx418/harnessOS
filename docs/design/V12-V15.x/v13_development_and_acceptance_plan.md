# V13 Development And Acceptance Plan

## Purpose

This document is the executable development and acceptance plan for the V13
editable Workflow Studio pilot. It assumes the accepted V12 bounded baseline is
available and does not expand V13 into complete Studio, runtime execution,
production readiness or Xpert parity.

## Stage Goal

V13 lets a reviewer create, inspect and edit a small multi-Agent
`WorkflowSpecGraph` from the browser, validate the graph, generate a
`WorkflowDiffProposal`, and confirm a governed publish handoff. It does not run
the workflow.

Allowed V13 exit claim:

```text
V13 complete: editable Workflow Studio pilot slice ready for review.
```

## Development Slices

| Order | Stage | Build Scope | Acceptance Gate | Evidence Package |
| --- | --- | --- | --- | --- |
| 0 | V13-R0 | Readiness audit, route allowlist, browser denylist, schema and evidence contract confirmation. | No open fatal or major readiness finding. | `v13_implementation_readiness_audit.md` |
| 1 | V13-S1 | WorkflowSpecGraph, node/edge schema, validation result, graph fixtures and `/bff/v13/*` test routes. | Valid graph PASS; invalid node, dangling edge and invalid fan-in/fan-out FAIL. | `evidence/v13-workflow-studio-dsl/` |
| 2 | V13-S2 | Editable Studio canvas: add/select/move/connect/configure nodes, linked inspector and visible validation feedback. | Browser screenshot, action log, inspector screenshot and network log prove user-visible editing through BFF only. | `evidence/v13-workflow-studio-dsl/` |
| 3 | V13-S3 | WorkflowDiffProposal, before/after refs, revise/reject/confirm controls and confirmation handoff. | WorkflowDiff waits for explicit confirmation and produces handoff evidence only. | `evidence/v13-workflow-studio-dsl/` |
| 4 | V13-SA | Aggregate V13 evidence, PRD review, architecture review, No False Green and redaction closure. | Every V13 positive claim maps to evidence; no forbidden claim appears. | `evidence/v13-workflow-studio-dsl/` |

## Required Interfaces

Required DTOs:

- `WorkflowSpecGraph`
- `WorkflowSpecNode`
- `WorkflowSpecEdge`
- `WorkflowVersion`
- `WorkflowDiffProposal`
- `StudioCanvasState`
- `NodeInspectorProjection`
- `StationAgentInspectorProjection`
- `WorkflowValidationResult`
- `StudioConfirmationHandoff`

Required BFF route allowlist:

- `GET /bff/v13/workflows/:workflow_id/graph`
- `POST /bff/v13/workflows/:workflow_id/graph/validate`
- `POST /bff/v13/workflows/:workflow_id/diff`
- `GET /bff/v13/workflow-diff/:proposal_id`
- `POST /bff/v13/workflow-diff/:proposal_id/revise`
- `POST /bff/v13/workflow-diff/:proposal_id/reject`
- `POST /bff/v13/workflow-diff/:proposal_id/confirm-publish-handoff`
- `GET /bff/v13/studio/node-inspector/:node_id`

Forbidden browser routes:

- direct workflow store writes
- direct runtime execution routes
- direct station run mutation
- direct artifact writes
- hidden apply, publish or run forms

## Acceptance Criteria

- User can open Studio from the V12 workbench context.
- User can add start, station, tool, branch, fan-in, fan-out, quality, evidence
  and end nodes.
- User can select nodes and see inspector data that matches DTO refs.
- User can move nodes and connect valid edges with visible feedback.
- Invalid graph states render clear validation messages.
- Valid graph round-trips through schema validation.
- WorkflowDiffProposal contains before/after graph refs and diff summary.
- Revise and reject do not mutate runtime truth.
- Confirm produces a governed handoff and no runtime execution evidence.
- Browser network log contains only allowed BFF routes.
- Evidence package validates against V13 schemas.
- PRD review, target architecture review, No False Green and redaction scans
  pass.

## Evidence Package Minimum

Required path:

```text
docs/design/V12-V15.x/evidence/v13-workflow-studio-dsl/
```

Required artifacts:

- `v13-acceptance-data.json`
- `artifact-manifest.json`
- `studio-canvas-screenshot.png`
- `node-inspector-screenshot.png`
- `workflow-spec-graph.json`
- `workflow-diff-proposal.json`
- `graph-roundtrip-report.json`
- `browser-action-log.json`
- `browser-network-log.json`
- `bff-route-log.json`
- `confirmation-transcript.txt`
- `prd-spec-review.md`
- `target-architecture-review.md`
- `audit-opinion.md`
- `audit-closure.md`
- `redaction-scan.txt`
- `no-false-green-scan.txt`

## Stop Conditions

- V13 implementation starts before V13-R0 readiness audit is closed.
- Browser writes internal workflow/runtime store directly.
- Studio auto applies, publishes or runs without confirmation.
- Graph cannot round-trip through schema validation.
- Canvas actions silently no-op or hide validation failures.
- Inspector leaks raw credential, raw prompt or raw artifact content.
- Evidence uses V12 design-only or Xpert reference material as HarnessOS
  implementation evidence.
- UI copy claims complete Workflow Studio ready, production ready, Xpert parity
  complete, product-grade frontend complete or Agent executor ready.
