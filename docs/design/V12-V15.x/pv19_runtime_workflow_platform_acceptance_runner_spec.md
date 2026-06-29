# PV19 Runtime Workflow Platform Acceptance Runner Spec

用途：定义 PV19 后续自动化验收 runner 的输入、流程和输出证据。
阅读对象：测试、开发、审计人员。
边界：本文是 runner 规格，不是 runner 实现，不产生 PASS 声明。

## 1. Runner Goal

PV19 runner 必须模拟真实用户完成：

```text
open workbench -> edit graph -> validate -> diff -> publish -> run -> handle human gate -> inspect -> evidence review
```

Runner 必须同时采集 browser evidence、BFF route evidence、DTO snapshots、runtime report、human interaction report 和 claim-to-evidence matrix。

## 2. Proposed Entry

```text
tools/pv19/run_runtime_workflow_platform_acceptance.py
apps/workflow-console/e2e/pv19_cdp_acceptance.mjs
apps/workflow-console/e2e/workflow-pv19-runtime-platform.spec.ts
```

## 3. Required Scenarios

| Scenario | Required assertion |
| --- | --- |
| workbench_loads | 工作台可见，非空白根路径。 |
| graph_edit_roundtrip | 节点、边、人工节点可保存和 readback。 |
| workflowdiff_required | publish 前必须有 WorkflowDiff 和用户确认。 |
| version_publish | 发布后可读取 WorkflowVersion。 |
| runtime_run | run 引用 WorkflowVersion 并产生 runtime events。 |
| human_gate | pending human gate 可处理，并改变状态。 |
| evidence_review | evidence summary 有 artifact、trace、audit、claim refs。 |
| browser_boundary | browser 无 direct runtime/store/connector route。 |
| platform_generality | 无业务专用 Core/Gateway/App shell shortcut。 |

## 4. Required Output

Runner 输出至少包括：

- `acceptance-data.json`
- `artifact-manifest.json`
- `workbench-state-report.json`
- `workflow-graph-roundtrip-report.json`
- `workflow-version-publish-report.json`
- `runtime-run-inspect-report.json`
- `human-interaction-report.json`
- `evidence-review-report.json`
- `browser-network-log.json`
- `bff-route-log.json`
- `dto-snapshots.json`
- `claim-to-evidence-matrix.json`
- `no-false-green-scan.txt`
- `redaction-scan.txt`

## 5. Failure Rules

Runner 必须失败于：

- 页面为空但仍继续验收。
- UI 模拟运行但无 runtime report。
- run 没有 workflow_version_id。
- human action 没有 before/after state。
- evidence summary 缺 artifact、trace 或 audit refs。
- 出现 forbidden positive claims。

