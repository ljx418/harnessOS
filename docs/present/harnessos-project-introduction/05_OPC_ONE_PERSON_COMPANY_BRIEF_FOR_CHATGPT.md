# HarnessOS OPC One-Person Company Brief For ChatGPT

## 用途、阅读对象与边界

- 用途：帮助 ChatGPT、DeepSeek、其他 Agent 和人类读者把 HarnessOS 放到 OPC（一人公司 / One-Person Company）产品化语境中讨论。
- 阅读对象：希望基于 HarnessOS 思考个人公司、小团队 AI 工作室、垂直流程产品化、服务交付自动化和商业验证路径的人。
- 边界：本文是产品化讨论 brief，不是商业计划书、投资承诺、运行时证据、BFF 证据、DTO 证据、browser E2E 证据或 production evidence。所有能力判断仍必须回到 `data/project-status.json`、V12-V15/PV16 evidence package 和 No-Go 声明。

## 一句话 OPC 定位

HarnessOS 可以作为一人公司或小团队的可治理 Agent 工作流底座：把一次性 AI 对话、人工判断、工具调用、产物交付和审计证据沉淀为可复用、可复查、可交接的业务流程。

这不是“当前已经能直接对外售卖的完整 SaaS”。更准确的讨论方式是：HarnessOS 已经具备若干可审查的基础能力和 pilot 证据，可以围绕高价值、低风险、强审计需求的细分场景设计 OPC 的第一批产品化实验。

## 为什么适合 OPC 讨论

| OPC 需求 | HarnessOS 可讨论价值 | 当前边界 |
| --- | --- | --- |
| 一个人要复用自己的交付流程 | 用 workflow、artifact、evidence、trace 把交付步骤沉淀下来。 | 仍需把具体业务流程产品化，不等于完整用户产品。 |
| 一个人要控制 AI 自动化风险 | 用 WorkflowDiff、人工确认、policy、audit 和 claim scan 降低误操作。 | V13/PV16 是 bounded pilot，不是完整 Agent executor。 |
| 一个人要向客户解释交付质量 | 用证据链、引用、审查记录和产物 lineage 支撑复盘。 | 展示页和图片不能作为运行证据。 |
| 一个人要逐步扩展能力 | 通过 Plugin / Skill / Tool / MCP 的受治理接入探索扩展生态。 | V14 不证明开放插件市场或任意工具执行。 |
| 一个人要自托管和控制数据 | 以 local / self-hosted、health、trace、audit、redaction 为方向设计。 | V15/PV16 不证明生产部署、SLA 或企业合规完成。 |

## OPC 应用场景优先级

以下场景基于现有介绍包中的 12 个应用前景重排。它们用于产品化讨论，不代表全部已实现。

| 优先级 | 场景 | OPC 价值主张 | 当前判断 |
| --- | --- | --- | --- |
| P0 | 代码与文档审查 | 帮独立开发者或小团队把需求、代码、文档、变更说明和审查证据串成可复查流程。 | 可围绕现有 evidence / WorkflowDiff 语义讨论 MVP，但仍需具体产品化开发。 |
| P0 | 知识工作流 | 把会议、资料、知识库问答、引用证据和 brief 生成统一到可追溯工作台。 | Meeting / Knowledge 有 reference pack 基础，但不是完整业务产品。 |
| P0 | AI 工作室 | 把重复的提示词、分工、检查点和交付件变成可复用的多 Agent 流程资产。 | 适合作为 OPC 总定位，但当前不能声称完整工作室产品完成。 |
| P1 | 内容与分镜 | 将 brief、脚本、分镜、素材检查、质量门禁和产物 lineage 组织成交付流水线。 | 属于高潜力方向，端到端媒体产品化仍需后续开发。 |
| P1 | 运维与合规 | 面向自托管或内部工具，把 health、trace、metrics、audit、redaction 和 claim scan 变成审查材料。 | V15/PV16 有 bounded smoke / hardening pilot；不是生产运维闭环。 |
| P1 | 私有化运维 | 为小团队提供本地部署、运行检查、审计导出和风险扫描的交付包。 | 可以讨论服务化交付，但不能写成 production ready。 |
| P2 | 扩展生态 | 围绕 MCP、Skill、Tool、Plugin 做受治理能力接入、兼容性检查和范围控制。 | V14 是 governed ecosystem pilot，不是开放市场。 |
| P2 | 招聘面试 | 将 JD 分析、候选人材料、模拟问答、评分和改进建议沉淀为可复查流程。 | 适合垂直产品假设，当前仍需业务链路产品化。 |
| P2 | 投研分析 | 将资料收集、假设拆解、引用追踪、风险审查和报告生成纳入证据链。 | 高价值但高责任，需要更严格引用、审计和免责声明。 |
| P2 | 销售与客服运营 | 把线索研判、话术生成、工单总结和升级建议放进受控 Agent 工作台。 | 可作为内部运营工具假设，仍需 CRM / 工单系统接入证据。 |
| P3 | 法务与财务流程 | 做文档初筛、条款检查、付款材料整理等需要审批和审计的流程。 | 高风险领域，只适合讨论辅助流程，不应宣称替代专业判断。 |
| P3 | 教育教研 | 探索课程资料整理、教案生成、学习反馈汇总和引用可追溯知识工作流。 | 适合低风险试点，仍需具体用户流程和质量评价。 |

## 推荐 OPC 切入路径

| 路径 | 第一批产品形态 | 为什么先做 | 主要补证 |
| --- | --- | --- | --- |
| 审查型 AI 工作台 | 代码/文档/知识 brief 审查包。 | 风险可控，能突出 evidence、WorkflowDiff、人工确认和审计价值。 | 真实样例、浏览器流程、BFF/DTO、产物 lineage、用户验收记录。 |
| 私有知识交付包 | 面向客户资料整理、会议纪要、知识问答和引用报告。 | 与 Meeting / Knowledge reference pack 方向一致，适合服务化试点。 | 端到端业务样例、引用质量、失败恢复、数据隔离、脱敏。 |
| 小团队 AI 工作室模板 | 把常见交付流程做成可复制 workflow 和审查模板。 | 对 OPC 来说可复用性强，容易从服务交付过渡到产品。 | 模板版本、运行记录、人工确认、回滚和可解释失败。 |
| 自托管治理包 | health、trace、audit、redaction、claim scan 和 smoke 检查。 | 与 V15/PV16 的运维审查方向一致，适合技术型客户。 | 部署手册、安全基线、租户隔离、密钥治理、故障演练。 |

## 30 / 60 / 90 天验证问题

| 时间窗 | 目标 | 需要回答的问题 |
| --- | --- | --- |
| 30 天 | 找到一个低风险、强复用、愿意付费的 OPC 场景。 | 谁最痛？他现在用什么替代方案？哪一步最愿意外包给可审计 AI 工作流？ |
| 60 天 | 做出一个可演示、可审查、可交付的业务闭环。 | 输入、人工确认、工具调用、产物、引用、审计和失败恢复是否可复查？ |
| 90 天 | 验证服务化收入或小范围产品付费。 | 客户愿意为流程、结果、审计证据还是自托管交付付费？交付成本是否下降？ |

## 商业模式假设

| 模式 | 适合场景 | 风险 |
| --- | --- | --- |
| 服务化交付 | 知识整理、代码/文档审查、内容分镜、私有化运维。 | 容易变成人工外包，需要用 workflow 和 evidence 沉淀可复用资产。 |
| 模板/流程包 | AI 工作室模板、审查清单、知识工作流模板。 | 需要足够明确的用户画像和可复制的输入输出。 |
| 自托管实施 | 小团队、咨询公司、研发团队、内部工具团队。 | 需要补生产部署、安全、权限、密钥和运维证据。 |
| 垂直微 SaaS | 招聘、投研、销售客服、教育教研等。 | 需要端到端产品前端、数据接入、质量评估和行业责任边界。 |

## 不适合当前直接宣称的方向

- 不适合把 HarnessOS 宣称为 production ready 的 SaaS。
- 不适合宣称已完全追平 Xpert。
- 不适合宣称 product-grade frontend complete。
- 不适合宣称 complete Workflow Studio ready。
- 不适合宣称 Agent executor ready。
- 不适合把 `docs/present` 的 HTML 页面、AI 内容图或介绍文档当作 runtime / BFF / DTO / browser E2E / production evidence。
- 不适合在法务、财务、投研、医疗、安全等高风险领域宣称替代专业人员或自动决策。

## 可直接复制给 ChatGPT 的 OPC 提示词

```text
你正在帮助我基于 HarnessOS 讨论 OPC（一人公司 / One-Person Company）方向。请先阅读：

1. docs/present/harnessos-project-introduction/00_CHATGPT_CONTEXT_INDEX.md
2. docs/present/harnessos-project-introduction/01_HARNESSOS_PROJECT_PRD_FOR_CHATGPT.md
3. docs/present/harnessos-project-introduction/02_TARGET_ARCHITECTURE_FOR_CHATGPT.md
4. docs/present/harnessos-project-introduction/03_CAPABILITY_BOUNDARY_AND_AUDIT.md
5. docs/present/harnessos-project-introduction/04_CHATGPT_REVIEW_PROMPT.md
6. docs/present/harnessos-project-introduction/05_OPC_ONE_PERSON_COMPANY_BRIEF_FOR_CHATGPT.md
7. docs/present/harnessos-project-introduction/data/project-status.json
8. docs/present/harnessos-project-introduction/data/sources.json

请用中文回答：

- 如果我要基于 HarnessOS 做一人公司，它最适合切入哪 3 个场景？
- 每个场景的目标客户、痛点、交付物、付费理由分别是什么？
- 哪些能力当前有 evidence 或 bounded pilot 支撑，哪些必须继续开发？
- 第一版 MVP 应该避免做什么？
- 30 / 60 / 90 天验证路线应该怎么排？
- 哪些说法属于 No-Go，不能对客户、投资人或外部读者宣称？
- 如果你是我的产品顾问，请提出 10 个最关键的追问。

重要边界：

- 不要宣称 HarnessOS production ready。
- 不要宣称 Xpert parity complete。
- 不要宣称 product-grade frontend complete。
- 不要宣称 complete Workflow Studio ready。
- 不要宣称 Agent executor ready。
- 不要把 docs/present 的 HTML 页面、AI 内容图或介绍文档当作 runtime / BFF / DTO / browser E2E / production evidence。
- 可以把这些材料当作项目介绍、OPC 产品化讨论和审计入口。
```

## 给 ChatGPT 的推荐输出格式

```text
## OPC 总判断

## 最适合先做的 3 个场景

## 每个场景的客户、痛点、交付物和付费理由

## 当前可依赖的能力与证据

## 必须继续开发的能力

## 不应对外宣称的 No-Go

## 30 / 60 / 90 天验证路线

## 10 个关键追问
```
