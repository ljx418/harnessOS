# HarnessOS Target Architecture For ChatGPT

## 用途、阅读对象与边界

- 用途：用 ChatGPT 可快速理解的方式说明 HarnessOS 的目标架构、当前阶段关系和关键边界。
- 阅读对象：技术评审者、架构师、Agent、产品负责人和需要做差距分析的人。
- 边界：本文是目标架构介绍，不是架构实现证明。任何实现状态必须回到 `data/project-status.json`、V12-V15/PV16 evidence summary 和代码验收报告。

## 架构意图

HarnessOS 的目标架构把“产品体验”和“运行时事实”分开：浏览器、Studio、Chat Workbench 和图形化内容只通过 BFF/DTO 与受控 Gateway 交互；runtime、tool、connector、artifact、trace、audit 和 evidence 由治理边界产生和记录。这样做的核心目的，是让 Agent 应用可以扩展，同时保留审计、审批、证据链和 No False Green 约束。

## 当前到目标的关系

```text
V3.0 Multi-App Core / Pack / Connector / Governance closeout
  -> V12 read-only Product Console and canvas foundation
  -> V13 editable Workflow Studio pilot
  -> V14 governed Plugin / Skill / Tool / MCP pilot
  -> V15 observability, audit and deployment-smoke baseline
  -> PV16 product-runtime hardening pilot
  -> future complete productized Studio and governed runtime platform
```

V3.0 证明了平台底座、Pack 装配、Connector registry、Job / Artifact / Governance hardening，以及 Meeting / Knowledge reference pack validation。V12-PV16 在此基础上推进浏览器产品化和 runtime-backed pilot，但仍按阶段保留严格边界。

## 目标架构总览

```text
User / Reviewer / Operator
  -> Product Console / Mission Studio
  -> Chat Workbench / Goal Intake
  -> Studio BFF / DTO allowlist
  -> Product Entity Control Plane
  -> Workflow DSL / Versioning / WorkflowDiff
  -> Agent / Station Configuration
  -> Plugin / Skill / Tool / MCP Ecosystem
  -> Runtime Gateway / Controlled Execution
  -> Artifact / Evidence / Quality
  -> Observability / Audit / Operations
  -> Deployment / Self-Hosting / PV16 Hardening
```

## 核心平面职责

| 平面 | 负责什么 | 不能负责什么 |
| --- | --- | --- |
| Product Console / Mission Studio | Web navigation、workspace/project/app 入口、Studio canvas、Inspector、Evidence browser。 | 直接 runtime mutation。 |
| Chat Workbench / Goal Intake | 自然语言目标输入、proposal timeline、WorkflowDiff 解释和 handoff。 | 静默发布或运行 workflow。 |
| Studio BFF / DTO | Browser route allowlist、DTO validation、manual confirmation、读写边界。 | provider secrets、raw runtime store writes。 |
| Product Entity Control Plane | StudioWorkspace、StudioProject、StationAgentProfile、binding、scope。 | runtime execution state。 |
| Workflow DSL / Versioning | WorkflowSpecGraph、WorkflowVersion、node/edge schema、diff、validation。 | 从浏览器直接改 StationRun truth。 |
| Agent / Station Configuration | role、goal、memory policy、model profile、tools、skills、MCP refs、permission policy。 | 不受限 Agent executor。 |
| Plugin / Skill / Tool / MCP Ecosystem | manifest、compatibility、install decision、scoped activation、unsafe denial。 | 未审查代码执行或绕过 policy。 |
| Runtime Gateway / Controlled Execution | GatewayService、RuntimeAdapter、controlled executor、event stream、run/inspect。 | 被 Studio 绕过。 |
| Artifact / Evidence / Quality | artifact refs、quality refs、evidence packages、redaction scan、claim scan。 | 用报告构造 runtime truth。 |
| Observability / Audit / Operations | trace、metrics、audit export、incident timeline、health check、deployment smoke。 | 产品能力过度声明。 |
| Deployment / Self-Hosting | compose/env/storage/queue/observability/runbook 的 bounded smoke。 | 生产 GA 声明。 |
| PV16 Product-Runtime Hardening | durable mutation、controlled runtime run/inspect、deployment health、setup-to-operations journey。 | 完整 Studio、完整 Agent executor 或生产可用。 |

## Product Console / Mission Studio

目标是让用户从一个真实产品入口管理 workspace、project、app 和 Station Agent，并进入 Studio canvas。当前 V12 证明的是 read-only workbench foundation：实体侧栏、只读画布、node cards、Inspector、evidence/status refs 和 unavailable action 的 disabled reasons。

这不等于完整产品级前端。它只说明浏览器 workbench 可以通过 BFF-shaped DTO 展示受控 read model。

## Workflow DSL 与 Studio

目标 DSL 包括 `WorkflowSpecGraph`、`WorkflowVersion`、node / edge schema、validation、diff、publish proposal 和 handoff。V13 已证明 editable Workflow Studio pilot slice：添加、配置、移动、连接节点，查看 validation，检查 selected node，并 review `WorkflowDiffProposal`。

V13 的关键边界是 `publish_or_run_started=false`。这说明它是编辑和 handoff pilot，不是完整运行或发布闭环。

## Agent / Station

目标 Agent / Station 配置包括 role、goal、memory policy、model profile、tools、skills、MCP refs 和 permission boundary。Station Agent 是产品实体和 workflow station 的桥梁，但当前不能把它描述为完整 Agent executor。

## Plugin / Skill / Tool / MCP

目标扩展生态要求 manifest validation、compatibility decision、workspace/tenant scope、policy checks、unsafe denial 和 audit refs。V14 证明的是 governed extension ecosystem pilot：可查看 manifest、compatibility、scoped activation 和 denial reason。

外部 MCP、LangGraph、Agents SDK、React Flow 等资料只提供生态参考；不能把这些生态能力写成 HarnessOS 已实现能力。

## Runtime Gateway / Controlled Execution

Runtime Gateway 是产品和执行面的受控边界。浏览器不应直接调用内部 runtime 或 store。run/inspect 应通过受控 RuntimeAdapter、GatewayService 和 evidence chain 产生可追溯事件。

PV16 证明了 runtime-backed run/inspect pilot 和 product-runtime hardening pilot，但不能把 pilot 扩大成完整 Agent executor 或生产运行平台。

## Evidence / Quality

Evidence plane 用来保存 acceptance data、route log、network log、schema validation、screenshots、redaction scan、No False Green scan、claim-to-evidence matrix 和 audit opinion。

判断原则：

- 有 evidence ref 才能说“该边界内可审查”。
- design-only artifact 只能支持设计审查。
- `docs/present` 内容只能帮助理解，不能替代 evidence package。

## Observability / Audit / Operations

V15 证明了 trace、metrics、audit、incident、deployment smoke 的前端交互和审查基线。它的职责是让 operator/reviewer 看到状态、问题和证据，而不是创造 runtime truth。

Deployment smoke 只说明 bounded local smoke 可审查，不说明生产部署、SLA、安全合规或正式 GA。

## PV16 Hardening

PV16 连接了产品实体 mutation、runtime-backed run/inspect、deployment hardening smoke 和 setup-to-operations journey。它是对 V12-V15 缺口的 pilot hardening，而不是最终完成声明。

PV16 可以说：

- 产品运行时硬化 pilot 已完成有界审查证据。
- runtime-backed run/inspect 在受控边界内可审查。
- deployment health 和 hardening smoke 有 bounded evidence。

PV16 不能说：

- HarnessOS 已生产可用。
- 完整 Workflow Studio 已完成。
- 完整 Agent executor 已完成。
- Xpert parity 已完成。

## Critical Boundaries

- Browser routes must go through BFF route allowlist。
- Browser denylist must block direct `/v1/rpc`、internal runtime routes 和 direct workflow store writes。
- Studio writes only through governed WorkflowSpec APIs and confirmation。
- Chat can propose and explain, but cannot silently publish or run。
- Plugin install requires manifest validation、compatibility、scope and policy checks。
- Tool/MCP invocation uses scoped capability binding。
- Observability is read-only unless it records governed audit/incident evidence。
- Presentation docs, HTML and images are not implementation evidence。
