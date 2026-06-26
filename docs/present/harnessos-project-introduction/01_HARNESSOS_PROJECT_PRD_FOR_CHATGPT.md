# HarnessOS Project PRD For ChatGPT

## 用途、阅读对象与边界

- 用途：帮助 ChatGPT、DeepSeek、其他 Agent 和人类读者用统一口径理解 HarnessOS 是什么、为什么做、当前证明了什么、还没有证明什么。
- 阅读对象：需要做项目理解、方案评审、差距分析、投资/产品/技术审查的读者。
- 边界：本文是 PRD-style introduction，不是代码实现、runtime evidence、BFF evidence、DTO evidence、browser E2E evidence 或 production evidence。

## 一句话定义

HarnessOS 是一个面向多应用、多 Agent、可治理执行和证据审计的 Agent runtime / app-server 项目。当前方向是 CLI-first backend iteration，并在此基础上逐步补齐 Product Console、Mission Studio、Workflow DSL、Agent/Station、Plugin/Skill/Tool/MCP 扩展生态、Runtime Gateway、Evidence、Observability 和 Deployment hardening。

## 产品愿景

HarnessOS 的目标不是复制 Xpert，也不是把展示页包装成产品完成状态。目标是把已有 CLI/TUI-first governed runtime 演进为可审查、可治理、可扩展的小工作室产品基础：

- 用户能在产品入口管理 workspace、project、app、Station Agent 和 workflow。
- 开发者能通过 Gateway、Pack、Connector、RuntimeAdapter、Policy、Approval、Trace 和 Evidence 边界接入新业务。
- 审计者能把每个产品声明追溯到运行证据、DTO、route log、browser scenario、acceptance report 或明确的设计/规划边界。
- 系统不能让概念图、原型页、HTML 介绍页或 AI 内容图替代真实验收证据。

## 目标用户

| 用户 | 主要诉求 | 当前边界 |
| --- | --- | --- |
| 开发者 / 平台工程师 | 用统一协议、Pack、Connector 和 RuntimeAdapter 接入 Meeting、Knowledge、Interview、Investment、Video Studio 等应用。 | V3.0 已验证 multi-app core 和 reference packs；新增业务仍需要遵守平台边界。 |
| 小团队 / 工作室操作者 | 从目标输入、Agent 配置、Workflow Studio、运行查看到证据审计形成闭环。 | 该目标仍处于 staged productization；V12-PV16 只是有界阶段证据。 |
| 审计者 / 评审者 | 区分已验收、pilot、规划中和 No-Go。 | 必须以 evidence package 和 `project-status.json` 为准。 |
| 运维 / 自托管用户 | 本地启动、health check、trace、metrics、audit、deployment smoke。 | V15/PV16 只证明 bounded smoke 和 hardening pilot，不证明生产可用。 |
| 外部 Agent / 对话模型 | 快速理解项目，不误报能力。 | 只能把本包作为介绍和审计入口。 |

## 核心场景

| 场景 | 目标体验 | 当前状态 |
| --- | --- | --- |
| CLI / Gateway 运行 | 通过 CLI、HTTP、RPC 或 stdio JSONL 启动 session/turn，获得规范化事件。 | Phase 0.5-0.7 和 V3.0 文档记录已完成核心协议与控制面闭环。 |
| Multi-App Core | 同一 Core 支持 meeting、knowledge、interview、investment、video_studio 等 app profile。 | V3.0-PhaseA 到 PhaseE 已完成 closeout / validation。 |
| Meeting reference pack | 通过 FunASR MCP 和 Meeting workflow 生成 transcript、analysis、result、minutes artifacts。 | V3.0 reference pack validation passed；业务质量不等同于完整产品化。 |
| Knowledge reference pack | 通过 data_service MCP 完成 source、note、brief、citation bundle 生命周期。 | V3.0 PhaseE validation passed；仍是 reference pack 语义。 |
| Product Console / Mission Studio | 浏览器产品入口、实体侧栏、画布、Inspector、Chat Workbench、Evidence drawer。 | V12 证明只读 foundation；不是完整产品前端。 |
| Editable Workflow Studio | 可编辑 WorkflowSpecGraph、节点、连线、验证、WorkflowDiff handoff。 | V13 证明 editable pilot slice；不发布、不运行。 |
| Extension ecosystem | Plugin / Skill / Tool / MCP manifest、兼容性、scoped activation、unsafe denial。 | V14 证明 governed ecosystem pilot。 |
| Observability / Deployment | trace、metrics、audit、incident、local health 和 smoke。 | V15 证明 frontend interaction baseline 和 bounded smoke。 |
| Product-runtime hardening | product mutation、runtime-backed run/inspect、setup-to-operations journey。 | PV16 证明 hardening pilot；不是 GA。 |

## 当前已验收能力

以下能力来自 `data/project-status.json` 和 V12-V15/PV16 acceptance summary，必须保留“有界审查证据”语义：

| 阶段 | 当前可说的正向结论 | 不能推出的结论 |
| --- | --- | --- |
| V12 | 产品实体、浏览器工作台与只读画布 foundation 已完成有界审查证据。 | 不证明运行时执行、产品级前端完成度或完整 Workflow Studio。 |
| V13 | 可编辑 Workflow Studio pilot slice 已完成有界审查证据。 | 不证明完整 Studio、不证明运行时执行或自主发布。 |
| V14 | 受治理的 Plugin / Skill / Tool / MCP 扩展生态 pilot 已完成有界审查证据。 | 不证明不受限插件市场或任意工具执行。 |
| V15 | 前端交互、观测、审计和部署 smoke 基线已完成有界审查证据。 | 不证明生产部署或正式 GA。 |
| PV16 | 产品运行时硬化 pilot 已完成有界审查证据。 | 不证明完整 Agent 执行器、完整 Studio 或生产可用。 |

## 受限完成能力

- 浏览器工作台可以展示真实 BFF/DTO 数据，但 V12 画布仍是只读 foundation。
- V13 Studio pilot 支持编辑、移动、连接和 WorkflowDiff handoff，但不是完整 Workflow Studio。
- V14 支持受治理扩展生态 pilot，但不是开放式插件市场或任意工具执行面。
- V15 支持 trace、metrics、audit、deployment smoke 的浏览器审查基线，但不是生产部署。
- PV16 可展示受控 runtime run/inspect 证据，但不是完整 Agent executor。
- V3.0 Meeting / Knowledge 是 reference packs / validation samples，不是内置业务终局。

## 规划中能力

| 方向 | 说明 |
| --- | --- |
| 统一产品入口 | 真实用户可从 Product Console 进入 workspace、project、app、Station Agent 和 Studio。 |
| 完整 Workflow Studio | 版本化 DSL、完整可视编辑、发布治理、回滚、运行检查和审计闭环。 |
| 多租户治理 | 更完整的权限、审批、审计、密钥治理、隔离、限流和运维手册。 |
| 业务链路产品化 | Meeting、Interview、Knowledge、Media 等从 reference pack / planned workflow 演进为端到端产品体验。 |
| 扩展生态 | Plugin、Skill、Tool、MCP 的第三方示例、兼容策略和安全沙箱。 |
| SDK / external app contract | Python / TypeScript SDK、protocol version、method/event/error registry、auth MVP。 |

## No-Go 声明

以下声明不能被 ChatGPT 或任何外部读者误报为已完成：

- 不要宣称 HarnessOS `production ready`。
- 不要宣称 `Xpert parity complete`。
- 不要宣称 `product-grade frontend complete`。
- 不要宣称 `complete Workflow Studio ready`。
- 不要宣称 `Agent executor ready`。
- 不要把 `docs/present` 的 HTML 页面、AI 内容图或介绍文档当作 runtime / BFF / DTO / browser E2E / production evidence。
- 不要把外部生态参考写成 HarnessOS 已实现能力。

## 验收证据口径

| 证据类型 | 可以证明 | 不能证明 |
| --- | --- | --- |
| Acceptance summary / runner output | 某个阶段在指定边界内 PASS。 | 超出该阶段边界的产品完成度。 |
| Browser E2E / screenshot / network log | 指定页面、路由和交互状态可审查。 | 生产可用或完整运行时能力。 |
| BFF route log / DTO schema validation | 浏览器通过 allowlisted BFF/DTO 边界访问数据。 | 浏览器可绕过 BFF 或直接拥有 runtime truth。 |
| Runtime-backed report | 指定 run/inspect pilot 经过受控 runtime。 | 完整 Agent executor 或生产执行平台。 |
| Deployment smoke | 本地 health / bounded smoke 可审查。 | 生产部署、SLA、安全合规完成。 |
| HTML 介绍页 / 内容图 | 帮助理解项目和架构。 | 任何产品运行、BFF、DTO、browser E2E 或 production evidence。 |

## 适合进入的应用场景

当前更适合：

- CLI-first backend iteration。
- 协议、Gateway、Pack、Connector、RuntimeAdapter、Artifact、Trace 和 Evidence 边界的持续开发。
- Meeting / Knowledge reference pack 的平台边界回归和 connector 验证。
- Product Console / Mission Studio 的 staged review、审计入口和 bounded pilot 演进。
- 面向外部 Agent 的项目理解、审计问题生成和 No False Green 检查。

当前仍需要后续开发后再进入：

- 真实生产部署。
- 面向非技术用户的完整产品化前端。
- 完整 Workflow Studio 发布/运行/回滚闭环。
- 不受限插件市场。
- 完整 Agent 执行器。
- 企业级多租户、权限、密钥、审计、计费、SLA 和运维闭环。
