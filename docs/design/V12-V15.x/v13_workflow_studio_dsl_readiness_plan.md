# V13 Workflow Studio And Visual DSL Readiness Plan

## Current Decision

V13 is blocked until V12 product entity, BFF, workbench and read-only canvas
foundation evidence exists. This document supports V13
implementation-readiness review after V12 PASS.

Allowed after V12 PASS:

- Workflow Studio visual authoring planning.
- WorkflowSpecGraph schema and browser/BFF route planning.
- WorkflowDiffProposal and confirmation-flow planning.
- Browser E2E and graph round-trip fixture planning.

Blocked:

- Direct runtime execution from Studio.
- Browser direct writes to WorkflowStore, StationRun or Artifact.
- Complete Workflow Studio ready claim.
- V14/V15 implementation before V13 evidence exists.

## V13 Objective

V13 lets a user create, inspect and edit a multi-Agent workflow visually from
the browser. It builds on the V12 browser canvas shell and turns the read-only
projection into an editable, schema-backed Studio. The output is a validated
`WorkflowSpecGraph` and `WorkflowDiffProposal`. Publish/run remain
confirmation-gated and governed by existing runtime boundaries.

## Required Schemas And DTOs

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

Required node types:

- `start`
- `end`
- `station`
- `tool`
- `branch`
- `parallel`
- `fan_in`
- `fan_out`
- `quality`
- `evidence`
- `handoff`

Required graph rules:

- exactly one start node
- at least one end node
- no dangling required edge
- `fan_in` must reference upstream branch refs
- `fan_out` must preserve downstream branch refs
- station node must reference a valid `StationAgentProfile`
- tool node must reference scoped capability binding
- evidence/quality nodes cannot construct runtime truth

## BFF And Browser Boundary

Allowed Studio routes:

- `GET /bff/v13/workflows/:workflow_id/graph`
- `POST /bff/v13/workflows/:workflow_id/graph/validate`
- `POST /bff/v13/workflows/:workflow_id/diff`
- `GET /bff/v13/workflow-diff/:proposal_id`
- `POST /bff/v13/workflow-diff/:proposal_id/revise`
- `POST /bff/v13/workflow-diff/:proposal_id/reject`
- `POST /bff/v13/workflow-diff/:proposal_id/confirm-publish-handoff`
- `GET /bff/v13/studio/node-inspector/:node_id`

Forbidden from browser:

- direct workflow store writes
- direct runtime execution routes
- direct station run mutation
- direct artifact writes
- hidden apply/publish/run forms

## Implementation Slices

### V13-1 Graph Schema And Validation

Exit evidence:

- graph schema parse PASS
- invalid node type rejected
- dangling edge rejected
- invalid fan-in/fan-out rejected
- station without Agent profile rejected

### V13-2 Studio Canvas And Inspector

Exit evidence:

- browser screenshot of canvas
- node inspector screenshot
- node add/select/move/connect evidence
- station Agent inspector uses V12 Agent profile refs
- browser network log contains only BFF routes

### V13-3 WorkflowDiff And Versioning

Exit evidence:

- before/after graph refs
- diff summary
- append-only version proposal
- confirmation transcript
- no auto publish/run

### V13-4 Studio E2E Acceptance

Exit evidence:

- user creates workflow graph
- user edits station/tool/branch nodes
- graph round-trip PASS
- WorkflowDiffProposal generated
- publish/run remains gated

## User Scenarios

### US-V13-01 Visual Multi-Agent Workflow Authoring

User creates a workflow with start, two station nodes, a parallel branch, fan-in
and evidence node.

PASS:

- graph validates
- screenshot exists
- WorkflowSpecGraph exists
- no direct runtime call appears

### US-V13-02 Workbench To Studio Loop

User starts from V12 Workbench proposal and opens it in Studio.

PASS:

- shared WorkflowDiffProposal ref exists
- Studio shows before/after graph
- revise/reject/confirm controls are visible
- confirm produces handoff, not runtime execution

### US-V13-03 Inspector Review

User clicks station and tool nodes and sees Agent role, goal, tools, skills,
MCP refs and evidence refs.

PASS:

- inspector refs match V12 entities
- raw credential material absent
- UI does not claim complete Workflow Studio ready

## V13 Evidence Package

```text
docs/design/V12-V15.x/evidence/v13-workflow-studio-dsl/
```

Required:

- `v13-acceptance-data.json`
- `studio-canvas-screenshot.png`
- `node-inspector-screenshot.png`
- `workflow-spec-graph.json`
- `workflow-diff-proposal.json`
- `graph-roundtrip-report.json`
- `browser-network-log.json`
- `confirmation-transcript.txt`
- `redaction-scan.txt`
- `no-false-green-scan.txt`
- `prd-spec-review.md`

## V13 Stop Conditions

- Studio publishes or runs without user confirmation.
- V13 implementation starts before V12 read-only canvas foundation PASS.
- Browser writes internal workflow/runtime store directly.
- Graph cannot round-trip through schema validation.
- Hidden mutation form exists.
- Inspector leaks raw credential, raw prompt or raw artifact content.
- UI copy claims complete Workflow Studio ready.
