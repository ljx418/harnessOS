# ChatGPT Review Prompt

## 用途、阅读对象与边界

- 用途：提供可直接复制给 ChatGPT / DeepSeek / 其他 Agent 的审查提示词。
- 阅读对象：希望让外部模型快速理解 HarnessOS 并避免误报的项目成员、审计者和读者。
- 边界：提示词只引导阅读和审查，不改变项目实际状态；模型回答仍必须遵守 `data/project-status.json`、V12-V15/PV16 evidence summary 和 No-Go 声明。

## 可直接复制的提示词

```text
你正在阅读 HarnessOS 项目介绍包。请先按顺序阅读以下文件：

1. docs/present/harnessos-project-introduction/00_CHATGPT_CONTEXT_INDEX.md
2. docs/present/harnessos-project-introduction/01_HARNESSOS_PROJECT_PRD_FOR_CHATGPT.md
3. docs/present/harnessos-project-introduction/02_TARGET_ARCHITECTURE_FOR_CHATGPT.md
4. docs/present/harnessos-project-introduction/03_CAPABILITY_BOUNDARY_AND_AUDIT.md
5. docs/present/harnessos-project-introduction/04_CHATGPT_REVIEW_PROMPT.md
6. docs/present/harnessos-project-introduction/05_OPC_ONE_PERSON_COMPANY_BRIEF_FOR_CHATGPT.md
7. docs/present/harnessos-project-introduction/index.html
8. docs/present/harnessos-project-introduction/image-manifest.json
9. docs/present/harnessos-project-introduction/data/project-status.json
10. docs/present/harnessos-project-introduction/data/sources.json

请基于这些文件，用中文回答：

- HarnessOS 是什么？
- 当前已验收能力有哪些？
- 哪些能力只是受限完成或 pilot？
- 哪些能力仍在规划中？
- 哪些声明属于 No-Go，不能被误报？
- 当前目标架构由哪些平面组成？
- V12、V13、V14、V15、PV16 分别证明了什么，又没有证明什么？
- 这个项目适合进入哪些应用场景，哪些场景仍需要后续开发？
- 如果基于本项目做 OPC（一人公司），最适合优先讨论哪 3 个产品化切入点？
- 如果你要审计本项目，请列出最重要的 10 个审计问题。

重要边界：

- 不要宣称 HarnessOS production ready。
- 不要宣称 Xpert parity complete。
- 不要宣称 product-grade frontend complete。
- 不要宣称 complete Workflow Studio ready。
- 不要宣称 Agent executor ready。
- 不要把 docs/present 的 HTML 页面、AI 内容图或介绍文档当作 runtime / BFF / DTO / browser E2E / production evidence。
- 可以把这些材料当作项目介绍、规划理解和审计入口。
```

## OPC 一人公司讨论提示词

```text
你正在帮助我基于 HarnessOS 讨论 OPC（一人公司 / One-Person Company）方向。请先阅读：

1. docs/present/harnessos-project-introduction/00_CHATGPT_CONTEXT_INDEX.md
2. docs/present/harnessos-project-introduction/01_HARNESSOS_PROJECT_PRD_FOR_CHATGPT.md
3. docs/present/harnessos-project-introduction/02_TARGET_ARCHITECTURE_FOR_CHATGPT.md
4. docs/present/harnessos-project-introduction/03_CAPABILITY_BOUNDARY_AND_AUDIT.md
5. docs/present/harnessos-project-introduction/05_OPC_ONE_PERSON_COMPANY_BRIEF_FOR_CHATGPT.md
6. docs/present/harnessos-project-introduction/data/project-status.json

请用中文回答：

- HarnessOS 对一人公司最有价值的定位是什么？
- 最适合先做的 3 个 OPC 场景是什么？
- 每个场景的目标客户、痛点、交付物和付费理由是什么？
- 当前有哪些能力可以作为 bounded evidence 或 pilot 讨论？
- 哪些能力必须继续开发后才能对外销售？
- 30 / 60 / 90 天验证路线应该怎么排？
- 哪些说法属于 No-Go，不能对客户、投资人或外部读者宣称？

重要边界：

- 不要宣称 HarnessOS production ready。
- 不要宣称 Xpert parity complete。
- 不要宣称 product-grade frontend complete。
- 不要宣称 complete Workflow Studio ready。
- 不要宣称 Agent executor ready。
- 不要把 docs/present 的 HTML 页面、AI 内容图或介绍文档当作 runtime / BFF / DTO / browser E2E / production evidence。
```

## 建议审查任务

| 任务 | 期望输出 |
| --- | --- |
| 项目理解 | 用 5 到 10 段中文说明 HarnessOS 的目标、当前状态和边界。 |
| 能力分类 | 按已验收、受限完成、规划中、No-Go 四类列出能力。 |
| 架构理解 | 解释 Product Console、Mission Studio、BFF/DTO、Workflow DSL、Agent/Station、Plugin/Skill/Tool/MCP、Runtime Gateway、Evidence、Observability、Deployment 的关系。 |
| 阶段审查 | 分别说明 V12、V13、V14、V15、PV16 的证明内容和未证明内容。 |
| OPC 产品化 | 基于 OPC brief 生成一人公司定位、首批场景、MVP 边界和验证路线。 |
| No False Green | 检查是否存在把 pilot 写成 complete、把 smoke 写成 production、把 presentation 写成 runtime evidence 的问题。 |
| 审计计划 | 生成 10 个最重要的审计问题，并指出需要查看的证据类型。 |

## 禁止误报清单

模型回答中不得正向声称：

- 不得正向声称 HarnessOS `production ready`。
- 不得正向声称 `Xpert parity complete`。
- 不得正向声称 `product-grade frontend complete`。
- 不得正向声称 `complete Workflow Studio ready`。
- 不得正向声称 `Agent executor ready`。
- 不得正向声称 `docs/present` HTML 页面或图片证明 runtime / BFF / DTO / browser E2E / production readiness。
- V13 handoff 已经 publish/run。
- V15 deployment smoke 等于生产部署。
- PV16 runtime-backed pilot 等于完整 Agent executor。
- 外部生态资料等于 HarnessOS 已实现能力。

## 推荐输出格式

```text
## HarnessOS 是什么

## 当前已验收能力

## 受限完成 / Pilot

## 规划中能力

## No-Go 声明

## 目标架构平面

## V12 / V13 / V14 / V15 / PV16 阶段判断

## 适合进入的场景

## OPC 一人公司切入点

## 仍需后续开发的场景

## 10 个审计问题
```

## 自检清单

回答完成前，模型应检查：

- 是否把 “有界审查证据” 写成了无边界完成？
- 是否把 pilot 写成 complete？
- 是否把 `index.html` 或图片当成实现证据？
- 是否漏掉 No-Go？
- 是否把外部生态参考当成 HarnessOS 能力？
- 是否把 V3.0 Meeting / Knowledge reference packs 写成平台内置业务终局？
