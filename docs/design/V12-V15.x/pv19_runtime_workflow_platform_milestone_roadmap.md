# PV19 Runtime Workflow Platform Milestone Roadmap

用途：定义 PV19 从文档冻结到阶段出门验收的里程碑。
阅读对象：产品、开发、测试、审计人员。
边界：本文是路线图，不是实现证据，不产生 PASS 声明。

## 1. Milestone Summary

| Milestone | Goal | Exit condition |
| --- | --- | --- |
| M0 文档冻结 | 完成 PV19 文档包和 drawio。 | 文档存在、口径一致、drawio <= 8 页、No False Green PASS。 |
| M1 工作台入口 | 用户进入真实工作台和可见 canvas。 | browser screenshot、state DTO、route log PASS。 |
| M2 编排与发布 | 图编辑、WorkflowDiff、版本发布闭环。 | graph roundtrip、publish report、audit refs PASS。 |
| M3 Runtime 运行 | 发布版本可启动并被 inspect。 | runtime event、run status、artifact refs PASS。 |
| M4 人工交互 | pending human gate 可被处理并影响状态。 | state transition、audit trail、negative fixtures PASS。 |
| M5 证据审查 | 同一工作台可审查 artifacts、trace、quality、audit。 | evidence summary、claim matrix、redaction PASS。 |
| M6 聚合验收 | 完成自动化验收和 PRD/架构审计。 | acceptance runner、audit closure、allowed claim PASS。 |

## 2. Human Review Gates

| Gate | Reviewer checks |
| --- | --- |
| G0 文档审查 | 目标体验是否清晰，是否存在过度承诺。 |
| G1 架构审查 | 代码实体、分层和交互是否具体，是否保持平台通用性。 |
| G2 UX 审查 | 工作台入口、画布、人工节点、证据面板是否能让人理解。 |
| G3 Evidence 审查 | 每个正向声明是否能映射到运行证据。 |

## 3. Recommended Implementation Order

1. 先修正工作台入口和 state DTO，确保用户能打开真实工作台。
2. 再打通 graph validation、WorkflowDiff 和 publish readback。
3. 再接 runtime-backed run/inspect。
4. 再加入 human gate 状态机和 audit trail。
5. 最后聚合 evidence review 和 acceptance runner。

## 4. Deferred Work

- 生产多租户、SLA、计费、完整部署恢复。
- 完整插件市场和外部 App SDK。
- 完整 Agent executor。
- 全量业务 Pack 产品化。

