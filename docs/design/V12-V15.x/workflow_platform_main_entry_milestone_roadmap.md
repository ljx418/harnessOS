# Workflow Platform Main Entry Milestone Roadmap

用途：定义从当前 PV21/PV22 状态到工作流平台首入口 MVP 的里程碑。
边界：本文是路线图，不是实现证据。

## 1. Roadmap

| Order | Milestone | Outcome | Exit boundary |
| --- | --- | --- | --- |
| 0 | WP-M0 Documentation Gate | 文档、架构、计划、验收、drawio 全部对齐工作流平台首入口。 | Ready for implementation review only。 |
| 1 | WP-M1 First Entry | 用户打开项目默认进入工作流平台，不再依赖分散 query page。 | Main-entry shell ready for bounded review。 |
| 2 | WP-M2 Canvas Interaction | 用户可缩放、平移、拖动节点、自由连线、取消连线并看到清晰箭头。 | Canvas interaction baseline ready for bounded review。 |
| 3 | WP-M3 Runtime Evidence Loop | 用户从 WorkflowDiff 到 publish/run/human/evidence 在同一工作台完成，并跑通三个必验业务场景。 | Runtime/evidence loop with three business scenarios ready for bounded review。 |
| 4 | WP-M4 Governed Executor Integration | Agent/Tool/Skill/MCP 能力以受治理方式显示和触发，并覆盖三个业务场景的治理证据。 | Governed executor integration ready for bounded review。 |
| 5 | WP-M5 External App Handoff | PV22 外部接入目标对齐到 Workflow Platform。 | External app implementation may start。 |

## 2. User-Visible MVP Definition

达到 WP-M3 后，才可以说项目具备“可让人类审查的工作流平台 MVP 候选体验”：

- 首入口是工作流平台。
- 画布可用且核心交互可验证。
- WorkflowDiff、发布、运行、人工确认和证据回看在同一体验中闭环。
- 文档/知识总结、代码审查/变更风险检查、会议/访谈整理三个业务场景全部有真实输入、运行产物、人工审查和 evidence refs。
- 所有正向能力都有 evidence package。

即便达到 WP-M3，也不能声明 complete Workflow Studio GA、production ready 或 product-grade frontend complete。

## 3. Dependency Order

```text
WP-M0 docs
  -> WP-M1 entry
  -> WP-M2 canvas
  -> WP-M3 runtime/evidence
  -> WP-M4 executor integration
  -> WP-M5 PV22 handoff
```

PV22 implementation 不应早于 WP-M0 通过。若用户明确要求优先 PV22，必须在 readiness audit 中记录风险。

## 4. Milestone Exit Artifacts

| Milestone | Required artifacts |
| --- | --- |
| WP-M0 | PRD、target architecture、development plan、milestone roadmap、acceptance gate、gap analysis、task matrix、document support audit、drawio。 |
| WP-M1 | Browser screenshots、route assertion、network log、DTO snapshot、copy scan。 |
| WP-M2 | Canvas action log、edge quality report、zoom/drag/connect/cancel screenshots。 |
| WP-M3 | Runtime inspect report、evidence panel report、human gate report、three-scenario user-scenario report、claim matrix。 |
| WP-M4 | Executor integration report、approval/denial fixtures、three-scenario governance report、redaction scan。 |
| WP-M5 | PV22 readiness update、SDK/template/reference-app acceptance plan refresh。 |
