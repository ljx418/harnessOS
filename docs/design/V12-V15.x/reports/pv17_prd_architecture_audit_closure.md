# PV17 PRD Architecture Audit Closure

用途：记录 PV17 本轮 PRD 规格检视、目标架构检视和审计闭环。
阅读对象：项目负责人、开发 Agent、测试、产品、审计人员。
边界：本文是审计意见摘要；最终通过状态必须以 evidence package 和 acceptance runner 输出为准。

## 1. Audit Result

```text
stage=PV17-SA
prd_spec_review=PASS
target_architecture_review=PASS
fatal_findings=0
major_findings=0
acceptance_runner=PASS
```

## 2. PRD Coverage

| PRD requirement | Audit conclusion |
| --- | --- |
| Product Console 可见当前 workspace/project/app/workflow/Station Agent/system health。 | PASS：由 `product-console-report.json`、DTO snapshots 和 browser screenshot 支撑。 |
| durable mutation 必须通过正式 BFF DTO，且需要用户确认。 | PASS：`entity-mutation-report.json` 含 accepted mutation、policy decision、audit ref 和 denial fixture。 |
| Mission Studio 必须保持 patch/publish/run 上下文连续。 | PASS：页面新增 patch/publish 用户动作，`studio-workflow-version-report.json` 记录 WorkflowDiff 和 WorkflowVersion。 |
| Runtime Inspect 必须展示 runtime/trace/artifact/quality/approval refs。 | PASS：`runtime-run-inspect-report.json` 非空 refs 通过 runner 校验。 |
| Evidence Review 必须能审查 claim-to-evidence、route boundary、redaction 和 lineage。 | PASS：`evidence-review-report.json`、`claim-to-evidence-matrix.json` 和 scans 均通过。 |
| Browser 不能直连 internal runtime/store。 | PASS：`browser-network-log.json` denylist scan 通过。 |

## 3. Architecture Coverage

本轮实现链路为：

```text
Browser PV17 page
  -> WorkflowConsoleClient with explicit PV17 scope
  -> /bff/pv17/* formal routes
  -> GatewayService
  -> workflow repository / runtime stores / trace / artifact / approval / quality stores
  -> evidence package / acceptance runner
```

关键边界：

- Browser 只使用 `/bff/pv17/*` 正式路径。
- PV16 test-only BFF 没有作为 PV17 正向证据。
- Product entity mutation 不直接写 runtime truth。
- Evidence Review 仅读取 refs，不构造 runtime truth。

## 4. Closed Findings

| Finding | Severity | Closure |
| --- | --- | --- |
| PV17 页面缺少 Studio patch/publish 用户动作。 | Major | 已补齐 `提出 Patch` 和 `发布版本` 操作，并进入 browser E2E。 |
| PV17 E2E 缺少正式 BFF seed server。 | Major | 已新增 `tools/pv17/formal_bff_server.py` 和 `tools/pv17/reference_seed.py`。 |
| Browser scope 与 seeded Gateway scope 不一致。 | Major | 已在 PV17 client 和 E2E direct validation 中显式传递 `reference_app/demo_a/local` scope。 |
| preview origin 被 auth guard 拒绝。 | Major | 已改用本地白名单 origin `127.0.0.1:5173`。 |
| redaction scan 把 DTO 字段名误判为敏感载荷泄漏。 | Major | 已把 redaction DTO 字段命名改为不含 raw 前缀的安全字段名。 |

## 5. Residual Risk

| Risk | Level | Disposition |
| --- | --- | --- |
| Frontend bundle size warning。 | Low | Vite build PASS；该 warning 不影响 PV17 bounded review。 |
| Chrome/CDP 本地依赖。 | Medium | `run_product_closed_loop_e2e.py` 明确要求 Chrome/Chromium；缺失时应视为验收环境阻塞，而不是功能 PASS。 |
| PV17 仍是 bounded review，不是生产治理完成。 | Medium | No-Go 文案和 runner forbidden claim scan 继续保留。 |

## 6. Audit Opinion

PV17 本轮文档、代码、真实浏览器证据和 acceptance runner 已形成闭环。当前可以进入 bounded review，但不能升级为生产可用、完整 Workflow Studio、Agent executor ready 或 Xpert parity 声明。
