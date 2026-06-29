# PV21 Complete Workflow Studio PRD

用途：定义 PV21 阶段的产品目标、用户体验、功能边界和验收口径。
阅读对象：产品、架构、开发、测试、审计人员。
边界：本文是 PV21 开发规格，不是实现证据；不得据此声明完整工作流工作台已完成、生产可用或 Xpert parity。

## 1. Background

HarnessOS 已经具备以下有界基础：

- V13：证明 editable Workflow Studio pilot，可编辑但不是完整工作台。
- PV19：证明 runtime-backed workflow closed loop，可发布、运行、人工交互和审查证据，但 Studio 体验仍是有界闭环页面。
- PV20：证明 governed Agent executor bounded review path，可在受控边界内执行 skill、tool、MCP fixture、approval、timeout、cancel、retry 和 redaction fixtures。

PV21 的任务是把这些基础收敛成一个完整 Workflow Studio 候选体验：用户可以在同一工作台完成工作流设计、校验、差异审查、版本发布、运行、回滚、人工交互和证据审查。PV21 必须保持平台通用性，不能为了某个业务 Pack 定制 workflow core、Gateway core 或 App shell。

## 2. Product Goal

PV21 目标体验：

1. 用户打开默认工作台入口时看到真实 Workflow Studio，而不是空白页或只读摘要页。
2. 用户可通过节点库、画布、连线、Inspector 和参数面板编辑通用工作流。
3. 用户可看到结构化 graph validation、WorkflowDiff、版本比较和发布影响。
4. 用户可发布 WorkflowVersion、运行已发布版本、查看 run history，并在需要时 rollback。
5. 用户可处理至少一个 runtime-backed human gate，并看到状态变化、audit trail 和 evidence summary。
6. 用户可在同一工作台审查 artifact、trace、quality、approval、claim 和 redaction evidence。

允许的阶段出口声明：

```text
PV21 complete Workflow Studio candidate ready for bounded review.
```

该声明只表示“候选能力进入有界审查”，不等于生产可用、Xpert parity、产品级前端完成或商业化完成。

## 3. Target Users

| User | Need | PV21 responsibility |
| --- | --- | --- |
| Workflow builder | 设计、编辑、校验和发布工作流。 | 画布、节点库、Inspector、validation、WorkflowDiff、publish。 |
| Operator / reviewer | 运行、观察、处理人工交互和审查证据。 | run history、inspect、human action、evidence summary。 |
| Platform engineer | 确认平台通用性、边界和回归风险。 | BFF DTO、runtime readback、negative fixtures、No False Green。 |
| Auditor | 判断实现是否支持 PRD 和目标架构。 | claim-to-evidence、route log、redaction、artifact manifest。 |

## 4. Functional Requirements

| ID | Requirement | Acceptance expectation |
| --- | --- | --- |
| PV21-F1 | 默认 Studio 入口非空，并指向 PV21 工作台候选体验。 | Browser E2E 首屏截图包含画布、节点库、Inspector、版本区和运行区。 |
| PV21-F2 | 支持通用节点库、拖放/添加节点、连线和删除。 | Graph DTO readback 与用户操作一致；不得写死业务节点。 |
| PV21-F3 | Inspector 支持节点参数、输入输出、policy、agent/tool/skill/MCP metadata。 | 编辑后可校验并生成 WorkflowDiff。 |
| PV21-F4 | 支持 graph validation 和连接规则错误反馈。 | 负向用例显示明确错误，不生成可发布版本。 |
| PV21-F5 | 支持 WorkflowDiff、版本比较、publish、rollback 和 run history。 | 发布、回滚、历史记录均有后端 readback 和 audit refs。 |
| PV21-F6 | 支持运行已发布 WorkflowVersion。 | Runtime 创建 WorkflowInstance / StationRun，并返回 inspect DTO。 |
| PV21-F7 | 支持 runtime-backed human gate。 | 人工操作改变后端状态，并进入 evidence summary。 |
| PV21-F8 | 支持完整 evidence review。 | Artifact、trace、quality、approval、claim、redaction refs 同屏可审。 |
| PV21-F9 | 浏览器只访问 BFF DTO，不直连 runtime/internal store。 | Browser network log 和 route denylist PASS。 |
| PV21-F10 | 工作台具备可审查 UX 质量。 | 响应式、空状态、错误状态、长文本、键盘焦点无 major 问题。 |

## 5. Scope

### In Scope

- `apps/workflow-console` 的 Workflow Studio 入口、布局和交互候选体验。
- `/bff/pv21/*` DTO read/write facade。
- Workflow graph readback、validation、diff、publish、rollback、run history、inspect 和 evidence summary。
- 与现有 WorkflowInstance、StationRun、AgentExecutionResult、artifact、trace、approval、quality stores 的强关联。
- Browser E2E、backend acceptance runner、claim-to-evidence、No False Green 和 redaction scan。

### Out Of Scope

- 生产多租户 SLA、生产部署、计费、限额和商业化发布。
- 外部 App SDK 契约冻结；该工作属于 PV22。
- 生产治理硬化；该工作属于 PV23。
- 业务 Pack 商业产品化；该工作属于 PV24。
- 任意 unrestricted MCP、自动生产部署、自动 git push 或 Agent 自动审批。

## 6. Experience Flow

1. 打开 `/?studio=pv21-complete-workflow-studio` 或默认 Studio 入口。
2. 选择 workspace/project/app/workflow。
3. 在节点库中添加 Start、Agent、Tool/MCP、Human Gate、Evidence Review 等通用节点。
4. 编辑节点参数和连接规则。
5. 点击 validation，查看错误或 warnings。
6. 查看 WorkflowDiff，确认发布 WorkflowVersion。
7. 从已发布版本发起 run。
8. 在运行区查看 WorkflowInstance / StationRun 状态。
9. 对 human gate 做人工确认或拒绝。
10. 打开 evidence review，检查 artifact、trace、quality、approval、claim、redaction refs。
11. 回滚到旧版本并确认 run history 和 audit trail 保留。

## 7. Red Lines

- 不得为了示例业务定制 workflow core、Gateway core 或 App shell。
- 不得让浏览器绕过 BFF 调用 runtime/internal API。
- 不得让 Agent 节点直接 publish、rollback、approve、git push 或 production deploy。
- 不得把 fixture、截图、介绍页或规划文档当作 runtime evidence。
- 不得删除历史版本、历史 run 或失败证据来制造通过结果。
- 不得做生产可用、Xpert parity、产品级前端完成或完整工作台已完成声明。

## 8. Success Metrics

| Metric | Target |
| --- | --- |
| Studio scenario matrix | PASS for create/edit/validate/diff/publish/run/human/evidence/rollback. |
| Backend acceptance runner | PASS with real DTO readback and runtime state refs. |
| Browser E2E | PASS with screenshots and network route log. |
| PRD spec review | Every PV21-F requirement has evidence or explicit blocker. |
| Platform generality review | No Knowledge/Meeting/Interview/Video-only core branch. |
| No False Green | PASS for forbidden claims and evidence misuse. |
| Redaction scan | PASS for secret/raw prompt/raw provider payload leakage. |

