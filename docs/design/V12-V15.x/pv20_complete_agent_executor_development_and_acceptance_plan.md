# PV20 Complete Agent Executor Development And Acceptance Plan

用途：把 PV20 受治理 Agent executor 候选能力拆成开发、验收和审计步骤。
阅读对象：开发、测试、产品、审计人员。
边界：本文是开工计划；在代码和证据生成前不产生任何 PASS 声明。

## 1. Stage Outline

| Stage | 用户可见效果 | 开发对象 | 验收证据 |
| --- | --- | --- | --- |
| PV20-R0 | Reviewer 看到 PV20 目标、架构、红线、任务矩阵和验收门槛。 | PRD、target architecture、plan、gate、readiness audit。 | 文档存在性、No False Green、风险闭环。 |
| PV20-S1 | 工作台能显示 Agent 节点 execution contract。 | AgentExecutionEnvelope DTO、StationRun read model、BFF route。 | DTO snapshot、route boundary log。 |
| PV20-S2 | Executor 可执行 allowlisted skill/read-model 节点。 | executor runtime、skill adapter、trace/artifact evidence。 | skill execution report、redaction scan。 |
| PV20-S3 | Executor 可执行 allowlisted MCP/tool 节点。 | tool/MCP adapter、connector runtime boundary。 | MCP/tool call refs、negative fixture。 |
| PV20-S4 | Executor 支持 approval / handoff。 | approval gate、waiting_approval state、human confirmed resume。 | state transition report、audit trail。 |
| PV20-S5 | Executor 支持 timeout / cancel / retry。 | timeout controller、cancel endpoint、attempt model。 | timeout/cancel/retry report。 |
| PV20-S6 | Evidence review 汇总 Agent execution evidence。 | evidence read model、browser panel、claim matrix。 | evidence summary、browser screenshots。 |
| PV20-SA | Reviewer 接受 bounded governed Agent executor candidate。 | aggregate runner、artifact manifest、audit closure。 | acceptance-data、artifact-manifest、audit closure。 |

## 2. Entry Conditions

PV20 实现不能开始，直到：

- PV20 PRD、目标架构、开发计划、验收门槛、任务矩阵和 readiness audit 存在。
- 文档明确 PV20 是 governed Agent executor candidate，不是 unrestricted automation。
- 文档明确发布、审批响应、git push、生产部署仍禁止 Agent 自动执行。
- 文档锁定至少两个非同构验收节点：skill/read-model 节点和 MCP/tool 节点。
- No False Green 扫描通过。

## 3. Required Acceptance Data

后续实现证据建议落在：

```text
docs/design/V12-V15.x/evidence/pv20-complete-agent-executor/
```

最低文件：

- `acceptance-data.json`
- `artifact-manifest.json`
- `agent-execution-envelope-snapshots.json`
- `agent-execution-result-report.json`
- `skill-node-execution-report.json`
- `tool-mcp-node-execution-report.json`
- `approval-handoff-report.json`
- `timeout-cancel-retry-report.json`
- `route-boundary-log.json`
- `browser-network-log.json`
- `executor-evidence-review-screenshot.png`
- `prd-spec-review.md`
- `target-architecture-review.md`
- `implementation-risk-audit.md`
- `no-false-green-scan.txt`
- `redaction-scan.txt`

## 4. Negative Fixtures

- `agent_direct_publish_denied`
- `agent_direct_approval_respond_denied`
- `unknown_tool_denied`
- `unknown_skill_denied`
- `mcp_scope_escape_denied`
- `raw_prompt_leak_denied`
- `raw_secret_leak_denied`
- `timeout_marks_station_failed_or_timeout`
- `cancel_stops_pending_execution`
- `retry_creates_new_attempt_without_erasing_prior_evidence`
- `browser_direct_rpc_denied`

## 5. Acceptance Blockers

- Agent 节点只是 UI 模拟，没有 backend StationRun / execution evidence。
- Executor 绕过 WorkflowInstance / StationRun 直接执行。
- Agent 可以自动 publish、approve、git push 或 production deploy。
- 未授权 tool/skill/MCP 调用未被拒绝。
- Timeout、cancel、retry 无后端状态证据。
- Evidence 缺少 artifact、trace、policy、approval 或 incident refs。
- DTO 或报告泄露 raw prompt、secret、raw provider payload。
- UI 或文档声明 production ready、unrestricted automation ready、完整 Workflow Studio 或商业化完成。

