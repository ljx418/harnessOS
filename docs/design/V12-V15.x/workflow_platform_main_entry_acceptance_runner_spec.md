# Workflow Platform Main Entry Acceptance Runner Spec

用途：定义 WP-M1 到 WP-M4 后续自动化验收 runner 的输入、输出、场景和 PASS/FAIL 规则。
边界：本文是 runner 规格，不是 runner 实现。

## 1. Runner Goals

自动化验收必须模拟人类真实使用路径，而不是只检查页面是否加载：

```text
open root
  -> confirm main entry
  -> interact with canvas
  -> inspect node and evidence
  -> create/review WorkflowDiff
  -> publish/run/human gate/evidence
  -> inspect governed Agent executor panel
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
| `dto-snapshot.json` | WP-M1+ | Main entry state, graph, validation, run/evidence snapshots。 |
| `canvas-edge-quality-report.json` | WP-M2 | Zoom/drag/connect/cancel/arrow/overlap checks。 |
| `runtime-inspect-report.json` | WP-M3 | WorkflowVersion, WorkflowInstance, StationRun, human gate readback。 |
| `agent-executor-integration-report.json` | WP-M4 | Governed executor actions, denial/approval/evidence refs。 |
| `user-scenario-report.json` | WP-M3+ | Minimum Agent workflow plus document/knowledge summary, code review and meeting/interview scenario results。 |
| `no-false-green-scan.txt` | all | Forbidden claim scan over docs, UI copy and report。 |
| `redaction-scan.txt` | all | Secret/token/raw credential leakage scan。 |

## 3. Scenario Matrix

| Scenario | Stage | PASS condition |
| --- | --- | --- |
| Root opens Workflow Platform | WP-M1 | `/` shows workflow platform state without manual query。 |
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
| Minimum Agent workflow scenario | WP-M3 | User completes canvas edit/connect/configure, Diff, publish, run, human gate and evidence review。 |
| Document knowledge summary scenario | WP-M3 | User imports/selects documents, builds input -> retrieval/read -> summarizer Agent -> human review -> report output workflow, runs it, and receives summary, citation/evidence refs and human review record。 |
| Code review risk scenario | WP-M3 | User selects repo/branch/PR or diff, builds code input -> static scan -> test runner -> risk Agent -> human gate -> issue output workflow, runs it, and receives file/line issues, test output, risk level and review record。 |
| Meeting interview brief scenario | WP-M3 | User imports transcript or interview text, builds transcript input -> extractor Agent -> decision classifier -> task planner -> human gate -> brief output workflow, runs it, and receives brief, action items, decisions, open questions and review record。 |
| Executor state | WP-M4 | Agent/Tool/Skill/MCP resources shown as governed。 |
| Executor action | WP-M4 | Allowlisted action has confirmation, audit refs and evidence refs。 |
| Denied action | WP-M4 | Forbidden or missing confirmation action is denied with reason。 |

## 4. PASS / FAIL Rules

The runner must mark the stage `FAIL` if any required scenario fails.

The runner must mark the stage `BLOCKED` if:

- Dev server or API server cannot start.
- Required route family is missing.
- Evidence directory cannot be written.
- Browser automation cannot capture screenshots.

The runner must mark the stage `NO_GO` if:

- Browser calls a forbidden route.
- Acceptance report uses docs/screenshots as runtime evidence.
- UI/report claims production ready, complete Studio GA, Agent executor ready or Xpert parity.
- Redaction scan finds raw secrets, tokens or credentials.

## 5. Suggested Commands

These are target commands for implementation; they are not passing evidence until implemented and executed.

```bash
# Backend contract smoke
.venv/bin/pytest tests/test_workflow_platform_main_entry_bff.py -q

# Frontend unit / interaction tests
pnpm --dir apps/workflow-console test

# Browser E2E
node apps/workflow-console/e2e/workflow_platform_main_entry_acceptance.mjs
```

## 6. Report Structure

`acceptance-report.html` must contain:

- 中文摘要。
- 当前目标架构与当前实现对比。
- 当前可完成功能：已验收、受限完成、规划中、No-Go。
- 用户应用场景：基础 Agent 工作流、三个 required business scenarios、optional/future scenario boundaries。
- 用户场景截图。
- Browser network log 摘要。
- DTO snapshot 摘要。
- PRD 检视结果。
- 目标架构检视结果。
- Claim safety and redaction summary。
- Clear non-claims。
