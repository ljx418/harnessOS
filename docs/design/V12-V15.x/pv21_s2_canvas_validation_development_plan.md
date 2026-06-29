# PV21-S2 Canvas Inspector Validation Development Plan

用途：定义 PV21-S2 的开发、验收和审计闭环。
阅读对象：开发、测试、产品、审计人员。
边界：本文是子阶段计划，不是实现证据。

## Scope

PV21-S2 完成 graph GET/PUT、Inspector 参数编辑和 validation。发布、运行、人工交互和证据汇总仍由后续子阶段完成。

## Development Tasks

- 后端新增 graph GET/PUT 和 validate routes。
- PUT graph 必须写入 backend draft graph，并返回 updated draft revision。
- Validation 必须覆盖 empty graph、unknown node type、invalid edge、missing required parameter、missing human gate。
- 前端支持基础节点选择、Inspector 参数编辑和保存 draft。

## Acceptance

- Graph roundtrip report PASS：前端或测试提交的 graph 被后端 readback。
- 负向 fixtures PASS：invalid edge、unknown node type、missing parameter 均阻止 publish readiness。
- No business-specific core branch。

## Audit Opinion

Go. 主要风险是只改前端状态。验收必须读取后端 draft revision 和 graph。

