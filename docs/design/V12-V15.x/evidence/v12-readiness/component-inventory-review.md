# V12 Component Inventory Review

## Decision

Status: PASS_FOR_COMPONENT_FOUNDATION_REVIEW

V12 browser UI should be built on a shadcn-style component foundation instead
of one-off bespoke controls. This review covers implementation foundation only;
it does not prove Xpert parity, complete Workflow Studio, production readiness
or runtime execution.

## Implemented Foundation

| Area | Component / Dependency | Purpose |
| --- | --- | --- |
| Variant handling | `class-variance-authority`, `clsx`, `tailwind-merge` | Stable state and size variants for shared UI primitives. |
| Interaction primitives | Radix Slot, Tabs, Tooltip, ScrollArea, Separator | Mature keyboard/focus behavior for common product controls. |
| Iconography | `lucide-react` | Consistent toolbar, navigation, state and evidence icons. |
| Styling | Tailwind utilities with preflight disabled | Utility styling without resetting existing V4-V11 console surfaces. |
| Canvas | `@xyflow/react` | Mature graph renderer for the V12 read-only canvas foundation. |

## Shared UI Components

- `Button`
- `Badge`
- `Card`
- `Tabs`
- `ScrollArea`
- `Separator`
- `Tooltip`

## V12 Workbench Usage

The V12 workbench uses the shared primitives for:

- Global product rail.
- Top tabs and status badges.
- Canvas toolbar actions.
- Disabled action tooltips.
- Entity cards.
- Station Agent profile panel.
- Node inspector panel.
- WorkflowDiff proposal panel.
- Evidence strip.

## Boundaries

- Components are product UI primitives only.
- Components do not own runtime truth.
- Components cannot bypass BFF/DTO policy.
- XyFlow canvas remains read-only in V12.
- Editable Workflow Studio remains V13 work.

## Required Follow-up Evidence

- Browser screenshot of the HarnessOS V12 workbench.
- Browser network denylist log.
- DTO snapshot for `CanvasReadModel`.
- Playwright interaction evidence for node selection and disabled actions.
- No False Green scan.
- Redaction scan.
