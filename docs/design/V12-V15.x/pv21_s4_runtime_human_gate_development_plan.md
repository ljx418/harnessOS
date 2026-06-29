# PV21-S4 Runtime Run Human Gate Development Plan

用途：定义 PV21-S4 的开发、验收和审计闭环。
阅读对象：开发、测试、产品、审计人员。
边界：本文是子阶段计划，不是实现证据。

## Scope

PV21-S4 完成从已发布 WorkflowVersion 启动 run、inspect 和 human gate action。

## Development Tasks

- 后端新增 run、inspect、human-actions routes。
- Run 必须绑定 published WorkflowVersion，不能运行未发布 draft。
- Human action 必须只处理 waiting gate，且必须带 user confirmation。
- 前端展示 run history、station runs、pending human gate 和状态变化。

## Acceptance

- Runtime report PASS：WorkflowInstance 和 StationRun readback 存在。
- Human transition report PASS：waiting_approval 到 completed/rejected 有后端状态变化。
- human action without waiting gate denied。

## Audit Opinion

Go. 主要风险是 human gate 由前端模拟。验收必须读取后端 inspect DTO。

