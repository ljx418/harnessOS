# PV18 Knowledge OPC Productization BFF DTO Contract

用途：定义 PV18 Knowledge OPC 后续实现需要的 planned BFF route、DTO 分组和浏览器边界。
阅读对象：后端、前端、测试、审计人员。
边界：本文是 planned contract，不是已实现 API；不得把本文当作 BFF route、DTO、browser E2E 或 runtime evidence。

## 1. Contract Status

```text
status=planned
implementation_status=not_started
allowed_document_claim=PV18 Knowledge OPC productization development plan ready for implementation review.
```

PV18 后续实现必须使用显式浏览器入口：

```text
/?studio=pv18-knowledge-opc
```

根路径继续保留当前 V13 editable Studio 默认体验；PV18 不得回滚该入口修复。

## 2. Planned Route Set

所有 planned route 必须走 `apps/api/routers/bff.py` 或明确的 BFF router，不允许 browser 直连 connector runtime、data_service MCP internals 或 `/v1/rpc`。

| Route | Method | Purpose | Required user-visible result |
| --- | --- | --- | --- |
| `/bff/pv18/knowledge/state` | GET | 返回 workspace、scope、connector health、source/build/query/evidence 概览。 | 用户知道当前 Knowledge 上下文和可用状态。 |
| `/bff/pv18/knowledge/workspaces` | POST | 创建或选择 Knowledge workspace。 | 用户看到 workspace ref、scope、audit ref。 |
| `/bff/pv18/knowledge/sources/import` | POST | 导入 source/document。 | 用户看到 source_reference、note、artifact refs。 |
| `/bff/pv18/knowledge/builds/start` | POST | 启动 build。 | 用户看到 build id、status、next action。 |
| `/bff/pv18/knowledge/builds/{build_id}/status` | GET | 查询 build 状态。 | 用户看到 running/completed/failed 和失败原因。 |
| `/bff/pv18/knowledge/query` | POST | 发起 query。 | 用户看到 answer、brief、citation bundle、coverage。 |
| `/bff/pv18/knowledge/quality-feedback` | POST | 对 answer/citations 做质量反馈。 | 用户看到 quality report、risk、low signal sources。 |
| `/bff/pv18/knowledge/correction-plan` | POST | 生成 correction plan。 | 用户看到人工审查建议，不发生自动发布。 |
| `/bff/pv18/knowledge/evidence/summary` | GET | 汇总 lineage、trace、route boundary、redaction、claim matrix。 | 用户能审查正向声明和证据链。 |

## 3. DTO Groups

| DTO | Required fields | Notes |
| --- | --- | --- |
| `PV18KnowledgeStateDTO` | `schema_version`, `status`, `scope`, `workspace`, `connector_health`, `sources`, `builds`, `queries`, `evidence_summary`, `redaction_status` | 首屏 read model。 |
| `PV18KnowledgeWorkspaceDTO` | `workspace_id`, `display_name`, `owner`, `scope`, `audit_refs`, `redaction_status` | 不包含 raw credential。 |
| `PV18SourceImportResultDTO` | `status`, `source_reference`, `note`, `artifact_refs`, `lineage_refs`, `audit_refs`, `redaction_status` | 必须产生标准 Knowledge artifact。 |
| `PV18BuildStatusDTO` | `build_id`, `workspace_id`, `status`, `stage`, `failure_reason`, `trace_refs`, `next_actions`, `redaction_status` | `failed` 必须可解释。 |
| `PV18QueryResultDTO` | `query_id`, `answer`, `brief`, `citation_bundle`, `citation_coverage`, `source_refs`, `artifact_refs`, `trace_refs`, `redaction_status` | 无 citation 不得标记 verified。 |
| `PV18QualityFeedbackDTO` | `quality_status`, `issues`, `low_signal_sources`, `correction_required`, `trace_refs`, `redaction_status` | 风险必须用户可见。 |
| `PV18CorrectionPlanDTO` | `plan_id`, `status`, `rules`, `requires_human_review`, `auto_publish_allowed`, `audit_refs`, `redaction_status` | `auto_publish_allowed` 必须为 `false`。 |
| `PV18EvidenceSummaryDTO` | `claims`, `route_boundary`, `artifact_lineage`, `trace_timeline`, `redaction`, `missing_evidence`, `allowed_claim`, `redaction_status` | 只读 evidence，不构造 runtime truth。 |

## 4. Boundary Rules

- Browser allowlist：`/bff/pv18/knowledge/*` 和必要静态资源。
- Browser denylist：`/v1/rpc`、connector runtime、internal runtime/store、data_service MCP internal route、debug runtime route。
- BFF DTO 必须带 `schema_version` 和 `redaction_status`.
- raw secret、raw provider payload、raw connector payload、raw artifact content 不得出现在 DTO、UI 或证据包。
- `citation_coverage.status` 不是 `pass` 时，UI 只能显示待审查或阻断状态。
- `CorrectionPlanDTO.auto_publish_allowed` 必须为 `false`；后续如允许发布，必须另起阶段和验收门槛。

## 5. Planned Schema Entries

机器可读草案：

- `schemas/pv18_knowledge_opc_acceptance_data.schema.json`
- `schemas/pv18_knowledge_opc_artifact_manifest.schema.json`
- `schemas/pv18_knowledge_opc_dto_snapshot.schema.json`

这些 schema 只服务后续实现验收，不代表当前 DTO 已存在。
