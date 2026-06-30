# Workflow Platform Main Entry Current Gap Analysis

用途：说明当前项目距离“PV13-based 工作流平台首页 MVP 候选体验”的差距，并记录 WP-M1A 到 WP-M4 当前关闭状态。
边界：本文是 gap 文档和 bounded evidence 索引，不证明生产级平台、完整 Studio GA 或生产可用。

## 1. Baseline

| Baseline | What it proves | What it does not prove |
| --- | --- | --- |
| V13 / PV13 editable Studio pilot | 有界 graph editing / WorkflowDiff pilot；当前最接近用户认可的 Light Studio 工作流平台体验。 | 不证明运行闭环、完整 Studio、产品级画布或生产可用。 |
| PV19 runtime workflow platform | 有界 publish/run/human/evidence loop。 | 不证明完整画布交互和 Agent executor 产品化。 |
| PV20 bounded Agent executor | 受治理 skill/tool/MCP fixture execution path。 | 不证明 unrestricted Agent executor 或生产调度。 |
| PV21 bounded Studio candidate | graph save/validate/diff、publish/rollback/run/human/evidence review。 | 不再作为首页视觉基线；不证明 complete Workflow Studio GA。 |
| PV22 R0 docs/readiness | 外部应用契约目标和门禁明确。 | 不证明 SDK/template/reference app implementation。 |

## 2. Gap Matrix

| Gap | Current state | Target state | Risk | Mitigation |
| --- | --- | --- | --- | --- |
| WP-G1 首页基线偏移 | 已关闭：默认 `workflow-platform` route 映射到 `V13EditableStudio`。 | 无 query 和 `workflow-platform` 均进入 `V13EditableStudio`。 | Low | Route assertion + PV13 baseline screenshots。 |
| WP-G2 阶段语义 | V13/PV19/PV20/PV21/PV22 容易互相混淆。 | PV13 是前端基线；PV19/PV20/PV21 是能力来源；PV22 后置。 | High | 命名表、drawio、claim scan。 |
| WP-G3 V13 BFF compatibility | 已关闭：主 API router 提供正式 `/bff/v13/*` compatibility routes。 | WP-M1A 明确 route ownership：主 BFF route smoke PASS。 | Low | `tests/test_v13_workflow_platform_bff.py` + route ownership report。 |
| WP-G4 画布体验 | 已关闭当前门槛：PV13 页面支持缩放、节点拖拽、自由连线、取消连线和箭头可见性验收。 | 以 PV13 力感画布为基线继续硬化缩放、拖拽、连线和箭头。 | Medium | WP-M2 Canvas action log + screenshots + edge quality report。 |
| WP-G5 运行闭环融合 | 已关闭当前门槛：PV21 parity loop 在 PV13 页面可触达并通过验收。 | WorkflowDiff -> publish -> run -> human -> evidence 在 PV13 工作台中完成。 | Medium | WP-M3 runtime/evidence acceptance。 |
| WP-G6 Executor 产品化 | 已关闭当前门槛：PV20 governed executor loop 在 PV13 页面可触达并通过验收。 | 受治理 Agent/Tool/Skill/MCP 在 PV13 资源/Inspector/证据面板中呈现。 | Medium | WP-M4 integration and copy guard。 |
| WP-G7 能力不退化 | 已关闭当前门槛：capability parity report 记录 PV21/PV20 能力未静默丢失。 | PV13-based 工作台继承保存、校验、Diff、发布、回滚、运行、人工门禁、证据和受治理执行器能力。 | Low | WP-M3/WP-M4 capability parity report。 |
| WP-G8 外部接入顺序 | PV22 已规划，但目标接入面可能不够稳定。 | PV22 接入稳定 PV13-based Workflow Platform，而不是分散 stage page。 | Medium | WP-M5 readiness update。 |

## 3. Document Support Assessment

当前已有 PV19/PV20/PV21/PV22 文档足以说明各 bounded stage，但旧 WP-M0 文档仍有偏差：

- 旧文档倾向“优先复用 PV21 shell，再吸收 V13 canvas”，这与用户确认的 PV13 首页基线不一致。
- 旧目标架构把 `WorkflowPlatformMainEntry` 写成待新增/目标 shell，但用户已明确当前入口体验退步。
- 旧验收门槛没有把“默认首页必须进入 PV13 Light Studio”作为 WP-M1 硬门槛。

本轮实现后，文档和证据可支撑 WP-M1A 到 WP-M4 bounded acceptance 复审：

- PRD 明确 `V13EditableStudio.tsx` 和 `v13-editable-studio.css` 是前端基线。
- Target architecture 明确 `App.tsx -> WorkflowStudioLayout -> V13EditableStudio` 是目标首页路径。
- Development plan 记录 WP-M1A 到 WP-M4 当前 PASS，并指向 evidence package。
- Acceptance gate 明确 `WorkflowPlatformMainEntry` 继续作为默认首页即 FAIL。
- Acceptance runner 明确 WP-M3/WP-M4 必须输出 `workflow-platform-capability-parity-report.json`，证明 PV21/PV20 能力未静默退化。
- Drawio 以代码实体和颜色状态呈现当前架构与目标架构差异。

文档仍不能替代后续 WP-M5/PV22、生产治理和产品级体验验收。

## 4. Claim Risk

| Claim risk | Level | Reason |
| --- | --- | --- |
| 把 PV13 首页基线写成 product-grade frontend complete | High | PV13 是可审查基线，不是产品级完成。 |
| 把 PV21 写成 complete Workflow Studio GA | High | PV21 名称容易误导，必须持续标注 bounded candidate。 |
| 把画布优化写成 complete Workflow Studio ready | High | 画布体验是专项硬化，不是 GA。 |
| 把 PV20 写成 Agent executor ready | High | PV20 是 bounded governed path，不是 unrestricted automation。 |
| 把 WP-M1A..WP-M4 写成完整平台完成 | Medium | 当前只是 bounded review evidence。 |

## 5. Conclusion

WP-M1A 到 WP-M4 的当前差距已按 bounded review 范围关闭，工作流平台 MVP 候选体验已达到可让人类审查的程度。剩余主线不应继续扩张本阶段，而应进入 WP-M5/PV22 readiness update、PV22-S1 外部应用契约实现评估，以及后续生产治理/产品级体验阶段。
