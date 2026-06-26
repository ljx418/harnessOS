# PV18 Knowledge OPC Productization Implementation Readiness Audit

用途：记录 PV18 Knowledge OPC 产品化文档阶段的实现准备度审计。
阅读对象：项目负责人、开发 Agent、测试、产品、审计人员。
边界：本文是文档阶段审计意见；最终通过状态必须以后续 evidence package 和 acceptance runner 输出为准。

## 1. Audit Result

```text
stage=PV18-R0
document_readiness=PASS_FOR_IMPLEMENTATION_REVIEW
implementation_status=NOT_STARTED
fatal_findings=0
major_findings=0
```

## 2. PRD Coverage

| PRD requirement | Audit conclusion |
| --- | --- |
| Knowledge OPC 目标用户、目标体验和非目标清晰。 | PASS：PRD 明确 workspace -> source -> query -> citation -> quality -> correction -> evidence。 |
| 当前实现事实不被夸大。 | PASS：`packs/knowledge` 被标注为 reference pack baseline。 |
| Knowledge 输出必须有 citation 和 evidence 边界。 | PASS：验收门槛要求 citation bundle、artifact lineage 和 trace refs。 |
| Correction plan 不能静默改写知识库。 | PASS：PRD、架构和 gate 均设为阻断条件。 |
| BFF DTO、runner 和 schema 支撑自动化开发。 | PASS：已补 planned BFF DTO contract、runner spec、task matrix 和 3 个 schema 草案。 |
| No-Go 声明完整。 | PASS：禁止生产可用、完整产品化、完整 Studio、Agent executor 和 Xpert parity。 |

## 3. Architecture Coverage

本轮目标链路为：

```text
Browser Knowledge OPC view
  -> WorkflowConsoleClient planned Knowledge DTO methods
  -> apps/api/routers/bff.py planned /bff/pv18/knowledge/* routes
  -> GatewayService
  -> KnowledgeMcpWorkflowRunner
  -> ConnectorExecutionRuntime / data_service_mcp
  -> ArtifactRegistry / TraceStore
  -> PV18 evidence package / acceptance runner
```

关键边界：

- Browser 不直连 connector runtime、data_service MCP internal route 或 `/v1/rpc`。
- Knowledge Pack 不被重写成 Core/Gateway 特例。
- Artifact lineage、trace refs 和 claim matrix 只读 evidence，不构造 runtime truth。
- Correction plan 是人工审查建议，不是自动发布。

## 4. Closed Findings

| Finding | Severity | Closure |
| --- | --- | --- |
| 下一阶段目标未锁定。 | Major | 已选择 Path C：Business Pack Productization。 |
| 首个业务域未锁定。 | Major | 已选择 Knowledge。 |
| Knowledge reference pack 与产品化目标可能混淆。 | Major | 所有 PV18 文档顶部和 No-Go 明确 reference pack baseline，不是完成声明。 |
| Drawio 需要包含架构、规格、计划和验收。 | Major | `pv18_knowledge_opc_productization_gap_analysis.drawio` 规划 7 页，覆盖目标体验、差异、代码实体、业务流、计划、里程碑、验收。 |
| 自动化开发缺少 DTO/runner/schema 细节。 | Major | 已新增 BFF DTO contract、acceptance runner spec、implementation task matrix 和 schema 草案。 |

## 5. Residual Risk

| Risk | Level | Disposition |
| --- | --- | --- |
| data_service MCP 当前可能仍是 contract / stub evidence。 | Medium | 后续实现必须区分 contract evidence 与真实生产数据服务。 |
| Knowledge 产品化 UI 可能与现有 V13 默认入口竞争。 | Medium | 后续实现需定义入口，不得回滚当前根路径体验修复。 |
| 业务质量评价容易被误报为自动可信答案。 | Medium | citation missing、quality failure、correction pending 均设为阻断或显式状态。 |
| PV18 容易被理解为生产业务产品。 | Medium | 只允许 bounded review 声明，No False Green 扫描必须保留。 |

## 6. Audit Opinion

PV18 文档可以支撑进入 implementation review。后续实现必须承接本文定义的 BFF DTO、evidence package、runner、schema 和 No False Green gate，且不得把文档阶段 PASS 当成功能实现 PASS。
