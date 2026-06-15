# V12-0P PRD Spec Review

## Decision

Status: `PASS_FOR_DESIGN_REVIEW`

Scope: PRD fit review for the V12-0P high-fidelity prototype. This review
checks whether the prototype can guide the next implementation-readiness audit.
It does not approve real browser implementation by itself.

## PRD Alignment

| PRD Requirement | Prototype Coverage | Decision |
| --- | --- | --- |
| Product shell makes workspace/project/app context visible. | Top bar shows workspace, project, active workflow, environment, API state and safe actions. | PASS |
| V12 canvas is a browser workbench foundation, not a complete Studio. | Canvas is explicitly marked read-only; add/layout/publish/run controls are disabled or proposal-only. | PASS |
| Users can understand L1/L2 navigation hierarchy. | L1 rail owns product domains; L2 owns objects inside the selected domain with concrete examples. | PASS |
| Users can inspect Agent / Station responsibilities. | Node card and inspector show role, goal, tools, skills, MCP refs, policy and evidence refs. | PASS |
| Users can understand node input/output semantics. | Selected station node has multiple input and output ports; edge and port rules are documented. | PASS |
| Users can use natural language as a workspace chat surface. | Bottom workbench shows Chat plus proposal timeline and confirms it does not auto publish or run. | PASS |
| Users can audit output quality and evidence. | Inspector and bottom tabs expose quality/evidence/trace ownership and redaction status. | PASS |
| Browser must not construct runtime truth. | Prototype repeatedly marks design-only/read-only/projection-only boundaries. | PASS |

## UX Issue Closure

The previous human review called out nine issues. This V12-0P package closes
them at design level:

1. Top bar compression and broken buttons: replaced with stable three-column
   top bar, semantic chips and fixed-height controls.
2. API/run state ambiguity: added concrete state enumeration for API, node,
   edge, confirmation and evidence states.
3. Sidebar content too shallow: L1 and L2 navigation now include concrete
   domains, objects, empty states and governance shortcuts.
4. Icon quality: prototype uses consistent symbolic placeholders and records
   implementation preference for lucide icons.
5. Navigation logic unclear: L1 owns product domains; L2 owns objects inside
   the selected domain.
6. Canvas links and curve quality: prototype uses curved active, normal and
   blocked edges.
7. Node hover/click detail missing: hover, selected and inspector ownership are
   explicitly shown.
8. Node input/output missing: node card includes multi-input and multi-output
   port affordances.
9. Chat Workbench wording wrong: bottom workbench is now a workspace chat with
   history/proposal timeline semantics, not a single "generate revision"
   button.

## Remaining Implementation Risks

- The prototype is static. V12 browser implementation still needs real BFF DTO
  snapshots, browser network logs and Playwright or equivalent interaction
  evidence.
- The prototype does not prove editable Workflow Studio behavior. V13 remains
  responsible for visual DSL authoring.
- Iconography must be replaced by one consistent implementation icon set,
  preferably `lucide-react`, during browser implementation.
- Canvas interactions must be implemented with real pointer, keyboard, focus
  and network-boundary tests before they can count as product evidence.

## Review Result

The V12-0P high-fidelity prototype is sufficient as a design-review input for
V12 implementation-readiness audit. It is not sufficient as browser
implementation evidence.
