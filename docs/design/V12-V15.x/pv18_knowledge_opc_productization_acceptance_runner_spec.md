# PV18 Knowledge OPC Productization Acceptance Runner Spec

用途：定义 PV18 后续自动化验收 runner 的输入、输出、判定规则和阻断条件。
阅读对象：测试、开发、审计人员。
边界：本文是 planned runner spec，不是 runner 实现；不得把本文当作自动化验收 PASS。

## 1. Planned Runner

建议后续实现：

```text
tools/pv18/run_knowledge_opc_e2e.py
tools/pv18/run_knowledge_opc_acceptance.py
```

报告输出：

```text
docs/design/V12-V15.x/reports/pv18_knowledge_opc_productization_acceptance_report.json
docs/design/V12-V15.x/evidence/pv18-knowledge-opc-productization/
```

## 2. Required Scenario Results

| Stage | Required case | PASS rule |
| --- | --- | --- |
| PV18-S1 | `knowledge_console_state_visible` | workspace、scope、connector health、evidence summary 非空。 |
| PV18-S2 | `source_import_registers_standard_artifacts` | `source_reference`、`note` artifact refs 存在，lineage 可追踪。 |
| PV18-S2 | `build_failed_is_visible` | failed build 必须有 `failure_reason` 和 `next_actions`。 |
| PV18-S3 | `query_returns_citation_bundle` | answer、brief、citation_bundle、source_refs 非空。 |
| PV18-S3 | `missing_citation_blocks_verified_answer` | citation 缺失时不能出现 verified/success completion claim。 |
| PV18-S4 | `quality_feedback_requires_review_when_risky` | quality issue 或 low signal source 必须进入 pending/review 状态。 |
| PV18-S4 | `correction_plan_does_not_auto_publish` | `auto_publish_allowed=false` 且显示人工审查。 |
| PV18-S5 | `evidence_summary_maps_claims_to_artifacts` | 每个 allowed claim 都有 artifact/trace/route evidence。 |
| PV18-S5 | `browser_network_denylist_passes` | 不出现 `/v1/rpc`、connector runtime、internal runtime/store。 |
| PV18-S5 | `platform_generality_review_passes` | Knowledge-specific code 只在 pack/domain BFF/view/runner 边界内，平台层无 Knowledge-only 定制。 |
| PV18-SA | `no_false_green_and_redaction_pass` | claim scan 和 redaction scan 均 PASS。 |

## 3. Required Evidence Files

后续 runner 至少写入：

- `acceptance-data.json`
- `artifact-manifest.json`
- `dto-snapshots.json`
- `knowledge-console-report.json`
- `source-ingest-report.json`
- `knowledge-query-report.json`
- `quality-correction-report.json`
- `artifact-lineage-report.json`
- `evidence-review-report.json`
- `browser-network-log.json`
- `bff-route-log.json`
- `claim-to-evidence-matrix.json`
- `no-false-green-scan.txt`
- `redaction-scan.txt`
- `prd-spec-review.md`
- `target-architecture-review.md`
- `platform-generality-review.md`
- `audit-closure.md`

## 4. Acceptance Data Shape

`acceptance-data.json` 必须包含：

```text
schema_version
stage_id
status
allowed_claim
scenario_results[]
artifact_refs[]
route_boundary
platform_generality_review
redaction_scan
claim_scan
blocking_failures[]
```

`status=PASS` 的必要条件：

- `blocking_failures` 为空。
- 所有 required scenario `status=PASS`。
- schema validation PASS。
- route denylist PASS。
- platform generality review PASS。
- No False Green PASS。
- redaction PASS。

## 5. Forbidden Claim Scan

以下文本只能出现在否定、禁止、风险或 No-Go 语境：

- `production ready`
- `HarnessOS is production ready`
- `Xpert parity complete`
- `product-grade frontend complete`
- `complete Workflow Studio ready`
- `Agent executor ready`
- `Knowledge productization complete`
- `production data service ready`

## 6. Stop Conditions

runner 必须 FAIL 的情况：

- 使用 docs/drawio/screenshot 替代 runtime/BFF/browser evidence。
- Browser 直连 connector runtime、data_service MCP internals 或 `/v1/rpc`。
- workflow core、Gateway core、connector runtime、artifact registry、trace store 或 App shell 中出现 Knowledge-only 特例、快捷通道、默认语义或不可泛化接口。
- 新增平台接口无法说明业务无关抽象，且无法给出非 Knowledge 复用检查。
- query answer 无 citation bundle 但 UI/报告声称 verified。
- correction plan 自动发布、自动改写知识库或绕过人工审查。
- artifact lineage 或 trace refs 为空但报告 PASS。
- raw secret、raw provider payload、raw connector payload、raw artifact content 泄漏。
