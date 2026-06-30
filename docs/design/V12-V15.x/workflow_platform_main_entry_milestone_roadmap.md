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
| 5 | WP-M5 External App Handoff | PV22 外部接入目标对齐到稳定 PV13-based Workflow Platform。 | External app implementation may start。 |

当前状态：WP-M1A、WP-M1B、WP-M2、WP-M3、WP-M4 已通过本阶段 Chrome CDP bounded acceptance。证据包见 `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/`。

## 2. User-Visible MVP Definition

达到 WP-M3 后，才可以说项目具备“可让人类审查的工作流平台 MVP 候选体验”：

- 首入口是 PV13 Light Studio 工作流平台。
- 画布可用且核心交互可验证。
- WorkflowDiff、发布、运行、人工确认和证据回看在同一 PV13-based 体验中闭环。
- `WorkflowPlatformMainEntry` 当前已经可触达的 PV21 graph/diff/version/run/human/evidence 能力没有被静默移除。
- 文档/知识总结、代码审查/变更风险检查、会议/访谈整理三个业务场景全部有真实输入、运行产物、人工审查和 evidence refs。
- 所有正向能力都有 evidence package。

即便达到 WP-M3，也不能声明 complete Workflow Studio GA、production ready 或 product-grade frontend complete。

## 3. Dependency Order

```text
WP-M0 docs
  -> WP-M1A V13 BFF compatibility
  -> WP-M1B PV13 baseline homepage
  -> WP-M2 PV13 canvas
  -> WP-M3 runtime/evidence
  -> WP-M4 executor integration
  -> WP-M5 PV22 handoff
```

PV22 implementation 不应早于 WP-M5。当前下一步是 WP-M5/PV22 readiness update，而不是继续扩张 WP-M1..WP-M4。

## 4. Milestone Exit Artifacts

| Milestone | Required artifacts |
| --- | --- |
| WP-M0 | PRD、target architecture、development plan、milestone roadmap、acceptance gate、gap analysis、task matrix、document support audit、drawio。 |
| WP-M1A | `/bff/v13/*` route ownership report、route smoke、DTO snapshot；当前主 BFF route ownership 已通过。 |
| WP-M1B | PV13 homepage screenshots、route assertion、network log、DTO snapshot、copy scan。 |
| WP-M2 | Canvas action log、edge quality report、zoom/drag/connect/cancel screenshots。 |
| WP-M3 | Runtime inspect report、evidence panel report、human gate report、three-scenario user-scenario report、PV21 capability parity report、claim matrix。 |
| WP-M4 | Executor integration report、approval/denial fixtures、three-scenario governance report、PV20 capability parity report、redaction scan。 |
| WP-M5 | PV22 readiness update、SDK/template/reference-app acceptance plan refresh。 |
