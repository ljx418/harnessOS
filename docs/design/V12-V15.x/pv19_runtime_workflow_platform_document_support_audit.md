# PV19 Runtime Workflow Platform Document Support Audit

用途：评估 PV19 当前文档是否足够支撑本阶段全部开发、自动化验收和出门审计。
阅读对象：产品、架构、开发、测试、审计人员。
边界：本文是文档支撑审计，不是实现证据。

## 1. Audit Conclusion

结论：经过本轮补强后，PV19 文档可以支撑后续进入实现阶段。

理由：

- PRD 已定义目标体验、目标用户、功能要求、No-Go 和允许声明。
- 目标架构已锁定 Browser、Client、BFF、Gateway、WorkflowStore、Runtime、Human loop 和 Evidence 的具体代码实体。
- BFF DTO contract 已固定 `/bff/pv19/*` route set，避免用 V13/PV17/PV18 test-only route 冒充 PV19 证据。
- implementation task matrix 已把每个子阶段映射到具体代码实体和证据文件。
- acceptance gate 和 runner spec 已定义 PASS/FAIL、负向用例、输出证据和阻断条件。
- drawio 已用 7 页表达目标、差异、架构、用户路径、开发验收、里程碑和出门条件。

## 2. Closed Findings

| Finding | Previous risk | Closure |
| --- | --- | --- |
| 入口不够明确 | 后续实现可能继续交付空白根路径。 | 锁定 `?studio=pv19-runtime-workflow-platform`，根路径不得作为空白交付体验。 |
| BFF route 可替代性过强 | 后续可能复用旧阶段 route 冒充 PV19。 | DTO contract 固定 `/bff/pv19/*`，禁止用 V13/PV17/PV18 route 作为 PV19 完成证据。 |
| Human gate 表达不明确 | 后续可能新增业务专用节点模型或只做 UI toast。 | 锁定现有 station approval fields 和 waiting states；human action 必须更新后端状态。 |
| 业务样例不明确 | 后续可能只做业务页面或污染平台核心。 | Knowledge OPC 为主样例，folder-summary/reference workflow 为非 Knowledge 复用检查。 |
| 任务粒度不够 | 自动化开发仍需自行拆任务。 | 新增 implementation task matrix。 |

## 3. Residual Risks

| Risk | Level | Mitigation |
| --- | --- | --- |
| Existing workflow runtime may not support every graph node kind needed by Studio. | Medium | PV19-S2 先做 graph validation/runtime readiness，不能跳到 UI polish。 |
| Human action state transition may require careful coordination across approval, handoff and workflow stores. | Medium | PV19-S5 单独成阶段，before/after state 和 audit trail 为硬门槛。 |
| Knowledge OPC primary sample may bias implementation toward Knowledge-specific logic. | Medium | folder-summary/reference workflow reuse check and platform generality review are mandatory。 |
| Browser automation may depend on local Chrome availability. | Low | runner spec keeps CDP and Playwright paths; failure must be reported as environment blocker, not acceptance PASS。 |

## 4. No Unmitigated High Risk

当前未发现必须让用户重新选择技术路线的高风险。推荐继续执行 PV19 当前路线，不需要切换到 Path B、Path D 或单独 Complete Agent Executor。

如果实现阶段发现 runtime 无法在合理范围内承接 WorkflowVersion -> WorkflowInstance -> human gate，则备选路线为：

| Route | Pros | Cons |
| --- | --- | --- |
| A. 保持 PV19，先实现最小 runtime closed loop | 最符合当前目标，能直接证明平台闭环。 | 需要严控范围，只支持少量节点种类。 |
| B. 先做 Complete Agent Executor | 可降低后续 Agent 节点执行风险。 | 会推迟工作台闭环，用户仍看不到完整平台路径。 |
| C. 先做 Complete Workflow Studio | 可提升画布体验完整度。 | 容易继续停留在设计/发布层，运行和人工交互仍缺证据。 |

推荐路线仍是 A。

## 5. Readiness Decision

PV19 文档已足够支撑自动化开发和阶段验收。进入实现前仍需人工审核 drawio，确认方向没有偏移或过度承诺。
