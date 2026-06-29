# PV20-S3 Tool / MCP Execution Audit

用途：记录 PV20-S3A / PV20-S3B 实现后审计结论。
阅读对象：开发、测试、审计人员。
边界：本文不是完整 Agent executor 证据；S3A 只证明本地 read-only tool，S3B 只证明 allowlisted local MCP fixture，不证明 unrestricted MCP。

## Conclusion

状态：PV20-S3A PASS FOR BOUNDED REVIEW；PV20-S3B PASS FOR BOUNDED REVIEW。

S3A 已通过自动化验收，因为它只使用本地 read-only artifact metadata tool/read-model，不需要外部服务。S3B 已使用本地 `data_service_mcp.knowledge_query_v2` stdio fixture，通过 `connector.submit`、`approval.respond` 和 retry context 完成自动化验收；这仍不等于 unrestricted MCP execution ready。

## S3A Evidence

| Item | Result | Evidence |
| --- | --- | --- |
| User confirmation | PASS | `/bff/pv20/runs/{run_id}/agent-tool-executions` requires `user_confirmed=true` |
| Tool boundary | PASS | allowlist only permits `artifact.metadata.read` |
| Runtime binding | PASS | StationRun metadata readback and artifact metadata refs |
| MCP refs | PASS | `mcp_call_refs=[]` |
| False green control | PASS | no MCP PASS claim; unrestricted tool execution remains not claimed |

## S3B Evidence

| Item | Result | Evidence |
| --- | --- | --- |
| User confirmation | PASS | `/bff/pv20/runs/{run_id}/agent-mcp-executions` requires `user_confirmed=true` |
| MCP allowlist | PASS | only `data_service_mcp.knowledge_query_v2` is accepted |
| Gateway connector runtime | PASS | execution uses `connector.submit` |
| Approval handoff skeleton | PASS | execution creates connector approval and resolves it through `approval.respond` |
| stdio MCP fixture | PASS | local JSON-RPC stdio `tools/call` produces artifact-backed evidence |
| False green control | PASS | unrestricted MCP execution remains not claimed |

## Risk Review

| Risk | Severity | Control |
| --- | --- | --- |
| Tool 变成任意 shell/filesystem/network | Critical | S3A allowlist 仅允许 read-only metadata/read-model tool。 |
| MCP 用 mock 冒充真实执行 | Major | S3B 使用本地 JSON-RPC stdio fixture；不得直接写入 PASS 结果。 |
| Browser 绕过 BFF | Major | 所有 route 限定 `/bff/pv20`。 |
| Raw artifact/secret 泄露 | Major | 只读 metadata，禁止 raw content。 |
| source=agent 触发工具执行 | Major | BFF user confirmation + executor source guard。 |

## Start Decision

- S3A 已完成：allowlisted local read-only tool/read-model execution。
- S3B 已完成：allowlisted local `data_service_mcp.knowledge_query_v2` stdio fixture execution。
- 下一步进入 PV20-S4：approval handoff UX 和 denied mutation fixtures。
