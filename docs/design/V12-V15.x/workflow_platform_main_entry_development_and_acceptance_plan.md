# Workflow Platform Main Entry Development And Acceptance Plan

用途：把“PV13 前端页面作为工作流平台首页和前端基线”的目标拆成可执行开发阶段和验收门槛，并记录 WP-M1A 到 WP-M5A 的 bounded acceptance 结果。
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
  -> WP-M5A business-scenario productization and data-driven projection
  -> WP-M5B / PV22 external app handoff to stable platform host
```

WP-M0 不替代 PV22，也不把 V13/PV13、PV19、PV20 或 PV21 升级为 GA。WP-M1A 到 WP-M5A 已完成 bounded implementation evidence；WP-M5A 把三个业务场景从路径证据推进到 DTO/evidence-driven 业务输出摘要，但仍不是最终商业业务应用完成。WP-M5B/PV22 readiness refresh 与 PV22-S1..SA 有界实现已完成。

最新用户决策将下一阶段改为 WP-M6 到 WP-M11：先把 PRD 定义的前端页面功能做成真实数据驱动、可编辑、可保存、可运行、可人工审查和可证据回看的有界完成状态。Path D / production governance hardening、业务 Pack 产品化和开源/商业化准备后置，除非用户再次明确改选。

## 2. Substages

| Stage | Goal | Development output | Acceptance output |
| --- | --- | --- | --- |
| WP-M0 | 文档和架构对齐到 PV13 首页基线。 | PRD、架构、计划、里程碑、验收门槛、任务矩阵、drawio、文档审计。 | Document support audit PASS。 |
| WP-M1A | PV13 BFF compatibility verification。 | 验证或恢复 `/bff/v13/*` compatibility routes；若只依赖 smoke server，必须标注 bounded acceptance evidence。 | Route existence smoke、DTO snapshot、No False Green PASS。 |
| WP-M1B | PV13 baseline homepage switch。 | 无 query 根入口和 `?studio=workflow-platform` 均进入 `V13EditableStudio`。 | 首屏 PV13 browser screenshot、route assertion、No False Green PASS。 |
| WP-M2 | PV13 画布交互专项硬化。 | 滚轮缩放、平移、节点拖拽、自由连线、取消连线、箭头可见性。 | Canvas E2E action log、截图、edge quality report PASS。 |
| WP-M3 | 运行与证据闭环融合到 PV13，且不退化 `WorkflowPlatformMainEntry` 已接入的 PV21 能力。 | WorkflowDiff -> publish -> rollback -> run -> human gate -> evidence review 在 PV13 工作台中可理解。 | BFF route log、DTO snapshot、runtime inspect、evidence panel、capability parity PASS。 |
| WP-M4 | Agent executor 产品化融合到 PV13，且不退化 `WorkflowPlatformMainEntry` 已接入的 PV20 能力。 | Agent/Tool/Skill/MCP 资源面板和受治理执行入口接入 PV13。 | Executor evidence refs、approval/denial fixtures、capability parity、copy scan PASS。 |
| WP-M5A | 业务场景产品化和前端静态数据收敛。 | 三个业务场景的场景定义、输入、业务输出摘要、证据和人工复核由 DTO/evidence 驱动；`scenarioData` 仅保留 fallback / design reference 边界。 | Scenario projection、business output report、mock reduction scan、业务输出截图、命令日志和 manifest PASS。 |
| WP-M5B | 外部接入前置检查。 | PV22 以 WP-M5A 后稳定 PV13-based Workflow Platform 为接入目标重检。 | PV22 readiness update PASS。 |
| WP-M6 | Frontend full data-driven closure。 | PV13 正常路径的场景、节点、Inspector、timeline、quality、evidence 和 chat 初始上下文由 BFF/DTO/artifact refs 驱动；本地静态数据只作显式 fallback。 | mock reduction normal path zero、network log、DTO snapshot、fallback boundary screenshots PASS。 |
| WP-M7 | WorkflowSpecGraph edit/save/readback。 | 用户在 PV13 画布拖拽节点、增删连线、配置节点、保存草稿、刷新回读并基于后端状态生成 WorkflowDiff。 | Graph edit/save/readback E2E、BFF route log、Diff review log PASS。 |
| WP-M8 | Publish/run/human/evidence inline loop。 | 用户在 PV13 工作台内发布版本、运行实例、查看 StationRun、执行 Human Gate、打开 Evidence Review。 | Runtime inspect、human action、evidence panel、route log PASS。 |
| WP-M9 | Three business scenario artifact closure。 | 文档总结、代码审查、会议整理生成可审查真实产物或机器可读产物文件，绑定 input hash、quality、human review 和 redaction refs。 | Three artifact manifests、content snapshots、human review reports、redaction scan PASS。 |
| WP-M10 | Frontend quality and failure-state gate。 | 加载、空、错误、权限拒绝、BFF 离线、校验失败、人工拒绝、取消/重试、键盘、响应式、可访问性和性能体验齐备。 | Failure-state matrix、screenshots、a11y report、performance budget PASS。 |
| WP-M11 | PRD-defined frontend completion aggregate audit。 | 汇总 WP-M6 到 WP-M10，逐条映射 WP-FR-1 到 WP-FR-20，缺证即 BLOCKED。 | Claim-to-evidence matrix、aggregate HTML report、No False Green scan PASS。 |

## 2.1 Current Implementation Result

```text
wp_m1a_v13_bff_compatibility=PASS
wp_m1b_pv13_homepage_switch=PASS
wp_m2_canvas_interaction=PASS
wp_m3_pv21_runtime_evidence_parity=PASS
wp_m4_pv20_governed_executor_parity=PASS
wp_m5a_business_scenario_productization=PASS_BOUNDED_REVIEW
wp_m6_to_wp_m11_prd_defined_frontend_completion=PLANNED_DOCUMENTATION_TARGET
evidence_dir=docs/design/V12-V15.x/evidence/workflow-platform-main-entry/
acceptance_report=docs/design/V12-V15.x/evidence/workflow-platform-main-entry/acceptance-report.html
```

已实现内容：

- `apps/api/routers/bff.py` 提供正式 `/bff/v13/*` compatibility routes，用于 PV13 graph、validation、WorkflowDiff、handoff 和 node inspector。
- `apps/workflow-console/src/ui/layout/WorkflowStudioLayout.tsx` 将 `workflow-platform` route 映射到 `V13EditableStudio`。
- `apps/workflow-console/src/ui/v13/V13EditableStudio.tsx` 保留 PV13 首屏和画布基线，并新增 PV21/PV20 capability parity 面板。
- `apps/workflow-console/src/ui/v13/V13EditableStudio.tsx` 读取 WP-M5A scenario projection / business output DTO，并在 Inspector 中展示业务输出摘要和证据边界。
- `apps/api/routers/bff.py` 提供正式 `/bff/workflow-platform/*` scenario projection 和 business output routes。
- `apps/workflow-console/e2e/workflow_platform_main_entry_cdp_acceptance.mjs` 生成截图、网络日志、动作日志、用户场景、能力等价和 HTML 验收报告。

受限完成内容：

- `V13EditableStudio.tsx` 仍包含本地 `scenarioData`、`fallbackGraph`、静态 timeline、静态 Inspector 和 proposal-only chat 回复，但 WP-M5A 已把它们限定为 fallback / design reference。
- `business-output-report.json` 证明三场景具备机器可读业务输出摘要和 evidence refs，但不证明最终独立 Markdown 总结、完整 PR/code review 报告或可商用会议纪要已经生成。
- 后续不得把这些静态内容或验收报告文本包装成最终业务产物完成证据。

## 3. Development Principles

- 后续代码实现优先复用 `V13EditableStudio.tsx` 和 `v13-editable-studio.css`，不继续把 `WorkflowPlatformMainEntry` 作为首页基线打补丁。
- `WorkflowPlatformMainEntry` 可暂时保留为历史/偏差对比文件；其视觉 shell 不作为目标体验继续开发，但其已接入的 PV21/PV20 用户动作必须作为能力迁移对照。
- 后续 BFF/DTO 实现默认复用 `/bff/v13/*` compatibility routes、`/bff/pv19/*`、`/bff/pv20/*` 和必要的 `/bff/pv21/*` route family；除非 readiness audit 说明必要，否则不先新增大而全的 `/bff/workflow-platform/*` facade。
- WP-M1A 已恢复主 API router 中的正式 `/bff/v13/*` compatibility routes；后续不得再把 V13 路由写成 smoke-server-only evidence。
- 不创建新的孤立演示页作为首入口。
- 首入口必须服务人类审查和真实使用路径，而不是只服务阶段验收。
- WP-M5A 已让业务场景输出摘要和 evidence refs 成为一等验收对象；静态场景矩阵只能作为 fallback 或设计参考。
- WP-M6 到 WP-M11 的实现必须先关闭本计划和 `workflow_platform_wp_m6_to_m11_frontend_completion_plan_and_audit.md` 中的审计意见；若存在致命或重大规格偏差，不得进入实质代码开发。
- WP-M6 到 WP-M11 验收必须使用真实 BFF/DTO、真实 artifact/evidence refs、真实浏览器动作日志和真实截图；mock 只能作为明确标注的 fallback/fixture。
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
| `scenario-projection-report.json` | WP-M5A | 证明场景列表、输入要求、节点模板、Inspector、timeline 和 evidence refs 来自 DTO/evidence projection，而不是纯前端静态数据。 |
| `business-output-report.json` | WP-M5A | 证明文档总结、代码审查、会议整理均有业务输出、artifact refs、人工复核状态和质量结论。 |
| `mock-reduction-report.json` | WP-M5A | 证明 `scenarioData`、`fallbackGraph`、静态 chat/timeline 的使用范围被限定为 fallback 或设计参考。 |
| `frontend-data-source-closure-report.json` | WP-M6 | 证明正常路径静态来源为 0，所有业务事实来自 BFF/DTO/artifact refs。 |
| `graph-edit-save-readback-report.json` | WP-M7 | 证明节点拖拽、连线、删除、配置、保存、刷新回读和 Diff 生成。 |
| `workflow-inline-runtime-report.json` | WP-M8 | 证明 PV13 工作台内完成 publish/run/human/evidence 连续路径。 |
| `business-artifact-manifest.json` | WP-M9 | 证明三业务场景产物文件、input hash、quality、human review、redaction refs。 |
| `frontend-quality-failure-state-report.json` | WP-M10 | 证明失败态、权限态、离线态、响应式、键盘、a11y 和性能。 |
| `frontend-completion-aggregate-audit.html` | WP-M11 | 中文聚合审计报告，列出 PRD、架构、代码、证据和残留风险。 |
| `no-false-green-scan.txt` | all stages | 禁止虚假完成声明。 |
| `acceptance-report.html` | all stages | 中文、人类可读、含截图证据。 |

## 5. PRD Review Loop

每个子阶段完成后必须回答：

- 用户是否默认进入 PV13 Light Studio 工作流平台体验。
- 用户是否能完成该阶段承诺的工作流动作。
- 用户是否能用平台完成文档/知识总结、代码审查、会议/访谈整理三个具体业务场景，而不是只看到抽象能力。
- 用户是否能看到业务产物本身，而不是只看到验收报告里说场景通过。
- 前端展示是否仍主要依赖本地静态场景矩阵；如是，是否被明确标注为受限完成或 fallback。
- UI 是否把受限能力说清楚。
- 文档是否把完成状态和后续目标混在一起。
- 是否出现 production ready、product-grade frontend complete、complete Workflow Studio ready、Agent executor ready 或 Xpert parity complete 误报。
- 是否把“PRD-defined frontend functionality complete for bounded review”误写成生产级或商业级完成。

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

WP-M5A 的出门验收已进一步证明：

- 三个业务场景都有机器可读业务输出摘要：文档摘要、代码审查风险摘要、会议纪要/行动项摘要。
- 每个业务输出都能回溯 artifact、trace、quality、audit、claim、redaction 和 human review refs。
- 场景目录、输入要求、节点配置、Inspector、timeline 和输出摘要来自 BFF/DTO/evidence projection，剩余静态内容明确标注 fallback。
- `mock-reduction-report.json` 已标出仍保留的本地静态数据、保留原因、用户可见边界和后续移除条件。
- HTML 验收报告把“已验收路径证据”和“业务输出摘要证据/最终产物边界”分开列示。
- WP-M5A、WP-M5B/PV22 readiness refresh 与 PV22-S1..SA 已通过有界验收；不得据此声明 PV22 production/commercial/external ecosystem complete。

WP-M6 的出门验收必须包含：

- 正常路径不再使用 `scenarioData`、`fallbackGraph`、静态 timeline、静态 Inspector 或 proposal-only chat 作为业务事实来源。
- UI 明确区分在线 BFF/DTO 数据和离线 fallback。
- `frontend-data-source-closure-report.json` 记录每个页面区域的数据来源。
- 若正常路径仍有本地 mock，必须打回开发计划阶段。

WP-M7 的出门验收必须包含：

- 用户在 PV13 画布中完成节点拖拽、合法连线、取消/删除连线、节点配置、保存草稿、刷新回读。
- WorkflowDiff 必须基于后端保存状态生成，并需要人工审查。
- 不得直接从 browser 写 WorkflowStore 或 Gateway internals。

WP-M8 的出门验收必须包含：

- 用户在 PV13 工作台内完成 publish、run、StationRun inspect、Human Gate approve/reject、Evidence Review。
- 运行结果和人工动作必须可从 BFF/DTO 回读。
- 不得只通过分散 PV19/PV21 页面完成。

WP-M9 的出门验收必须包含：

- 文档总结、代码审查、会议整理三场景均有真实输入、产物文件或机器可读产物、artifact refs、quality refs、human review refs 和 redaction refs。
- HTML 报告必须展示每个产物的用户输入、平台动作、人工审查点、输出产物和证据链。
- 若只有摘要卡片而没有可审查产物文件，仍标记为受限完成。

WP-M10 的出门验收必须包含：

- 加载、空、错误、权限拒绝、BFF 离线、校验失败、人工拒绝、取消/重试均有截图和状态断言。
- 键盘操作、焦点可见性、响应式断点、可访问性扫描和性能预算均 PASS 或给出明确豁免。

WP-M11 的出门验收必须包含：

- WP-FR-1 到 WP-FR-20 的 claim-to-evidence matrix。
- WP-M6 到 WP-M10 所有 evidence package manifest。
- 文档、UI copy、验收报告 No False Green scan。
- 明确剩余后置阶段：生产治理、业务 Pack 产品化、开源/商业化准备。

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
- 只复用 acceptance report 或 scenario pass JSON，却声明已经生成独立业务产物。
- 前端本地 `scenarioData` / `fallbackGraph` / 静态 chat/timeline 被写成后端真实业务投影。
- 创意分镜规划被写成真实视频渲染完成。
- WP-M6 到 WP-M11 任一阶段使用设计稿、截图、静态 mock 或 acceptance report 文本替代 BFF/DTO/browser/action/artifact evidence。
- 正常路径 mock 未清零却声明 PRD-defined frontend functionality complete。

## 7.1 Remaining Plan

当前 WP-M1A 到 WP-M5A、WP-M5B 和 PV22-S1..SA 已按 bounded review 范围完成。用户已选择新的当前阶段为 WP-M6 到 WP-M11 PRD-defined frontend functionality completion。剩余开发顺序为：

1. WP-M6：正常路径数据驱动闭环。
2. WP-M7：WorkflowSpecGraph 编辑、保存、刷新回读和 Diff 审查。
3. WP-M8：发布、运行、人工门禁和证据回看在 PV13 工作台内闭环。
4. WP-M9：三个业务场景真实产物和证据链闭环。
5. WP-M10：失败态、可访问性、响应式和性能体验门槛。
6. WP-M11：PRD-defined frontend completion 聚合审计。

WP-M11 之后才重新选择：

- Production governance hardening：另设阶段处理 tenant isolation、credential lifecycle、audit retention、deployment runbook 和 operational smoke。
- Business Pack productization：另设阶段把 Meeting / Knowledge / Interview / Investment / Video Studio 推进为真实业务 App。
- Open-source / commercial readiness：另设阶段处理 contributor docs、release pipeline、license/CLA、deployment docs、billing/rate-limit strategy。

## 8. WP-M0 Document Acceptance

WP-M0 仅在以下条件满足后通过：

- 新增/修订文档集齐全。
- Drawio 页数不超过 8 页，并且每页中文、无重复冲突。
- PRD、架构、里程碑、验收门槛和任务矩阵互相一致，都明确 PV13 是首页前端基线。
- 文档审计结论为 `GO for PV13 baseline homepage implementation planning only`。
- Claim scan 未发现 forbidden positive claims。
- BFF/DTO 合约、acceptance runner 规格和 implementation readiness audit 均存在且互相一致。
