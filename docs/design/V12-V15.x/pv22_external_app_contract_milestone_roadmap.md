# PV22 External App Contract Milestone Roadmap

用途：把 PV22 外部应用接入契约拆解成可验收里程碑。
阅读对象：项目管理、开发、测试、审计人员。
边界：本文是路线图，不是实现证据。

| Milestone | Scope | Exit evidence | Blocker if missing |
| --- | --- | --- | --- |
| M0 Readiness | 文档包、风险、任务矩阵、验收门槛。 | readiness audit Go。 | 不能进入实现。 |
| M0.5 WP-M5A Gate | 工作流平台业务场景产品化、真实业务产物、mock reduction。 | WP-M5A PASS evidence 已存在；如未来重跑失败则需重新审计。 | PV22 不得进入 M1。 |
| M0.6 WP-M5B Readiness Refresh | 将 PV22 接入目标对齐到 PV13-based workflow platform host surface。 | readiness audit GO，且不替代 WP-M5A 业务证据。 | PV22 不得进入 M1。 |
| M1 Registry Freeze | external method/event/error/capability subset。 | registry snapshot。 | SDK 和 template 无稳定目标。 |
| M2 SDK Smoke | Python/TypeScript 最小路径。 | SDK smoke report。 | 外部开发者无法验证。 |
| M3 BFF Template Smoke | full/minimal template。 | route boundary report。 | 浏览器安全边界不可审。 |
| M4 Auth Negative Fixtures | token/origin/scope/capability/method denial。 | expected-denial report。 | 安全边界不可审。 |
| M5 Reference App | 外部 app E2E。 | browser/API report。 | 无真实接入体验。 |
| M6 Aggregate Acceptance | 汇总证据、红线、redaction。 | PV22 acceptance report。 | 不能给 bounded integration review 声明。 |

推荐顺序：M0 -> M0.5 -> M0.6 -> M1 -> M2 -> M3 -> M4 -> M5 -> M6。

PV22 的 M1 之后里程碑不得绕过 M0.5/M0.6。若未来重新验收 WP-M5A 失败，PV22 不能继续新增正向完成声明，只能保留已有 bounded evidence 并回到 readiness audit。
