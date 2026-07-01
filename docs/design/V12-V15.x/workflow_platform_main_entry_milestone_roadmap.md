# Workflow Platform Main Entry Milestone Roadmap

用途：定义从 PV13/V13、PV19、PV20、PV21 状态到 PV13-based 工作流平台首页 MVP 的里程碑，并记录 WP-M1A 到 WP-M4 当前通过状态。
边界：本文是路线图和 bounded evidence 索引，不证明生产级平台、完整 Studio GA 或生产可用。

## 1. Roadmap

| Order | Milestone | Outcome | Exit boundary |
| --- | --- | --- | --- |
| 0 | WP-M0 Documentation Gate | 文档、架构、计划、验收、drawio 全部对齐 PV13 首页基线。 | Ready for implementation review only。 |
| 1A | WP-M1A V13 BFF Compatibility | `/bff/v13/*` route ownership 明确：主 BFF route smoke PASS，或 smoke-server-only evidence 被标注为 bounded。 | V13 compatibility route ready for homepage remap。 |
| 1B | WP-M1B PV13 Baseline Homepage | 用户打开项目默认进入 PV13 Light Studio 工作流平台，`workflow-platform` 路由也呈现 PV13。 | PV13 baseline homepage ready for bounded review。 |
| 2 | WP-M2 PV13 Canvas Interaction | 用户可在 PV13 画布缩放、平移、拖动节点、自由连线、取消连线并看到清晰箭头。 | Canvas interaction baseline ready for bounded review。 |
| 3 | WP-M3 Runtime Evidence Loop | 用户从 WorkflowDiff 到 publish/run/human/evidence 在 PV13 工作台中完成，并跑通三个必验业务场景；相对 `WorkflowPlatformMainEntry` 的 PV21 能力不退化。 | Runtime/evidence loop with three business scenarios and PV21 parity ready for bounded review。 |
| 4 | WP-M4 Governed Executor Integration | Agent/Tool/Skill/MCP 能力以受治理方式显示和触发，并覆盖三个业务场景的治理证据；相对 `WorkflowPlatformMainEntry` 的 PV20 能力不退化。 | Governed executor integration with PV20 parity ready for bounded review。 |
| 5A | WP-M5A Business Scenario Productization | 文档总结、代码审查、会议整理从验收路径升级为业务产物闭环，前端静态场景数据改为 DTO/evidence-driven projection。 | Business scenario productization ready for bounded review。 |
| 5B | WP-M5B External App Handoff | PV22 外部接入目标对齐到 WP-M5A 后稳定的 PV13-based Workflow Platform。 | External app implementation may start only after readiness review。 |
| 6 | WP-M6 Frontend Full Data-Driven Closure | PV13 正常路径不再依赖本地业务 mock，场景、节点、Inspector、timeline、quality、evidence、chat 初始上下文来自 BFF/DTO/artifact refs。 | Data-driven normal path ready for bounded review。 |
| 7 | WP-M7 WorkflowSpecGraph Edit/Save/Readback | 用户在 PV13 工作台编辑图、保存草稿、刷新回读并审查 WorkflowDiff。 | Graph edit/save/readback ready for bounded review。 |
| 8 | WP-M8 Publish/Run/Human/Evidence Loop | 用户在 PV13 工作台内发布、运行、人工审批/拒绝并回看证据。 | Runtime and evidence loop ready for bounded review。 |
| 9 | WP-M9 Three Scenario Artifact Closure | 文档总结、代码审查、会议整理生成可审查产物文件和证据链。 | Required business artifacts ready for bounded review。 |
| 10 | WP-M10 Frontend Quality Gate | 失败态、权限态、离线态、校验失败、人工拒绝、取消/重试、a11y、响应式、性能通过验收。 | Frontend quality states ready for bounded review。 |
| 11 | WP-M11 Aggregate Frontend Completion Audit | WP-FR-1 到 WP-FR-20 均有证据映射，缺证即 BLOCKED。 | PRD-defined frontend completion ready for bounded review。 |

当前状态：WP-M1A、WP-M1B、WP-M2、WP-M3、WP-M4、WP-M5A 已通过本阶段 Chrome CDP bounded acceptance。WP-M5B/PV22 readiness refresh 与 PV22-S1..SA 有界实现也已通过，证据包分别见 `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/` 和 `docs/design/V12-V15.x/evidence/pv22-external-app-contract/`。最新用户决策选择 WP-M6 到 WP-M11 作为当前下一阶段，用于完成 PRD 定义的前端页面功能闭环。Path D / production governance、业务 Pack 产品化和开源/商业化准备均后置。

## 2. User-Visible MVP Definition

达到 WP-M3 后，才可以说项目具备“可让人类审查的工作流平台 MVP 候选体验”：

- 首入口是 PV13 Light Studio 工作流平台。
- 画布可用且核心交互可验证。
- WorkflowDiff、发布、运行、人工确认和证据回看在同一 PV13-based 体验中闭环。
- `WorkflowPlatformMainEntry` 当前已经可触达的 PV21 graph/diff/version/run/human/evidence 能力没有被静默移除。
- 文档/知识总结、代码审查/变更风险检查、会议/访谈整理三个业务场景全部有真实输入、运行产物、人工审查和 evidence refs。
- 所有正向能力都有 evidence package。

WP-M3/WP-M4 证据证明三个业务场景路径可自动化验收；WP-M5A 进一步证明三个场景具备机器可读业务输出摘要、artifact refs、human review refs 和 mock boundary。该证据仍不证明三份最终商业业务产物已经完成。

达到 WP-M11 后，才可以在有界审查语境中说“PRD-defined frontend functionality complete for bounded review”：

- 正常路径数据源已从前端静态 mock 收敛到 BFF/DTO/artifact refs。
- 用户可以在 PV13 首页完成图编辑、保存、刷新回读和 Diff 审查。
- 用户可以在同一工作台发布、运行、人工审查和回看证据。
- 三个必验业务场景都有可审查产物和证据链。
- 失败态、权限态、离线态、校验失败、人工拒绝、响应式、a11y 和性能均有证据。
- 所有 PRD 前端功能声明都有 claim-to-evidence 映射。

即便 WP-M5A 已通过，也不能声明 complete Workflow Studio GA、production ready 或 product-grade frontend complete。

## 3. Dependency Order

```text
WP-M0 docs
  -> WP-M1A V13 BFF compatibility
  -> WP-M1B PV13 baseline homepage
  -> WP-M2 PV13 canvas
  -> WP-M3 runtime/evidence
  -> WP-M4 executor integration
  -> WP-M5A business-scenario productization [PASS bounded review]
  -> WP-M5B / PV22 handoff and external app contract [PASS bounded review]
  -> WP-M6 frontend data-driven closure
  -> WP-M7 graph edit/save/readback
  -> WP-M8 publish/run/human/evidence loop
  -> WP-M9 business scenario artifact closure
  -> WP-M10 frontend quality gate
  -> WP-M11 aggregate frontend completion audit
```

PV22 implementation 已在 WP-M5B 后完成 bounded integration review evidence。当前下一步是 WP-M6 到 WP-M11，不得把 PV22 bounded evidence 写成 production ready、external ecosystem complete 或 commercial readiness complete。

## 4. Milestone Exit Artifacts

| Milestone | Required artifacts |
| --- | --- |
| WP-M0 | PRD、target architecture、development plan、milestone roadmap、acceptance gate、gap analysis、task matrix、document support audit、drawio。 |
| WP-M1A | `/bff/v13/*` route ownership report、route smoke、DTO snapshot；当前主 BFF route ownership 已通过。 |
| WP-M1B | PV13 homepage screenshots、route assertion、network log、DTO snapshot、copy scan。 |
| WP-M2 | Canvas action log、edge quality report、zoom/drag/connect/cancel screenshots。 |
| WP-M3 | Runtime inspect report、evidence panel report、human gate report、three-scenario user-scenario report、PV21 capability parity report、claim matrix。 |
| WP-M4 | Executor integration report、approval/denial fixtures、three-scenario governance report、PV20 capability parity report、redaction scan。 |
| WP-M5A | Scenario projection report、business output report、mock reduction report、三业务场景产物 artifacts、HTML productization report。 |
| WP-M5B | PV22 readiness update、SDK/template/reference-app acceptance plan refresh。 |
| WP-M6 | Frontend data source closure report、normal path mock scan、BFF/DTO network log、fallback boundary screenshots。 |
| WP-M7 | Graph edit/save/readback report、before/after DTO snapshots、WorkflowDiff review log、browser action screenshots。 |
| WP-M8 | Runtime inline report、WorkflowVersion/WorkflowInstance/StationRun readback、human action report、evidence panel report。 |
| WP-M9 | Three business artifact manifests、artifact content snapshots、input hash report、human review refs、redaction scan。 |
| WP-M10 | Failure-state matrix、a11y report、responsive screenshots、performance budget report、keyboard interaction log。 |
| WP-M11 | Aggregate frontend completion audit、claim-to-evidence matrix、No False Green scan、final human-readable HTML report。 |
