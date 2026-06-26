# PV18 Knowledge OPC Productization Implementation Task Matrix

用途：把 PV18 文档目标拆成后续实现任务、代码实体和验收输出。
阅读对象：开发、测试、审计人员。
边界：本文是 planned implementation matrix，不是代码实现；不得把任务项当作完成证据。

## 1. Task Matrix

| Stage | Implementation task | Code entity | Acceptance output |
| --- | --- | --- | --- |
| PV18-S1 | 增加显式入口 `?studio=pv18-knowledge-opc` 和 Knowledge Console read model。 | `App.tsx`, `WorkflowStudioLayout` 或等价 view | `knowledge-console-screenshot.png`, `knowledge-console-report.json` |
| PV18-S1 | 增加 planned Knowledge client methods。 | `WorkflowConsoleClient`, `types.ts` | DTO snapshot and client route tests |
| PV18-S1 | 增加 `/bff/pv18/knowledge/state`。 | `apps/api/routers/bff.py` | BFF route log and state DTO |
| PV18-S2 | 封装 source import。 | `KnowledgeMcpWorkflowRunner`, connector runtime, BFF route | `source-ingest-report.json` |
| PV18-S2 | 暴露 build start/status read model。 | `knowledge_build_start`, `knowledge_build_status` | build success/failure reports |
| PV18-S3 | 封装 query answer and citation bundle。 | `knowledge_query_v2`, `packs/knowledge/workflow.py` | `knowledge-query-report.json` |
| PV18-S3 | 增加 citation missing negative fixture。 | runner fixtures | blocking failure evidence |
| PV18-S4 | 封装 quality feedback and correction plan。 | `knowledge_quality_feedback_v2`, `knowledge_correction_plan_v2` | `quality-correction-report.json` |
| PV18-S4 | 阻止 correction auto publish。 | BFF policy and UI state | denial/blocked evidence |
| PV18-S5 | 聚合 artifact lineage and trace refs。 | `ArtifactRegistry`, `TraceStore`, GatewayService read methods | `artifact-lineage-report.json` |
| PV18-S5 | 增加 evidence summary view/report。 | planned UI panel, BFF evidence DTO | `evidence-review-report.json` |
| PV18-S5 | 完成 platform generality review，证明 Knowledge 没有污染通用平台层。 | `App.tsx`, `apps/api/routers/bff.py`, `GatewayService`, connector runtime, artifact/trace stores | `platform-generality-review.md` |
| PV18-SA | 增加 acceptance runner and schemas。 | `tools/pv18`, schemas | acceptance report PASS |

## 2. Negative Fixtures

后续实现至少需要：

- `missing_citation_blocks_verified_answer`
- `build_failed_is_visible`
- `connector_approval_required_is_visible`
- `correction_plan_auto_publish_denied`
- `browser_direct_rpc_denied`
- `connector_runtime_direct_route_denied`
- `knowledge_only_platform_customization_denied`
- `raw_secret_redaction_required`
- `artifact_lineage_missing_blocks_pass`

## 3. UI State Requirements

Knowledge OPC 页面必须有：

- empty state：无 workspace/source/query 时显示下一步。
- loading state：source import、build、query、quality 进行中。
- denied state：权限、scope、connector approval 或 policy 拒绝。
- failed state：build/query/connector failure。
- pending review state：citation missing、quality risk、correction plan 待人工审查。
- evidence ready state：lineage、trace、claim matrix 都可审查。

## 4. Implementation Constraints

- Knowledge OPC 是业务工作流验证样本，不是平台定制项目。
- 不新增 Core/Gateway business special-case 绕过 Pack。
- 不在 workflow core、Gateway core、connector runtime、artifact registry、trace store 或 App shell 写入 Knowledge-only 分支、枚举、快捷通道或默认语义。
- 新增平台接口必须业务无关；如果确实需要扩展平台层，任务说明和测试必须证明该接口可被非 Knowledge Pack 复用。
- 不让 browser 直连 connector runtime、data_service MCP internals 或 `/v1/rpc`。
- 不回滚当前根路径 V13 默认入口。
- 不混入 Path B external app contract 或 Path D production governance hardening。
- 不把 PV18 实现扩大成生产数据服务、商业计费、SLA 或完整权限体系。

## 5. Exit Dependency

PV18 代码实现开始前必须满足：

- 本 task matrix 已读。
- BFF DTO contract 已读。
- acceptance runner spec 已读。
- schema 草案可解析。
- drawio 方向经人工审核未偏移或过度承诺。
