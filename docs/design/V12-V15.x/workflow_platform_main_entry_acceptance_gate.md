# Workflow Platform Main Entry Acceptance Gate

用途：定义 PV13-based 工作流平台首入口文档阶段和后续实现阶段的验收门槛。
边界：本文不是实现证据。

## 1. WP-M0 Document Gate

| Gate | PASS condition | FAIL condition |
| --- | --- | --- |
| Document completeness | PRD、架构、计划、里程碑、验收、gap、任务矩阵、审计、drawio 全部存在并明确 PV13 是首页基线。 | 任一必需文档缺失或仍把 PV21 shell / 退化入口作为首页基线。 |
| Contract completeness | BFF/DTO contract、acceptance runner spec、implementation readiness audit 全部存在。 | 缺少 route allowlist、DTO snapshot 或 runner output 规格。 |
| Naming consistency | 统一使用 WP-M0/WP-M1... 表示首入口对齐；V13/PV13 是前端基线，PV19/PV20/PV21 是能力来源。 | 把 WP-M0 写成 PV22 implementation、把 PV13 写成 product-grade complete 或把 PV21 写成 GA。 |
| Capability non-regression | 明确 `WorkflowPlatformMainEntry` 是 PV21/PV20 能力迁移对照，不是目标首页视觉基线。 | 只写“替换 WorkflowPlatformMainEntry”，但未规定已接入运行/执行器能力如何迁移。 |
| WP-M5A ordering | 明确 WP-M5A 是业务场景产品化与数据驱动投影前置门禁，PV22 后置为 WP-M5B。 | 直接从 WP-M4 跳到 PV22-S1，或把三场景路径验收写成业务产物完成。 |
| Drawio quality | 不超过 8 页，中文，颜色语义一致，具体代码实体清晰。 | 文本溢出、重复冲突、含糊模块名、架构关系不清。 |
| Architecture specificity | 出现真实代码实体、BFF routes、DTO、store、runtime/evidence artifacts。 | 只出现抽象概念，无法指导实现。 |
| Claim safety | forbidden terms 只允许出现在 No-Go、风险、FAIL 条件或禁止声明语境中。 | 出现 production ready、complete Studio ready、Agent executor ready 等正向误报。 |

## 2. WP-M1 PV13 Baseline Homepage Gate

- `/bff/v13/*` compatibility route 来源必须明确：主 BFF route smoke PASS，或明确标注为 bounded acceptance smoke server evidence。
- 若 `/bff/v13/*` 仅来自 smoke server，报告不得把它写成主 BFF/runtime 完成证据。
- 无 query 根入口默认进入 PV13 Light Studio 工作流平台。
- `?studio=workflow-platform` 进入 PV13 Light Studio 工作流平台。
- `?studio=v13-editable-studio` 继续可访问。
- 首屏明确 workspace/project/state，并保留 PV13 场景列表、力感画布、Inspector、仿真控制、Workspace/evidence 区域。
- Browser network log 只出现允许 BFF routes。
- DTO snapshot 必须符合 `/bff/v13/*` 或后续兼容 DTO 组合形态。
- 中文验收报告含首屏截图。
- FAIL：`/bff/v13/*` route 缺失或 route 来源未说明。
- FAIL：默认首页仍进入 `WorkflowPlatformMainEntry` 退化版。

## 3. WP-M2 PV13 Canvas Interaction Gate

- 滚轮缩放 PASS。
- 平移和节点拖拽 PASS，包括右侧/远端画布区域。
- 端口发起连接 PASS。
- 合法目标自由连接 PASS。
- 取消连线 PASS。
- 非法连接提示 PASS。
- 箭头在首眼和缩放状态下可见 PASS。
- 连线不遮挡关键文本 PASS。

## 4. WP-M3 Runtime Evidence Gate

- WorkflowDiff 需要人工确认。
- Publish 生成 WorkflowVersion readback。
- Run 生成 WorkflowInstance / StationRun readback。
- Human gate 改变后端可回读状态。
- Evidence panel 展示 artifact / trace / quality / audit / claim / redaction refs。
- Acceptance report 区分真实运行证据、浏览器证据和文档证据。
- Runtime inspect report 必须包含 WorkflowVersion、WorkflowInstance、StationRun 和 audit refs。
- 以上能力必须呈现在 PV13-based 工作台中，不能只跳转到分散 PV19/PV21 阶段页完成。
- `workflow-platform-capability-parity-report.json` 必须证明 `WorkflowPlatformMainEntry` 当前 PV21 能力未退化：graph save/readback、validate、diff、publish、rollback、run、inspect、human action、evidence review。
- FAIL：PV13-based 工作台只保留外观，但缺失上述任一 PV21 闭环能力且未获用户确认延期。

## 5. WP-M4 Executor Integration Gate

- Agent/Tool/Skill/MCP 入口只展示受治理能力。
- Approval denial、timeout、cancel、retry、redaction fixtures 可回读。
- UI 不暗示 unrestricted automation。
- Evidence ref 能追踪到 PV20 bounded executor path 或后续真实执行证据。
- 以上能力必须接入 PV13-based 资源/Inspector/证据区域。
- `workflow-platform-capability-parity-report.json` 必须证明 `WorkflowPlatformMainEntry` 当前 PV20 executor 能力未退化：executor state、execution contract、execution evidence、skill/tool/MCP action、approval/denial refs。
- FAIL：PV13-based 工作台无法触达 PV20 受治理执行器能力，或把其误写成 unrestricted automation。

## 6. WP-M5A Business Scenario Productization Gate

WP-M5A 是 PV22 前置门禁。它必须把当前三个 required business scenarios 从“路径验收通过”升级为“业务产物可审查”。

- 场景目录、输入要求、节点模板、Inspector、timeline、输出摘要和 evidence refs 必须来自 DTO/evidence projection，或明确标注 fallback。
- 文档/知识总结必须至少生成机器可读摘要、引用/证据 refs、质量结果和人工复核记录。
- 代码审查/变更风险检查必须至少生成机器可读审查摘要、风险等级、测试/静态检查 refs 和审批记录。
- 会议/访谈整理必须至少生成机器可读纪要/行动项摘要、引用证据和复核记录。
- `business-output-report.json` 必须逐场景记录 artifact refs、trace refs、quality refs、audit refs、claim refs、redaction refs 和 human review refs。
- `mock-reduction-report.json` 必须列出仍保留的 `scenarioData`、`fallbackGraph`、静态 chat/timeline/Inspector 使用点，并标注为 fallback/design reference。
- HTML 报告必须把“路径验收证据”和“业务产物证据”分开。
- FAIL：只复用 `business-scenario-groups.json`、截图或 acceptance report 文本，就声明业务产物完成。
- FAIL：前端静态场景数据被写成后端真实业务投影。

## 7. Target User Scenario Exit Gate

工作流平台出门验收不能只证明“用户能看到画布、运行和证据”。验收报告必须证明用户能用平台完成具体工作。

### 7.1 Required Minimum Scenario

| Scenario | User input | Required platform actions | Human review point | Required output | Exit evidence |
| --- | --- | --- | --- | --- | --- |
| 基础 Agent 工作流 | 一个工作目标，例如“总结一组文档并审查证据”。 | 打开 PV13 首页、拖拽/调整节点、连接节点、配置 Agent/Tool/Skill/MCP、保存草稿、校验图、生成 WorkflowDiff、发布版本、运行工作流。 | WorkflowDiff 确认和 Human Gate 审批。 | WorkflowInstance、StationRun、工作流产物、Evidence panel。 | PV13 画布截图、edge action log、BFF route log、DTO snapshot、runtime inspect、human action report、evidence panel report。 |

该场景是 WP-M3 出门的最低条件。若不能完成，不得声明工作流平台 MVP 候选体验 ready for bounded review。

### 7.2 Required Business Scenarios

WP-M3 出门前必须跑通以下三个业务场景；WP-M4 出门前必须证明三个场景对应的 Agent/Tool/Skill/MCP 入口均是受治理能力；WP-M5A 出门前必须进一步证明每个场景都有可审查业务产物。

| Scenario | How the user uses HarnessOS | Platform workflow | Acceptance output | Boundary |
| --- | --- | --- | --- | --- |
| 文档/知识总结 | 用户导入文档、Markdown 文件夹或知识材料，要求系统总结并保留证据。 | 输入节点 -> 解析节点 -> 事实抽取 Agent -> 总结 Agent -> 质量检查 -> 证据审查。 | 带 evidence refs 的摘要产物、质量结果、人工审查记录。 | 必验业务场景。 |
| 代码审查 | 用户输入 Git diff、PR patch 或代码包，要求系统生成审查报告。 | 输入节点 -> 静态检查 Agent -> 安全审计 Agent -> 汇总 Agent -> 合规 Human Gate。 | 代码审查报告、风险列表、人工合规审批记录。 | 必验业务场景，不能替代 CI 生产安全审计。 |
| 会议/访谈整理 | 用户输入 transcript 或 audio-derived text，要求生成纪要和行动项。 | 输入节点 -> 议题提取 Agent -> 行动项 Agent -> 事实核对 -> 人工复核。 | 会议纪要、行动项、引用证据和复核记录。 | 必验业务场景；真实音频 ASR 仍按 Meeting pack / connector 证据单独验收。 |

### 7.3 Optional / Future Application Scenarios

以下场景可以展示平台应用前景，但不得作为本阶段已经完成的核心出门声明，除非后续生成独立实现证据。

| Scenario | How the user would use HarnessOS | Output | No-Go boundary |
| --- | --- | --- | --- |
| 创意分镜规划 | 输入脚本，编排导演/艺术/摄影/版权审查 Agent，生成 storyboard spec。 | 分镜规划 JSON、审查记录、版权/合规 gate。 | 不声明真实视频渲染完成。 |
| 外部工具/MCP 受治理自动化 | 绑定 allowlisted Tool/MCP，运行受控节点并审查 approval/denial。 | Tool/MCP execution refs、audit refs、denial fixtures。 | 不声明 unrestricted automation 或 Agent executor ready。 |
| 外部 App 接入 | 外部应用通过 SDK/BFF template/reference app 接入工作流平台。 | SDK smoke、template smoke、reference app E2E。 | PV22 implementation evidence 生成前不得声明完成。 |

### 7.4 Scenario Exit Rule

- WP-M3 PASS requires the minimum Agent workflow scenario and all three required business scenarios.
- WP-M4 PASS requires governed Agent/Tool/Skill/MCP evidence for all three required business scenarios.
- WP-M5A PASS requires independent business output artifacts or machine-readable business output summaries for all three required business scenarios.
- Each scenario must include screenshots, BFF route log, DTO snapshot, runtime/evidence refs, PRD review and No False Green scan.
- If a scenario is presented only as future applicability, the acceptance report must label it as `规划中` or `后续扩展`.

## 8. Forbidden Positive Claims

以下文本或等价中文不得出现在验收通过声明中：

- `production ready`
- `product-grade frontend complete`
- `complete Workflow Studio ready`
- `Workflow Studio GA`
- `Agent executor ready`
- `unrestricted automation`
- `Xpert parity complete`
- `WP-M5A business scenarios productized`，除非明确限定为 bounded machine-readable summaries，不得暗示最终商业业务产物完成
- `PV13 homepage replacement complete`，除非后续真实实现证据已生成
- `PV22 implementation complete`，除非后续真实实现证据已生成
- `real video rendering complete`，除非后续 Video Studio 真实渲染证据已生成

## 9. Allowed Claims

WP-M0 完成后仅允许：

```text
Workflow Platform main-entry documentation gate is aligned to the PV13 frontend baseline for implementation review.
```

WP-M1+ 后续实现必须按实际证据逐阶段声明 bounded review ready。

WP-M5A 有界验收通过后仅允许：

```text
WP-M5A business-scenario productization passed bounded review for machine-readable business output summaries and evidence refs.
```
