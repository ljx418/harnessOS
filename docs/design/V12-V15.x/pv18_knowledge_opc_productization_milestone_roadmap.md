# PV18 Knowledge OPC Productization Milestone Roadmap

用途：定义 PV18 Knowledge OPC 产品化的里程碑、依赖和出门顺序。
阅读对象：项目管理、开发、测试、审计人员。
边界：本文不代表实现已完成；所有 PASS 只能来自对应证据包。

| Milestone | Stage | 用户可见结果 | 代码范围 | Exit Gate |
| --- | --- | --- | --- | --- |
| PV18-R0 | Readiness | 用户和 reviewer 知道 Knowledge OPC 目标、范围、No-Go 和代码实体。 | 文档与 drawio。 | PV18 文档验收 PASS。 |
| PV18-R1 | Contract Readiness | 开发者看到 BFF DTO、runner spec、task matrix 和 schema 草案。 | 文档与 schema。 | schema parse + No False Green PASS。 |
| PV18-E0 | Environment | 开发者能运行 API/CLI/pack smoke 和 Knowledge pack assembly。 | Python env、依赖、测试命令。 | P0 smoke documented PASS 或清晰 BLOCKED。 |
| PV18-S1 | Knowledge Console | 用户看到 Knowledge workspace、source/build/query 状态和 connector health。 | `App.tsx`, planned Knowledge view, `WorkflowConsoleClient`, `bff.py`。 | Console inventory + health evidence PASS。 |
| PV18-S2 | Source Ingest | 用户导入 source 并看到 artifacts、build status 和 lineage。 | `KnowledgeMcpWorkflowRunner`, connector runtime, artifact registry。 | ingest + artifact lineage PASS。 |
| PV18-S3 | Query And Citation | 用户提问并看到 answer、brief、citations 和 source refs。 | `knowledge_query_v2`, `packs/knowledge/workflow.py`。 | citation coverage PASS。 |
| PV18-S4 | Quality And Correction | 用户看到 quality feedback、correction rules 和 correction plan。 | quality/correction MCP tools, quality panel。 | quality gate PASS。 |
| PV18-S5 | Evidence Review | 用户审查 claim、redaction、route boundary、artifact lineage 和 trace refs。 | evidence panel、runner、reports。 | evidence review PASS。 |
| PV18-SA | Aggregate | Reviewer 接受 bounded Knowledge OPC 产品化结论。 | aggregate runner + manifest。 | PV18 bounded review allowed claim PASS。 |

## Dependency Rules

- PV18-R0/R1 只做文档；不得进入代码实现。
- PV18-E0 是实现前置；环境无法恢复时不能用文档替代功能 PASS。
- PV18-S2 必须先有 source/reference artifact，再进入 query 和 citation 验收。
- PV18-S3 不能在 citation bundle 缺失时进入质量验收。
- PV18-S4 的 correction plan 必须是人工审查建议，不能自动发布或改写知识库。
- PV18-S5 不能在 redaction、route denylist 或 No False Green 失败时进入 PV18-SA。
- PV18-SA 不能升级成 production、complete business product、complete Studio、Agent executor 或 Xpert parity 声明。

## Recommended Sequence

1. 完成本轮 PV18 文档、drawio、BFF DTO 合同、runner spec、task matrix 和 schema 草案。
2. 重跑或记录 API/CLI/pack smoke，尤其是 Knowledge pack assembly。
3. 实现 PV18-S1/S2，让 Knowledge workspace 和 source ingest 进入显式 `?studio=pv18-knowledge-opc` 入口。
4. 实现 PV18-S3/S4，让 query/citation/quality/correction 成为一条可审查业务流。
5. 实现 PV18-S5/SA，用证据包和 runner 收口。
