# PV17 Product Closed Loop Acceptance Gate

用途：定义路径1 PV17 Product Closed Loop 的文档阶段、实现阶段和阶段性复验门槛。
阅读对象：测试、审计、开发、产品人员。
边界：本文定义 gate 并记录当前 PV17 bounded review 结论；不把 PV17 扩大为生产可用、完整 Workflow Studio 或 Agent executor。
PV16 `/bff/pv16/*` 来自 test-only BFF evidence route，PV17 只能把它作为参考，不能把它当作正式产品 API。

## 1. 文档阶段 Gate

本轮文档开发必须满足：

- PV17 PRD、目标架构、开发及验收计划、里程碑、验收门槛、gap 分析和 drawio 均存在。
- PV17 BFF/DTO 合约、实现任务矩阵、acceptance runner spec 和 implementation readiness audit 均存在。
- 每份 Markdown 顶部说明用途、阅读对象和边界。
- drawio 页数不超过 8 页，使用中文，包含颜色图例和具体代码实体。
- 文档明确 PV16 `/bff/pv16/*` 是 test-only BFF evidence，不是正式产品 API。
- 文档不能把 docs、drawio、截图或介绍页描述为 runtime / BFF / DTO / browser E2E / production evidence。

## 2. 实现 Gate

| Scenario | PASS 条件 | Blocking Failure |
| --- | --- | --- |
| Product Console | 用户能看到 workspace/project/app/workflow/Station Agent/system health，并理解当前上下文。 | UI 仍是分散阶段页，或 API/config mismatch 被隐藏。 |
| Entity Mutation | durable mutation 通过正式 `/bff/pv17/*` DTO，含 ownership check、policy decision、audit refs。 | 直接写 runtime/store，或只有 fixture evidence。 |
| Station Agent Setup | 用户能配置 role、goal、memory/model/tool/skill/MCP refs，敏感信息脱敏。 | raw secret、raw provider payload 或 raw artifact content 出现在 UI/证据。 |
| Studio Versioning | WorkflowDiff/patch 可 round-trip，publish/run 需要用户确认。 | source=agent 静默 publish/run，或 graph 不能 round-trip。 |
| Runtime Inspect | UI 展示 WorkflowInstance、StationRun、trace refs、artifact refs、quality refs、approval refs。 | runtime evidence 缺失或由静态文档替代。 |
| Evidence Review | 用户看到 claim-to-evidence、route boundary、artifact lineage、redaction 和 No False Green。 | claim scan 或 redaction scan FAIL。 |
| Browser Boundary | browser network log 只包含 allowlist route。 | 出现 `/v1/rpc`、`/internal/runtime`、`/runtime/store`、`/api/runtime`、`/debug/runtime`。 |

## 3. Required Artifacts For PV17-SA

PV17-SA 至少需要，且当前证据包已按这些类别落盘：

- browser screenshots and action logs;
- BFF route log and browser network log;
- DTO snapshots and schema validation;
- explicit `/bff/pv17/*` route allowlist evidence;
- runtime run inspect report;
- trace/artifact/quality/approval refs;
- claim-to-evidence matrix;
- No False Green scan;
- redaction scan;
- PRD review;
- target architecture review;
- audit closure.

## 4. Forbidden Positive Claims

以下声明只能出现在明确否定、禁止、风险或 No-Go 语境中：

- HarnessOS is production ready.
- Xpert parity complete.
- product-grade frontend complete.
- complete Workflow Studio ready.
- Agent executor ready.

## 5. Current Exit

历史文档阶段允许出门条件：

```text
PV17 product closed loop documentation ready for implementation review.
```

该条件只说明文档可进入实现评审，不说明任何功能已经实现。

当前 PV17 bounded review 出门条件：

```text
PV17 complete: product closed loop implementation ready for bounded review.
```

该条件由正式 `/bff/pv17/*` 路由、DTO 快照、browser E2E、acceptance runner、PRD/架构审计和证据包共同支撑；它仍不表示生产可用、完整 Workflow Studio、Agent executor 或 Xpert parity。
