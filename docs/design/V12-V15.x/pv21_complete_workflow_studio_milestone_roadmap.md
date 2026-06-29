# PV21 Complete Workflow Studio Milestone Roadmap

用途：定义 PV21 的里程碑、阶段出口和交付物顺序。
阅读对象：产品、项目管理、开发、测试、审计人员。
边界：本文是路线图，不是实现证据；不得据此声明完整工作流工作台已完成。

## 1. Milestone Summary

| Milestone | Name | Exit outcome | Exit artifacts |
| --- | --- | --- | --- |
| M0 | Documentation readiness | PV21 规格、架构、任务、门槛和 drawio 可支撑开发。 | PV21 doc package、drawio、readiness audit。 |
| M1 | Studio state and entry | 默认入口显示真实工作台骨架和 BFF state。 | State DTO snapshot、home screenshot、route log。 |
| M2 | Canvas edit and validation | 用户可编辑 graph、Inspector 和 validation。 | Graph roundtrip、validation report、negative fixtures。 |
| M3 | Diff, version and rollback | 用户可审查 diff、发布版本、回滚和看历史。 | Diff report、version report、rollback audit refs。 |
| M4 | Run, inspect and human gate | 用户可运行版本、查看 inspect、处理 human gate。 | Runtime report、human action transition report。 |
| M5 | Evidence and UX closure | 用户可审查 evidence，工作台 UX 达到有界审查标准。 | Evidence report、screenshots、UX review、claim/redaction scan。 |
| M6 | Aggregate acceptance | PV21 进入有界审查候选状态。 | Acceptance-data、artifact-manifest、audit closure。 |

## 2. Milestone Dependencies

```text
M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> M6
```

- M2 不能跳过 M1，因为画布需要 BFF state 和 node library。
- M3 不能跳过 M2，因为 diff/publish 必须基于后端 graph readback。
- M4 不能跳过 M3，因为 run 必须基于已发布 WorkflowVersion。
- M5 不能跳过 M4，因为 evidence 必须绑定真实 WorkflowInstance / StationRun。

## 3. Outbound Scope Mapping

| Future stage | Deferred from PV21 |
| --- | --- |
| PV22 Path B | 外部 App SDK、BFF template、reference app、capability token contract。 |
| PV23 Path D | 生产多租户隔离、凭证生命周期、审计留存和部署恢复硬化。 |
| PV24 Business Pack | Knowledge/Meeting/Interview/Investment/Video 的商业产品化。 |
| PV25 Commercial | 开源发布、许可、计费、限额、商业文档和发布流水线。 |

## 4. Milestone Exit Review

每个 milestone 出口必须记录：

- 完成的 PRD requirements。
- 涉及的 concrete code entities。
- 正向和负向验收结果。
- 未完成项和是否阻塞下一步。
- No False Green / redaction 状态。

