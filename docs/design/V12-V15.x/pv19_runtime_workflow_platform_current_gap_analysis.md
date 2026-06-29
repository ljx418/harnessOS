# PV19 Runtime Workflow Platform Current Gap Analysis

用途：对比当前 V13/PV17/PV18 bounded evidence 和 PV19 完整工作流平台受控闭环目标。
阅读对象：架构、开发、测试、审计人员。
边界：本文是 gap 分析，不是实现证据；不得把 gap closure plan 当作 PASS。

## 1. Baseline

当前项目已经具备：

- V13 editable Studio pilot：画布编辑、graph validation、WorkflowDiff、handoff。
- PV17 product closed loop：Product Console、Mission Studio、confirm run、inspect、evidence。
- PV18 Knowledge OPC：真实 data_service MCP 业务流、citation、quality、evidence。
- Gateway、WorkflowStore、artifact registry、trace store、approval/audit 基线。

当前仍缺：

- 默认真实工作台入口，而不是空白根路径。
- 图编辑到 WorkflowVersion 发布的通用闭环。
- 发布版本到 Runtime 执行的强关联证据。
- 人工节点对 runtime 状态的真实影响。
- 同一工作台内聚合运行证据和审计结论。
- 证明业务样例没有污染平台核心的 generality review。

## 2. Gap Matrix

| Gap | 当前状态 | PV19 目标 | 状态 |
| --- | --- | --- | --- |
| 首页/入口 | 根路径可能显示空白实例；V13/PV18 需 query 参数进入。 | 明确真实工作台入口和最小体验路径。 | 需修改 |
| Studio 编排 | V13 可编辑 pilot graph，但不 run。 | Graph 可发布为 runtime 版本。 | 需修改 |
| WorkflowVersion | PV17/PV16 有 run/inspect slice，V13 publish 只是 handoff。 | WorkflowDiff -> publish -> version readback。 | 待新增 |
| Runtime 执行 | PV17 有 bounded run/inspect，PV18 有业务 runner。 | 发布版本驱动通用 WorkflowInstance。 | 需整合 |
| 人工交互 | handoff/approval 证据分散。 | human gate 改变 runtime 状态并可审计。 | 待新增 |
| Evidence | 各阶段证据包存在。 | 同一 run 聚合 artifact、trace、quality、audit、claim。 | 需修改 |
| 平台通用性 | PV18 已有 Knowledge 红线。 | PV19 样例不得新增业务专用平台逻辑。 | 需审计 |

## 3. Code Entity Gap

| Code entity | 当前作用 | PV19 gap |
| --- | --- | --- |
| `apps/workflow-console/src/App.tsx` | 根据 query 选择 V13/PV17/PV18 等视图。 | 需定义真实工作台入口，不让根路径成为空白交付体验。 |
| `apps/workflow-console/src/ui/v13/V13EditableStudio.tsx` | editable Studio pilot。 | 需承接 runtime publish/run，而不是只 handoff。 |
| `apps/workflow-console/src/api/workflowConsoleClient.ts` | BFF client。 | 需新增 PV19 graph/version/run/human/evidence DTO 方法。 |
| `apps/api/routers/bff.py` | BFF route 聚合。 | 需新增 PV19 planned route 或等价正式 BFF route。 |
| `apps/gateway/service.py` | Gateway method registry。 | 需串接 version、run、human、artifact、trace read model。 |
| `core/workflows/models.py` | workflow domain model。 | 需确认 graph、version、instance、human node 的一致模型。 |
| `core/workflows/store.py` | workflow repository/store。 | 需支持发布版本 readback 和 run handoff 所需查询。 |
| artifact/trace/audit stores | 运行证据基础设施。 | 需聚合成 PV19 evidence summary。 |

## 4. Audit Questions

1. 用户是否能从一个明确入口进入真实工作台？
2. 画布编辑结果是否可被 BFF readback，而不是只存在前端状态？
3. WorkflowDiff 是否必须人工确认才能发布？
4. WorkflowVersion 是否能被 run report 引用？
5. Runtime 是否真的按发布版本执行？
6. 人工节点是否改变后端状态？
7. 人工动作是否记录操作者、时间、前后状态和 audit refs？
8. Evidence 是否覆盖 artifact、trace、quality、audit 和 claim matrix？
9. Browser network log 是否没有 direct runtime/store/connector route？
10. 业务样例是否没有污染平台核心？

## 5. Recommended Closure

PV19 先完成文档、drawio、BFF DTO contract、runner spec 和 readiness audit，再进入代码实现。实现顺序必须从入口和 graph/version 一致性开始，再接 run/human/evidence，避免继续堆叠不可运行的工作台页面。

