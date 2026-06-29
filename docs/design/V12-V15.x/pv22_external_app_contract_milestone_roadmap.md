# PV22 External App Contract Milestone Roadmap

用途：把 PV22 外部应用接入契约拆解成可验收里程碑。
阅读对象：项目管理、开发、测试、审计人员。
边界：本文是路线图，不是实现证据。

| Milestone | Scope | Exit evidence | Blocker if missing |
| --- | --- | --- | --- |
| M0 Readiness | 文档包、风险、任务矩阵、验收门槛。 | readiness audit Go。 | 不能进入实现。 |
| M1 Registry Freeze | external method/event/error/capability subset。 | registry snapshot。 | SDK 和 template 无稳定目标。 |
| M2 SDK Smoke | Python/TypeScript 最小路径。 | SDK smoke report。 | 外部开发者无法验证。 |
| M3 BFF Template Smoke | full/minimal template。 | route boundary report。 | 浏览器安全边界不可审。 |
| M4 Auth Negative Fixtures | token/origin/scope/capability/method denial。 | expected-denial report。 | 安全边界不可审。 |
| M5 Reference App | 外部 app E2E。 | browser/API report。 | 无真实接入体验。 |
| M6 Aggregate Acceptance | 汇总证据、红线、redaction。 | PV22 acceptance report。 | 不能给 bounded integration review 声明。 |

推荐顺序：M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> M6。

