# PV21-S1 Entry And State DTO Development Plan

用途：定义 PV21-S1 的开发、验收和审计闭环。
阅读对象：开发、测试、产品、审计人员。
边界：本文是子阶段计划，不是实现证据；不得据此声明完整工作流工作台已完成。

## Scope

PV21-S1 只完成默认入口、PV21 Studio shell 和 `/bff/pv21/studio/state`。不在本子阶段实现完整画布编辑、发布、运行或回滚。

## Development Tasks

- 后端新增 PV21 schema version、scope/user confirmation/audit helper。
- 后端新增 `/bff/pv21/studio/state`，复用 PV19 workflow fixture 和 repository state，返回 scope、node library、draft graph、published version、version history、run history、evidence health。
- 前端新增 `pv21-complete-workflow-studio` entry state 和 PV21 shell。
- 前端新增 PV21 DTO types 和 client method。

## Acceptance

- `/bff/pv21/studio/state` 返回 `pv21.complete_workflow_studio.v1`。
- 默认或显式 PV21 URL 首屏非空。
- Browser route boundary 只需要读取 `/bff/pv21/studio/state`。
- No False Green 和 redaction scan 无新增违规。

## Audit Opinion

Go. 本子阶段风险低，核心风险是入口仍然空白或误用前端 mock。验收必须以 BFF state DTO 为准。

