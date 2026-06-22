# V12-0P High-Fidelity Prototype Plan

## Decision

Status: `IN_PROGRESS_READY_FOR_HUMAN_REVIEW`

V12-0P is the high-fidelity product-experience freeze gate after V12-0A
component sketch acceptance. It translates the accepted component sketches and
interaction contract into a reviewable Light Studio prototype package.

This stage is design-only. It is not browser implementation evidence, BFF
evidence, DTO evidence, runtime evidence, complete Workflow Studio evidence or
Xpert parity evidence.

## Inputs

- `v12_component_prototype_plan.md`
- `v12_component_prototype_execution_plan.md`
- `v12_0p_interaction_experience_spec.md`
- `v12_0p_component_design_decision_record.md`
- `v12_figma_prototype_review_plan.md`
- `v12_to_v15_target_prd.md`
- `v12_to_v15_target_architecture.md`
- `evidence/v12-component-prototype/index.html`
- `evidence/v12-component-prototype/imag2-experience/index.html`
- `evidence/v12-component-prototype/v12-0a-deep-ux-design-audit.md`

## Allowed Work

- High-fidelity HTML prototype for human review.
- Component layout and state finalization.
- Product shell, L1/L2 navigation, canvas, inspector and workbench visual
  composition.
- State machine and interaction-flow visualization.
- PRD fit review and design audit.
- No False Green and redaction scans.
- Static render evidence for the prototype page.

## Blocked Work

- Real V12 browser implementation.
- V13 editable Workflow Studio implementation.
- V14 plugin runtime implementation.
- V15 final acceptance.
- Direct browser calls to runtime/store/credential/provider routes.
- Any claim that the prototype proves Xpert parity, product-grade frontend,
  complete Workflow Studio, production readiness or Agent executor readiness.

## Prototype Scope

The high-fidelity prototype must include:

| Area | Required Design Content | Boundary |
| --- | --- | --- |
| Product shell | Workspace, project, app, environment, API status, saved status and safe global actions. | Product prototype only. |
| L1/L2 navigation | Product rail and domain object list with examples for workbench, agents, workflow, skills, evidence, runs and settings. | Navigation taxonomy only. |
| Canvas workbench | Dot-grid canvas, node cards, ports, curved edges, active path, minimap, toolbar and disabled authoring controls. | Read-only canvas foundation. |
| Node card | Role, goal, provider/model, status, ports, tools, skills, MCP and evidence count. | Station projection only. |
| Right inspector | Overview, configuration, policy, quality, evidence, validation and disabled reasons. | Projection, not runtime truth. |
| Bottom workbench | Chat, proposal timeline, trace, quality and evidence tabs. | Supporting review surface. |
| Interaction states | Hover, selected, blocked, invalid edge, awaiting confirmation, API offline and evidence missing. | Design states, not execution proof. |

## Frozen Design Decisions

The accepted V12-0P design decisions are frozen in:

```text
docs/design/V12-V15.x/v12_0p_component_design_decision_record.md
```

That record is the canonical handoff from HTML prototype review into Figma /
high-fidelity prototype design. Future Figma work may improve visual polish,
spacing and component detail, but must not silently change:

- L1 product rail as product domain navigation;
- L2 sidebar as current workflow-context navigation;
- Agent / skill / MCP resources living in drawer or Inspector, not workflow L2;
- canvas node cards with concrete ports and edge semantics;
- Inspector as read-only projection;
- bottom Chat as independent workspace chat with proposal handoff semantics;
- visible state machine and confirmation boundaries;
- design-only evidence boundary.

## Acceptance Criteria

V12-0P high-fidelity prototype review may pass only if:

- `index.html` exists and is readable without a dev server.
- The page explains that it is design-only and not runtime/browser evidence.
- The top bar, L1/L2 navigation, canvas, inspector and bottom workbench are
  visible in one integrated target screen.
- The prototype shows at least five concrete interaction states:
  `api_online`, `api_offline`, `node_hover`, `node_selected`,
  `invalid_edge`, `awaiting_confirmation` or `evidence_missing`.
- Navigation examples include at least workbench, agent, workflow, skill/MCP,
  evidence, run and settings domains.
- Canvas examples include at least one trigger node, one station Agent node,
  one tool/skill/MCP node and one evidence/quality node.
- Node design shows multi-input or multi-output affordances.
- Inspector design exposes policy, quality, evidence and validation sections.
- Bottom workbench defines Chat, proposal timeline, trace, quality and evidence
  tabs with concrete user meaning.
- PRD spec review confirms the prototype supports V12 product shell,
  read-only canvas foundation and Chat Workbench proposal handoff.
- No False Green scan passes or records only safe-context matches.
- Redaction scan passes or records only safe-context matches.
- Static render evidence exists for the HTML page.

## Stop Conditions

- Prototype is treated as HarnessOS browser implementation evidence.
- Prototype uses Xpert screenshots as HarnessOS implementation proof.
- Prototype hides read-only canvas or proposal-only boundaries.
- Canvas nodes are disconnected generic blocks with no ports or edge semantics.
- L1/L2 navigation does not explain domain-to-object relationship.
- Inspector does not show policy, quality, evidence and validation meanings.
- Bottom workbench is a generic chat box with no tab ownership or proposal
  timeline.
- UI copy claims Xpert parity complete, product-grade frontend complete,
  complete Workflow Studio ready, production ready or Agent executor ready.

## Next Gate

If V12-0P is accepted, the next stage is V12 implementation-readiness audit.
Real browser implementation still requires acceptance of schema/DTO, BFF route,
browser denylist, evidence package and user scenario contracts.
