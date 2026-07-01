# Workflow Platform Main Entry BFF / DTO Contract

用途：定义 WP-M1 到 WP-M11 使用的 BFF、DTO、route allowlist 和兼容策略，并记录本阶段 route ownership 结果。
边界：本文是合约和验收记录，不证明生产级 API、完整平台 GA 或生产可用。

## 1. Contract Strategy

WP-M1 到 WP-M4 不应先发明一套完全独立的工作流平台 API。默认路线是先让 PV13 基线页面成为首页，再逐步集成已有 route families。WP-M5A 已新增 additive scenario projection / business output contract，且不得破坏 V13/PV20/PV21 evidence replay routes。

WP-M6 到 WP-M11 的合约策略是：优先复用现有 `/bff/v13/*`、`/bff/pv19/*`、`/bff/pv20/*`、`/bff/pv21/*` 和 `/bff/workflow-platform/*` route families；只有当 PV13 工作台无法形成连续用户路径时，才新增 additive `/bff/workflow-platform/*` facade。新增 facade 必须保持 typed DTO、readback、audit refs 和 evidence refs，不得让 browser 绕过 BFF 直接调用 store/runtime。

当前 route ownership 结论：WP-M1A 已在主 API router `apps/api/routers/bff.py` 中恢复正式 `/bff/v13/*` compatibility routes，并由 `tests/test_v13_workflow_platform_bff.py` 与 Chrome CDP browser network log 验证。历史 `apps/workflow-console/e2e/bff_smoke_server.py` 仍可作为 E2E harness 的 bounded fixture，但本阶段不再依赖 smoke-server-only route ownership。

```text
PV13-based Workflow Platform UI
  -> WorkflowConsoleClient typed methods
  -> required /bff/v13/* compatibility for PV13 graph, inspector, WorkflowDiff pilot and health
  -> existing /bff/pv19/* for runtime loop compatibility where PV21 delegates
  -> existing /bff/pv20/* for governed Agent executor evidence and actions
  -> existing /bff/pv21/* for graph/version/run/evidence candidate compatibility where useful
  -> implemented /bff/workflow-platform/* scenario projection and business output DTOs
  -> future broader /bff/workflow-platform/* facade only after compatibility review
```

该策略降低重写风险，并保留 V13/PV19/PV20/PV21 已验收 evidence 的可追踪性。

`WorkflowPlatformMainEntry` 不再是目标首页视觉 shell，但它是当前 PV21/PV20 能力接入事实的对照来源。WP-M3/WP-M4 必须通过 `WorkflowConsoleClient` 或同等 typed client 复用既有 PV21/PV20 route families，不能在 PV13 组件里绕过 BFF 或直接调用 runtime/store。

## 2. Allowed Browser Routes

| Stage | Required route family | Purpose | Required evidence |
| --- | --- | --- | --- |
| WP-M1A | `/bff/v13/system/health` | PV13 compatibility route 存在性和边界确认；若主 BFF 缺失，必须先恢复或明确使用 bounded smoke BFF。 | route existence smoke、`browser-network-log.json`、health snapshot。 |
| WP-M1A | `/bff/v13/workflows/{workflow_id}/graph` | PV13 首页 graph / workspace / baseline state。 | route existence smoke、`dto-snapshot.json`、PV13 screenshot。 |
| WP-M2 | `/bff/v13/workflows/{workflow_id}/graph` | PV13 画布 nodes/edges/layout read/write。 | canvas action log、graph DTO snapshot。 |
| WP-M2 | `/bff/v13/workflows/{workflow_id}/graph/validate` | 连接规则、缺参、未知节点等负向反馈。 | validation DTO 和失败态截图。 |
| WP-M2 | `/bff/v13/studio/node-inspector/{node_id}` | PV13 Inspector 联动。 | inspector DTO 和截图。 |
| WP-M3 | `/bff/v13/workflows/{workflow_id}/diff` | PV13 WorkflowDiff pilot 审查。 | diff DTO、人工确认记录。 |
| WP-M3 | `/bff/v13/workflow-diff/{diff_id}/revise` | Diff revise action。 | route log、action report。 |
| WP-M3 | `/bff/v13/workflow-diff/{diff_id}/reject` | Diff reject action。 | route log、action report。 |
| WP-M3 | `/bff/v13/workflow-diff/{diff_id}/confirm-publish-handoff` | Diff confirmation handoff。 | confirmation transcript。 |
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
| WP-M5A | `/bff/workflow-platform/scenarios` | 场景目录、输入要求、节点模板、Inspector/timeline projection。 | `scenario-projection-report.json`、DTO snapshot、frontend mock reduction scan。 |
| WP-M5A | `/bff/workflow-platform/scenarios/{scenario_id}/outputs` | 文档总结、代码审查、会议整理的业务输出摘要和 artifact refs。 | `business-output-report.json`、artifact refs、human review refs。 |
| WP-M6 | `/bff/workflow-platform/state` or composed existing routes | PV13 正常路径首页状态、场景、图、Inspector、timeline、quality、evidence、chat 初始上下文。 | `frontend-data-source-closure-report.json`、DTO snapshot、network log。 |
| WP-M6 | `/bff/workflow-platform/fallback-status` | 显式返回 fallback 使用状态和原因，避免静态数据被误写成真实投影。 | fallback boundary screenshot、mock scan。 |
| WP-M7 | `/bff/workflow-platform/workflows/{workflow_id}/graph` or `/bff/pv21/workflows/{workflow_id}/graph` | WorkflowSpecGraph read/save/readback。 | before/after DTO、refresh readback report。 |
| WP-M7 | `/bff/workflow-platform/workflows/{workflow_id}/graph/validate` or existing validate route | 图校验、非法连接、缺参、未知节点反馈。 | validation DTO、failure screenshot。 |
| WP-M7 | `/bff/workflow-platform/workflows/{workflow_id}/diff` or existing diff route | 基于后端保存状态生成 WorkflowDiff。 | Diff DTO、human review log。 |
| WP-M8 | `/bff/workflow-platform/workflows/{workflow_id}/versions/publish` or existing PV21 route | 发布 WorkflowVersion。 | version DTO、audit refs。 |
| WP-M8 | `/bff/workflow-platform/workflows/{workflow_id}/runs` or existing PV21/PV19 route | 启动 WorkflowInstance。 | run DTO、StationRun readback。 |
| WP-M8 | `/bff/workflow-platform/runs/{run_id}/human-actions` or existing PV21 route | Human Gate approve/reject。 | before/after state digest。 |
| WP-M8 | `/bff/workflow-platform/runs/{run_id}/evidence` or existing PV21 route | Evidence Review 聚合。 | evidence panel report。 |
| WP-M9 | `/bff/workflow-platform/scenarios/{scenario_id}/artifacts` | 三业务场景产物 manifest、content summary、input hash 和 refs。 | `business-artifact-manifest.json`、content snapshot。 |
| WP-M10 | `/bff/workflow-platform/quality/failure-fixtures` | 加载、空、错误、权限拒绝、BFF 离线、校验失败、人工拒绝、取消/重试等可验收 fixture。 | failure-state report、screenshots。 |
| WP-M11 | `/bff/workflow-platform/audit/claims` or generated offline evidence | PRD claim-to-evidence matrix source。 | aggregate audit、No False Green scan。 |

## 2.1 Implemented V13 Compatibility Routes

```text
GET  /bff/v13/system/health
GET  /bff/v13/workflows/{workflow_id}/graph
POST /bff/v13/workflows/{workflow_id}/graph/validate
POST /bff/v13/workflows/{workflow_id}/diff
POST /bff/v13/workflow-diff/{proposal_id}/revise
POST /bff/v13/workflow-diff/{proposal_id}/reject
POST /bff/v13/workflow-diff/{proposal_id}/confirm-publish-handoff
GET  /bff/v13/studio/node-inspector/{node_id}
```

这些 routes 的边界是 PV13 compatibility / handoff-only。它们明确返回 `runtime_backed=false` 或 `publish_or_run_started=false`，不能被解释为真实发布运行路径；真实 bounded runtime parity 仍通过 `/bff/pv21/*` 验证。

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
    "frontend_baseline": "v13-editable-studio",
    "baseline_component": "V13EditableStudio",
    "root_empty_allowed": false,
    "bounded_claim": "workflow_platform_main_entry_candidate"
  },
  "workspace": {
    "workspace_id": "demo-space",
    "label": "Demo Space"
  },
  "workflow": {
    "workflow_id": "wf-v13-markdown-summary-studio-pilot",
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

### 4.4 `WorkflowPlatformScenarioProjectionDTO`

This DTO is the WP-M5A accepted contract for replacing business-critical local `scenarioData` rendering. It is currently returned by the additive `/bff/workflow-platform/scenarios` route; a future broader facade must remain additive.

```json
{
  "schema_version": "workflow_platform.scenario_projection.v1",
  "source": "bff_projection",
  "fallback_used": false,
  "scenarios": [
    {
      "scenario_id": "document_summary",
      "title": "文档/知识总结",
      "input_contract": {
        "accepted_inputs": ["markdown_folder", "document_set"],
        "required_refs": ["source_refs"]
      },
      "workflow_template": {
        "node_refs": ["input", "parse", "extract", "summarize", "quality", "evidence"],
        "edge_refs": []
      },
      "inspector_projection": {
        "agent_refs": [],
        "tool_refs": [],
        "skill_refs": [],
        "mcp_refs": [],
        "quality_gate_refs": []
      },
      "evidence_categories": ["artifact", "trace", "quality", "audit", "claim", "redaction"]
    }
  ]
}
```

### 4.5 `WorkflowPlatformBusinessOutputDTO`

```json
{
  "schema_version": "workflow_platform.business_output.v1",
  "scenario_id": "document_summary",
  "status": "ready_for_human_review",
  "output_summary": {
    "title": "摘要产物",
    "artifact_refs": [],
    "human_review_ref": "review://...",
    "quality_status": "PASS"
  },
  "evidence_refs": {
    "artifact": [],
    "trace": [],
    "quality": [],
    "audit": [],
    "claim": [],
    "redaction": []
  },
  "non_claims": [
    "not_production_ready",
    "not_complete_workflow_studio_ga"
  ]
}
```

### 4.6 `WorkflowPlatformDataSourceClosureDTO`

```json
{
  "schema_version": "workflow_platform.data_source_closure.v1",
  "stage": "WP-M6",
  "normal_path_static_sources": 0,
  "regions": [
    {
      "region_id": "canvas",
      "source": "bff_dto",
      "route": "/bff/workflow-platform/state",
      "fallback_allowed": true,
      "fallback_visible_to_user": true
    }
  ],
  "blocked_static_sources": [
    "scenarioData",
    "fallbackGraph",
    "static_timeline",
    "static_inspector",
    "proposal_only_chat"
  ]
}
```

### 4.7 `WorkflowPlatformGraphMutationDTO`

```json
{
  "schema_version": "workflow_platform.graph_mutation.v1",
  "workflow_id": "wf-v13-markdown-summary-studio-pilot",
  "base_revision": 3,
  "mutation": {
    "nodes_upserted": [],
    "nodes_deleted": [],
    "edges_upserted": [],
    "edges_deleted": [],
    "node_config_updates": []
  },
  "requires_validation": true,
  "requires_human_diff_review": true
}
```

### 4.8 `WorkflowPlatformArtifactClosureDTO`

```json
{
  "schema_version": "workflow_platform.artifact_closure.v1",
  "scenario_id": "document_summary",
  "input_hash": "sha256:...",
  "artifact_ref": "artifact://...",
  "content_snapshot_ref": "artifact://...",
  "quality_refs": [],
  "human_review_refs": [],
  "redaction_refs": [],
  "claim_refs": []
}
```

### 4.9 `WorkflowPlatformQualityStateDTO`

```json
{
  "schema_version": "workflow_platform.quality_state.v1",
  "state_id": "bff_offline",
  "user_visible_message": "BFF 暂不可用，当前显示离线 fallback。",
  "recoverable": true,
  "allowed_actions": ["retry", "view_cached_refs"],
  "evidence_ref": "screenshot://wp-m10-bff-offline.png"
}
```

## 5. Compatibility Rules

- Existing V13 graph, validation, inspector and WorkflowDiff DTO shapes remain canonical for WP-M1/WP-M2 baseline homepage and canvas work.
- Existing `PV21StudioStateDTO`, `PV21WorkflowGraphDTO`, `PV21WorkflowDiffDTO`, `PV21VersionsDTO`, `PV21RunDTO` and `PV21EvidenceSummaryDTO` remain canonical for later runtime/evidence convergence until a facade is implemented.
- Existing `PV20AgentExecutorStateDTO`, `PV20AgentExecutionContractDTO` and `PV20AgentExecutionEvidenceDTO` remain canonical for governed executor integration.
- WP-M5A scenario projection and business output DTOs are additive. They may compose existing PV18/PV19/PV20/PV21 data, but the UI must expose whether `fallback_used=true`.
- A future `/bff/workflow-platform/*` facade must be additive. It cannot remove V13/PV19/PV20/PV21 evidence replay routes.
- UI copy must say “受治理执行” or equivalent bounded wording for Agent/Tool/Skill/MCP actions.
- Capability parity is required: if a PV21/PV20 capability is currently reachable from `WorkflowPlatformMainEntry`, the PV13-based target must either expose it with matching BFF evidence or mark it as deferred/No-Go with user confirmation. Silent removal is not allowed.
- Business productization is required for WP-M5A: scenario path PASS alone cannot satisfy business output acceptance.
- WP-M6 normal path data-source closure is required before any frontend completion claim. `normal_path_static_sources > 0` blocks WP-M11.
- WP-M7 graph mutation routes must support before/after DTO snapshots and refresh readback. Local-only graph state cannot satisfy acceptance.
- WP-M8 runtime routes must provide readback for version, run, station and human action state. UI-only simulation cannot satisfy acceptance.
- WP-M9 artifact routes must return auditable artifact refs and content snapshots. Summary cards alone cannot satisfy acceptance.
- WP-M10 quality/failure fixtures may be bounded test fixtures, but they must be served through BFF/DTO or deterministic browser state setup and clearly labeled.
- WP-M11 claim matrix must reference evidence files, not prose claims.

## 6. Contract Exit Criteria

WP-M1 implementation may start only if:

- Route allowlist is referenced by the implementation plan.
- `/bff/v13/*` compatibility route ownership is explicit: either available from the main BFF router or bounded to the acceptance smoke server with no production/runtime claim.
- DTO snapshot shape is referenced by the acceptance runner.
- Browser denylist is enforced in E2E.
- No future facade is required before WP-M1.
- WP-M1 can prove PV13 baseline homepage using `/bff/v13/*` without waiting for PV19/PV20/PV21 integration.

WP-M6 implementation may start only if:

- This contract includes WP-M6 to WP-M11 route families and DTO shapes.
- The implementation plan identifies whether each target route reuses PV13/PV19/PV20/PV21 routes or adds an additive `/bff/workflow-platform/*` facade.
- The runner can fail on forbidden browser routes and on normal-path static source usage.
- The evidence package can store DTO snapshots, route logs, browser action logs, screenshots and artifact manifests.
- Any use of local fallback is user-visible and represented in DTO/report fields.
