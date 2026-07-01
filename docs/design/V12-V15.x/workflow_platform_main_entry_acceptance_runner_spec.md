# Workflow Platform Main Entry Acceptance Runner Spec

用途：定义 WP-M1 到 WP-M11 后续自动化验收 runner 的输入、输出、场景和 PASS/FAIL 规则。
边界：本文是 runner 规格，不是 runner 实现。

## 1. Runner Goals

自动化验收必须模拟人类真实使用路径，而不是只检查页面是否加载：

```text
open root
  -> confirm PV13 baseline main entry
  -> interact with PV13 canvas
  -> inspect node and evidence
  -> create/review WorkflowDiff
  -> publish/run/human gate/evidence
  -> inspect governed Agent executor panel
  -> verify WP-M5A business scenario outputs when that stage is active
  -> verify WP-M6 normal-path data source closure
  -> edit/save/readback WorkflowSpecGraph
  -> publish/run/human/evidence inside the PV13 workbench
  -> verify three business scenario artifacts
  -> verify failure states, accessibility, responsive behavior and performance
  -> generate WP-M11 claim-to-evidence matrix when aggregate stage is active
  -> generate Chinese HTML acceptance report
```

## 2. Required Outputs

| Artifact | Stage | Required content |
| --- | --- | --- |
| `acceptance-data.json` | all | Stage, status, scenarios, commands, evidence refs, claim safety result。 |
| `artifact-manifest.json` | all | Every screenshot/log/report path and checksum if available。 |
| `acceptance-report.html` | all | 中文、人类可读、截图证据、目标架构 vs 当前实现、能力分类。 |
| `browser-action-log.json` | WP-M1+ | Click, drag, wheel, connect, cancel, panel switch, human action。 |
| `browser-network-log.json` | WP-M1+ | BFF routes only, forbidden-route detection。 |
| `dto-snapshot.json` | WP-M1+ | PV13 baseline state, graph, validation, run/evidence snapshots。 |
| `v13-route-ownership-report.json` | WP-M1A | `/bff/v13/*` route source, main BFF/smoke-server boundary, route smoke result and claim boundary。 |
| `pv13-baseline-homepage-report.json` | WP-M1 | Root, `workflow-platform` and `v13-editable-studio` route assertions。 |
| `canvas-edge-quality-report.json` | WP-M2 | Zoom/drag/connect/cancel/arrow/overlap checks。 |
| `runtime-inspect-report.json` | WP-M3 | WorkflowVersion, WorkflowInstance, StationRun, human gate readback。 |
| `agent-executor-integration-report.json` | WP-M4 | Governed executor actions, denial/approval/evidence refs。 |
| `user-scenario-report.json` | WP-M3+ | Minimum Agent workflow plus document/knowledge summary, code review and meeting/interview scenario results。 |
| `workflow-platform-capability-parity-report.json` | WP-M3+ | No-regression checklist against `WorkflowPlatformMainEntry` PV21/PV20 capabilities, with source route, target UI surface, evidence refs and PASS/FAIL status。 |
| `scenario-projection-report.json` | WP-M5A | Scenario catalog, input contracts, node templates, Inspector/timeline projection, fallback usage and DTO source。 |
| `business-output-report.json` | WP-M5A | Document summary, code review and meeting brief output summaries with artifact, quality, audit, human review and redaction refs。 |
| `mock-reduction-report.json` | WP-M5A | Remaining static `scenarioData`, `fallbackGraph`, chat/timeline/Inspector usage and whether each is fallback/design-only。 |
| `frontend-data-source-closure-report.json` | WP-M6 | 每个 UI 区域的数据来源、fallback 条件、normal_path_static_sources 统计。 |
| `graph-edit-save-readback-report.json` | WP-M7 | 节点拖拽、连线、取消/删除、配置、保存、刷新回读、Diff review。 |
| `workflow-inline-runtime-report.json` | WP-M8 | PV13 工作台内 publish、run、StationRun inspect、Human Gate、Evidence Review 连续路径。 |
| `business-artifact-manifest.json` | WP-M9 | 文档总结、代码审查、会议整理产物、input hash、content snapshot、quality/human/redaction refs。 |
| `frontend-quality-failure-state-report.json` | WP-M10 | 加载、空、错误、权限拒绝、BFF 离线、校验失败、人工拒绝、取消/重试、a11y、响应式、性能。 |
| `claim-to-evidence-matrix.json` | WP-M11 | WP-FR-1 到 WP-FR-20 的声明、证据、状态和阻断项。 |
| `frontend-completion-aggregate-audit.html` | WP-M11 | 中文聚合审计报告，面向人类审查。 |
| `no-false-green-scan.txt` | all | Forbidden claim scan over docs, UI copy and report。 |
| `redaction-scan.txt` | all | Secret/token/raw credential leakage scan。 |

WP-M6 through WP-M11 reports must validate against these minimum schemas before a substage can be marked PASS:

| Report | Schema |
| --- | --- |
| `frontend-data-source-closure-report.json` | `docs/design/V12-V15.x/schemas/frontend-data-source-closure-report.schema.json` |
| `graph-edit-save-readback-report.json` | `docs/design/V12-V15.x/schemas/graph-edit-save-readback-report.schema.json` |
| `workflow-inline-runtime-report.json` | `docs/design/V12-V15.x/schemas/workflow-inline-runtime-report.schema.json` |
| `business-artifact-manifest.json` | `docs/design/V12-V15.x/schemas/business-artifact-manifest.schema.json` |
| `frontend-quality-failure-state-report.json` | `docs/design/V12-V15.x/schemas/frontend-quality-failure-state-report.schema.json` |
| `claim-to-evidence-matrix.json` | `docs/design/V12-V15.x/schemas/claim-to-evidence-matrix.schema.json` |

## 3. Scenario Matrix

| Scenario | Stage | PASS condition |
| --- | --- | --- |
| V13 compatibility route ownership | WP-M1 | `/bff/v13/*` route source is explicit and route smoke passes; smoke-server-only evidence is labeled bounded。 |
| Root opens PV13 Workflow Platform | WP-M1 | `/` shows `v13-editable-studio` state without manual query。 |
| Workflow-platform route opens PV13 | WP-M1 | `?studio=workflow-platform` shows `v13-editable-studio` state。 |
| V13 route remains available | WP-M1 | `?studio=v13-editable-studio` remains available for replay。 |
| Workspace/project comprehension | WP-M1 | User-visible workspace/project/workflow state exists。 |
| BFF-only network | WP-M1 | Browser log contains only allowed BFF routes for the scenario。 |
| Wheel zoom | WP-M2 | Wheel event changes viewport scale and records screenshot。 |
| Right-area drag | WP-M2 | Node can be dragged in right/empty canvas region。 |
| Node select + inspector | WP-M2 | Selecting node updates inspector DTO and UI。 |
| Free connect | WP-M2 | Edge can be created between legal ports。 |
| Cancel connect | WP-M2 | In-progress edge can be cancelled with no stale edge。 |
| Arrow visibility | WP-M2 | Arrows visible at first-eye and zoomed states。 |
| Invalid edge feedback | WP-M2 | Illegal connection is denied with visible reason。 |
| WorkflowDiff review | WP-M3 | Diff DTO visible and not auto-published。 |
| Publish and version readback | WP-M3 | Version appears in version list with audit refs。 |
| Run and inspect | WP-M3 | WorkflowInstance and StationRun readback exists。 |
| Human gate transition | WP-M3 | Before/after state digest changes after confirmed action。 |
| Evidence classification | WP-M3 | Artifact/trace/quality/audit/claim/redaction categories visible。 |
| PV21 capability parity | WP-M3 | PV13-based workbench preserves `WorkflowPlatformMainEntry` graph save/readback, validation, diff, publish, rollback, run, inspect, human gate and evidence review capabilities。 |
| Minimum Agent workflow scenario | WP-M3 | User completes canvas edit/connect/configure, Diff, publish, run, human gate and evidence review。 |
| Document knowledge summary scenario | WP-M3 | User imports/selects documents, builds input -> retrieval/read -> summarizer Agent -> human review -> report output workflow, runs it, and receives summary, citation/evidence refs and human review record。 |
| Code review risk scenario | WP-M3 | User selects repo/branch/PR or diff, builds code input -> static scan -> test runner -> risk Agent -> human gate -> issue output workflow, runs it, and receives file/line issues, test output, risk level and review record。 |
| Meeting interview brief scenario | WP-M3 | User imports transcript or interview text, builds transcript input -> extractor Agent -> decision classifier -> task planner -> human gate -> brief output workflow, runs it, and receives brief, action items, decisions, open questions and review record。 |
| Executor state | WP-M4 | Agent/Tool/Skill/MCP resources shown as governed。 |
| Executor action | WP-M4 | Allowlisted action has confirmation, audit refs and evidence refs。 |
| Denied action | WP-M4 | Forbidden or missing confirmation action is denied with reason。 |
| PV20 capability parity | WP-M4 | PV13-based workbench preserves `WorkflowPlatformMainEntry` executor state, execution contract, execution evidence, skill action, tool action, MCP action and approval/denial refs。 |
| Scenario projection DTO | WP-M5A | Scenario list, input requirements, node templates, Inspector/timeline and evidence categories come from BFF/DTO projection or are explicitly marked fallback。 |
| Document summary output | WP-M5A | User receives a summary artifact or machine-readable summary output with citations, quality status and human review refs。 |
| Code review output | WP-M5A | User receives code review findings with file/line refs, risk level, test/static scan refs and human approval refs。 |
| Meeting brief output | WP-M5A | User receives meeting brief, action items, decisions, open questions, citation refs and review refs。 |
| Mock reduction | WP-M5A | Static scenario data is no longer used as the source of truth for accepted business output, or each remaining use is marked fallback/design reference。 |
| Normal-path data source closure | WP-M6 | `normal_path_static_sources == 0`; scenario, graph, Inspector, timeline, quality, evidence and chat initial context come from BFF/DTO/artifact refs or explicit fallback。 |
| Fallback visibility | WP-M6 | If fallback is used, UI and report visibly label source, reason and non-claim boundary。 |
| Graph node drag persisted | WP-M7 | Dragging a node changes graph DTO after save and survives refresh readback。 |
| Edge create/delete persisted | WP-M7 | Legal edge create and delete/cancel produce expected backend graph state; illegal edge is denied with visible reason。 |
| Node configuration persisted | WP-M7 | Editing role/goal/tool/skill/MCP/quality config updates DTO and inspector readback。 |
| WorkflowDiff from saved graph | WP-M7 | Diff is generated from backend saved graph state and requires human review。 |
| Publish inline | WP-M8 | PV13 workbench publishes WorkflowVersion and reads it back with audit refs。 |
| Run inline | WP-M8 | PV13 workbench starts WorkflowInstance and reads WorkflowInstance / StationRun through BFF。 |
| Human gate inline | WP-M8 | Approve/reject changes backend state and UI reflects before/after digest。 |
| Evidence inline | WP-M8 | Evidence Review displays artifact/trace/quality/audit/claim/redaction refs in PV13 workbench。 |
| Document summary artifact | WP-M9 | Document scenario produces auditable artifact/content snapshot, input hash, quality refs and human review refs。 |
| Code review artifact | WP-M9 | Code scenario produces review artifact/content snapshot, file/risk refs, test/static refs and approval refs。 |
| Meeting brief artifact | WP-M9 | Meeting scenario produces brief/action item artifact/content snapshot and review refs。 |
| Loading and empty states | WP-M10 | Loading and empty states are user-visible and do not block recovery actions。 |
| Error and permission states | WP-M10 | Error, permission denied and BFF offline states are visible, actionable and screenshot-backed。 |
| Validation and human reject states | WP-M10 | Graph validation failure and human rejection are visible with reason and next action。 |
| Accessibility and responsive baseline | WP-M10 | Keyboard path, focus visibility, text containment, responsive screenshots and a11y scan PASS or explicit bounded exception。 |
| Performance budget | WP-M10 | First usable workbench and key interactions meet documented budget or are blocked with risk。 |
| Claim-to-evidence closure | WP-M11 | WP-FR-1..WP-FR-20 all have evidence refs; missing evidence marks BLOCKED。 |

## 4. PASS / FAIL Rules

The runner must mark the stage `FAIL` if any required scenario fails.

The runner must mark the stage `BLOCKED` if:

- Dev server or API server cannot start.
- Required route family is missing.
- `/bff/v13/*` route source cannot be established before WP-M1 route remap.
- Evidence directory cannot be written.
- Browser automation cannot capture screenshots.

The runner must mark the stage `NO_GO` if:

- Browser calls a forbidden route.
- Acceptance report uses docs/screenshots as runtime evidence.
- UI/report claims production ready, complete Studio GA, Agent executor ready or Xpert parity.
- Redaction scan finds raw secrets, tokens or credentials.
- WP-M1 default homepage still renders the degraded `WorkflowPlatformMainEntry` instead of PV13 baseline.
- Report treats smoke-server-only `/bff/v13/*` evidence as main BFF/runtime completion.
- WP-M3/WP-M4 capability parity report misses any required `WorkflowPlatformMainEntry` PV21/PV20 capability without explicit defer/No-Go label and user confirmation.
- WP-M5A report claims business output completion using only scenario path PASS, screenshots or acceptance report text.
- WP-M5A UI/report treats local `scenarioData`, `fallbackGraph` or static chat/timeline as backend business projection.
- WP-M6 normal path still uses local static business facts but the report claims data-driven closure.
- WP-M7 graph edits are local-only and do not survive BFF save/readback.
- WP-M8 runtime result is UI simulation without WorkflowVersion / WorkflowInstance / StationRun / HumanAction readback.
- WP-M9 business artifacts are summary cards or report prose without auditable artifact/content snapshot refs.
- WP-M10 omits failure states that materially affect the minimum user path.
- WP-M11 aggregate audit marks PASS while any WP-FR item lacks evidence.

## 5. Suggested Commands

These are target commands for implementation; they are not passing evidence until implemented and executed.

```bash
# Backend contract smoke
.venv/bin/pytest tests/test_workflow_platform_main_entry_bff.py -q

# Frontend unit / interaction tests
pnpm --dir apps/workflow-console test

# Browser E2E
node apps/workflow-console/e2e/workflow_platform_main_entry_acceptance.mjs

# WP-M5A business scenario productization acceptance
node apps/workflow-console/e2e/workflow_platform_business_scenarios_acceptance.mjs

# WP-M6 to WP-M11 frontend completion acceptance
node apps/workflow-console/e2e/workflow_platform_frontend_completion_acceptance.mjs
```

## 6. Report Structure

`acceptance-report.html` must contain:

- 中文摘要。
- 当前目标架构与当前实现对比，必须说明 PV13 是首页前端基线。
- 当前可完成功能：已验收、受限完成、规划中、No-Go。
- 用户应用场景：基础 Agent 工作流、三个 required business scenarios、optional/future scenario boundaries。
- 用户场景截图。
- Browser network log 摘要。
- DTO snapshot 摘要。
- Capability parity 摘要：相对 `WorkflowPlatformMainEntry` 已接入 PV21/PV20 能力的保留、迁移、延期或阻断状态。
- WP-M5A 业务场景产品化摘要：三类业务产物、artifact refs、human review refs、mock/fallback 状态。
- WP-M6 数据源闭环摘要：每个 UI 区域的数据来源、normal path mock scan、fallback 边界。
- WP-M7 图编辑摘要：保存前后 DTO、刷新回读、Diff 审查。
- WP-M8 运行闭环摘要：版本、实例、StationRun、人工动作、证据分类。
- WP-M9 业务产物摘要：三个业务场景的输入、产物、content snapshot、质量、人审和脱敏 refs。
- WP-M10 质量摘要：失败态、权限态、离线态、响应式、a11y、性能。
- WP-M11 claim-to-evidence matrix 摘要：WP-FR-1 到 WP-FR-20 状态。
- PRD 检视结果。
- 目标架构检视结果。
- Claim safety and redaction summary。
- Clear non-claims。
