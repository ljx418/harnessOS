# V12-V15 Canvas Plan Recalibration After Xpert Survey

## Decision

The post-V11 roadmap is recalibrated after the focused Xpert Studio canvas
survey.

The original V12-V15 direction remains valid, but the implementation order
must change:

- V12 must deliver the browser workbench shell and canvas foundation, not only
  product entities.
- V13 must build on that shell to deliver the editable Workflow Studio and
  visual DSL.
- V14 must attach plugin, skill, tool and MCP entities to the same node
  inspector and capability boundary.
- V15 must validate the complete interaction baseline with observability,
  deployment and scenario evidence. It must not be used as a late catch-all for
  missing canvas fundamentals.

## Xpert Canvas Evidence Used

Reference evidence:

- `docs/design/V12-V15.x/evidence/xpert-reference/canvas-survey/index.html`
- `docs/design/V12-V15.x/evidence/xpert-reference/canvas-survey/xpert-canvas-loaded.png`
- `docs/design/V12-V15.x/evidence/xpert-reference/canvas-survey/xpert-canvas-node-selected.png`
- `docs/design/V12-V15.x/evidence/xpert-reference/canvas-survey/xpert-canvas-add-menu.png`
- `docs/design/V12-V15.x/evidence/xpert-reference/canvas-survey/xpert-canvas-survey-results.json`

Evidence boundary:

- These files prove that the local Xpert Studio canvas was opened and
  inspected.
- The local Xpert canvas used a benchmark fixture and placeholder model to
  bypass local model setup friction.
- These files are reference and planning evidence only. They do not prove
  HarnessOS implementation, runtime execution or model invocation.

## Recalibrated Stage Meaning

| Stage | Recalibrated Meaning | Must Not Claim |
| --- | --- | --- |
| V12 | Product shell, entity foundation, BFF boundary, Chat Workbench and read-only canvas foundation. | Complete Workflow Studio ready. |
| V13 | Editable Workflow Studio: canvas graph, node/edge editing, node inspector, WorkflowDiff and graph round-trip. | Full Xpert parity or autonomous workflow editing ready. |
| V14 | Extension ecosystem integrated into Agent/Station inspector and capability bindings. | Unrestricted plugin ecosystem ready. |
| V15 | Observability, deployment smoke and final Xpert-inspired interaction baseline review. | Production ready or Xpert parity complete. |

## V12 Must Now Include

- Browser workbench shell with layout comparable to an early Studio shell:
  navigation, entity sidebar, central canvas area, top action bar and evidence
  area.
- Read-only canvas foundation that can render project, station-agent and
  proposal nodes from DTOs.
- Node selection and inspector foundation for Agent role, goal, memory, model,
  tool, skill, MCP and evidence refs.
- Canvas command surface placeholders for zoom, add, layout and history, marked
  disabled or planning-only until V13 if not implemented.
- Browser network evidence proving the shell only uses BFF/DTO routes.

## V13 Must Now Include

- Editable WorkflowSpecGraph canvas.
- Node and edge creation, drag, selection and validation.
- Graph round-trip through schema validation.
- WorkflowDiff proposal and before/after graph review.
- Confirmation transcript proving no publish/run before user confirmation.
- Node inspector panels for station-agent, tool, evidence and quality nodes.

## V14 Must Now Include

- Plugin, skill, tool and MCP entity panels in the same inspector pattern.
- Compatibility and policy decisions visible where the capability is bound.
- Unsafe and incompatible packages denied with visible reason.
- Scoped activation evidence linked to Agent/Station profiles.

## V15 Must Now Include

- Final scenario matrix that includes canvas-first workflows:
  onboarding -> project -> Agent setup -> canvas graph -> WorkflowDiff -> run
  inspect -> plugin binding -> observability -> deployment smoke.
- Trace, metrics, audit and incident views linked from the Studio/workbench
  surface.
- Browser health and deployment smoke evidence from a fresh local stack.

## Stop Conditions Added

- V12 completes without a browser canvas/workbench shell screenshot.
- V12 canvas shell is represented only by a static image or drawio diagram.
- V13 starts before V12 BFF/browser denylist and read-only canvas shell evidence
  pass.
- V13 claims complete Workflow Studio ready.
- V15 final interaction baseline runs while V12 canvas shell or V13 editable
  canvas evidence is missing.
- Xpert reference screenshots are counted as HarnessOS implementation evidence.

## Updated Next Step

The next implementation path should be:

1. V12 readiness audit with the canvas foundation requirement included.
2. V12 implementation: product entities, BFF route boundary, browser shell,
   read-only canvas foundation, node inspector foundation and workbench
   proposal timeline.
3. V12 E2E acceptance with screenshots, BFF logs, browser denylist and
   redaction/claim scans.
4. V13 readiness audit and editable Studio implementation.

