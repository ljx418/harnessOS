# Workflow Platform Main Entry Acceptance Gate

用途：定义工作流平台首入口文档阶段和后续实现阶段的验收门槛。
边界：本文不是实现证据。

## 1. WP-M0 Document Gate

| Gate | PASS condition | FAIL condition |
| --- | --- | --- |
| Document completeness | PRD、架构、计划、里程碑、验收、gap、任务矩阵、审计、drawio 全部存在。 | 任一必需文档缺失。 |
| Contract completeness | BFF/DTO contract、acceptance runner spec、implementation readiness audit 全部存在。 | 缺少 route allowlist、DTO snapshot 或 runner output 规格。 |
| Naming consistency | 统一使用 WP-M0/WP-M1... 表示首入口对齐；PV19-22 保持历史阶段含义。 | 把 WP-M0 写成 PV22 implementation 或把 PV21 写成 GA。 |
| Drawio quality | 不超过 8 页，中文，颜色语义一致，具体代码实体清晰。 | 文本溢出、重复冲突、含糊模块名、架构关系不清。 |
| Architecture specificity | 出现真实代码实体、BFF routes、DTO、store、runtime/evidence artifacts。 | 只出现抽象概念，无法指导实现。 |
| Claim safety | forbidden claims 未出现。 | 出现 production ready、complete Studio ready、Agent executor ready 等误报。 |

## 2. WP-M1 First Entry Gate

- 根入口默认工作流平台。
- 首屏明确 workspace/project/state。
- 入口不依赖用户手动输入阶段 query。
- Browser network log 只出现允许 BFF routes。
- DTO snapshot 必须符合 `workflow_platform.main_entry.v1` 或现有 PV21/PV20 DTO 组合形态。
- 中文验收报告含首屏截图。

## 3. WP-M2 Canvas Interaction Gate

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

## 5. WP-M4 Executor Integration Gate

- Agent/Tool/Skill/MCP 入口只展示受治理能力。
- Approval denial、timeout、cancel、retry、redaction fixtures 可回读。
- UI 不暗示 unrestricted automation。
- Evidence ref 能追踪到 PV20 bounded executor path 或后续真实执行证据。

## 6. Target User Scenario Exit Gate

工作流平台出门验收不能只证明“用户能看到画布、运行和证据”。验收报告必须证明用户能用平台完成具体工作。

### 6.1 Required Minimum Scenario

| Scenario | User input | Required platform actions | Human review point | Required output | Exit evidence |
| --- | --- | --- | --- | --- | --- |
| 基础 Agent 工作流 | 一个工作目标，例如“总结一组文档并审查证据”。 | 打开平台、拖拽/调整节点、连接节点、配置 Agent/Tool/Skill/MCP、保存草稿、校验图、生成 WorkflowDiff、发布版本、运行工作流。 | WorkflowDiff 确认和 Human Gate 审批。 | WorkflowInstance、StationRun、工作流产物、Evidence panel。 | 画布截图、edge action log、BFF route log、DTO snapshot、runtime inspect、human action report、evidence panel report。 |

该场景是 WP-M3 出门的最低条件。若不能完成，不得声明工作流平台 MVP 候选体验 ready for bounded review。

### 6.2 Required Business Scenarios

WP-M3 出门前必须跑通以下三个业务场景；WP-M4 出门前必须证明三个场景对应的 Agent/Tool/Skill/MCP 入口均是受治理能力。

| Scenario | How the user uses HarnessOS | Platform workflow | Acceptance output | Boundary |
| --- | --- | --- | --- | --- |
| 文档/知识总结 | 用户导入文档、Markdown 文件夹或知识材料，要求系统总结并保留证据。 | 输入节点 -> 解析节点 -> 事实抽取 Agent -> 总结 Agent -> 质量检查 -> 证据审查。 | 带 evidence refs 的摘要产物、质量结果、人工审查记录。 | 必验业务场景。 |
| 代码审查 | 用户输入 Git diff、PR patch 或代码包，要求系统生成审查报告。 | 输入节点 -> 静态检查 Agent -> 安全审计 Agent -> 汇总 Agent -> 合规 Human Gate。 | 代码审查报告、风险列表、人工合规审批记录。 | 必验业务场景，不能替代 CI 生产安全审计。 |
| 会议/访谈整理 | 用户输入 transcript 或 audio-derived text，要求生成纪要和行动项。 | 输入节点 -> 议题提取 Agent -> 行动项 Agent -> 事实核对 -> 人工复核。 | 会议纪要、行动项、引用证据和复核记录。 | 必验业务场景；真实音频 ASR 仍按 Meeting pack / connector 证据单独验收。 |

### 6.3 Optional / Future Application Scenarios

以下场景可以展示平台应用前景，但不得作为本阶段已经完成的核心出门声明，除非后续生成独立实现证据。

| Scenario | How the user would use HarnessOS | Output | No-Go boundary |
| --- | --- | --- | --- |
| 创意分镜规划 | 输入脚本，编排导演/艺术/摄影/版权审查 Agent，生成 storyboard spec。 | 分镜规划 JSON、审查记录、版权/合规 gate。 | 不声明真实视频渲染完成。 |
| 外部工具/MCP 受治理自动化 | 绑定 allowlisted Tool/MCP，运行受控节点并审查 approval/denial。 | Tool/MCP execution refs、audit refs、denial fixtures。 | 不声明 unrestricted automation 或 Agent executor ready。 |
| 外部 App 接入 | 外部应用通过 SDK/BFF template/reference app 接入工作流平台。 | SDK smoke、template smoke、reference app E2E。 | PV22 implementation evidence 生成前不得声明完成。 |

### 6.4 Scenario Exit Rule

- WP-M3 PASS requires the minimum Agent workflow scenario and all three required business scenarios.
- WP-M4 PASS requires governed Agent/Tool/Skill/MCP evidence for all three required business scenarios.
- Each scenario must include screenshots, BFF route log, DTO snapshot, runtime/evidence refs, PRD review and No False Green scan.
- If a scenario is presented only as future applicability, the acceptance report must label it as `规划中` or `后续扩展`.

## 7. Forbidden Positive Claims

以下文本或等价中文不得出现在验收通过声明中：

- `production ready`
- `product-grade frontend complete`
- `complete Workflow Studio ready`
- `Workflow Studio GA`
- `Agent executor ready`
- `unrestricted automation`
- `Xpert parity complete`
- `PV22 implementation complete`，除非后续真实实现证据已生成
- `real video rendering complete`，除非后续 Video Studio 真实渲染证据已生成

## 8. Allowed Claims

WP-M0 完成后仅允许：

```text
Workflow Platform main-entry documentation gate passed for implementation review.
```

WP-M1+ 后续实现必须按实际证据逐阶段声明 bounded review ready。
