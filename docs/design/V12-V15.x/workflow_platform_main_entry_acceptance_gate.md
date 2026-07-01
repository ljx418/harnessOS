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

## 10. WP-M6 Frontend Data-Driven Closure Gate

- PV13 正常路径的场景列表、节点、连线、Inspector、timeline、quality、evidence、chat 初始上下文必须来自 BFF/DTO 或 artifact refs。
- `scenarioData`、`fallbackGraph`、静态 timeline、静态 Inspector、proposal-only chat 只能作为显式 fallback / fixture / design reference。
- Browser network log 必须证明正常路径只使用允许 BFF routes。
- `frontend-data-source-closure-report.json` 必须逐页面区域列出数据来源和 fallback 条件。
- `mock-reduction-report.normal_path_static_sources` 必须为 `0`。
- FAIL：正常路径仍从前端静态矩阵读取业务事实。
- FAIL：报告没有区分真实 DTO 数据和离线 fallback。

## 11. WP-M7 WorkflowSpecGraph Edit/Save/Readback Gate

- 用户可以在 PV13 画布拖动节点、增加合法连线、取消/删除连线、更新节点配置。
- 保存草稿必须通过 BFF DTO route，不得直接写 WorkflowStore 或 Gateway internals。
- 刷新页面后必须能回读同一 WorkflowSpecGraph。
- WorkflowDiff 必须基于后端保存状态生成，且需要人工审查。
- `graph-edit-save-readback-report.json` 必须包含 before/after graph DTO、browser action log、route log 和截图。
- FAIL：只有本地状态变化，没有 BFF 保存和刷新回读。
- FAIL：WorkflowDiff 来自静态 fixture，却被写成保存状态差异。

## 12. WP-M8 Publish/Run/Human/Evidence Gate

- 用户可以在 PV13 工作台内发布 WorkflowVersion。
- 用户可以运行已发布工作流并回读 WorkflowInstance / StationRun。
- 用户可以在 Human Gate 中 approve 或 reject，并看到后端状态变化。
- 用户可以打开 Evidence Review，查看 artifact、trace、quality、audit、claim、redaction refs。
- `workflow-inline-runtime-report.json` 必须证明 publish/run/human/evidence 是同一 PV13 工作台内连续路径。
- FAIL：通过分散 PV19/PV21 页面完成，却声明 PV13 工作台内闭环。
- FAIL：UI 构造运行结果但没有 BFF/DTO readback。

## 13. WP-M9 Business Artifact Closure Gate

- 文档总结、代码审查、会议整理必须各有真实输入、input hash、产物文件或机器可读产物内容。
- 每个产物必须绑定 artifact refs、trace refs、quality refs、audit refs、claim refs、redaction refs 和 human review refs。
- HTML 报告必须展示每个业务场景的用户操作路径：输入 -> 编排 -> 运行 -> 人工审查 -> 输出产物 -> 证据链。
- `business-artifact-manifest.json` 必须逐产物列出路径、摘要、hash、证据 refs 和审查结论。
- FAIL：只有摘要卡片、验收报告摘录或截图，没有可审查产物内容。
- FAIL：把应用前景或规划中场景写成已验收业务产物。

## 14. WP-M10 Frontend Quality And Failure-State Gate

- 加载、空状态、错误、权限拒绝、BFF 离线、校验失败、人工拒绝、取消/重试必须有 UI 状态和截图证据。
- 键盘操作、焦点可见性、核心按钮状态、响应式断点和文本不溢出必须通过检查。
- 可访问性扫描和性能预算必须有报告；无法自动化的项目必须有人工审计说明和风险等级。
- `frontend-quality-failure-state-report.json` 必须列出每个状态的触发方式、预期 UI、截图、断言和结果。
- FAIL：happy path 通过但关键失败态不可见。
- FAIL：文本溢出、按钮不可操作、焦点丢失或移动端遮挡影响核心路径。

## 15. WP-M11 Aggregate Frontend Completion Gate

- WP-FR-1 到 WP-FR-20 必须全部有 evidence path；缺证项标记为 `BLOCKED`。
- WP-M6 到 WP-M10 的 artifact manifest 必须存在并能互相引用。
- PRD、目标架构、开发计划、验收门槛、gap 和 drawio 必须同步更新。
- No False Green scan 必须覆盖 Markdown、HTML 报告、UI copy 和 JSON evidence。
- 聚合报告必须使用中文 HTML，包含目标架构、当前架构、用户场景截图、证据索引、残留风险和后置阶段。
- 仅允许声明 `PRD-defined frontend functionality complete for bounded review`。
- FAIL：把 WP-M11 写成 production ready、product-grade frontend complete、complete Workflow Studio ready 或最终商业产品完成。
- FAIL：缺少任一 WP-M6 到 WP-M10 证据包，却给出绿色结论。
