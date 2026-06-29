# PV20-S2 Skill Read-Model Execution Development Plan

用途：定义 PV20-S2 的开发步骤、验收标准和证据输出。
阅读对象：开发、测试、审计人员。
边界：S2 只执行本地 allowlisted bundled skill/read-model；不执行 MCP、shell、外部网络或生产动作。

## 1. Scope

PV20-S2 在 S1 contract/read model 之上增加一个低风险真实执行能力：

- 读取 `AgentExecutionEnvelope`。
- 校验 `user_confirmed=true`、source allowlist、skill allowlist 和 redaction boundary。
- 执行一个 bundled skill/read-model，生成 redacted execution result。
- 将 skill_call_refs、artifact refs 和 audit refs 写回 StationRun metadata。

## 2. Development Tasks

| Task | Code entity | Output |
| --- | --- | --- |
| S2-T1 | `core/agent_executor/*` | Add governed local skill executor. |
| S2-T2 | `apps/api/routers/bff.py` | Add user-confirmed `/bff/pv20/.../agent-skill-executions` route. |
| S2-T3 | `tests/test_pv20_agent_execution_contract_bff.py` | Verify skill execution, idempotent readback and no MCP/tool refs. |
| S2-T4 | `tools/pv20/run_agent_execution_contract_acceptance.py` | Extend acceptance with S2 execution evidence. |

## 3. Acceptance Criteria

- Skill execution requires user confirmation and allowed source.
- Unknown skill is denied.
- Successful execution writes `skill_call_refs` and an artifact ref.
- Contract readback reflects the execution result from backend StationRun metadata.
- MCP/tool refs remain empty in S2.

## 4. Stop Conditions

- Implementation requires external model, external MCP, shell, unrestricted filesystem or network access.
- Implementation lets source=agent trigger execution.
- Implementation writes raw skill content, raw prompt or secrets into DTO.

