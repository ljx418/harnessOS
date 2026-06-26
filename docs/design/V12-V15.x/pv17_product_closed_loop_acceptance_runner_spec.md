# PV17 Product Closed Loop Acceptance Runner Spec

用途：定义后续 PV17 自动验收 runner 必须检查什么、如何失败、输出什么。
阅读对象：测试、开发 Agent、审计人员。
边界：本文是 runner 规格，不是 runner 实现；PV16 `/bff/pv16/*` 来自 test-only BFF evidence route，PV17 只能把它作为参考，不能把它当作正式产品 API。

## 1. Future Commands

建议后续实现以下命令：

```text
python3 tools/pv17/run_product_closed_loop_e2e.py
python3 tools/pv17/run_product_closed_loop_acceptance.py
```

当前文档阶段不创建工具实现。实现工具前必须先通过 `pv17_product_closed_loop_implementation_readiness_audit.md`。

## 2. Evidence Directory

默认证据目录：

```text
docs/design/V12-V15.x/evidence/pv17-product-closed-loop/
```

## 3. Required Files

Runner 必须要求以下文件存在：

- `acceptance-data.json`
- `artifact-manifest.json`
- `product-console-report.json`
- `entity-mutation-report.json`
- `studio-workflow-version-report.json`
- `runtime-run-inspect-report.json`
- `evidence-review-report.json`
- `browser-network-log.json`
- `bff-route-log.json`
- `dto-snapshots.json`
- `claim-to-evidence-matrix.json`
- `product-console-screenshot.png`
- `studio-run-inspect-screenshot.png`
- `evidence-review-screenshot.png`
- `prd-spec-review.md`
- `target-architecture-review.md`
- `audit-closure.md`
- `no-false-green-scan.txt`
- `redaction-scan.txt`

## 4. Required Stage Results

`acceptance-data.json` must include PASS entries for:

- `PV17-S1-product-console`
- `PV17-S2-entity-mutation`
- `PV17-S3-studio-versioning`
- `PV17-S4-runtime-inspect`
- `PV17-S5-evidence-review`
- `PV17-SA-aggregate`

Each stage result must include `user_visible_result`, `evidence_refs` and `blocking_failures`.

## 5. Fail Conditions

Runner must fail when any condition is true:

- required file missing;
- schema validation fails;
- any required stage missing or not PASS;
- browser network log contains `/v1/rpc`, `/internal/runtime`, `/runtime/store`, `/api/runtime` or `/debug/runtime`;
- BFF route log uses `/bff/pv16/*` as the PV17 positive path;
- DTO snapshots are missing for S1-S5;
- entity mutation report lacks `user_confirmed=true`, `audit_ref`, policy decision or denial fixture;
- Studio versioning report lacks WorkflowDiff before/after, expected revision or confirmation transcript;
- runtime inspect report lacks non-empty runtime event refs, trace refs, artifact refs or quality refs;
- evidence review report lacks claim-to-evidence matrix;
- No False Green scan finds a forbidden positive claim outside safe negative context;
- redaction scan finds raw secret, raw provider payload or raw artifact content;
- allowed claim differs from the approved PV17 bounded wording.

## 6. Forbidden Positive Claims

Runner must scan at least:

- `production ready`
- `HarnessOS is production ready`
- `Xpert parity complete`
- `product-grade frontend complete`
- `complete Workflow Studio ready`
- `Agent executor ready`

Allowed contexts are only headings or sentences that explicitly say do not claim, not equal to, forbidden, No-Go, blocked or cannot prove.

## 7. Report Shape

`reports/pv17_product_closed_loop_acceptance_report.json` should include:

- `schema_version`
- `status`
- `stage_id`
- `evidence_dir`
- `missing_artifacts`
- `schema_results`
- `stage_results`
- `browser_boundary`
- `bff_boundary`
- `dto_coverage`
- `runtime_evidence`
- `claim_to_evidence`
- `claim_scan`
- `redaction_scan`
- `allowed_claim`
- `forbidden_positive_claims`

## 8. Allowed Claim After PASS

If and only if PV17-SA passes, the runner may emit:

```text
PV17 complete: product closed loop implementation ready for bounded review.
```

This still does not mean production ready, Xpert parity complete, product-grade frontend complete, complete Workflow Studio ready or Agent executor ready.
