# PV22 External App Contract Current Gap Analysis

用途：说明当前实现与 PV22 外部应用接入契约目标之间的差距。
阅读对象：产品、架构、开发、测试、审计人员。
边界：本文是 gap 文档，不是实现证据。

## 1. Baseline

| Baseline | What exists | What is missing |
| --- | --- | --- |
| SDK | `sdk/python`、`sdk/typescript` 已存在。 | 外部 app contract smoke 和 evidence 未冻结。 |
| BFF templates | `templates/bff/fastapi`、`fastapi_minimal` 已存在。 | 统一验收、route denylist 和 error mapping evidence 未完成。 |
| AppProfile | built-in profiles 已存在。 | external profile compatibility policy 和 token fixture 不完整。 |
| Auth | capability token、origin、scope、capability 校验存在。 | PV22 negative fixture matrix 未形成阶段证据。 |
| Reference app | examples/template 资产存在。 | 作为外部 App 的端到端接入证据未形成。 |

## 2. Gap Matrix

| Gap | Risk | PV22 mitigation |
| --- | --- | --- |
| Contract subset 不清 | 外部开发者不知道哪些接口稳定。 | M1 registry freeze。 |
| SDK smoke 不统一 | Python/TS 行为漂移。 | M2 双 SDK smoke。 |
| BFF template 无验收 | 业务 App 可能绕过安全边界。 | M3 template route boundary。 |
| Token negative 不完整 | scope/origin/capability 越权风险。 | M4 expected denial fixtures。 |
| Reference app 缺证据 | 无法证明外部接入体验。 | M5 E2E evidence。 |
| No False Green | 误报生产或生态完成。 | M6 claim scan。 |

## 3. Document Support Assessment

PV22-R0 文档包完成后，应足以支撑实现阶段开工；但在 SDK smoke、template smoke 和 reference app E2E 通过前，不得宣称 PV22 完成。

