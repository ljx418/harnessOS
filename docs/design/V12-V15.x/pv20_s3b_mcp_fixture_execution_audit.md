# PV20-S3B MCP Fixture Execution Audit

用途：进入 PV20-S3B 实质开发前审计 MCP fixture、审批链路和虚假验收风险。
阅读对象：开发、测试、审计人员。
边界：本文不是完成证据；完成证据只能来自测试和 `evidence/pv20-complete-agent-executor/`。

## Audit Conclusion

状态：READY FOR IMPLEMENTATION WITH STRICT FIXTURE BOUNDARY。

可进入实现的原因：仓库已有 `ConnectorExecutionRuntime`、`data_service_mcp` stdio connector contract、`connector.submit`、approval store 和 `approval.respond`。S3B 可以在测试/验收 runner 内创建本地 stdio MCP fixture，并通过真实 Gateway connector runtime 调用，不需要生产凭证或外部网络。

## Risk Controls

| Risk | Severity | Control |
| --- | --- | --- |
| Mock 冒充 MCP PASS | Critical | Fixture 必须通过 JSON-RPC stdio `tools/call` 返回，不能直接写结果。 |
| Agent 越权批准外部动作 | Critical | BFF 只在 `user_confirmed=true` 下执行，并记录 approval refs；后续 S4 继续硬化人工交互体验。 |
| 任意 MCP/tool 打开 | Critical | allowlist 仅允许 `data_service_mcp.knowledge_query_v2`。 |
| 生产凭证或网络依赖 | Major | Fixture 使用临时目录、当前 Python、network_policy=none。 |
| 原始 payload 泄露 | Major | Evidence 只保留 refs、job/artifact ids 和 redacted summaries。 |

## Pre-Implementation Decision

- 可以实现 S3B：使用本地临时 `data_service.mcp_stdio` fixture，并通过 `connector.submit` + `approval.respond` 完成真实 stdio 调用。
- 不允许扩展到任意 connector、任意 tool、shell、filesystem raw read、外部网络或生产凭证。
