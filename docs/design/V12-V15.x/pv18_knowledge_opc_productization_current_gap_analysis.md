# PV18 Knowledge OPC Productization Current Gap Analysis

用途：对比当前 Knowledge reference pack 和 PV18 Knowledge OPC 产品化目标，列出开发差距。
阅读对象：架构、开发、测试、审计人员。
边界：本文是 gap 分析，不是实现证据；不得把 gap closure plan 当作 PASS。

## 1. Baseline

当前项目已经有：

- `packs/knowledge` active reference pack。
- Knowledge workflow，支持 connector-backed ingest/search 和 legacy fallback。
- data_service MCP lifecycle runner，覆盖 workspace/source/build/query/quality/correction。
- Connector runtime、artifact registry、trace store 和 PackRegistry。
- PV17 产品闭环 bounded review 证据，可作为产品入口和证据 discipline 参考。

当前仍缺：

- 一个面向用户的 Knowledge OPC 产品入口。
- 正式 BFF Knowledge DTO route 和 browser client 方法。
- source ingest、build、query、citation、quality、correction 的连续用户体验。
- PV18 专属 schema、runner、证据包和审计报告。
- PV18 BFF DTO 合同、runner spec、task matrix 和 schema 草案已补齐为文档阶段支撑，但尚未实现。
- 对 Knowledge 输出“可引用、可审查、可纠错”的验收门槛。

## 2. Gap Matrix

| Gap | 当前状态 | PV18 目标 | 状态 |
| --- | --- | --- | --- |
| Knowledge Console | 只有通用 console 和 reference pack。 | 用户可进入 Knowledge workspace 产品流。 | 待新增 |
| BFF DTO | 无 PV18 Knowledge 专属 route。 | planned `/bff/pv18/knowledge/*` DTO 边界。 | 待新增 |
| DTO/schema contract | 文档阶段已有 planned contract 和 schema 草案。 | 后续实现按 schema 输出 DTO snapshots。 | 需实现 |
| Source ingest UX | workflow 能 ingest，但非产品化 UI。 | 用户导入 source 并看到 artifact lineage。 | 待新增 |
| Build status | runner 有 build step。 | UI 显示 build lifecycle 和失败原因。 | 需修改 |
| Query/citation | workflow 能返回 brief/citation artifact。 | UI 显示 answer、brief、citation coverage。 | 需修改 |
| Quality/correction | runner 有 quality/correction steps。 | UI 显示 quality feedback 和人工审查 correction plan。 | 需修改 |
| Evidence review | artifact/trace 设施存在。 | 一屏审查 lineage、trace、redaction、claim matrix。 | 待新增 |
| Acceptance runner | 无 PV18 runner。 | `tools/pv18` runner 和 evidence schema。 | 待新增 |

## 3. Code Entity Gap

| Code entity | 当前作用 | PV18 gap |
| --- | --- | --- |
| `packs/knowledge/manifest.json` | 定义 workflow、agents、skills、connectors、artifact schemas。 | 需被文档映射为产品化业务规格。 |
| `packs/knowledge/workflow.py` | connector-backed ingest/search，注册 Knowledge artifacts。 | 需支撑产品级 source/query/quality evidence 的验收口径。 |
| `apps/gateway/knowledge_mcp_workflow.py` | data_service MCP lifecycle runner。 | 需被 BFF DTO 封装，不暴露内部 connector details。 |
| `apps/gateway/connector_execution.py` | connector submit / artifact / approval path。 | 需保证 browser 不直连。 |
| `apps/gateway/artifacts.py` | artifact registry and lineage。 | 需产出 PV18 artifact lineage report。 |
| `apps/gateway/traces.py` | trace read model。 | 需产出 query/quality/correction trace refs。 |
| `apps/api/routers/bff.py` | 正式 product BFF。 | 需新增 planned Knowledge DTO route。 |
| `apps/workflow-console/src/api/workflowConsoleClient.ts` | Browser BFF client。 | 需新增 planned Knowledge methods。 |
| `apps/workflow-console/src/components/ConsoleShell.tsx` | 当前主 console。 | 需新增或接入 Knowledge OPC 页面/面板。 |
| `docs/design/V12-V15.x/schemas/pv18_knowledge_opc_*.schema.json` | 文档阶段 schema 草案。 | 后续 runner 必须按 schema 校验证据。 |

## 4. Audit Questions

1. 用户是否能在 60 秒内识别当前 Knowledge workspace、source、query 和 build 状态？
2. source import 是否产生 source_reference、note 和 artifact lineage？
3. query answer 是否必须带 citation bundle 和 source refs？
4. citation missing 时 UI 是否阻止“已验证答案”声明？
5. quality feedback 是否能解释风险和低信号来源？
6. correction plan 是否保持人工审查建议，不自动发布或改写知识库？
7. Browser network log 是否没有 direct connector/runtime/store route？
8. Evidence view 是否能把正向声明映射到 artifact、trace 和 route evidence？
9. Redaction scan 是否覆盖 raw secret、provider payload 和 raw artifact content？
10. 文档和 UI 是否避免所有 forbidden positive claims？

## 5. Recommended Closure

PV18 先完成文档、BFF DTO contract、evidence schema、runner spec、task matrix 和 implementation readiness audit，再进入代码实现。不要在这些实现前置项冻结前开始产品化代码开发。
