# PV20-S4 Approval Handoff Audit

用途：进入 PV20-S4 实质开发前审计 approval handoff 与 denied mutation 风险。
阅读对象：开发、测试、审计人员。
边界：本文不是完成证据；完成证据只能来自测试和 PV20 evidence package。

## Audit Conclusion

状态：READY FOR IMPLEMENTATION。

PV20-S3B 已经通过 `connector.submit` 产生 approval，并通过 `approval.respond` 完成本地 MCP fixture 执行。S4 可以在此基础上补齐显式 denial fixtures 和 approval readback，不需要开放新的高风险执行面。

## Risk Controls

| Risk | Severity | Control |
| --- | --- | --- |
| Agent 自行批准动作 | Critical | `source=agent` 被 BFF 和 executor guard 拒绝。 |
| 无用户确认触发执行 | Critical | `user_confirmed=true` 是所有 execution route 的硬门槛。 |
| 误称完整审批 UI | Major | S4 只声明 approval handoff evidence，不声明 browser approval UX complete。 |
| 未知 MCP/tool 越权 | Major | allowlist 拒绝 unknown connector/tool。 |
| 直接 runtime mutation | Major | Envelope 保留 `approval.respond`、`workflow.template.publish` 等 forbidden operation refs。 |

## Start Decision

可以进入 S4：以现有 PV20 execution routes 为对象补充 denial fixtures、approval refs readback 和验收 runner 检查。
