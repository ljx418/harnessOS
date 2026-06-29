# PV21 Complete Workflow Studio Acceptance Runner Spec

用途：定义 PV21 后续自动化验收 runner、浏览器 E2E、截图证据和审计报告生成规则。
阅读对象：测试、开发、架构、审计人员。
边界：本文是验收自动化规格，不是验收结果；不得据此声明完整工作流工作台已完成。

## 1. Runner Goal

PV21 acceptance runner 必须证明一个真实用户路径，而不是证明文档或静态页面存在。

目标路径：

```text
open Studio -> load state -> edit graph -> validate -> diff -> publish -> run -> inspect -> human action -> evidence -> rollback
```

## 2. Evidence Directory

后续实现验收证据固定落在：

```text
docs/design/V12-V15.x/evidence/pv21-complete-workflow-studio/
```

Runner 必须生成：

- `acceptance-data.json`
- `artifact-manifest.json`
- `studio-state-dto-snapshot.json`
- `workflow-graph-roundtrip-report.json`
- `graph-validation-report.json`
- `workflow-diff-report.json`
- `workflow-version-publish-rollback-report.json`
- `runtime-run-inspect-report.json`
- `human-action-transition-report.json`
- `evidence-summary-report.json`
- `browser-network-log.json`
- `route-boundary-log.json`
- `pv21-studio-home.png`
- `pv21-canvas-edit.png`
- `pv21-version-run-evidence.png`
- `prd-spec-review.md`
- `target-architecture-review.md`
- `ux-review.md`
- `platform-generality-review.md`
- `no-false-green-scan.txt`
- `redaction-scan.txt`

## 3. Runner Phases

| Phase | Action | Pass condition |
| --- | --- | --- |
| R1 State load | Call `/bff/pv21/studio/state`. | DTO has scope, node library, draft graph, version history, run history and evidence health. |
| R2 Graph edit | Add/update/remove generic nodes and edges through BFF. | Backend graph readback matches intended mutation. |
| R3 Validation | Validate both valid and invalid graphs. | Valid graph passes; invalid graph blocks publish with stable error codes. |
| R4 Diff | Generate WorkflowDiff against base version. | Added/removed/changed nodes and risk summary are populated. |
| R5 Publish | Publish with user confirmation. | WorkflowVersion created with audit refs. |
| R6 Run | Start run from published version. | WorkflowInstance / StationRun readback exists. |
| R7 Human gate | Submit human action to waiting gate. | Backend run/station state changes and audit refs exist. |
| R8 Evidence | Load evidence summary. | Artifact, trace, quality, approval, claim and redaction refs are present or explicitly listed in `missing_refs`. |
| R9 Rollback | Roll back to prior version with confirmation. | Active version changes; history and evidence remain. |
| R10 Browser | Execute Chrome/Playwright user path. | Screenshots and network log exist; no forbidden route calls. |
| R11 Guards | Run No False Green, redaction and platform generality scans. | All guard scans PASS. |

## 4. Browser E2E Requirements

Browser automation must simulate human actions:

1. Open `http://127.0.0.1:5173/?studio=pv21-complete-workflow-studio`.
2. Wait for Studio state loaded indicator.
3. Add or select one generic Agent node and one Human Gate node.
4. Edit node params through Inspector.
5. Trigger validation.
6. Trigger diff and publish.
7. Trigger run.
8. Execute human gate action.
9. Open evidence review.
10. Trigger rollback.

Screenshots:

- `pv21-studio-home.png`: initial workbench, not empty.
- `pv21-canvas-edit.png`: canvas with edited graph and Inspector.
- `pv21-version-run-evidence.png`: version/run/evidence panels visible.

Network assertions:

- Every mutable action uses `/bff/pv21/*`.
- No browser request to `/v1/rpc`, `/v1/internal/*`, raw connector or runtime store route.
- Failed requests are captured with structured `PV21ErrorDTO`.

## 5. Acceptance Data Shape

`acceptance-data.json` must include:

| Field | Type | Required |
| --- | --- | --- |
| `stage` | string | yes |
| `generated_at` | string | yes |
| `overall_status` | `pass\|fail` | yes |
| `prd_requirements` | object | yes |
| `architecture_entities` | object | yes |
| `runner_phases` | object | yes |
| `browser_e2e` | object | yes |
| `guard_scans` | object | yes |
| `blockers` | string[] | yes |
| `evidence_files` | string[] | yes |

## 6. Required Negative Fixtures

| Fixture | Expected result |
| --- | --- |
| `browser_direct_rpc_denied` | Browser route scan fails if `/v1/rpc` is called. |
| `invalid_edge_publish_blocked` | Publish denied with `PV21_GRAPH_INVALID`. |
| `missing_required_node_param_publish_blocked` | Publish denied with node-level error. |
| `unknown_node_type_denied` | Save or validate denied with `PV21_UNKNOWN_NODE_TYPE`. |
| `business_specific_core_branch_denied` | Platform generality scan fails. |
| `agent_direct_publish_denied` | Agent-origin durable publish denied. |
| `rollback_without_confirmation_denied` | Rollback denied with `PV21_CONFIRMATION_REQUIRED`. |
| `human_action_without_waiting_gate_denied` | Human action denied with `PV21_HUMAN_GATE_NOT_WAITING`. |
| `run_unpublished_draft_denied` | Run denied with `PV21_RUN_VERSION_REQUIRED`. |
| `raw_prompt_leak_denied` | Redaction scan fails. |
| `raw_secret_leak_denied` | Redaction scan fails. |
| `history_delete_denied` | Rollback cannot delete old version/run/evidence. |

## 7. PRD Spec Review Checklist

Runner or audit script must map PV21 requirements:

- PV21-F1: default Studio entry.
- PV21-F2: graph authoring.
- PV21-F3: Inspector.
- PV21-F4: validation.
- PV21-F5: diff/version/publish/rollback/run history.
- PV21-F6: runtime run.
- PV21-F7: human gate.
- PV21-F8: evidence review.
- PV21-F9: BFF boundary.
- PV21-F10: UX quality.

Each item must be:

- `pass`
- `fail`
- `blocked`

`blocked` must include a concrete blocker and cannot be counted as PASS.

## 8. Stop Conditions

Runner must fail and stop the stage if:

- Studio home screenshot is blank or static-only.
- Backend graph readback does not match browser edit.
- Publish succeeds despite blocking validation errors.
- Run does not bind to a published WorkflowVersion.
- Human action is simulated only in frontend state.
- Evidence summary omits required refs without `missing_refs`.
- Browser calls a forbidden route.
- No False Green or redaction scan fails.
- Acceptance report writes PASS while any required phase failed.

