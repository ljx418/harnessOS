# Workflow Platform Main Entry Current Gap Analysis

用途：说明当前项目距离“工作流平台首入口 MVP 候选体验”的差距。
边界：本文是 gap 文档，不是实现证据。

## 1. Baseline

| Baseline | What it proves | What it does not prove |
| --- | --- | --- |
| V13 editable Studio pilot | 有界 graph editing / WorkflowDiff pilot。 | 不证明运行闭环、完整 Studio 或产品级画布。 |
| PV19 runtime workflow platform | 有界 publish/run/human/evidence loop。 | 不证明完整画布交互和 Agent executor 产品化。 |
| PV20 bounded Agent executor | 受治理 skill/tool/MCP fixture execution path。 | 不证明 unrestricted Agent executor 或生产调度。 |
| PV21 bounded Studio candidate | 默认 Studio entry、graph save/validate/diff、publish/rollback/run/human/evidence review。 | 不证明 complete Workflow Studio GA、product-grade frontend 或 production ready。 |
| PV22 R0 docs/readiness | 外部应用契约目标和门禁明确。 | 不证明 SDK/template/reference app implementation。 |

## 2. Gap Matrix

| Gap | Current state | Target state | Risk | Mitigation |
| --- | --- | --- | --- | --- |
| WP-G1 首入口定位 | PV21 已接近默认入口，但文档主线仍指向 PV22 实现。 | 工作流平台首入口成为 PV22 前置目标。 | High | WP-M0 更新 source-of-truth 文档。 |
| WP-G2 阶段语义 | V13/PV19/PV20/PV21/PV22 容易互相混淆。 | WP-M0 只做首入口对齐，PV 阶段保持历史证据边界。 | High | 命名表和 claim scan。 |
| WP-G3 画布体验 | 用户反馈仍有缩放、拖拽区域、取消连线、箭头可见性问题。 | WP-M2 专项验收核心画布交互。 | High | Canvas action log + screenshots + edge quality report。 |
| WP-G4 运行闭环融合 | PV19/PV21 能力存在但产品体验仍需整合。 | WorkflowDiff -> publish -> run -> human -> evidence 同屏。 | High | WP-M3 runtime/evidence acceptance。 |
| WP-G5 Executor 产品化 | PV20 evidence path 有界，但 UI 可能仍像独立阶段页。 | 受治理 Agent/Tool/Skill/MCP 在工作流平台资源面板中呈现。 | Medium | WP-M4 integration and copy guard。 |
| WP-G6 外部接入顺序 | PV22 已规划，但目标接入面可能不够稳定。 | PV22 接入 Workflow Platform，而不是分散 stage page。 | Medium | WP-M5 readiness update。 |

## 3. Document Support Assessment

当前已有 PV19/PV20/PV21/PV22 文档足以说明各 bounded stage，但不足以单独支撑“工作流平台首入口”后续开发，因为：

- 缺少一个明确把 PV21 首入口、V13 画布、PV19 运行闭环、PV20 executor 和 PV22 外部接入串起来的 PRD。
- 缺少以具体代码实体为中心的首入口目标架构图。
- 缺少针对用户反馈画布问题的专项验收门槛。
- 缺少把 PV22 implementation 推迟到首入口对齐后的主线说明。

新增 WP-M0 文档包后，文档应能支撑后续实现计划制定，但仍不能替代真实代码实现和 E2E evidence。

本轮补充后，WP-M0 还增加了：

- `workflow_platform_main_entry_bff_dto_contract.md`：锁定 route allowlist、DTO snapshot、browser denylist 和兼容策略。
- `workflow_platform_main_entry_acceptance_runner_spec.md`：定义自动化验收 runner 场景、输出和 PASS/FAIL/NO_GO 规则。
- `workflow_platform_main_entry_implementation_readiness_audit.md`：给出实现前 Go/No-Go、残余风险和 fallback routes。

因此，当前文档支撑度从“可支撑实现计划制定”提升为“可支撑 WP-M1 自动化开发启动，并可支撑 WP-M2/WP-M4 详细计划执行”。后续仍必须通过真实端到端验收才能证明目标达成。

## 4. Claim Risk

| Claim risk | Level | Reason |
| --- | --- | --- |
| 把 PV21 写成 complete Workflow Studio GA | High | PV21 名称容易误导，必须持续标注 bounded candidate。 |
| 把画布优化写成 product-grade frontend complete | High | 画布体验是专项硬化，不是产品级完成。 |
| 把 PV20 写成 Agent executor ready | High | PV20 是 bounded governed path，不是 unrestricted automation。 |
| 把 WP-M0 写成 implementation complete | Medium | 本阶段只有文档开发。 |

## 5. Conclusion

当前项目仍存在未完成开发计划。WP-M0 文档包完成后，可以支撑后续首入口实现开发计划；但只有后续 WP-M1 到 WP-M4 真实实现和验收通过后，才能说工作流平台 MVP 候选体验达到人类审查程度。
