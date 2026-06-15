# V12-0P Interaction Experience Specification

## Decision

Status: `READY_FOR_V12_0P_REVIEW_INPUT`

Scope: detailed UX and interaction contract for the V12 Light Studio
high-fidelity prototype. This document is a design specification. It is not
browser implementation evidence, BFF evidence, DTO evidence, runtime evidence
or a complete Workflow Studio readiness claim.

## Product Experience Target

V12-0P must turn the accepted V12-0A Light Studio direction into a concrete,
developer-ready interaction prototype. The target is a browser workbench where
users can understand the current workspace, inspect a read-only workflow graph,
inspect Agent/station responsibilities, discuss goals in a workspace chat,
review proposal state and audit evidence without confusing the prototype with
runtime execution.

## 1. Left Navigation Information Architecture

### 1.1 Navigation Model

The left side uses a two-level navigation model:

| Level | Name | Width | Owns | User Meaning |
| --- | --- | --- | --- | --- |
| L1 | Product Rail | 56 px collapsed rail | Product domains | "Which product domain am I in?" |
| L2 | Domain Navigation | 220-260 px panel | Objects inside selected domain | "Which workspace/project object am I looking at?" |

L1 selection changes the object taxonomy shown in L2. L2 selection changes the
main workbench content. L1 and L2 must never look like two unrelated sidebars.

### 1.2 L1 Product Rail

| Rail Item | Icon Style | L2 Content | Primary Use |
| --- | --- | --- | --- |
| 工作台 | Home / dashboard icon | Overview, my space, shared space, recent projects | First-run entry and project status. |
| 智能体 | Bot / users icon | Station Agents, Agent profiles, role templates | Inspect and configure Agent identities. |
| 工作流 | Graph / branch icon | Workflow specs, versions, drafts, templates | Open canvas and workflow graph read model. |
| 技能 | Puzzle / cube icon | Skills, MCP refs, tools, capability bindings | Inspect capability surface. |
| 证据 | File-check icon | Evidence packages, quality reports, trace refs | Audit outputs and proofs. |
| 运行 | Play-circle / pulse icon | Runs, incidents, timelines, debug sessions | Inspect status and failures. |
| 设置 | Gear icon | Workspace settings, model profiles, policies | Manage environment and defaults. |

Visual rules:

- Active L1 item uses blue soft background, blue icon and a 3 px left accent.
- Hover uses slate text, pale background and no layout shift.
- Disabled L1 item uses 45% opacity, tooltip with reason and remains keyboard
  focusable only if it has an explanation action.
- Badge positions use top-right 12 px dot or numeric pill.
- Icons must come from the same outline family in implementation, preferably
  `lucide-react`.

### 1.3 L2 Domain Navigation

L2 has a stable structure:

```text
Domain Header
  Workspace / Project Switcher
  Search or Filter

Primary Section
  Current domain objects

Secondary Section
  Recent / Shared / Pinned

Governance Section
  Evidence / Policy / Audit shortcuts when relevant
```

Examples:

| L1 Domain | L2 Primary Objects | Required Empty State | Required Disabled State |
| --- | --- | --- | --- |
| 工作台 | 总览, 我的空间, 共享空间, 最近项目 | "还没有项目，创建或导入一个工作流。" | API offline: show read-only cached mode. |
| 智能体 | Station Agents, Role Templates, Model Profiles | "还没有 Agent，先从工作流节点生成或手动创建。" | Missing policy: creation disabled with policy ref. |
| 工作流 | Drafts, Published, Templates, Archived | "还没有工作流，使用 Chat 生成提案。" | V12 read-only: edit action disabled until V13. |
| 技能 | Skills, MCP, Tools, Capability Bindings | "还没有启用技能或 MCP。" | Unsafe binding denied with capability decision. |
| 证据 | Evidence Chain, Quality, Trace, Export | "还没有运行证据。" | Raw content hidden; only redacted refs visible. |
| 运行 | Active, Completed, Failed, Incident Timeline | "当前没有运行。" | Retry disabled if no valid handoff. |

### 1.4 Navigation Keyboard UX

- `Tab` enters L1 rail, then L2, then top shortcuts, canvas, inspector and bottom
  workbench in visual order.
- Arrow keys move inside L1 rail.
- `Enter` or `Space` activates current rail item.
- `Esc` collapses L2 detail overlays but does not collapse the main sidebar by
  default.
- Focus ring is 2 px blue outline with 2 px offset; focus must remain visible
  on white and blue-soft backgrounds.

## 2. Canvas Interaction Experience

### 2.1 Canvas State Model

| State | Visual Treatment | User Feedback |
| --- | --- | --- |
| empty | centered setup prompt, faint grid | Shows next safe action: open Chat or select workflow. |
| loading | skeleton nodes, dimmed toolbar, spinner in status chip | "正在加载画布 read model..." |
| read_only | lock badge, disabled edit controls | "V12 只读画布，编辑在 V13 启用。" |
| node_hover | node elevation +1, port glow, connected edges highlight at 30% | Tooltip shows role, status and evidence count. |
| node_selected | 2 px blue outline, stronger shadow, inspector opens | Right inspector owns details. |
| edge_hover | edge thickens from 2 px to 3 px, endpoint ports glow | Shows source/target labels. |
| drag_preview | ghost node or ghost edge, magnetic snap hint | V12 shows preview only; no durable mutation. |
| invalid_action | red/amber hint line, denied toast, no movement committed | Shows policy/capability reason. |
| blocked | node/edge warning badge, inspector opens blocked reason | Shows required fix or missing evidence. |

### 2.2 Drag, Click And "Tactile Feel"

V12-0P must define the tactile feel even if V12 implementation remains
read-only:

| Interaction | Prototype Behavior | Motion / Feel | Boundary |
| --- | --- | --- | --- |
| Pan canvas | Hold space or drag empty canvas | 1:1 pointer tracking, inertial stop under 120 ms | Does not mutate graph. |
| Zoom | Wheel / trackpad / toolbar | Zoom anchored to cursor, smooth 120-160 ms | Min 40%, max 180%. |
| Hover node | Pointer hover | shadow deepens, ports appear, edge neighborhood highlights | No data fetch side effect. |
| Click node | Single click | selected outline, inspector slide-in or update under 180 ms | Selection is display state only. |
| Drag node | Pointer drag | ghost transform, snap guides, drop preview | V12 blocks commit; V13 may produce WorkflowDiff. |
| Start edge | Drag from output port | curved ghost edge follows pointer, valid targets glow | V12 preview only unless V13 edit mode. |
| Drop edge invalid | Release on invalid target | edge snaps back, reason toast and inspector validation | No silent failure. |
| Multi-select | Shift-click or drag marquee | pale blue selection area, selected count chip | Does not batch mutate. |
| Open context menu | Right click / keyboard menu | menu anchored to node, no viewport jump | Dangerous actions disabled with reasons. |

### 2.3 Edge And Port Rules

- Inputs are left-side ports; outputs are right-side ports.
- Multi-input nodes show stacked input ports with labels.
- Multi-output nodes show stacked output ports with labels.
- Valid connection preview uses blue ghost curve.
- Existing connected edge uses slate curve; active path uses blue curve.
- Blocked edge uses amber dashed curve with warning badge.
- Invalid edge uses red temporary curve and disappears after feedback.
- Edge labels appear only on hover or selected path to keep canvas readable.

### 2.4 Canvas Toolbar

Toolbar groups:

| Group | Controls | V12 Behavior |
| --- | --- | --- |
| Selection | pointer, hand/pan, fit view | enabled |
| Review | inspect, evidence, trace | enabled if selected node has refs |
| Layout | auto-layout, align, collapse | preview enabled; durable change disabled |
| Authoring | add node, connect, branch | disabled with V13 message |
| History | undo, redo, version history | version history read-only; undo/redo disabled if no local edit |
| View | zoom, minimap, grid toggle | enabled |

## 3. Panel Hierarchy, Z Axis And Layout Layers

### 3.1 Layout Regions

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Z-100 Top Route Shortcut / Global Bar                                       │
├───────┬───────────────────────┬───────────────────────────────┬────────────┤
│ Z-80  │ Z-70 L2 Domain Nav    │ Z-10 Canvas Base              │ Z-60 Right │
│ L1    │                       │                               │ Inspector │
│ Rail  │                       │                               │            │
├───────┴───────────────────────┴───────────────────────────────┴────────────┤
│ Z-50 Bottom Debug / Chat / Timeline Workbench                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Z-Index Contract

| Layer | z-index token | Contains | Rule |
| --- | --- | --- | --- |
| Canvas base | `z-canvas-base = 10` | grid, nodes, edges | Never covers panels. |
| Canvas hover overlays | `z-canvas-overlay = 30` | tooltips, port labels | Clipped to canvas viewport unless popover. |
| Bottom workbench | `z-bottom-workbench = 50` | Chat, logs, trace, evidence tabs | Stays above canvas, below inspector popovers. |
| Right inspector | `z-inspector = 60` | node details, evidence preview | Owns selected-node details. |
| L2 navigation | `z-sidebar = 70` | domain objects | Covers canvas when expanded on narrow width. |
| L1 rail | `z-rail = 80` | product domains | Always visible on desktop. |
| Top route shortcuts | `z-topbar = 100` | workspace/project/env/status/actions | Always above canvas and panels. |
| Popovers / menus | `z-popover = 200` | menus, tooltips, node context menus | Must trap focus only when modal-like. |
| Modal confirmation | `z-modal = 300` | confirmation dialogs | Requires explicit close/focus return. |

### 3.3 Panel Ownership

| Panel | Owns | Must Not Own |
| --- | --- | --- |
| Top route shortcut panel | route context, environment, model, API/run/evidence state, safe actions | workflow truth or runtime mutation |
| Left rail | product domain selection | object details |
| L2 domain nav | object list, filters, recent/pinned groups | canvas selection state |
| Canvas | graph read model, node/edge selection | inspector details or durable mutation |
| Right inspector | selected node detail, policy, quality, evidence | graph layout ownership |
| Bottom workbench | chat, proposal timeline, logs, trace, evidence review | source of runtime truth |

### 3.4 Resize And Collision Rules

- Minimum desktop width: 1280 px. Below 1180 px, right inspector becomes drawer.
- L2 can collapse to 64 px summary but L1 remains visible.
- Bottom workbench default height is 280 px, resizable between 180 and 460 px.
- Inspector default width is 360 px, resizable between 320 and 480 px.
- Canvas controls must never overlap node cards; they anchor to top-left and
  bottom-right safe zones.
- Popovers must avoid covering the active port or selected node title.

## 4. Design Language Consistency

### 4.1 Tokens

| Token | Value | Usage |
| --- | --- | --- |
| Primary blue | `#2563EB` | selected state, primary action, focus ring |
| Blue soft | `#EFF6FF` | selected surface, non-destructive emphasis |
| Slate text | `#0F172A`, `#334155`, `#64748B` | title, body, secondary |
| Surface | `#FFFFFF`, `#F8FAFC`, `#F5F7FB` | panels and workbench background |
| Border | `#DBE3EE` | panel and card boundaries |
| Success | `#16A34A` | completed, online, evidence ready |
| Warning | `#B45309` | awaiting confirmation, blocked, missing evidence |
| Error | `#DC2626` | failed, denied, destructive |
| Radius | 8 px / 12 px / 16 px | controls / cards / large panels |
| Shadow | subtle 0 12-34 px | selected cards and panels only |

### 4.2 Component Rules

- Cards use 8-16 px radius; no pill-shaped giant cards.
- Buttons use icons from one icon family, preferably lucide.
- Text density: title 16-18 px, body 13-14 px, metadata 12 px.
- Status colors must be semantic and consistent across top bar, node card,
  inspector and bottom workbench.
- Disabled actions must preserve layout and show a reason through tooltip,
  inline hint or inspector block.
- All panels use the same border, shadow and background scale.

### 4.3 Copy Rules

- Use action labels: `查看`, `预览`, `确认`, `修订`, `拒绝`, `打开证据`.
- Do not use vague labels such as `执行一下` or `搞定`.
- Dangerous actions include a state: `需要确认`, `已阻断`, `只读`.
- UI copy must not claim Xpert parity, production readiness or complete Studio
  readiness.

## 5. Bottom Workbench Tab Specification

### 5.1 Tab List

| Tab | Purpose | Required Visible Data | Primary Actions | Disabled States |
| --- | --- | --- | --- | --- |
| 对话 | Workspace-scoped chat and goal intake | conversation, attachments, context refs, proposal status | send, attach, insert command, open proposal | send disabled when API offline; run disabled before confirmation |
| 提案 | WorkflowDiff proposal timeline | parsed goal, changed nodes, risk, confirmation state | confirm, revise, reject, open graph review | confirm disabled if policy missing |
| 运行日志 | Current or selected run event stream | session, turn, station status, timestamps | filter, jump to node, copy trace ref | retry disabled if no valid handoff |
| 证据库 | Evidence/quality/trace refs | evidence package, redaction, quality, artifact refs | open evidence, compare, export ref | raw content hidden |
| 调试 | Developer/operator diagnostics | API state, BFF route, DTO snapshot, denylist result | copy debug bundle, open trace | write operations disabled |
| 建议 | System suggestions and next safe actions | blocked reason, recommended fix, owner, priority | create proposal, assign follow-up | proposal disabled if no target |

### 5.2 Tab Interaction

- `Tab` moves into active tab panel; arrow keys move between tab buttons.
- Switching tabs preserves selected canvas node.
- Chat messages can highlight canvas nodes but cannot mutate them.
- Proposal tab can open graph review overlay but cannot confirm automatically.
- Run logs can jump to node or timeline event.
- Evidence tab can open redacted refs and quality summaries only.
- Debug tab is visible to admin/operator roles; standard users see simplified
  status and evidence refs.
- Suggestions tab must distinguish "safe suggestion" from "action already
  executed".

### 5.3 Cross-Panel Synchronization

| Source Action | Canvas Effect | Inspector Effect | Bottom Workbench Effect |
| --- | --- | --- | --- |
| Click node | selected node outline | inspector loads selected entity | log/proposal/evidence filters to node |
| Hover edge | path highlights | no inspector change | status hint shows source/target |
| Click evidence ref | related node pulses | evidence tab opens | evidence tab becomes active |
| Chat proposal step click | affected nodes highlighted | first affected node selected | proposal step details expand |
| Run event click | station path highlighted | station details shown | run log scrolls to event |

## 6. Accessibility And Inclusive Interaction Requirements

- All interactive controls require accessible names.
- Icon-only controls require tooltip plus `aria-label`.
- Tabs use ARIA tab pattern.
- Menus use menu button pattern; Escape closes and returns focus.
- Canvas keyboard alternative must exist: node list, edge list and inspector
  navigation.
- Status updates should use polite live regions for loading/completed and
  assertive only for failed/blocked.
- Reduced motion mode disables inertial pan and long transitions.
- Contrast target: WCAG 2.2 AA minimum.
- Focus target size: 24 px minimum; pointer target 32 px preferred.

## 7. V12-0P Acceptance Checks

V12-0P prototype can pass only if:

- L1/L2 navigation hierarchy is visible and documented.
- Each L1 item has an example L2 object set.
- Canvas hover/select/drag/edge/invalid-action feedback is shown in prototype
  frames or documented interaction states.
- Z-index and panel ownership are frozen.
- Bottom workbench tabs have purpose, data, actions, disabled states and
  keyboard behavior.
- Design tokens are consistent across generated images, wireframes and
  high-fidelity prototype.
- Accessibility review finds no unresolved critical or serious keyboard/focus
  blocker in the prototype.
- No false-green UI copy appears outside safe boundary contexts.

## 8. Stop Conditions

- V12-0P prototype treats Chat transcript as runtime execution.
- V12-0P hides disabled reason for run/publish/edit.
- Canvas drag or edge creation appears to persist changes without WorkflowDiff.
- L1 and L2 navigation relationship remains visually ambiguous.
- Bottom workbench tabs are labels only and do not define data/action/state.
- Z-index allows menus, inspector or bottom workbench to obscure critical
  confirmation controls.
- Prototype uses inconsistent icon styles, colors, corner radius or status
  semantics.
- Accessibility review identifies keyboard traps, missing focus, unlabeled
  icon buttons or non-announced blocked states.

