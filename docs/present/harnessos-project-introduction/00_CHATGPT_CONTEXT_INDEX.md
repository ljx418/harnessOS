# HarnessOS ChatGPT Context Index

## 用途、阅读对象与边界

- 用途：作为 ChatGPT、DeepSeek、其他 Agent 和人类读者理解 HarnessOS 项目介绍包的入口。
- 阅读对象：没有时间遍历全仓库、但需要审查项目目标、阶段状态、目标架构和证据边界的外部读者。
- 边界：本目录是 documentation-only presentation pack。`index.html`、22 张内容图和本文档只能作为介绍、规划理解和审计入口，不能作为 runtime、BFF、DTO、browser E2E、production evidence。

## 推荐阅读顺序

1. `00_CHATGPT_CONTEXT_INDEX.md`：入口索引和证据边界。
2. `01_HARNESSOS_PROJECT_PRD_FOR_CHATGPT.md`：面向 ChatGPT 的项目 PRD。
3. `02_TARGET_ARCHITECTURE_FOR_CHATGPT.md`：目标架构、平面职责和当前到目标关系。
4. `03_CAPABILITY_BOUNDARY_AND_AUDIT.md`：能力边界、No-Go 声明和审计规则。
5. `04_CHATGPT_REVIEW_PROMPT.md`：可复制审查提示词和输出格式。
6. `05_OPC_ONE_PERSON_COMPANY_BRIEF_FOR_CHATGPT.md`：面向 OPC（一人公司）产品化讨论的 ChatGPT brief。
7. `index.html`：人类可读项目介绍页。
8. `image-manifest.json`：22 张内容图的路径、用途、生成状态和来源记录。
9. `data/project-status.json`：本介绍包采用的能力状态 source of truth。
10. `data/sources.json`：本介绍包采用的本地与外部来源清单。

## 本包内容

| 文件 | 作用 | 证据边界 |
| --- | --- | --- |
| `README.md` | 目录说明和快速入口。 | 文档包说明，不是实现证据。 |
| `05_OPC_ONE_PERSON_COMPANY_BRIEF_FOR_CHATGPT.md` | OPC（一人公司）产品化讨论 brief 和可复制提示词。 | 商业/产品讨论入口，不是产品完成或生产证据。 |
| `index.html` | 可视化介绍页。 | 介绍页，不是运行、BFF、DTO 或浏览器验收证据。 |
| `presentation-preview.png` | 介绍页预览图。 | 视觉预览，不是产品运行证据。 |
| `image-manifest.json` | 22 张内容图的 manifest。 | 记录图像资产，不证明能力实现。 |
| `data/project-status.json` | V12/V13/V14/V15/PV16 状态和 No-Go。 | 当前介绍包的状态口径来源。 |
| `data/sources.json` | 本地与外部资料来源。 | 来源索引，不自动提升项目能力声明。 |
| `generation-log.md` | 图像生成记录。 | 只证明图像生成过程。 |
| `prompts/*.md` | 图像提示词。 | 说明素材，不是实现或验收证据。 |

## 22 张内容图

这些图片用于帮助读者快速理解项目，不能替代代码、运行日志、BFF route log、DTO schema validation、browser E2E 或 acceptance runner 输出。

```text
images/01-capability-status-map.png
images/02-target-architecture-map.png
images/03-user-journey-overview.png
images/04-workflow-studio-experience.png
images/05-evidence-governance-loop.png
images/06-extension-ecosystem.png
images/07-runtime-ops-and-observability.png
images/08-application-prospects.png
images/09-application-scenario-map.png
images/10-application-scenario-radar.png
images/11-ai-studio.png
images/12-code-doc-review.png
images/13-knowledge-workflow.png
images/14-content-storyboard.png
images/15-extension-ecosystem-scenario.png
images/16-ops-compliance.png
images/17-recruiting-interview.png
images/18-investment-research.png
images/19-sales-customer-ops.png
images/20-legal-finance-workflow.png
images/21-education-research.png
images/22-private-operations.png
```

## 本地 source of truth

本介绍包的阶段判断只跟随以下文件，不从展示图或宣传文案推导：

| 来源 | 用途 |
| --- | --- |
| `data/project-status.json` | 当前介绍包的 accepted / limited_done / planned / no_go 列表。 |
| `docs/design/V12-V15.x/v12_to_v15_target_prd.md` | V12 到 PV16 的产品目标、用户场景、受限完成口径。 |
| `docs/design/V12-V15.x/v12_to_v15_target_architecture.md` | 目标架构平面、职责边界和 critical boundaries。 |
| `docs/design/V12-V15.x/evidence/full-stage-acceptance-review-2026-06-25/acceptance-summary.json` | V12/V13/V14/V15/PV16 有界验收摘要。 |
| `TASKS.md` | CLI-first backend iteration、业务链路、生产治理和多 Agent 后续规划。 |
| `CLAUDE.md` | 项目工作方式、编码规范和历史架构约束。 |
| `docs/design/V3.0/00_README.md` | V3.0 final closeout archive 入口。 |
| `docs/design/V3.0/v3_development_plan_multi_app_core.md` | V3.0 Multi-App Core、Pack、Connector、Governed Runtime Adapter source of truth。 |
| `docs/design/V3.0/v3_current_gap_analysis.md` | V3.0 已具备能力、差距和 V3.x+ 后续边界。 |
| `docs/design/V3.0/CURRENT-STATUS_v3.md` | V3.0 当前实际实现、验收证据和冻结原则。 |

## 外部生态参考

外部资料只用于说明生态方向和应用前景，不能写成 HarnessOS 已实现能力。

| 外部资料 | 用途 |
| --- | --- |
| <https://modelcontextprotocol.io/docs/getting-started/intro> | MCP 作为连接外部系统、工具、数据和工作流的开放标准参考。 |
| <https://www.langchain.com/langgraph> | single-agent、multi-agent、hierarchical workflow 的行业方向参考。 |
| <https://reactflow.dev/> | 节点画布交互基线参考。 |
| <https://developers.openai.com/api/docs/guides/agents> | Agents、工具调用、多步状态管理方向参考。 |
| <https://github.com/openai/openai-agents-python> | multi-agent workflow 框架参考。 |
| <https://github.com/modelcontextprotocol> | MCP 开源生态参考。 |
| <https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/4496698/nsa-releases-security-design-considerations-for-ai-driven-automation-leveraging/> | AI-driven automation 与 MCP 安全设计提醒。 |
| <https://socprime.com/blog/mcp-security-risks-and-mitigations/> | MCP 风险、最小权限、审计和工具治理提醒。 |

## 快速判断规则

- 能力声明必须能追溯到 `data/project-status.json` 或 V12-V15/PV16 evidence summary。
- “展示图好看”不等于“能力已实现”。
- “HTML 页面可打开”不等于“产品前端已完成”。
- “deployment smoke PASS”不等于“生产可用”。
- “PV16 runtime-backed run/inspect pilot”不等于“完整 Agent 执行器已完成”。
- “V13 editable Studio pilot”不等于“完整 Workflow Studio 已完成”。
