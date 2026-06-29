# PV19 Runtime Workflow Platform PRD

用途：定义“完整工作流平台受控闭环”的本阶段产品目标、用户体验、边界和验收口径。
阅读对象：产品、架构、开发、测试、审计人员。
边界：本文是后续开发规格，不是实现证据；不得据此声明生产可用、完整 Workflow Studio、完整 Agent executor 或 Xpert parity。

## 1. Product Problem

当前 HarnessOS 已经具备多个 bounded review slice：

- V13 证明 editable Studio pilot：可以编辑 WorkflowSpecGraph、校验、查看 WorkflowDiff 和交接，但不运行。
- PV17 证明 product closed loop：可以从 Product Console 到 run inspect 和 evidence review，但不是完整 Studio。
- PV18 证明 Knowledge OPC bounded review：可以用真实 data_service MCP 跑业务审查流，但不是通用工作流平台闭环。

主要缺口是：用户还不能在同一个真实工作台里完成“编排 -> 发布 -> 运行 -> 人工交互 -> 证据审查”的通用平台闭环。

## 2. Stage Goal

PV19 的目标是让一个真实业务工作流通过通用工作流平台完成端到端受控闭环：

1. 用户打开工作台入口，看到可操作画布、节点库、Inspector、版本和运行区。
2. 用户在画布中创建或修改一个业务工作流。
3. 画布状态保存为通用 Workflow DSL / WorkflowSpecGraph。
4. 用户确认 WorkflowDiff 并发布 WorkflowVersion。
5. Runtime 按发布版本真实运行 WorkflowInstance。
6. 运行中出现至少一个人工确认、补充输入、驳回或重试节点。
7. 人工操作改变 runtime 状态，并留下 audit trail。
8. 用户在同一工作台查看 artifacts、trace、quality、audit 和 claim-to-evidence。

允许的完成声明只能是：

```text
PV19 complete: runtime-backed workflow platform closed loop ready for bounded review.
```

该声明仍不等于生产可用、完整 Workflow Studio、完整 Agent executor、product-grade frontend complete 或 Xpert parity complete。

## 3. Target Users

| User | Need | PV19 target experience |
| --- | --- | --- |
| 业务流程设计者 | 把业务目标变成可运行工作流 | 在画布中配置节点、连线、参数和人工卡点，并发布版本。 |
| 审核人员 | 确认工作流变更和人工卡点 | 查看 WorkflowDiff、确认发布、处理人工节点、审查 evidence。 |
| 平台开发者 | 验证平台通用性 | 看到业务样例通过通用 DSL、BFF、Gateway、Runtime、Evidence 路径运行。 |
| 审计人员 | 判断声明是否有证据支撑 | 对照 route log、DTO snapshot、runtime report、artifact lineage 和 audit trail。 |

## 4. User Scenarios

| Scenario | Target experience | Required evidence |
| --- | --- | --- |
| 工作台入口 | 用户打开 PV19 工作台，不再落到空白根路径。 | browser screenshot、visible route、health DTO。 |
| 编排工作流 | 用户添加节点、连线、配置参数、加入人工节点。 | graph DTO、action log、WorkflowDiff。 |
| 发布版本 | 用户确认 WorkflowDiff 后生成 WorkflowVersion。 | publish DTO、version readback、audit ref。 |
| 运行工作流 | 用户运行发布版本并看到 WorkflowInstance 进度。 | runtime event refs、station/node status、route log。 |
| 人工交互 | 用户处理 pending human gate 后流程继续或安全终止。 | approval/handoff DTO、state transition、audit trail。 |
| 证据审查 | 用户查看 artifact、trace、quality、claim evidence。 | artifact lineage、trace refs、claim-to-evidence matrix。 |

## 5. Functional Requirements

| ID | Requirement | Acceptance |
| --- | --- | --- |
| PV19-F1 | 工作台必须有明确默认入口和可见画布。 | 用户 60 秒内能识别 workspace、workflow、canvas、run 状态。 |
| PV19-F2 | 画布编辑必须落到通用 WorkflowSpecGraph。 | 节点、边、参数、人工节点可通过 BFF DTO readback。 |
| PV19-F3 | 发布必须经过 WorkflowDiff 和用户确认。 | 没有确认不得 publish 或 run。 |
| PV19-F4 | Runtime 必须按 WorkflowVersion 运行。 | run report 必须引用 workflow_version_id 和 runtime events。 |
| PV19-F5 | 人工交互必须改变 runtime 状态。 | pending -> approved/rejected/resumed/failed 状态有后端证据。 |
| PV19-F6 | Evidence 必须来自 runtime/artifact/trace/audit。 | 前端不得构造 runtime truth。 |
| PV19-F7 | 业务样例不得驱动平台定制。 | core、Gateway、App shell 无业务专用分支。 |

## 6. Non-Goals

- 不做生产可用声明。
- 不做完整 Workflow Studio 声明。
- 不做完整 Agent executor 声明。
- 不做 Xpert parity 声明。
- 不纳入多租户 SLA、商业计费、完整外部 App SDK、完整插件市场。
- 不把 PV19 业务样例做成平台核心的硬编码路径。
- 不把截图、介绍文档或 drawio 当成 runtime evidence。

## 7. Success Metrics

| Metric | Target |
| --- | --- |
| 用户主路径 | 编排、发布、运行、人工处理、证据审查全路径自动化 PASS。 |
| BFF 边界 | 浏览器只调用允许的 `/bff/pv19/*` 或正式 BFF route。 |
| Runtime truth | WorkflowInstance、node status、artifact、trace、audit 均由后端证据支撑。 |
| 平台通用性 | 至少一个业务样例运行，但平台核心不出现业务专用逻辑。 |
| 审计安全 | No False Green、redaction、claim-to-evidence 全部 PASS。 |

