# Workflow Platform Main Entry PRD

用途：把用户认可的“工作流平台作为 HarnessOS 首入口”目标固化为本阶段产品规格。
阅读对象：产品、架构、开发、测试、审计人员和后续 Agent。
边界：本文是文档开发产物，不是实现证据；不得据此声明工作流平台、完整 Workflow Studio、Agent executor 或生产可用已经完成。

## 1. Product Goal

HarnessOS 的后续产品体验必须从分散的 V13 / PV19 / PV20 / PV21 页面，收敛为一个以工作流平台为首入口的产品表面。

用户打开项目后，应首先看到一个可理解、可操作、可审计的工作流平台：

```text
工作空间
  -> 工作流画布
  -> Agent / Tool / Skill / MCP 资源配置
  -> WorkflowDiff 审查
  -> 发布 / 回滚 / 运行
  -> Human gate
  -> Artifact / Trace / Quality / Audit / Claim evidence
```

该目标继承 PV21 bounded candidate 的已验收能力，但不能把 PV21 误写成 GA、production ready 或 product-grade frontend complete。

## 2. Target Users

| User | Primary need | Must see in the product |
| --- | --- | --- |
| 人类评审者 | 快速判断 HarnessOS 能否作为工作流平台继续开发。 | 首屏工作流平台、画布、节点、运行与证据路径。 |
| 产品/架构审计人员 | 判断 PRD、架构、实现和验收是否一致。 | 当前能力、受限能力、待实现能力和 No-Go 边界。 |
| 后续开发 Agent | 按明确规格继续实现，不再混淆阶段目标。 | 具体代码实体、BFF route、DTO、证据目录和验收命令。 |
| 潜在集成方 | 判断后续外部 App 接入应接到哪里。 | 工作流平台首入口稳定后，再进入 PV22 外部契约实现。 |

## 3. User Experience Target

### 3.1 First Entry

根入口默认进入 Workflow Platform，而不是空白页面、单独原型页面或分散阶段页面。

首屏必须让用户在 60 秒内识别：

- 当前 workspace / project。
- 当前工作流图是否可编辑、可运行或处于受限审查状态。
- 画布中有哪些节点、连接和状态。
- Agent / Tool / Skill / MCP 资源在哪里配置。
- 运行、证据、审计和人工确认在哪里查看。
- 哪些能力当前不可用，以及原因。

### 3.2 Workflow Canvas Experience

目标体验不是静态截图，而是可操作画布：

- 支持滚轮缩放、平移、节点拖拽。
- 支持节点选择、Inspector 联动和状态反馈。
- 支持可见端口、自由连线、取消连线和连接规则提示。
- 支持首眼布局正确：连线不穿过关键文本，箭头清晰可见，节点不落在不可拖动区域。
- 支持失败、禁用、待人工确认、已完成等状态的可见反馈。

### 3.3 Runtime And Evidence Experience

用户必须能够理解一次工作流从设计到运行的闭环：

- 画布编辑产生 WorkflowSpecGraph。
- WorkflowDiff 必须经过人工确认。
- 发布后生成 WorkflowVersion。
- 运行产生 WorkflowInstance / StationRun。
- Human gate 必须显示人工操作来源和结果。
- Evidence panel 汇总 artifact、trace、quality、audit、claim、redaction refs。

### 3.4 Minimum Target User Journey

本阶段后续实现的最小目标用户路径是：

1. 用户打开 HarnessOS，默认进入工作流平台。
2. 用户在画布上看到基础 Agent 工作流。
3. 用户拖拽画布、缩放画布、拖动节点调整布局。
4. 用户从节点端口拖出连线，连接成基础 Agent 工作流。
5. 用户选择节点，在 Inspector 中配置 Agent 角色、目标、Tool/Skill/MCP 和审批策略。
6. 用户保存草稿，系统通过 BFF 保存 WorkflowSpecGraph。
7. 用户校验图，看到连接规则和缺失参数反馈。
8. 用户生成 WorkflowDiff，并人工审查变更。
9. 用户确认后发布 WorkflowVersion。
10. 用户运行已发布工作流，产生 WorkflowInstance / StationRun。
11. 用户在 Human Gate 中审批通过或拒绝。
12. 用户打开 Evidence Review，审查产物、trace、quality、audit、claim 和 redaction refs。

WP-M3 出门验收必须覆盖该路径。若只能展示静态画布或只展示运行结果，不能作为工作流平台 MVP 候选体验通过。

### 3.5 Target Application Scenarios

| Scenario | User goal | Platform use | Exit expectation | Boundary |
| --- | --- | --- | --- | --- |
| 基础 Agent 工作流 | 用画布编排一个可运行的 Agent 工作流。 | 拖拽节点、自由连线、配置 Agent/Tool/Skill/MCP、Diff、发布、运行、人工审查。 | 形成可审查的 WorkflowInstance、StationRun 和 evidence refs。 | WP-M3 required。 |
| 文档/知识总结 | 总结一组文档并保留证据。 | 文件/文档输入、解析、事实抽取、总结、质量检查、证据审查。 | 带 evidence refs 的摘要产物和人工复核记录。 | Required business scenario。 |
| 代码审查 | 审查 Git diff 或代码包。 | 静态检查、安全审计、汇总报告、合规 Human Gate。 | 代码审查报告、风险列表和审批记录。 | Required business scenario；不替代生产 CI 安全审计。 |
| 会议/访谈整理 | 从 transcript 生成纪要和行动项。 | 议题提取、行动项整理、事实核对、人工复核。 | 会议纪要、行动项和引用证据。 | Required business scenario；真实音频 ASR 另按 Meeting pack 验收。 |
| 创意分镜规划 | 从脚本生成分镜规划。 | 导演/艺术/摄影 Agent 协作，版权/合规 gate。 | Storyboard spec 和审查记录。 | 不声明真实视频渲染完成。 |
| 外部工具/MCP 自动化 | 在受治理边界内调用工具或 MCP。 | allowlisted Tool/MCP、approval/denial、audit refs。 | Tool/MCP execution refs 和 evidence。 | 不声明 unrestricted automation。 |

## 4. Current Capability Classification

| Category | Capability | Current evidence / limitation |
| --- | --- | --- |
| 已验收 | PV21 bounded candidate default Studio entry, graph save/validate/diff, publish/rollback, runtime run, human gate, evidence review。 | `evidence/pv21-complete-workflow-studio/`，但不是 GA。 |
| 已验收 | PV20 bounded Agent executor review path through S6。 | 证明受控执行路径，不证明 unrestricted automation。 |
| 已验收 | PV19 runtime workflow platform closed loop。 | 证明有界 runtime-backed workflow loop。 |
| 受限完成 | 首入口已偏向 PV21，但产品定位仍未在文档中统一为 Workflow Platform。 | 需要 WP-M0 文档门禁和后续实现验收。 |
| 受限完成 | 画布交互已有多轮优化，但仍需以 PRD 规格重新固化验收项。 | 需要滚轮缩放、拖拽区域、自由连线、取消连线、箭头可见性专项验收。 |
| 规划中 | PV22 external app contract implementation。 | PV22-R0 文档/readiness 已有，implementation evidence 尚未生成。 |
| No-Go | 声明 production ready / product-grade frontend complete / complete Workflow Studio ready / Agent executor ready / Xpert parity complete。 | 禁止。 |

## 5. Functional Requirements

| ID | Requirement | Acceptance signal |
| --- | --- | --- |
| WP-FR-1 | 根入口和主要导航必须以 Workflow Platform 为主体验。 | 首屏截图和 route assertion 证明默认进入平台工作台。 |
| WP-FR-2 | 画布必须支持缩放、平移、节点拖拽、选择和 Inspector 联动。 | Browser E2E action log、截图和 DOM assertions。 |
| WP-FR-3 | 连线必须支持从端口发起、自由连接到合法目标、取消连接和错误提示。 | Edge interaction E2E 和连接规则负向用例。 |
| WP-FR-4 | WorkflowDiff、publish、rollback、run、human gate 必须在同一产品表面可理解。 | BFF route log、DTO snapshots、runtime inspect report。 |
| WP-FR-5 | Evidence panel 必须区分 artifact、trace、quality、audit、claim、redaction。 | Evidence DTO snapshot 和 human-readable acceptance report。 |
| WP-FR-6 | Agent/Tool/Skill/MCP 能力必须以受治理资源显示，不能暗示 unrestricted automation。 | UI copy scan 和 No False Green scan。 |
| WP-FR-7 | PV22 外部接入必须以后续工作流平台为接入目标，不再作为孤立页面目标。 | PV22 文档引用 WP-M0 platform entry boundary。 |

## 6. Non-Functional Requirements

- UI 文案使用简体中文。
- 代码注释、变量名和 commit message 使用英文。
- Browser 不得直接调用 internal runtime/store routes。
- 所有正向完成声明必须绑定 evidence path。
- 任何截图、drawio、介绍页、设计稿只能作为文档或 UX review evidence，不能替代 runtime/BFF/browser E2E evidence。
- 后续实现必须优先复用现有 `apps/workflow-console`、`apps/api/routers/bff.py`、`core/workflows/store.py` 和已验收 PV19/PV20/PV21 DTO 边界。

## 7. Out Of Scope

- 不在本阶段实现新业务代码。
- 不在本阶段声明 PV22 implementation complete。
- 不在本阶段声明 production ready。
- 不在本阶段声明 complete Workflow Studio GA。
- 不在本阶段声明 Agent executor ready。
- 不在本阶段实现完整外部 marketplace、商业计费或生产部署。

## 8. Allowed Claim After This Document Stage

仅允许声明：

```text
Workflow Platform main-entry documentation is ready for implementation review.
```

不得声明：

```text
Workflow Platform implementation complete.
Complete Workflow Studio ready.
Product-grade frontend complete.
Agent executor ready.
Production ready.
Xpert parity complete.
```
