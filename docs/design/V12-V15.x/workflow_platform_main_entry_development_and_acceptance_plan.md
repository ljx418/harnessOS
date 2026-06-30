# Workflow Platform Main Entry Development And Acceptance Plan

用途：把“PV13 前端页面作为工作流平台首页和前端基线”的目标拆成可执行开发阶段和验收门槛，并记录 WP-M1A 到 WP-M4 的 bounded acceptance 结果。
边界：本文记录本阶段计划和验收结果；它不证明生产级工作流平台、完整 Workflow Studio GA、无限制 Agent executor 或生产可用。

## 1. Stage Position

WP-M0 是 PV21 bounded candidate 之后、PV22 implementation 之前的主线对齐门禁。最新用户决策把首页基线从“PV21 shell 提升”修正为“PV13 Light Studio 直接作为首页基线”。

```text
V13 / PV13 editable Studio frontend baseline
  -> WP-M0 documentation realignment
  -> WP-M1 PV13 baseline homepage switch
  -> WP-M2 PV13 canvas interaction hardening
  -> WP-M3 runtime/evidence convergence into PV13 baseline
  -> WP-M4 governed Agent executor integration into PV13 baseline
  -> WP-M5 PV22 external app handoff to stable platform host
```

WP-M0 不替代 PV22，也不把 V13/PV13、PV19、PV20 或 PV21 升级为 GA。WP-M1A 到 WP-M4 已完成本阶段 bounded implementation evidence；后续 WP-M5/PV22 仍必须单独审计。

## 2. Substages

| Stage | Goal | Development output | Acceptance output |
| --- | --- | --- | --- |
| WP-M0 | 文档和架构对齐到 PV13 首页基线。 | PRD、架构、计划、里程碑、验收门槛、任务矩阵、drawio、文档审计。 | Document support audit PASS。 |
| WP-M1A | PV13 BFF compatibility verification。 | 验证或恢复 `/bff/v13/*` compatibility routes；若只依赖 smoke server，必须标注 bounded acceptance evidence。 | Route existence smoke、DTO snapshot、No False Green PASS。 |
| WP-M1B | PV13 baseline homepage switch。 | 无 query 根入口和 `?studio=workflow-platform` 均进入 `V13EditableStudio`。 | 首屏 PV13 browser screenshot、route assertion、No False Green PASS。 |
| WP-M2 | PV13 画布交互专项硬化。 | 滚轮缩放、平移、节点拖拽、自由连线、取消连线、箭头可见性。 | Canvas E2E action log、截图、edge quality report PASS。 |
| WP-M3 | 运行与证据闭环融合到 PV13，且不退化 `WorkflowPlatformMainEntry` 已接入的 PV21 能力。 | WorkflowDiff -> publish -> rollback -> run -> human gate -> evidence review 在 PV13 工作台中可理解。 | BFF route log、DTO snapshot、runtime inspect、evidence panel、capability parity PASS。 |
| WP-M4 | Agent executor 产品化融合到 PV13，且不退化 `WorkflowPlatformMainEntry` 已接入的 PV20 能力。 | Agent/Tool/Skill/MCP 资源面板和受治理执行入口接入 PV13。 | Executor evidence refs、approval/denial fixtures、capability parity、copy scan PASS。 |
| WP-M5 | 外部接入前置检查。 | PV22 以稳定 PV13-based Workflow Platform 为接入目标重检。 | PV22 readiness update PASS。 |

## 2.1 Current Implementation Result

```text
wp_m1a_v13_bff_compatibility=PASS
wp_m1b_pv13_homepage_switch=PASS
wp_m2_canvas_interaction=PASS
wp_m3_pv21_runtime_evidence_parity=PASS
wp_m4_pv20_governed_executor_parity=PASS
evidence_dir=docs/design/V12-V15.x/evidence/workflow-platform-main-entry/
acceptance_report=docs/design/V12-V15.x/evidence/workflow-platform-main-entry/acceptance-report.html
```

已实现内容：

- `apps/api/routers/bff.py` 提供正式 `/bff/v13/*` compatibility routes，用于 PV13 graph、validation、WorkflowDiff、handoff 和 node inspector。
- `apps/workflow-console/src/ui/layout/WorkflowStudioLayout.tsx` 将 `workflow-platform` route 映射到 `V13EditableStudio`。
- `apps/workflow-console/src/ui/v13/V13EditableStudio.tsx` 保留 PV13 首屏和画布基线，并新增 PV21/PV20 capability parity 面板。
- `apps/workflow-console/e2e/workflow_platform_main_entry_cdp_acceptance.mjs` 生成截图、网络日志、动作日志、用户场景、能力等价和 HTML 验收报告。

## 3. Development Principles

- 后续代码实现优先复用 `V13EditableStudio.tsx` 和 `v13-editable-studio.css`，不继续把 `WorkflowPlatformMainEntry` 作为首页基线打补丁。
- `WorkflowPlatformMainEntry` 可暂时保留为历史/偏差对比文件；其视觉 shell 不作为目标体验继续开发，但其已接入的 PV21/PV20 用户动作必须作为能力迁移对照。
- 后续 BFF/DTO 实现默认复用 `/bff/v13/*` compatibility routes、`/bff/pv19/*`、`/bff/pv20/*` 和必要的 `/bff/pv21/*` route family；除非 readiness audit 说明必要，否则不先新增大而全的 `/bff/workflow-platform/*` facade。
- WP-M1A 已恢复主 API router 中的正式 `/bff/v13/*` compatibility routes；后续不得再把 V13 路由写成 smoke-server-only evidence。
- 不创建新的孤立演示页作为首入口。
- 首入口必须服务人类审查和真实使用路径，而不是只服务阶段验收。
- 每个子阶段开始前必须有独立 implementation-readiness audit。
- 每个子阶段完成后必须有 PRD review、target architecture review、E2E evidence、No False Green 和 redaction scan。
- 每个子阶段必须按 `workflow_platform_main_entry_bff_dto_contract.md` 和 `workflow_platform_main_entry_acceptance_runner_spec.md` 生成证据。

## 4. Evidence Requirements

| Evidence | Required from | Notes |
| --- | --- | --- |
| `browser-action-log.json` | WP-M1+ | 包含真实用户操作序列。 |
| `browser-network-log.json` | WP-M1+ | 证明浏览器只使用允许 BFF routes。 |
| `dto-snapshot.json` | WP-M1+ | 记录 PV13 baseline state / graph / evidence DTO。 |
| `v13-route-ownership-report.json` | WP-M1A | 记录 `/bff/v13/*` route 来源、主 BFF/smoke server 边界和 No False Green 结论。 |
| `pv13-baseline-homepage-report.json` | WP-M1 | 证明无 query 和 `workflow-platform` 均进入 PV13 baseline。 |
| `canvas-edge-quality-report.json` | WP-M2 | 记录缩放、拖拽、连线、取消、箭头可见性检查。 |
| `runtime-inspect-report.json` | WP-M3 | 证明 WorkflowVersion -> WorkflowInstance -> StationRun readback。 |
| `evidence-panel-report.json` | WP-M3+ | 证明 artifact/trace/quality/audit/claim/redaction 分类显示。 |
| `agent-executor-integration-report.json` | WP-M4 | 证明受治理执行入口和 denial path。 |
| `user-scenario-report.json` | WP-M3+ | 证明基础 Agent 工作流和三个必验业务场景完成端到端路径。 |
| `workflow-platform-capability-parity-report.json` | WP-M3+ | 逐项证明 PV13-based 工作台没有丢失 `WorkflowPlatformMainEntry` 已接入的 PV21/PV20 闭环能力。 |
| `no-false-green-scan.txt` | all stages | 禁止虚假完成声明。 |
| `acceptance-report.html` | all stages | 中文、人类可读、含截图证据。 |

## 5. PRD Review Loop

每个子阶段完成后必须回答：

- 用户是否默认进入 PV13 Light Studio 工作流平台体验。
- 用户是否能完成该阶段承诺的工作流动作。
- 用户是否能用平台完成文档/知识总结、代码审查、会议/访谈整理三个具体业务场景，而不是只看到抽象能力。
- UI 是否把受限能力说清楚。
- 文档是否把完成状态和后续目标混在一起。
- 是否出现 production ready、product-grade frontend complete、complete Workflow Studio ready、Agent executor ready 或 Xpert parity complete 误报。

## 6. Scenario Acceptance

WP-M1 的出门验收必须包含：

- `/bff/v13/*` compatibility route 来源明确，且 route existence smoke PASS。
- 无 query 根入口打开 PV13 baseline。
- `?studio=workflow-platform` 打开 PV13 baseline。
- `?studio=v13-editable-studio` 仍可作为历史基线路由访问。
- 当前退化版入口不再是默认首页。

WP-M3 的出门验收必须包含：

- 基础 Agent 工作流端到端路径：PV13 画布拖拽、节点拖拽、自由连线、配置、保存、校验、Diff、发布、运行、Human Gate、Evidence Review。
- `WorkflowPlatformMainEntry` 已有 PV21 能力不退化：graph save/readback、validate、diff、publish、rollback、run、inspect、human action、evidence review 全部在 PV13 工作台可触达并有 evidence。
- 三个 required business scenarios 全部通过：文档/知识总结、代码审查、会议/访谈整理。
- 中文 HTML 验收报告必须把每个业务场景写成“用户输入 -> 平台动作 -> 人工审查点 -> 输出产物 -> 证据”的结构。

WP-M4 的出门验收必须进一步证明：

- 三个业务场景中的 Agent/Tool/Skill/MCP 入口均是受治理能力。
- Approval、denial、timeout/cancel/retry 或 redaction 至少覆盖一个负向或边界用例。
- `WorkflowPlatformMainEntry` 已有 PV20 executor 能力不退化：state、execution contract、execution evidence、skill action、tool action、MCP action、denial/approval refs 全部在 PV13 工作台可触达并有 evidence。
- UI copy 不暗示 unrestricted automation 或 Agent executor ready。

## 7. Stop Conditions

出现以下任一情况必须停止进入下一阶段：

- 默认首页仍进入 `WorkflowPlatformMainEntry` 退化版体验。
- `/bff/v13/*` route 缺失，或只来自 smoke server 却被写成主 BFF/runtime 完成证据。
- WP-M3/WP-M4 丢失 `WorkflowPlatformMainEntry` 已有 PV21/PV20 闭环能力，且没有明确 `规划中`/`No-Go` 标注和用户确认。
- Browser 直接调用 internal runtime/store route。
- UI 模拟 runtime truth 并被写成真实运行证据。
- 画布核心动作没有自动化 action log 或截图证据。
- 文档把 WP-M0 写成实现完成。
- 文档或 UI 出现禁止 claim。
- PV22 implementation 被提前写成已验收。
- 只展示应用前景但没有跑通 required scenario，却声明用户场景验收通过。
- 创意分镜规划被写成真实视频渲染完成。

## 7.1 Remaining Plan

当前本阶段 WP-M1A 到 WP-M4 已按 bounded review 范围完成。剩余开发计划不应继续在本阶段内扩张，而应进入：

- WP-M5：基于 PV13-based host surface 重做 PV22 readiness update。
- PV22-S1：仅在 WP-M5 审计通过后，实现 External App Contract 的 SDK smoke、BFF template、reference app、capability token 和 method/event/error registry。
- Production governance hardening：另设阶段处理 tenant isolation、credential lifecycle、audit retention、deployment runbook 和 operational smoke。

## 8. WP-M0 Document Acceptance

WP-M0 仅在以下条件满足后通过：

- 新增/修订文档集齐全。
- Drawio 页数不超过 8 页，并且每页中文、无重复冲突。
- PRD、架构、里程碑、验收门槛和任务矩阵互相一致，都明确 PV13 是首页前端基线。
- 文档审计结论为 `GO for PV13 baseline homepage implementation planning only`。
- Claim scan 未发现 forbidden positive claims。
- BFF/DTO 合约、acceptance runner 规格和 implementation readiness audit 均存在且互相一致。
