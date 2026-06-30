# Workflow Platform Main Entry PRD

用途：把用户确认的“PV13 前端页面直接作为 HarnessOS 工作流平台首页和后续前端基线”固化为本阶段产品规格。
阅读对象：产品、架构、开发、测试、审计人员和后续 Agent。
边界：本文是文档开发产物，不是实现证据；不得据此声明首页替换、运行闭环、完整 Workflow Studio、Agent executor 或生产可用已经完成。

## 1. Product Goal

HarnessOS 的后续前端体验必须以 PV13 Light Studio 工作流平台为首页基线。

本阶段“PV13 前端页面”具体指：

| Item | Concrete source |
| --- | --- |
| 页面组件 | `apps/workflow-console/src/ui/v13/V13EditableStudio.tsx` |
| 页面样式 | `apps/workflow-console/src/ui/v13/v13-editable-studio.css` |
| 当前路由 | `?studio=v13-editable-studio` |
| 目标首页路由 | 无 query 根入口与 `?studio=workflow-platform` 均呈现 PV13 基线体验 |
| 外部原型参考 | `C:\Users\Administrator\Downloads\harnessos_v13_prototype*.html` |

后续实现不应继续在退化版 `WorkflowPlatformMainEntry` 上扩展工作流平台首页。该实现只能作为当前偏差记录，后续应被 PV13 基线替换或降级为历史参考。

同时，`WorkflowPlatformMainEntry` 当前已经承载的 PV21/PV20 闭环能力不能因为首页视觉基线切回 PV13 而丢失。正确路线是：

```text
PV13 = 首页视觉和画布交互基线
WorkflowPlatformMainEntry = 已接入能力的迁移来源和不退化对照
PV21/PV20/PV19 route families = 运行、执行器和证据能力来源
```

## 2. Target Users

| User | Primary need | Must see in product |
| --- | --- | --- |
| 人类评审者 | 快速体验 HarnessOS 是否像一个工作流平台。 | PV13 Light Studio 首页、力感画布、场景列表、节点、连线、Inspector、仿真控制。 |
| 产品/架构审计人员 | 判断 PRD、架构、实现和验收是否一致。 | 明确的 PV13 基线、当前偏差、待集成 PV19/PV20/PV21 能力和 No-Go 边界。 |
| 后续开发 Agent | 按明确代码实体继续开发。 | `App.tsx -> WorkflowStudioLayout.tsx -> V13EditableStudio.tsx` 的默认入口路径。 |
| 潜在集成方 | 判断后续外部 App 应接入哪里。 | 稳定的 Workflow Platform host surface；PV22 只能在该 surface 稳定后继续。 |

## 3. User Experience Target

### 3.1 First Entry

用户打开 HarnessOS 默认看到 PV13 工作流平台，而不是：

- 空白页。
- 当前退化版 `WorkflowPlatformMainEntry`。
- 分散的 PV19/PV20/PV21 阶段页。
- 只用于验收的静态原型页。

首屏必须在 60 秒内让用户识别：

- HarnessOS Light Studio 品牌和 workspace。
- 左侧工作流平台场景导航。
- 中央力感画布、节点、端口、连线和 minimap。
- 顶部仿真控制、缩放按钮和状态 chip。
- 右侧 Agent Profile / Inspector / 工具 / 技能 / MCP / 质量门槛。
- 底部 workspace、timeline、trace、quality、evidence 审查区域。

### 3.2 Workflow Canvas Experience

PV13 基线目标不是静态截图，而是可操作工作台：

- 支持滚轮缩放、平移、节点拖拽。
- 支持节点选择、Inspector 联动和状态反馈。
- 支持从端口发起连线、自由连接合法目标、取消连线和非法连接提示。
- 支持首眼布局正确：连线不穿过关键文本，箭头清晰可见，节点不落在不可拖动区域。
- 支持仿真态、待人工、已完成、阻断等状态的可见反馈。

### 3.3 Runtime And Evidence Experience

PV13 基线本身负责首页、画布和 WorkflowDiff pilot 体验。后续 WP-M3 必须把已验收能力融合到该基线中：

- PV19 提供 publish / run / human gate / evidence loop 的 bounded runtime 来源。
- PV20 提供 governed Agent / Tool / Skill / MCP executor evidence 来源。
- PV21 提供 graph save / validate / diff / publish / rollback / run / evidence 的 bounded candidate 来源。

这些能力必须集成进 PV13 基线工作台，而不是把 PV19/PV20/PV21 阶段页提升为新的首页视觉基线。

### 3.4 Function Non-Regression Target

直接用 PV13 页面覆盖当前工作流平台入口只能作为 WP-M1B 首页体验修正，不等于工作流平台能力完成。WP-M3/WP-M4 必须证明以下能力没有相对 `WorkflowPlatformMainEntry` 退化：

| Capability group | Current capability source | Target PV13-based behavior | Non-regression evidence |
| --- | --- | --- | --- |
| Graph draft | `WorkflowPlatformMainEntry` + PV21 graph routes | 用户在 PV13 工作台保存、读取和校验 WorkflowSpecGraph。 | graph save/readback DTO、validation report、browser action log。 |
| WorkflowDiff | `WorkflowPlatformMainEntry` + PV21 diff routes + PV13 diff pilot | 用户在 PV13 工作台查看、拒绝、修订或确认 Diff，不自动发布。 | diff DTO、human confirmation log、No auto-publish assertion。 |
| Version lifecycle | `WorkflowPlatformMainEntry` + PV21 version routes | 用户在 PV13 工作台发布、回滚并回读 active version。 | version lifecycle report、audit refs、route log。 |
| Runtime run | `WorkflowPlatformMainEntry` + PV21/PV19 run routes | 用户在 PV13 工作台运行已发布工作流并回读 WorkflowInstance / StationRun。 | runtime inspect report、StationRun DTO、artifact refs。 |
| Human gate | `WorkflowPlatformMainEntry` + PV21 human action route | 用户在 PV13 工作台进行人工确认/拒绝并看到后端状态变化。 | before/after state digest、human action report。 |
| Evidence review | `WorkflowPlatformMainEntry` + PV21 evidence route | 用户在 PV13 工作台查看 artifact、trace、quality、audit、claim、redaction 分类证据。 | evidence panel report、screenshot、DTO snapshot。 |
| Governed executor | `WorkflowPlatformMainEntry` + PV20 executor routes | 用户在 PV13 工作台以受治理方式触发 Skill/Tool/MCP，并能看到 approval/denial/evidence refs。 | executor integration report、approval/denial fixtures、redaction scan。 |

若 WP-M3/WP-M4 的实现只保留 PV13 外观、但丢失上述任一能力，验收必须标记为 `FAIL`，并回到开发计划阶段重新设计。

### 3.5 Minimum Target User Journey

本阶段后续实现的最小目标用户路径是：

1. 用户打开 HarnessOS，默认进入 PV13 Light Studio 工作流平台。
2. 用户选择“罗马广场讨论工作流”或其他工作流场景。
3. 用户在力感画布上看到基础 Agent 工作流节点和连接。
4. 用户滚轮缩放、拖动画布、拖动节点调整布局。
5. 用户从节点端口拖出连线，连接成基础 Agent 工作流，并可取消连线。
6. 用户选择节点，在 Inspector 中查看或配置 Agent 角色、目标、Tool/Skill/MCP 和质量门槛。
7. 用户保存草稿，系统通过 BFF 保存 WorkflowSpecGraph。
8. 用户校验图，看到连接规则和缺失参数反馈。
9. 用户生成 WorkflowDiff，并人工审查变更。
10. 用户确认后发布 WorkflowVersion。
11. 用户运行已发布工作流，产生 WorkflowInstance / StationRun。
12. 用户在 Human Gate 中审批通过或拒绝。
13. 用户打开 Evidence Review，审查 artifact、trace、quality、audit、claim 和 redaction refs。

WP-M1 至少证明 1-6。WP-M3 才能要求 7-13 完整闭环。

### 3.6 Target Application Scenarios

| Scenario | User goal | Platform use | Exit expectation | Boundary |
| --- | --- | --- | --- | --- |
| 基础 Agent 工作流 | 用 PV13 画布编排可审查的 Agent 工作流。 | 场景选择、节点拖拽、自由连线、Inspector、Diff、发布、运行、人工审查。 | WorkflowInstance、StationRun、工作流产物和 evidence refs。 | WP-M3 required。 |
| 文档/知识总结 | 总结一组文档并保留证据。 | 文件/文档输入、解析、事实抽取、总结、质量检查、证据审查。 | 带 evidence refs 的摘要产物和人工复核记录。 | Required business scenario。 |
| 代码审查 | 审查 Git diff 或代码包。 | 静态检查、安全审计、汇总报告、合规 Human Gate。 | 代码审查报告、风险列表和审批记录。 | Required business scenario；不替代生产 CI 安全审计。 |
| 会议/访谈整理 | 从 transcript 生成纪要和行动项。 | 议题提取、行动项整理、事实核对、人工复核。 | 会议纪要、行动项和引用证据。 | Required business scenario；真实音频 ASR 另按 Meeting pack 验收。 |
| 创意分镜规划 | 从脚本生成分镜规划。 | 导演/艺术/摄影 Agent 协作，版权/合规 gate。 | Storyboard spec 和审查记录。 | 不声明真实视频渲染完成。 |
| 外部工具/MCP 自动化 | 在受治理边界内调用工具或 MCP。 | allowlisted Tool/MCP、approval/denial、audit refs。 | Tool/MCP execution refs 和 evidence。 | 不声明 unrestricted automation。 |

## 4. Current Capability Classification

| Category | Capability | Current evidence / limitation |
| --- | --- | --- |
| 已验收 | V13 editable Studio pilot / PV13 Light Studio 前端基线。 | `apps/workflow-console/src/ui/v13/*` 和 `evidence/v13-workflow-studio-pilot/`，但不是 product-grade frontend complete；历史 `/bff/v13/*` 证据来自 bounded acceptance smoke server，后续 WP-M1A 需确认主 BFF compatibility。 |
| 已验收 | PV19 runtime workflow platform closed loop。 | 证明有界 runtime-backed workflow loop，可作为 WP-M3 集成来源。 |
| 已验收 | PV20 bounded Agent executor review path through S6。 | 证明受控执行路径，可作为 WP-M4 集成来源。 |
| 已验收 | PV21 bounded candidate default Studio entry。 | 可作为运行/证据能力参考，不再作为首页视觉基线。 |
| 需替换 | 当前 `WorkflowPlatformMainEntry` 退化版入口。 | 首屏和交互体验不符合用户已确认的 PV13 基线。 |
| 规划中 | PV22 external app contract implementation。 | PV22-R0 文档/readiness 已有，implementation evidence 尚未生成。 |
| No-Go | 声明 production ready / product-grade frontend complete / complete Workflow Studio ready / Agent executor ready / Xpert parity complete。 | 禁止。 |

## 5. Functional Requirements

| ID | Requirement | Acceptance signal |
| --- | --- | --- |
| WP-FR-1 | 根入口和 `?studio=workflow-platform` 必须呈现 PV13 Light Studio 工作流平台体验。 | 首屏截图、route assertion 和 DOM assertion 证明 `v13-editable-studio` 可见。 |
| WP-FR-2 | `?studio=v13-editable-studio` 必须继续可访问，作为基线回放路由。 | Backward compatibility smoke PASS。 |
| WP-FR-3 | 当前 `WorkflowPlatformMainEntry` 不得继续作为目标首页体验。 | 架构审计和 route mapping 检查 PASS。 |
| WP-FR-4 | `/bff/v13/*` compatibility route 来源必须明确，不能把 smoke-server-only evidence 写成主 BFF/runtime 完成。 | WP-M1A route ownership report 和 route smoke PASS。 |
| WP-FR-5 | 画布必须支持缩放、平移、节点拖拽、选择、Inspector 联动、自由连线和取消连线。 | Browser E2E action log、截图和 DOM assertions。 |
| WP-FR-6 | WorkflowDiff、publish、rollback、run、human gate 必须后续在 PV13 基线工作台中可理解。 | BFF route log、DTO snapshots、runtime inspect report。 |
| WP-FR-7 | Evidence panel 必须区分 artifact、trace、quality、audit、claim、redaction。 | Evidence DTO snapshot 和 human-readable acceptance report。 |
| WP-FR-8 | Agent/Tool/Skill/MCP 能力必须以受治理资源显示，不能暗示 unrestricted automation。 | UI copy scan 和 No False Green scan。 |
| WP-FR-9 | PV22 外部接入必须以后续稳定的 PV13 基线工作流平台为目标 host surface。 | PV22 文档引用 WP-M0 platform entry boundary。 |
| WP-FR-10 | WP-M3/WP-M4 必须证明相对 `WorkflowPlatformMainEntry` 的 PV21/PV20 闭环能力不退化。 | `workflow-platform-capability-parity-report.json` PASS。 |

## 6. Non-Functional Requirements

- UI 文案使用简体中文。
- 代码注释、变量名和 commit message 使用英文。
- Browser 不得直接调用 internal runtime/store routes。
- 所有正向完成声明必须绑定 evidence path。
- 任何截图、drawio、介绍页、设计稿只能作为文档或 UX review evidence，不能替代 runtime/BFF/browser E2E evidence。
- 后续实现必须优先复用 `V13EditableStudio.tsx` 和 `v13-editable-studio.css`，再集成 PV19/PV20/PV21 的 BFF/DTO 能力。

## 7. Out Of Scope

- 不在本文档阶段修改前端代码。
- 不在本文档阶段声明首页替换已经完成。
- 不在本文档阶段声明 PV22 implementation complete。
- 不在本文档阶段声明 production ready。
- 不在本文档阶段声明 complete Workflow Studio GA。
- 不在本文档阶段声明 Agent executor ready。
- 不在本文档阶段实现完整外部 marketplace、商业计费或生产部署。

## 8. Allowed Claim After This Document Stage

仅允许声明：

```text
Workflow Platform main-entry documentation is aligned to the PV13 frontend baseline and ready for implementation review.
```

不得声明：

```text
Workflow Platform implementation complete.
PV13 homepage replacement complete.
Complete Workflow Studio ready.
Product-grade frontend complete.
Agent executor ready.
Production ready.
Xpert parity complete.
```
