# PV17 Product Closed Loop Milestone Roadmap

用途：定义路径1的里程碑、依赖和出门顺序。
阅读对象：项目管理、开发、测试、审计人员。
边界：本文不代表实现已完成；所有 PASS 只能来自对应证据包。
PV16 `/bff/pv16/*` 来自 test-only BFF evidence route，PV17 只能把它作为参考，不能把它当作正式产品 API。

| Milestone | Stage | 用户可见结果 | 代码范围 | Exit Gate |
| --- | --- | --- | --- | --- |
| PV17-R0 | Readiness | 用户和 reviewer 知道路径1目标、范围、No-Go 和代码实体。 | 文档与 drawio。 | PV17 文档验收 PASS。 |
| PV17-E0 | Environment | 开发者能在本地运行 API/CLI/pack smoke。 | Python env、依赖、测试命令。 | P0 smoke documented PASS 或清晰 BLOCKED。 |
| PV17-S1 | Product Console | 用户看到一个主线产品入口，不再只靠分散阶段页面理解项目。 | `App.tsx`, `ConsoleShell`, `WorkflowConsoleClient`, `bff.py`。 | Console inventory + health evidence PASS。 |
| PV17-S2 | Entity Mutation | 用户创建/更新 workspace/project/app/Station Agent 并看到 audit refs。 | BFF DTO、scope policy、Station Agent projection。 | Mutation + denial + route log PASS。 |
| PV17-S3 | Studio Versioning | 用户从 graph/patch/diff 到 WorkflowVersion，并可确认 run。 | `WorkflowEditingPanel`, `WorkflowRepository`, `GatewayService.workflow_patch_*`。 | graph round-trip + publish handoff PASS。 |
| PV17-S4 | Runtime Inspect | 用户看到 WorkflowInstance、StationRun、trace、artifact、quality、approval。 | `GatewayService.workflow_instance_*`, `station_run_*`, artifact/trace methods。 | runtime-backed inspect PASS。 |
| PV17-S5 | Evidence Review | 用户在一个证据视图完成 claim、redaction、route boundary 和 lineage 检查。 | evidence panel、operation evidence、runner。 | evidence review PASS。 |
| PV17-SA | Aggregate | Reviewer 接受一个 bounded 产品闭环结论。 | aggregate runner + manifest。 | PV17 bounded review allowed claim PASS。 |

## Dependency Rules

- PV17-E0 是实现前置；若环境无法恢复，必须在 PV17-R0 关闭文档计划后单独处理。
- PV17-S2 不能绕过 BFF 直接写 `WorkflowStore` 或 runtime truth。
- PV17-S3 不能在缺少 WorkflowDiff / confirmation / audit refs 时 publish/run。
- PV17-S4 不能从 screenshot 或 static docs 证明 runtime inspect。
- PV17-S5 不能在 redaction 或 No False Green 失败时进入 PV17-SA。
- PV17-SA 不能升级成 production、complete Studio、Agent executor 或 Xpert parity 声明。

## Recommended Sequence

1. 完成本轮 PV17 文档和 drawio。
2. 恢复本地 Python 环境并重跑 P0 smoke。
3. 实现 PV17-S1/S2，让正式 BFF DTO 替代 PV16 test-only product-runtime route 依赖。
4. 实现 PV17-S3/S4，把 Studio versioning 和 runtime inspect 串成一条用户路径。
5. 实现 PV17-S5/SA，用证据包和 runner 收口。
