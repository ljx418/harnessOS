# V12 Component Prototype Execution Plan

## Decision

V12-0A is the next design execution stage. It is a documentation and prototype
stage only. It must finish before V12-0P Figma/high-fidelity prototype freeze
and before any new V12 browser UI implementation is accepted.

Allowed:

- Component decomposition.
- imag2 concept image prompts and outputs.
- Local HTML/CSS wireframe fallback.
- HTML prototype sketch report.
- Human component-by-component review.
- No False Green and redaction scan for prototype text.

Blocked:

- New browser runtime implementation.
- Full Figma freeze before component decisions.
- Treating component sketches as runtime, browser, BFF or WorkflowSpec evidence.
- Any claim of product-grade frontend complete, Xpert-level UX complete,
  complete Workflow Studio ready, production ready or Agent executor ready.

## Output Directory

All V12-0A outputs should live under:

```text
docs/design/V12-V15.x/evidence/v12-component-prototype/
```

Required files:

```text
index.html
component-prototype-review.md
component-prototype-review-data.json
artifact-manifest.json
no-false-green-scan.txt
redaction-scan.txt
assets/
  01-global-top-bar.png
  02-left-product-navigation.png
  03-canvas-workbench.png
  04-agent-station-node-card.png
  05-right-inspector.png
  06-chat-workbench-proposal-timeline.png
wireframes/
  01-global-top-bar.html
  02-left-product-navigation.html
  03-canvas-workbench.html
  04-agent-station-node-card.html
  05-right-inspector.html
  06-chat-workbench-proposal-timeline.html
```

Image files may be replaced by documented fallback wireframes if imag2 is
unavailable. Missing visual artifacts block V12-0A PASS unless the reviewer
explicitly accepts a bounded text-only design decision and records
`visual_artifact_exception_reason` in `component-prototype-review-data.json`.
`artifact-manifest.json` may exist as `PLANNED_NOT_EVIDENCE` before execution,
but it cannot satisfy V12-0A PASS until real asset or wireframe hashes and
review decisions are filled.

## First-Batch Component Acceptance Matrix

| Component | Required Visible Data | Required Actions | Required States | PASS Condition |
| --- | --- | --- | --- | --- |
| Global top bar | workspace, project, environment, model/provider, save status, evidence status | preview, proposal-only publish/run, settings/menu | loading, saved, draft, blocked, disabled publish/run | User can identify current context and safe next action within 10 seconds. |
| Left product navigation | workspace, Agent, workflow, skill, MCP, evidence, ops entries | switch section, show active section | selected, disabled, badge/count, collapsed | User can locate the primary product areas without reading docs. |
| Canvas workbench | entity sidebar, dot grid, node cards, toolbar, minimap/zoom, read-only/editable badge | select node, inspect node, open disabled add/layout placeholders | empty, loaded, selected, read-only, disabled reason | User understands V12 is read-only canvas foundation and why editing is deferred. |
| Agent / Station node card | role, goal summary, model/provider, tools, skills, MCP refs, status, evidence refs, ports | select, inspect, view evidence refs | running, completed, blocked, missing config, selected | User can tell what the Agent does and what evidence backs it. |
| Right inspector | selected node id, role, goal, memory summary, model, tools, skills, MCP, policy, quality, evidence | switch tabs, view evidence, see validation | no selection, selected, validation warning, denied, redacted refs | User can explain selected node responsibilities and blocked reasons. |
| Chat Workbench + Proposal Timeline | user goal, assistant response, proposal steps, WorkflowDiff ref, confirmation state | submit goal, revise, confirm, reject, open graph review | empty, generating, proposal ready, awaiting confirmation, blocked | User can follow goal -> proposal -> graph review without confusing proposal with execution. |

## Component Sketch Prompt Requirements

Every imag2 or wireframe prompt must include:

- HarnessOS product context;
- Xpert-inspired workbench density without copying Xpert assets;
- shadcn/Radix/Tailwind component language;
- operational SaaS layout, not marketing layout;
- Simplified Chinese UI copy;
- visible disabled/denied/failure state where relevant;
- explicit V12 boundary if the component touches canvas or run controls;
- no production-ready, Xpert parity, complete Studio or Agent executor claim.

## HTML Report Structure

`index.html` must contain:

1. V12-0A scope and boundary.
2. Current user-experience gap summary.
3. Component inventory.
4. First-batch component cards with image/wireframe, purpose, visible data,
   allowed actions, disabled actions and acceptance checks.
5. Assembled user paths:
   - first-run comprehension;
   - goal to proposal to graph review;
   - node selection to inspector;
   - disabled action explanation;
   - evidence review.
6. Human review decision table.
7. No False Green result.
8. Questions requiring user decision.

## Review Data Shape

`component-prototype-review-data.json` must include:

```json
{
  "schema_version": "v12.component_prototype_review.v1",
  "stage_id": "V12-0A",
  "status": "PASS|PASS_WITH_MINOR_ISSUES|PARTIAL_ACCEPTED|BLOCKED|FAIL",
  "evidence_scope": "design_only",
  "runtime_backed": false,
  "browser_implementation_backed": false,
  "figma_backed": false,
  "artifact_manifest_ref": "artifact-manifest.json",
  "components": [
    {
      "component_id": "global_top_bar",
      "status": "ACCEPTED|ACCEPTED_WITH_BOUNDED_REVISION|REJECTED|NEEDS_REVISION",
      "asset_ref": "assets/01-global-top-bar.png",
      "wireframe_ref": "wireframes/01-global-top-bar.html",
      "visual_artifact_type": "image|wireframe|text_only_exception",
      "visual_artifact_exception_reason": null,
      "user_goal": "...",
      "accepted_boundaries": ["design_only", "no_runtime_evidence"],
      "open_questions": []
    }
  ],
  "no_false_green_scan": "PASS|FAIL",
  "redaction_scan": "PASS|FAIL",
  "created_at": "ISO-8601"
}
```

The file must validate against:

```text
docs/design/V12-V15.x/schemas/v12_component_prototype_review.schema.json
```

`artifact-manifest.json` must validate against:

```text
docs/design/V12-V15.x/schemas/v12_component_prototype_artifact_manifest.schema.json
```

## V12-0A PASS Gate

V12-0A can pass only if:

- all six first-batch components are present;
- every component has a visual image or wireframe;
- every component has a user goal, visible data, allowed actions, disabled
  actions, required states and PASS condition;
- HTML report exists and is readable;
- review data JSON exists, parses and validates against
  `v12_component_prototype_review.schema.json`;
- artifact manifest exists, parses, validates against
  `v12_component_prototype_artifact_manifest.schema.json`, and records real
  asset or wireframe refs, hashes, boundary tags and review statuses;
- every first-batch component is `ACCEPTED` or
  `ACCEPTED_WITH_BOUNDED_REVISION`;
- No False Green scan passes;
- redaction scan passes;
- reviewer confirms the design is allowed to proceed to V12-0P.

## Return-To-Design Conditions

Return to component design if:

- any first-batch component is `REJECTED` or `NEEDS_REVISION`;
- any missing image/wireframe is not backed by an explicit
  `visual_artifact_exception_reason`;
- `artifact-manifest.json` remains `PLANNED_NOT_EVIDENCE` while V12-0A claims
  PASS;
- a component does not make the safe next action visible;
- canvas or chat components imply apply/publish/run without confirmation;
- node cards do not explain role, goal, model/tool/skill/MCP and evidence refs;
- inspector cannot explain policy, quality, evidence and disabled reasons;
- component sketches look like generic flowchart blocks rather than a product
  workbench;
- UI copy contains forbidden positive claims.
