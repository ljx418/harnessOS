# PV18 Knowledge OPC Productization Target Architecture

用途：定义 PV18 Knowledge OPC 产品化目标架构、当前差异和具体代码实体交互。
阅读对象：架构、后端、前端、测试、审计人员。
边界：本文定义 PV18 目标架构、当前实现映射和证据边界；实现状态必须以代码、browser E2E、BFF route log、DTO schema、acceptance runner 和 evidence package 为准。

## 1. 架构意图

PV18 采用“业务 Pack 产品化但不绕过平台边界”的路径。Knowledge 业务能力必须继续运行在 Pack / Connector / Gateway / BFF / Evidence 分层内，不能把业务逻辑硬编码进 Core/Gateway 特例，也不能让浏览器直连 connector runtime。

目标不是创建一个孤立 demo 页面，而是把 `packs/knowledge` 的 workspace、source、build、query、quality 和 correction lifecycle 映射为可审查的产品体验。

架构红线：Knowledge OPC 只能验证平台通用能力，不能驱动平台向 Knowledge-only 方向定制。任何新增平台抽象都必须保持业务无关，并能被 Meeting、Knowledge 或后续 Pack 复用；否则应留在 `packs/knowledge`、domain adapter、PV18 BFF facade 或 UI view 内。

## 2. 当前到目标分层

```text
User
  -> apps/workflow-console/src/App.tsx
  -> ?studio=pv18-knowledge-opc
  -> PV18KnowledgeOpc browser view
  -> WorkflowConsoleClient Knowledge DTO methods
  -> apps/api/routers/bff.py /bff/pv18/knowledge/* routes
  -> apps.gateway.service.GatewayService
  -> apps.gateway.knowledge_mcp_workflow.KnowledgeMcpWorkflowRunner
  -> apps.gateway.connector_execution.ConnectorExecutionRuntime
  -> data_service_mcp connector contract
  -> ArtifactRegistry / TraceStore / evidence package
```

## 3. 具体代码实体状态

| Layer | 已实现/复用 | PV18 需修改 | PV18 待新增 |
| --- | --- | --- | --- |
| Browser shell | `App.tsx`, `WorkflowStudioLayout`, `PV18KnowledgeOpc` | 已增加 Knowledge OPC 入口与状态视图 | 后续只做体验增强，不扩大阶段声明 |
| Browser client | `WorkflowConsoleClient` | 已增加 Knowledge DTO 方法 | 后续如稳定外部 API 需另立契约 |
| API BFF | `apps/api/routers/bff.py` | 已将 Knowledge lifecycle 暴露为 BFF DTO，不暴露 connector internals | 后续可补持久化和生产权限，但不属于 PV18 bounded review |
| Gateway | `apps/gateway/service.py` | 复用 pack、connector、artifact、trace 能力；新增能力必须业务无关 | generic read model aggregation hook if needed |
| Knowledge Pack | `packs/knowledge/manifest.json`, `packs/knowledge/workflow.py` | 明确产品化输入输出、quality gate、evidence refs | product-facing scenario contract |
| MCP runner | `apps/gateway/knowledge_mcp_workflow.py` | 已对齐 BFF DTO 的 workspace/source/build/query/quality/correction 状态 | bounded acceptance fixtures |
| Connector runtime | `apps/gateway/connector_execution.py` | 保持 approval、job、artifact boundary | 无；优先复用 |
| Evidence | `apps/gateway/artifacts.py`, `apps/gateway/traces.py` | 已聚合 Knowledge artifact lineage 和 trace refs 到 evidence package | 后续生产审计需单独阶段 |
| Tests/tools | pack assembly tests, PV18 BFF tests, PV18 acceptance runner, CDP E2E | 已增加 Knowledge OPC acceptance runner | CI 浏览器依赖 hardening 可单独处理 |

## 4. BFF / DTO Interface

实现必须以 `pv18_knowledge_opc_productization_bff_dto_contract.md` 为接口来源。当前 PV18 bounded review 已实现：

```text
GET  /bff/pv18/knowledge/state
POST /bff/pv18/knowledge/workspaces
POST /bff/pv18/knowledge/sources/import
POST /bff/pv18/knowledge/builds/start
GET  /bff/pv18/knowledge/builds/{build_id}/status
POST /bff/pv18/knowledge/query
POST /bff/pv18/knowledge/quality-feedback
POST /bff/pv18/knowledge/correction-plan
GET  /bff/pv18/knowledge/evidence/summary
```

最低 DTO 组：

- `PV18KnowledgeStateDTO`
- `PV18SourceImportResultDTO`
- `PV18BuildStatusDTO`
- `PV18QueryResultDTO`
- `PV18QualityFeedbackDTO`
- `PV18CorrectionPlanDTO`
- `PV18EvidenceSummaryDTO`

所有 DTO 必须包含 `schema_version` 和 `redaction_status`，并禁止 raw secret、raw provider payload、raw connector payload 和 raw artifact content。

## 5. 目标交互链路

| 用户动作 | Browser | BFF | Gateway/Pack | Evidence |
| --- | --- | --- | --- | --- |
| 打开 Knowledge Console | 显示 workspace、connector health、scope | `GET /bff/pv18/knowledge/state` | pack registry + connector health | screenshot、DTO snapshot |
| 导入 source | 粘贴 source metadata/content | `POST /sources/import` | `knowledge_source_import` via data_service MCP | source_reference、note artifacts |
| 启动 build | 用户确认 build | `POST /builds/start` | `knowledge_build_start/status` | build status trace |
| 查询答案 | 输入问题 | `POST /query` | `knowledge_query_v2` | brief、citation_bundle |
| 质量审查 | 请求 quality feedback | `POST /quality-feedback` | `knowledge_quality_feedback_v2` | quality report |
| 修正计划 | 生成 correction plan | `POST /correction-plan` | correction rules / plan tools | correction refs |
| 审查证据 | 打开 evidence panel | `GET /evidence/summary` | read-only artifact/trace stores | claim-to-evidence、redaction |

## 6. 边界规则

- Browser 不能直接调用 `/v1/rpc`、connector runtime、internal runtime/store 或 data_service MCP internals。
- Knowledge source import、query、quality 和 correction 必须通过 BFF DTO 或后端受控 API。
- Knowledge answer 不能没有 citation bundle 就被标记为可发布结论。
- Correction plan 只能作为人工审查建议，不能静默改写知识库。
- Artifact lineage 和 trace refs 只能读取 evidence，不能由前端构造 runtime truth。
- raw secret、raw provider payload、raw artifact content 不得进入 UI 或证据报告。
- Core workflow model、Gateway service、connector runtime、artifact registry、trace store 和 App shell 不得引入 Knowledge-only 分支、枚举或硬编码流程。
- Knowledge-specific code 必须收敛在 `packs/knowledge`、PV18 BFF DTO facade、PV18 Knowledge OPC view、runner fixtures 或 domain adapter 内。
- 如果实现需要新增 workflow platform 能力，命名、接口和测试必须保持业务无关，并提供至少一个非 Knowledge 复用说明或回归检查。

## 7. 平台通用性验收

PV18-SA 通过前必须完成 platform generality review，至少检查：

- `apps/gateway/service.py` 没有 Knowledge-only runtime shortcut。
- `apps/gateway/connector_execution.py` 没有 Knowledge-only connector execution branch。
- `apps/workflow-console/src/App.tsx` 只做 route/view selection，不把 Knowledge 设为平台默认语义。
- `/bff/pv18/knowledge/*` 是 domain facade，不替代通用 `/bff/*` 分层边界。
- 新增 DTO、runner 和 evidence schema 能证明业务域边界，不污染通用 workflow/run/artifact/trace 语义。

## 8. 架构取舍

PV18 选择复用 existing Knowledge Pack 与 data_service MCP runner，而不是重写业务服务或定制平台内核。理由：

- `packs/knowledge` 已包含 manifest、workflow、agents、skills、artifact schemas 和 evaluation rules。
- `KnowledgeMcpWorkflowRunner` 已覆盖 workspace/source/build/query/quality/correction lifecycle。
- 当前缺口是产品化入口、BFF DTO、验收证据和用户体验，而不是底层 Pack 能力从零实现。

代价是 PV18 仍不证明生产数据服务、商业计费、SLA、完整权限体系或跨租户生产隔离。这些保持在后续阶段。
