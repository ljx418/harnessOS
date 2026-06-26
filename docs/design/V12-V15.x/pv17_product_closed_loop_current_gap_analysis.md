# PV17 Product Closed Loop Current Gap Analysis

用途：对比当前架构和路径1目标架构，列出开发差距。
阅读对象：架构、开发、测试、审计人员。
边界：本文是 gap 分析，不是实现证据；不得把 gap closure plan 当作 PASS。
PV16 `/bff/pv16/*` 来自 test-only BFF evidence route，PV17 只能把它作为参考，不能把它当作正式产品 API。

## 1. Baseline

当前项目已经有：

- Gateway protocol control plane、BFF routes、runtime workflow methods、artifact/trace/approval/quality methods。
- `apps/workflow-console` 的主 Console、V12/V13/V14/V15/PV16 阶段页面和 e2e 证据。
- PV16 product-runtime hardening pilot evidence。
- Meeting / Knowledge reference packs 和 connector runtime。

当前仍缺：

- 一个主线产品入口承载完整 `setup -> Studio -> run -> inspect -> evidence`。
- 正式 BFF 产品实体 mutation route，而不是依赖 PV16 test-only route。
- Studio versioning、publish/run、runtime inspect 和 evidence review 的连续用户体验。
- PV17 专属 schema、runner 和证据包；runner 行为已由 `pv17_product_closed_loop_acceptance_runner_spec.md` 定义。

## 2. Gap Matrix

| Gap | 当前状态 | PV17 目标 | 状态 |
| --- | --- | --- | --- |
| Product Console continuity | 主 Console 和阶段页面并存。 | 主线入口能解释和驱动完整闭环。 | 需修改 |
| PV16 route maturity | `/bff/pv16/*` 在 e2e smoke server。 | 正式 `/bff/*` DTO route 承载产品实体和 run inspect。 | 待新增 |
| Product entity mutation | V12 projection、PV16 pilot mutation evidence。 | workspace/project/app/Station Agent 正式 mutation + audit refs。 | 待新增 |
| Studio to runtime continuity | V13 editable pilot 和 PV16 runtime pilot 分离。 | WorkflowDiff -> WorkflowVersion -> WorkflowInstance -> inspect 连续。 | 需修改 |
| Runtime inspect | Gateway methods 已存在，UI 闭环未主线化。 | UI 读取 station/run/trace/artifact/quality/approval DTO。 | 需修改 |
| Evidence review | operation evidence 和 PV16 evidence package 存在。 | 一屏审计 claim-to-evidence、route boundary、lineage、redaction。 | 待新增 |
| Local validation | 当前 Python env 未验证。 | 恢复 smoke 后再进入实现。 | 阻断 |

## 3. Code Entity Gap

| Code entity | 当前作用 | PV17 gap |
| --- | --- | --- |
| `apps/workflow-console/src/App.tsx` | 选择主 Console 或 `?studio=` 阶段页。 | 需要主线产品闭环入口。 |
| `apps/workflow-console/src/api/workflowConsoleClient.ts` | 调用 `/bff` workflow/agent/evidence routes。 | 需要正式 product entity 和 run inspect DTO client。 |
| `apps/workflow-console/src/ui/pv16/PV16ProductRuntimeHardening.tsx` | 展示 PV16 bounded pilot。 | 作为体验参考，不应继续绑定 test-only `/bff/pv16/*`。 |
| `apps/api/routers/bff.py` | 正式 workflow console BFF。 | 需要承载 PV17 主线 DTO 和 mutation/inspect route。 |
| `apps/api/routers/runs.py` | `/v1/runs`、stream、rpc。 | 需通过 BFF handoff 复用，不让 browser 直连。 |
| `apps/gateway/service.py` | workflow、station、quality、artifact、trace、approval、pack、connector RPC。 | 需明确 product closed loop 调用链和 evidence refs。 |
| `core/workflows/store.py` | dev/local workflow repository。 | 需保证 patch/version/instance 的用户闭环一致性。 |
| `core/station_agents/contracts.py` | Station Agent bounded contracts。 | 需映射为产品实体 DTO 与 audit projection。 |

## 4. Audit Questions

1. 用户是否能在 60 秒内识别当前 workspace/project/app/workflow？
2. 每个 durable mutation 是否有 BFF route、user confirmation、ownership policy 和 audit ref？
3. Browser network log 是否没有 direct runtime/store route？
4. WorkflowDiff 是否能解释 before/after，并阻止 source=agent 静默 publish/run？
5. Runtime inspect 是否包含 runtime events、trace refs、artifact refs、quality refs？
6. Evidence view 是否能把正向声明映射到证据文件？
7. PV16 test-only evidence 是否被清楚标注为 pilot reference？
8. Redaction scan 是否覆盖 raw secret、provider payload 和 raw artifact content？
9. 失败、拒绝、空状态和加载状态是否对用户可见？
10. 文档和 UI 是否避免所有 forbidden positive claims？

## 5. Recommended Closure

PV17 先完成文档和环境验证，再实现主线产品闭环。不要在环境未恢复、正式 BFF route 未定义、证据 schema 未冻结前进入功能开发。当前文档支撑状态记录在 `pv17_product_closed_loop_implementation_readiness_audit.md`。
