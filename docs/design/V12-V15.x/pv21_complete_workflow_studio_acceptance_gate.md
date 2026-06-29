# PV21 Complete Workflow Studio Acceptance Gate

用途：定义 PV21 阶段的验收门槛、出门条件和阻断条件。
阅读对象：测试、审计、产品、架构、开发人员。
边界：本文是验收规格，不是验收结果；不得据此声明完整工作流工作台已完成。

## 1. Gate Matrix

| Gate | Required result | Evidence |
| --- | --- | --- |
| G1 Entry and UX | 默认 Studio 入口非空，展示工作台骨架、画布、节点库、Inspector、版本、运行和 evidence 区。 | Browser screenshot、UX review。 |
| G2 BFF boundary | Browser 只调用 `/bff/pv21/*` 和允许的静态资源。 | Browser network log、route denylist。 |
| G3 Graph authoring | 节点和连线增删改能被后端 draft graph readback。 | Graph roundtrip report、DTO snapshot。 |
| G4 Validation | 无效节点、无效边、缺失参数会阻止 publish/run。 | Validation report、negative fixtures。 |
| G5 Diff and publish | WorkflowDiff 可审查，publish 创建 WorkflowVersion 和 audit refs。 | Diff report、version publish report。 |
| G6 Rollback | 回滚保留历史和 audit refs，不删除旧 run/evidence。 | Rollback report、audit refs。 |
| G7 Runtime run | 运行已发布版本创建 WorkflowInstance / StationRun。 | Runtime run inspect report。 |
| G8 Human interaction | Human gate 由用户操作改变后端状态。 | Human action transition report。 |
| G9 Evidence | Artifact、trace、quality、approval、claim、redaction refs 可审查。 | Evidence summary report。 |
| G10 Platform generality | 没有业务 Pack 专用 core/Gateway/App shell 分支。 | Platform generality review、code scan。 |
| G11 No False Green | 禁止声明和证据误用扫描通过。 | No False Green scan。 |
| G12 Redaction | raw prompt、secret、raw provider payload 不泄露。 | Redaction scan。 |

## 2. Exit Conditions

PV21 可进入有界审查候选状态，必须同时满足：

- G1-G12 全部 PASS。
- PRD PV21-F1 到 PV21-F10 均有证据或明确非阻塞说明。
- 目标架构中的 Browser、BFF、Gateway、Workflow truth、Agent executor、Evidence 关系均有实现或 readback 证据。
- 浏览器截图能展示真实用户路径，不是静态介绍页或 mock-only 页面。
- aggregate acceptance report 与 artifact manifest 可追踪。

## 3. Hard Blockers

- 默认入口空白或无法解释用户工作路径。
- 只有 UI mock，没有 BFF/Runtime readback。
- 运行路径绕过 WorkflowVersion。
- human gate 状态由前端模拟。
- 证据审查缺失 claim-to-evidence 或 redaction。
- 业务定制污染平台核心。
- 自动化验收失败后仍写 PASS。
- 文档或 UI 宣称生产可用、Xpert parity、产品级前端完成或完整工作台已完成。

## 4. Human Review Criteria

人工审查需要判断：

- 目标体验是否像一个工作流平台，而不是单一业务表单。
- 用户是否能理解从设计到运行到审查的完整路径。
- 错误提示是否足够具体，能指导修复 graph。
- 版本、运行和证据是否互相强关联。
- 出口声明是否保持有界，不越过 PV22/PV23/PV24/PV25。

