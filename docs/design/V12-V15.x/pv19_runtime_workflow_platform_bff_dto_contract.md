# PV19 Runtime Workflow Platform BFF DTO Contract

用途：定义 PV19 BFF DTO 的最低语义，供后续实现和验收使用。
阅读对象：前端、后端、测试、审计人员。
边界：本文是实现合同；实现前不得把 route 或 DTO 当作已存在证据。PV19 实现不得用其他阶段 test-only route 替代本合同验收。

## 1. Route Set

| Route | Purpose |
| --- | --- |
| `GET /bff/pv19/workbench/state` | 返回 workspace、project、workflow、version、run、health 和入口状态。 |
| `GET /bff/pv19/workflows/{workflow_id}/graph` | 返回当前 WorkflowSpecGraph。 |
| `POST /bff/pv19/workflows/{workflow_id}/graph/validate` | 校验 graph schema、节点、边、人工卡点和 runtime 可执行性。 |
| `POST /bff/pv19/workflows/{workflow_id}/diff` | 生成 WorkflowDiff。 |
| `POST /bff/pv19/workflows/{workflow_id}/versions/publish` | 用户确认后发布 WorkflowVersion。 |
| `POST /bff/pv19/workflows/{workflow_id}/runs` | 按发布版本启动 WorkflowInstance。 |
| `GET /bff/pv19/runs/{run_id}/inspect` | 返回运行进度、节点状态、human gate、artifact 和 trace refs。 |
| `POST /bff/pv19/runs/{run_id}/human-actions` | 处理人工确认、补充输入、驳回或重试。 |
| `GET /bff/pv19/runs/{run_id}/evidence` | 返回 evidence summary 和 claim-to-evidence。 |

## 2. Required DTO Fields

所有 DTO 必须包含：

- `schema_version`
- `scope`
- `redaction_status`
- `audit_refs`
- `evidence_refs`

关键 DTO 必须包含：

| DTO | Required semantic fields |
| --- | --- |
| `PV19WorkbenchStateDTO` | active workflow、active version、active run、health、entry status。 |
| `PV19WorkflowGraphDTO` | workflow_id、draft_revision、nodes、edges、human_gate_nodes。 |
| `PV19GraphValidationDTO` | status、errors、warnings、runtime_readiness。 |
| `PV19WorkflowDiffDTO` | before_graph_ref、after_graph_ref、change summary、confirmation boundary。 |
| `PV19WorkflowVersionDTO` | workflow_version_id、published_from_diff、published_by、published_at。 |
| `PV19RunInspectDTO` | workflow_instance_id、workflow_version_id、node states、events、pending human gates。 |
| `PV19HumanActionDTO` | action type、actor、before state、after state、audit ref。 |
| `PV19EvidenceSummaryDTO` | artifacts、trace refs、quality refs、audit refs、claim matrix。 |

## 3. Boundary Requirements

- DTO 不得包含 raw secret、raw provider payload、raw connector payload 或 raw artifact content。
- Browser 只能通过 BFF DTO 获得运行和证据状态。
- `run` 必须引用已发布 `workflow_version_id`。
- `human-actions` 必须返回后端状态变化，不得只返回 UI toast。
- Evidence summary 必须引用后端 artifact/trace/audit read model。

## 4. Fixed Route Ownership

| Route group | Owning implementation file | Forbidden shortcut |
| --- | --- | --- |
| Workbench / graph / diff / publish | `apps/api/routers/bff.py` | 复用 `/bff/v13/*` 作为 PV19 完成证据。 |
| Run / inspect | `apps/api/routers/bff.py` plus `apps/api/routers/runs.py` handoff | 复用 `/bff/pv17/*` 或前端模拟 run。 |
| Human actions | `apps/api/routers/bff.py` plus approval/handoff stores | 只更新 UI toast、不更新 workflow/approval 状态。 |
| Evidence | `apps/api/routers/bff.py` plus artifact/trace/audit read models | 前端拼接 claim matrix 或 raw artifact content。 |
