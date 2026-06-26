# PV18 Knowledge OPC Productization PRD

用途：定义 PV18 Knowledge OPC 产品化阶段的产品规格。
阅读对象：产品、架构、开发、测试、审计人员和外部 Agent。
边界：本文是 PV18 开发规格和阶段口径说明；实现状态必须以代码、BFF DTO、browser E2E、acceptance runner 和 evidence package 为准。不得把本文、drawio、介绍页或单独截图当作 production evidence。

## 1. 阶段定位

PV18 选择 Path C：Business Pack Productization，首个业务域为 Knowledge。目标是把当前 `packs/knowledge` reference pack 推进为一条可审查的 OPC 业务产品流：

```text
Knowledge workspace setup
  -> source import / ingest
  -> build status
  -> query and answer
  -> citation review
  -> quality feedback
  -> correction plan
  -> evidence review
```

PV18 不替代 PV17 Product Closed Loop。PV17 证明 bounded 产品闭环 ready for review；PV18 证明一个业务域可以按 Pack / Connector / Gateway / BFF / Evidence 边界被产品化为 bounded review 业务流。

## 1.1 当前实现与证据状态

截至 2026-06-27，PV18 Knowledge OPC bounded review implementation 已通过阶段验收：

- `/bff/pv18/knowledge/*` BFF DTO route 已实现；
- `/?studio=pv18-knowledge-opc` 浏览器工作台已实现 source / query 输入和证据审查路径；
- 真实 `data_service_mcp / mcp_stdio` source、build、query、quality、correction 路径已通过验收；
- evidence package、截图、route log、browser network log、claim matrix、redaction scan 和 acceptance runner report 已生成；
- 允许声明仅限：`PV18 complete: Knowledge OPC productization implementation ready for bounded review.`

该状态不证明 production ready、完整 Workflow Studio、完整 Agent executor、Xpert parity 或完整商业 Knowledge 产品。

## 2. 目标用户

| 用户 | 目标体验 | PV18 要证明的内容 |
| --- | --- | --- |
| OPC 操作者 | 通过浏览器创建知识空间、导入资料、查询答案并审查引用。 | Knowledge 业务流可被产品化为用户可理解的端到端体验。 |
| 业务审查者 | 检查答案是否有 citation、quality feedback 和 correction plan。 | Knowledge 输出不能脱离证据链和质量门槛。 |
| 平台开发者 | 知道哪些 existing code 已复用、哪些 BFF/UI/runner 已新增。 | 实现不绕过 Pack、Connector、Gateway 和 BFF 边界。 |

## 3. 当前事实

| Area | 当前事实 | 代码入口 |
| --- | --- | --- |
| Knowledge Pack | `knowledge` pack 已 active，含 workflow、agents、skills、artifact schemas 和 data_service MCP capability。 | `packs/knowledge/manifest.json` |
| Knowledge workflow | 支持 connector-backed ingest/search，能注册 `source_reference`、`note`、`brief`、`citation_bundle` artifacts。 | `packs/knowledge/workflow.py` |
| Data Service MCP runner | 已有 workspace/source/build/query/quality/correction lifecycle runner。 | `apps/gateway/knowledge_mcp_workflow.py` |
| Connector runtime | 已有 connector submit / artifact / approval 运行路径。 | `apps/gateway/connector_execution.py` |
| Artifact / trace | 已有 artifact registry、lineage 和 trace read model。 | `apps/gateway/artifacts.py`, `apps/gateway/traces.py` |
| Browser console | 已有 workflow-console、ConsoleShell、V13 Studio 和 PV17 page。 | `apps/workflow-console/src/App.tsx` |

## 4. PV18 目标体验

PV18 bounded review 实现完成后，用户应能在一个 Knowledge OPC 页面完成：

0. 通过显式入口 `/?studio=pv18-knowledge-opc` 进入 Knowledge OPC；根路径继续保留当前 V13 editable Studio 体验。
1. 选择或创建 Knowledge workspace，并看到当前 `workspace_id`、scope、connector health 和 data boundary。
2. 导入一份 source/document，看到 source reference、note、artifact id 和 build status。
3. 发起 query，看到 answer / brief / citation bundle。
4. 检查每条 citation 的 source ref、artifact lineage 和引用覆盖状态。
5. 触发 quality feedback，看到质量结果、低信号来源提示和 correction rules。
6. 生成 correction plan，但不得静默改写知识库或发布业务结论。
7. 在 Evidence 视图审查 trace refs、artifact lineage、redaction、claim-to-evidence 和 No False Green 结果。
8. 在失败、空数据、权限拒绝、connector approval required、build failed、citation missing 时看到明确状态和下一步。

## 5. 功能范围

| 能力 | PV18 目标 | 主要实体 |
| --- | --- | --- |
| Knowledge Console | 从通用 Product Console 进入 Knowledge 工作流。 | `App.tsx`, `WorkflowStudioLayout`, `PV18KnowledgeOpc` |
| Source ingest | 通过 BFF DTO 调用 Knowledge Pack / data_service MCP 导入资料。 | `packs/knowledge/workflow.py`, `KnowledgeMcpWorkflowRunner` |
| Build status | 展示 build started / running / completed / failed。 | `apps/gateway/knowledge_mcp_workflow.py` |
| Query answer | 展示 answer、brief、citations、source refs。 | `knowledge_query_v2`, `citation_bundle` |
| Quality review | 展示 quality feedback、correction rules、correction plan。 | `knowledge_quality_feedback_v2`, `knowledge_correction_plan_v2` |
| Evidence review | 统一 artifact lineage、trace refs、redaction 和 claim scan。 | `ArtifactRegistry`, `TraceStore`, acceptance package |
| Browser boundary | 浏览器只走 `/bff/pv18/knowledge/*` route，不直连 connector/runtime/store。 | network log and denylist |

## 6. Interface Boundary

PV18 实现应以 `pv18_knowledge_opc_productization_bff_dto_contract.md` 为准。当前 bounded review 已实现以下 route 和 DTO 组：

- `/bff/pv18/knowledge/*` BFF route；
- `PV18KnowledgeStateDTO`、`PV18QueryResultDTO`、`PV18EvidenceSummaryDTO` 等 DTO；
- `schemas/pv18_knowledge_opc_acceptance_data.schema.json`；
- `schemas/pv18_knowledge_opc_artifact_manifest.schema.json`；
- `schemas/pv18_knowledge_opc_dto_snapshot.schema.json`。

这些内容仍只证明 bounded review；不表示生产 API、稳定外部 API 或完整商业数据服务已经完成。

## 7. 平台通用性红线

Knowledge OPC 是本阶段用来验证工作流平台的业务样本，不是平台定制化方向。实现和验收必须证明：

- Workflow platform 仍然面向多业务 Pack，不能把 Knowledge 业务语义写进通用 workflow core、runtime core、Gateway core 或 App shell 默认逻辑。
- 通用实体仍以 workspace、project、app、workflow、run、artifact、trace、evidence、policy、DTO 为边界；Knowledge 只能作为 pack/domain adapter 或 PV18 BFF DTO 的业务投影存在。
- `/bff/pv18/knowledge/*` 可以是业务域 BFF facade，但其内部必须复用通用 Pack / Connector / Gateway / Evidence 能力，不能创建绕过平台抽象的 Knowledge-only 快捷通道。
- 如果需要扩展平台能力，必须抽象成业务无关接口，并至少说明 Meeting / Knowledge / future Pack 均可复用；否则视为 PV18 阻断风险。
- 验收报告必须包含“platform generality review”，确认本阶段没有因为 Knowledge OPC 破坏工作流平台的通用性、泛用性和后续业务扩展能力。

## 8. 非目标

- 不声明 Knowledge 产品化已完成。
- 不声明 HarnessOS production ready。
- 不声明完整 Workflow Studio ready。
- 不声明 Agent executor ready。
- 不声明 Xpert parity complete。
- 不把 `packs/knowledge` reference pack 说成最终商业产品。
- 不为了 Knowledge OPC 对 workflow platform 做业务专用、不可泛化的 core/runtime/Gateway/App shell 定制。
- 不把 PV18 bounded review 实现扩大为生产实现声明。
- 不把 data_service MCP stub / contract evidence 说成真实生产数据服务。
- 不把未经过 evidence package 和 acceptance runner 验收的 route、schema 草案或 runner spec 写成已实现证据。

## 9. 允许声明

PV18 bounded review 验收通过后只允许：

```text
PV18 complete: Knowledge OPC productization implementation ready for bounded review.
```

该声明必须同时引用 `docs/design/V12-V15.x/evidence/pv18-knowledge-opc-productization/` 和 `docs/design/V12-V15.x/reports/pv18_knowledge_opc_productization_acceptance_report.json`。

新的 bounded claim 只能由 evidence package 和 acceptance runner 定义。
