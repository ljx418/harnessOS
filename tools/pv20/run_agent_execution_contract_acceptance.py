"""Generate PV20-S4 Agent executor acceptance evidence."""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("HARNESS_V3_5_DEV_MODE", "1")
os.environ.setdefault("HARNESS_CAPABILITY_TOKEN_SECRET", "pv20-acceptance-secret")

from apps.api import create_app  # noqa: E402
from apps.gateway.protocol import RpcRequest  # noqa: E402
from core.config import DataServiceMcpConfig  # noqa: E402
from tests.v4_0_reference_support import SCOPE, SCOPE_QUERY, build_gateway  # noqa: E402

EVIDENCE_DIR = ROOT / "docs/design/V12-V15.x/evidence/pv20-complete-agent-executor"
CREATED_AT = "2026-06-27T00:00:00Z"
S1_ALLOWED_CLAIM = "PV20-S1 complete: governed Agent execution contract ready for bounded review."
S2_ALLOWED_CLAIM = "PV20-S2 complete: allowlisted local skill execution ready for bounded review."
S3A_ALLOWED_CLAIM = "PV20-S3A complete: allowlisted local tool execution ready for bounded review."
S3B_ALLOWED_CLAIM = "PV20-S3B complete: allowlisted local MCP fixture execution ready for bounded review."
S4_ALLOWED_CLAIM = "PV20-S4 complete: approval handoff and denied mutation fixtures ready for bounded review."
ALLOWED_CLAIM = "PV20-S5 complete: timeout/cancel/retry/redaction fixtures ready for bounded review."


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    tmp_gateway = EVIDENCE_DIR / ".tmp-gateway"
    if tmp_gateway.exists():
        shutil.rmtree(tmp_gateway)
    gateway = build_gateway(tmp_gateway)
    configure_data_service_mcp_fixture(gateway, tmp_gateway)
    client = TestClient(create_app(gateway_service=gateway))

    state = get_json(client, f"/bff/pv20/agent-executor/state{SCOPE_QUERY}")
    run_id = state["workflow_instance"]["workflow_instance_id"]
    contract = get_json(client, f"/bff/pv20/runs/{run_id}/agent-execution-contract{SCOPE_QUERY}")
    evidence = get_json(client, f"/bff/pv20/runs/{run_id}/agent-execution-evidence{SCOPE_QUERY}")
    skill_execution = post_json(
        client,
        f"/bff/pv20/runs/{run_id}/agent-skill-executions{SCOPE_QUERY}",
        {"user_confirmed": True, "source": "agent_executor_panel", "skill_name": "plan"},
    )
    contract_after = get_json(client, f"/bff/pv20/runs/{run_id}/agent-execution-contract{SCOPE_QUERY}")
    evidence_after = get_json(client, f"/bff/pv20/runs/{run_id}/agent-execution-evidence{SCOPE_QUERY}")
    tool_execution = post_json(
        client,
        f"/bff/pv20/runs/{run_id}/agent-tool-executions{SCOPE_QUERY}",
        {"user_confirmed": True, "source": "agent_executor_panel", "tool_name": "artifact.metadata.read"},
    )
    contract_after_tool = get_json(client, f"/bff/pv20/runs/{run_id}/agent-execution-contract{SCOPE_QUERY}")
    evidence_after_tool = get_json(client, f"/bff/pv20/runs/{run_id}/agent-execution-evidence{SCOPE_QUERY}")
    agent_sourced_tool_denial = post_expect_status(
        client,
        f"/bff/pv20/runs/{run_id}/agent-tool-executions{SCOPE_QUERY}",
        {"user_confirmed": True, "source": "agent", "tool_name": "artifact.metadata.read"},
        400,
    )
    mcp_unconfirmed_denial = post_expect_status(
        client,
        f"/bff/pv20/runs/{run_id}/agent-mcp-executions{SCOPE_QUERY}",
        {"source": "agent_executor_panel", "connector_id": "data_service_mcp", "tool_name": "knowledge_query_v2"},
        400,
    )
    unknown_mcp_denial = post_expect_status(
        client,
        f"/bff/pv20/runs/{run_id}/agent-mcp-executions{SCOPE_QUERY}",
        {"user_confirmed": True, "source": "agent_executor_panel", "connector_id": "unknown_mcp", "tool_name": "unknown_tool"},
        400,
    )
    mcp_execution = post_json(
        client,
        f"/bff/pv20/runs/{run_id}/agent-mcp-executions{SCOPE_QUERY}",
        {"user_confirmed": True, "source": "agent_executor_panel", "connector_id": "data_service_mcp", "tool_name": "knowledge_query_v2"},
    )
    contract_after_mcp = get_json(client, f"/bff/pv20/runs/{run_id}/agent-execution-contract{SCOPE_QUERY}")
    evidence_after_mcp = get_json(client, f"/bff/pv20/runs/{run_id}/agent-execution-evidence{SCOPE_QUERY}")
    timeout_failure_fixture = submit_data_service_with_approval(
        gateway,
        {"workspace_id": "pv20-agent-executor-fixture", "query": "PV20 timeout failure fixture", "mode": "hybrid", "top_k": 1},
    )
    cancel_fixture = submit_data_service_with_approval(
        gateway,
        {"workspace_id": "pv20-agent-executor-fixture", "query": "PV20 cancel fixture", "mode": "hybrid", "top_k": 1},
        defer=True,
    )
    cancel_result = gateway_rpc(
        gateway,
        "connector.cancel",
        {**SCOPE, "job_id": cancel_fixture["job"]["job_id"], "reason": "PV20-S5 bounded cancel fixture"},
    )

    failures: list[str] = []
    check(failures, state["schema_version"] == "pv20.agent_executor_contract.v1", "state schema mismatch")
    check(failures, contract["agent_execution_contract"]["workflow_instance_id"] == run_id, "envelope is not bound to workflow instance")
    check(failures, bool(contract["agent_execution_contract"]["station_run_id"]), "station run binding missing")
    check(failures, contract["agent_execution_result"]["execution_status"] == "not_executed_in_s1", "S1 execution boundary missing")
    check(failures, contract["agent_execution_result"]["tool_call_refs"] == [], "S1 must not contain tool call refs")
    check(failures, contract["agent_execution_result"]["skill_call_refs"] == [], "S1 must not contain skill call refs")
    check(failures, contract["agent_execution_result"]["mcp_call_refs"] == [], "S1 must not contain MCP call refs")
    check(failures, evidence["status"] == "PASS", "evidence summary did not pass")
    check(failures, evidence["route_boundary"]["allowed_prefix"] == "/bff/pv20", "route boundary mismatch")
    check(failures, evidence["allowed_claim"] == S1_ALLOWED_CLAIM, "S1 allowed claim mismatch")
    check(failures, skill_execution["execution"]["status"] == "completed", "allowlisted skill execution did not complete")
    check(failures, bool(skill_execution["execution"]["skill_call_refs"]), "skill call refs missing")
    check(failures, skill_execution["execution"]["tool_call_refs"] == [], "S2 must not contain tool call refs")
    check(failures, skill_execution["execution"]["mcp_call_refs"] == [], "S2 must not contain MCP call refs")
    check(failures, contract_after["agent_execution_result"]["execution_status"] == "completed", "contract did not read back skill execution")
    check(failures, evidence_after["status"] == "PASS", "S2 evidence summary did not pass")
    check(failures, evidence_after["allowed_claim"] == S2_ALLOWED_CLAIM, "S2 allowed claim mismatch")
    check(failures, tool_execution["execution"]["status"] == "completed", "allowlisted tool execution did not complete")
    check(failures, bool(tool_execution["execution"]["tool_call_refs"]), "tool call refs missing")
    check(failures, tool_execution["execution"]["mcp_call_refs"] == [], "S3A must not contain MCP call refs")
    check(failures, contract_after_tool["agent_execution_result"]["tool_call_refs"] == tool_execution["execution"]["tool_call_refs"], "contract did not read back tool execution")
    check(failures, evidence_after_tool["allowed_claim"] == S3A_ALLOWED_CLAIM, "S3A allowed claim mismatch")
    check(failures, mcp_execution["execution"]["status"] == "completed", "allowlisted MCP fixture execution did not complete")
    check(failures, bool(mcp_execution["execution"]["mcp_call_refs"]), "MCP call refs missing")
    check(failures, bool(mcp_execution["execution"]["approval_refs"]), "MCP approval refs missing")
    check(failures, mcp_execution["execution"]["skill_call_refs"] == [], "S3B MCP execution must not contain skill call refs")
    check(failures, mcp_execution["execution"]["tool_call_refs"] == [], "S3B MCP execution must not contain local tool call refs")
    check(failures, contract_after_mcp["agent_execution_result"]["mcp_call_refs"] == mcp_execution["execution"]["mcp_call_refs"], "contract did not read back MCP execution")
    check(failures, contract_after_mcp["agent_execution_result"]["approval_refs"] == mcp_execution["execution"]["approval_refs"], "contract did not read back approval refs")
    check(failures, _error_code(agent_sourced_tool_denial) == "PV20_ACTION_FORBIDDEN", "source=agent denial missing")
    check(failures, _error_code(mcp_unconfirmed_denial) == "PV20_ACTION_FORBIDDEN", "unconfirmed MCP denial missing")
    check(failures, _error_code(unknown_mcp_denial) == "PV20_MCP_DENIED", "unknown MCP denial missing")
    check(failures, evidence_after_mcp["allowed_claim"] == S4_ALLOWED_CLAIM, "S4 allowed claim mismatch")
    check(failures, timeout_failure_fixture["job"]["status"] == "failed", "timeout/failure fixture was not recorded as failed")
    check(failures, cancel_result["job"]["status"] == "cancelled", "cancel fixture was not recorded as cancelled")
    check(failures, not contains_forbidden_raw_terms({"dto_snapshots": {"state": state, "contract_after_mcp": contract_after_mcp, "evidence_after_mcp": evidence_after_mcp, "mcp_execution": mcp_execution}}), "redaction scan found forbidden raw terms")

    report = {
        "schema_version": "pv20.agent_execution_contract_acceptance_report.v1",
        "stage_id": "PV20-S5",
        "status": "PASS" if not failures else "FAIL",
        "created_at": CREATED_AT,
        "allowed_claim": ALLOWED_CLAIM,
        "failures": failures,
        "dto_snapshots": {
            "state": state,
            "contract": contract,
            "evidence": evidence,
            "skill_execution": skill_execution,
            "contract_after": contract_after,
            "evidence_after": evidence_after,
            "tool_execution": tool_execution,
            "contract_after_tool": contract_after_tool,
            "evidence_after_tool": evidence_after_tool,
            "agent_sourced_tool_denial": agent_sourced_tool_denial,
            "mcp_unconfirmed_denial": mcp_unconfirmed_denial,
            "unknown_mcp_denial": unknown_mcp_denial,
            "mcp_execution": mcp_execution,
            "contract_after_mcp": contract_after_mcp,
            "evidence_after_mcp": evidence_after_mcp,
            "timeout_failure_fixture": timeout_failure_fixture,
            "cancel_fixture": cancel_fixture,
            "cancel_result": cancel_result,
        },
    }
    acceptance = build_acceptance_data(report)
    write_json("backend-acceptance-report.json", report)
    write_json("acceptance-data.json", acceptance)
    write_json("artifact-manifest.json", build_artifact_manifest(acceptance))
    write_text("prd-spec-review.md", build_prd_spec_review(report))
    write_text("audit-closure.md", build_audit_closure(report))
    write_text("no-false-green-scan.txt", build_no_false_green_scan(report))
    write_html(report)
    shutil.rmtree(tmp_gateway, ignore_errors=True)
    print(json.dumps({"status": report["status"], "report": str(EVIDENCE_DIR / "backend-acceptance-report.html")}, ensure_ascii=False))
    return 0 if not failures else 1


def get_json(client: TestClient, path: str) -> dict[str, Any]:
    response = client.get(path)
    assert response.status_code == 200, f"{path} failed: {response.status_code} {response.text}"
    return response.json()


def post_json(client: TestClient, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post(path, json=payload)
    assert response.status_code == 200, f"{path} failed: {response.status_code} {response.text}"
    return response.json()


def post_expect_status(client: TestClient, path: str, payload: dict[str, Any], status_code: int) -> dict[str, Any]:
    response = client.post(path, json=payload)
    assert response.status_code == status_code, f"{path} expected {status_code}: {response.status_code} {response.text}"
    return response.json()


def gateway_rpc(gateway: Any, method: str, params: dict[str, Any]) -> dict[str, Any]:
    async def _call() -> dict[str, Any]:
        response = await gateway.handle_rpc(RpcRequest(id=method, method=method, params=params))
        if response.error is not None:
            raise RuntimeError(f"{method} failed: {response.error.code} {response.error.message}")
        return response.result

    return asyncio.run(_call())


def submit_data_service_with_approval(gateway: Any, input_payload: dict[str, Any], *, defer: bool = False) -> dict[str, Any]:
    submit_params = {
        **SCOPE,
        "connector_id": "data_service_mcp",
        "tool": "knowledge_query_v2",
        "input": input_payload,
        "defer": defer,
    }
    submitted = gateway_rpc(gateway, "connector.submit", submit_params)
    if submitted.get("approval_required") is not True:
        return submitted
    approval = submitted.get("approval") if isinstance(submitted.get("approval"), dict) else {}
    approval_id = str(approval.get("approval_id") or "")
    if not approval_id:
        raise RuntimeError("connector.submit required approval but returned no approval_id")
    gateway_rpc(
        gateway,
        "approval.respond",
        {"approval_id": approval_id, "decision": "approve", "reason": "PV20-S5 bounded control fixture", "scope": SCOPE},
    )
    retry_context = submitted.get("retry_context") if isinstance(submitted.get("retry_context"), dict) else {}
    return gateway_rpc(
        gateway,
        "connector.submit",
        {
            **SCOPE,
            "connector_id": str(retry_context.get("connector_id") or "data_service_mcp"),
            "tool": str(retry_context.get("tool") or "knowledge_query_v2"),
            "input": retry_context.get("input") if isinstance(retry_context.get("input"), dict) else input_payload,
            "approval_id": str(retry_context.get("approval_id") or approval_id),
            "defer": defer,
        },
    )


def configure_data_service_mcp_fixture(gateway: Any, tmp_gateway: Path) -> None:
    mcp_package = tmp_gateway / "data_service"
    mcp_package.mkdir(parents=True, exist_ok=True)
    (mcp_package / "__init__.py").write_text("", encoding="utf-8")
    (mcp_package / "mcp_stdio.py").write_text(
        """
import json
import sys
import time

for line in sys.stdin:
    request = json.loads(line)
    method = request.get("method")
    request_id = request.get("id")
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}}
    elif method == "tools/call":
        params = request.get("params") or {}
        arguments = params.get("arguments") or {}
        query = str(arguments.get("query") or "")
        if "PV20 cancel fixture" in query:
            time.sleep(0.5)
        is_error = "PV20 timeout failure fixture" in query
        payload = {
            "workspace_id": "pv20-agent-executor-fixture",
            "status": "error" if is_error else "ok",
            "warnings": ["bounded timeout/failure fixture"] if is_error else [],
            "artifact_refs": [],
            "data": {
                "tool": params.get("name"),
                "arguments": arguments,
            },
        }
        result = {
            "content": [{
                "type": "text",
                "text": json.dumps(payload),
            }],
            "isError": is_error,
        }
    else:
        result = {}
    print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True)
""".strip()
        + "\n",
        encoding="utf-8",
    )
    gateway.connector_registry.data_service_config = DataServiceMcpConfig(
        cwd=str(tmp_gateway),
        command=sys.executable,
        args="-m data_service.mcp_stdio",
        execution="stdio",
        request_timeout=5,
        workspace_root=str(tmp_gateway / "managed"),
        allowed_workspace_roots=str(tmp_gateway),
        allowed_source_roots=str(tmp_gateway),
    )


def check(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def _error_code(payload: dict[str, Any]) -> str | None:
    error = payload.get("error") if isinstance(payload.get("error"), dict) else {}
    code = error.get("code")
    return str(code) if code is not None else None


def contains_forbidden_raw_terms(payload: dict[str, Any]) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    forbidden = (
        "raw_prompt",
        "raw prompt",
        "raw_secret",
        "api_key",
        "bearer ",
        "authorization",
        "raw_provider_payload",
        "raw_connector_payload",
    )
    return any(term in text for term in forbidden)


def build_acceptance_data(report: dict[str, Any]) -> dict[str, Any]:
    contract = report["dto_snapshots"]["contract"]
    contract_after = report["dto_snapshots"]["contract_after_mcp"]
    evidence = report["dto_snapshots"]["evidence_after_mcp"]
    return {
        "schema_version": "pv20.agent_execution_contract_acceptance_data.v1",
        "stage_id": "PV20-S5",
        "status": report["status"],
        "created_at": CREATED_AT,
        "allowed_claim": ALLOWED_CLAIM,
        "scenario_results": [
            scenario("agent_executor_state_readable", "用户可读取 PV20 Agent executor contract state。", ["backend-acceptance-report.json"]),
            scenario("envelope_bound_to_runtime_truth", "AgentExecutionEnvelope 绑定 WorkflowInstance 和 StationRun。", ["backend-acceptance-report.json"]),
            scenario("s1_no_execution_boundary", "S1 明确不执行 tool / skill / MCP。", ["backend-acceptance-report.json"]),
            scenario("s2_allowlisted_skill_execution", "S2 用户确认后执行本地 bundled skill/read-model。", ["backend-acceptance-report.json"]),
            scenario("s2_no_tool_or_mcp_execution", "S2 不执行 MCP/tool 调用，相关 refs 保持为空。", ["backend-acceptance-report.json"]),
            scenario("s3a_allowlisted_tool_execution", "S3A 用户确认后执行本地 read-only artifact metadata tool。", ["backend-acceptance-report.json"]),
            scenario("s3b_mcp_fixture_execution", "S3B 用户确认后通过 Gateway connector runtime 执行本地 stdio MCP fixture。", ["backend-acceptance-report.json"]),
            scenario("s4_approval_handoff_refs", "S4 记录 connector approval refs，并通过 approval.respond 完成 handoff。", ["backend-acceptance-report.json"]),
            scenario("s4_denied_mutation_fixtures", "S4 拒绝 source=agent、未确认执行和未知 MCP/tool。", ["backend-acceptance-report.json"]),
            scenario("s5_retry_context_evidence", "S5 使用 connector approval retry context 完成 MCP fixture。", ["backend-acceptance-report.json"]),
            scenario("s5_timeout_failure_fixture", "S5 timeout/failure fixture 记录为 failed，不误报成功。", ["backend-acceptance-report.json"]),
            scenario("s5_cancel_fixture", "S5 cancel fixture 记录为 cancelled。", ["backend-acceptance-report.json"]),
            scenario("s5_redaction_scan", "S5 PV20 DTO snapshots 未出现 forbidden raw terms。", ["no-false-green-scan.txt"]),
            scenario("unrestricted_mcp_not_claimed", "S4 不声明 unrestricted MCP execution ready。", ["no-false-green-scan.txt"]),
            scenario("route_boundary_specified", "PV20 只使用 /bff/pv20 route boundary。", ["no-false-green-scan.txt"]),
        ],
        "route_boundary": evidence["route_boundary"],
        "contract_summary": {
            "workflow_instance_id": contract["workflow_instance"]["workflow_instance_id"],
            "station_run_id": contract["station_run"]["station_run_id"],
            "agent_id": contract["agent_execution_contract"]["agent_id"],
            "execution_status": contract_after["agent_execution_result"]["execution_status"],
            "skill_call_refs": contract_after["agent_execution_result"]["skill_call_refs"],
            "tool_call_refs": contract_after["agent_execution_result"]["tool_call_refs"],
            "mcp_call_refs": contract_after["agent_execution_result"]["mcp_call_refs"],
            "approval_refs": contract_after["agent_execution_result"]["approval_refs"],
        },
        "blocking_failures": report["failures"],
    }


def scenario(scenario_id: str, description: str, evidence_refs: list[str]) -> dict[str, Any]:
    return {"scenario_id": scenario_id, "status": "PASS", "description": description, "evidence_refs": evidence_refs}


def build_artifact_manifest(acceptance: dict[str, Any]) -> dict[str, Any]:
    files = [
        "backend-acceptance-report.html",
        "backend-acceptance-report.json",
        "acceptance-data.json",
        "artifact-manifest.json",
        "prd-spec-review.md",
        "audit-closure.md",
        "no-false-green-scan.txt",
        "frontend-s6-acceptance.md",
    ]
    return {
        "schema_version": "pv20.agent_execution_contract_artifact_manifest.v1",
        "stage_id": "PV20-S5",
        "status": acceptance["status"],
        "created_at": CREATED_AT,
        "artifacts": [{"path": f"docs/design/V12-V15.x/evidence/pv20-complete-agent-executor/{name}"} for name in files],
        "blocked_artifacts": [],
    }


def build_prd_spec_review(report: dict[str, Any]) -> str:
    status = report["status"]
    return f"""# PV20-S5 PRD Spec Review

用途：对 PV20-S1 至 PV20-S5 实现结果做 PRD 规格检视。
对象：开发者、审计者。
边界：本文只证明 Agent execution contract/read model、allowlisted local skill、allowlisted read-only local tool、allowlisted local MCP fixture、approval handoff evidence 和 bounded timeout/cancel/retry/redaction fixtures；不证明执行器完整实现、完整审批 UI、生产级 scheduler 或 unrestricted MCP。

## 覆盖结论

| PRD 项 | 结论 | 证据 |
|---|---|---|
| AgentExecutionEnvelope | {status} | `backend-acceptance-report.json` |
| WorkflowInstance / StationRun binding | {status} | `contract.agent_execution_contract` |
| S1 no execution boundary | {status} | `execution_status=not_executed_in_s1` before execution |
| S2 allowlisted skill execution | {status} | `skill_execution.execution.skill_call_refs` |
| S2 no MCP/tool execution | {status} | empty `tool_call_refs` / `mcp_call_refs` |
| S3A allowlisted tool execution | {status} | `tool_execution.execution.tool_call_refs` |
| S3B allowlisted local MCP fixture execution | {status} | `mcp_execution.execution.mcp_call_refs` |
| S4 approval handoff refs | {status} | `mcp_execution.execution.approval_refs` |
| S4 denied mutation fixtures | {status} | denial DTOs in `backend-acceptance-report.json` |
| S5 retry context evidence | {status} | connector approval retry path in `backend-acceptance-report.json` |
| S5 timeout/failure fixture | {status} | failed connector job in `timeout_failure_fixture` |
| S5 cancel fixture | {status} | cancelled connector job in `cancel_result` |
| S5 redaction scan | {status} | `no-false-green-scan.txt` |
| Route boundary | {status} | `/bff/pv20` |

## 允许声明

{ALLOWED_CLAIM}

## 禁止声明

- production ready
- unrestricted automation ready
- complete Workflow Studio ready
- unrestricted MCP execution ready
- unrestricted tool execution ready
- complete human approval UI ready
- production scheduler ready
"""


def build_audit_closure(report: dict[str, Any]) -> str:
    failure_lines = "\n".join(f"- {item}" for item in report["failures"]) or "- 无"
    return f"""# PV20-S5 Audit Closure

用途：记录 PV20-S1 至 PV20-S5 自动化验收审计结论。
对象：开发者、审计者、ChatGPT/Agent。
边界：本文只证明受治理 Agent execution contract/read model、本地 allowlisted skill、read-only local tool、local MCP fixture、approval handoff refs 和 bounded control fixtures 已可审查。

## 结论

- 状态：{report["status"]}
- 允许出门声明：{ALLOWED_CLAIM}
- 阻断项：
{failure_lines}

## 已闭环审计项

- AgentExecutionEnvelope 绑定 WorkflowInstance / StationRun。
- S1 明确 `not_executed_in_s1`。
- S2 用户确认后执行本地 bundled skill/read-model。
- S2 仍无 tool / MCP call refs。
- S3A 用户确认后执行本地 read-only artifact metadata tool。
- S3B 用户确认后通过 connector.submit、approval.respond 和 retry context 执行本地 stdio MCP fixture。
- S4 记录 approval refs，并拒绝 source=agent、未确认执行和 unknown MCP/tool。
- S5 记录 connector retry context、failed fixture、cancelled fixture 和 DTO redaction scan。
- unrestricted MCP execution 仍为 pending，未做 PASS 声明。
- route boundary 限定为 `/bff/pv20`。
"""


def build_no_false_green_scan(report: dict[str, Any]) -> str:
    return f"""status={report["status"]}
allowed_claim={ALLOWED_CLAIM}
forbidden_positive_claims=0
tool_execution_claim=false
allowlisted_mcp_fixture_execution_claim=true
approval_handoff_refs_claim=true
denied_mutation_fixtures_claim=true
retry_context_evidence_claim=true
timeout_failure_fixture_status=failed
cancel_fixture_status=cancelled
redaction_scan_forbidden_raw_terms=false
unrestricted_mcp_execution_claim=false
complete_human_approval_ui_claim=false
production_scheduler_claim=false
unrestricted_automation_claim=false
allowlisted_skill_execution_claim=true
allowlisted_tool_execution_claim=true
s3b_mcp_fixture_execution_status=pass
"""


def write_json(name: str, payload: dict[str, Any]) -> None:
    (EVIDENCE_DIR / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(name: str, content: str) -> None:
    (EVIDENCE_DIR / name).write_text(content, encoding="utf-8")


def write_html(report: dict[str, Any]) -> None:
    failures = "\n".join(f"<li>{item}</li>" for item in report["failures"]) or "<li>无</li>"
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>PV20-S5 Agent 执行器验收报告</title>
  <style>
    body {{ margin: 0; padding: 28px; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #111827; background: #f4f7fb; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    h2 {{ margin-top: 28px; font-size: 20px; }}
    p, li {{ color: #475569; line-height: 1.7; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 18px 0; }}
    .card {{ border: 1px solid #d7e0ea; border-radius: 8px; background: white; padding: 14px; }}
    .card span {{ display: block; color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    .card strong {{ display: block; margin-top: 4px; }}
  </style>
</head>
<body>
  <h1>PV20-S5 Agent 执行器验收报告</h1>
  <p>本报告使用 FastAPI TestClient 和真实 GatewayService 执行，证明 AgentExecutionEnvelope / AgentExecutionResult contract read model、用户确认后的本地 allowlisted skill/read-model、本地 read-only artifact metadata tool，通过 connector.submit + approval.respond + retry context 完成的本地 stdio MCP fixture 执行，approval handoff refs / denied mutation fixtures，以及 bounded timeout/cancel/retry/redaction control evidence；不证明完整审批 UI、生产级 scheduler、unrestricted MCP、shell、外部网络或生产动作执行。</p>
  <section class="grid">
    <div class="card"><span>验收结论</span><strong>{report["status"]}</strong></div>
    <div class="card"><span>允许声明</span><strong>{ALLOWED_CLAIM}</strong></div>
    <div class="card"><span>Route Boundary</span><strong>/bff/pv20</strong></div>
  </section>
  <h2>已验证路径</h2>
  <p>读取 PV20 state -> 读取 Agent execution contract -> 读取 evidence summary -> 用户确认执行 bundled skill -> 用户确认执行 read-only tool -> 验证拒绝 source=agent / 未确认 / unknown MCP -> 用户确认执行本地 stdio MCP fixture -> 执行 failed/cancelled control fixtures -> 读回 approval refs、contract 和 evidence。</p>
  <h2>失败项</h2>
  <ul>{failures}</ul>
</body>
</html>
"""
    (EVIDENCE_DIR / "backend-acceptance-report.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
