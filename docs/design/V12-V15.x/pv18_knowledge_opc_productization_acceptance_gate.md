# PV18 Knowledge OPC Productization Acceptance Gate

用途：定义 PV18 Knowledge OPC 产品化的文档阶段、实现阶段和阶段性复验门槛。
阅读对象：测试、审计、开发、产品人员。
边界：本文定义 gate；不把 PV18 扩大为生产可用、完整 Knowledge 产品或完整 Agent executor。

## 1. 文档阶段 Gate

本轮文档开发必须满足：

- PV18 PRD、目标架构、开发及验收计划、里程碑、验收门槛、gap 分析、implementation readiness audit 和 drawio 均存在。
- PV18 BFF DTO contract、acceptance runner spec、implementation task matrix 和 schema 草案均存在。
- 每份 Markdown 顶部说明用途、阅读对象和边界。
- drawio 页数不超过 8 页，使用中文，包含颜色图例和具体代码实体。
- 文档明确 Knowledge 是本阶段唯一业务域。
- 文档明确 `packs/knowledge` 是 reference pack baseline，不是最终产品完成声明。
- 文档明确 Knowledge OPC 不能驱动 workflow platform 做业务专用定制；平台层新增能力必须保持业务无关和可复用。
- 文档不能把 docs、drawio、截图或介绍页描述为 runtime / BFF / DTO / browser E2E / production evidence。

## 2. 实现 Gate

| Scenario | PASS 条件 | Blocking Failure |
| --- | --- | --- |
| Knowledge Console | 用户能看到 workspace、scope、connector health、source/build/query 概览。 | UI 不能说明当前 Knowledge 上下文或 connector 状态。 |
| Source Ingest | source/document 经 BFF DTO 进入 Knowledge workflow，产出 source_reference 和 note artifacts。 | 直接调用 connector runtime，或没有 artifact id / lineage。 |
| Build Status | 用户能看到 build started/running/completed/failed 和失败原因。 | build 状态缺失但 UI 显示成功。 |
| Query And Citation | answer / brief 必须带 citation bundle、source refs 和 coverage 状态。 | 无 citation 仍展示为已验证答案。 |
| Quality Review | quality feedback、correction rules、correction plan 可见，且需人工审查。 | correction plan 自动发布或静默改写知识库。 |
| Evidence Review | 用户看到 artifact lineage、trace refs、route boundary、redaction 和 claim-to-evidence。 | claim scan 或 redaction scan FAIL。 |
| Browser Boundary | browser network log 只包含 allowlist route。 | 出现 `/v1/rpc`、connector runtime、internal runtime/store 或 data_service MCP internal route。 |
| Contract Boundary | planned route、schema 草案和 runner spec 只作为实现目标。 | 把 planned contract 写成已实现 evidence。 |
| Platform Generality | Knowledge 只存在于 pack/domain BFF/view/runner 边界内，平台层保持通用 workflow/run/artifact/trace/evidence 抽象。 | workflow core、Gateway core、connector runtime、artifact/trace store 或 App shell 出现 Knowledge-only 特例、快捷通道、默认语义或不可复用接口。 |

## 3. Required Artifacts For PV18-SA

PV18-SA 至少需要：

- browser screenshots and action logs;
- BFF route log and browser network log;
- DTO snapshots and schema validation;
- source ingest report;
- query and citation report;
- quality and correction report;
- artifact lineage report;
- trace refs and artifact refs;
- claim-to-evidence matrix;
- No False Green scan;
- redaction scan;
- PRD review;
- target architecture review;
- platform generality review;
- audit closure.
- schema validation report.

## 4. Forbidden Positive Claims

以下声明只能出现在明确否定、禁止、风险或 No-Go 语境中：

- HarnessOS is production ready.
- Xpert parity complete.
- product-grade frontend complete.
- complete Workflow Studio ready.
- Agent executor ready.
- Knowledge productization complete.
- production data service ready.

## 5. Current Exit

本轮文档阶段允许出门条件：

```text
PV18 Knowledge OPC productization development plan ready for implementation review.
```

该条件只说明文档可进入实现评审，不说明任何功能已经实现。
