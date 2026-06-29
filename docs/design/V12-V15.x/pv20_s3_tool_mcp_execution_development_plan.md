# PV20-S3 Tool / MCP Execution Development Plan

用途：定义 PV20-S3 的开发步骤、验收标准和证据输出。
阅读对象：开发、测试、审计人员。
边界：S3 只允许受治理的 allowlisted tool/MCP execution；不得开放 shell、任意文件系统、任意网络或生产动作。

## 1. Scope

PV20-S3 分两段执行：

- S3A：本地 read-only tool execution，优先选择 artifact metadata / workflow read model 这类已存在平台工具。
- S3B：本地可控 MCP/connector execution，只在仓库已有可自动启动、可审计、无外部生产凭证依赖的 MCP fixture 时执行。

若 S3B 无法使用真实本地 fixture，不得用 mock 或文档声明替代 MCP evidence；必须将 S3B 标为 blocked/pending。

## 2. Development Tasks

| Task | Code entity | Output |
| --- | --- | --- |
| S3-T1 | `core/agent_executor/runtime.py` | Add governed read-only tool execution contract. |
| S3-T2 | `apps/api/routers/bff.py` | Add user-confirmed tool execution route under `/bff/pv20`. |
| S3-T3 | `tests/test_pv20_agent_execution_contract_bff.py` | Verify allowed tool execution and denied unknown/durable tools. |
| S3-T4 | `tools/pv20/run_agent_execution_contract_acceptance.py` | Extend acceptance with tool call refs and no MCP overclaim. |
| S3-T5 | MCP fixture review | Only implement S3B after local MCP fixture is selected and audited. |

## 3. Acceptance Criteria

- Tool execution requires user confirmation and allowed source.
- Allowed read-only tool writes `tool_call_refs` and artifact/trace refs.
- Unknown tool, durable tool and source=agent tool execution are denied.
- MCP evidence is either real and local, or explicitly pending; no fake MCP PASS.
- Contract/evidence readback distinguishes skill, tool and MCP refs.

## 4. Stop Conditions

- S3B requires external service credentials, production endpoints, unrestricted network or long-running unmanaged process.
- Tool execution needs raw artifact content or raw secrets in DTO.
- BFF route exposes `/v1/rpc`, `/v1/internal/*` or direct connector internals to browser.

