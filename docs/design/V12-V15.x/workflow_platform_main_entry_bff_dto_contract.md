# Workflow Platform Main Entry BFF / DTO Contract

用途：定义 WP-M1 到 WP-M4 后续实现必须使用的 BFF、DTO、route allowlist 和兼容策略。
边界：本文是合约文档，不是实现证据；不得据此声明新 route 已实现。

## 1. Contract Strategy

WP-M1 到 WP-M4 不应先发明一套完全独立的工作流平台 API。默认路线是：

```text
Workflow Platform UI
  -> WorkflowConsoleClient typed methods
  -> existing /bff/pv21/* for Studio state, graph, diff, version, run, human, evidence
  -> existing /bff/pv19/* for runtime loop compatibility where PV21 delegates
  -> existing /bff/pv20/* for governed Agent executor evidence and actions
  -> future /bff/workflow-platform/* facade only after compatibility review
```

该策略降低重写风险，并保留 PV19/PV20/PV21 已验收 evidence 的可追踪性。

## 2. Allowed Browser Routes

| Stage | Required route family | Purpose | Required evidence |
| --- | --- | --- | --- |
| WP-M1 | `/bff/pv21/studio/state` | 首入口 state、workspace/project/workflow/run/evidence 摘要。 | `browser-network-log.json`、`dto-snapshot.json`。 |
| WP-M2 | `/bff/pv21/workflows/{workflow_id}/graph` | 画布 nodes/edges/layout read/write 和 validation。 | canvas action log、graph DTO snapshot。 |
| WP-M2 | `/bff/pv21/workflows/{workflow_id}/graph/validate` | 连接规则、缺参、未知节点等负向反馈。 | validation DTO 和失败态截图。 |
| WP-M3 | `/bff/pv21/workflows/{workflow_id}/diff` | WorkflowDiff 审查。 | diff DTO、人工确认记录。 |
| WP-M3 | `/bff/pv21/workflows/{workflow_id}/versions` | 版本列表和 active version。 | version DTO snapshot。 |
| WP-M3 | `/bff/pv21/workflows/{workflow_id}/versions/publish` | 发布 WorkflowVersion。 | publish route log、audit refs。 |
| WP-M3 | `/bff/pv21/workflows/{workflow_id}/versions/{version_id}/rollback` | 回滚 WorkflowVersion。 | rollback route log、audit refs。 |
| WP-M3 | `/bff/pv21/workflows/{workflow_id}/runs` | 启动 WorkflowInstance。 | runtime inspect report。 |
| WP-M3 | `/bff/pv21/runs/{run_id}/inspect` | 运行状态、StationRun、runtime refs。 | inspect DTO snapshot。 |
| WP-M3 | `/bff/pv21/runs/{run_id}/human-actions` | Human gate transition。 | before/after state digest。 |
| WP-M3 | `/bff/pv21/runs/{run_id}/evidence` | Evidence summary。 | evidence panel report。 |
| WP-M4 | `/bff/pv20/agent-executor/state` | 受治理 executor state。 | executor state DTO。 |
| WP-M4 | `/bff/pv20/runs/{run_id}/agent-execution-contract` | AgentExecutionEnvelope read model。 | contract DTO snapshot。 |
| WP-M4 | `/bff/pv20/runs/{run_id}/agent-execution-evidence` | executor evidence summary。 | evidence DTO snapshot。 |
| WP-M4 | `/bff/pv20/runs/{run_id}/agent-skill-executions` | allowlisted skill action。 | approval and action report。 |
| WP-M4 | `/bff/pv20/runs/{run_id}/agent-tool-executions` | allowlisted read-only tool action。 | tool action report。 |
| WP-M4 | `/bff/pv20/runs/{run_id}/agent-mcp-executions` | allowlisted MCP fixture action。 | MCP action report。 |

## 3. Forbidden Browser Routes

Browser E2E network logs must fail if they contain:

- Direct `core/workflows/*` calls.
- Direct Gateway internals.
- Direct runtime store mutation.
- Direct filesystem or artifact content reads outside BFF evidence refs.
- Unscoped MCP/tool invocation outside `/bff/pv20/*` governed routes.

## 4. Minimum DTO Shape

### 4.1 `WorkflowPlatformMainEntryState`

The UI may compose this state from existing PV21/PV20 DTOs. A future facade may return the same shape directly.

```json
{
  "schema_version": "workflow_platform.main_entry.v1",
  "entry": {
    "route": "/",
    "default_studio": "workflow-platform",
    "root_empty_allowed": false,
    "bounded_claim": "workflow_platform_main_entry_candidate"
  },
  "workspace": {
    "workspace_id": "demo-space",
    "label": "Demo Space"
  },
  "workflow": {
    "workflow_id": "pv21_complete_workflow_studio_reference",
    "draft_revision": 1,
    "editable": true,
    "publishable": "requires_validation_and_confirmation",
    "runnable": "requires_published_version"
  },
  "graph": {
    "nodes": [],
    "edges": [],
    "layout": {}
  },
  "run_summary": {
    "active_run_id": null,
    "status": "not_started",
    "human_gate_pending": false
  },
  "evidence_summary": {
    "artifact_refs": [],
    "trace_refs": [],
    "quality_refs": [],
    "audit_refs": [],
    "claim_refs": [],
    "redaction_refs": []
  }
}
```

### 4.2 Canvas Action Log

```json
{
  "schema_version": "workflow_platform.canvas_action_log.v1",
  "stage": "WP-M2",
  "actions": [
    {
      "action_id": "wheel-zoom-001",
      "type": "wheel_zoom",
      "target": "canvas",
      "expected": "viewport_scale_changed",
      "actual": "viewport_scale_changed",
      "status": "PASS",
      "screenshot_ref": "screenshots/wp-m2-wheel-zoom.png"
    }
  ]
}
```

### 4.3 Edge Quality Report

```json
{
  "schema_version": "workflow_platform.edge_quality_report.v1",
  "stage": "WP-M2",
  "checks": [
    {"id": "arrow-visible-first-eye", "status": "PASS"},
    {"id": "right-area-node-drag", "status": "PASS"},
    {"id": "edge-cancel", "status": "PASS"},
    {"id": "edge-no-critical-text-overlap", "status": "PASS"}
  ]
}
```

## 5. Compatibility Rules

- Existing `PV21StudioStateDTO`, `PV21WorkflowGraphDTO`, `PV21WorkflowDiffDTO`, `PV21VersionsDTO`, `PV21RunDTO` and `PV21EvidenceSummaryDTO` remain canonical until a facade is implemented.
- Existing `PV20AgentExecutorStateDTO`, `PV20AgentExecutionContractDTO` and `PV20AgentExecutionEvidenceDTO` remain canonical for governed executor integration.
- A future `/bff/workflow-platform/*` facade must be additive. It cannot remove PV19/PV20/PV21 evidence replay routes.
- UI copy must say “受治理执行” or equivalent bounded wording for Agent/Tool/Skill/MCP actions.

## 6. Contract Exit Criteria

WP-M1 implementation may start only if:

- Route allowlist is referenced by the implementation plan.
- DTO snapshot shape is referenced by the acceptance runner.
- Browser denylist is enforced in E2E.
- No future facade is required before WP-M1.

