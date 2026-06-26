# PV18 Knowledge OPC Productization Development And Acceptance Plan

用途：把 PV18 Knowledge OPC 产品化拆成可执行开发与验收阶段。
阅读对象：开发、测试、产品、审计人员。
边界：本文是开发及验收计划；在实际代码和证据生成前，不产生任何 PASS 声明。

## 1. Stage Outline

| Stage | 用户可见效果 | 开发对象 | 验收证据 |
| --- | --- | --- | --- |
| PV18-R0 | Reviewer 看到 Knowledge OPC 已选、范围、代码实体、No-Go 和 drawio。 | 文档、drawio、索引、stage gate。 | 文档存在性、drawio 页数、No False Green 扫描。 |
| PV18-S1 | 用户打开 Knowledge Console，看到 workspace、scope、connector health 和已有 source/build/query 状态。 | `App.tsx`, planned Knowledge view, `WorkflowConsoleClient`, `bff.py`。 | browser screenshot、DTO snapshot、BFF route log。 |
| PV18-S2 | 用户导入 source/document，并看到 source_reference、note、artifact id 和 build status。 | BFF source import DTO、`KnowledgeMcpWorkflowRunner`, connector runtime。 | source ingest report、artifact lineage、negative fixtures。 |
| PV18-S3 | 用户发起 query，看到 answer、brief、citation bundle 和 citation coverage。 | `knowledge_query_v2`, artifact registry, trace store。 | query report、citation bundle、redaction scan。 |
| PV18-S4 | 用户执行 quality feedback，看到质量结果、correction rules 和 correction plan。 | `knowledge_quality_feedback_v2`, `knowledge_correction_plan_v2`。 | quality report、correction plan、claim scan。 |
| PV18-S5 | 用户在 Evidence 视图审查 artifact lineage、trace refs、route boundary、redaction 和 claim-to-evidence。 | evidence panel、acceptance runner。 | evidence review report、network denylist、claim matrix。 |
| PV18-SA | Reviewer 接受一个 bounded Knowledge OPC 产品化实现结论。 | aggregate runner、artifact manifest、audit closure。 | acceptance-data、artifact-manifest、audit closure、allowed claim。 |

## 2. 入口前置条件

PV18 实现不能开始，直到：

- 本轮 PV18 PRD、目标架构、开发计划、里程碑、验收门槛、gap 分析、readiness audit 和 drawio 存在。
- `pv18_knowledge_opc_productization_bff_dto_contract.md`、`pv18_knowledge_opc_productization_acceptance_runner_spec.md`、`pv18_knowledge_opc_productization_implementation_task_matrix.md` 已存在并纳入实现计划。
- `schemas/pv18_knowledge_opc_acceptance_data.schema.json`、`schemas/pv18_knowledge_opc_artifact_manifest.schema.json`、`schemas/pv18_knowledge_opc_dto_snapshot.schema.json` 可解析。
- 文档明确 PV18 只选择 Knowledge，不把 Meeting / Video / Interview / Investment 混入本阶段。
- 现有 `packs/knowledge`、`KnowledgeMcpWorkflowRunner`、connector runtime、artifact registry 和 trace store 已读并映射到目标架构。
- 已读并接受平台通用性红线：Knowledge OPC 是业务样本，不能驱动 workflow platform 做 Knowledge-only core/runtime/Gateway/App shell 定制。
- No False Green 扫描通过。
- 后续实现计划不得回滚已存在的 PV17 bounded review 证据或当前前端入口修复。

## 3. Evidence Package Proposal

后续实现证据建议落在：

```text
docs/design/V12-V15.x/evidence/pv18-knowledge-opc-productization/
```

最低文件：

- `acceptance-data.json`
- `artifact-manifest.json`
- `knowledge-console-report.json`
- `source-ingest-report.json`
- `knowledge-query-report.json`
- `quality-correction-report.json`
- `evidence-review-report.json`
- `browser-network-log.json`
- `bff-route-log.json`
- `dto-snapshots.json`
- `artifact-lineage-report.json`
- `claim-to-evidence-matrix.json`
- `knowledge-console-screenshot.png`
- `query-and-citation-screenshot.png`
- `evidence-review-screenshot.png`
- `prd-spec-review.md`
- `target-architecture-review.md`
- `platform-generality-review.md`
- `audit-closure.md`
- `no-false-green-scan.txt`
- `redaction-scan.txt`

Future runner/report names:

- `tools/pv18/run_knowledge_opc_e2e.py`
- `tools/pv18/run_knowledge_opc_acceptance.py`
- `docs/design/V12-V15.x/reports/pv18_knowledge_opc_productization_acceptance_report.json`

## 4. Required Negative Fixtures

后续实现至少需要以下负向验收：

- `missing_citation_blocks_verified_answer`
- `build_failed_is_visible`
- `connector_approval_required_is_visible`
- `correction_plan_auto_publish_denied`
- `browser_direct_rpc_denied`
- `connector_runtime_direct_route_denied`
- `knowledge_only_platform_customization_denied`
- `raw_secret_redaction_required`
- `artifact_lineage_missing_blocks_pass`

## 5. 验收阻断条件

- Browser 直连 connector runtime、`/v1/rpc`、internal runtime/store 或 data_service MCP internals。
- Knowledge answer 没有 citation bundle 却被展示为已验证结论。
- Correction plan 静默改写知识库或绕过人工审查。
- Artifact lineage、trace refs 或 source refs 为空，但 UI 仍显示成功。
- BFF DTO 无法证明 scope、workspace、source、query、artifact 和 evidence 的对应关系。
- 为了 Knowledge OPC 在 workflow core、Gateway core、connector runtime、artifact registry、trace store 或 App shell 中加入 Knowledge-only 特例、枚举、快捷通道或默认语义。
- 新增平台能力不能说明业务无关抽象和至少一个非 Knowledge 复用路径。
- raw secret、raw provider payload、raw artifact content 出现在 UI、日志或证据包。
- planned route、schema 草案或 runner spec 被当作已实现 evidence。
- 文档或 UI 把 PV18 说成 production ready、Knowledge 产品化已完成、完整 Workflow Studio、Agent executor 或 Xpert parity。

## 6. 允许的实现后声明

PV18 实现完成前不允许新的完成声明。后续如果 PV18-SA 证据通过，建议只允许：

```text
PV18 complete: Knowledge OPC productization implementation ready for bounded review.
```

该声明仍不等于生产可用、完整业务产品、完整数据服务、完整 Workflow Studio 或 Agent executor ready。
