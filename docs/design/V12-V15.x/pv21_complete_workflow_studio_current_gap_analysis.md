# PV21 Complete Workflow Studio Current Gap Analysis

用途：说明当前实现与 PV21 目标之间的差距。
阅读对象：产品、架构、开发、测试、审计人员。
边界：本文是 gap 文档，不是实现证据；不得据此声明完整工作流工作台已完成。

## 1. Baseline

| Baseline | What it proves | What it does not prove |
| --- | --- | --- |
| V13 editable Studio pilot | 可编辑 Workflow Studio pilot slice。 | 不证明完整工作流工作台、运行闭环、版本回滚或生产体验。 |
| PV19 runtime workflow platform | 有界 runtime-backed 工作流闭环。 | 不证明完整画布、完整 Studio UX、完整 Agent executor 或生产可用。 |
| PV20 Agent executor bounded review | 受控 skill/tool/MCP fixture、approval、timeout/cancel/retry/redaction path。 | 不证明完整 Studio 集成、产品级 human handoff UX 或 unrestricted automation。 |

## 2. Gap Matrix

| Gap | Current state | PV21 target | Risk | Mitigation |
| --- | --- | --- | --- | --- |
| G-PV21-1 Default entry | 当前入口存在空白/体验割裂风险。 | 默认进入真实 Workflow Studio 工作台。 | High | M1 首先锁定 route、state DTO、首屏截图。 |
| G-PV21-2 Unified canvas | V13/PV19/PV20 页面分散。 | 一个工作台中完成编辑、运行和审查。 | High | 建立 PV21 shell，复用但不复制各阶段能力。 |
| G-PV21-3 Graph roundtrip | Pilot 编辑能力与 runtime graph readback 不完整统一。 | 所有 graph 操作经 BFF 后端 readback。 | High | Graph DTO snapshot 和 roundtrip runner。 |
| G-PV21-4 Validation | 连接规则和参数错误反馈不完整。 | Validation 阻止 publish/run 并定位节点/边。 | Medium | Negative fixtures 覆盖 invalid edge、missing param、unknown type。 |
| G-PV21-5 Version lifecycle | Publish 有基础，rollback/run history 需要补齐。 | 版本列表、比较、发布、回滚和历史可审。 | High | Version report 和 rollback audit refs。 |
| G-PV21-6 Runtime integration | PV19 run 与 Studio 体验仍偏分离。 | Studio 内启动已发布版本并 inspect。 | High | M4 绑定 WorkflowVersion -> WorkflowInstance -> StationRun。 |
| G-PV21-7 Human gate UX | PV19/PV20 有状态证据，但产品 UX 仍弱。 | Studio 内完成 human action 并看到 evidence。 | Medium | Human transition report 和截图。 |
| G-PV21-8 Evidence aggregation | Evidence 分散在阶段报告。 | 同屏聚合 artifact/trace/quality/approval/claim/redaction。 | Medium | Evidence summary DTO 和 claim matrix。 |
| G-PV21-9 Platform generality | 业务场景容易诱导定制。 | 工作流平台保持通用。 | High | Platform generality review 和 business-specific branch scan。 |
| G-PV21-10 UX quality | 长文本、空状态、错误状态、响应式仍需审查。 | 有界审查无 fatal/major UX 问题。 | Medium | Browser screenshots、accessibility/UX checklist。 |

## 3. Development Support Assessment

当前 PV21 文档包完成后，应能支持自动化开发：

- PRD 明确目标体验和红线。
- Target architecture 明确代码实体、分层和 DTO。
- Development plan 明确子阶段和证据。
- Milestone roadmap 明确顺序和出门产物。
- Acceptance gate 明确 PASS/FAIL 标准。
- Task matrix 明确实现任务和验收任务。
- Drawio 明确当前/目标差异、分层关系、计划和验收门槛。

剩余风险不来自文档缺口，而来自后续实现复杂度：前端画布状态、后端版本语义、运行证据聚合和 UX 质量需要逐阶段真实验收。

