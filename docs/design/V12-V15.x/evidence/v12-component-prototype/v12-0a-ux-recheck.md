# V12-0A UX Recheck

## Review Basis

This recheck uses the UX Architect and UI Designer rules:

- Information architecture must explain the user's current context and safe next
  action.
- Component design must expose states, disabled reasons and boundaries.
- Visual primitives must be consistent enough to support developer handoff.
- Accessibility and keyboard/focus behavior must be carried into V12-0P.

## Result

Status: `PASS_WITH_BOUNDED_REVISIONS`

The user's nine reported issues were valid. The prototype package now closes
them at design-only level and is suitable for V12-0P high-fidelity refinement.
It is still not sufficient for direct browser implementation.

## UX Findings Closed

| Area | Before | After | Remaining V12-0P Work |
| --- | --- | --- | --- |
| Top bar | Compressed layout, ambiguous buttons. | Three-zone layout with context, status grid and stable actions. | Final responsive behavior and button variant choice. |
| State model | Only one API health label. | API/run/evidence/permission catalog plus drawio user-state machine. | Tokenize state colors and copy. |
| Navigation content | Mostly Agent enumeration. | Rail product domains plus secondary project objects and audit areas. | Keyboard focus and collapsed mode. |
| Navigation icons | Emoji/glyph icons felt inconsistent. | Inline SVG icons and structured abbreviations. | Replace with final icon library in implementation. |
| Rail/secondary relationship | Ambiguous. | Explicit domain-to-object mapping. | Final navigation IA validation. |
| Canvas edges | Straight, disconnected lines. | SVG curved edges connected to node ports. | XyFlow interaction and edge handles in V12 implementation. |
| Node detail | No hover/click detail. | Selected/hovered states, detail overlay and node menu semantics. | Real hover/focus behavior and inspector sync. |
| Node IO | No multi-input/multi-output model. | 2 input / 2 output ports and IO panels. | Port naming, validation and edge constraints. |
| Chatbox | One-off revision button. | Workspace-scoped chat history, independent chat panel and proposal timeline. | Conversation persistence and timeline-to-canvas highlight. |

## Design Quality Opinion

The prototype now provides a clearer path toward an Xpert-inspired workbench:
it has product navigation, a denser canvas, connected nodes, visible state
models and a proposal-oriented chat surface. The visual quality is still
wireframe-level and must not be treated as product-grade frontend complete.

## Multi-Direction Visual Recheck

The follow-up critique that the design still lacked polish was valid. The
package now includes `xpert-style-concept-board.html`, which compares three
candidate directions:

- Light Studio Workbench: closest to the Xpert-like default product workbench.
- Dense Operator Console: stronger observability, policy, evidence and runtime
  state density.
- Creative Workflow Studio: stronger video/storyboard, asset preview and QA
  Agent experience.

UX recommendation: use Light Studio Workbench as the default V12-0P direction,
then keep Dense Operator Console and Creative Workflow Studio as mode-specific
extensions. This creates a clearer product foundation without overloading the
first high-fidelity prototype.

## Component Detail Recheck

The follow-up request to deepen component detail was valid. The package now
includes `light-studio-component-detail-board.html`, which takes the recommended
Light Studio direction beyond a visual mockup and defines:

- token-level foundation for color, typography, radius, spacing and status
  semantics;
- stable page skeleton dimensions for top bar, rail, sidebar, canvas,
  inspector and Chat Workbench;
- component-level display data, states, interactions, disabled reasons and
  acceptance checks;
- visible state taxonomy for healthy, collecting, proposal-ready, blocked,
  read-only, missing-config, failed and evidence-ready states;
- natural-language-to-proposal flow showing why Chat can generate proposal
  evidence but cannot directly publish or run.

UX recommendation: V12-0P should use this component-detail board as the
handoff checklist before creating Figma or high-fidelity browser frames.

## Interaction Detail Recheck

The follow-up request to deepen navigation, canvas interaction, panel layering,
design language consistency and bottom workbench tabs was valid. The package now
includes `v12_0p_interaction_experience_spec.md`,
`interaction-experience-detail.html` and `v12-0a-deep-ux-design-audit.md`.

These additions define:

- L1 product rail and L2 domain navigation hierarchy, content examples and
  keyboard behavior;
- canvas hover, click, drag, ghost edge, invalid edge, multi-select, zoom and
  pan interaction states;
- z-index and ownership rules for topbar, rail, L2 nav, canvas, inspector and
  bottom workbench;
- shared design tokens for color, radius, typography, state semantics and copy;
- bottom workbench tabs for chat, proposal, run log, evidence, debug and
  suggestions.

UX recommendation: V12-0P should convert these contracts into high-fidelity
frames and variants before any browser implementation is accepted.

## Required Before Real Browser Implementation

- V12-0P high-fidelity prototype accepts typography, spacing, color, icon and
  interaction tokens.
- State machine terms are converted into UI status tokens.
- XyFlow behavior is specified for hover, select, edge, port and minimap.
- L1/L2 navigation and panel Z-order are frozen in a high-fidelity prototype.
- Bottom workbench tabs have explicit data, actions, disabled states and
  keyboard behavior.
- Browser route denylist and BFF DTO evidence remain required.
