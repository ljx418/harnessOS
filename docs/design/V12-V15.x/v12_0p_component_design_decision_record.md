# V12-0P Component Design Decision Record

Status: `ACCEPTED_FOR_FIGMA_PROTOTYPE_INPUT`

Last updated: `2026-06-16`

Canonical review page:

```text
docs/design/V12-V15.x/evidence/v12-0p-high-fidelity-prototype/imag2-vs-html-comparison.html
```

This record freezes the V12-0P component design decisions accepted from the
high-fidelity review page. It is the handoff contract for the next Figma /
high-fidelity design step.

This document is design-only. It is not browser implementation evidence, BFF
evidence, DTO evidence, runtime evidence, complete Workflow Studio evidence,
Xpert parity evidence or production readiness evidence.

## 1. Product Experience Direction

V12 should move toward a quiet, dense, professional low-code workbench inspired
by the Xpert canvas experience, while preserving HarnessOS runtime and evidence
boundaries.

The target product screen must present these surfaces together:

- global top bar and product status;
- left product rail;
- secondary contextual navigation for the active product domain;
- canvas workbench;
- node resource drawer;
- right-side Inspector;
- bottom Chat / proposal / Trace / quality / evidence workbench;
- user-visible status and confirmation gates.

The screen should feel like an operational product workspace, not a report page,
marketing page or generic diagram.

## 2. Navigation Information Architecture

The accepted navigation model is:

```text
L1 product rail = product domain
L2 sidebar = objects and filters within the current domain
Canvas resource drawer = node templates and creation resources
Inspector = selected object review and configuration projection
```

### L1 Product Rail

The L1 rail represents stable product domains. It must not be used as a mixed
list of node templates.

Accepted L1 domains:

| Domain | Purpose | Boundary |
| --- | --- | --- |
| 工作台 | workspace-level overview and entry surface | No runtime mutation. |
| 工作流平台 | primary workflow canvas and run/evidence context | Main V12 product route. |
| 智能体资产 | reusable Agent profiles and station-agent projections | Asset review, not Agent executor readiness. |
| 工具与 MCP | tool, skill and MCP catalog | Availability and scope review only. |
| 证据与运行 | runtime report, evidence chain and run review surfaces | Read-only review. |
| 模板中心 | reusable workflow templates and fragments | Proposal source only. |
| 设置 | workspace/project/app settings | No direct runtime truth. |

### L2 Contextual Navigation

When the active L1 route is `工作流平台`, the L2 sidebar must show workflow
context rather than Agent/tool templates.

Accepted L2 workflow context:

- 当前项目
- 运行中
- 证据待审
- 全部工作流
- 草稿提案
- 已发布
- 失败 / 阻断

Agent, skill, MCP, quality, approval and template fragments are not primary L2
navigation items in this route. They belong in the canvas resource drawer or
selected-node Inspector.

## 3. Component Library Decisions

The V12-0P component library has nine accepted component groups.

| ID | Component | Required visible content | Required interactions | Must not do |
| --- | --- | --- | --- | --- |
| C01 | 全局顶栏 / 状态栏 | workspace, project, environment, model, provider, API status, run status, evidence status, waiting confirmation | preview, debug, readonly toggle, version history, save draft, submit review | Claim production readiness or silently enable publish/run. |
| C02 | 一级 Rail + 二级上下文导航 | product domains, current project, running, evidence pending, workflows, drafts, published, blocked | switch views, filter object lists, open project/run/evidence context | Directly mutate WorkflowDraft, WorkflowVersion, WorkflowInstance or StationRun. |
| C03 | 节点资源抽屉 | triggers, Agents, skills, MCP, quality, approval, template fragments, risk and permission labels | search, filter, drag resource to canvas | Auto apply/publish/run after drag. |
| C04 | 画布工作区与工具栏 | dot grid, pan/select/connect tools, zoom, lock, minimap, node positions, edge states | pan, zoom, select, connect, inspect | Show incomplete floating edges or disconnected generic blocks. |
| C05 | Agent / Station 节点卡 | id, name, role, status, input ports, output ports, tools, evidence refs, quality state | hover preview, click Inspector, port hover highlight | Let source=agent directly perform durable mutation. |
| C06 | 右侧 Inspector | role, goal, memory summary, tools, skills, MCP, policy, quality, evidence, latest output | inspect, copy redacted refs, view disabled reasons | Provide hidden Apply / Publish / Run / Approve controls. |
| C07 | 底部 Chat 工作台 | workspace chat, proposal timeline, Trace, quality and evidence tabs | natural-language input, tab switch, proposal review, locate node | Present Chat as if runtime already executed. |
| C08 | 状态与反馈系统 | ready, running, evidence-ready, awaiting-confirmation, blocked, disabled, empty | explain state, show reason, surface next action | Hide failed, denied or waiting states. |
| C09 | 实现映射组件栈 | shadcn/Radix controls, lucide icons, XyFlow canvas, BFF DTO route boundaries | map design components to implementation primitives | Rebuild low-level canvas or icon system from scratch without need. |

## 4. Visual System Decisions

The accepted visual system is a restrained Light Studio product surface:

- background: light operational workspace, not decorative hero;
- cards: 14-18px radius for prototype review, with implementation allowed to
  tighten to product-system radius if shadcn tokens require it;
- color semantics:
  - blue = active, selected, running, current route;
  - green = ready, passed, evidence-ready;
  - amber = awaiting confirmation, needs review, bounded warning;
  - red = blocked, denied, failed;
  - neutral = disabled, read-only, empty, secondary metadata;
- typography: dense product UI, Simplified Chinese user-facing copy;
- iconography: unified line icons, preferably lucide in implementation;
- no emoji-as-icon substitutions;
- no letter placeholders in final browser implementation.

The review page uses inline SVG symbols only to document icon intent. Browser
implementation should use lucide/shadcn-compatible icons.

## 5. Canvas And Node Interaction Decisions

The canvas must support these interaction semantics:

- pan and zoom;
- select node;
- hover node;
- connect ports;
- invalid edge feedback;
- selected edge feedback;
- blocked edge feedback;
- minimap orientation;
- read-only lock state;
- resource-drag-to-proposal.

Node cards must support:

- multiple input ports;
- multiple output ports;
- selected state;
- running state;
- ready state;
- waiting-confirmation state;
- blocked state;
- hover preview;
- Inspector binding.

Edges must visually connect concrete ports. Half-connected decorative curves are
not accepted for browser implementation.

## 6. Inspector Decisions

The Inspector is the selected-node review surface. It must show:

- node id and selected object type;
- role and goal;
- memory summary;
- tool list;
- skill list;
- MCP refs;
- policy/capability decision refs;
- quality status and quality report link;
- evidence refs;
- latest redacted output preview;
- disabled or blocked reason.

The Inspector is not runtime truth and must not directly mutate durable runtime
objects.

## 7. Bottom Workbench Decisions

The bottom workbench is a multi-tab operational surface, not a generic chat box.

Accepted tabs:

| Tab | Purpose | Boundary |
| --- | --- | --- |
| Chat | user goal, follow-up and workspace chat history | Does not imply execution. |
| 提案时间线 | WorkflowSpec / WorkflowDiff / confirmation state | Proposal-only before confirmation. |
| Trace | event and run visibility | Read-only projection. |
| 质量 | quality gates and reports | Does not overwrite scores. |
| 证据 | evidence refs and redaction status | Redacted refs only. |

The Chat input should not be labeled as "生成修订提案". It should behave as an
independent workspace chat box that can reference current workspace history and
produce proposal handoffs when appropriate.

## 8. User-Visible State Machine

Normal user-visible flow:

```text
输入目标 -> 生成草案 -> 等待确认 -> 受控运行 -> 证据就绪
```

Exception / policy flow:

```text
用户操作 -> 策略检查 -> 权限拒绝/阻断 -> 修订提案 -> 用户确认
```

The top bar, canvas node, Inspector and bottom timeline must not disagree about
the visible state. If the system is running, waiting, blocked or failed, the user
must be able to see that state and the reason.

## 9. Typical User Scenarios To Preserve

The accepted component design must support these V12-facing user scenarios:

| Scenario | Required experience |
| --- | --- |
| 多 Agent 讨论 | User enters a topic; the canvas shows multiple viewpoint Agents, a summary Agent and a QA Agent; evidence tab shows discussion refs. |
| 视频分镜创作 | User enters a creative idea; planner, style, storyboard and QA nodes show consistent style constraints and storyboard evidence refs. |
| 自然语言修订 | User asks to add QA or change order; Chat creates a WorkflowDiff proposal; canvas highlights changed nodes and edges; no execution before confirmation. |
| 失败阻断审查 | Blocked node/edge is visible; Inspector shows cause; Trace points to failed event; Chat suggests bounded repair actions. |
| 证据审计 | User opens Evidence tab, checks artifact refs, quality reports, runtime report refs, redaction status and review summary. |

## 10. Implementation Mapping

The accepted browser implementation direction is:

- shadcn/Radix for buttons, tabs, forms, popovers, tooltips and dialogs;
- lucide for line icons;
- XyFlow or equivalent for graph canvas, node positioning, ports, edges and
  minimap;
- BFF DTOs for all browser data access;
- Playwright for screenshot, action log, network denylist and interaction
  evidence;
- redacted refs for evidence, runtime report, artifact and quality links.

V12 implementation should not create a bespoke canvas engine unless XyFlow or an
equivalent mature library fails a documented technical spike.

## 11. Figma Handoff Rules

The Figma prototype must preserve this decision record.

Required Figma frames or sections:

- Light Studio workbench overview;
- L1 product rail component;
- L2 workflow-context sidebar component;
- node resource drawer component;
- canvas toolbar and minimap component;
- Agent / Station node card component with port variants;
- selected-node Inspector component;
- bottom Chat workbench with tabs;
- state and feedback component sheet;
- scenario flow sheet.

The Figma prototype may improve visual polish, spacing, density and micro-copy,
but it must not silently change component ownership, runtime boundaries or
navigation model.

## 12. Acceptance Criteria For Figma Review

Figma review cannot pass unless:

- major UI groups are editable layers, not one flattened screenshot;
- L1/L2 navigation matches this decision record;
- Agent/skill/MCP resources are in drawer/Inspector, not mixed into workflow L2;
- canvas nodes have visible ports and edge semantics;
- node selected/blocked/waiting/ready states are shown;
- Inspector is clearly read-only for evidence/runtime projections;
- bottom Chat is an independent workspace chat with proposal handoff semantics;
- state machine is visible through top bar, node state, Inspector and timeline;
- no copy claims Xpert parity, product-grade frontend completion, complete
  Workflow Studio, production readiness or Agent executor readiness.

## 13. Stop Conditions

- Using Xpert screenshots as HarnessOS implementation evidence.
- Treating this design record, HTML prototype or Figma prototype as browser,
  BFF, DTO or runtime evidence.
- Reintroducing letter placeholder icons into the final implementation.
- Hiding disabled or blocked reasons.
- Allowing drag/drop or Chat output to auto apply, publish or run.
- Adding Apply / Publish / Run controls without disabled, proposal-only or
  confirmation semantics.
- Collapsing `ready for review` into `ready`.

## 14. Traceability

Primary artifacts:

- `evidence/v12-0p-high-fidelity-prototype/imag2-vs-html-comparison.html`
- `evidence/v12-0p-high-fidelity-prototype/imag2-vs-html-comparison.fullpage.png`
- `evidence/v12-0p-high-fidelity-prototype/component-library-deep-design-audit.md`
- `evidence/v12-0p-high-fidelity-prototype/artifact-manifest.json`

Related planning documents:

- `v12_0p_high_fidelity_prototype_plan.md`
- `v12_figma_prototype_review_plan.md`
- `v12_to_v15_target_prd.md`
- `v12_to_v15_target_architecture.md`
